# theme.py - VERSION COMPLETE
import flet as ft

ROUGE_CANADA = "#D80621"
ROUGE_FONCE = "#A5001A"
OR_ERABLE = "#C9A227"
BLEU_GLACIER = "#1F5C8B"
VERT_FORET = "#1E6E4E"
BLANC = "#FFFFFF"
GRIS_CLAIR = "#F4F5F7"
GRIS_MOYEN = "#8A8F98"
GRIS_TEXTE = "#1F2937"
NOIR_DOUX = "#111318"
VERT_SUCCES = "#1E8E5A"
ORANGE_ALERTE = "#E08A00"

DEGRADE_HEADER = ft.LinearGradient(
    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
    colors=[ROUGE_CANADA, ROUGE_FONCE, "#7A0015"],
)
DEGRADE_ACCENT = ft.LinearGradient(
    begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
    colors=[OR_ERABLE, "#E0BE55"],
)

# Vrais drapeaux (CDN public flagcdn.com - images reelles, pas de dessin SVG)
DRAPEAU_CANADA_URL = "https://flagcdn.com/w160/ca.png"
DRAPEAU_CAMEROUN_URL = "https://flagcdn.com/w160/cm.png"

POLICE_TEXTE = "Segoe UI"

ENTREPRISE = {
    "nom": "HI CONSULTING IMMIGRATION",
    "slogan": "Visitez. Travaillez. Etudiez.",
    "logo": "logo_HICI.jpg",
    "adresse": "Logpom Carrefour Bassong, face immeuble Mont Baloua, 2e etage, Douala",
    "telephones": ["+237 678 924 045", "+237 691 871 842", "+237 658 937 466"],
    "email": "hiciofficiel@gmail.com",
    "facebook": "https://www.facebook.com/share/19HhsYJj7C/?mibextid=wwXIfr",
    "tiktok": "https://www.tiktok.com/@hiconsultingimmigration",
    "mission": "Vous accompagner avec transparence et expertise a chaque etape de votre projet d'immigration.",
}

# ============================================================
# CORRECTION : URL de l'API pour Vercel
# ============================================================

# frontend/theme.py
import os
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000')  # URL du backend


def construire_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(primary=ROUGE_CANADA, on_primary=BLANC, secondary=BLEU_GLACIER, surface=BLANC),
        font_family=POLICE_TEXTE,
    )
