# Junhee Lee, Jackie Lin, Michael Zhang, Amanda Zheng (KIRKLAND MEESEEKS)
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
        flash('You must be logged in to view this page!', 'alert-danger')
        return redirect('/')
    return dec

# decorator for checking no login
def no_login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'username' not in session:
            return f(*args, **kwargs)
        flash('You cannot view this page while logged in!', 'alert-danger')
        return redirect('/home')
    return dec
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
        flash('Please fill out all fields!', 'alert-danger')
        return render_template("login.html")
    if (db_manager.userValid(enteredU,enteredP)):
        flash('You were successfully logged in!', 'alert-success')
        session['username'] = enteredU
        return redirect('/home')
    else:
        flash('Wrong Credentials!', 'alert-danger')
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
        flash('Please fill out all fields!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    if (confirm!=password):
        flash('Passwords do not match!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    added = db_manager.addUser(username,password,flag)
    if (not added):
        flash('Username taken!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    #return redirect(url_for("leaderboard"))
    flash('You have successfully created an account! Please log in!', 'alert-success')
    return redirect("/login")

#====================================================
#STARTING FROM HERE USER MUST BE LOGGED IN

@app.route("/home")
@login_required
def home():
    username = session['username']
    pic = db_manager.getPic(username)
    score = db_manager.getScore(username)
    money = db_manager.getMoney(username)
    stats = db_manager.getStats(username).items()
    return render_template("home.html", home="active", user=username, pic=pic, score=score, money=money, stats=stats)

@app.route("/leaderboard")
@login_required
def leaderboard():
    user = session['username']
    country = db_manager.getCountry(user)
    leaderboard=db_manager.userLeaderboard()
    nationboard=db_manager.nationLeaderboard()
    countryboard=db_manager.myCountryboard(user)
    return render_template("leaderboard.html",
                            leaderboard=enumerate(leaderboard.items()),
                            nationboard=enumerate(nationboard.items()),
                            countryboard=enumerate(countryboard.items()),
                            country=country)

@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out.', 'alert-success')
    return redirect('/')

#profile pages below
@app.route("/profile")
@login_required
def profile():
    username=session['username']
    command = 'SELECT coll,money,game_id FROM user_tbl WHERE username=?'
    inputs = (username, )
    raw = db_manager.execmany(command, inputs).fetchone()
    iconstring = raw[0]
    coll = iconstring.split(",")
    money = raw[1]
    games = raw[2].split(",")
    return render_template("profile.html",
            enumcoll=range(len(coll)),
            coll=coll,
            money=money,
            games=games,
            profile="active")

@app.route("/icon", methods=["POST"])
@login_required
def icon():
    if 'img' not in request.form:
        flash("Please Select a Profile Icon!", "alert-danger")
        return redirect("/profile")
    index = int(request.form['img'])
    user = session['username']
    img = db_manager.getColl(user)[index]
    db_manager.updatePic(user, img)
    flash("Successfully set Player Icon", 'alert-success')
    return redirect("/home")

@app.route("/resetpasswd", methods=["POST"])
@login_required
def password():
    #Jackie: Insert Code Here
    password = request.form['password']
    verif = request.form['verif']
    oldpass = request.form['oldpass']
    if (password == "" or verif == "" or oldpass == ""):
        flash("Please fill out all fields!", 'alert-danger')
        return redirect("/profile")
    if (password != verif):
        flash("Passwords do not match!", 'alert-danger')
        return redirect("/profile")
    username = session['username']
    if (not db_manager.userValid(username, oldpass)):
        flash("Wrong password!", 'alert-danger')
        return redirect("/profile")
    db_manager.changePass(username, password)
    flash("Password successfully changed!", 'alert-success')
    return redirect("/home")

@app.route("/store")
def store():
    return render_template("store.html")

@app.route("/purchase")
def purchase():
    username = session['username']
    selection = int(request.args['value'])
    purchased = db_manager.purchase(username, selection)
    if (purchased):
        flash('Purchase successfully made!','alert-success')
    flash('You don\'t have enough money to make this purchase!', 'alert-danger')
    return redirect(url_for("store"))

@app.route("/play", methods=['GET', 'POST'])
@login_required
def play():
    if request.method == 'GET':
        #display your games with search bar
        command = 'SELECT game_id FROM user_tbl WHERE username="{}"'.format(session['username'])
        games = db_manager.exec(command).fetchall()
        games=games[0][0].split(",")
        games.remove('')
        team = []
        pvp = []
        single = []
        for game in games:
            if "T" in game:
                team.append(game)
            elif "P" in game:
                pvp.append(game)
            else:
                single.append(game)
        return render_template("games.html",
                team=team,
                pvp=pvp,
                single=single,
                play="active")
    game = request.form['id']
    if game == 'new':
        #create game
        redirect("/play")
    command = 'SELECT team1,team2,playing FROM cached_game_tbl WHERE game_id="{}";'.format(game)
    raw = db_manager.exec(command).fetchall()
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
    #fetch question from API
    raw = urlopen("https://opentdb.com/api.php?amount=1&type=multiple").read()
    question = loads(raw)['results'][0]
    choices = question['incorrect_answers']
    choices.append(question['correct_answer'])
    #cache
    command='INSERT INTO cached_question_tbl VALUES ("{}", "{}", "{}", "{}", "{}")'.format(question['category'],
            question['question'],
            question['difficulty'],
            choices,
            question['correct_answer'])
    q = question['question'] #question here
    c = set(choices) #choices
    if "T" in game:
        #team rally
        return render_template("_gameplay.html",
                player=session['username'],
                up=up,
                t1=t1,
                t2=t2,
                question=q,
                choices=c,
                game=game)
    if "P" in game:
        #pvp
        return render_template("_gameplay.html",
                player=session["username"],
                up=up,
                t1=t1,
                t2=t2,
                question=q,
                choices=c,
                game=game)
    #single player
    return render_template("_gameplay.html",
            player=session["username"],
            up=up,
            t1=t1,
            t2=['', []],
            question=q,
            choices=c,
            game=game)

@app.route("/triviacheck", methods=['POST'])
@login_required
def check():
    command = 'SELECT answer FROM cached_question_tbl WHERE question="{}"'.format(request.form['question'])
    ans = db_manager.exec(command).fetchall()
    #if ans[0][0] == request.form['answer']:
        #correct answer
        #update points
    command = 'SELECT participants FROM game_tbl WHERE game_id="{}"'.format(request.form['id'])
    participants = db_manager.exec(command).fetchall()[0][0].split(',')
    participants.remove('')
    player = participants.index(session['username'])
    command = 'UPDATE cached_game_tbl SET playing="{}" WHERE game_id="{}"'.format(participants[player - 1], request.form['id'])
    db_manager.exec(command)
    return redirect("/play")

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    app.debug = True
    app.run()
