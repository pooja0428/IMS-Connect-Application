from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '789654123'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('innovative_ideas.db')
    conn.row_factory = sqlite3.Row  # This allows access to columns by name
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

# User registration route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        name = request.form['name']
        email = request.form['email']
        region = request.form['region']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (employee_id, name, email, region, password) VALUES (?, ?, ?, ?, ?)', 
                           (employee_id, name, email, region, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered. Please login or use a different email."
    
    return render_template('signup.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['name']
            return redirect(url_for('home'))
        else:
            return "Invalid login credentials. Please try again."
    
    return render_template('login.html')

# Home page route
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Post idea route
@app.route('/post_idea', methods=['GET', 'POST'])
def post_idea():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ideas (title, description, votes, user_id, approved) VALUES (?, ?, 0, ?, 0)',
            (title, description, user_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('post_idea.html')





# Route for voting an idea
@app.route('/vote/<int:idea_id>', methods=['POST'])
def vote(idea_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Check if the user has already voted for this idea
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM votes WHERE user_id = ? AND idea_id = ?', (user_id, idea_id))
    existing_vote = cursor.fetchone()

    if existing_vote:
        # If the user has already voted, do nothing
        conn.close()
        return redirect(url_for('trending'))

    # If the user hasn't voted yet, record the vote and update the vote count for the idea
    cursor.execute('INSERT INTO votes (user_id, idea_id) VALUES (?, ?)', (user_id, idea_id))
    cursor.execute('UPDATE ideas SET votes = votes + 1 WHERE id = ?', (idea_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('trending'))

# Trending Ideas Route
@app.route('/trending')
def trending():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ideas WHERE approved = 1 ORDER BY votes DESC')  # Only approved ideas
    ideas = cursor.fetchall()
    conn.close()

    return render_template('trending.html', ideas=ideas)




# User profile page
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    cursor.execute('SELECT * FROM ideas WHERE user_id = ?', (user_id,))
    user_ideas = cursor.fetchall()
    conn.close()
    
    return render_template('profile.html', user=user, user_ideas=user_ideas)

# Admin login page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        admin_password = request.form['admin_password']

        if admin_id == 'admin' and admin_password == 'admin':
            session['admin_id'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials. Please try again."
    
    return render_template('admin_login.html')



@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    """if 'user_id' not in session or session['user_id'] != 'admin':  # Ensure only admin can access
        return redirect(url_for('login'))"""

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all users
    cursor.execute('SELECT id, name, email, region FROM users')
    users = cursor.fetchall()

    # Fetch all ideas
    cursor.execute('SELECT * FROM ideas')
    ideas = cursor.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', users=users, ideas=ideas)

@app.route('/change_approval/<int:idea_id>/<int:status>', methods=['POST'])
def change_approval(idea_id, status):
    """if 'user_id' not in session or session['user_id'] != 'admin':  # Ensure only admin can access
        return redirect(url_for('login'))"""

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the approval status
    cursor.execute('UPDATE ideas SET approved = ? WHERE id = ?', (status, idea_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))




# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('admin_id', None)
    return redirect(url_for('login'))

# Initialize the app
if __name__ == '__main__':
    app.run(debug=True)
