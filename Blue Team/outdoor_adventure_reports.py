"""
BLUE TEAM: Vaneshiea Bell, Jess Monnier, DeJanae Faison
Professor Sue Sampson
Assignment 11 Milestone 3, 3/2/2025
"""

# Import needed modules
import mysql.connector
from mysql.connector import errorcode
import os # Used to control python's working directory
import sys # Used if matplotlib is not installed
import tkinter as tk
from tkinter import font # was being stubborn when not separately imported
from copy import deepcopy # Used for ease of having a template variable
# Print error and exit if matplotlib is not installed
try:
    from matplotlib import pyplot as plt
except ImportError:
    print('\nThis program requires the matplotlib module.')
    print('Please install it and try again.\n')
    sys.exit()

# Connect to .env file
from dotenv import dotenv_values

# Get the directory of the script so we don't have to execute 
# the script from that directory for the .env file to work
working_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(working_dir)

# Using ENV file; note we renamed ours .env_outland and moved
# to parent folder so it doesn't need to be duplicated each module
secrets = dotenv_values("..\\.env_outland")

# Set up config dictionary to match named variables expected by mysql.connector
config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True # not in .env file
}

# Initial text variable values
welcome = "Welcome to Outland Adventures' Report Generator! "
welcome += "Please click on the button matching the report you would like to generate."
help_text = "Please click one of the report buttons to generate a report here. "
help_text += "Note that the Trip Destination Trends report will also open a new window."
query = ""

