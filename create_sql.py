import pymysql.cursors
import csv
import tqdm


def main():
    def get_connection():
        """
        connects to the database.
        :return: connection
        """
        return pymysql.connect(host='localhost',
                               user='root',
                               password='1712541',
                               cursorclass=pymysql.cursors.DictCursor)

    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP DATABASE freelancer; ")

#  database freelancer
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE freelancer;")

# table job
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE jobs ( 
                    job_id INT ,
                    PRIMARY KEY(job_id),
                    title TEXT,
                    days_left_to_bid INT,
                    job_description TEXT,
                    url TEXT
                    ) ;""")

            sql11 = "INSERT INTO jobs \
        (job_id, title, days_left_to_bid, job_description, url) \
        VALUES (%s, %s, %s, %s, %s)"
            with open("output.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql11, (row['id'], row['titles'], row['days left to bid'], row['description'], row['url']))
                cursor.execute("COMMIT")

    # budgets
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE budgets ( 
                    job_id INT,
                    currency VARCHAR(20),
                    per_hour TEXT,
                    min_value TEXT,
                    max_value TEXT
                    ) ;""")

            cursor.execute("USE freelancer;")
            sql11 = "INSERT INTO budgets \
        (job_id, currency, min_value, max_value, per_hour) \
        VALUES (%s, %s, %s, %s, %s)"
            sql_commit = "COMMIT"
            with open("output.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql11, (row['id'], row['currency'], row['min_value'], row['max_value'], row['per_hour']))
                cursor.execute(sql_commit)


    # table verif_catalogue
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE verif_catalogue ( 
                    verif_id INT ,
                    PRIMARY KEY(verif_id),
                    elements_verified TEXT
                    ) ;""")

            sql11 = "INSERT INTO verif_catalogue \
        (verif_id, elements_verified) \
        VALUES (%s, %s)"
            with open("traits_id.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    for trait in row:
                        cursor.execute(sql11, (row[trait], trait))
                cursor.execute(sql_commit)
                cursor.execute("COMMIT")

    # verifications
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE verifications ( 
                    verif_id TEXT,
                    job_id INT
                    ) ;""")

            sql11 = "INSERT INTO verifications \
        (verif_id, job_id) \
        VALUES (%s, %s)"
            sql_commit = "COMMIT"
            with open("verifications.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql11, (row["element_id"], row['index']))

                cursor.execute(sql_commit)

# skills

    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE skills_catalogue ( 
                    skill_id INT ,
                    name TEXT
                    ) ;""")

            sql11 = "INSERT INTO skills_catalogue \
        (skill_id, name) \
        VALUES (%s, %s)"
            with open("skills_id.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    for skill in row:
                        cursor.execute(sql11, (row[skill], skill))
                cursor.execute(sql_commit)
                cursor.execute("COMMIT")

    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("USE freelancer;")
            cursor.execute("""CREATE TABLE skills ( 
                    skill_id INT,
                    job_id INT
                    ) ;""")

            sql11 = "INSERT INTO skills \
        (skill_id, job_id) \
        VALUES (%s, %s)"
            sql_commit = "COMMIT"
            with open("skills.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute(sql11, (row["element_id"], row['index']))
                cursor.execute(sql_commit)


if __name__ == "__main__":
    main()
