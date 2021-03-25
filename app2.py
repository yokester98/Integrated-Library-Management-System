# import dependencies
from flask import Flask, render_template, redirect, url_for, request, session, make_response, flash
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
import datetime
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_session import Session


app = Flask(__name__)

app.secret_key = "random string"

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

@app.route('/Search.html', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        keywords = request.form['book']
        action = request.form["action"]
        if action == "Title":
            query = { "title" : { "$regex": keywords, "$options" : "i"}}
        elif action == "Author":
            query = { "authors" : { "$regex": keywords, "$options" : "i"}}
        elif action == "Category":
            query = { "categories" : { "$regex": keywords, "$options" : "i"}}
        elif action == "YearOfPublish":
            query = { "publishedDate" : { "$regex": keywords, "$options" : "i"}}
        data = collection.find(query, {"_id":1, "title":1})
        listdata = list(data)
        data = []
        headings = ("BookID", "Title")
        for dic in listdata:
            data += ((dic.get("_id"), dic.get("title")),)

        return render_template('Search.html', data=data)
    return render_template('Search.html')

@app.route("/Manage.html", methods=["POST", "GET"])
def manage():
    # Check if user has submitted any actions
    if request.method == "POST":
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d')

        currentBookID = request.form["bookID"]
        action = request.form["action"]

        sql_getfine_query = "SELECT userID, amount FROM fine WHERE userID = {}".format(2)     #need to add global user here
        cursor.execute(sql_getfine_query)
        fineRecord = cursor.fetchall()

        if action == "Convert" or action == "Cancel":
            sql_getReserved_query = "SELECT userID FROM Reserved WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getReserved_query)
            reservedBookRecord = cursor.fetchall()

            if action == "Convert":
                cursor.execute("SELECT COUNT(1) FROM borrowed WHERE bookID = {}".format(currentBookID))
                count = cursor.fetchone()[0]
                if count:
                    # insert error message here
                    print("Error Converting Reserved book to Borrowed")
                else:
                    cursor.execute("SELECT COUNT(*) FROM borrowed WHERE userID = {}".format(2))  #need to add global user here
                    count = cursor.fetchone()[0]
                    if reservedBookRecord[0][0] == 2 and count < 4:
                        dueDate = now.date() + timedelta(days=28)
                        formatted_date = dueDate.strftime('%Y-%m-%d')
                        sql_updateBorrowed_query = "INSERT INTO borrowed VALUES ({}, {}, '{}', '{}')".format(currentBookID, 2, formatted_now, formatted_date) #need to add global user here
                        sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                        cursor.execute(sql_updateBorrowed_query)
                        cursor.execute(sql_updateReserved_query)

            elif action == "Cancel":
                if len(reservedBookRecord) == 0:
                    print("Reserved Book not found")
                else:
                    if reservedBookRecord[0][0] == 2:   #need to add global user here
                        sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                        cursor.execute(sql_updateReserved_query)

        elif action == "Extend" or action == "Return":
            sql_getBorrowedBook_query = "SELECT bookID, userID, borrowDate, dueDate FROM borrowed WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getBorrowedBook_query)
            borrowedBookRecord = cursor.fetchall()

            if action == "Extend" and borrowedBookRecord[0][1] == 2:  #need to add global user here
                cursor.execute("SELECT COUNT(1) FROM reserved WHERE bookID = {}".format(currentBookID))
                count = cursor.fetchone()[0]
                # Check if the current book is already being reserved
                if count:
                    # insert error message here
                    print("Error Extending Borrowed book")
                else:
                    dueDate = now + timedelta(days=28)
                    formatted_date = dueDate.strftime('%Y-%m-%d')
                    sql_updateBorrowed_query = "UPDATE borrowed SET dueDate = '{}' WHERE bookID = {}".format(formatted_date, currentBookID)
                    cursor.execute(sql_updateBorrowed_query)

            elif action == "Return":
                if borrowedBookRecord[0][1] == 2: #need to add global user here
                    dueDate = borrowedBookRecord[0][3]
                    delta = now.date() - dueDate
                    if delta.days > 0:
                        cursor.execute("SELECT COUNT(1) FROM fine WHERE userID = {}".format(2))  # need to add global user here
                        count = cursor.fetchone()[0]
                        if count:  
                            sql_updateFine_query = "UPDATE fine SET amount = {} WHERE userID = {}".format(fineRecord[0][1] + delta.days, 2)  #need to add global user here
                            cursor.execute(sql_updateFine_query)
                        else:
                            sql_insertFine_query = "INSERT INTO fine VALUES ({}, {})".format(2, delta.days)  # need to add global user here
                            cursor.execute(sql_insertFine_query)

                    # delete borrow record from borrowed
                    cursor.execute("DELETE FROM borrowed WHERE bookID = {}".format(currentBookID))

        connection.commit()

        headings = ("BookID", "Status", "Due/Available Date")
        data = []
        sql_getBorrowed_query = "SELECT bookID, borrowDate, dueDate FROM borrowed WHERE userID = {}".format(2)  # need to add global user var here
        cursor.execute(sql_getBorrowed_query)
        borrowed_records = cursor.fetchall()

        sql_getReserved_query = "SELECT bookID, reserveDate FROM reserved WHERE userID = {}".format(2)  # need to add global user var here
        cursor.execute(sql_getReserved_query)
        reserved_records = cursor.fetchall()

        for row in borrowed_records:
            bookID, borrowDate, dueDate = row
            data.append([bookID, "Borrowed", dueDate])

        for row in reserved_records:
            bookID, reserveDate = row
            # check when is the available date for the reserved books
            sql_getBorrowedBook_query = "SELECT dueDate FROM borrowed WHERE bookID = {}".format(bookID)
            cursor.execute(sql_getBorrowedBook_query)
            reserved_book = cursor.fetchall()
            if len(reserved_book) > 0:
                availDate = reserved_book[0][0].strftime('%Y-%m-%d')
            else:
                availDate = datetime.now().strftime('%Y-%m-%d')
            data.append([bookID, "Reserved", availDate])
        return render_template('Manage.html', data = data)
    
    headings = ("BookID", "Status", "Due/Available Date")
    data = []
    sql_getBorrowed_query = "SELECT bookID, borrowDate, dueDate FROM borrowed WHERE userID = {}".format(2)  # need to add global user var here
    cursor.execute(sql_getBorrowed_query)
    borrowed_records = cursor.fetchall()

    sql_getReserved_query = "SELECT bookID, reserveDate FROM reserved WHERE userID = {}".format(2)  # need to add global user var here
    cursor.execute(sql_getReserved_query)
    reserved_records = cursor.fetchall()

    for row in borrowed_records:
        bookID, borrowDate, dueDate = row
        data.append([bookID, "Borrowed", dueDate])

    for row in reserved_records:
        bookID, reserveDate = row
        # check when is the available date for the reserved books
        sql_getBorrowedBook_query = "SELECT dueDate FROM borrowed WHERE bookID = {}".format(bookID)
        cursor.execute(sql_getBorrowedBook_query)
        reserved_book = cursor.fetchall()
        if len(reserved_book) > 0:
            availDate = reserved_book[0][0].strftime('%Y-%m-%d')
        else:
            availDate = datetime.now().strftime('%Y-%m-%d')
        data.append([bookID, "Reserved", availDate])

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
    sql_check_numBorrowed = "SELECT bookBorrowings FROM User WHERE userID=?"
    cursor.execute(sql_check_numBorrowed)
    num_borrowed = cursor.fetchall()[0][0]
    return render_template('Holding.html', bookID = ID, title = title, borrowed = borrowed, reserved = reserved, amount = amount, num_borrowed = num_borrowed)
'''
@app.route("Borrow.html/<bookID>")
def borrow(bookID):
    currDate = date.today().strftime('%Y/%m/%d')
    dueDate = currDate + datetime.timedelta(days=28)
    cursor = connection.cursor()
    # update borrow status of book
    sql_borrow_query = "UPDATE book SET borrowID=?, borrowDate=?, dueDate=? WHERE _id=?"
    cursor.execute(sql_borrow_query, (userID, currDate, dueDate, bookID))
    connection.commit()
    return render_template('Success.html')
    
@app.route("Reserve.html/<bookID>")
def reserve(bookID):
    # update reserve status of book
    sql_reserve_query = "UPDATE book SET reserveID=? WHERE _id=?"
    cursor = connection.cursor()
    cursor.execute(sql_reserve_query, (userID, bookID))
    connection.commit()
    return render_template('Sucesss.html')
'''

@app.route('/Signup.html')
def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            cursor = connection.cursor()
            mysql_user_count = cursor.execute("SELECT COUNT(*) FROM User")
            #  insert new user, with userID = no. of rows in User + 1 (idk if my way is correct)
            mysql_insert_new_user = """INSERT INTO User (userID, firstName, lastName, password) 
            VALUES (mysql_user_count + 1, firstName, lastName, password)"""
            cursor.execute(mysql_insert_new_user)
            connection.commit()

            cursor.close()
            flash('Account created!', category='success')
            return redirect(url_for('Success'))

    return render_template("Signup.html"

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

        if "userID" in session:
            userID = session['userID']
            cursor = connection.cursor()
            mysql_user_pw = "SELECT password FROM User WHERE userID=userID"
            if check_password_hash(cursor.execute(mysql_user_pw), password):
                session['loggedin'] = True
                return redirect(url_for('Profile'))
        
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('Home.html')

@app.route('/Logout.html')
def logout():
    session.pop('userID', None)
    return redirect(url_for('Home'))

@app.route('/Profile.html')
def profile(user):
    return render_template("Profile.html")
    
# final line
if __name__ == "__main__":
    app.run()
