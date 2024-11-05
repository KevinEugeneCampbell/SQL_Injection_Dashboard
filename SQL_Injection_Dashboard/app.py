from flask import Flask
from flask import render_template
from flask import request
import sqlite3

app = Flask(__name__)


# Function to initialize databases
def initialize_db(level):
    conn = sqlite3.connect(f'{level}_security.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    # Insert sample data if not already present
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin_pass')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'user', 'user_pass')")
    conn.commit()
    conn.close()


# Initialize all databases on startup
initialize_db('easy')
initialize_db('medium')
initialize_db('hard')


# SQL Injection Handler
def sql_injection_handler(level, attack_type, user_input):
    conn = sqlite3.connect(f'{level}_security.db')
    cursor = conn.cursor()
    response = None

    if level == 'easy':
        if attack_type == 'basic':
            query = f"SELECT * FROM users WHERE username = '{user_input}' AND password = '1' OR '1'='1'"
            #print(f"Executing Query: {query}")
            response = cursor.execute(query).fetchall()
        elif attack_type == 'union':
            query = f"SELECT id, username, password FROM users WHERE username = '{user_input}' UNION SELECT 1, username, password FROM users"
            response = cursor.execute(query).fetchall()
        elif attack_type == 'blind':
            query = f"SELECT * FROM users WHERE username = '{user_input}'"
            response = cursor.execute(query).fetchall()


    elif level == 'medium':
        user_input = user_input.replace("'", "''")
        if attack_type == 'basic':
            query = f"SELECT * FROM users WHERE username = '{user_input}' AND password = '{user_input}'"
            response = cursor.execute(query).fetchall()
        elif attack_type == 'union':
            query = f"SELECT * FROM users WHERE username = '{user_input}'"
            response = cursor.execute(query).fetchall()
        elif attack_type == 'blind':
            query = f"SELECT * FROM users WHERE username = '{user_input}'"
            response = cursor.execute(query).fetchall()

    elif level == 'hard':
        if attack_type == 'basic':
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            response = cursor.execute(query, (user_input, user_input)).fetchall()
        elif attack_type == 'union':
            query = "SELECT * FROM users WHERE username = ?"
            response = cursor.execute(query, (user_input,)).fetchall()
        elif attack_type == 'blind':
            query = "SELECT * FROM users WHERE username = ?"
            response = cursor.execute(query, (user_input,)).fetchall()

    conn.close()
    return response


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/attack', methods=['POST'])
def attack():
    security_level = request.form.get('security_level')
    sql_attack_type = request.form.get('attack_type')
    user_input = request.form.get('user_input')

    # Perform SQL injection
    result = sql_injection_handler(security_level, sql_attack_type, user_input)

    return render_template('index.html', result=result, security_level=security_level, sql_attack_type=sql_attack_type, user_input=user_input)


if __name__ == '__main__':
    app.run(debug=True)
