#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session, flash
import sqlite3, os
from utl import db_builder, db_manager

app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_FILE = "trivia.db"
#Michael's Code Below
@app.route("/")
def root():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
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
        return redirect('/home')
    else:
        flash('Wrong Credentials!', 'red')
        return render_template("login.html")

#Amanda's Code Below
@app.route("/signup")
def signup():
    data = db_manager.allCountries()
    return render_template("signup.html",options=data)

@app.route("/signupcheck", methods=["POST"])
def signupcheck():
    username=request.form['username']
    password=request.form['password']
    confirm=request.form['confirmation']
    flag=request.form['flag']
    allcountries=db_manager.allCountries()
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

@app.route("/home")
def home():
    return "LOGGED IN"

#====================================================
#STARTING FROM HERE USER MUST BE LOGGED IN

@app.route("/leaderboard")
def leaderboard():
    leaderboard=db_manager.userLeaderboard()
    #print(leaderboard)
    return render_template("leaderboard.html", title="Leaderboard", rank=sorted(leaderboard.keys())[::-1] ,scoreDict=leaderboard)

@app.route("/nationboard")
def nationboard():
    countryRank = db_manager.nationLeaderboard()
    #print(countryRank)
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)
    #######################################

@app.route("/mycountryboard")
def mycountryboard():
    user = session['username']
    if (user is None):
        flash('Oops, Lost Connection. Please Login Again!', 'red')
        return redirect(url_for("login"))
    countryRank=db_manager.myCountryboard(user)
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)

#profile pages below
@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/icon", methods=["POST"])
def icon():
    command='UPDATE user_tbl SET pic="{}" WHERE username="{}";'.format(request.form['img'], session['username'])
    db_builder.exec(command)
    return redirect("/home")

@app.route("/resetpasswd", methods=["POST"])
def password():
    #Jackie: Insert Code Here
    return redirect("/home")

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
