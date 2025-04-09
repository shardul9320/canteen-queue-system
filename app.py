from flask import Flask, render_template, request, redirect, url_for
import json, time, os
from datetime import datetime, timedelta

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

def remove_expired_tokens():
    current_time = datetime.now()
    updated_tokens = []
    for t in data['tokens']:
        if t['status'] != 'waiting':
            continue
        try:
            # Convert timestamp to datetime object
            if isinstance(t['timestamp'], float) or isinstance(t['timestamp'], int):
                token_time = datetime.fromtimestamp(t['timestamp'])
            elif isinstance(t['timestamp'], str):
                token_time = datetime.strptime(t['timestamp'], '%Y-%m-%d %H:%M:%S')
            else:
                continue  # Skip unknown formats

            # Only keep tokens that haven't expired
            if token_time + timedelta(minutes=5) > current_time:
                updated_tokens.append(t)

        except Exception as e:
            print(f"Error parsing timestamp: {t['timestamp']} → {e}")
            continue

    data['tokens'] = updated_tokens
    save_data()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_token', methods=['POST'])
def generate_token():
    remove_expired_tokens()
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
    remove_expired_tokens()
    avg_time = data['avg_time']
    waiting = [t for t in data['tokens'] if t['status'] == 'waiting']
    token_info = next((t for t in data['tokens'] if t['token'] == token), None)
    position = waiting.index(token_info) + 1 if token_info in waiting else -1
    estimated_wait = position * avg_time if position > 0 else 0
    return render_template('queue.html', token=token, position=position,
                           estimated_wait=estimated_wait, total=len(waiting))

@app.route('/admin')
def admin_panel():
    remove_expired_tokens()
    return render_template('admin.html', tokens=data['tokens'])

@app.route('/remove_token/<int:token_id>', methods=['POST'])
def remove_token(token_id):
    data['tokens'] = [t for t in data['tokens'] if t['token'] != token_id]
    save_data()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    print("🚀 Starting Flask App...")
    app.run(debug=True)
