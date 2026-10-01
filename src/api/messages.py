"""
API message definitions.

This module defines message types and the common message
structure used for communication between the client and backend.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Types of messages exchanged with the backend."""

    MATCH_REQUEST = "match_request"
    MATCH_FOUND = "match_found"

    PLAYER_READY = "player_ready"
    GAME_START = "game_start"

    LEVEL_START = "level_start"
    SCORE_UPDATE = "score_update"

    PATTERN_COMPLETED = "pattern_completed"
    PLAYER_FINISHED = "player_finished"

    GAME_OVER = "game_over"
    MATCH_RESULT = "match_result"

    HEARTBEAT = "heartbeat"


@dataclass
class Message:
    """
    Generic API message.

    Attributes:
        type: Message type.
        data: Event-specific payload.
    """

    type: MessageType
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the message into a dictionary."""

        return {
            "type": self.type.value,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]):
        """Create a Message from a dictionary."""

        message_type = MessageType(payload["type"])

        return cls(
            type=message_type,
            data=payload.get("data", {}),
        )