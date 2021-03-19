import click

from datacamp_downloader.helper import Logger
from . import datacamp, active_session
import os


@click.group()
def main():
    pass


@main.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(username, password):
    """Log in to Datacamp using your username and password."""
    datacamp.login(username, password)


@main.command()
@click.option("--token", prompt=True, hide_input=True)
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
@click.option("--slides/--no-slides", default=True, help="Download slides.")
@click.option("--datasets/--no-datasets", default=True, help="Download datasets.")
@click.option("--videos/--no-videos", default=True, help="Download videos.")
@click.option("--exercises/--no-exercises", default=True, help="Download exercises.")
@click.option("--subtitle/--no-subtitle", default=True, help="Download subtitle.")
@click.option("--audios", default=False, help="Download audio files if available.")
@click.option(
    "--scripts", "--transcript", default=True, help="Download scripts or transcripts"
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
    subtitle,
    audios,
    scripts,
    warnings,
):
    """Download courses given their ids.

    Example: datacamp download id1 id2 id3
    """
    Logger.show_warnings = warnings
    datacamp.download_courses(
        courses_ids,
        path,
        slides,
        datasets,
        videos,
        exercises,
        subtitle,
        audios,
        scripts,
    )


@main.command()
def reset():
    """Restart the session."""
    active_session.restart()


if __name__ == "__main__":
    main()


# def login_parser():
#     parser = ArgumentParser()
#     parser.add_argument("-t", "--token", required=True, type=str,
#                         help="Specify your Datacamp authentication token.")
#     parser.add_argument("-l", "--list", required=True, type=str,
#                         help="List completed (T) for tracks, (C) for courses")
#     parser.add_argument("-p", "--path", required=False, default=os.getcwd(), type=str,
#                         help="Path to download the contents, default is the current directory")
#     parser.add_argument("-v", "--video", action='store_true',
#                         help="Include it if you want to download the videos")
#     parser.add_argument("-e", "--exercise", action='store_true',
#                         help="Include it if you want to download the exercises")
#     parser.add_argument("-d", "--dataset", action='store_true',
#                         help="Include it if you want to download the datasets")
#     parser.add_argument("-a", "--all", action='store_true',
#                         help="Include it if you want to download all the track/course and data")
#     return parser
