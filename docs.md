# `datacamp`

**Usage**:

```console
$ datacamp [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--version`: Show version.
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `courses`: List your completed courses.
- `download`: Download courses/tracks given their ids.
- `login`: Log in to Datacamp using your username and password
- `reset`: Restart the session.
- `set-token`: Log in to Datacamp using your token.
- `tracks`: List your completed tracks.

## `datacamp login`

Log in to Datacamp using your username and password.

**Usage**:

```console
$ datacamp login [OPTIONS]
```

**Options**:

- `-u, --username TEXT`: [required]
- `-p, --password TEXT`: [required]
- `--help`: Show this message and exit.

## `datacamp set-token`

Log in to Datacamp using your token.

**Usage**:

```console
$ datacamp set-token [OPTIONS] TOKEN
```

**Arguments**:

- `TOKEN`: [required]

**Options**:

- `--help`: Show this message and exit.

## `datacamp courses`

List your completed courses.

**Usage**:

```console
$ datacamp courses [OPTIONS]
```

**Options**:

- `-r, --refresh`: Refresh completed courses. [default: False]
- `--help`: Show this message and exit.

## `datacamp tracks`

List your completed tracks.

**Usage**:

```console
$ datacamp tracks [OPTIONS]
```

**Options**:

- `-r, --refresh`: Refresh completed tracks. [default: False]
- `--help`: Show this message and exit.

## `datacamp download`

Download courses/tracks given their ids.

Example: `datacamp download id1 id2 id3`

To download all your completed courses run:
`datacamp download all`

To download all your completed tracks run:
`datacamp download all-t`

**Usage**:

```console
$ datacamp download [OPTIONS] IDS...
```

**Arguments**:

- `IDS...`: IDs for courses/tracks to download or `all` to download all your completed courses or `all-t` to download all your completed tracks. [required]

**Options**:

- `-p, --path DIRECTORY`: Path to the download directory. [default: `current_directory/Datacamp`]
- `--slides / --no-slides`: Download slides. [default: True]
- `--datasets / --no-datasets`: Download datasets. [default: True]
- `--videos / --no-videos`: Download videos. [default: True]
- `--exercises / --no-exercises`: Download exercises. [default: True]
- `-st, --subtitles [en|zh|fr|de|it|ja|ko|pt|ru|es|none]`: Choose subtitles to download. [default: en]
- `--audios / --no-audios`: Download audio files. [default: False]
- `--scripts, --transcript / --no-scripts, --no-transcript`: Download scripts or transcripts. [default: True]
- `--python-file / --no-python-file`: Download your own solution as a python file if available. [default: True]
- `--no-warnings`: Disable warnings. [default: True]
- `-w, --overwrite`: Overwrite files if exist. [default: False]
- `--help`: Show this message and exit.

## `datacamp reset`

Restart the session.

**Usage**:

```console
$ datacamp reset [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.
