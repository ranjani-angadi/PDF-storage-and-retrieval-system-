from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "digital_library"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
conn = sqlite3.connect("library.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,      
    filename TEXT
)
""")

conn.commit()
conn.close()

# Login
@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/dashboard')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    conn.close()

    return render_template("dashboard.html", books=books)

# Upload book
@app.route('/upload', methods=['GET','POST'])
def upload():

    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']
        category = request.form['category']

        file = request.files['pdf']

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO books(title,author,category,filename) VALUES(?,?,?,?)",
            (title,author,category,filename)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template("upload.html")

# Download PDF
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

# Search
@app.route('/search')
def search():

    keyword = request.args.get('keyword')

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM books WHERE title LIKE ?",
        ('%' + keyword + '%',)
    )

    books = cur.fetchall()

    conn.close()

    return render_template("dashboard.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)