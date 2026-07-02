"""Unit tests for the core configuration, event bus, and lifecycle modules."""

import pytest
from brain.core.config import Settings
from brain.core.events import EventBus
from brain.core.lifecycle import LifecycleManager


def test_settings_default_values() -> None:
    settings = Settings()
    assert settings.app_name == "Brain"
    assert settings.db_name == "brain.db"
    assert settings.ollama_url == "http://localhost:11434"


@pytest.mark.asyncio
async def test_event_bus_pub_sub() -> None:
    bus = EventBus()
    received_data = []

    async def callback(data: str) -> None:
        received_data.append(data)

    await bus.subscribe("test-event", callback)
    await bus.publish("test-event", "hello")
    assert received_data == ["hello"]

    await bus.unsubscribe("test-event", callback)
    await bus.publish("test-event", "world")
    assert received_data == ["hello"]


@pytest.mark.asyncio
async def test_lifecycle_manager() -> None:
    manager = LifecycleManager()
    startup_called = False
    shutdown_called = False

    async def on_start() -> None:
        nonlocal startup_called
        startup_called = True

    async def on_stop() -> None:
        nonlocal shutdown_called
        shutdown_called = True

    manager.register_startup(on_start)
    manager.register_shutdown(on_stop)

    await manager.startup()
    assert startup_called is True
    assert shutdown_called is False

    await manager.shutdown()
    assert shutdown_called is True
