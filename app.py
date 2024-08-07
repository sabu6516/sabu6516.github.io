from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import csv
import os
from io import BytesIO
import base64

app = Flask(__name__)

# SQLite database file path
DB_FILE = 'fish.db'

# Function to initialize the database and create the table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create fishcaught table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS fishcaught (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fishcaught VARCHAR(255) NOT NULL,
                    weight REAL,  -- Allow weight to be nullable
                    bait VARCHAR(100) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    dateofcatch DATE NOT NULL,
                    timeofcatch TIME NOT NULL,
                    catcher VARCHAR(100) NOT NULL,
                    image TEXT
                )''')

    conn.commit()
    conn.close()

# Initialize the database on application startup
init_db()

# Route to add a new fish caught
@app.route('/add_fish', methods=['POST'])
def add_fish():
    if request.method == 'POST':
        try:
            fish_caught = request.form['fish_caught']
            weight = request.form['weight']
            bait = request.form['bait']
            location = request.form['location']
            date_of_catch = request.form['date_of_catch']
            time_of_catch = request.form['time_of_catch']
            catcher = request.form['catcher']
            image_url = request.form['image_url']

            # Validate form data
            if not fish_caught or not bait or not location or not date_of_catch or not time_of_catch or not catcher:
                return render_template('add_fish_form.html', error_message='Error: All fields are required!')

            # Connect to SQLite database
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()

            # Insert into database
            c.execute('''INSERT INTO fishcaught (fishcaught, weight, bait, location, dateofcatch, timeofcatch, catcher, image)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (fish_caught, weight, bait, location, date_of_catch, time_of_catch, catcher, image_url))
            conn.commit()
            conn.close()

            # Redirect to add_fish_form with success message
            return redirect(url_for('add_fish_form', message='Fish added successfully!'))

        except Exception as e:
            return render_template('add_fish_form.html', error_message=f'Error adding fish: {str(e)}')

    return redirect(url_for('add_fish_form'))

# Route to display form for adding a new fish caught
@app.route('/add_fish_form')
def add_fish_form():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Fetch all entries from the fishcaught table
    c.execute('''SELECT id, fishcaught, weight, bait, location, dateofcatch, timeofcatch, catcher, image FROM fishcaught''')
    entries = c.fetchall()

    conn.close()

    return render_template('add_fish_form.html', entries=entries)

@app.route('/delete_fish', methods=['POST'])
def delete_fish():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    try:
        entry_id = request.form['delete_entry']

        # Delete the selected entry from the database
        c.execute('''DELETE FROM fishcaught WHERE id = ?''', (entry_id,))
        conn.commit()

        message = 'Entry deleted successfully!'
    except Exception as e:
        print(str(e))
        message = 'Error: Failed to delete entry.'

    # Fetch all entries from the fishcaught table after deletion
    c.execute('''SELECT id, fishcaught, weight, bait, location, dateofcatch, timeofcatch, catcher, image FROM fishcaught''')
    entries = c.fetchall()

    conn.close()

    return render_template('add_fish_form.html', entries=entries, message=message)

# Route to display all fish caught
@app.route('/database')
def database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Fetch all entries from the fishcaught table
    c.execute('''SELECT * FROM fishcaught''')
    fish_list = c.fetchall()

    # Create DataFrame for plotting
    df = pd.DataFrame(fish_list, columns=['id', 'fishcaught', 'weight', 'bait', 'location', 'dateofcatch', 'timeofcatch', 'catcher', 'image'])

    # Generate plots
    catches_per_person_img = plot_number_of_catches_per_person(df)
    catches_per_bait_img = plot_number_of_catches_per_bait(df)
    catches_by_location_img = plot_by_location(df)

    conn.close()
    return render_template('database.html', fish_list=fish_list,
                           catches_per_person_img=catches_per_person_img,
                           catches_per_bait_img=catches_per_bait_img,
                           catches_by_location_img=catches_by_location_img)

# Function to create a plot for the number of catches per person
def plot_number_of_catches_per_person(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(x='catcher', data=df)
    plt.title('Number of Catches per Person')
    plt.xlabel('Catcher')
    plt.ylabel('Number of Catches')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to BytesIO
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    plt.close()
    return img_base64

# Function to create a plot for the number of catches per bait
def plot_number_of_catches_per_bait(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(x='bait', data=df)
    plt.title('Number of Catches per Bait')
    plt.xlabel('Bait')
    plt.ylabel('Number of Catches')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to BytesIO
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    plt.close()
    return img_base64

# Function to create a plot for the number of catches by location
def plot_by_location(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(x='location', data=df)
    plt.title('Number of Catches by Location')
    plt.xlabel('Location')
    plt.ylabel('Number of Catches')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to BytesIO
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

    plt.close()
    return img_base64

@app.route('/download_csv')
def download_csv():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Fetch all entries from the fishcaught table
        c.execute('''SELECT id, fishcaught, weight, bait, location, dateofcatch, timeofcatch, catcher FROM fishcaught''')
        entries = c.fetchall()

        conn.close()

        # Prepare CSV data
        csv_filename = 'fish_data.csv'
        csv_filepath = os.path.join(app.root_path, 'static', csv_filename)

        with open(csv_filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Fish Caught', 'Weight', 'Bait', 'Location', 'Date of Catch', 'Time of Catch', 'Catcher'])
            writer.writerows(entries)

        # Send CSV file as a download
        return send_file(csv_filepath, as_attachment=True)

    except Exception as e:
        return f"An error occurred: {str(e)}"

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
