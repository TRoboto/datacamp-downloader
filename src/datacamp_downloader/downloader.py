import click
from . import datacamp, session


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
@click.option("--refresh/--no-refresh", default=False)
def tracks(refresh):
    """List your completed tracks."""
    datacamp.list_completed_tracks(refresh)


@main.command()
def reset():
    """Restart the session."""
    session.restart()


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
