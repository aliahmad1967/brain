"""Event bus implementation for decoupled package communication."""

import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for event listener callbacks
EventCallback = Callable[[Any], Coroutine[Any, Any, None] | None | Any]


class EventBus:
    """A thread-safe, async-capable Event Bus for publish-subscribe communication."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[EventCallback]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe a callback to a specific event type."""
        async with self._lock:
            if callback not in self._listeners[event_type]:
                self._listeners[event_type].append(callback)
                logger.debug("Subscribed callback %s to event %s", callback.__name__, event_type)

    async def unsubscribe(self, event_type: str, callback: EventCallback) -> None:
        """Unsubscribe a callback from a specific event type."""
        async with self._lock:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
                logger.debug(
                    "Unsubscribed callback %s from event %s", callback.__name__, event_type
                )

    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event to all subscribed listeners asynchronously."""
        # Make a copy of listeners to prevent modification during iteration
        async with self._lock:
            listeners = list(self._listeners[event_type])

        if not listeners:
            return

        tasks = []
        for callback in listeners:
            try:
                if inspect.iscoroutinefunction(callback):
                    # For coroutine callbacks, schedule them in the current event loop
                    tasks.append(self._safe_execute_async(callback, data))
                else:
                    # For synchronous callbacks, run them in a separate thread/executor
                    # or execute immediately if safe. We execute immediately but catch exceptions.
                    self._safe_execute_sync(callback, data)
            except Exception as e:
                logger.exception("Error scheduling listener for event %s: %s", event_type, e)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute_async(self, callback: EventCallback, data: Any) -> None:
        try:
            # We know it is a coroutine function, so we invoke it and await it
            await callback(data)  # type: ignore[misc]
        except Exception as e:
            logger.exception(
                "Exception raised in async event listener %s: %s", callback.__name__, e
            )

    def _safe_execute_sync(self, callback: EventCallback, data: Any) -> None:
        try:
            callback(data)
        except Exception as e:
            logger.exception("Exception raised in sync event listener %s: %s", callback.__name__, e)


# Global event bus instance
event_bus = EventBus()
