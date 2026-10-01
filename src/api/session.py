from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SessionStatus(str, Enum):
    WAITING = "waiting"
    READY = "ready"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Session:
    session_id: str
    host_id: str
    grid_size: int
    difficulty: str
    status: SessionStatus = SessionStatus.WAITING
    players: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.session_id:
            raise ValueError("session_id cannot be empty")

        if not self.host_id:
            raise ValueError("host_id cannot be empty")

        if self.grid_size not in (2, 3):
            raise ValueError("grid_size must be 2 or 3")

        if self.difficulty not in ("easy", "normal", "hard"):
            raise ValueError("Invalid difficulty")

        if self.host_id not in self.players:
            self.players.insert(0, self.host_id)


class SessionManager:
    def __init__(self):
        self._session: Optional[Session] = None

    @property
    def session(self) -> Optional[Session]:
        return self._session

    @property
    def is_active(self) -> bool:
        return self._session is not None

    def set_session(self, session: Session) -> None:
        if not isinstance(session, Session):
            raise TypeError("session must be a Session instance")

        self._session = session

    def clear_session(self) -> None:
        self._session = None

    def update_status(self, status: SessionStatus) -> None:
        if self._session is None:
            raise RuntimeError("No active session")

        if not isinstance(status, SessionStatus):
            raise TypeError("status must be a SessionStatus")

        self._session.status = status

    def add_player(self, player_id: str) -> None:
        if self._session is None:
            raise RuntimeError("No active session")

        if not player_id:
            raise ValueError("player_id cannot be empty")

        if player_id in self._session.players:
            return

        if len(self._session.players) >= 2:
            raise ValueError("Session is full")

        if self._session.status != SessionStatus.WAITING:
            raise RuntimeError("Players can only join a waiting session")

        self._session.players.append(player_id)

    def remove_player(self, player_id: str) -> None:
        if self._session is None:
            raise RuntimeError("No active session")

        if player_id == self._session.host_id:
            raise ValueError("Host cannot be removed directly")

        if player_id in self._session.players:
            self._session.players.remove(player_id)