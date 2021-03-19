import click

from .helper import Logger
from . import datacamp, active_session
import os


@click.group()
def main():
    pass


@main.command()
@click.option("--username", "-u", prompt=True)
@click.option("--password", "-p", prompt=True, hide_input=True)
def login(username, password):
    """Log in to Datacamp using your username and password."""
    datacamp.login(username, password)


@main.command()
@click.option("--token", "-t", prompt=True, hide_input=True)
def set_token(token):
    """Log in to Datacamp using your token."""
    datacamp.set_token(token)


@main.command()
@click.option("--refresh", is_flag=True, help="Refresh completed tracks.")
def tracks(refresh):
    """List your completed tracks."""
    datacamp.list_completed_tracks(refresh)


@main.command()
@click.option("--refresh", is_flag=True, help="Refresh completed courses.")
def courses(refresh):
    """List your completed courses."""
    datacamp.list_completed_courses(refresh)


@main.command()
@click.argument("courses_ids", nargs=-1, required=True)
@click.option(
    "--path",
    "-p",
    required=True,
    type=click.Path(dir_okay=True, file_okay=False),
    help="Path to the download directory",
    default=os.getcwd() + "/Datcamp",
    show_default=True,
)
@click.option(
    "--slides/--no-slides",
    default=True,
    help="Download slides.",
    show_default=True,
)
@click.option(
    "--datasets/--no-datasets",
    default=True,
    help="Download datasets.",
    show_default=True,
)
@click.option(
    "--videos/--no-videos",
    default=True,
    help="Download videos.",
    show_default=True,
)
@click.option(
    "--exercises/--no-exercises",
    default=True,
    help="Download exercises.",
    show_default=True,
)
@click.option(
    "--subtitles",
    "-st",
    default=("en",),
    multiple=True,
    type=click.Choice(["en", "zh", "fr", "de", "it", "ja", "ko", "pt", "ru", "es"]),
    help="Choice subtitles to download.",
    show_default=True,
)
@click.option(
    "--audios/--no-audios",
    default=False,
    help="Download audio files.",
    show_default=True,
)
@click.option(
    "--scripts/--no-scripts",
    "--transcript/--no-transcript",
    default=True,
    show_default=True,
    help="Download scripts or transcripts",
)
@click.option(
    "--no-warnings",
    "warnings",
    flag_value=False,
    is_flag=True,
    default=True,
    help="Disable warnings.",
)
def download(
    courses_ids,
    path,
    slides,
    datasets,
    videos,
    exercises,
    subtitles,
    audios,
    scripts,
    warnings,
):
    """Download courses given their ids.

    Example: datacamp download id1 id2 id3
    To download all your completed courses run:
    ```
    datacamp download all
    ```
    """
    Logger.show_warnings = warnings
    datacamp.download_courses(
        courses_ids,
        path,
        slides,
        datasets,
        videos,
        exercises,
        subtitles,
        audios,
        scripts,
    )


@main.command()
def reset():
    """Restart the session."""
    active_session.restart()


if __name__ == "__main__":
    main()