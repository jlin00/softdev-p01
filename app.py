#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os
from utl import db_builder, db_manager
import random

app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_FILE = "trivia.db"

#====================================================
# decorator for checking login
def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'username' in session:
            for arg in args:
                print(arg)
            return f(*args, **kwargs)
        flash('You must be logged in to view this page!', 'red')
        return redirect('/')
    return dec

# decorator for checking no login
def no_login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'username' not in session:
            return f(*args, **kwargs)
        flash('You cannot view this page while logged in!', 'red')
        return redirect('/home')
    return dec
#====================================================

#Michael's Code Below
@app.route("/singleplayer")
def single():
    categories = ['General Knowledge', 'Books', 'Film','Music', 'Theater', 'Television', 'Video Games','Board Games', 'Science & Nature', 'Computers & Technology', 'Mathematics', 'Mythology', 'Sports', 'Geography', 'History', 'Politics', 'Art', 'Celebrities', 'Animals', 'Vehicles', 'Comics', 'Inventions', 'Anime & Manga', 'Cartoons']
    categorynums = range(9, 33)
    selection = []
    for i in range(0, 5):
        selection.append(categories.pop(random.randint(0, len(categories) - 1)))
    return render_template("singleplayer.html", categoriess = selection)

@app.route("/pvp")
def pvp():
    return render_template("pvp.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/play")
def play():
    return render_template("play.html")

@app.route("/")
def root():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route("/login")
@no_login_required
def login():
    return render_template('login.html')

@app.route("/auth", methods=["POST"])
@no_login_required
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
@no_login_required
def signup():
    data = db_manager.allCountries()
    return render_template("signup.html",options=data)

@app.route("/signupcheck", methods=["POST"])
@no_login_required
def signupcheck():
    username=request.form['username']
    password=request.form['password']
    confirm=request.form['confirmation']
    flag=request.form['flag']
    if flag=="":
        flag="United States of America"
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

#====================================================
#STARTING FROM HERE USER MUST BE LOGGED IN

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/leaderboard")
@login_required
def leaderboard():
    leaderboard=db_manager.userLeaderboard()
    return render_template("leaderboard.html", title="Leaderboard", rank=sorted(leaderboard.keys())[::-1] ,scoreDict=leaderboard)

@app.route("/nationboard")
@login_required
def nationboard():
    countryRank = db_manager.nationLeaderboard()
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)

@app.route("/mycountryboard")
@login_required
def mycountryboard():
    countryRank=db_manager.myCountryboard(user)
    return render_template("leaderboard.html", title="Country Leaderboard", rank=sorted(countryRank.keys())[::-1] ,scoreDict=countryRank)

@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out.')
    return redirect('/')

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

@app.route("/store")
def store():

    return render_template("store.html")

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
