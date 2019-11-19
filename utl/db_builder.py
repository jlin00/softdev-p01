#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3

DB_FILE = "trivia.db"

#commits the changes after a command
def exec(cmd):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd)
    db.commit()
    return output

#==========================================================
#creates tables if they do not exist with necessary columns
def build_db():
    command = "CREATE TABLE IF NOT EXISTS user_tbl (username TEXT, password TEXT, pic TEXT, coll TEXT, game_id TEXT, money INT, flag TEXT, stat TEXT, score INT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS game_tbl (game_id TEXT, type TEXT, participants TEXT, team1 TEXT, team2 TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS question_tbl (category TEXT, question TEXT, diff TEXT, choices TEXT, answer TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS cached_game_tbl (game_id TEXT, type TEXT, participants TEXT, team1 TEXT, team2 TEXT, playing TEXT)"
    exec(command)
