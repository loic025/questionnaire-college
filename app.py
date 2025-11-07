import os
import json
from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 🔹 Charger les variables d’environnement Render
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_ID = os.getenv("SHEET_ID")
RESET_PASSWORD = os.getenv("RESET_PASSWORD", "enseignant2024")

# 🔹 Connexion à Google Sheets
def get_gsheet():
    if not GOOGLE_CREDS_JSON or not SHEET_ID:
        print("❌ Variables d’environnement manquantes")
        return None

    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1  # première feuille du document

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyse")
def analyse():
    return render_template("analyse.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Aucune donnée reçue"}), 400

    print(f"[SUBMIT] reçu {len(data)} champs")

    # 🔹 Connexion à la feuille
    sheet = get_gsheet()
    if not sheet:
        return jsonify({"status": "error", "message": "Google Sheets non configuré"}), 500

    try:
        # Vérifie si la première ligne (en-tête) existe déjà
        headers = sheet.row_values(1)
        if not headers:
            headers = ["nomEleve", "classe", "sexe", "annee"] + [f"q{i}" for i in range(1, 45)]
            sheet.append_row(headers)

        # Crée une nouvelle ligne à partir des données reçues
        row = [data.get("nomEleve", ""), data.get("classe", ""), data.get("sexe", ""), data.get("annee", "")]
        for i in range(1, 45):
            row.append(data.get(f"q{i}", ""))
        sheet.append_row(row)

        print("[SUBMIT] ligne ajoutée avec succès")
        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"[ERREUR Google Sheets] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/data")
def get_data():
    sheet = get_gsheet()
    if not sheet:
        return jsonify([])

    try:
        records = sheet.get_all_records()
        return jsonify(records)
    except Exception as e:
        print(f"[ERREUR get_data] {e}")
        return jsonify([])

@app.route("/reset", methods=["POST"])
def reset_data():
    data = request.get_json()
    if data.get("password") != RESET_PASSWORD:
        return jsonify({"status": "error", "message": "Mot de passe incorrect"})

    try:
        sheet = get_gsheet()
        if sheet:
            sheet.clear()
        return jsonify({"status": "ok", "message": "Toutes les données ont été effacées."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


