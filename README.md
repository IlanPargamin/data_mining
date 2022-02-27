

# web_scraping_freelance

web_scraping_freelance is a web scraping tool. The website target is https://www.freelancer.com. 

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
pip install requirements.txt
```

## Usage

You can run the scraper file web_scraping_freelance.py in the command line. The first argument argument is the (existing or not) csv file where you want to save the collected data.

If the csv file exists, it will be overwritten. 

```bash
python web_scraping_freelance.py my_csv_file
```

###### Future usage
in the future, we should be able to put arguments as for the elements that we do not want to scrape.
Ex:
If user does not want to collect data on bid and job descriptions:
```bash
python web_scraping_freelance.py my_csv_file bid job_description
```

## Project status
This is a work in progress.

## Roadmap
Four checkpoints in total.
This part checks the first checkpoint. Three more to go.

## Authors and acknowledgement 
The authors of this web scraper are Shai Duchan and Ilan Pargamin.
It is part of the Israel Tech Challenge 2-month data mining project, data science 2022 cohort.