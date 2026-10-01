import asyncio
import json as json_module
from typing import Any, Dict, Mapping, Optional

import aiohttp


class APIError(Exception):
    """Base exception for API errors."""


class HTTPStatusError(APIError):
    """Raised when the server returns a non-2xx status."""

    def __init__(
        self,
        status: int,
        message: str,
        payload: Any = None,
    ):
        self.status = status
        self.payload = payload
        super().__init__(f"HTTP {status}: {message}")


class APIConnectionError(APIError):
    """Raised when a connection or timeout error occurs."""


class APIResponseError(APIError):
    """Raised when the server response is invalid."""


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        headers: Optional[Mapping[str, str]] = None,
    ):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url cannot be empty")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._headers = dict(headers or {})
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def is_closed(self) -> bool:
        return self._session is None or self._session.closed

    def _build_url(self, endpoint: str) -> str:
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise ValueError("endpoint cannot be empty")

        return f"{self._base_url}/{endpoint.lstrip('/')}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers=self._headers,
            )

        return self._session

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        session = await self._get_session()
        url = self._build_url(endpoint)

        try:
            async with session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                headers=headers,
            ) as response:
                body = await response.text()

                if not 200 <= response.status < 300:
                    try:
                        payload = (
                            json_module.loads(body) if body else None
                        )
                    except json_module.JSONDecodeError:
                        payload = body or None

                    raise HTTPStatusError(
                        status=response.status,
                        message=response.reason or "Request failed",
                        payload=payload,
                    )

                if not body.strip():
                    return None

                try:
                    return json_module.loads(body)
                except json_module.JSONDecodeError as exc:
                    raise APIResponseError(
                        "Server returned invalid JSON"
                    ) from exc

        except asyncio.TimeoutError as exc:
            raise APIConnectionError(
                "Request timed out"
            ) from exc

        except aiohttp.ClientError as exc:
            raise APIConnectionError(
                f"Connection error: {exc}"
            ) from exc

    async def get(self, endpoint: str, **kwargs: Any) -> Any:
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> Any:
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> Any:
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs: Any) -> Any:
        return await self.request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> Any:
        return await self.request("DELETE", endpoint, **kwargs)

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

        self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()