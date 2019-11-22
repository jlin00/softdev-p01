#Amanda Zheng , Jackie Lin, Junhee Lee, Michael Zhang (KIRKLAND MEESEEKS)
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template,request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os
from utl import db_builder, db_manager
from urllib.request import urlopen
from json import loads
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
#code for creating icons
icons=[]

for i in range(1, 200):
    data = loads(urlopen("https://rickandmortyapi.com/api/character/{}".format(str(i))).read())
    icons.append(data['image'])

#====================================================

#Michael's Code Below
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
@login_required
def profile():
    username=session['username']
    command = 'SELECT coll,money FROM user_tbl WHERE username="{}"'.format(username)
    raw = db_manager.exec(command).fetchall()
    iconstring = raw[0][0]
    money = raw[0][1]
    coll = iconstring.split(",")
    coll.remove('')
    stats = db_manager.getStats(username).items()
    return render_template("profile.html",
            stats=stats,
            coll=coll,
            not_owned=[item for item in icons if item not in coll],
            money=money,
            games=games)

@app.route("/icon", methods=["POST"])
@login_required
def icon():
    if 'img' not in request.form:
        flash("Please Select a Profile Icon!", "red")
        return redirect("/profile")
    command='UPDATE user_tbl SET pic="{}" WHERE username="{}";'.format(request.form['img'], session['username'])
    db_manager.exec(command)
    flash("Successfully set Player Icon", "blue")
    return redirect("/home")

@app.route("/resetpasswd", methods=["POST"])
@login_required
def password():
    #Jackie: Insert Code Here
    password = request.form['password']
    verif = request.form['verif']
    oldpass = request.form['oldpass']
    if (password == "" or verif == "" or oldpass == ""):
        flash("Please fill out all fields!", 'red')
        return redirect("/profile")
    if (password != verif):
        flash("Passwords do not match!", 'red')
        return redirect("/profile")
    username = session['username']
    if (not db_manager.userValid(username, oldpass)):
        flash("Wrong password!", 'red')
        return redirect("/profile")
    db_manager.changePass(username, password)
    flash("Password successfully changed!")
    return redirect("/home")

@app.route("/store")
def store():
    return render_template("store.html")
@app.route("/purchase")
def purchase():
    if request.args.get('value') == "R":

        return render_template("collection.html")
    elif request.args.get('value') == "S":
        return render_template("collection.html")
    else:
        return render_template("collection.html")

@app.route("/play", methods=['GET', 'POST'])
@login_required
def play():
    if request.method == 'GET':
        #display your games with search bar
        return render_template("games.html")
    game = request.form['id']
    command = 'SELECT team1,team2,playing FROM cached_game_tbl WHERE game_id="{}";'.format(game)
    raw = db_manager.exec(command)
    team1 = raw[0][0].split(',')
    team2 = raw[0][1].split(',')
    team1.remove('')
    team2.remove('')
    up = raw[0][2]
    t1 = (team1.pop(0), [])
    for user in team1:
        command = 'SELECT pic FROM user_tbl WHERE username="{}";'.format(user)
        raw = db_manager.exec(command)
        t1[1].append((user, raw[0][0]))
    t2 = (team2.pop(0), [])
    for user in team2:
        command = 'SELECT pic FROM user_tbl WHERE username="{}";'.format(user)
        raw = db_manager.exec(command)
        t2[1].append((user, raw[0][0]))
    if "T" in game:
        #team rally
        return render_template("_gameplay.html",
                player=session['username'],
                up=up,
                t1=t1,
                t2=t2)
    if "P" in game:
        #pvp
        return render_template("_gameplay.html",
                player=session["username"],
                up=up,
                t1=t1,
                t2=t2)
    #single player
    return render_template("_gameplay.html",
            player=session["username"],
            up=up,
            t1=t1)

@app.route("/triviacheck")
@login_required
def check():
    #check answer and update points accordingly
    return redirect("/play")

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
