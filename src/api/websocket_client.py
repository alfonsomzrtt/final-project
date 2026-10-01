import asyncio
from typing import Mapping, Optional

import aiohttp
from aiohttp import WSMsgType

from api.messages import Message


class WebSocketError(Exception):
    """Base exception for WebSocket errors."""


class WebSocketConnectionError(WebSocketError):
    """Raised when a WebSocket connection fails."""


class WebSocketMessageError(WebSocketError):
    """Raised when a WebSocket message is invalid."""


class WebSocketClient:
    def __init__(
        self,
        url: str,
        timeout: float = 10.0,
        headers: Optional[Mapping[str, str]] = None,
    ):
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url cannot be empty")

        if not url.startswith(("ws://", "wss://")):
            raise ValueError("url must start with ws:// or wss://")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self._url = url
        self._timeout = timeout
        self._headers = dict(headers or {})
        self._session: Optional[aiohttp.ClientSession] = None
        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None

    @property
    def is_connected(self) -> bool:
        return (
            self._websocket is not None
            and not self._websocket.closed
        )

    async def connect(self) -> None:
        if self.is_connected:
            return

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                headers=self._headers,
            )

        try:
            self._websocket = await self._session.ws_connect(
                self._url,
                heartbeat=30.0,
            )
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            await self._close_session()
            raise WebSocketConnectionError(
                f"Failed to connect: {exc}"
            ) from exc

    async def send(self, message: Message) -> None:
        ws = self._websocket

        if ws is None or ws.closed:
            raise WebSocketConnectionError(
                "WebSocket is not connected"
            )

        if not isinstance(message, Message):
            raise TypeError("message must be a Message instance")

        try:
            await ws.send_json(message.to_dict())
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise WebSocketConnectionError(
                f"Failed to send message: {exc}"
            ) from exc

    async def receive(self) -> Optional[Message]:
        ws = self._websocket

        if ws is None or ws.closed: 
            raise WebSocketConnectionError(
                "WebSocket is not connected"
            )

        try:
            response = await ws.receive()

        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise WebSocketConnectionError(
                f"Failed to receive message: {exc}"
            ) from exc

        if response.type == WSMsgType.TEXT:
            try:
                return Message.from_dict(response.json())
            except (ValueError, TypeError, KeyError) as exc:
                raise WebSocketMessageError(
                    "Received an invalid message"
                ) from exc

        if response.type == WSMsgType.ERROR:
            raise WebSocketConnectionError(
                "WebSocket encountered an error"
            )

        if response.type in (
            WSMsgType.CLOSED,
            WSMsgType.CLOSE,
            WSMsgType.CLOSING,
        ):
            return None

        if response.type == WSMsgType.BINARY:
            raise WebSocketMessageError(
                "Binary messages are not supported"
            )

        return None

    async def disconnect(self) -> None:
        if self._websocket is not None and not self._websocket.closed:
            await self._websocket.close()

        self._websocket = None
        await self._close_session()

    async def _close_session(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()