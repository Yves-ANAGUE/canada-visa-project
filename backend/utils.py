# utils.py
# Boite a outils centralisee : dictionnaires bilingues,
# feature engineering, prediction, securite des mots de passe.
# Ce fichier est importe par train.py ET par le backend FastAPI.


import hashlib
import os
import numpy as np
import pandas as pd
import copy
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage


from decimal import Decimal

def nettoyer_decimals(d: dict) -> dict:
    """Convertit tous les decimal.Decimal (issus de PostgreSQL NUMERIC)
    en float natif Python, pour eviter les erreurs de calcul."""
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in d.items()}

# 1. DICTIONNAIRES DE REFERENCE (feature engineering) Identiques a ceux valides dans le Notebook 

FUNDS_BY_YEAR = {
    2015: 11851, 2016: 12164, 2017: 12300, 2018: 12475,
    2019: 12669, 2020: 12960, 2021: 13213, 2022: 13310,
    2023: 13757, 2024: 14690, 2025: 15263, 2026: 15263
}

EXTRA_FUNDS_PER_DEPENDANT = {0: 0, 1: 3200, 2: 4000, 3: 5000, 4: 6500}

FRANCOPHONE_COUNTRIES = [
    'France', 'Morocco', 'Algeria', 'Tunisia', 'Senegal',
    'Cameroon', 'Lebanon', 'Haiti',
    'Ivory Coast', 'Democratic Republic of Congo'
]

COLONNES_BRUTES_ATTENDUES = [
    'application_year', 'age', 'sex', 'marital_status', 'country_of_origin',
    'education_level', 'eca_obtained', 'english_test',
    'clb_speaking_english', 'clb_listening_english', 'clb_reading_english', 'clb_writing_english',
    'french_test', 'nclc_speaking_french', 'nclc_listening_french',
    'nclc_reading_french', 'nclc_writing_french',
    'years_foreign_experience', 'years_canadian_experience', 'sector', 'teer_category',
    'job_offer_canada', 'job_offer_teer', 'provincial_nomination', 'studied_in_canada',
    'family_in_canada', 'funds_available_cad', 'dependants', 'medical_exam_ok',
    'criminal_record', 'inadmissibility', 'program'
]


# 2. DICTIONNAIRES BILINGUES POUR LES MENUS DEROULANTS FLET
#    Cle = valeur technique stockee en base / envoyee au modele
#    Valeur = libelle affiche a l'agent dans l'interface

LIBELLES_SEXE = {
    'Male': 'Homme (Male)',
    'Female': 'Femme (Female)'
}

LIBELLES_STATUT_MATRIMONIAL = {
    'Single': 'Célibataire (Single)',
    'Married': 'Marié(e) (Married)',
    'Divorced': 'Divorcé(e) (Divorced)',
    'Widowed': 'Veuf/Veuve (Widowed)',
    'Common-Law': 'Union de fait (Common-Law)'
}

LIBELLES_EDUCATION = {
    'Less than secondary': 'Inférieur au secondaire (Less than secondary)',
    'Secondary diploma': 'Diplôme secondaire (Secondary diploma)',
    'One-year post-secondary': 'Post-secondaire 1 an (One-year post-secondary)',
    'Two-year post-secondary': 'Post-secondaire 2 ans (Two-year post-secondary)',
    'Bachelor degree': 'Licence (Bachelor degree)',
    'Master degree': 'Master (Master degree)',
    'PhD': 'Doctorat (PhD)'
}

LIBELLES_OUI_NON = {
    'Yes': 'Oui (Yes)',
    'No': 'Non (No)'
}

LIBELLES_TEST_ANGLAIS = {
    'IELTS': 'IELTS',
    'CELPIP': 'CELPIP',
    'PTE': 'PTE',
    'None': 'Aucun test (None)'
}

LIBELLES_TEST_FRANCAIS = {
    'TEF Canada': 'TEF Canada',
    'TCF Canada': 'TCF Canada',
    'None': 'Aucun test (None)'
}

