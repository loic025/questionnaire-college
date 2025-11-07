import os
import json
from flask import Flask, request, jsonify, send_from_directory
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
    return send_from_directory('.', 'index.html')

@app.route("/analyse")
def analyse():
    return send_from_directory('.', 'analyse.html')

@app.route("/submit", methods=["POST"])
def submit():
    from google.oauth2.service_account import Credentials
    import json
    import os
    import gspread

    data = request.get_json() or {}
    print(f"[SUBMIT] reçu {len(data)} champs")

    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    sheet_id = os.environ.get("SHEET_ID")

    if not creds_json or not sheet_id:
        return jsonify({"status": "error", "message": "Configuration Google Sheets manquante."}), 500

    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1  # première feuille

    try:
        # 🔹 Si le header n’existe pas, on le crée une fois
        existing_headers = worksheet.row_values(1)
        if not existing_headers:
            headers = ["nomEleve", "classe", "sexe", "annee"] + [f"q{i}" for i in range(1, 45)]
            worksheet.append_row(headers)

        # 🔹 Ajoute la réponse unique
        row = [data.get("nomEleve", ""), data.get("classe", ""), data.get("sexe", ""), data.get("annee", "")]
        for i in range(1, 45):
            row.append(data.get(f"q{i}", ""))

        worksheet.append_row(row, value_input_option="USER_ENTERED")
        print("[SUBMIT] ✅ ligne ajoutée dans Google Sheets")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"[SUBMIT][ERREUR] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/data")
def get_data():
    from google.oauth2.service_account import Credentials
    import json
    import os
    import gspread

    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    sheet_id = os.environ.get("SHEET_ID")

    if not creds_json or not sheet_id:
        return jsonify([])

    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=[
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ])
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1

    try:
        records = worksheet.get_all_records()
        print(f"[DATA] ✅ {len(records)} lignes lues depuis Google Sheets")
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


