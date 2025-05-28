import koalak
from cybsuite.cyberdb import (
    pm_formatters,
    pm_ingestors,
    pm_passive_scanners,
    pm_reporters,
)

CMD_GROUP_MIGRATIONS = "migrations"
CMD_GROUP_PLUGINS = "plugins"
CMD_GROUP_OTHERS = "others"
CMD_GROUP_UTILS = "utils"
CMD_GROUP_DELETE = "group_delete"


def print_ingestors_table():
    rows = []
    for ingestor in pm_ingestors:
        rows.append(
            {
                "name": ingestor.name,
                "extension": ingestor.extension,
                "description": ingestor.metadata.description,
            }
        )
    koalak.containers.print_table(rows)


def print_reporters_table():
    rows = []
    for reporter in pm_reporters:
        rows.append(
            {
                "name": reporter.name,
                "description": reporter.metadata.description,
            }
        )
    koalak.containers.print_table(rows)


def print_scanners_table():
    rows = []
    for scanner in pm_passive_scanners:
        rows.append(
            {
                "name": scanner.name,
                "description": scanner.metadata.description,
            }
        )
    koalak.containers.print_table(rows)


def print_formatters_table():
    rows = []
    for formatter in pm_formatters:
        rows.append(
            {
                "name": formatter.name,
                "description": formatter.metadata.description,
            }
        )
    koalak.containers.print_table(rows)
