from flask import Flask, request, jsonify, send_from_directory
import csv, os

app = Flask(__name__)
DATA_FILE = 'donnees.csv'

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyse')
def analyse():
    return send_from_directory('.', 'analyse.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    return jsonify({'status': 'ok'})

@app.route('/data')
def data():
    if not os.path.exists(DATA_FILE):
        return jsonify([])
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
        return jsonify(list(csv.DictReader(f)))

if __name__ == '__main__':
    app.run(debug=True)

    from flask import send_from_directory

@app.route('/logo-education.png')
def logo():
    return send_from_directory('.', 'logo-education.png')

