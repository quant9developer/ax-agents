from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable

from enterprise_ai_platform.models.events import EventType, PlatformEvent

EventHandler = Callable[[PlatformEvent], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: PlatformEvent) -> None:
        for handler in self._handlers.get(event.event_type, []):
            await handler(event)
