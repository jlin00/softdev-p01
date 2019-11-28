#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-12-04

from flask import Flask , render_template,request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os
from utl import db_builder, db_manager
import random

app = Flask(__name__)
app.secret_key = os.urandom(32)

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
    if(enteredU == "" or enteredP == ""): #if fields empty
        flash('Please fill out all fields!', 'alert-danger')
        return redirect(url_for('login'))
    if (db_manager.userValid(enteredU,enteredP)): #returns true if login successful
        flash('You were successfully logged in!', 'alert-success')
        session['username'] = enteredU
        return redirect(url_for('home'))
    else:
        flash('Wrong Credentials!', 'alert-danger')
        return redirect(url_for('login'))

@app.route("/signup")
@no_login_required
def signup():
    data = db_manager.allCountries()
    return render_template("signup.html", options=data)

@app.route("/signupcheck", methods=["POST"])
@no_login_required
def signupcheck():
    username = request.form['username']
    password = request.form['password']
    confirm = request.form['confirmation']
    flag = request.form['flag']
    if flag == "": #default country is USA
        flag = "United States of America"
    allcountries = db_manager.allCountries()
    #preliminary checks on entered fields
    if(username == "" or password == "" or confirm == ""):
        flash('Please fill out all fields!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    if ("," in username):
            flash('Commas are not allowed in username!', 'alert-danger')
            return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    if (confirm!=password):
        flash('Passwords do not match!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    #form information delivered to backend
    added = db_manager.addUser(username,password,flag) #returns True if user was sucessfully added
    if (not added):
        flash('Username taken!', 'alert-danger')
        return render_template("signup.html", username=username,password=password,confirm=confirm,flag=flag,options=allcountries)
    flash('You have successfully created an account! Please log in!', 'alert-success')
    return redirect(url_for('login'))

#====================================================
#STARTING FROM HERE USER MUST BE LOGGED IN

@app.route("/home")
@login_required
def home():
    username = session['username']
    owner = session['username'] #owner of the profile
    if (request.args): #if querystring exists
        if ('user' in request.args): #if username was given, display that user's profile
            username = request.args['user']
        elif ('value' in request.args): #if value of profile picture given
            pic = db_manager.getpfp(request.args['value']) #checks if picture exists
            if (pic is not None): #if picture exists, change user's profile picture
                db_manager.updatePic(username, pic)
    isOwner = False
    if (owner == username): #if logged-in user matches owner of profile
        isOwner = True
    pic = db_manager.getPic(username)
    score = db_manager.getScore(username)
    money = db_manager.getMoney(username)
    stats = db_manager.getStats(username).items()
    ##### code to get games of user
    return render_template("home.html", home="active", user=username, pic=pic, score=score, money=money, stats=stats, isOwner=isOwner)

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
                            country=country,
                            board="active")

@app.route("/profile")
@login_required
def profile():
    username=session['username']
    command = 'SELECT coll,money,game_id FROM user_tbl WHERE username=?'
    inputs = (username, )
    raw = db_manager.execmany(command, inputs).fetchone()
    iconstring = raw[0]
    coll = iconstring.split(",")
    collID = db_manager.getCollID(username)
    money = raw[1]
    games = raw[2].split(",")
    return render_template("profile.html",
            enumcoll=range(len(coll)),
            coll=coll,
            collID=collID,
            money=money,
            games=games,
            profile="active")

@app.route("/resetpasswd", methods=["POST"])
@login_required
def password():
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
@login_required
def store():
    return render_template("store.html", store="active")

@app.route("/purchase")
@login_required
def purchase():
    username = session['username']
    selection = int(request.args['value'])
    purchased = db_manager.purchase(username, selection)
    if (purchased):
        flash('Purchase successfully made!','alert-success')
    else:
        flash('You don\'t have enough money to make this purchase!', 'alert-danger')
    return redirect(url_for("store"))

@app.route("/play", methods=['GET', 'POST'])
@login_required
def play():
    username = session['username']
    if request.method == 'GET':
        #display your games with search bar
        team = db_manager.getTeam(username)
        pvp = db_manager.getPVP(username)
        single = db_manager.getSingle(username)
        return render_template("games.html",
                team=team,
                pvp=pvp,
                single=single,
                play="active")
    if 'id' in request.form:
        game = request.form['id']
    else:
        game = request.args['id']
    command = 'SELECT team1,team2,playing FROM game_tbl WHERE game_id="{}";'.format(game)
    raw = db_manager.exec(command).fetchall()
    team1 = raw[0][0].split(',')
    team2 = raw[0][1].split(',')
    if (team1.count('') > 0):
        team1.remove('')
    if (team2.count('') > 0):
        team2.remove('')
    up = raw[0][2] #who's up next
    t1 = (team1.pop(0), team1.pop(0), [])
    for user in team1:
        t1[2].append(user)
    #single player exceptions
    single=True
    if ("S" not in game):
        single=False
        t2 = (team2.pop(0), [])
        for user in team2:
            t2[1].append(user)
    else:
        t2=['', []]
    #check if game is completed
    if (db_manager.gameCompleted(game)):
        return render_template("completed.html", t1=t1, t2=t2, completed=True, single=single)
    #get current question
    questionEntry = db_manager.getCurrentQuestion(username, game)
    if (questionEntry is None):
        db_manager.updateQuestion(username, game)
        questionEntry = db_manager.getCurrentQuestion(username, game)
    question = questionEntry[1]
    choices = set(questionEntry[3].split("~"))
    category = questionEntry[0]
    num = db_manager.currentNumber(username, game)
    started = db_manager.gameStarted(game)
    return render_template("gameplay.html",
                started=started,
                player=username,
                up=up,
                t1=t1,
                t2=t2,
                question=question,
                choices=choices,
                game=game,
                category=category,
                single=single,
                num=num)

@app.route("/new", methods=['POST'])
@login_required
def create():
    #create game code here
    username = session['username']
    if 'p' in request.form['id']:
        #check if there exists a game with room first
        return 'under construction'
    #else:
            #command = 'INSERT INTO game_tbl VALUES ();'
    elif 't' in request.form['id']:
        #check if there exists a game with room first
        return 'under construction'
        #else:
            #command = 'INSERT INTO game_tbl VALUES ();'
    else:
        db_manager.addSingle(username)
    return redirect("/play")

@app.route("/triviacheck", methods=['POST'])
@login_required
def check():
    game_id = request.form['id']
    username = session['username']
    command = 'SELECT answer FROM question_tbl WHERE question=?;'
    inputs = (request.form['question'], )
    ans = db_manager.execmany(command, inputs).fetchall()
    if 'answer' not in request.form:
        flash("Please select an answer!", 'alert-danger')
        return redirect(url_for("play", id=game_id), code=307)
    else:
        if ans[0][0] == request.form['answer']:
            #correct answer
            command = 'SELECT team1, team2 FROM game_tbl WHERE game_id="{}";'.format(game_id)
            teams = db_manager.exec(command).fetchall()[0]
            team1 = teams[0]
            team2 = teams[1]
            if username in teams[0]:
                data = teams[0].split(',')
                data[0] = str(int(data[0]) + 10)
                team1 = ",".join(data)
            if username in teams[1]:
                data = teams[1].split(',')
                data[0] = str(int(data[0]) + 10)
                team2 = ",".join(data)
            command = 'UPDATE game_tbl SET team1="{}", team2="{}" WHERE game_id="{}";'.format(team1, team2, game_id)
            db_manager.exec(command)
            #update score
            command = 'SELECT score FROM user_tbl WHERE username=?'
            inputs = (username, )
            data = db_manager.execmany(command, inputs).fetchone()[0]
            data += 10
            command = 'UPDATE user_tbl SET score=? WHERE username=?'
            inputs = (data, username)
            db_manager.execmany(command, inputs)
            flash('Correct!', 'alert-success')
        else:
            flash('Wrong answer!', 'alert-danger')

    command = 'SELECT participants FROM game_tbl WHERE game_id="{}";'.format(game_id)
    participants = db_manager.exec(command).fetchall()[0][0].split(',')
    if (participants.count('') > 0):
        participants.remove('')
    player = participants.index(username)
    command = 'UPDATE game_tbl SET playing="{}" WHERE game_id="{}";'.format(participants[player - 1], game_id)
    db_manager.exec(command)
    command = 'SELECT stat FROM user_tbl WHERE username=?;'
    inputs = (username, )
    data = db_manager.execmany(command, inputs).fetchone()[0].split(",")
    for i in range(len(data)):
        category = data[i].split("|")
        if category[0] == request.form['category']:
            if ans[0][0] == request.form['answer']:
                category[1] = str(int(category[1]) + 1)
            category[2] = str(int(category[2]) + 1)
        data[i] = "|".join(category)
    data = ",".join(data)
    command = 'UPDATE user_tbl SET stat=? WHERE username=?'
    inputs = (data, username)
    db_manager.execmany(command, inputs)
    db_manager.updateQuestion(username, game_id)
    return redirect(url_for("play"), code=307)

@app.route("/search")
@login_required
def search():
    if (request.args):
        if ('select' in request.args and 'query' in request.args):
            select = request.args['select']
            query = request.args['query'] #search keyword
            results = []
            byUser = False
            user=""
            game=""
            if (select == "byuser"):
                results = db_manager.findUser(query)
                byUser = True
                user = "selected"
            if (select == "bygame"):
                results = db_manager.findGame(query)
                game = "selected"
            return render_template('search.html', results=results, byUser=byUser, search="active", user=user, game=game)
    return render_template('search.html', search="active")

@app.route("/logout")
def logout():
    session.clear()
    flash('You were successfully logged out.', 'alert-success')
    return redirect('/')

if __name__ == "__main__":
    db_builder.build_db()
    db_builder.build_flag()
    db_builder.build_pic()
    db_builder.build_question()
    app.debug = True
    app.run()
