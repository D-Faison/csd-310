#Blue Team
#Professor Sue
#Are there inventory items (we extrapolated this to mean specifically rental equipment) more than 5 years old?

import mysql.connector
from mysql.connector import errorcode
import os

# Connect to .env file
from dotenv import dotenv_values

# Get the directory of the script so we don't have to execute 
# the script from that directory for the .env file to work
working_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(working_dir)

# Using ENV file
secrets = dotenv_values(".env")

config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True # not in .env file
}

# open connection with error checking
try:
    """ try/catch block for handling potential MySQL database errors """ 

    db = mysql.connector.connect(**config) # connect to the database 
    
    # output the connection status 
    print("\n  Database user {} connected to MySQL on host {} with database {}".format(config["user"], config["host"], config["database"]))

    input("\n\n  Press Enter to view the contents of the customer table...")

    # Get a database "cursor" to execute queries in our database
    cursor = db.cursor()

except mysql.connector.Error as err:
    """ on error code """

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")

    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")

    else:
        print(err)






#Display inventory items more than five years old
cursor.execute("SELECT rental_inventory.rental_id, rental_inventory.initial_use, order_inventory.name FROM rental_inventory INNER JOIN order_inventory ON rental_inventory.product_code = order_inventory.product_code HAVING initial_use < CURDATE() - INTERVAL 5 YEAR;")
inventoryAges = cursor.fetchall()
print("--Equipment more than 5 Years Old:")
for inventoryAge in inventoryAges:
        print("\nRental ID:{}".format(inventoryAge[0]))
        print("Name:{}".format(inventoryAge[2]))
        print("Initial Use:{}\n".format(inventoryAge[1]))
        

# Close the database
#finally:
    #""" close the connection to MySQL """

    #db.close()