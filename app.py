from flask import Flask, redirect, url_for, \
				  request, render_template, json
from pymongo import MongoClient
import pymongo
import os
import socket
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = MongoClient('mongodb://backend:27017/dockerdemo')
db = client.blogpostDB

app = Flask(__name__)

@app.route("/")
def landing_page():
    posts = get_all_posts()
    
    return render_template('blog.html', posts=json.loads(posts))

@app.route("/edit/<post_id>")
def edit_page(post_id):
    post = get_post(post_id)
    return render_template('blog_entry.html', post=json.loads(post))


@app.route('/add_post', methods=['POST'])
def add_post():

    new()
    return redirect(url_for('landing_page'))


@app.route('/edit_post/<post_id>', methods=['POST'])
def edit_post(post_id):

    edit(post_id)
    return redirect(url_for('landing_page'))


@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):

    delete(post_id)
    return redirect(url_for('landing_page'))


@app.route('/remove_all')
def remove_all():
    db.blogpostDB.delete_many({})

    return redirect(url_for('landing_page'))


## Services
@app.route("/posts", methods=['GET'])
def get_all_posts():
    
    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]
    return JSONEncoder().encode(posts)

@app.route("/post/<post_id>", methods=['GET'])
def get_post(post_id):
    
    _post = db.blogpostDB.find_one({"_id":ObjectId(post_id)})
    return JSONEncoder().encode(_post)


@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'title': request.form['title'],
        'post': request.form['post']
    }
    db.blogpostDB.insert_one(item_doc)

    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]

    return JSONEncoder().encode(posts[-1])


### Insert function here ###
@app.route('/post/<post_id>', methods=['PUT'])
def edit(post_id):

    item_doc = {
        'title': request.form['title'],
        'post': request.form['post']
    }
    db.blogpostDB.update({"_id":ObjectId(post_id)},item_doc)

    return get_post(post_id)


@app.route('/post/<post_id>', methods=['DELETE'])
def delete(post_id):

    db.blogpostDB.delete_one({"_id":ObjectId(post_id)})

    return JSONEncoder().encode({})
############################


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
