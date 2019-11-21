#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3, urllib, json

DB_FILE = "trivia.db"

#commits the changes after a command
def exec(cmd):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd)
    db.commit()
    return output

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

#populates flag_tbl if it isn't already populated
def build_flag():
    command = "SELECT * FROM flags_tbl;"
    data = exec(command).fetchone()
    if (data is None):
        print("EXECUTING BUILD_FLAG")
        u = urllib.request.urlopen("https://restcountries.eu/rest/v2/all?fields=name;flag")
        response = json.loads(u.read())
        for country in response:
            q = "INSERT OR IGNORE INTO flags_tbl VALUES(?, ?)"
            inputs = (country['name'], country['flag'])
            execmany(q, inputs)
    #else:
        #print("NOT EXECUTING BUILD_FLAG")
