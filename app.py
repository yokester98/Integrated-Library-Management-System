# import dependencies
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('Home.html')

@app.route("/Home.html")
def main2():
    return render_template('Home.html')

@app.route("/Search.html")
def search():
    return render_template('Search.html')

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