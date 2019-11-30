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
    if(enteredU == "admin"):
        flash('Login is disabled for this account!', 'alert-warning')
        return redirect(url_for('login'))
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
    return render_template("signup.html",options=data,flag="United States of America")

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
            db_manager.updatePic(username, request.args['value'])
    isOwner = False
    if (owner == username): #if logged-in user matches owner of profile
        isOwner = True
    pic = db_manager.getPic(username)
    score = db_manager.getScore(username)
    money = db_manager.getMoney(username)
    stats = db_manager.getStats(username).items()
    games = db_manager.getGames(username, owner)
    flag = db_manager.getFlag(username)
    return render_template("home.html", home="active", user=username, pic=pic, score=score, money=money, stats=stats, games=games, isOwner=isOwner, flag=flag)

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
    coll = db_manager.getColl(username)
    collID = db_manager.getCollID(username)
    return render_template("profile.html",
            enumcoll=range(len(coll)),
            coll=coll,
            collID=collID,
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

@app.route("/purchase", methods=["POST"])
@login_required
def purchase():
    username = session['username']
    value = request.form['value']
    selection = int(request.form['value'])
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
    db_manager.joinGame(username, game)
    started = db_manager.gameStarted(game)
    number = db_manager.getTeamNum(username, game)
    command = 'SELECT team1,team2,playing%s FROM game_tbl WHERE game_id=?;' % number
    inputs = (game, )
    raw = db_manager.execmany(command, inputs).fetchall()
    team1 = raw[0][0].split(',')
    team2 = raw[0][1].split(',')
    if (team1.count('') > 0):
        team1.remove('')
    if (team2.count('') > 0):
        team2.remove('')
    score1=0
    score2=0
    if(len(team1)>0 and len(team2)>0):
        score1=team1[0]
        score2=team2[0]
        if score1>score2:
            higher="1"
            highscore=score1
        else:
            highscore=score2
            higher="2"
            if username in team2:
                score1=team2[0]
                score2=team1[0]

    up = raw[0][2] #who's up next
    t1 = (team1.pop(0), team1.pop(0), [])
    for user in team1:
        t1[2].append(user)
    #single player exceptions
    single=True
    t2=['', []]
    if ("S" not in game):
        single=False
        if (started):
            t2 = (team2.pop(0), team2.pop(0), [])
            for user in team2:
                t2[2].append(user)
    #check if game is completed
    if (db_manager.gameCompleted(game)):
        if score1 != score2:
            if higher=="1":
                winners=team1
            else:
                winners=team2
            for user in winners:
                q="UPDATE user_tbl SET money = money + ? WHERE username=?"
                inputs = (highscore, user)
                db_manager.execmany(q, inputs)
        return render_template("completed.html", t1=t1, t2=t2, completed=True, single=single, code=303)
    #get current question
    questionEntry = db_manager.getCurrentQuestion(username, game)
    if (questionEntry is None):
        db_manager.updateQuestion(username, game)
        questionEntry = db_manager.getCurrentQuestion(username, game)
    question = questionEntry[1]
    choices = set(questionEntry[3].split("~"))
    category = questionEntry[0]
    num = db_manager.currentNumber(username, game)
    team = db_manager.getTeamNum(username, game)
    waiting = db_manager.team2Completed(game)
    currentteam = t2
    if (team == "1"):
        waiting = db_manager.team1Completed(game)
        currentteam = t1
    if (single):
        team1Completed = False
        team2Completed = False
    ##### EDIT TO RETURN WHICH TEAM THE PLAYER IS ON
    return render_template("gameplay.html",
                started=started,
                waiting=waiting,
                player=username,
                up=up,
                currentteam=currentteam,
                question=question,
                choices=choices,
                game=game,
                category=category,
                single=single,
                num=num,
                score=score1,
                Oscore=score2)

@app.route("/new", methods=['POST'])
@login_required
def create():
    username = session['username']
    if 'p' in request.form['id']:
        added = db_manager.joinPVP(username, "P")
    elif 't' in request.form['id']:
        added = db_manager.joinTeam(username, "T")
    else:
        added = db_manager.addSingle(username)
    if (not added):
        flash('Maximum number of games reached!', 'alert-danger')
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
            #correct answer, update team score
            number = db_manager.getTeamNum(username, game_id)
            command = 'SELECT team%s FROM game_tbl WHERE game_id=?' % number
            inputs = (game_id, )
            team = db_manager.execmany(command, inputs).fetchall()[0]
            data = team[0].split(',')
            data[0] = str(int(data[0]) + 10)
            team = ",".join(data)
            command = 'UPDATE game_tbl SET team%s=? WHERE game_id=?' % number
            inputs = (team, game_id)
            db_manager.execmany(command, inputs)
            #update user score
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
    #switch turns
    number = db_manager.getTeamNum(username, game_id)
    q = "SELECT team%s FROM game_tbl WHERE game_id=?" % number
    inputs = (game_id, )
    team = db_manager.execmany(q, inputs).fetchone()[0].split(",")
    team.pop(0) #pop score and question number
    team.pop(0)
    player = team.index(username)
    next = (player + 1) % 3
    if ("T" in game_id):
        command = 'UPDATE game_tbl SET playing%s=? WHERE game_id=?;' % number
        inputs = (team[next], game_id)
        db_manager.execmany(command, inputs)
    #update user stats
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
    #set next question for team
    db_manager.updateQuestion(username, game_id)
    return redirect(url_for("play", id=game_id), code=307)

@app.route("/search")
@login_required
def search():
    byUser = False
    byGame = False
    username = session['username']
    if (request.args):
        if ('select' in request.args and 'query' in request.args):
            select = request.args['select']
            query = request.args['query'] #search keyword
            results = []
            user=""
            game=""
            if (select == "byuser"):
                users = db_manager.findUser(query)
                games = []
                user = "selected"
                byUser = True
            if (select == "bygame"):
                users = []
                games = db_manager.findGame(username, query)
                game = "selected"
                byGame = True
            return render_template('search.html', users=users, games=games, byUser=byUser, byGame=byGame, search="active", user=user, game=game)
    return render_template('search.html', search="active")

@app.route("/logout")
@login_required
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
