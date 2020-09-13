# coding=utf-8

"""Logging for AntEye.

Loggers process every monitor, every iteration, to record their state in some fashion.
"""


import logging
from typing import Any, Dict, List, Optional, cast

from ..Monitors.monitor import Monitor
from ..util import LoggerConfigurationError, get_config_option, subclass_dict_handler


class Logger:
    """Abstract class basis for loggers."""

    logger_type = "unknown"

    supports_batch = False
    doing_batch = False
    batch_data = None  # type: Optional[Dict[str, Any]]
    connected = True
    _global_info = None  # type: Optional[dict]

    def __init__(self, config_options: dict) -> None:
        self._config_options = config_options
        self.name = self.get_config_option("_name", default="unnamed")
        self.logger_logger = logging.getLogger("AntEye.logger-" + self.name)
        self._dependencies = cast(
            List[str],
            self.get_config_option("depend", required_type="[str]", default=[]),
        )
        # only log for Monitors with one of these groups
        self._groups = self.get_config_option(
            "groups", required_type="[str]", default=["default"]
        )
        if self.batch_data is None:
            self.batch_data = {}
        self.tz = cast(Optional[str], self.get_config_option("tz", default="UTC"))
        if self._global_info is None:
            self._global_info = {}

    def __enter__(self) -> None:
        """Context manager entry."""
        self.start_batch()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Context manager exit."""
        self.end_batch()

    def set_global_info(self, info: dict) -> None:
        """Receive global info about the AntEye state.

        Includes but not limited to refresh interval, known remote instances, etc"""
        self._global_info = info

    def get_config_option(self, key: str, **kwargs: Any) -> Any:
        """Get a config value.

        Throws the right flavour exception if something is wrong."""
        kwargs["exception"] = LoggerConfigurationError
        return get_config_option(self._config_options, key, **kwargs)

    def hup(self) -> None:
        """Close and reopen our log file, if supported.

        This should be overridden where needed."""
        return  # pragma: no cover

    def save_result2(self, name: str, monitor: Monitor) -> None:
        """Record a result.

        Subclasses must override this with their implementation."""
        raise NotImplementedError

    @property
    def dependencies(self) -> list:
        """The dependencies of this Logger."""
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependency_list: List[str]) -> None:
        if not isinstance(dependency_list, list):
            raise TypeError("dependency_list must be a list")
        self._dependencies = dependency_list

    def check_dependencies(self, failed_list: List[str]) -> bool:
        """Compare a list of failed monitors to our dependencies, and mark
        the Logger as offline if one failed"""
        self.connected = True
        for dependency in failed_list:
            if dependency in self._dependencies:
                self.connected = False
        return self.connected

    @property
    def groups(self) -> List[str]:
        """The groups this Logger belongs to."""
        return self._groups

    def start_batch(self) -> None:
        """Prepare to process a batch of results"""
        if not self.supports_batch:
            return
        if self.doing_batch:
            self.logger_logger.error(
                "starting a batch while one was already in progress"
            )
        self.batch_data = {}
        self.doing_batch = True

    def end_batch(self) -> None:
        """End receiving a batch of results and process them"""
        if not self.supports_batch:
            return
        if not self.doing_batch:
            self.logger_logger.error("ending a batch when one wasn't in progress")
        self.process_batch()
        self.doing_batch = False

    def process_batch(self) -> None:
        """Process the batched data.
        This is blank for the base class."""
        return  # pragma: no cover

    def describe(self) -> str:
        """Explain what this logger does.
        We don't throw NotImplementedError here as it won't show up until something breaks,
        and we don't want to randomly die then."""
        return "(Logger did not write an auto-biography.)"  # pragma: no cover

    def __str__(self) -> str:
        return self.describe()


(register, get_class, all_types) = subclass_dict_handler(
    "AntEye.Loggers.logger", Logger, "logger_type"
)
