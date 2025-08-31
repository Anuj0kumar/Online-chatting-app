from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import subprocess
import socket
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key
socketio = SocketIO(app, cors_allowed_origins="*")

# Function to check if port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Function to start server1.py in background
def start_server_background():
    if not is_port_in_use(8001):
        subprocess.Popen(['python', 'server1.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_server', methods=['GET', 'POST'])
def start_server():
    started = start_server_background()
    if started:
        return redirect('/login')
    else:
        # Check if server is running by trying to connect to port 8001
        if is_port_in_use(8001):
            return redirect('/login')
        return "Server is already running or failed to start."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect('/chat')
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/login')
    return render_template('chat.html', username=session['username'])

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        emit('message', f'{username} has joined the chat!', broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    message = data['message']
    username = session.get('username')
    if username:
        emit('message', f'{username}: {message}', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