LIBELLES_SECTEUR = {
    'STEM': 'Sciences, technologies, ingénierie, maths (STEM)',
    'Healthcare': 'Santé (Healthcare)',
    'Transport': 'Transport (Transport)',
    'Trades': 'Métiers spécialisés (Trades)',
    'Education': 'Éducation (Education)',
    'Business': 'Affaires (Business)',
    'Agriculture': 'Agriculture (Agriculture)',
    'Other': 'Autre (Other)'
}

LIBELLES_TEER = {
    'TEER 0': 'TEER 0 - Gestion',
    'TEER 1': 'TEER 1 - Formation universitaire',
    'TEER 2': 'TEER 2 - Formation collégiale/apprentissage (2+ ans)',
    'TEER 3': 'TEER 3 - Formation collégiale/apprentissage (<2 ans)',
    'TEER 4': 'TEER 4 - Diplôme secondaire',
    'TEER 5': 'TEER 5 - Aucune formation formelle',
    'None': 'Sans objet (None)'
}

LIBELLES_CASIER = {
    'None': 'Aucun antécédent (None)',
    'Minor': 'Antécédent mineur (Minor)',
    'Major': 'Antécédent majeur (Major)'
}

LIBELLES_PROGRAMME = {
    'FSWP': 'Travailleurs qualifiés fédéral (FSWP)',
    'FSTP': 'Métiers spécialisés fédéral (FSTP)',
    'CEC': "Catégorie de l'expérience canadienne (CEC)",
    'PNP': 'Programme des candidats des provinces (PNP)'
}

LIBELLES_PHASE_TRAITEMENT = {
    'File Opened': 'Dossier ouvert (File Opened)',
    'Awaiting Language Test': 'En attente de test de langue (Awaiting Language Test)',
    'Submitted in Pool': 'Soumis dans le bassin (Submitted in Pool)',
    'Biometrics Requested': 'Convocation biométrique (Biometrics Requested)',
    'Closed': 'Clôturé (Closed)'
}

LIBELLES_DECISION = {
    'Accepted': 'Accepté (Accepted)',
    'Refused': 'Refusé (Refused)'
}



# 3. SECURITE - HACHAGE DES MOTS DE PASSE 

def hacher_mot_de_passe(mot_de_passe_clair: str) -> str:
    """Hache un mot de passe en SHA-256 (64 caracteres hexadecimaux)."""
    return hashlib.sha256(mot_de_passe_clair.encode('utf-8')).hexdigest()


def verifier_mot_de_passe(mot_de_passe_clair: str, hache_stocke: str) -> bool:
    """Compare un mot de passe saisi au hash stocke en base."""
    return hacher_mot_de_passe(mot_de_passe_clair) == hache_stocke




# REMPLACE entierement construire_profil_features() dans utils.py

import numpy as np

