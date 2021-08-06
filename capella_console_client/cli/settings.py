import typer
import questionary

from capella_console_client.validate import _must_be_int
from capella_console_client.cli.cache import CLICachePaths
from capella_console_client.cli.config import (
    CLI_SUPPORTED_SEARCH_FILTERS,
    CURRENT_SETTINGS,
)


# TODO: disable global callback
app = typer.Typer(callback=None)


@app.command()
def set_search_result_fields(help="set fields to be displayed in search results table"):
    search_result_fields = questionary.checkbox(
        "Which fields would you like to display in the search results table?",
        choices=CLI_SUPPORTED_SEARCH_FILTERS,
    ).ask()

    CLICachePaths.write_user_settings("search_fields", search_result_fields)


@app.command()
def set_default_limit(help="set default limit to be used in search"):
    cur_limit = CURRENT_SETTINGS["limit"]
    limit = questionary.text(
        "Specify your default search limit",
        default=str(cur_limit),
        validate=_must_be_int,
    ).ask()

    CLICachePaths.write_user_settings("limit", int(limit))
