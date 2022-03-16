

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
usage: web_scraping.py [-h] [-not] [-tosql] [-tocsv]
                       page_start page_stop directory_path

positional arguments:
  page_start
  page_stop
  directory_path

optional arguments:
  -h, --help            show this help message and exit
  -not, --no_scrape_all
                        collect titles, urls and number of days left to bid
                        only
  -tosql, --tosql       export to freelancer.db
  -tocsv, --tocsv       export to freelancer.csv

additional information: If neither -tocsv nor -csv are specified, the scraper
does not export the data to any file
```

The file takes three arguments: page_start, page_stop and directory_path. 

There are hundreds of pages in the website. The user must specify which range she wants to scrape. 

The directory_path is where the output file will be exported.

The file gives three options:
* -not, --no_scrape_all : this allows to scrape data from the main page only, not from the sub-pages
* -tosql, --tosql: export to freelancer.db
* -tocsv, --tocsv: export to freelancer.csv

For example, if user wants to get  data from the main page and the sub-pages, from page 1 to 5, and export in a csv file in the directory whose path is "directory_path" she must write the following command:
```bash
python3 web_scraping.py -tocsv 1 5 directory_path
```

For example, if user wants to get data from the main page only, from page 1 only, and export it to a db file (database) she must write the following command:
```bash
python3 web_scraping.py -not -tosql 1 1 directory_path
```

## Access to db database
In the terminal, write the command:
```bash
sqlite3
```
and 
```bash
.open freelancer.db
```

To check that the database exists, write
```bash
.tables
```
The output should look like:

```bash
BudgetInfo       Job              SkillSet         VerificationSet
BudgetSet        Skill            Verification
```



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