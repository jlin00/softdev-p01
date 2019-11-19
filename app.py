#Amanda Zheng
#SoftDev1 pd1
#K25: Getting More Rest
#2019-11-13
from flask import Flask , render_template
import urllib, json
from json import loads
app = Flask(__name__)

#Michael's Code Below
@app.route("/login")
def login():
    return "Hello World"
#Amanda's Code Below
@app.route("/signup")
def signup():



if __name__ == "__main__":
    app.debug = True
    app.run()
