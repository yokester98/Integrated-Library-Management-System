# import dependencies
from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json

app = Flask(__name__)

# mongoDB connection
mongodb = MongoClient('localhost', 27017)
db = mongodb.bookcollection
collection = db.book

# mySQL connection
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='Library',
                                         user='root',
                                         password=input("type password for mySQL here: "))
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)

with open('./libbooks.json') as f:
    data = json.load(f)

add_data = ("INSERT INTO libbooks(_id, title, isbn, pageCount, publishedDate, thumbnailUrl, shortDescription, longDescription, status, authors, categories) " \
            "VALUES (%(_id)d, %(title)s, %(isbn)s, %(pageCount)d, %(publishedDate)s, %(thumbnailUrl)s, %(shortDescription)s, %(longDescription)s, %(status)s, %(authors)s, %(categories)s)")

for row in data:
    cursor.execute(add_data, row)
    
connection.commit()

'''
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
'''

@app.route("/")
def main():
    return render_template('Home.html')

@app.route("/Home.html")
def main2():
    return render_template('Home.html')

@app.route('/simpleSearch',methods=['POST'])
def simpleSearch():
    _keyword = request.form['u-border-1 u-border-grey-30 u-input u-input-rectangle u-white']
    return collection.find({title : _keyword})

@app.route("/Search.html")
def search():
    return render_template('Search.html', data = data)

@app.route("/Result.html")
def result():

    headings = ("BookID", "Title")

    dataResult = {
    ("BookID1", "BookTitle1"),
    ("BookID2", "BookTitle2"),
    ("BookID3", "BookTitle3"),
    ("BookID4", "BookTitle4")
    }
    return render_template('Result.html', dataResult = dataResult)

@app.route("/Manage.html")
def manage():
    headings = ("BookID", "Status", "Due/Available Date", "Action")
    sql_select_Query = "select * from Book"
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    # get all records
    records = cursor.fetchall()
    for row in records:
        bookID, title, authors, category, publisher, year, userID, 
    return render_template('Manage.html', data = data)

@app.route("/Payment.html")
def payment():
    return render_template('Payment.html')

@app.route("/Admin.html")
def admin():
    return render_template('Admin.html')

@app.route("/Success.html")
def success():
    return render_template('Success.html')

@app.route("/Fail.html")
def fail():
    return render_template('Fail.html')

# final line
if __name__ == "__main__":
    app.run()