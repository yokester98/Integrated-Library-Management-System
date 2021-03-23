# import dependencies
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
import datetime
from datetime import datetime, timedelta

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

@app.route("/Search.html",methods=['POST', "GET"])
def search():
    if request.method == "POST":
        keywords = request.form["name"]
        print(keywords)
        return redirect(url_for('result', keywords = keywords))
    else: 
        return render_template("Search.html")
    '''return render_template("Search.html")'''

@app.route('/Result.html/<keywords>')
def result(keywords):
    print("result:" + keywords)
    query = { "title" : { "$regex": keywords, "$options" : "i"}}
    result_count = collection.count_documents(query)
    print(query)
    print(result_count)
    dataResult = collection.find(query)

    return render_template("Result.html")

@app.route("/Manage.html", methods=["POST", "GET"])
def manage():
    headings = ("BookID", "Status", "Due/Available Date")
    data = []
    sql_getBorrowed_query = "SELECT bookID, borrowDate, dueDate FROM borrowed WHERE userID = {}".format(2)  # need to add global user var here
    cursor.execute(sql_getBorrowed_query)
    borrowed_records = cursor.fetchall()

    sql_getReserved_query = "SELECT bookID, reserveDate FROM reserved WHERE userID = {}".format(2)  # need to add global user var here
    cursor.execute(sql_getReserved_query)
    reserved_records = cursor.fetchall()

    for row in reserved_records:
        bookID, reserveDate = row
        sql_getReservedBook_query = "SELECT dueDate FROM borrowed WHERE bookID = {}".format(bookID)
        cursor.execute(sql_getReservedBook_query)
        reserved_book = cursor.fetchall()
        row.append(reserved_book[0])

    for row in borrowed_records:
        bookID, borrowDate, dueDate = row
        data.append([bookID, "Borrowed", dueDate])

    for row in reserved_records:
        bookID, reserveDate, availDate = row
        data.append([bookID, "Reserved", availDate])

    # Check if user has submitted any actions
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

        if action == "Convert" or action == "Cancel":
            sql_getReserved_query = "SELECT userID FROM Reserved WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getReserved_query)
            reservedBookRecord = cursor.fetchall()

            if action == "Convert":
                if cursor.execute("SELECT COUNT(1) FROM borrowed WHERE bookID = {}".format(currentBookID)):
                    # insert error message here
                else:
                    if reservedBookRecord[0][0] == 2 and cursor.execute("SELECT COUNT(*) FROM borrowed WHERE bookID = {}".format(currentBookID)) < 4:    #need to add global user here
                        dueDate = now + timedelta(days=28)
                        formatted_date = dueDate.strftime('%Y-%m-%d')
                        sql_updateBorrowed_query = "INSERT INTO borrowed VALUES ({}, {}, '{}', '{}')".format(currentBookID, 2, formatted_now, formatted_date) #need to add global user here
                        sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                        cursor.execute(sql_updateBorrowed_query)
                        cursor.execute(sql_updateReserved_query)

            elif action == "Cancel":
                if reservedBookRecord[0][0] == 2:   #need to add global user here
                    sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                    cursor.execute(sql_updateReserved_query)

        elif action == "Extend" or action == "Return":
            sql_getBorrowedBook_query = "SELECT bookID, userID, borrowDate, dueDate FROM borrowed WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getBorrowedBook_query)
            borrowedBookR = cursor.fetchall()


            if action == "Extend" and borrowedBookRecord[0][1] == 2:  #need to add global user here
                # Check if the current book is already being reserved
                if cursor.execute("SELECT COUNT(1) FROM reserved WHERE bookID = {}".format(currentBookID)):
                    # insert error message here
                else:
                    dueDate = now + timedelta(days=28)
                    formatted_date = dueDate.strftime('%Y-%m-%d')
                    sql_updateBorrowed_query = "UPDATE book SET dueDate = '{}' WHERE bookID = {}".format(formatted_date, currentBookID)
                    cursor.execute(sql_updateBorrowed_query)

            elif action == "Return":
                if borrowedBookRecord[0][1] == 2: #need to add global user here
                    if now

        elif action == "Return":
            if bookRecord[0][1] == 2:    #need to add global user here
                sql_updatebook_query = "UPDATE book SET borrowedBy = NULL, dueDate = NULL, borrowDate = NULL WHERE bookID = {}".format(currentBookID)
                sql_updateuser_query = "UPDATE users SET bookBorrowings = {} WHERE userID = {}".format(userRecord[0][1] - 1, 2)    #need to add global user here
                cursor.execute(sql_updatebook_query)
                cursor.execute(sql_updateuser_query)
        
        connection.commit()
    
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
def holding(ID, title):
    cursor = connection.cursor()
    # check whether book is borrowed
    sql_check_borrow = "SELECT borrowedBy FROM book WHERE bookID=?"
    cursor.execute(sql_check_borrow, (ID))
    borrow_row = cursor.fetchall()
    if borrow_row[0][0] == null:
        borrowed = No
    else:
        borrowed = Yes
    # check whether book is reserved
    sql_check_reserve = "SELECT reservedBy FROM book WHERE bookID=?"
    cursor.execute(sql_check_reserve, (ID))
    reserve_row = cursor.fetchall()
    if reserve_row[0][0] == null:
        reserved = No
    else:
        reserved = Yes
    # check for outstanding fines
    sql_check_fine = "SELECT amount FROM Fine WHERE userID=?"
    cursor.execute(sql_check_fine, (userID))
    amount = cursor.fetchall()[0][0]
    # check number of books borrowed
    sql_check_numBorrowed = "SELECT bookBorrowings FROM Users WHERE userID=?"
    cursor.execute(sql_check_numBorrowed)
    num_borrowed = cursor.fetchall()[0][0]
    return render_template('Holding.html', bookID = ID, title = title, borrowed = borrowed, reserved = reserved, amount = amount, num_borrowed = num_borrowed)

@app.get("Borrow.html/{bookID}")
def borrow(bookID):
    currDate = date.today().strftime('%Y/%m/%d')
    dueDate = currDate + datetime.timedelta(days=28)
    cursor = connection.cursor()
    # update borrow status of book
    sql_borrow_query = "UPDATE book SET borrowID=?, borrowDate=?, dueDate=? WHERE _id=?"
    cursor.execute(sql_borrow_query, (userID, currDate, dueDate, bookID))
    connection.commit()
    return render_template('Success.html')
    
@app.get("Reserve.html/{bookID}")
def reserve(bookID):
    # update reserve status of book
    sql_reserve_query = "UPDATE book SET reserveID=? WHERE _id=?"
    cursor = connection.cursor()
    cursor.execute(sql_reserve_query, (userID, bookID))
    connection.commit()
    return render_template('Sucesss.html')

# final line
if __name__ == "__main__":
    app.run()
