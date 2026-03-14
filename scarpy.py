from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openpyxl
import io
import spacy

app = Flask(__name__)
CORS(app)

# Charger modèle spaCy avec vecteurs (français ou anglais)
nlp = spacy.load("fr_core_news_md")  # Remplace par "en_core_web_md" si anglais

# Profils simulés avec compétences en liste
def fake_linkedin_profiles():
    return [
        {"nom": "Ahmed Gharbi", "poste": "Cloud Engineer", "entreprise": "AWS", "competences": ["AWS", "Terraform", "Linux"]},
        {"nom": "Sara Amara", "poste": "Data Scientist", "entreprise": "Google", "competences": ["Python", "sql", "Pandas"]},
        {"nom": "Yassine Kefi", "poste": "DevOps Cloud Architect", "entreprise": "AzureTech", "competences": ["Azure", "Docker", "CI/CD", "Jenkins"]},
        {"nom": "Nour Chatti", "poste": "Backend Developer", "entreprise": "Cloudify", "competences": ["Python", "Docker", "PostgreSQL"]},
        {"nom": "Rania Jlassi", "poste": "Cloud Consultant", "entreprise": "IBM", "competences": ["IBM Cloud", "Linux", "Bash"]},
        # Ajoute jusqu’à 20 profils ici si besoin
    ]

def calculer_score_spacy(profil, poste_cible, mots_cles, entreprise_cible):
    # Construire les textes à comparer
    texte_profil = f"{profil['poste']} {profil['entreprise']} {' '.join(profil['competences'])}"
    texte_requete = f"{poste_cible} {entreprise_cible} {' '.join(mots_cles)}"

    doc_profil = nlp(texte_profil.lower())
    doc_requete = nlp(texte_requete.lower())

    similarite = doc_profil.similarity(doc_requete)

    # Score de 0 à 100
    score = int(similarite * 100)
    return score

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    poste_cible = data.get("poste_cible", "")
    mots_cles = data.get("mots_cles", [])
    entreprise_cible = data.get("entreprise_cible", "")

    profils = fake_linkedin_profiles()
    profils_scores = []

    for p in profils:
        score = calculer_score_spacy(p, poste_cible, mots_cles, entreprise_cible)
        if score > 0:
            p_copy = p.copy()
            p_copy['score'] = score
            profils_scores.append(p_copy)

    # Trier par score décroissant, garder max 20
    profils_scores = sorted(profils_scores, key=lambda x: x['score'], reverse=True)[:20]

    return jsonify(profils_scores)

@app.route('/export', methods=['POST'])
def export_excel():
    data = request.json
    profils = data.get("profils", [])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Profils filtrés"

    ws.append(["Nom", "Poste", "Entreprise", "Compétences", "Score"])

    for p in profils:
        ws.append([
            p.get("nom", ""),
            p.get("poste", ""),
            p.get("entreprise", ""),
            ", ".join(p.get("competences", [])),
            p.get("score", "")
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
                     download_name="profils_scoring_spacy.xlsx",
                     as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
