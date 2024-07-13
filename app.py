from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

app = Flask(__name__)

# SQLite database file path
DB_FILE = 'fish.db'

# Route to handle adding a new fish caught
@app.route('/add_fish', methods=['POST'])
def add_fish():
    if request.method == 'POST':
        fishcaught = request.form['fish_caught']
        sizeoffish = request.form['size_of_fish']
        bait = request.form['bait']
        pondcaught = request.form['pond_caught']
        dateofcatch = request.form['date_of_catch']  # Get date of catch from form
        timeofcatch = request.form['time_of_catch']
        catcher = request.form['catcher']
        image_url = request.form['image_url'] if 'image_url' in request.form else None

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT INTO fishcaught
                     (fishcaught, sizeoffish, bait, pondcaught, dateofcatch, timeofcatch, catcher, image)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (fishcaught, sizeoffish, bait, pondcaught, dateofcatch, timeofcatch, catcher, image_url))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

# Route to display form for adding a new fish caught
@app.route('/add_fish_form')
def add_fish_form():
    return render_template('add_fish_form.html')

# Route to display all fish caught
@app.route('/database')
def database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''SELECT * FROM fishcaught''')
    fish_list = c.fetchall()

    df = pd.DataFrame(fish_list, columns=['id', 'fishcaught', 'sizeoffish', 'bait', 'pondcaught', 'dateofcatch', 'timeofcatch', 'catcher', 'image'])

    # Create plots
    plot_number_of_catches_per_person(df)
    plot_number_of_catches_per_bait(df)

    conn.close()
    return render_template('database.html', fish_list=fish_list)

# Function to create a plot for the number of catches per person
def plot_number_of_catches_per_person(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(x='catcher', data=df)
    plt.title('Number of Catches per Person')
    plt.xlabel('Catcher')
    plt.ylabel('Number of Catches')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/number_of_catches_per_person.png')
    plt.close()

# Function to create a plot for the number of catches per bait
def plot_number_of_catches_per_bait(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(x='bait', data=df)
    plt.title('Number of Catches per Bait')
    plt.xlabel('Bait')
    plt.ylabel('Number of Catches')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/number_of_catches_per_bait.png')
    plt.close()

# Route for other pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

if __name__ == "__main__":
    app.run(debug=True)
