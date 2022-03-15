"""
This file, imported in web_scraping, creates the sql database based on a list of dictionaries with the scraped data
from freelancer.com.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cleaner import cleaner

# TODO write README - explain each table + design database table
# TODO do not create database if already exists


def create_sql(dict_merged, directory_path):
    """
    Given dict_merged, a list of dictionaries with the scraped data from freelancer.com, and a dicrectory path,
    the function creates a sql database freelancer.db in the given directory.
    Each class is a table in the database.
    """
    # clean dictionaries
    dict_merged = cleaner(dict_merged)

    # initialize database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + directory_path + '/freelancer.db'
    db = SQLAlchemy(app)
    db.init_app(app)

    # create tables (each class is a table)
    class Job(db.Model):
        __tablename__ = 'Job'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        days_left_to_bid = db.Column(db.Integer)
        job_description = db.Column(db.String(100))
        url = db.Column(db.String(100), nullable=False)

    class SkillSet(db.Model):
        __tablename__ = 'SkillSet'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        job_id = db.Column(db.Integer, db.ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = db.relationship('Job', backref=db.backref('SkillSet', lazy=True))

    class Skill(db.Model):
        __tablename__ = 'Skill'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        skill_set_id = db.Column(db.Integer, db.ForeignKey('SkillSet.id'), nullable=False)
        name = db.Column(db.String(100))

        # Initialize the relationship
        skillset = db.relationship('SkillSet', backref=db.backref('Skill', lazy=True))

    class BudgetSet(db.Model):
        __tablename__ = 'BudgetSet'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        job_id = db.Column(db.Integer, db.ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = db.relationship('Job', backref=db.backref('BudgetSet', lazy=True))

    class BudgetInfo(db.Model):
        __tablename__ = 'BudgetInfo'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        budgets_id = db.Column(db.Integer, db.ForeignKey('BudgetSet.id'), nullable=False)
        currency = db.Column(db.String(100))
        per_hour = db.Column(db.String(100))
        min = db.Column(db.Integer)
        max = db.Column(db.Integer)

        # Initialize the relationship
        budget_set = db.relationship('BudgetSet', backref=db.backref('BudgetInfo', lazy=True))

    class VerificationSet(db.Model):
        __tablename__ = 'VerificationSet'
        # Initialize the Column
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        job_id = db.Column(db.Integer, db.ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = db.relationship('Job', backref=db.backref('VerificationSet', lazy=True))

    class Verification(db.Model):
        __tablename__ = 'Verification'
        # Initialize the Column (there should be 9 lines in this table
        id = db.Column(db.Integer, nullable=False, primary_key=True)
        verifications_id = db.Column(db.Integer, db.ForeignKey('VerificationSet.id'), nullable=False)
        name = db.Column(db.String(100))

        # Initialize the relationship
        verification_set = db.relationship('VerificationSet', backref=db.backref('Verification', lazy=True))

    # create database if does not exist
    # TODO add condition if database already exists -> update it
    db.create_all()

    # insert values from dict_merged
    for a_dict in dict_merged:
        # job
        job = Job(title=a_dict["titles"],
                  days_left_to_bid=a_dict["days left to bid"],
                  job_description=a_dict["description"],
                  url=a_dict["url"])
        db.session.add(job)

        # budgets
        budget_set = BudgetSet(job=job)
        db.session.add(budget_set)

        # budget
        budget = BudgetInfo(budget_set=budget_set,
                            currency=a_dict["currency"],
                            per_hour=a_dict["per_hour"],
                            min=a_dict["min_value"],
                            max=a_dict["max_value"])
        db.session.add(budget)

        # skills
        skill_set = SkillSet(job=job)
        db.session.add(skill_set)

        # add skill in catalogue
        for my_skill in [x.strip() for x in a_dict["skills"].split(',')]:
            skill = Skill(skillset=skill_set,
                          name=my_skill)
            db.session.add(skill)

        # verifications
        verification_set = VerificationSet(job=job)
        db.session.add(verification_set)

        # add verification in catalogue
        for my_verif in a_dict["verified_traits_list"]:
            verification = Verification(verification_set=verification_set,
                                        name=my_verif)
            db.session.add(verification)

    # Insert to the database
    db.session.commit()

