from cybsuite.core.logger import get_logger, get_rich_console


class Printer:
    def __init__(self, *, styles):
        self.console = get_rich_console()
        self.logger = get_logger()
        self.styles = styles

    def format_message(self, *args, **kwargs):
        message_parts = []
        for key, value in kwargs.items():
            if value is None:
                continue

            if key not in self.styles:
                message_parts.append(f"\\[{value}]")
                continue

            key_styles = self.styles.get(key)
            key_style = key_styles.get(value)
            if key_style:
                message_parts.append(f"[{key_style}]\\[{value}][/{key_style}]")
            else:
                message_parts.append(f"\\[{value}]")
        message_parts.extend(args)
        return message_parts

    def print(self, *args, **kwargs):
        message_parts = self.format_message(*args, **kwargs)
        self.logger.info(" ".join(message_parts))


STYLES = {
    "confidence": {
        "certain": "bold cyan",
        "firm": "bold blue",
        "tentative": "bold magenta",
        "manual": "bold white",
    },
    "severity": {
        "critical": "bold red on black",
        "high": "bold red",
        "medium": "bold orange",
        "low": "bold yellow3",
    },
    "type": {
        "info": "bold blue",
        "ok": "bold green",
        "ko": "bold red",
        "error": "bold red",
    },
    "feed_status": {
        "existing": "gray",
        "new": "bold green",
        "updated": "bold yellow",
    },
}

printer = Printer(styles=STYLES)