def construire_profil_features(profil_brut: dict) -> pd.DataFrame:
    """
    Prend un dictionnaire de 32 criteres bruts (saisis par l'agent
    dans les 5 onglets Flet ou lus depuis PostgreSQL) et retourne
    une ligne DataFrame enrichie des variables derivees necessaires
    au modele entraine.
    """
    manquantes = set(COLONNES_BRUTES_ATTENDUES) - set(profil_brut.keys())
    if manquantes:
        raise ValueError(f"Champs manquants dans le profil : {manquantes}")

    p = nettoyer_decimals(profil_brut.copy())

    # ---- CLB English ----
    clb_vals = [
        p['clb_speaking_english'],
        p['clb_listening_english'],
        p['clb_reading_english'],
        p['clb_writing_english']
    ]
    clb_ok = [v for v in clb_vals if v is not None]
    p['clb_english_min'] = min(clb_ok) if clb_ok else np.nan
    p['clb_english_mean'] = float(np.mean(clb_ok)) if clb_ok else np.nan

    # ---- NCLC French ----
    nclc_vals = [
        p['nclc_speaking_french'],
        p['nclc_listening_french'],
        p['nclc_reading_french'],
        p['nclc_writing_french']
    ]
    nclc_ok = [v for v in nclc_vals if v is not None]
    p['nclc_french_min'] = min(nclc_ok) if nclc_ok else np.nan
    p['nclc_french_mean'] = float(np.mean(nclc_ok)) if nclc_ok else np.nan

    # ---- Ratio des fonds ----
    if p.get('funds_available_cad') is not None and p.get('application_year') is not None:
        fonds_min = (
            FUNDS_BY_YEAR.get(p['application_year'], 15263) +
            EXTRA_FUNDS_PER_DEPENDANT.get(p.get('dependants') or 0, 6500)
        )
        p['ratio_fonds'] = float(p['funds_available_cad']) / fonds_min
    else:
        p['ratio_fonds'] = np.nan

    # ---- Pays francophone ----
    p['is_francophone_country'] = (
        int(p['country_of_origin'] in FRANCOPHONE_COUNTRIES)
        if p.get('country_of_origin') else np.nan
    )

    # ---- Experience totale ----
    if p.get('years_foreign_experience') is not None and p.get('years_canadian_experience') is not None:
        p['experience_totale'] = p['years_foreign_experience'] + p['years_canadian_experience']
    else:
        p['experience_totale'] = np.nan

    return pd.DataFrame([p])


def predire_client(profil_brut: dict, modele, seuil: float = 0.5) -> dict:
    """
    Pipeline complet de prediction : profil brut -> feature
    engineering -> preprocessing (integre au pipeline sklearn)
    -> prediction -> decision finale avec niveau de confiance.
    """
    X_client = construire_profil_features(profil_brut)
    proba_accepted = modele.predict_proba(X_client)[0, 1]
    decision = 'Accepted' if proba_accepted >= seuil else 'Refused'
    
    ecart = abs(proba_accepted - seuil)
    if ecart > 0.25:
        confiance = 'Elevee'
    elif ecart > 0.10:
        confiance = 'Moyenne'
    else:
        confiance = 'Faible (dossier limite)'

    nb_champs_manquants = sum(1 for c in COLONNES_BRUTES_ATTENDUES if profil_brut.get(c) is None)

    return {
        'decision_predite': decision,
        'probabilite_acceptation': round(float(proba_accepted), 4),
        'seuil_utilise': seuil,
        'niveau_confiance': confiance,
        'estime': nb_champs_manquants > 0,
        'nb_champs_manquants': nb_champs_manquants
    }


# CORRECTION dans utils.py - remplace generer_id_client existant

from sqlalchemy import text

def generer_id_client_atomique(engine, annee: int) -> str:
    """
    Genere un id_client unique de maniere atomique via un compteur
    dedie (table compteurs_id), immunise contre :
    - les modifications ulterieures du champ application_year
    - les suppressions/archivages de dossiers
    - les requetes concurrentes (INSERT ... ON CONFLICT est atomique
      au niveau de PostgreSQL, contrairement a un simple COUNT)
    """
    with engine.begin() as conn:   # transaction atomique
        resultat = conn.execute(text("""
            INSERT INTO compteurs_id (annee, dernier_numero)
            VALUES (:annee, 1)
            ON CONFLICT (annee)
            DO UPDATE SET dernier_numero = compteurs_id.dernier_numero + 1
            RETURNING dernier_numero
        """), {"annee": annee}).scalar()

    return f"CAN-{annee}-{resultat:03d}"


def calculer_age(date_naissance) -> int:
    """Calcule l'age exact a partir de la date de naissance (section 5.1)."""
    from datetime import date
    if isinstance(date_naissance, str):
        date_naissance = pd.to_datetime(date_naissance).date()
    today = date.today()
    return today.year - date_naissance.year - (
        (today.month, today.day) < (date_naissance.month, date_naissance.day)
    )


def profil_complet_pour_prediction(profil_dict: dict) -> bool:
    """Verifie que tous les champs necessaires au modele sont renseignes
    (permet de savoir si on peut deja calculer une prediction ou non)."""
    return all(profil_dict.get(col) is not None for col in COLONNES_BRUTES_ATTENDUES)




