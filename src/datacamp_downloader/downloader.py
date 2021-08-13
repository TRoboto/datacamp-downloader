import os
from pathlib import Path
from typing import List, Optional

import typer

from . import active_session, datacamp
from .helper import Logger
from .templates.lang import Language

__version__ = "3.1.0"


def version_callback(value: bool):
    if value:
        typer.echo(f"Datacamp Downloader CLI Version: {__version__}")
        raise typer.Exit()


def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version.",
    ),
):
    pass


app = typer.Typer(callback=main)


@app.command()
def login(
    username: str = typer.Option(..., "-u", "--username", prompt=True),
    password: str = typer.Option(..., "-p", "--password", prompt=True, hide_input=True),
):
    """Log in to Datacamp using your username and password."""
    datacamp.login(username, password)


@app.command()
def set_token(token: str = typer.Argument(...)):
    """Log in to Datacamp using your token."""
    datacamp.set_token(token)


@app.command()
def tracks(
    refresh: Optional[bool] = typer.Option(
        False, "--refresh", "-r", is_flag=True, help="Refresh completed tracks."
    )
):
    """List your completed tracks."""
    datacamp.list_completed_tracks(refresh)


@app.command()
def courses(
    refresh: Optional[bool] = typer.Option(
        False, "--refresh", "-r", is_flag=True, help="Refresh completed courses."
    )
):
    """List your completed courses."""
    datacamp.list_completed_courses(refresh)


@app.command()
def download(
    ids: List[str] = typer.Argument(
        ...,
        help="IDs for courses/tracks to download or `all` to download all your completed courses or `all-t` to download all your completed tracks.",
    ),
    path: Path = typer.Option(
        Path(os.getcwd() + "/Datacamp"),
        "--path",
        "-p",
        help="Path to the download directory.",
        dir_okay=True,
        file_okay=False,
    ),
    slides: Optional[bool] = typer.Option(
        True,
        "--slides/--no-slides",
        help="Download slides.",
    ),
    datasets: Optional[bool] = typer.Option(
        True,
        "--datasets/--no-datasets",
        help="Download datasets.",
    ),
    videos: Optional[bool] = typer.Option(
        True,
        "--videos/--no-videos",
        help="Download videos.",
    ),
    exercises: Optional[bool] = typer.Option(
        True,
        "--exercises/--no-exercises",
        help="Download exercises.",
    ),
    subtitles: Optional[List[Language]] = typer.Option(
        [Language.EN.value],
        "--subtitles",
        "-st",
        help="Choose subtitles to download.",
        case_sensitive=False,
    ),
    audios: Optional[bool] = typer.Option(
        False,
        "--audios/--no-audios",
        help="Download audio files.",
    ),
    scripts: Optional[bool] = typer.Option(
        True,
        "--scripts/--no-scripts",
        "--transcript/--no-transcript",
        show_default=True,
        help="Download scripts or transcripts.",
    ),
    python_file: Optional[bool] = typer.Option(
        True,
        "--python-file/--no-python-file",
        show_default=True,
        help="Download your own solution as a python file if available.",
    ),
    warnings: Optional[bool] = typer.Option(
        True,
        "--no-warnings",
        flag_value=False,
        is_flag=True,
        help="Disable warnings.",
    ),
    overwrite: Optional[bool] = typer.Option(
        False,
        "--overwrite",
        "-w",
        flag_value=True,
        is_flag=True,
        help="Overwrite files if exist.",
    ),
):
    """Download courses/tracks given their ids.

    Example: `datacamp download id1 id2 id3`\n
    To download all your completed courses run:
    \t`datacamp download all`\n
    To download all your completed tracks run:
    \t`datacamp download all-t`
    """
    Logger.show_warnings = warnings
    datacamp.download(
        ids,
        path,
        slides=slides,
        datasets=datasets,
        videos=videos,
        exercises=exercises,
        subtitles=subtitles,
        audios=audios,
        scripts=scripts,
        overwrite=overwrite,
        last_attempt=python_file,
    )


@app.command()
def reset():
    """Restart the session."""
    active_session.reset()
