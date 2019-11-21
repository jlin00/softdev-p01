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
        session['username'] = enteredU
        session['password'] = enteredP
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
    if("\"" in username):
        flash('Username can\'t have Double Quotes!', 'red')
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
    #here is how to get the all the countries
    u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all")
    response = json.loads(u.read())
    allcountries=[]
    for country in response:
        allcountries.append(country['name'])
    ##########################################
    countryRank={}
    #Here uses the the list of allcountries
    for places in allcountries:
        command="SELECT SUM(score) FROM user_tbl WHERE flag= \""+places+"\";"
        output=db_builder.exec(command).fetchall()[0][0]
        if output !="None":
            countryRank[places]=output
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)
    #######################################
@app.route("/mycountryboard")
def mycountryboard():
    if session.get('username') is None:
        flash('Oops, Lost Connection. Please Login Again!', 'red')
        return redirect(url_for("login"))
    command="SELECT flag FROM user_tbl WHERE username = \""+session.get("username")+"\";"
    country=db_builder.exec(command).fetchall()
    country=country[0][0]
    command="SELECT username,score FROM user_tbl WHERE flag = \""+country+"\";"
    countryRank=db_manager.makeDict(db_builder.exec(command).fetchall())
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)


if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
