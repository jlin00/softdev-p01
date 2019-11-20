#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3
from utl.db_builder import exec

#====================================================

#add user-provided credentials to database
def addUser(username, password, flag):
    q = "SELECT * FROM user_tbl WHERE username = '%s';" % username
    data = exec(q).fetchone()
    if (data is None):
        q = "INSERT INTO user_tbl VALUES('%s', '%s', '', '', '', 200, '%s', '', 0);" % (username, password, flag)
        exec(q)
        return True
    return False #if username already exists

#turns tuple into a list
def formatFetch(results):
    collection=[]
    for item in results:
        if str(item) not in collection:
            collection.append(str(item)[2:-3])
    return collection

#====================================================
