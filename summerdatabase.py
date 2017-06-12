import requests
import sqlite3
import time
import datetime
import sys
import csv
conn = sqlite3.connect('summeropp.db')  # opens DB, DB will be created if it doesn't exist
conn.text_factory = str
c = conn.cursor()  # cursor is analogous to mouse cursor in computer
c.execute('CREATE TABLE IF NOT EXISTS summer_opportunities(event TEXT, '
          'location TEXT, address TEXT, city TEXT, zipcode INTEGER, restrictions TEXT,'
          'agerange TEXT, finaid TEXT, cost TEXT, deadline TEXT, duration TEXT, '
          'startdate TEXT, enddate TEXT, hours TEXT, language TEXT,'
          'website TEXT, programtype TEXT, description TEXT, contact TEXT, tags TEXT)')

with open ('sumopp.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        c.execute('INSERT INTO summer_opportunities (event, location,address,city,zipcode,restrictions,agerange,finaid,'
                  'cost,deadline,duration,startdate,enddate,hours,language,website,programtype,description,contact,'
                  'tags)'
                  'VALUES (?, ?, ?, ?, ?, ?,?,?,?,'
                  '?, ?, ?,?, ?, ?,?, ?, ?,?,?)',
                  (row['Event'],row['Location'],row['Address'],row['City'],row['Zip Code'],row['Restrictions'],
                   row['Age Range'],row['Financial Aid'],row['Cost'],
                   row['Deadline'],row['Duration/Days'],row['Start Date'],
                   row['End Date'],row['Hours'],row['Language'],row['Website'],
                   row['Type of Program'],row['Description'],row['Contact'],row['Tags']))
c.close()
conn.close()