#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session, flash
import sqlite3, os
from json import loads
from utl import db_builder, db_manager

app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_FILE = "trivia.db"
#Michael's Code Below
@app.route("/")
def root():
    if 'username' in session:
        return redirect('/menu')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('password')
    flash('You were successfully logged out!')
    return redirect('/')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/auth", methods=["POST"])
def auth():
    enteredU = request.form['username']
    enteredP = request.form['password']
    if(enteredU=="" or enteredP==""):
        flash('Please fill out all fields!', 'red')
        return render_template("login.html")
    if (db_manager.userValid(enteredU,enteredP)):
        flash('You were successfully logged in!')
        return redirect('/home')
    else:
        flash('Wrong Credentials!', 'red')
        return render_template("login.html")

@app.route("/home")
def home():
    return "LOGGED IN"

#Amanda's Code Below
@app.route("/signup")
def signup():
    u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all")
    response = json.loads(u.read())
    allcountries=[]
    for country in response:
        allcountries.append(country['name'])
    return render_template("signup.html",options=allcountries)
@app.route("/signupcheck", methods=["POST"])
def signupcheck():
    username=request.form['username']
    password=request.form['password']
    confirm=request.form['confirmation']
    flag=request.form['flag']
    u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all")
    response = json.loads(u.read())
    allcountries=[]
    for country in response:
        allcountries.append(country['name'])
    if(username=="" or password=="" or confirm==""):
        flash('Please fill out all fields!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    if (confirm!=password):
        flash('Passwords do not match!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    added = db_manager.addUser(username,password,flag)
    if (not added):
        flash('Username taken!', 'red')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    #return redirect(url_for("leaderboard"))
    flash('You have successfully created an account! Please log in!')
    return redirect("/login")
@app.route("/leaderboard")
def leaderboard():
    command="SELECT username,score FROM user_tbl;"
    userScores=db_builder.exec(command).fetchall()
    leaderboard=db_manager.makeDict(userScores)
    return render_template("leaderboard.html", title="Leaderboard", rank=sorted(leaderboard.keys())[::-1] ,scoreDict=leaderboard)
@app.route("/nationboard")
def nationboard():
    u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all")
    response = json.loads(u.read())
    allcountries=[]
    for country in response:
        allcountries.append(country['name'])
    countryRank={}
    for places in allcountries:
        command="SELECT SUM(score) FROM user_tbl WHERE flag= \""+places+"\";"
        output=str(db_builder.exec(command).fetchall())[2:-3]
        if output !="None":
            countryRank[places]=output
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
