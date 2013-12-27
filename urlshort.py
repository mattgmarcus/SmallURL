import os
from flask import Flask, request, render_template, url_for, redirect
from urlparse import urlparse
from pymongo import MongoClient

app = Flask(__name__)
url_collection = None

#Function to initialize database by connecting to it and getting the collection we use
def initDatabase():
    client = MongoClient("mongodb://mattgmarcus:smallurl@linus.mongohq.com:10057/SmallURL")
    database = client.SmallURL
    global url_collection 
    url_collection = database.url_collection

#Add an entry to the database for the handle/url pair
def addHandle(handle, url):
    url_collection.insert({"handle": handle, "url": url, "num_visits": 0})

#Return true if the handle exists in the database
def handleExists(handle):
    return (None != url_collection.find_one({"handle": handle}))

#When a page is visited through its handle, increment the num_visits attribute
def addVisit(entry):
    num_visits = entry["num_visits"] + 1
    url_collection.update({"_id": entry["_id"]}, {"$set": {"num_visits": num_visits}})

#Function to ensure that the user enters a url and handle that aren't just an empty string or spaces
def isValidEntry(handle, url):
    return not ( ("" == handle) or handle.isspace() or ("" == url) or url.isspace() )

#Function to add http to a url if it doesn't have it already
def normalizeURL(url):
    if '' == urlparse(url).scheme:
        url = "http://%s" % url
    return url

#Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create-handle", methods=["POST"])
def createHandle():
    #Get url and handle from form
    handle = request.form["handle"].lower()
    url = request.form["original_url"]

    #Check that the inputs are valid and in the proper format
    if not isValidEntry(handle, url):
        return render_template("index.html", error_msg="Invalid url/handle. Try again")
    url = normalizeURL(url)

    #Add the shortened url if it doesn't exist yet
    if not handleExists(handle):
        addHandle(handle, url)
        return render_template("result.html", handle=handle, url=url)
    else:
        return render_template("index.html", error_msg="Shortened URL already taken, try again")

@app.route("/<handle>")
def redirectUser(handle):
    handle = handle.lower()
    entry = url_collection.find_one({"handle": handle})
    if (None != entry):
        addVisit(entry)
        return redirect(entry["url"])
    else:
        return render_template("404.html")


if __name__=="__main__":
    initDatabase()
    p = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=p)
