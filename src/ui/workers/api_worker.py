import asyncio
from concurrent.futures import Future
from typing import Any, Coroutine, Mapping, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from api.client import APIClient
from api.messages import Message


class _APIThread(QThread):
    """Dedicated thread that hosts the asyncio event loop."""

    def __init__(self, worker: "APIWorker"):
        super().__init__()
        self._worker = worker

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            self._worker._initialize(loop)
            loop.run_forever()
        finally:
            pending = asyncio.all_tasks(loop)

            for task in pending:
                task.cancel()

            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )

            loop.close()
            self._worker._finalize()


class APIWorker(QObject):
    """QObject interface for asynchronous API operations."""

    ready = pyqtSignal()
    stopped = pyqtSignal()
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    message_received = pyqtSignal(object)
    request_succeeded = pyqtSignal(str, object)
    request_failed = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._client: Optional[APIClient] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._thread = _APIThread(self)

    @property
    def is_running(self) -> bool:
        return self._thread.isRunning()

    def start(self) -> None:
        if not self._thread.isRunning():
            self._thread.start()

    def _initialize(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._client = APIClient()
        self.ready.emit()

    def _finalize(self) -> None:
        self._loop = None
        self._client = None
        self._receive_task = None
        self.stopped.emit()

    def _submit(
        self,
        coroutine: Coroutine[Any, Any, Any],
    ) -> Future:
        loop = self._loop

        if loop is None or not loop.is_running():
            coroutine.close()
            raise RuntimeError("APIWorker is not running")

        return asyncio.run_coroutine_threadsafe(coroutine, loop)

    async def _request(
        self,
        method: str,
        endpoint: str,
        request_id: Optional[str],
        **kwargs: Any,
    ) -> Any:
        if self._client is None:
            raise RuntimeError("APIClient is not initialized")

        identifier = request_id or endpoint

        try:
            operation = getattr(self._client, method)
            result = await operation(endpoint, **kwargs)
        except Exception as exc:
            self.request_failed.emit(identifier, str(exc))
            raise

        self.request_succeeded.emit(identifier, result)
        return result

    def get(
        self, endpoint: str, request_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future:
        return self._submit(
            self._request("get", endpoint, request_id, **kwargs)
        )

    def post(
        self, endpoint: str, request_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future:
        return self._submit(
            self._request("post", endpoint, request_id, **kwargs)
        )

    def put(
        self, endpoint: str, request_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future:
        return self._submit(
            self._request("put", endpoint, request_id, **kwargs)
        )

    def patch(
        self, endpoint: str, request_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future:
        return self._submit(
            self._request("patch", endpoint, request_id, **kwargs)
        )

    def delete(
        self, endpoint: str, request_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future:
        return self._submit(
            self._request("delete", endpoint, request_id, **kwargs)
        )

    async def _connect_websocket(self) -> None:
        if self._client is None:
            raise RuntimeError("APIClient is not initialized")

        if (
            self._receive_task is not None
            and not self._receive_task.done()
        ):
            return

        try:
            await self._client.connect_websocket()
        except Exception as exc:
            self.error.emit(str(exc))
            raise

        self.connected.emit()
        self._receive_task = asyncio.create_task(
            self._receive_messages()
        )

    async def _receive_messages(self) -> None:
        try:
            while (
                self._client is not None
                and self._client.is_websocket_connected
            ):
                message = await self._client.receive()

                if message is None:
                    break

                self.message_received.emit(message)

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.disconnected.emit()

    def connect_websocket(self) -> Future:
        return self._submit(self._connect_websocket())

    async def _send(self, message: Message) -> None:
        if self._client is None:
            raise RuntimeError("APIClient is not initialized")

        await self._client.send(message)

    def send(self, message: Message) -> Future:
        return self._submit(self._send(message))

    async def _disconnect_websocket(self) -> None:
        if self._client is None:
            return

        task = self._receive_task
        was_connected = self._client.is_websocket_connected

        if task is not None:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            self._receive_task = None

        await self._client.disconnect_websocket()

        if task is None and was_connected:
            self.disconnected.emit()

    def disconnect_websocket(self) -> Future:
        return self._submit(self._disconnect_websocket())

    async def _shutdown(self) -> None:
        if self._client is not None:
            try:
                await self._disconnect_websocket()
            finally:
                await self._client.close()

    def stop(self) -> Optional[Future]:
        loop = self._loop

        if loop is None or not loop.is_running():
            return None

        future = asyncio.run_coroutine_threadsafe(
            self._shutdown(), loop
        )

        def stop_loop(_):
            loop.call_soon_threadsafe(loop.stop)

        future.add_done_callback(stop_loop)
        return future