# REMPLACE entierement simuler_optimisation() dans utils.py
# (tolerant aux valeurs manquantes, ne plante plus)

import copy

def simuler_optimisation(profil_brut: dict, modele, seuil: float = 0.5) -> dict:
    """
    Teste des ameliorations plausibles du dossier (leviers d'action)
    et mesure l'impact de chacune sur la probabilite d'acceptation.
    Aucun reentrainement : uniquement des appels d'inference sur le
    modele deja valide et fige.
    """
    profil_brut = nettoyer_decimals(profil_brut)
    baseline = predire_client(profil_brut, modele, seuil)
    leviers = []

    # ---- CLB English ----
    clb_vals = [
        profil_brut.get('clb_speaking_english'),
        profil_brut.get('clb_listening_english'),
        profil_brut.get('clb_reading_english'),
        profil_brut.get('clb_writing_english')
    ]
    clb_ok = [v for v in clb_vals if v is not None]
    if not clb_ok or min(clb_ok) < 9:
        p = copy.deepcopy(profil_brut)
        for cle in ['clb_speaking_english', 'clb_listening_english', 'clb_reading_english', 'clb_writing_english']:
            p[cle] = 9
        leviers.append(("Ameliorer l'anglais a CLB 9 (les 4 competences)", p))

    # ---- NCLC French ----
    nclc_vals = [
        profil_brut.get('nclc_speaking_french'),
        profil_brut.get('nclc_listening_french'),
        profil_brut.get('nclc_reading_french'),
        profil_brut.get('nclc_writing_french')
    ]
    nclc_ok = [v for v in nclc_vals if v is not None]
    if not nclc_ok or min(nclc_ok) < 9:
        p = copy.deepcopy(profil_brut)
        for cle in ['nclc_speaking_french', 'nclc_listening_french', 'nclc_reading_french', 'nclc_writing_french']:
            p[cle] = 9
        p['french_test'] = 'TEF Canada' if p.get('french_test') in (None, 'None') else p['french_test']
        leviers.append(("Obtenir NCLC 9 en francais (les 4 competences)", p))

    # ---- Provincial Nomination (PNP) ----
    if profil_brut.get('provincial_nomination') != 'Yes':
        p = copy.deepcopy(profil_brut)
        p['provincial_nomination'] = 'Yes'
        leviers.append(("Obtenir une nomination provinciale (PNP)", p))

    # ---- ECA (Educational Credential Assessment) ----
    if profil_brut.get('eca_obtained') != 'Yes':
        p = copy.deepcopy(profil_brut)
        p['eca_obtained'] = 'Yes'
        leviers.append(("Faire evaluer son diplome (ECA)", p))

    # ---- Funds available ----
    if profil_brut.get('funds_available_cad') is not None:
        p = copy.deepcopy(profil_brut)
        p['funds_available_cad'] = round(float(profil_brut['funds_available_cad']) * 1.5, 2)
        leviers.append(("Augmenter les fonds disponibles de 50%", p))

    # ---- Foreign experience ----
    if profil_brut.get('years_foreign_experience') is not None:
        p = copy.deepcopy(profil_brut)
        p['years_foreign_experience'] = profil_brut['years_foreign_experience'] + 1
        leviers.append(("Acquerir 1 an d'experience professionnelle supplementaire", p))

    # ---- Job offer ----
    if profil_brut.get('job_offer_canada') != 'Yes':
        p = copy.deepcopy(profil_brut)
        p['job_offer_canada'] = 'Yes'
        p['job_offer_teer'] = profil_brut.get('teer_category') or 'TEER 2'
        leviers.append(("Obtenir une offre d'emploi valide au Canada", p))

    # ---- Calcul des scenarios ----
    scenarios = []
    for libelle, profil_modifie in leviers:
        resultat = predire_client(profil_modifie, modele, seuil)
        scenarios.append({
            "levier": libelle,
            "probabilite_apres": resultat['probabilite_acceptation'],
            "gain_absolu": round(resultat['probabilite_acceptation'] - baseline['probabilite_acceptation'], 4),
            "nouvelle_decision": resultat['decision_predite']
        })

    scenarios.sort(key=lambda x: x['gain_absolu'], reverse=True)
    
    return {
        "situation_actuelle": baseline,
        "scenarios_ameliorations": scenarios
    }



