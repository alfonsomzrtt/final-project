from typing import Any, Mapping, Optional

from config.settings import (
    API_BASE_URL,
    API_TIMEOUT,
    WEBSOCKET_URL,
)
from api.http_client import HTTPClient
from api.messages import Message
from api.websocket_client import WebSocketClient


class APIClient:
    """High-level client for HTTP and WebSocket communication."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        websocket_url: Optional[str] = None,
        timeout: Optional[float] = None,
        headers: Optional[Mapping[str, str]] = None,
    ):
        self._http = HTTPClient(
            base_url=API_BASE_URL if base_url is None else base_url,
            timeout=API_TIMEOUT if timeout is None else timeout,
            headers=headers,
        )

        self._websocket = WebSocketClient(
            url=WEBSOCKET_URL if websocket_url is None else websocket_url,
            timeout=API_TIMEOUT if timeout is None else timeout,
            headers=headers,
        )

    @property
    def http(self) -> HTTPClient:
        return self._http

    @property
    def websocket(self) -> WebSocketClient:
        return self._websocket

    @property
    def is_websocket_connected(self) -> bool:
        return self._websocket.is_connected

    async def connect_websocket(self) -> None:
        await self._websocket.connect()

    async def disconnect_websocket(self) -> None:
        await self._websocket.disconnect()

    async def send(self, message: Message) -> None:
        await self._websocket.send(message)

    async def receive(self) -> Optional[Message]:
        return await self._websocket.receive()

    async def get(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._http.get(endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._http.post(endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._http.put(endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._http.patch(endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> Any:
        return await self._http.delete(endpoint, **kwargs)

    async def close(self) -> None:
        try:
            await self._websocket.disconnect()
        finally:
            await self._http.close()