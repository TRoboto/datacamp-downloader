# Datacamp Downloader

[![GitHub license](https://img.shields.io/github/license/TRoboto/datacamp-downloader)](https://github.com/TRoboto/datacamp-downloader/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/TRoboto/datacamp-downloader)](https://github.com/TRoboto/datacamp-downloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/TRoboto/datacamp-downloader)](https://github.com/TRoboto/datacamp-downloader/network)
[![GitHub contributors](https://img.shields.io/github/contributors/TRoboto/datacamp-downloader)](https://github.com/TRoboto/datacamp-downloader/graphs/contributors)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](docs.md)

## Table of Contents

- [Datacamp Downloader](#datacamp-downloader)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
    - [PIP](#pip)
    - [From source](#from-source)
    - [Autocompletion](#autocompletion)
  - [Documentation](#documentation)
  - [Getting Started](#getting-started)
    - [Login](#login)
    - [Download](#download)
  - [User Privacy](#user-privacy)
  - [Disclaimer](#disclaimer)

## Description

Datacamp Downloader is a command-line interface tool developed in Python
in order to help you download your completed contents on [Datacamp](https://datacamp.com)
and keep them locally on your computer.

Datacamp Downloader helps you download all videos, slides, audios, exercises, transcripts, datasets and subtitles in organized folders.

The design and development of this tool was inspired by [udacimak](https://github.com/udacimak/udacimak)

**Datacampers!**

If you find this CLI helpful, please support the developers by starring this repository.

## Installation

### PIP

If you use pip, you can install datacamp-downloader with:

```bash
pip install datacamp-downloader
```

### From source

You can directly clone this repo and install the tool. First clone the repo with:

```bash
git clone https://github.com/TRoboto/datacamp-downloader.git
```

Then cd to the directory and install the tool with:

```bash
pip install .
```

### Autocompletion

To allow command autocompletion with `[TAB][TAB]`, run:

```bash
datacamp --install-autocompletion
```

Then restart the terminal.

**Note:** autocompletion might not be supported by all operating systems.

## Documentation

The available commands with full documentation can be found in [docs](docs.md)

## Getting Started

---

**IMPORTANT**

You must have a Datacamp account with **active** subscription to use the tool.

---

### Login

- To login using your username or password, run:

```bash
datacamp login -u [USERNAME] -p [PASSWORD]
```

or simply run:

```bash
datacamp login
```

- To login using Datacamp authentication token, run:

```bash
datacamp set-token [TOKEN]
```

Datacamp authentication token can be found in Datacamp website browser _cookies_.
To get your Datacamp authentication, follow these steps:

**Firefox**

1. Visit [datacamp.com](https://datacamp.com) and log in.
2. Open the **Developer Tools** (press `Cmd + Opt + J` on MacOS or `F12` on Windows).
3. Go to **Storage tab**, then **Cookies** > `https://www.datacamp.com`
4. Find `_dct` key, its **Value** is the Datacamp authentication token.

**Chrome**

1. Visit [datacamp.com](https://datacamp.com) and log in.
2. Open the **Developer Tools** (press `Cmd + Opt + J` on MacOS or `F12` on Windows).
3. Go to **Application tab**, then **Storage** > **Cookies** > `https://www.datacamp.com`
4. Find `_dct` key, its **Value** is the Datacamp authentication token.

---

**Security Note**

Datacamp authentication token is a secret key and is unique to you. **You should not share it publicly**.

---

If you provided valid credentials, you should see the following:

```text
Hi, YOUR_NAME
Active subscription found
```

### Download

First, you should list your completed courses/track.

To list your completed **courses**, run:

```bash
datacamp courses
```

To list your completed **tracks**, run:

```bash
datacamp tracks
```

Similar output to this should appear with your completed courses/tracks:

```text
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| #  |  ID   |                        Title                        | Datasets | Exercises | Videos |
+====+=======+=====================================================+==========+===========+========+
| 1  | 799   | Intermediate Python                                 | 3        | 69        | 18     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 2  | 15876 | Writing Functions in Python                         | 0        | 31        | 15     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 3  | 14630 | Writing Efficient Code with pandas                  | 3        | 31        | 14     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 4  | 1550  | Statistical Thinking in Python (Part 2)             | 10       | 51        | 15     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 5  | 13369 | Writing Efficient Python Code                       | 1        | 38        | 15     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 6  | 15108 | Introduction to TensorFlow in Python                | 3        | 36        | 15     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 7  | 15974 | Unit Testing for Data Science in Python             | 0        | 38        | 17     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 8  | 14336 | Feature Engineering for Machine Learning in Python  | 2        | 37        | 16     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 9  | 16921 | Image Processing in Python                          | 1        | 38        | 16     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
| 10 | 15162 | Model Validation in Python                          | 2        | 32        | 15     |
+----+-------+-----------------------------------------------------+----------+-----------+--------+
```

Now, you can download any of the courses/tracks with:

```bash
datacamp download id1 id2 id3
```

For example to download the first and fifth course, run:

```bash
datacamp download 799 13369
```

- To download all your completed courses, run:

```bash
datacamp download all
```

- To download all your completed tracks, run:

```bash
datacamp download all-t
```

This by default will download **videos**, **slides**, **datasets**, **exercises**, **english subtitles** and **transcripts** in organized folders in the **current directory**.

To customize this behavior see `datacamp download` command in the [docs](docs.md).

## User Privacy

`datacamp` creates a session file with your credentials saved in the temp folder. If you no longer need to use the tool, it is preferable to reset the session, which will remove the saved file, with:

```bash
datacamp reset
```

## Disclaimer

This CLI is provided to help you download Datacamp courses/tracks for personal use only. Sharing the content of the courses is strictly prohibited under [Datacamp's Terms of Use](https://www.datacamp.com/terms-of-use/).

By using this CLI, the developers of this CLI are not responsible for any law infringement caused by the users of this CLI.