# A ajouter dans utils.py

from fpdf import FPDF
from io import BytesIO
import smtplib
from email.message import EmailMessage


# REMPLACE _construire_rapport ET generer_pdf_diagnostic
# dans utils.py / main_api.py

# Dans utils.py, remplacez generer_pdf_diagnostic :

def dessiner_drapeau_canada(pdf, x, y, largeur=30, hauteur=18):
    bande = largeur / 3
    pdf.set_fill_color(216, 6, 33)
    pdf.rect(x, y, bande, hauteur, style='F')
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(x + bande, y, bande, hauteur, style='F')
    pdf.set_fill_color(216, 6, 33)
    pdf.rect(x + 2 * bande, y, bande, hauteur, style='F')
    # feuille simplifiee (triangle rouge au centre)
    cx = x + largeur / 2
    pdf.set_fill_color(216, 6, 33)
    pdf.triangle = None  # fpdf2 n'a pas de triangle direct pre-v2.7, on utilise un losange via polygon
    pdf.polygon([(cx, y+3), (cx-4, y+hauteur-3), (cx+4, y+hauteur-3)], style='F') if hasattr(pdf, 'polygon') else None



# REMPLACE entierement generer_pdf_diagnostic dans backend/utils.py

import requests
from io import BytesIO

def _telecharger_image(url: str) -> BytesIO:
    reponse = requests.get(url, timeout=5)
    reponse.raise_for_status()
    return BytesIO(reponse.content)



# CORRECTION dans utils.py - generer_pdf_diagnostic() accepte
# maintenant les vraies metriques en parametre

