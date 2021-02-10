# Konin flats scraper
Gather flats advertisements from local Konin websites.


## Table of contents
* [General info](#general-info)
* [Setup](#setup)
* [Usage](#usage)
* [Technologies](#technologies)


## General info
Application gathers flats advertisements from local Konin websites and then 
put new advertisements into html template. Results are available at:

https://www.mieszkania.retip1994.usermd.net/

(I am aware that website is very slow due to lack of pagination, 
but for me it was more convenient to browse ads this way)

Scraping is performed with use of multiprocessing, what makes it much faster.

## Setup
* Make sure you have Python 3.7+ installed. (I developed it with Python 3.7)
* Some Python modules are required which are contained in requirements.txt and will be installed below.

#### 1. Requirements
In the mieszkania-konin-scraper folder, run:

`python -m pip install -r requirements.txt`

Adapt the command to your operating system if needed.

#### 2. Scraper setup
You can change scraper settings in config.py file

## Usage
Open cmd in scraper folder and run script by:

`python main.py`



## Technologies
Project is created with:
* Python 3.7
* requests
* pandas
* Jinja2
* BeautifulSoup

## [License](https://github.com/retip94/konin-flats-scraper/blob/master/LICENSE.md)

MIT © [Piotr Piekielny](https://github.com/retip94)

