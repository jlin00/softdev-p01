#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3, urllib, json

gameID = 0;
DB_FILE = "trivia.db"

#commits the changes after a command
def exec(cmd):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd)
    db.commit()
    return output

#executing using ? placeholder
def execmany(cmd, inputs):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd, inputs)
    db.commit()
    return output

#==========================================================
#creates tables if they do not exist with necessary columns
def build_db():
    command = "CREATE TABLE IF NOT EXISTS user_tbl (username TEXT, password TEXT, pic TEXT, coll TEXT, game_id TEXT, money INT, flag TEXT, stat TEXT, score INT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS game_tbl (game_id TEXT, participants TEXT, team1 TEXT, team2 TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS question_tbl (category TEXT, question TEXT, diff TEXT, choices TEXT, answer TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS cached_game_tbl (game_id TEXT, type TEXT, participants TEXT, team1 TEXT, team2 TEXT, playing TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS flags_tbl (country TEXT PRIMARY KEY, flag TEXT)"
    exec(command)

def build_question():
    u = urllib.request.urlopen("https://opentdb.com/api.php?amount=1&type=multiple")
    response = json.loads(u.read())
    qtype = response['results'][0]['category']
    q = response['results'][0]['question']
    qdiff = response['results'][0]['difficulty']
    randomint = random.randint(0, 3)
    if (randomint == 0):
        qchoices = response['results'][0]['correct_answer'] + "," + response['results'][0]['incorrect_answers'][0] + "," + response['results'][0]['incorrect_answers'][1] + "," + response['results'][0]['incorrect_answers'][2]
    if (randomint == 1):
        qchoices = response['results'][0]['incorrect_answers'][0] + "," + response['results'][0]['correct_answer'] + "," + response['results'][0]['incorrect_answers'][1] + "," + response['results'][0]['incorrect_answers'][2]
    if (randomint == 2):
        qchoices = response['results'][0]['incorrect_answers'][0] + "," + response['results'][0]['incorrect_answers'][1] + "," + response['results'][0]['correct_answer'] + "," + response['results'][0]['incorrect_answers'][2]
    if (randomint == 3):
        qchoices = response['results'][0]['incorrect_answers'][0] + "," + response['results'][0]['incorrect_answers'][1] + "," + response['results'][0]['incorrect_answers'][2] + "," + response['results'][0]['correct_answer']
    qans = response['results'][0]['correct_answer']
        q = "INSERT INTO question_tbl VALUES(?, ?)"
        inputs = (country['name'], country['flag'])
        execmany(q, inputs)

#populates flag_tbl if it isn't already populated
def build_flag():
    command = "SELECT * FROM flags_tbl;"
    data = exec(command).fetchone()
    if (data is None):
        #print("EXECUTING BUILD_FLAG")
        u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all?fields=name;flag")
        response = json.loads(u.read())
        for country in response:
            q = "INSERT OR IGNORE INTO flags_tbl VALUES(?, ?)"
            inputs = (country['name'], country['flag'])
            execmany(q, inputs)
    #else:
        #print("NOT EXECUTING BUILD_FLAG")
