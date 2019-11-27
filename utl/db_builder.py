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

    command = "SELECT * FROM user_tbl WHERE username='jackielin'" #dummy account
    data = exec(command).fetchone()
    if (data is None):
        u = urllib.request.urlopen("https://opentdb.com/api_category.php")
        response = json.loads(u.read())['trivia_categories']
        allcategories = ""
        for category in response:
            allcategories += category['name'] + "|0|0,"
        #print(allcategories)
        allcategories = allcategories[0:-1]
        command = "INSERT OR IGNORE INTO user_tbl VALUES('jackielin', '123', '', '', '', 2000, '', '%s', 0)" % allcategories
        exec(command)

    command = "CREATE TABLE IF NOT EXISTS game_tbl (game_id TEXT, participants TEXT, team1 TEXT, team2 TEXT, playing TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS question_tbl (category TEXT, question TEXT PRIMARY KEY, diff TEXT, choices TEXT, answer TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS flags_tbl (country TEXT PRIMARY KEY, flag TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS pic_tbl (category TEXT, pic TEXT PRIMARY KEY)"
    exec(command)

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

#build pic cache
def build_pic():
    command = "SELECT * FROM pic_tbl;"
    data = exec(command).fetchone()
    if (data is None):
        q = "INSERT OR IGNORE INTO pic_tbl VALUES(?, ?)"

        #building Rick and Morty picture cache
        for i in range(80):
            i = i + 1
            pic = "https://rickandmortyapi.com/api/character/avatar/%d.jpeg" % i
            id = "R" + str(i)
            inputs = (id, pic)
            execmany(q, inputs)

        #building lorem picsum picture cache
        url = "https://picsum.photos/v2/list?page=1&limit=80"
        u = urllib.request.urlopen(url)
        response = json.loads(u.read())
        for entry in response: #take every id
            id = entry['id']
            pic = "https://picsum.photos/id/%s/250" % id
            id = "M" + id
            inputs = (id, pic)
            execmany(q, inputs)

        #building pokemon picture cache
        for i in range(80):
            i = i + 1
            pic = "https://pokeres.bastionbot.org/images/pokemon/%d.png" % i
            id = "P" + str(i)
            inputs = (id, pic)
            execmany(q, inputs)

#build question cache
def build_question():
    command = "SELECT * FROM question_tbl;"
    data = exec(command).fetchone()
    if (data is None):
        return data
