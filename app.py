# import dependencies
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
<<<<<<< Updated upstream
import datetime
=======
from datetime import datetime, timedelta
>>>>>>> Stashed changes

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

#insert data from libbooks.json to libbooks entity
add_data_libbooks = ("INSERT INTO libbooks(_id, title, isbn, pageCount, publishedDate, thumbnailUrl, shortDescription, longDescription, status, authors, categories) " \
                     "VALUES (%(_id)s, %(title)s, %(isbn)s, %(pageCount)s, %(publishedDate)s, %(thumbnailUrl)s, %(shortDescription)s, %(longDescription)s, %(status)s, %(authors)s, %(categories)s)")

for row in data:
    cursor.execute(add_data_libbooks, row)
    
connection.commit()

# insert data from libbooks entity to book entity
query_add_data_book = ("INSERT INTO book(bookID, title, authors, category, datePublished) " \
                       "SELECT _id, title, authors, categories, publishedDate FROM libbooks")

cursor.execute(query_add_data_book)

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

@app.route("/Manage.html", methods=["POST", "GET"])
def manage():
    if request.method == "POST":
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d')

        currentBookID = request.form["bookID"]
        action = request.form["action"]
        
        sql_getbook_query = "SELECT bookID, borrowedBy, reservedBy, dueDate, borrowDate FROM book WHERE bookID = {}".format(currentBookID)
        cursor.execute(sql_getbook_query)
        bookRecord = cursor.fetchall()

        sql_getuser_query = "SELECT userID, bookBorrowings, bookReservations FROM users WHERE userID = {}".format(2)   #need to add global user here
        cursor.execute(sql_getuser_query)
        userRecord = cursor.fetchall()

        sql_getfine_query = "SELECT userID, amount FROM fine WHERE userID = {}".format(2)     #need to add global user here
        cursor.execute(sql_getfine_query)
        fineRecord = cursor.fetchall()

        if action == "Convert":
            if bookRecord[0][1] == None and bookRecord[0][2] == 2 and userRecord[0][1] < 4:    #need to add global user here
                dueDate = now + timedelta(days=28)
                formatted_date = dueDate.strftime('%Y-%m-%d')
                sql_updatebook_query = "UPDATE book SET borrowedBy = {}, reservedBy = NULL, borrowDate = '{}', dueDate = '{}' WHERE bookID = {}".format(2, formatted_now, formatted_date, currentBookID)  #need to add global user here
                sql_updateuser_query = "UPDATE users SET bookBorrowings = {}, bookReservations = {} WHERE userID = {}".format(userRecord[0][1] + 1, userRecord[0][2] - 1, 2)    #need to add global user here
                cursor.execute(sql_updatebook_query)
                cursor.execute(sql_updateuser_query)

        elif action == "Cancel":
            if bookRecord[0][2] == 2:   #need to add global user here
                sql_updatebook_query = "UPDATE book SET reservedBy = NULL WHERE bookID = {}".format(currentBookID)
                sql_updateuser_query = "UPDATE users SET bookReservations = {} WHERE userID = {}".format(userRecord[0][2] - 1, 2)   #need to add global user here
                cursor.execute(sql_updatebook_query)
                cursor.execute(sql_updateuser_query)

        elif action == "Extend":
            if bookRecord[0][1] == 2 and bookRecord[0][2] == None:   #need to add global user here
                dueDate = now + timedelta(days=28)
                formatted_date = dueDate.strftime('%Y-%m-%d')
                sql_updatebook_query = "UPDATE book SET dueDate = '{}' WHERE bookID = {}".format(formatted_date, currentBookID)
                cursor.execute(sql_updatebook_query)

        elif action == "Return":
            if bookRecord[0][1] == 2:    #need to add global user here
                sql_updatebook_query = "UPDATE book SET borrowedBy = NULL, dueDate = NULL, borrowDate = NULL WHERE bookID = {}".format(currentBookID)
                sql_updateuser_query = "UPDATE users SET bookBorrowings = {} WHERE userID = {}".format(userRecord[0][1] - 1, 2)    #need to add global user here
                cursor.execute(sql_updatebook_query)
                cursor.execute(sql_updateuser_query)
        
        connection.commit()
        return redirect(url_for(manage))

    headings = ("BookID", "Status", "Due/Available Date", "Action")
    data = []
    sql_select_Query = "SELECT bookID, borrowedBy, reservedBy, dueDate FROM Book WHERE borrowedBy = {0} OR reservedBy = {0}".format(2)  # need to add global user var here
    cursor.execute(sql_select_Query)
    # get all records
    records = cursor.fetchall()
    for row in records:
        bookID, borrowedBy, reservedBy, dueDate = row
        if borrowedBy == 2:       # need to add global user var here
            status = "Borrowed"
        else:
            status = "Reserved"
        data.append([bookID, status, dueDate])
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

@app.route("/Holding.html")
def holding(ID, title, borrowed, reserved):
    return render_template('Holding.html', bookID = ID, title = title, bool1 = borrowed, bool2 = reserved)

@app.route("/Borrow.html")
def borrow(bookID, userID):
    currDate = date.today().strftime('%d/%m/%Y')
    dueDate = currDate + datetime.timedelta(days=14)
    # update borrow status of book
    sql_borrow_query = "UPDATE book SET borrowID=?, borrowDate=?, dueDate=? WHERE _id=?"
    cursor = connection.cursor()
    cursor.execute(sql_borrow_query, (userID, currDate, dueDate, bookID))
    connection.commit()
    
@app.route("/Reserve.html")
def reserve(bookID, userID):
    # update reserve status of book
    sql_reserve_query = "UPDATE book SET reserveID=? WHERE _id=?"
    cursor = connection.cursor()
    cursor.execute(sql_reserve_query, (userID, bookID))
    connection.commit()

# final line
if __name__ == "__main__":
    app.run()
