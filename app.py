# import dependencies
from flask import Flask, render_template, redirect, url_for, request, session, make_response, flash, Blueprint
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
from datetime import date, datetime, timedelta

app = Flask(__name__)

# for session
app.secret_key = "random string"

# mongoDB connection
mongodb = MongoClient('localhost', 27017)
db = mongodb.bookcollection
collection = db.book

# mySQL connection
try:
    connection = mysql.connector.connect(host='localhost', database='Library', user='root', password=input("type password for mySQL here: "))
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor(buffered=True)
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

@app.route('/', methods=['GET','POST'])
def main():
    session.clear()
    return redirect(url_for("login"))

@app.route('/Signup.html', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        print(firstName, lastName, password1, password2)


        if password1 != password2:
            flash("Passwords don't match.")
        else:
            mysql_insert_new_user = "INSERT INTO user (firstName, lastName, password) VALUES ('{}', '{}', '{}')".format(firstName, lastName, password1)
            cursor.execute(mysql_insert_new_user)
            connection.commit()
            cursor.execute("SELECT userID FROM user ORDER BY userID DESC LIMIT 1")
            userID = cursor.fetchall()[0][0]
            session["userID"] = userID
            return redirect(url_for('success'))

    return render_template("Signup.html")

@app.route("/Home.html", methods=["POST","GET"])
def login():
    if request.method == "POST":
        userID = request.form['userID']
        password = request.form['password']
        action = request.form["action"]
        
        mysql_user_count = "SELECT COUNT(*) FROM User"
        cursor.execute(mysql_user_count)
        user_count = cursor.fetchone()[0]
        
        if action == "User":
            cursor.execute("SELECT COUNT(1) FROM user WHERE userID = {}".format(userID))
            count = cursor.fetchone()[0]
            if count == 0:
                flash("Incorrect userID/password.")
                return render_template("Home.html")
            elif int(userID) in range(1, user_count + 1):
                mysql_user_pw = "SELECT password FROM user WHERE userID = {}".format(userID)
                cursor.execute(mysql_user_pw)
                pw = cursor.fetchone()[0]
                # creates session if both userID and password are correct
                if password == pw:
                    session["userID"] = userID
                    return redirect(url_for("profile"))
                else:
                    flash("Incorrect userID/password.")
                    return render_template("Home.html")

        elif action == "Admin":
            mysql_admin_query = "SELECT adminID, password FROM admin WHERE adminID = {}".format(userID)
            cursor.execute(mysql_admin_query)
            admin_data = cursor.fetchall()
            if admin_data:
                if password == admin_data[0][1]:
                    session["userID"] = userID
                    return redirect(url_for("admin"))
                else:
                    flash("Incorrect adminID/password.")
                    return render_template("Home.html")
            else:
                flash("Incorrect userID/password.")
                return render_template("Home.html")

    else:
        return render_template("Home.html")

@app.route("/Profile.html", methods = ["POST", "GET"])
def profile():
    # check if user wants to logout
    if request.method == "POST":
        session.clear()
        return redirect(url_for("login"))

    # if logged in
    if "userID" in session:
        userID = session["userID"]

        cursor.execute("SELECT COUNT(1) FROM user WHERE userID = {}".format(userID))
        count = cursor.fetchone()[0]
        if count == 0:
            return redirect(url_for("login"))

        mysql_lastName = "SELECT lastName FROM user WHERE userID = {}".format(userID)
        cursor.execute(mysql_lastName)
        lastname = cursor.fetchone()[0]

        mysql_borrowed = "SELECT COUNT(*) FROM borrowed WHERE userID = {}".format(userID)
        cursor.execute(mysql_borrowed)
        borrowed = cursor.fetchone()[0]
        
        mysql_reserved = "SELECT COUNT(*) FROM Reserved WHERE userID = {}".format(userID)
        cursor.execute(mysql_reserved)
        reserved = cursor.fetchone()[0]
        
        cursor.execute("SELECT amount FROM fine WHERE userID = {}".format(userID))
        count = cursor.fetchone()
        if count:
            amt = count[0]
        else:
            amt = 0

        return render_template("Profile.html", userID=userID, lastName=lastname, borrowed=borrowed, reserved=reserved, amt=amt)

    return redirect(url_for("login"))

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
    # check if user is logged in
    if len(session) == 0:
        return redirect(url_for("login"))

    # check if it is an admin who is logged in
    cursor.execute("SELECT COUNT(1) FROM user WHERE userID = {}".format(session["userID"]))
    count = cursor.fetchone()[0]
    if count == 0:
        return redirect(url_for("login"))

    # Check if user has submitted any actions
    if request.method == "POST":
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d')

        currentBookID = request.form["bookID"]
        action = request.form["action"]

        sql_getfine_query = "SELECT userID, amount FROM fine WHERE userID = {}".format(session["userID"])     #need to add global user here
        cursor.execute(sql_getfine_query)
        fineRecord = cursor.fetchall()

        if action == "Convert" or action == "Cancel":
            sql_getReserved_query = "SELECT userID FROM Reserved WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getReserved_query)
            reservedBookRecord = cursor.fetchall()
            if len(reservedBookRecord) == 0:
                flash("No such book reserved")
            elif action == "Convert":
                cursor.execute("SELECT COUNT(1) FROM borrowed WHERE bookID = {}".format(currentBookID))
                count = cursor.fetchone()[0]
                # check existing fines
                cursor.execute("SELECT amount FROM Fine WHERE userID = {}".format(session["userID"]))
                finecount = cursor.fetchone()
                if finecount:
                    amount = finecount[0]
                else:
                    amount = 0
                
                if count:
                    flash("Error Converting Reserved book to Borrowed, book has not been returned by another user.")
                elif amount > 0:
                    # insert error message here
                    flash("Error Converting Reserved book to Borrowed, you have an outstanding fine.")
                else:
                    cursor.execute("SELECT COUNT(*) FROM borrowed WHERE userID = {}".format(session["userID"]))  #need to add global user here
                    count = cursor.fetchone()[0]
                    if count >= 4:
                        flash("Error Converting Reserved book to Borrowed, you have borrowed a maximum of 4 books.")
                    elif reservedBookRecord[0][0] == int(session["userID"]) and count < 4:
                        dueDate = now.date() + timedelta(days=28)
                        formatted_date = dueDate.strftime('%Y-%m-%d')
                        sql_updateBorrowed_query = "INSERT INTO borrowed VALUES ({}, {}, '{}', '{}')".format(currentBookID, session["userID"], formatted_now, formatted_date) #need to add global user here
                        sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                        cursor.execute(sql_updateBorrowed_query)
                        cursor.execute(sql_updateReserved_query)

            elif action == "Cancel":
                if len(reservedBookRecord) == 0:
                    flash("Error Cancelling Reserved book, you did not reserve this book.")
                else:
                    if reservedBookRecord[0][0] == int(session["userID"]):   #need to add global user here
                        sql_updateReserved_query = "DELETE FROM reserved WHERE bookID = {}".format(currentBookID)
                        cursor.execute(sql_updateReserved_query)

        elif action == "Extend" or action == "Return":
            sql_getBorrowedBook_query = "SELECT bookID, userID, borrowDate, dueDate FROM borrowed WHERE bookID = {}".format(currentBookID)
            cursor.execute(sql_getBorrowedBook_query)
            borrowedBookRecord = cursor.fetchall()
            if len(borrowedBookRecord) == 0:
                flash("No such book borrowed")
            elif action == "Extend" and borrowedBookRecord[0][1] == int(session["userID"]):  #need to add global user here
                cursor.execute("SELECT COUNT(1) FROM reserved WHERE bookID = {}".format(currentBookID))
                count = cursor.fetchone()[0]
                # check existing fines
                cursor.execute("SELECT amount FROM Fine WHERE userID = {}".format(session["userID"]))
                finecount = cursor.fetchone()
                if finecount:
                    amount = finecount[0]
                else:
                    amount = 0
                # Check if the current book is already being reserved
                if amount > 0:
                    # insert error message here
                    flash("Error Extending Borrowed book, you have an outstanding fine.")
                elif count:
                    flash("Error Extending Borrowed book, another user has made a reservation.")
                else:
                    dueDate = now + timedelta(days=28)
                    formatted_date = dueDate.strftime('%Y-%m-%d')
                    sql_updateBorrowed_query = "UPDATE borrowed SET dueDate = '{}' WHERE bookID = {}".format(formatted_date, currentBookID)
                    cursor.execute(sql_updateBorrowed_query)

            elif action == "Return":
                if borrowedBookRecord[0][1] == int(session["userID"]): #need to add global user here
                    dueDate = borrowedBookRecord[0][3]
                    delta = now.date() - dueDate
                    if delta.days > 0:
                        cursor.execute("SELECT COUNT(1) FROM fine WHERE userID = {}".format(session["userID"]))  # need to add global user here
                        count = cursor.fetchone()[0]
                        if count:  
                            sql_updateFine_query = "UPDATE fine SET amount = {} WHERE userID = {}".format(fineRecord[0][1] + delta.days, session["userID"])  #need to add global user here
                            cursor.execute(sql_updateFine_query)
                            cursor.execute("DELETE FROM reserved WHERE userID = {}".format(session["userID"]))
                        else:
                            sql_insertFine_query = "INSERT INTO fine VALUES ({}, {})".format(session["userID"], delta.days)  # need to add global user here
                            cursor.execute(sql_insertFine_query)
                            cursor.execute("DELETE FROM reserved WHERE userID = {}".format(session["userID"]))

                    # delete borrow record from borrowed
                    cursor.execute("DELETE FROM borrowed WHERE bookID = {}".format(currentBookID))

        elif action == "Borrow":
            # check if bookID exists in Borrowed
            cursor.execute("SELECT COUNT(1) FROM Borrowed WHERE bookID = {}".format(currentBookID))
            exist = cursor.fetchone()[0]
            # check number of books borrowed 
            cursor.execute("SELECT COUNT(1) FROM Borrowed WHERE userID = {}".format(session["userID"]))
            numBorrowed = cursor.fetchone()[0]
            # check existing fines
            cursor.execute("SELECT amount FROM Fine WHERE userID = {}".format(session["userID"]))
            count = cursor.fetchone()
            if count:
                amount = count[0]
            else:
                amount = 0

            # check if bookID exists in book entity
            cursor.execute("SELECT COUNT(1) FROM Book WHERE bookID = {}".format(currentBookID))
            bookExist = cursor.fetchone()[0]
            # need to check if book is being reserved
            cursor.execute("SELECT userID FROM Reserved WHERE bookID = {}".format(currentBookID))
            reserve_user_data = cursor.fetchall()
            if reserve_user_data:
                reserve_user = str(reserve_user_data[0][0])
            else:
                reserve_user = ""

            if exist == 0 and numBorrowed < 4 and amount == 0 and bookExist and (reserve_user == "" or reserve_user == session["userID"]):
                dueDate = now + timedelta(days=28)
                dueDate_formatted = dueDate.strftime('%Y-%m-%d')
                now_formatted = now.strftime('%Y-%m-%d')
                # insert row into Borrowed
                cursor.execute("INSERT INTO Borrowed VALUES ({}, {}, '{}', '{}')".format(currentBookID, session["userID"], now_formatted, dueDate_formatted))
                cursor.execute("DELETE FROM Reserved WHERE bookID = {}".format(currentBookID))
            elif bookExist == 0:
                flash("Error Borrowing book, book does not exist.")
            elif amount > 0:
                flash("Error Borrowing book, you have an outstanding fine.")
            elif numBorrowed >= 4:
                flash("Error Borrowing book, you have borrowed a maximum of 4 books.")
            elif exist != 0:
                flash("Error Borrowing book, book is already borrowed by another user.")
            elif reserve_user != "":
                flash("Error Borrowing book, book is reserved by another user.")

    
        elif action == "Reserve":
            # check if book is reserved
            cursor.execute("SELECT COUNT(1) FROM Reserved WHERE bookID = {}".format(currentBookID))
            exist = cursor.fetchone()[0]
            # check existing fines
            cursor.execute("SELECT amount FROM Fine WHERE userID = {}".format(session["userID"]))
            count = cursor.fetchone()
            if count:
                amount = count[0]
            else:
                amount = 0
            # check if the bookID exists in book entity
            cursor.execute("SELECT COUNT(1) FROM Book WHERE bookID = {}".format(currentBookID))
            bookExist = cursor.fetchone()[0]
            # need to check if the book is already borrowed by the same user
            cursor.execute("SELECT userID FROM Borrowed WHERE bookID = {}".format(currentBookID))
            borrow_user_data = cursor.fetchall()
            if borrow_user_data:
                borrow_user = str(borrow_user_data[0][0])
            else:
                borrow_user = ""           

            if exist == 0 and amount == 0 and bookExist > 0 and borrow_user != session["userID"]:
                currDate = date.today().strftime('%Y-%m-%d')
                # insert row into Reserved
                cursor.execute("INSERT into Reserved values ({}, {}, '{}')".format(currentBookID, session["userID"], currDate))
            elif bookExist == 0:
                flash("Error Reserving book, book does not exist.")
            elif borrow_user == session["userID"]:
                flash("Error Reserving book, you have already borrowed this book.")
            elif amount > 0:
                flash("Error Reserving book, you have an outstanding fine.")
            elif exist != 0:
                flash("Error Reserving book, book is already being reserved.")

        connection.commit()

        headings = ("BookID", "Status", "Due/Available Date")
        data = []
        sql_getBorrowed_query = "SELECT bookID, borrowDate, dueDate FROM borrowed WHERE userID = {}".format(session["userID"])  # need to add global user var here
        cursor.execute(sql_getBorrowed_query)
        borrowed_records = cursor.fetchall()

        sql_getReserved_query = "SELECT bookID, reserveDate FROM reserved WHERE userID = {}".format(session["userID"])  # need to add global user var here
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
    sql_getBorrowed_query = "SELECT bookID, borrowDate, dueDate FROM borrowed WHERE userID = {}".format(session["userID"])  # need to add global user var here
    cursor.execute(sql_getBorrowed_query)
    borrowed_records = cursor.fetchall()

    sql_getReserved_query = "SELECT bookID, reserveDate FROM reserved WHERE userID = {}".format(session["userID"])  # need to add global user var here
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

@app.route("/Payment.html", methods=["POST", "GET"])
def payment():
    if len(session) == 0:
        return redirect(url_for('login'))
    # check if it is an admin who is logged in
    cursor.execute("SELECT COUNT(1) FROM user WHERE userID = {}".format(session["userID"]))
    count = cursor.fetchone()[0]
    if count == 0:
        return redirect(url_for("login"))

    # get amount payable
    amountPaid_query = "SELECT amount FROM fine WHERE userID = {}".format(session["userID"])
    cursor.execute(amountPaid_query)
    amountPaidData = cursor.fetchone()
    if amountPaidData:
        amountPaid = amountPaidData[0]
    else:
        amountPaid = 0
    print(amountPaid)

    if request.method == "POST":
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d')
        print(formatted_now)

        #insert into payment table
        sql_deleteFineEntry_query = "DELETE FROM fine WHERE userID = {}".format(session["userID"])
        cursor.execute(sql_deleteFineEntry_query)
        connection.commit()

        #delete row from fine table
        sql_insertPayment_query = "INSERT INTO payment (amountPaid, userID, datePaid) VALUES ({}, {}, '{}')".format(amountPaid, session["userID"], formatted_now)
        cursor.execute(sql_insertPayment_query)
        connection.commit()

        

        return redirect(url_for('profile'))    
    return render_template('Payment.html', amountPaid = amountPaid)

@app.route("/Admin.html")
def admin():

    sql_getAllBorrowings_query = "SELECT u.userID, firstName, lastName, br.bookID, title, br.dueDate FROM user u JOIN borrowed br ON u.userID = br.userID JOIN book b ON br.bookID = b.bookID"
    cursor.execute(sql_getAllBorrowings_query)
    data_borrowed = cursor.fetchall()

    sql_getAllReserved_query = "SELECT u.userID, firstName, lastName, r.bookID, title FROM user u JOIN reserved r ON u.userID = r.userID JOIN book b ON r.bookID = b.bookID"
    cursor.execute(sql_getAllReserved_query)
    data_reserved = cursor.fetchall()

    sql_getAllFine_query = "SELECT u.userID, firstName, lastName, amount FROM user u JOIN fine f ON u.userID = f.userID"
    cursor.execute(sql_getAllFine_query)
    data_fine = cursor.fetchall()

    return render_template('Admin.html', data_borrowed = data_borrowed, data_reserved = data_reserved, data_fine = data_fine)



@app.route("/Success.html")
def success():
    userID = session["userID"]
    return render_template('Success.html', userID = userID)

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
# final line
if __name__ == "__main__":
    app.debug = True
    app.run()