# open connection with error checking
try:
    db = mysql.connector.connect(**config) # connect to the database 

    # Get a database "cursor" to execute queries in our database
    cursor = db.cursor()

    """ FUNCTIONS CALLED BY TKINTER APP BUTTONS """

    # Function to generate a report on equipment sales trends
    def equipment_report():
       help_label.config(text = "This report functionality is still being constructed.") 

    def trip_report():

        '''INITIAL QUERIES TO GET DISTINCT CONTINENTS, EARLIEST/LATEST TRIP'''

        # Get all continent values in database where
        # continent follows the final ', ' in the destination string
        query = "select distinct substring_index(destination, ', ', -1) as 'Continent' from trip;"
        cursor.execute(query)
        continents = cursor.fetchall()

        # Get earliest trip end in database to help find earliest quarter
        query = "select trip_end from trip order by trip_end limit 1;"
        cursor.execute(query)
        earliest_trip = cursor.fetchone()[0] # returns a tuple, of which we want index 0
        earliest_year = int(earliest_trip.year)
        earliest_month = int(earliest_trip.month)

        # Get latest trip end in database to help find latest quarter
        query = "select trip_end from trip order by trip_end desc limit 1;"
        cursor.execute(query)
        latest_trip = cursor.fetchone()[0]
        latest_year = int(latest_trip.year)
        latest_month = int(latest_trip.month)

        '''PREPPING FOR MORE COMPLEX REPORT QUERY & REPORT GENERATION'''

        # Determine starting quarter and make array to match
        # We'll be rotating through the array continuously, so
        # it's important to start at the right quarter.
        # For our purposes, Q1 is Jan-Mar, Q2 Apr-Jun, etc.
        if 1 <= earliest_month < 4:
            quarters = [1, 2, 3, 4]
        elif 4 <= earliest_month < 7:
            quarters = [2, 3, 4, 1]
        elif 7 <= earliest_month < 10:
            quarters = [3, 4, 1, 2]
        else:
            quarters = [4, 1, 2, 3]
        
        # Variables to be populated by following while loop; quarter end
        # dates will only be used in query, where template dictionary will
        # be used both in query and to generate report
        quarter_end_dates = []
        template = {'quarter': [], 'number': []}
        
        # While loop to generate the relevant quarter end-dates 
        # & quarter/# of trips template dictionary. We will be mutating
        # the earliest_year & earliest_month variables to control the loop.
        while earliest_year <= latest_year:
            
            # Get the appropriate end date for the quarter of the current
            # value of earliest_month and earliest_year, then append to list
            for quarter in quarters:
                if 1 <= earliest_month < 4:
                    date_string = str(earliest_year) + "-03-31"
                elif 4 <= earliest_month < 7:
                    date_string = str(earliest_year) + "-06-30"
                elif 7 <= earliest_month < 10:
                    date_string = str(earliest_year) + "-09-30"
                else:
                    date_string = str(earliest_year) + "-12-31"
                quarter_end_dates.append(date_string)
                
                # Append the current quarter to quarter key of template, append 0
                # as the number of trips to the number key of template; this is to
                # ensure that if query returns 0 trips for a quarter, it is not skipped.
                template['quarter'].append(str(earliest_year) + "Q" + str(quarter)) # e.g. 2025Q1
                template['number'].append(0)

                # Add three months to get to the next quarter
                earliest_month += 3

                # If we go beyond 12, change it to the beginning of the next year instead
                if earliest_month > 12:
                    earliest_month -= 12
                    earliest_year += 1
                
                # Check to see if we've reached/surpassed the latest trip date & if so, break
                if earliest_year == latest_year and earliest_month >= latest_month:
                    break
            
            # Need to do a second check outside the for loop to break the while loop
            # Without this we might get 1-3 extra empty quarters, depending on latest 
            # vs earliest quarter number.
            if earliest_year == latest_year and earliest_month >= latest_month:
                break
        
        '''MAIN QUERY LOOP'''

        # make a query for each continent, store in results dictionary
        results = {}
        for res in continents:
            continent = res[0] # Get just the continent name out of result tuple

            # Use copy module's deepcopy method to get an actual copy of the template
            # that won't be mutated by each run of the loop
            results[continent] = deepcopy(template)

            # Start of query; get by continent name, initiate a case
            query = "select substring_index(destination, ', ', -1) as 'Continent', case "

            # for loop with the quarter array we generated to build the query case
            for i, entry in enumerate(quarter_end_dates[:-1]):
                query += "when trip_end <= '" + entry + "' then '" + template['quarter'][i] + "' "
            
            # capture that final index as the else statement for the case
            query += "else '" + template['quarter'][-1] + "' end, count(*) from trip "
            
            # finish up query with grouping, limiting to current continent, ordering
            query += "group by 2, 1 having continent = '" + continent + "' order by 2;"

            # Send query to the database, store in temp_results
            cursor.execute(query)
            temp_results = cursor.fetchall()

            # Our template has every possible quarter with a corresponding 0 in the number key's list,
            # so we want to look up the index of the current quarter in the quarter key and then
            # change the number at that index in the number key's list to the corresponding value
            for result in temp_results:
                results[continent]['number'][results[continent]['quarter'].index(result[1])] = result[2]
        
        '''GENERATE TEXTUAL REPORT'''

        # Set the summary/help text in tkinter
        report = "A chart should populate in a new window that will give a better visual of the following results. "
        report += "For each quarter and continent, the number shown represents the number of trips to that continent "
        report += "that ended during that quarter.\n\n"
        help_label.config(text = report)

        # Create an initial list of labels (Quarter, each continent name)
        labeler = ["Quarter"]
        labeler.extend(results.keys())

        # Create a "table" out of tkinter Entry widgets to show the data in a neat format.
        # I learned this technique from a GeeksforGeeks tutorial bc str.center(width) was being stubborn ._.
        for n in range(-1, len(template['quarter'])):
            for i, label in enumerate(labeler):
                
                # Create the Entry widget, assign its position within report_container frame
                # n starts at -1 for ease of identifying the label row, so the actual row value
                # for each entry is n+1 (to start at 0).
                e = tk.Entry(report_container, justify = "center")
                e.grid(row = n+1, column = i)

                # Handle label row
                if n == -1:
                    e.insert(tk.END, label)
                    e.configure(font = (default_font["family"], default_font["size"]-1, "bold"))
                
                # Handle data rows by looking up the correct quarter from template based on
                # current value of n OR correct number of trips from results based on both
                # the current value of n and the current continent
                else:
                    if label == "Quarter":
                        e.insert(tk.END, template['quarter'][n])
                    else:
                        e.insert(tk.END, results[label]["number"][n])

        '''GRAPHICAL REPORT VIA MATPLOTLIB'''

        # Create an array of possible colors to use; more would need to be added if there
        # were trips to more than 6 continents/major continental areas          
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown']

        # For each continent, use its index to pick its line color and use its "quarter" list for
        # x values and its "number" list for y values; also label it by name
        for i, continent in enumerate(results.keys()):
            plt.plot(results[continent]['quarter'], results[continent]['number'], label=continent, c=colors[i])
        
        # Configure titles etc for plot and axes, add a legend, show the plot
        plt.title("Trip Destination Trends", fontsize=18)
        plt.xlabel('Quarter', fontsize=14)
        plt.ylabel("Number of Trips", fontsize=14)
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.legend()
        plt.show()

    # Function to display the report of inventory items by age
    def inventory_report():
        help_label.config(text = "This report functionality is still being constructed.") 

    """ BUILD TKINTER APP WINDOW """
    
    # Build the main app window.
    window = tk.Tk()
    window.title("Outland Adventure Reports")
    window.geometry("520x700")

    # Get the default font values
    default_font = font.nametofont("TkDefaultFont").actual()

    # Include a static greeting with instructions the user can refer back to as needed.
    greeting = tk.Label(window,
                        text = welcome,
                        wraplength = 480,
                        justify = "left")
    greeting.grid(row = 0,
                columnspan = 3,
                padx = 10,
                pady = 5,
                sticky = "NSEW")
    
    # Create the buttons that generate the reports and set command to the matching function
    equipment_button = tk.Button(window,
                            text = "Equipment Sales Trends",
                            command = equipment_report)
    equipment_button.grid(row = 1,
                        column = 0,
                        padx = 20,
                        pady = 5,
                        sticky = "NESW")

    trip_button = tk.Button(window,
                            text = "Trip Destination Trends",
                            command = trip_report)
    trip_button.grid(row = 1,
                    column = 1,
                    padx = 20,
                    pady = 5,
                    sticky = "NSEW")
    
    inventory_button = tk.Button(window,
                                 text = "Inventory Age Report",
                                 command = inventory_report)
    inventory_button.grid(row = 1,
                          column = 2,
                          padx = 20,
                          pady = 5,
                          sticky = "NSEW")
    
    # Create the container for the help/description text for reports
    help_label = tk.Label(window,
                          text = help_text,
                          wraplength = 480,
                          justify = "left")
    help_label.grid(row = 2,
                    columnspan = 3,
                    padx = 10,
                    pady = 5,
                    sticky = "NSEW")
    
    # Create the container for the report itself; it's a frame, as each
    # function will generate its own label or what-have-you
    report_container = tk.Frame(window)
    report_container.grid(row = 3,
                          columnspan = 3,
                          padx = 10,
                          pady = 5,
                          sticky = "NSEW")
    
    # Open the tkinter window
    window.mainloop()

# MySQL connection error resolution actions
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")
    else:
        print(err)

# Close the database
finally:
    db.close()