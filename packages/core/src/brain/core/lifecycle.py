"""Application lifecycle management for startup and shutdown hooks."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for lifecycle hook functions
LifecycleHook = Callable[[], Coroutine[Any, Any, None]]


class LifecycleManager:
    """Manages the startup and shutdown sequences of the Brain platform."""

    def __init__(self) -> None:
        self._startup_hooks: list[LifecycleHook] = []
        self._shutdown_hooks: list[LifecycleHook] = []
        self._started = False

    def register_startup(self, hook: LifecycleHook) -> None:
        """Register a coroutine function to be executed during startup."""
        self._startup_hooks.append(hook)
        logger.debug("Registered startup hook: %s", hook.__name__)

    def register_shutdown(self, hook: LifecycleHook) -> None:
        """Register a coroutine function to be executed during shutdown."""
        self._shutdown_hooks.append(hook)
        logger.debug("Registered shutdown hook: %s", hook.__name__)

    async def startup(self) -> None:
        """Execute all registered startup hooks sequentially."""
        if self._started:
            logger.warning("Application has already started.")
            return

        logger.info("Initializing application lifecycle startup...")
        for hook in self._startup_hooks:
            try:
                await hook()
            except Exception as e:
                logger.critical("Critical failure in startup hook %s: %s", hook.__name__, e)
                # Propagate startup exception to abort bootstrap
                raise

        self._started = True
        logger.info("Application lifecycle startup completed successfully.")

    async def shutdown(self) -> None:
        """Execute all registered shutdown hooks in reverse order of registration."""
        if not self._started:
            logger.warning("Application was not started; proceeding with shutdown hooks anyway.")

        logger.info("Executing application lifecycle shutdown...")
        # Shutdown in reverse order of startup registration
        for hook in reversed(self._shutdown_hooks):
            try:
                await hook()
            except Exception as e:
                logger.error("Error executing shutdown hook %s: %s", hook.__name__, e)

        self._started = False
        logger.info("Application lifecycle shutdown completed.")


# Global lifecycle manager instance
lifecycle = LifecycleManager()
