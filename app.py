#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session
import urllib, json, sqlite3
from json import loads
from utl import db_builder, db_manager
app = Flask(__name__)

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
    command="SELECT username FROM user_tbl WHERE username = \'"+username+"\';"
    users=db_manager.formatFetch(db_builder.exec(command))
    print(users)
    if(username=="" or password=="" or confirm==""):
        return render_template("signupfail.html",errMessage="Missing a Field. Please Fill Out All The Inputs!", username=username,password=password,confirm=confirm,flag=flag)
    elif(len(users)!=0):
        return render_template("signupfail.html",errMessage="Username Taken!", username=username,password=password,confirm=confirm,flag=flag)
    elif (confirm!=password):
        return render_template("signupfail.html",errMessage="Password and Password Confirmation Do Not Match!", username=username,password=password,confirm=confirm,flag=flag)
    db_manager.addUser(username,password,flag)
    return "Signed In"

command="SELECT username,score FROM user_tbl;"
leaderboard=db_manager.formatFetch(exec(command));


if __name__ == "__main__":
    db_builder.build_db()
    app.debug = True
    app.run()