def generer_pdf_diagnostic(dossier: dict, resultat_prediction: dict, diagnostic_texte: str,
                            scenarios: list = None, metriques: dict = None,
                            chemin_logo: str = '../frontend/assets/logo_HICI.jpg') -> bytes:
    """
    Génère un rapport PDF complet avec les métriques du modèle.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # ---- En-tete ----
    try:
        pdf.image(chemin_logo, x=15, y=12, w=28)
    except Exception:
        pass

    try:
        pdf.image(_telecharger_image("https://flagcdn.com/w80/ca.png"), x=170, y=12, w=13)
        pdf.image(_telecharger_image("https://flagcdn.com/w80/cm.png"), x=185, y=12, w=13)
    except Exception:
        pass

    pdf.set_xy(48, 14)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.cell(0, 7, 'HI CONSULTING IMMIGRATION', ln=True)
    pdf.set_x(48)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, "Rapport d'evaluation - Entree Express Canada", ln=True)

    pdf.set_y(42)
    pdf.set_draw_color(216, 6, 33)
    pdf.set_line_width(0.6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)

    # ---- Informations du dossier ----
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, f"Dossier : {dossier.get('nom') or 'Non renseigne'} {dossier.get('prenom') or ''}", ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"Programme vise : {dossier.get('program') or '-'}", ln=True)
    pdf.cell(0, 6, f"Pays d'origine : {dossier.get('country_of_origin') or '-'}", ln=True)

    # ---- Résultat de l'analyse predictive ----
    pdf.ln(6)
    pdf.set_fill_color(244, 245, 247)
    pdf.rect(15, pdf.get_y(), 180, 34, style='F')
    pdf.set_xy(20, pdf.get_y() + 4)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 7, "Resultat de l'analyse predictive", ln=True)
    pdf.set_x(20)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"Decision predite : {resultat_prediction.get('decision_predite', '-')}", ln=True)
    pdf.set_x(20)
    proba = resultat_prediction.get('probabilite_acceptation', 0) or 0
    pdf.cell(0, 6, f"Probabilite d'acceptation : {proba*100:.1f}%   |   "
                    f"Confiance : {resultat_prediction.get('niveau_confiance', '-')}", ln=True)
    pdf.set_x(20)

    # ---- Métriques ----
    if metriques and metriques.get('accuracy') is not None:
        date_exec = str(metriques.get('date_execution', ''))[:10]
        pdf.cell(0, 6, f"Metriques du modele (entrainement du {date_exec}) : "
                        f"Accuracy {float(metriques['accuracy'])*100:.1f}% - "
                        f"Precision {float(metriques['precision_score'])*100:.1f}% - "
                        f"Recall {float(metriques['recall_score'])*100:.1f}% - "
                        f"Specificity {float(metriques.get('specificity_score') or 0)*100:.1f}% - "
                        f"F1 {float(metriques['f1_score'])*100:.1f}% - "
                        f"ROC-AUC {float(metriques['roc_auc']):.4f}", ln=True)
    else:
        pdf.cell(0, 6, "Metriques du modele : Precision 75.6% - Recall 67.5% - Specificity 95.9% - "
                        "F1-Score 71.3% - ROC-AUC 0.9524", ln=True)

    # ---- Diagnostic IA ----
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Diagnostic et recommandations (Data Analyst IA)', ln=True)
    pdf.ln(1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 6, diagnostic_texte or "Diagnostic non disponible.")

    # ---- Simulateur d'optimisation ----
    if scenarios:
        pdf.ln(6)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, "Simulateur d'optimisation prescriptive", ln=True)
        pdf.ln(1)
        
        
        # SOLUTION : Utiliser un tableau simple au lieu de multi_cell
        
        pdf.set_font('Helvetica', '', 8)
        
        # En-tête du tableau
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(90, 6, "Levier d'optimisation", border=1, ln=0, align='L', fill=True)
        pdf.cell(40, 6, "Nouvelle proba", border=1, ln=0, align='C', fill=True)
        pdf.cell(30, 6, "Gain", border=1, ln=0, align='C', fill=True)
        pdf.cell(30, 6, "Decision", border=1, ln=1, align='C', fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        for s in scenarios[:6]:
            gain = s['gain_absolu'] * 100
            levier = s['levier']
            # Troncature agressive
            if len(levier) > 25:
                levier = levier[:22] + "..."
            
            pdf.cell(90, 5, levier, border=1, ln=0, align='L')
            pdf.cell(40, 5, f"{s['probabilite_apres']*100:.1f}%", border=1, ln=0, align='C')
            pdf.cell(30, 5, f"{'+' if gain>=0 else ''}{gain:.1f} pts", border=1, ln=0, align='C')
            pdf.cell(30, 5, s['nouvelle_decision'], border=1, ln=1, align='C')

    # ---- Pied de page ----
    pdf.set_y(-22)
    pdf.set_draw_color(216, 6, 33)
    pdf.line(15, pdf.get_y() - 3, 195, pdf.get_y() - 3)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5, 'HI Consulting Immigration - Logpom Carrefour Bassong, Douala - +237 678 924 045', align='C')

    return bytes(pdf.output())





# CORRECTION dans utils.py - envoyer_email_pdf()

def envoyer_email_pdf(destinataire: str, sujet: str, corps: str, pdf_bytes: bytes, nom_fichier: str):
    expediteur = os.environ['GMAIL_ADDRESS']
    mot_de_passe_app = os.environ['GMAIL_APP_PASSWORD']

    message = EmailMessage()
    message['Subject'] = sujet
    message['From'] = f"HI Consulting Immigration <{expediteur}>"   # <-- nom affiche par Gmail
    message['To'] = destinataire
    message.set_content(corps)
    message.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=nom_fichier)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as serveur:
        serveur.login(expediteur, mot_de_passe_app)
        serveur.send_message(message)



# A ajouter dans utils.py - detection de completude du profil

def profil_complet_pour_prediction(profil_dict: dict) -> bool:
    """Verifie que tous les champs necessaires au modele sont renseignes
    (permet de savoir si on peut deja calculer une prediction ou non)."""
    return all(profil_dict.get(col) is not None for col in COLONNES_BRUTES_ATTENDUES)

# utils.py - Ajouter à la fin

def generer_diagnostic_openrouter(profil_brut: dict, resultat_prediction: dict,
                                   top_facteurs_globaux: pd.DataFrame = None) -> str:
    import os
    import requests
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "openrouter/free"

    top5 = top_facteurs_globaux.head(5)['Variable_origine'].tolist() if top_facteurs_globaux is not None else ['experience_totale', 'ratio_fonds', 'eca_obtained', 'provincial_nomination', 'clb_english_min']

    # ---- Construction des informations supplémentaires (comme avant) ----
    champs_manquants = []
    for champ in COLONNES_BRUTES_ATTENDUES:
        valeur = profil_brut.get(champ)
        if valeur is None or (isinstance(valeur, float) and np.isnan(valeur)):
            champs_manquants.append(champ)

    note_estimation = ""
    if champs_manquants:
        note_estimation = f"""
