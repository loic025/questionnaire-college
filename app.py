from flask import Flask, request, jsonify, send_from_directory
import csv, os

app = Flask(__name__)
DATA_FILE = 'donnees.csv'

# --- Routes principales ---

@app.route('/')
def index():
    """Affiche le questionnaire."""
    return send_from_directory('.', 'index.html')

@app.route('/analyse')
def analyse():
    """Affiche la page d'analyse protégée."""
    return send_from_directory('.', 'analyse.html')


# --- Route pour recevoir les réponses ---
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    file_exists = os.path.exists(DATA_FILE)

    # ✅ Définit l'ordre exact des colonnes (y compris nomEleve)
    fieldnames = ["nomEleve", "classe", "sexe", "annee"] + [f"q{i}" for i in range(1, 35)]

    # ✅ Crée le fichier avec en-tête s’il n’existe pas encore
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    
    return jsonify({'status': 'ok'})


# --- Route pour lire les données (analyse) ---
@app.route('/data')
def data():
    if not os.path.exists(DATA_FILE):
        return jsonify([])
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
        return jsonify(list(csv.DictReader(f)))


# --- Route pour le logo (dans le dossier static) ---
@app.route('/static/<path:filename>')
def static_files(filename):
    """Permet d'afficher les images et fichiers statiques."""
    return send_from_directory('static', filename)


# --- Lancement du serveur ---
if __name__ == '__main__':
    app.run(debug=True)


