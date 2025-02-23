#BLUE TEAM: Vaneshiea Bell, Jess Monnier, DeJanae Faison
#Professor Sue Sampson
#Assignment 10 Milestone 2, 2/23/25
#Connect to SQL file
import mysql.connector
from mysql.connector import errorcode

#Connect to ENV file
import dotenv # to use .env file
from dotenv import dotenv_values


#Using ENV file
secrets = dotenv_values("env")

config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True #not in .env file

}

#test connection
try:
    """ try/catch block for handling potential MySQL database errors """ 

    db = mysql.connector.connect(**config) # connect to the database 
    
    # output the connection status 
    print("\n  Database user {} connected to MySQL on host {} with database {}".format(config["user"], config["host"], config["database"]))

    input("\n\n  Press any key to continue...")

except mysql.connector.Error as err:
    """ on error code """

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")

    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")

    else:
        print(err)

cursor = db.cursor()

#Display Contents from each table

#Display Customer
cursor.execute("SELECT * FROM customer")

customers = cursor.fetchall()
print("--Customers--")
for customer in customers:
    
    print(customer ,"\n")


#Display Staff
cursor.execute("SELECT * FROM staff")

employees = cursor.fetchall()
print("--Staff--")
for staff in employees:
    print(staff,"\n")



#Close the database
#finally:
    """ close the connection to MySQL """

   # db.close()