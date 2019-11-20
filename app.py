#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session, flash
import urllib, json, sqlite3
from json import loads
from utl import db_builder, db_manager
import os
app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_FILE = "trivia.db"
#Michael's Code Below
@app.route("/login")
def login():
    return "Hello World"
#Amanda's Code Below
@app.route("/signup")
def signup():
    return render_template("signup.html")
@app.route("/signupcheck", methods=["POST"])
def signupcheck():
    username=request.form['username']
    password=request.form['password']
    confirm=request.form['confirmation']
    flag=request.form['flag']
    if(username=="" or password=="" or confirm==""):
        flash('Please fill out all fields!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag)
    if (confirm!=password):
        flash('Passwords do not match!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag)
    added = db_manager.addUser(username,password,flag)
    if (not added):
        flash('Username taken!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag)
    return "Signed In"

command="SELECT username,score FROM user_tbl;"
leaderboard=db_manager.formatFetch(exec(command));


if __name__ == "__main__":
    db_builder.build_db()
    app.debug = True
    app.run()
