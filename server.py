import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import http.cookies as Cookie
import hashlib
import os
from datetime import datetime

DB_NAME = 'site.db'
SECRET_KEY = 'changeme'

# Initialize database with admin user and posts table
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
# default admin login: admin/admin
hashed = hashlib.sha256('admin'.encode()).hexdigest()
try:
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', hashed))
except sqlite3.IntegrityError:
    pass
c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TEXT)')
conn.commit()
conn.close()

sessions = {}

def is_authenticated(headers):
    cookie = Cookie.SimpleCookie()
    if 'Cookie' in headers:
        cookie.load(headers['Cookie'])
        sid = cookie.get('sid')
        if sid and sid.value in sessions:
            return True
    return False

def render_template(title, body):
    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>{title}</title>
<link rel='stylesheet' href='/static/styles.css'>
</head>
<body>
<nav>
<a href='/'>Home</a> | <a href='/services'>Services</a> | <a href='/case-studies'>Case Studies</a> | <a href='/contact'>Contact</a>
</nav>
{body}
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.home()
        elif self.path == '/services':
            self.services()
        elif self.path == '/case-studies':
            self.case_studies()
        elif self.path == '/contact':
            self.contact()
        elif self.path.startswith('/static/'):
            self.serve_static()
        elif self.path == '/admin':
            self.login_page()
        elif self.path == '/dashboard':
            if is_authenticated(self.headers):
                self.dashboard()
            else:
                self.redirect('/admin')
        elif self.path.startswith('/edit/'):
            if is_authenticated(self.headers):
                self.edit_post()
            else:
                self.redirect('/admin')
        elif self.path.startswith('/delete/'):
            if is_authenticated(self.headers):
                self.delete_post()
            else:
                self.redirect('/admin')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/login':
            self.process_login()
        elif self.path == '/create':
            if is_authenticated(self.headers):
                self.create_post()
            else:
                self.redirect('/admin')
        elif self.path.startswith('/update/'):
            if is_authenticated(self.headers):
                self.update_post()
            else:
                self.redirect('/admin')
        elif self.path == '/contact':
            self.handle_contact()
        else:
            self.send_error(404)

    def serve_static(self):
        path = self.path.lstrip('/')
        if os.path.exists(path):
            self.send_response(200)
            if path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            self.end_headers()
            with open(path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def home(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        posts = c.execute('SELECT id, title, created_at FROM posts ORDER BY created_at DESC').fetchall()
        conn.close()
        items = ''.join([f"<li><a href='/edit/{p[0]}'>{p[1]}</a> ({p[2]})</li>" for p in posts])
        body = f"<h1>Welcome</h1><p>Consultancy for construction data and AI.</p><ul>{items}</ul>"
        self.respond(render_template('Home', body))

    def services(self):
        body = """
<h1>Services</h1>
<ul>
<li>Cost and Contract Management</li>
<li>Digital Transformation</li>
<li>Data Structuring and Analytics</li>
<li>AI Strategy and Implementation</li>
<li>Risk Management and Procurement Optimisation</li>
</ul>"""
        self.respond(render_template('Services', body))

    def case_studies(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        posts = c.execute('SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC').fetchall()
        conn.close()
        items = ''.join([f"<article><h2>{p[1]}</h2><p>{p[2]}</p><small>{p[3]}</small></article>" for p in posts])
        body = f"<h1>Case Studies & Insights</h1>{items}"
        self.respond(render_template('Case Studies', body))

    def contact(self):
        body = """
<h1>Contact</h1>
<form method='post' action='/contact'>
<input type='text' name='name' placeholder='Your Name' required><br>
<input type='email' name='email' placeholder='Your Email' required><br>
<textarea name='message' placeholder='Message'></textarea><br>
<button type='submit'>Send</button>
</form>"""
        self.respond(render_template('Contact', body))

    def handle_contact(self):
        length = int(self.headers.get('Content-Length', 0))
        data = parse_qs(self.rfile.read(length).decode())
        print('Contact form submitted', data)
        body = '<p>Thank you for your message.</p>'
        self.respond(render_template('Contact', body))

    def login_page(self):
        body = """
<h1>Admin Login</h1>
<form method='post' action='/login'>
<input type='text' name='username' placeholder='Username' required><br>
<input type='password' name='password' placeholder='Password' required><br>
<button type='submit'>Login</button>
</form>"""
        self.respond(render_template('Login', body))

    def dashboard(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        posts = c.execute('SELECT id, title, created_at FROM posts ORDER BY created_at DESC').fetchall()
        conn.close()
        items = ''.join([f"<li>{p[1]} - <a href='/edit/{p[0]}'>Edit</a> | <a href='/delete/{p[0]}'>Delete</a></li>" for p in posts])
        body = f"<h1>Dashboard</h1><a href='/edit/0'>New Post</a><ul>{items}</ul>"
        self.respond(render_template('Dashboard', body))

    def edit_post(self):
        post_id = int(self.path.split('/')[-1])
        title = ''
        content = ''
        if post_id != 0:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            row = c.execute('SELECT title, content FROM posts WHERE id=?', (post_id,)).fetchone()
            conn.close()
            if row:
                title, content = row
        body = f"""
<h1>{'New Post' if post_id==0 else 'Edit Post'}</h1>
<form method='post' action='/{'create' if post_id==0 else f'update/{post_id}'}'>
<input type='text' name='title' value='{title}' required><br>
<textarea name='content'>{content}</textarea><br>
<button type='submit'>Save</button>
</form>"""
        self.respond(render_template('Edit Post', body))

    def create_post(self):
        length = int(self.headers.get('Content-Length', 0))
        data = parse_qs(self.rfile.read(length).decode())
        title = data.get('title', [''])[0]
        content = data.get('content', [''])[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)', (title, content, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        self.redirect('/dashboard')

    def update_post(self):
        post_id = int(self.path.split('/')[-1])
        length = int(self.headers.get('Content-Length', 0))
        data = parse_qs(self.rfile.read(length).decode())
        title = data.get('title', [''])[0]
        content = data.get('content', [''])[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('UPDATE posts SET title=?, content=? WHERE id=?', (title, content, post_id))
        conn.commit()
        conn.close()
        self.redirect('/dashboard')

    def delete_post(self):
        post_id = int(self.path.split('/')[-1])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id=?', (post_id,))
        conn.commit()
        conn.close()
        self.redirect('/dashboard')

    def process_login(self):
        length = int(self.headers.get('Content-Length', 0))
        data = parse_qs(self.rfile.read(length).decode())
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        row = c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, hashed)).fetchone()
        conn.close()
        if row:
            sid = hashlib.sha256(f"{username}{SECRET_KEY}".encode()).hexdigest()
            sessions[sid] = username
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            cookie = Cookie.SimpleCookie()
            cookie['sid'] = sid
            self.send_header('Set-Cookie', cookie.output(header='', sep=''))
            self.end_headers()
        else:
            self.respond(render_template('Login Failed', '<p>Invalid credentials</p>'))

    def respond(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    with open('static/styles.css', 'w') as f:
        f.write('body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; } nav a { margin-right: 10px; }')
    server = HTTPServer(('0.0.0.0', 8000), Handler)
    print('Server started at http://0.0.0.0:8000')
    server.serve_forever()
