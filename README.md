

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
  -tosql, --tosql       export to freelancer sql database

additional information: the main url is "freelancer.com"
```

The file takes five arguments: page_start, page_stop, and the three necessary SQL information (username, password and host). 

There are hundreds of pages in the website. The user must specify which range she wants to scrape. 

The file gives one option:
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
* CompetitionSet - a correspondence between a job and a competitor
* Competition - information about the bidders: average url and rating
* SkillSet - a correspondence between a job and skills
* Skill - information about each skill (name)
* VerificationSet: a correspondence between a job and verifications
* Verification : Boolean values : email, deposit and payment


###### Future usage
Empty.

## Data cleaning process
There is no general rule. The data is clean.

We identified, for bids and budget, the currency, the type of payment (per hour or fixed range) and the amount.

## Project status
This is a work in progress.

## Roadmap
Four checkpoints in total.
This part checks the second checkpoint. Two more to go.

## Authors and acknowledgement 
The authors of this web scraper are Shai Duchan and Ilan Pargamin.
It is part of the Israel Tech Challenge 2-month data mining project, data science 2022 cohort.