⚠️ ATTENTION : Ce dossier est incomplet ({len(champs_manquants)} champs manquants).
Champs manquants : {', '.join(champs_manquants[:10])}{'...' if len(champs_manquants) > 10 else ''}
La prédiction est basée sur des valeurs estimées par le modèle.
Complétez ces champs pour une évaluation plus fiable.
"""
    elif resultat_prediction.get('estime', False):
        note_estimation = """
ℹ️ Note : Certaines valeurs ont été estimées par le modèle car le dossier n'est pas complètement rempli.
"""

    note_simulateur = """
📊 Note sur le simulateur : Les gains indiqués sont des estimations individuelles,
une modification à la fois, en partant du profil actuel. L'effet combiné de
plusieurs modifications peut être différent (interactions non-linéaires).
"""

    # ---- Construction du prompt ----
    prompt = f"""Tu es un analyste expert en immigration canadienne (Entree Express).
Voici un dossier client evalue par un modele de Machine Learning (GradientBoosting).

{note_estimation}

{note_simulateur}

PROFIL DU CANDIDAT :
- Age : {profil_brut.get('age', 'inconnu')} ans, {profil_brut.get('marital_status', 'inconnu')}
- Pays d'origine : {profil_brut.get('country_of_origin', 'inconnu')}
- Niveau d'etudes : {profil_brut.get('education_level', 'inconnu')} (ECA : {profil_brut.get('eca_obtained', 'inconnu')})
- Programme vise : {profil_brut.get('program', 'inconnu')}
- CLB anglais (min) : {min(profil_brut.get('clb_speaking_english', 0), profil_brut.get('clb_listening_english', 0), profil_brut.get('clb_reading_english', 0), profil_brut.get('clb_writing_english', 0))}
- Experience etrangere : {profil_brut.get('years_foreign_experience', 0)} ans
- Experience canadienne : {profil_brut.get('years_canadian_experience', 0)} ans
- Fonds disponibles : {profil_brut.get('funds_available_cad', 'non renseigne')} CAD
- PNP : {profil_brut.get('provincial_nomination', 'inconnu')}
- Offre d'emploi : {profil_brut.get('job_offer_canada', 'inconnu')}

RESULTAT DU MODELE :
- Decision predite : {resultat_prediction['decision_predite']}
- Probabilite : {resultat_prediction['probabilite_acceptation']*100:.1f}%
- Confiance : {resultat_prediction['niveau_confiance']}

VARIABLES LES PLUS INFLUENTES : {', '.join(top5)}

Redige un diagnostic court (100-150 mots) en francais, professionnel et bienveillant,
qui explique les facteurs cles et donne 1-2 recommandations concretes.
Ne repete pas les chiffres bruts, interprete-les.
Si le dossier est incomplet, mentionne-le et conseille de completer les champs manquants.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hici-canada-visa-api.onrender.com",
        "X-Title": "HI Consulting Immigration"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 400
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Erreur OpenRouter : {e}")