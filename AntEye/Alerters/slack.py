try:
    import requests

    requests_available = True
except ImportError:
    requests_available = False

from typing import Any, Dict, cast

from ..Monitors.monitor import Monitor
from ..util import format_datetime
from .alerter import Alerter, AlertType, register


@register
class SlackAlerter(Alerter):
    """Send alerts to a Slack webhook."""

    alerter_type = "slack"

    channel = None
    username = None

    def __init__(self, config_options: dict) -> None:
        super().__init__(config_options)
        if not requests_available:
            self.alerter_logger.critical(
                "Requests package is not available, cannot use SlackAlerter."
            )
            self.alerter_logger.critical("Try: pip install -r requirements.txt")
            return

        self.url = cast(
            str, self.get_config_option("url", required=True, allow_empty=False)
        )

        self.channel = cast(str, self.get_config_option("channel"))
        self.username = cast(str, self.get_config_option("username"))

    def send_alert(self, name: str, monitor: Monitor) -> None:
        """Send the message."""

        alert_type = self.should_alert(monitor)
        downtime = monitor.get_downtime()

        message_json = {}  # type: Dict[str, Any]
        if self.channel is not None:
            message_json = {"channel": self.channel}
        elif self.username is not None:
            message_json = {"username": self.username}
        else:
            message_json = {}

        message_json["attachments"] = [{}]

        if alert_type == AlertType.NONE:
            return
        if alert_type == AlertType.FAILURE:
            message_json["text"] = "Monitor {} failed!".format(name)
            message_json["attachments"][0]["color"] = "danger"
            fields = [
                {
                    "title": "Failed at",
                    "value": format_datetime(monitor.first_failure_time()),
                    "short": True,
                },
                {"title": "Downtime", "value": str(downtime), "short": True},
                {
                    "title": "Virtual failure count",
                    "value": monitor.virtual_fail_count(),
                    "short": True,
                },
                {"title": "Host", "value": self.hostname, "short": True},
                {"title": "Additional info", "value": monitor.get_result()},
                {"title": "Description", "value": monitor.describe()},
            ]

            try:
                if monitor.recover_info != "":
                    fields.append(
                        {
                            "title": "Recovery info",
                            "value": "Recovery info: %s" % monitor.recover_info,
                        }
                    )
                    message_json["attachments"][0]["color"] = "warning"
            except AttributeError:
                pass
            message_json["attachments"][0]["fields"] = fields

        elif alert_type == AlertType.SUCCESS:
            message_json["text"] = "Monitor {} succeeded.".format(name)
            fields = [
                {
                    "title": "Failed at",
                    "value": format_datetime(monitor.first_failure_time()),
                    "short": True,
                },
                {"title": "Downtime", "value": str(downtime), "short": True},
                {"title": "Host", "value": self.hostname, "short": True},
                {"title": "Description", "value": monitor.describe()},
            ]
            message_json["attachments"][0]["color"] = "good"
            message_json["attachments"][0]["fields"] = fields

        else:
            self.alerter_logger.error("unknown alert type %s", alert_type)
            return

        if not self._dry_run:
            try:
                r = requests.post(self.url, json=message_json)
                if not r.status_code == 200:
                    self.alerter_logger.error("POST to slack webhook failed: %s", r)
            except Exception:
                self.alerter_logger.exception("Failed to post to slack webhook")
                self.available = False
        else:
            self.alerter_logger.info(
                "dry_run: would send slack: %s", message_json.__repr__()
            )
