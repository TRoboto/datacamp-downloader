# Datacamp Downloader
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/TRoboto/datacamp-downloader/blob/master/LICENSE)  

**Docker version of this repo can be found [here](https://github.com/amughrabi/datacamp-downloader)**

## Table of Contents
- [Datacamp Downloader](#datacamp-downloader)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Instructions](#instructions)
    - [Installation](#installation)
    - [Commands](#commands)
    - [How to use](#how-to-use)
  - [Disclaimer](#disclaimer)

## Description
Datacamp Downloader is a command-line interface tool developed in Python
in order to help you download your completed contents on [Datacamp](https://datacamp.com) 
and keep them locally on your computer.  

Datacamp Downloader helps you download all videos, slides and some additional
contents if available (e.g. datasets) and organize them in folders.

The design and development of this tool was inspired by [udacimak](https://github.com/udacimak/udacimak)

**Support!**  
If you find this CLI helpful, please support the developers by starring this repository.

## Instructions

### Installation
1. Download this repository or clone it using:
```
git clone https://github.com/TRoboto/datacamp-downloader
```
2. Open the terminal and change the current working directory to the location where you downloaded/cloned the repo, run:
```
cd PATH
```
3. Download the required dependancies, run:
```
pip install -r requirements.txt
```
### Commands
`settoken`: **Set Datacamp authentication token**.  
`list` : List your completed **tracks**.  
`listc` : List your completed **courses**.  
`download` : Download **slides** and any available additional contents.  
`downloadv` : Download **videos, slides** and any available additional contents.

### How to use
1. First you should configure your token to be able to download your contents, run:
```
python downloader.py settoken YOUR_DATACAMP_AUTH_TOKEN
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

**Security Note**  
Datacamp authentication token is a secret key and is unique to you. **You should not share it publicly**.

Then if you have an active subscription, you should see the following:
```
====================================================================================================
Hi, YOUR_NAME
Active subscription found
====================================================================================================
Use the following commands in order.
1. list : to print your completed tracks.
or listc : to print your completed courses.
2. download followed by the destination and the id(s) of the track(s)/course(s).
This command downloads slides only.
or downloadv followed by the destination and the id(s) of the track(s)/course(s).
This command downloads both slides and videos.
Note: you can type 1-13 in the download command to download courses from 1 to 13.
====================================================================================================
Example to print your completed tracks.
>> list
1. Introduction to Databases in Python
2. Building Chatbots in Python
>>> downloadv 'C:/' 2
====================================================================================================
```
2. To list your completed track(s), run:
```
>> list
```
or to list your completed course(s), run:
```
>> listc
```
You should each course/track has a unique number as follows:
```
1. FIRST_COURSE
2. SECOND_COURSE
3. THIRD_COURSE
```
3. To download the **slides** and any available additional contents, run:
```
>>> download 'DOWNLOAD_PATH' COURSE_ID(s)
```
or to download the **slides, videos** and any available additional contents, run:
```
>>> downloadv 'DOWNLOAD_PATH' COURSE_ID(s)
```

**Example**  
To download the second course directly on `C` drive, run:
```
>>> download 'C:/' 1
```
To download the first and the third course directly on `C` drive, run:
```
>>> download 'C:/' 1 3
```
To download all three courses directly on `C` drive, run:
```
>>> download 'C:/' 1-3
```
where `1-3` is the range of the courses you want to download.

## Disclaimer
This CLI is provided to help you download Datacamp courses for personal use only. Sharing the content of the courses is strictly prohibited under [Datacamp's Terms of Use](https://www.datacamp.com/terms-of-use/).

By using this CLI, the developers of this CLI are not responsible for any law infringement caused by the users of this CLI.
