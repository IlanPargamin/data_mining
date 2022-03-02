

# web_scraping_freelance

***web_scraping_freelance*** is a web scraping tool. The website target is https://www.freelancer.com. 

## data collection
The scraper collects the following data:
    1. main page : https://www.freelancer.com/jobs/
        - jot titles
        - time left to make a bid
        - job description
        - average bid
        - tags
    2. job page : https://www.freelancer.com/projects/project_type/project_title-project_id 
        - rating of the employer
        - location of the employer
        - other job offers from this employer
        - similar jobs
        - list of bidders:
            * name
            * description
            * review
            * link to profile


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required modules.

```bash
pip install -r requirements.txt
```

## Usage

In the file globals.py, you can choose the first and last page of the webiste to scrape.

You can run the scraper file web_scraping_freelance.py in the command line. 

```bash
python web_scraping_freelance.py 
```

The output, a list of dictionaries, is extracted in the file output.log.

###### Future usage
in the future, we should be able to put arguments as for the elements that we do not want to scrape.

Ex:
If user does not want to collect data on bid and job descriptions:

```bash
python web_scraping_freelance.py bid job_description
```

## Project status
This is a work in progress.

## Roadmap
Four checkpoints in total.
This part checks the first checkpoint. Three more to go.

## Authors and acknowledgement 
The authors of this web scraper are Shai Duchan and Ilan Pargamin.
It is part of the Israel Tech Challenge 2-month data mining project, data science 2022 cohort.