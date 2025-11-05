from flask import Flask, request, jsonify, send_from_directory
import csv, os

app = Flask(__name__, static_folder='static')

DATA_FILE = 'donnees.csv'
# Tu peux aussi définir ce mot de passe dans Render (Environment Variables) sous RESET_PASSWORD
RESET_PASSWORD = os.environ.get('RESET_PASSWORD', 'enseignant2024')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/analyse')
def analyse():
    return send_from_directory('.', 'analyse.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json() or {}

    # Schéma de colonnes stable (ajout du nom/prénom facultatif)
    fieldnames = ['nomEleve', 'classe', 'sexe', 'annee'] + [f"q{i}" for i in range(1, 35)]

    file_exists = os.path.exists(DATA_FILE)

    # Normalise la ligne aux colonnes prévues (valeurs manquantes -> '')
    row = {k: data.get(k, '') for k in fieldnames}

    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    return jsonify({'status': 'ok'})


@app.route('/data')
def data():
    if not os.path.exists(DATA_FILE):
        return jsonify([])
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return jsonify(list(reader))


@app.route('/reset', methods=['POST'])
def reset():
    payload = request.get_json() or {}
    pwd = payload.get('password', '')
    if pwd != RESET_PASSWORD:
        return jsonify({'status': 'error', 'message': 'Mot de passe incorrect.'}), 403

    # Réinitialise le fichier (on supprime pour repartir propre, l’en-tête sera réécrit au prochain submit)
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    return jsonify({'status': 'ok', 'message': 'Fichier réinitialisé.'})


# Route statique pour le logo etc.
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    # Utile en local uniquement. Sur Render, c'est gunicorn qui lance l'app.
    app.run(host='0.0.0.0', port=5000)
