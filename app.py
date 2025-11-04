from flask import Flask, request, jsonify, send_from_directory
import csv, os

app = Flask(__name__)
DATA_FILE = 'donnees.csv'
RESET_PASSWORD = "enseignant2024"  # mot de passe enseignant pour réinitialisation

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
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    
    return jsonify({'status': 'ok'})


# --- Route pour lire les données (analyse) ---
@app.route('/data')
def data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return jsonify([])
try:
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return jsonify(data)
    except Exception as e:
        print("Erreur lecture CSV :", e)
        return jsonify([]), 500

# 🧹 Route protégée pour réinitialiser le fichier CSV
@app.route('/reset', methods=['POST'])
def reset_data():
    req = request.get_json()
    pwd = req.get("password", "")
    if pwd != RESET_PASSWORD:
        return jsonify({"status": "error", "message": "Mot de passe incorrect."}), 403
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        fieldnames = ['nomEleve', 'classe', 'sexe', 'annee'] + [f'q{i}' for i in range(1, 35)]
        writer.writerow(fieldnames)
    return jsonify({"status": "ok", "message": "Toutes les données ont été effacées."})
    
# --- Route pour le logo (dans le dossier static) ---
@app.route('/static/<path:filename>')
def static_files(filename):
    """Permet d'afficher les images et fichiers statiques."""
    return send_from_directory('static', filename)


# --- Lancement du serveur ---
if __name__ == '__main__':
    app.run(debug=True)


