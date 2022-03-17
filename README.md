

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
pip install -r requirements.txt
```

## Usage

You can run the scraper file web_scraping.py in the command line. 

```bash
usage: web_scraping.py [-h] [-not] [-tosql]
                       page_start page_stop sql_username sql_password sql_host

positional arguments:
  page_start            Scraping will start from this page
  page_stop             Scraping will stop at this page
  sql_username          Your sql username (commonly 'root')
  sql_password          Your sql password
  sql_host              Your sql hostname (commonly 'localhost')

optional arguments:
  -h, --help            show this help message and exit
  -not, --no_scrape_all
                        collect titles, urls and number of days left to bid
                        only
  -tosql, --tosql       export to freelancer sql database

additional information: the main url is "freelancer.com"
```

The file takes five arguments: page_start, page_stop, and the three necessary SQL information (username, password and host). 

There are hundreds of pages in the website. The user must specify which range she wants to scrape. 

The file gives two options:
* -not, --no_scrape_all : this allows to scrape data from the main page only, not from the sub-pages
* -tosql, --tosql: export to freelancer.db


For example, if user wants to get data from page 1 only, and export it to a sql database (freelancer) she must write the following command:
```bash
python3 web_scraping.py -tosql 1 1 username password localhost
```

## Access to db database
From the terminal, or MySQLWorkbench or other.


## Database Design
See the Entity Relationship Diagram (ERD) in the folder.
Tables:
* Job - information about title, days left to bid, job description, url
* Budget - info about the currency, per hour or not and min-max range of the budget
* BidderInfo - information on the bidder : url, rating and name
* CompetitionSet - a one to many (one?) relationship between a job and a competition
* Competition - information about the competition: average bid, currency, bid type and number of competitors
* SkillSet - a one to one relationship between a job and a skill set
* Skill - information about each skill (name)
* VerificationSet: a one to one relationship between a job and a verification set
* Verification : Boolean values : email, deposit and 


###### Future usage
Empty.

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