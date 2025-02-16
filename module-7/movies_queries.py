#DeJanae Faison 2/16/24 Movies Table Queries
#Displaying the information from the sql movie database in a particular format
import mysql.connector
from mysql.connector import errorcode

import dotenv 
from dotenv import dotenv_values

#Using ENV file
secrets = dotenv_values("env")

#database config object
config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True #not in .env file
}
try:
    """ try/catch block for handling potential MySQL database errors """ 

    db = mysql.connector.connect(**config) # connect to the movies database 
    
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

#Display Studio
#studio name is index 0 and studio id is index 1
cursor.execute("SELECT studio_name, studio_id FROM studio")

studios = cursor.fetchall()
print("--DISPLAYING Studio RECORDS--")
for studio in studios:
    print("Studio ID:{}".format(studio[1]))
    print(f"Studio Name: {studio[0]}")
    print('')


#Display Genre 
cursor.execute("SELECT genre_id, genre_name FROM genre")

genres = cursor.fetchall()
print("--DISPLAYING Genre RECORDS--")
for genre in genres:
    print("Genre ID: {}".format(genre[0]))
    print("Genre Name: {}".format(genre[1]))
    print('')

#Display SHORT movies
cursor.execute("SELECT film_runtime, film_name FROM film WHERE film_runtime < 120;")
print("--DISPLAYING Short Film RECORDS--")
shortFilms = cursor.fetchall()
for shortFilm in shortFilms:
    print("Film Name: {}".format(shortFilm[1]))
    print("Runtime:{}".format(shortFilm[0]))
    print('')

#Display Film and Director
cursor.execute("SELECT film_director, film_name FROM film ORDER BY film_director;")
print("--DISPLAYING Directors RECORDS in order--")
directors = cursor.fetchall()
for director in directors:
    print("Film Name: {}".format(director[1]))
    print("Director: {}".format(director[0]))
    print("")


   #finally:
    #"" close the connection to MySQL """

   #db.close()

