

# web_scraping_freelance

***web_scraping_freelance*** is a web scraping tool. The website target is https://www.freelancer.com. 

## data collection
The scraper collects the following data:
1. main page : https://www.freelancer.com/jobs/
- jot titles
- time left to make a bid
 - job url
2. job page : https://www.freelancer.com/projects/project_type/project_title-project_id 
- rating of the employer
- budget of the employer
- required skills
- job description
- verified traits of the employer
- average bid
- list of bidders:
-    * rating
-    * link to profile


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required modules.

```bash
pip install requirements.txt
```

## Usage

You can run the scraper file web_scraping_freelance.py in the command line. 

The output of the file is the csv file output.csv (for now).
```bash
usage: web_scraping.py [-h] [-not] [-tosql]
                       page_start page_stop directory_path

positional arguments:
  page_start
  page_stop
  directory_path

optional arguments:
  -h, --help            show this help message and exit
  -not, --no_scrape_all
  -tosql, --tosql
```

The file takes two arguments: page_start and page_stop. There are hundreds of pages in the website. The user must specify which range she wants to scrape.

The file gives two options:
* -not, --no_scrape_all : this allows to scrape data from the main page only, not from the sub-pages

For example, if user wants to get  data from the main page and the sub-pages, from page 1 to 5, she must write the following command:
```bash
python3 web_scraping.py 1 5
```

For example, if user wants to get data from the main page only, from page 1 only, she must write the following command:
```bash
python3 web_scraping.py -not 1 1
```


###### Future usage

## Data cleaning process
There is no general rule.

We identified, for bids and budget, the currency, the type of payment (per hour or fixed range) and the amount.

## Project status
This is a work in progress.

## Roadmap
Four checkpoints in total.
This part checks the second checkpoint. Two more to go.

## Authors and acknowledgement 
The authors of this web scraper are Shai Duchan and Ilan Pargamin.
It is part of the Israel Tech Challenge 2-month data mining project, data science 2022 cohort.