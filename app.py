from flask import Flask, render_template
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/database')
def login():
    return render_template('database.html')

@app.route('/contact')
def view_bookbag():
    return render_template('contact.html')

@app.route('/leaderboard')
def signup():
    return render_template('leaderboard.html')

if __name__ == "__main__":
    app.run(debug = True)