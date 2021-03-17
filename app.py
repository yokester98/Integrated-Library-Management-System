# import dependencies
from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

mongodb = MongoClient('localhost', 27017)
db = mongodb.bookcollection
collection = db.book

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
    data = (("123", "Borrowed", "21/01/2021", "Return/Extend"), ("456", "Reserved", "16/03/2021", "Convert/Cancel"))
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