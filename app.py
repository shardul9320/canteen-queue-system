from flask import Flask, render_template, request, redirect, url_for
import json, time
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# Initialize or load token data
if not os.path.exists(DATA_FILE):
    data = {'tokens': [], 'avg_time': 30}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
else:
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_token', methods=['POST'])
def generate_token():
    token_number = len(data['tokens']) + 1
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    data['tokens'].append({
        'token': token_number,
        'timestamp': timestamp,
        'status': 'waiting'
    })
    save_data()
    return redirect(url_for('queue_status', token=token_number))

@app.route('/queue/<int:token>')
def queue_status(token):
    avg_time = data['avg_time']
    waiting = [t for t in data['tokens'] if t['status'] == 'waiting']
    token_info = next((t for t in data['tokens'] if t['token'] == token), None)
    position = waiting.index(token_info) + 1 if token_info in waiting else -1
    estimated_wait = position * avg_time if position > 0 else 0
    return render_template('queue.html', token=token, position=position,
                           estimated_wait=estimated_wait, total=len(waiting))

@app.route('/admin')
def admin_panel():
    return render_template('admin.html', tokens=data['tokens'])

if __name__ == '__main__':
    print("🚀 Starting Flask App...")
    app.run(debug=True)
