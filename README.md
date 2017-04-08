OpenSubtitlesDownloadQt.py
==========================

[![GitHub release](https://img.shields.io/github/release/emericg/OpenSubtitlesDownloadQt.svg?style=flat-square)](https://github.com/emericg/OpenSubtitlesDownloadQt/releases)
[![GitHub contributors](https://img.shields.io/github/contributors/emericg/OpenSubtitlesDownloadQt.svg?style=flat-square)](https://github.com/emericg/OpenSubtitlesDownloadQt/graphs/contributors)
[![GitHub issues](https://img.shields.io/github/issues/emericg/OpenSubtitlesDownloadQt.svg?style=flat-square)](https://github.com/emericg/OpenSubtitlesDownloadQt/issues)
[![License: GPL v3](https://img.shields.io/badge/license-GPL%20v3-brightgreen.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0)

Introduction
------------

**OpenSubtitlesDownloadQt.py** is a small software written in python, built to help you **quickly find and download subtitles for your favorite videos**. It can be used as a nautilus script, or as a regular application working under GNOME or KDE desktop environments.  
It's a **fork** of [OpenSubtitlesDownload](https://github.com/emericg/OpenSubtitlesDownload) version 3.6, but using only a pyQt5 GUI and dropping python 2 support.

The subtitles search is done by precisly **identifying your video files** by computing unique movie hash sums. This way, you have more chance to find the **exact subtitles for your videos**, avoiding synchronization problems between the subtitles and the soundtrack. But what if that doesn't work? Well, a search with the filename will be performed, but be aware: results are a bit more... unpredictable (don't worry, you will be warned! and you can even disable this feature if you want).

The subtitles search and download service is powered by [opensubtitles.org](http://www.opensubtitles.org). Big thanks to their hard work on this amazing project! Be sure to [give them your support](http://www.opensubtitles.org/en/support) if you appreciate the service provided, they sure need donations for handling the ever growing hosting costs!

Features
--------

- Use a nice Qt5 GUI.
- Query subtitles in more than 60 different languages for documentaries, movies, TV shows and more...
- Query subtitles in multiple languages at once.
- Query subtitles for multiple video files at once.
- Detect valid video files (using mime types and file extensions).
- Detect correct video titles by computing unique movie hash sums in order to download the right subtitles for the right file!
- If the video detection fails, search by filename will be performed as backup method.
- Download subtitles automatically if only one is available, choose the one you want otherwise.
- Rename downloaded subtitles to match source video file. Possibility to append the language code to the file name (ex: movie_en.srt).

Requirements
------------

- python (version 3 only!)
- PyQt5
- common unix tools: wget & gzip (subtitles downloading)

Installation
------------

Quick installation as a nautilus script, under GNOME 3 desktop environment:

> $ git clone https://github.com/emericg/OpenSubtitlesDownloadQt.git  
> $ mkdir -p ~/.local/share/nautilus/scripts/  
> $ cp OpenSubtitlesDownloadQt/OpenSubtitlesDownloadQt.py ~/.local/share/nautilus/scripts/OpenSubtitlesDownloadQt.py  
> $ chmod u+x ~/.local/share/nautilus/scripts/OpenSubtitlesDownloadQt.py  

Website
-------

You can browse the project's GitHub page at <https://github.com/emericg/OpenSubtitlesDownloadQt>  
Learn much more about OpenSubtitlesDownloadQt.py installation and configuration on its wiki at <https://github.com/emericg/OpenSubtitlesDownloadQt/wiki>  

Contributors
------------

- Emeric Grange <emeric.grange@gmail.com> maintainer
- LenuX for his work on the Qt5 GUI
- jeroenvdw for his work on the 'subtitles automatic selection' and the 'search by filename'
- Gui13 for his work on the arguments parsing
- Tomáš Hnyk <tomashnyk@gmail.com> for his work on the 'multiple language' feature
- Carlos Acedo <carlos@linux-labs.net> for his work on the original script

License
-------

OpenSubtitlesDownloadQt.py is a free software released under the GPL v3 license <http://www.gnu.org/licenses/gpl-3.0.txt>

Screenshots!
------------

![Start subtitles search](https://raw.githubusercontent.com/emericg/OpenSubtitlesDownloadQt/screenshots/osd_screenshot_launch.png)

![Download selected subtitles](https://raw.githubusercontent.com/emericg/OpenSubtitlesDownloadQt/screenshots/osd_screenshot_autodownload.png)

Enjoy your subtitled video!
![Enjoy your subtitled video!](https://raw.githubusercontent.com/emericg/OpenSubtitlesDownloadQt/screenshots/enjoy-sintel.jpg)

What if multiple subtitles are available? Just pick one from the list!
![Multiple subtitles selection](https://raw.githubusercontent.com/emericg/OpenSubtitlesDownloadQt/screenshots/osd_screenshot_selection.png)
