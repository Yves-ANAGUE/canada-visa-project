# main_api.py
from fastapi import BackgroundTasks

import os
import sys
import json
import logging
from datetime import date, datetime
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Optional

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from fastapi import Request
import requests as requests_lib

from backend.utils import (
    predire_client, hacher_mot_de_passe, verifier_mot_de_passe,
    generer_id_client_atomique, calculer_age, COLONNES_BRUTES_ATTENDUES,
    simuler_optimisation, generer_pdf_diagnostic, envoyer_email_pdf, nettoyer_decimals,
    generer_diagnostic_openrouter
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main_api')

DATABASE_URL = os.environ.get('NEON_DATABASE_URL')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Variables pour GitHub Actions
USE_GITHUB_ACTIONS = os.environ.get('USE_GITHUB_ACTIONS', 'false').lower() == 'true'
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'Yves-ANAGUE/canada-visa-project')
GITHUB_PAT = os.environ.get('GITHUB_PAT', '')

etat_application = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Chargement du modele ML en memoire...")
    
    etat_application['modele'] = joblib.load(os.path.join(BASE_DIR, 'modele_canada.pkl'))
    etat_application['seuil'] = joblib.load(os.path.join(BASE_DIR, 'seuil_decision.pkl'))
    etat_application['engine'] = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=3,
        max_overflow=5
    )
    
    try:
        with open(os.path.join(BASE_DIR, 'top_features.json'), 'r') as f:
            etat_application['top_features'] = json.load(f)
        logger.info(f"Facteurs clés chargés : {etat_application['top_features'][:5]}")
    except FileNotFoundError:
        etat_application['top_features'] = [
            'experience_totale', 'ratio_fonds', 'eca_obtained',
            'provincial_nomination', 'clb_english_min'
        ]
        logger.warning("top_features.json non trouvé - utilisation des valeurs par défaut")
    
    try:
        etat_application['feature_importance'] = pd.read_csv(
            os.path.join(BASE_DIR, 'feature_importance_finale.csv')
        )
        logger.info("Donnees d'importance des features chargees.")
    except FileNotFoundError:
        logger.warning("Fichier feature_importance_finale.csv non trouve - analytics desactivees")
    
    logger.info("Modele charge avec succes. API prete.")
    yield
    logger.info("Fermeture de l'application, liberation des ressources...")
    etat_application['engine'].dispose()

app = FastAPI(
    title="API Prediction Visa Canada",
    description="Systeme predictif de decision visa - Entree Express",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hici-canada-visa.onrender.com",   # Remplacez par l'URL réelle de votre frontend Render
        "http://localhost:3000",
        "http://localhost:8550",
        "https://hici-canada-visa-api.onrender.com"  # L'URL du backend lui-même
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def gestionnaire_erreurs_global(request: Request, exc: Exception):
    logger.error(f"Erreur non geree sur {request.url.path} : {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erreur interne : {str(exc)}", "route": str(request.url.path)}
    )

security = HTTPBasic()

@app.get("/")
def racine():
    return {"message": "API HI Consulting Immigration - Prediction Visa Canada", "documentation": "/docs"}

def verifier_identifiants(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    engine = etat_application['engine']
    with engine.connect() as conn:
        resultat = conn.execute(
            text("""SELECT identifiant_conseiller, nom_agent, mot_de_passe_hache, statut_compte
                     FROM gestion_utilisateurs WHERE email_agent = :email"""),
            {"email": credentials.username}
        ).fetchone()

    if resultat is None or resultat.statut_compte != 'Actif':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides ou compte suspendu"
        )

    if not verifier_mot_de_passe(credentials.password, resultat.mot_de_passe_hache):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides"
        )

    return {"identifiant_conseiller": resultat.identifiant_conseiller, "nom_agent": resultat.nom_agent}

# ============================================================
# SCHEMAS PYDANTIC
# ============================================================

from pydantic import field_validator

class ProfilCandidatPartiel(BaseModel):
    application_year: Optional[int] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    marital_status: Optional[str] = None
    country_of_origin: Optional[str] = None
    education_level: Optional[str] = None
    eca_obtained: Optional[str] = None
    english_test: Optional[str] = None
    clb_speaking_english: Optional[int] = None
    clb_listening_english: Optional[int] = None
    clb_reading_english: Optional[int] = None
    clb_writing_english: Optional[int] = None
    french_test: Optional[str] = None
    nclc_speaking_french: Optional[int] = None
    nclc_listening_french: Optional[int] = None
    nclc_reading_french: Optional[int] = None
    nclc_writing_french: Optional[int] = None
    years_foreign_experience: Optional[int] = None
    years_canadian_experience: Optional[int] = None
    sector: Optional[str] = None
    teer_category: Optional[str] = None
    job_offer_canada: Optional[str] = None
    job_offer_teer: Optional[str] = None
    provincial_nomination: Optional[str] = None
    studied_in_canada: Optional[str] = None
    family_in_canada: Optional[str] = None
    funds_available_cad: Optional[float] = None
    dependants: Optional[int] = None
    medical_exam_ok: Optional[str] = None
    criminal_record: Optional[str] = None
    inadmissibility: Optional[str] = None
    program: Optional[str] = None
    crs_score: Optional[int] = None

    @field_validator('*', mode='before')
    @classmethod
    def vide_devient_none(cls, valeur):
        if valeur == '':
            return None
        return valeur

class ProfilCandidat(BaseModel):
    application_year: int
    age: int
    sex: str
    marital_status: str
    country_of_origin: str
    education_level: str
    eca_obtained: str
    english_test: str
    clb_speaking_english: int
    clb_listening_english: int
    clb_reading_english: int
    clb_writing_english: int
    french_test: str
    nclc_speaking_french: int
    nclc_listening_french: int
    nclc_reading_french: int
    nclc_writing_french: int
    years_foreign_experience: int
    years_canadian_experience: int
    sector: str
    teer_category: str
    job_offer_canada: str
    job_offer_teer: str
    provincial_nomination: str
    studied_in_canada: str
    family_in_canada: str
    funds_available_cad: float
    dependants: int
    medical_exam_ok: str
    criminal_record: str
    inadmissibility: str
    program: str

class DossierPartiel(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    numero_document: Optional[str] = None
    date_naissance: Optional[date] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    ville_residence: Optional[str] = None
    type_contrat: Optional[str] = None
    frais_encaisses: Optional[float] = None
    restes_a_payer: Optional[float] = None
    phase_traitement: Optional[str] = None
    visa_decision: Optional[str] = None
    notes: Optional[str] = None
    profil: Optional[ProfilCandidatPartiel] = None

    @field_validator('nom', 'prenom', 'numero_document', 'email', 'telephone',
                      'ville_residence', 'type_contrat', 'phase_traitement', 'visa_decision', 'notes',
                      mode='before')
    @classmethod
    def vide_devient_none(cls, valeur):
        if valeur == '':
            return None
        return valeur

    @field_validator('date_naissance', mode='before')
    @classmethod
    def date_vide_devient_none(cls, valeur):
        if valeur == '' or valeur is None:
            return None
        return valeur

# ============================================================
# ROUTES
# ============================================================

@app.post("/predire")
def endpoint_predire(profil: ProfilCandidat, agent: dict = Depends(verifier_identifiants)):
    try:
        resultat = predire_client(
            profil.model_dump(),
            modele=etat_application['modele'],
            seuil=etat_application['seuil']
        )
        return resultat
    except Exception as e:
        logger.error(f"Erreur de prediction : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prediction : {str(e)}")

@app.post("/diagnostic")
def endpoint_diagnostic(profil: ProfilCandidat, agent: dict = Depends(verifier_identifiants)):
    resultat_prediction = predire_client(
        profil.model_dump(),
        modele=etat_application['modele'],
        seuil=etat_application['seuil']
    )
    try:
        top_df = etat_application.get('feature_importance')
        diagnostic_texte = generer_diagnostic_openrouter(profil.model_dump(), resultat_prediction, top_df)
    except Exception as e:
        logger.error(f"Erreur OpenRouter : {e}")
        diagnostic_texte = "Diagnostic IA temporairement indisponible."
    return {**resultat_prediction, "diagnostic_ia": diagnostic_texte}



# 6. ROUTE : CREATION D'UN NOUVEAU DOSSIER (predictions_canada)


# creation de dossier (accepte maintenant un profil PARTIEL - saisie progressive)


from backend.utils import generer_id_client_atomique   # ajouter cet import


# REMPLACE creer_dossier dans main_api.py

@app.post("/dossiers/nouveau")
def creer_dossier(dossier: DossierPartiel, agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    profil_dict = dossier.profil.model_dump() if dossier.profil else {}
    annee = profil_dict.get('application_year') or datetime.now().year
    if dossier.date_naissance:
        profil_dict['age'] = calculer_age(dossier.date_naissance)

    resultat_prediction = predire_client(
        profil_dict, modele=etat_application['modele'], seuil=etat_application['seuil']
    )

    id_client = generer_id_client_atomique(engine, annee)

    # --- Cas : dossier cree directement comme historique cloture ---
    if dossier.phase_traitement == 'Closed':
        if not dossier.visa_decision:
            raise HTTPException(status_code=400, detail="visa_decision requis pour un dossier cloture")
        
        colonnes_communes = [
            'id_client','nom','prenom','numero_document','date_naissance','email','telephone',
            'ville_residence','type_contrat','frais_encaisses','restes_a_payer',
            'identifiant_conseiller','notes'
        ] + list(profil_dict.keys()) + ['visa_decision', 'crs_score']
        
        valeurs = {
            'id_client': id_client,
            'nom': dossier.nom,
            'prenom': dossier.prenom,
            'numero_document': dossier.numero_document,
            'date_naissance': dossier.date_naissance,
            'email': dossier.email,
            'telephone': dossier.telephone,
            'ville_residence': dossier.ville_residence,
            'type_contrat': dossier.type_contrat,
            'frais_encaisses': dossier.frais_encaisses or 0,
            'restes_a_payer': dossier.restes_a_payer or 0,
            'identifiant_conseiller': agent['identifiant_conseiller'],
            'notes': dossier.notes or '',
            **profil_dict,
            'visa_decision': dossier.visa_decision,
            'crs_score': profil_dict.get('crs_score') or dossier.profil.crs_score if dossier.profil else None,
        }
        
        with engine.connect() as conn:
            conn.execute(text(f"""
                INSERT INTO apprentissage_canada ({', '.join(colonnes_communes)})
                VALUES ({', '.join(':' + c for c in colonnes_communes)})
            """), valeurs)
            conn.commit()
        return {"id_client": id_client, "statut": "Dossier historique cree", "prediction": resultat_prediction}

    # --- Cas normal : dossier en cours ---
    with engine.connect() as conn:
        toutes_colonnes = {**profil_dict}
        if dossier.profil and dossier.profil.crs_score is not None:
            toutes_colonnes['crs_score'] = dossier.profil.crs_score
        
        colonnes_sql = ', '.join(toutes_colonnes.keys())
        valeurs_sql = ', '.join(':' + k for k in toutes_colonnes.keys())
        
        conn.execute(text(f"""
            INSERT INTO predictions_canada (
                id_client, nom, prenom, numero_document, date_naissance,
                email, telephone, ville_residence, type_contrat,
                frais_encaisses, restes_a_payer, phase_traitement,
                identifiant_conseiller, notes, {colonnes_sql},
                probabilite_acceptation_ml, decision_predite_ml, date_derniere_prediction
            ) VALUES (
                :id_client, :nom, :prenom, :numero_document, :date_naissance,
                :email, :telephone, :ville_residence, :type_contrat,
                :frais_encaisses, :restes_a_payer, :phase_traitement,
                :identifiant_conseiller, :notes, {valeurs_sql},
                :proba, :decision, :date_prediction
            )
        """), {
            "id_client": id_client,
            "nom": dossier.nom,
            "prenom": dossier.prenom,
            "numero_document": dossier.numero_document,
            "date_naissance": dossier.date_naissance,
            "email": dossier.email,
            "telephone": dossier.telephone,
            "ville_residence": dossier.ville_residence,
            "type_contrat": dossier.type_contrat,
            "frais_encaisses": dossier.frais_encaisses or 0,
            "restes_a_payer": dossier.restes_a_payer or 0,
            "phase_traitement": dossier.phase_traitement or 'File Opened',
            "identifiant_conseiller": agent['identifiant_conseiller'],
            "notes": dossier.notes or '',
            **toutes_colonnes,
            "proba": resultat_prediction['probabilite_acceptation'] if resultat_prediction else None,
            "decision": resultat_prediction['decision_predite'] if resultat_prediction else None,
            "date_prediction": datetime.now() if resultat_prediction else None
        })
        conn.commit()

    return {"id_client": id_client, "prediction": resultat_prediction}


# 7. ROUTE : RECHERCHE MULTICRITERE 


# CORRECTION dans main_api.py - lister_dossiers accepte decision

@app.get("/dossiers/liste")
def lister_dossiers(
    terme: str = "", 
    programme: str = "", 
    pays: str = "", 
    phase: str = "", 
    decision: str = "",
    limit: int = 100, 
    agent: dict = Depends(verifier_identifiants)
):
    engine = etat_application['engine']
    colonnes = ("id_client, nom, prenom, numero_document, telephone, email, "
                "phase_traitement, program, country_of_origin, decision_predite_ml, "
                "date_creation, date_maj")
    colonnes_archive = colonnes.replace("decision_predite_ml", "visa_decision")

    conditions_actifs = []
    params_actifs = {"limit": limit}
    conditions_archives = []
    params_archives = {"limit": limit}
    
    if terme:
        conditions_actifs.append("(nom ILIKE :terme OR prenom ILIKE :terme OR numero_document ILIKE :terme "
                                 "OR telephone ILIKE :terme OR id_client ILIKE :terme OR email ILIKE :terme "
                                 "OR identifiant_conseiller ILIKE :terme)")
        conditions_archives.append("(nom ILIKE :terme OR prenom ILIKE :terme OR numero_document ILIKE :terme "
                                   "OR telephone ILIKE :terme OR id_client ILIKE :terme OR email ILIKE :terme "
                                   "OR identifiant_conseiller ILIKE :terme)")
        params_actifs["terme"] = f"%{terme}%"
        params_archives["terme"] = f"%{terme}%"
    
    if programme:
        conditions_actifs.append("program = :programme")
        conditions_archives.append("program = :programme")
        params_actifs["programme"] = programme
        params_archives["programme"] = programme
    
    if pays:
        conditions_actifs.append("country_of_origin = :pays")
        conditions_archives.append("country_of_origin = :pays")
        params_actifs["pays"] = pays
        params_archives["pays"] = pays
    
    if phase:
        conditions_actifs.append("phase_traitement = :phase")
        params_actifs["phase"] = phase
        if phase == "Closed":
            pass
        else:
            conditions_archives.append("1 = 0")
    
    if decision:
        conditions_archives.append("visa_decision = :decision")
        params_archives["decision"] = decision

    clause_actifs = ("WHERE " + " AND ".join(conditions_actifs)) if conditions_actifs else ""
    clause_archives = ("WHERE " + " AND ".join(conditions_archives)) if conditions_archives else ""

    with engine.connect() as conn:
        actifs = conn.execute(text(
            f"SELECT {colonnes} FROM predictions_canada {clause_actifs} ORDER BY date_maj DESC LIMIT :limit"
        ), params_actifs).fetchall()
        
        archives = conn.execute(text(
            f"SELECT {colonnes_archive} FROM apprentissage_canada {clause_archives} ORDER BY date_maj DESC LIMIT :limit"
        ), params_archives).fetchall()

    resultats = []
    for r in actifs:
        d = dict(r._mapping)
        d["origine"] = "En cours"
        d["decision"] = d.pop("decision_predite_ml", None)
        resultats.append(d)
    
    for r in archives:
        d = dict(r._mapping)
        d["origine"] = "Archive"
        d["decision"] = d.pop("visa_decision", None)
        d["phase_traitement"] = "Closed"
        resultats.append(d)

    resultats.sort(key=lambda x: x["date_maj"] or x["date_creation"], reverse=True)
    return resultats[:limit]

# 8. ROUTE DE SANTE (verification que l'API est en vie)

@app.get("/sante")
def verifier_sante():
    return {
        "statut": "operationnel",
        "modele_charge": 'modele' in etat_application,
        "horodatage": datetime.now().isoformat()
    }


@app.get("/analytics/feature-importance")
def endpoint_feature_importance(agent: dict = Depends(verifier_identifiants)):
    if 'feature_importance' not in etat_application:
        raise HTTPException(status_code=503, detail="Donnees analytiques non chargees")
    df_imp = etat_application['feature_importance'].head(15)
    
    # Déterminer le nom de la colonne d'importance (peut être 'importance' ou 'Importance')
    col_importance = 'importance' if 'importance' in df_imp.columns else 'Importance'
    
    return [
        {"variable": row['Variable_origine'], "importance": round(row[col_importance], 4)}
        for _, row in df_imp.iterrows()
    ]


@app.get("/analytics/statistiques-globales")
def endpoint_stats_globales(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        taux_par_annee = conn.execute(text("""
            SELECT application_year,
                   ROUND(100.0 * SUM(CASE WHEN visa_decision='Accepted' THEN 1 ELSE 0 END) / COUNT(*), 1) AS taux_acceptation
            FROM apprentissage_canada
            GROUP BY application_year ORDER BY application_year
        """)).fetchall()

        repartition_programme = conn.execute(text("""
            SELECT program, COUNT(*) AS total FROM apprentissage_canada GROUP BY program
        """)).fetchall()

    return {
        "taux_acceptation_par_annee": [dict(row._mapping) for row in taux_par_annee],
        "repartition_par_programme": [dict(row._mapping) for row in repartition_programme]
    }



@app.post("/simulateur-optimisation")
def endpoint_simulateur(profil: ProfilCandidat, agent: dict = Depends(verifier_identifiants)):
    return simuler_optimisation(profil.model_dump(), etat_application['modele'], etat_application['seuil'])



# CORRECTION dans main_api.py - simplifie _construire_rapport,
# supprime le "gate" bloquant, appelle toujours predire_client

def _construire_rapport(id_client: str):
    dossier = obtenir_dossier(id_client, agent={"identifiant_conseiller": "system"})
    profil = nettoyer_decimals({c: dossier.get(c) for c in COLONNES_BRUTES_ATTENDUES})
    est_archive = dossier.get("archive", False)

    resultat = predire_client(profil, etat_application['modele'], etat_application['seuil'])

    scenarios = []
    try:
        simulation = simuler_optimisation(profil, etat_application['modele'], etat_application['seuil'])
        scenarios = simulation['scenarios_ameliorations']
    except Exception as e:
        logger.error(f"Erreur simulateur {id_client} : {e}", exc_info=True)

    try:
        top_df = etat_application.get('feature_importance')
        diagnostic_texte = generer_diagnostic_openrouter(profil, resultat, top_df)
    except Exception as e:
        logger.error(f"Erreur OpenRouter : {e}")
        diagnostic_texte = "Diagnostic IA temporairement indisponible."

    return dossier, resultat, diagnostic_texte, scenarios, None


@app.get("/dossiers/{id_client}/diagnostic-complet")
def endpoint_diagnostic_complet(id_client: str, agent: dict = Depends(verifier_identifiants)):
    dossier, resultat, diagnostic, scenarios, erreur_simulation = _construire_rapport(id_client)
    return {"resultat": resultat, "diagnostic_ia": diagnostic, "scenarios": scenarios,
            "erreur_simulation": erreur_simulation, "dossier": dossier}

# ============================================================
# PDF ET EMAIL
# ============================================================

@app.get("/dossiers/{id_client}/pdf")
def endpoint_telecharger_pdf(id_client: str, agent: dict = Depends(verifier_identifiants)):
    dossier, resultat, diagnostic, scenarios, _ = _construire_rapport(id_client)
    metriques = endpoint_metriques_modele(agent)
    pdf_bytes = generer_pdf_diagnostic(dossier, resultat, diagnostic, scenarios, metriques)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=rapport_{id_client}.pdf'}
    )

@app.post("/dossiers/{id_client}/envoyer-email")
def endpoint_envoyer_email(id_client: str, agent: dict = Depends(verifier_identifiants)):
    dossier, resultat, diagnostic, scenarios, _ = _construire_rapport(id_client)
    if not dossier.get('email'):
        raise HTTPException(status_code=400, detail="Aucune adresse e-mail enregistree pour ce dossier")
    metriques = endpoint_metriques_modele(agent)
    pdf_bytes = generer_pdf_diagnostic(dossier, resultat, diagnostic, scenarios, metriques)
    envoyer_email_pdf(
        destinataire=dossier['email'],
        sujet="Votre rapport d'evaluation - HI Consulting Immigration",
        corps=(
            f"Bonjour {dossier.get('nom','')} {dossier.get('prenom','')},\n\n"
            f"Suite a l'analyse de votre dossier d'immigration (programme {dossier.get('program','-')}), "
            f"veuillez trouver ci-joint votre rapport d'evaluation detaille, incluant le diagnostic "
            f"de notre systeme et nos recommandations personnalisees.\n\n"
            f"Pour toute question, notre equipe reste a votre disposition.\n\n"
            f"Cordialement,\nL'equipe HI Consulting Immigration\n"
            f"Logpom Carrefour Bassong, Douala - +237 678 924 045"
        ),
        pdf_bytes=pdf_bytes,
        nom_fichier=f"rapport_{id_client}.pdf"
    )
    return {"statut": "Email envoye avec succes", "destinataire": dossier['email']}


@app.get("/dossiers/{id_client}/diagnostic-complet")
def endpoint_diagnostic_complet(id_client: str, agent: dict = Depends(verifier_identifiants)):
    dossier, resultat, diagnostic, scenarios = _construire_rapport(id_client)
    return {"resultat": resultat, "diagnostic_ia": diagnostic, "scenarios": scenarios, "dossier": dossier}


def _agent_est_admin(agent: dict = Depends(verifier_identifiants)) -> dict:
    engine = etat_application['engine']
    with engine.connect() as conn:
        est_admin = conn.execute(text(
            "SELECT est_admin FROM gestion_utilisateurs WHERE identifiant_conseiller = :id"
        ), {"id": agent['identifiant_conseiller']}).scalar()
    if not est_admin:
        raise HTTPException(status_code=403, detail="Reserve aux administrateurs")
    return agent



@app.post("/admin/reentrainer")
def endpoint_reentrainer(background_tasks: BackgroundTasks, admin: dict = Depends(_agent_est_admin)):
    if USE_GITHUB_ACTIONS:
        if not GITHUB_PAT:
            raise HTTPException(status_code=503, detail="GITHUB_PAT non configuré")
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/train-monthly.yml/dispatches"
        response = requests_lib.post(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_PAT}",
                "Accept": "application/vnd.github+json",
            },
            json={"ref": "main"},
            timeout=10,
        )
        if response.status_code != 204:
            raise HTTPException(status_code=502, detail=f"Erreur déclenchement : {response.text}")
        return {"statut": "Reentrainement déclenché via GitHub Actions."}
    else:
        # Import local pour éviter le chargement au démarrage
        try:
            import backend.train as module_train
        except ImportError:
            # Fallback pour le développement local (si backend n'est pas un package)
            import train as module_train
        background_tasks.add_task(module_train.main, declenchement='manuel')
        return {"statut": "Reentrainement local lancé (BackgroundTasks)."}




@app.get("/admin/historique-entrainement")
def endpoint_historique(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        lignes = conn.execute(text(
            "SELECT * FROM historique_entrainement ORDER BY date_execution DESC LIMIT 20"
        )).fetchall()
    return [dict(row._mapping) for row in lignes]



# NOUVEAU : recuperer un dossier existant (pour l'ecran d'edition)


# REMPLACE obtenir_dossier dans main_api.py

@app.get("/dossiers/{id_client}")
def obtenir_dossier(id_client: str, agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        ligne = conn.execute(text(
            "SELECT * FROM predictions_canada WHERE id_client = :id"
        ), {"id": id_client}).fetchone()
        if ligne:
            d = dict(ligne._mapping); d["archive"] = False
            return d

        ligne = conn.execute(text(
            "SELECT * FROM apprentissage_canada WHERE id_client = :id"
        ), {"id": id_client}).fetchone()
        if ligne:
            d = dict(ligne._mapping); d["archive"] = True
            d["decision_predite_ml"] = d.get("visa_decision")
            return d

    raise HTTPException(status_code=404, detail="Dossier introuvable")


@app.post("/dossiers/{id_client}/reouvrir")
def reouvrir_dossier(id_client: str, agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.begin() as conn:
        ligne = conn.execute(text(
            "SELECT * FROM apprentissage_canada WHERE id_client = :id"
        ), {"id": id_client}).fetchone()
        if ligne is None:
            raise HTTPException(status_code=404, detail="Dossier introuvable dans les archives")

        donnees = dict(ligne._mapping)
        colonnes_communes = [
            'id_client','nom','prenom','numero_document','date_naissance','email','telephone',
            'ville_residence','type_contrat','frais_encaisses','restes_a_payer',
            'identifiant_conseiller','notes'
        ] + COLONNES_BRUTES_ATTENDUES + ['crs_score']
        valeurs = {c: donnees.get(c) for c in colonnes_communes}
        valeurs['phase_traitement'] = 'Submitted in Pool'
        valeurs['probabilite_acceptation_ml'] = None
        valeurs['decision_predite_ml'] = None
        valeurs['date_derniere_prediction'] = None

        colonnes_insert = colonnes_communes + ['phase_traitement', 'probabilite_acceptation_ml',
                                                  'decision_predite_ml', 'date_derniere_prediction']
        conn.execute(text(f"""
            INSERT INTO predictions_canada ({', '.join(colonnes_insert)})
            VALUES ({', '.join(':' + c for c in colonnes_insert)})
        """), valeurs)
        conn.execute(text("DELETE FROM apprentissage_canada WHERE id_client = :id"), {"id": id_client})

    return {"statut": "Dossier reouvert et deplace vers les dossiers en cours", "id_client": id_client}


# NOUVEAU : modifier un dossier existant (UPDATE cible,  + declenchement automatique de l'archivage transactionnel si phase_traitement passe a 'Closed')

@app.put("/dossiers/{id_client}")
def modifier_dossier(id_client: str, dossier: DossierPartiel, agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']

    with engine.connect() as conn:
        existant = conn.execute(text(
            "SELECT * FROM predictions_canada WHERE id_client = :id"
        ), {"id": id_client}).fetchone()

    if existant is None:
        raise HTTPException(status_code=404, detail="Dossier introuvable ou deja cloture/archive")

    donnees_existantes = dict(existant._mapping)

    # Fusion : seuls les champs fournis (non None) ecrasent l'existant
    champs_modifies = {}
    
    # Champs du dossier principal (en utilisant getattr avec default None)
    champs_dossier = ['nom','prenom','numero_document','date_naissance','email','telephone',
                      'ville_residence','type_contrat','frais_encaisses','restes_a_payer',
                      'phase_traitement','visa_decision', 'notes']
    
    for champ in champs_dossier:
        valeur = getattr(dossier, champ, None)
        if valeur is not None:
            champs_modifies[champ] = valeur

    # Champs du profil
    if dossier.profil:
        # Récupérer tous les champs du profil
        for champ, valeur in dossier.profil.model_dump().items():
            if valeur is not None:
                champs_modifies[champ] = valeur
        
        # crs_score est dans le profil
        if hasattr(dossier.profil, 'crs_score') and dossier.profil.crs_score is not None:
            champs_modifies['crs_score'] = dossier.profil.crs_score

    donnees_fusionnees = {**donnees_existantes, **champs_modifies}

    # CAS 1 : le dossier est cloture -> ARCHIVAGE
    if donnees_fusionnees.get('phase_traitement') == 'Closed':
        if not donnees_fusionnees.get('visa_decision'):
            raise HTTPException(
                status_code=400,
                detail="visa_decision (Accepted/Refused) est obligatoire pour cloturer un dossier."
            )

        colonnes_communes = [
            'id_client','nom','prenom','numero_document','date_naissance','email','telephone',
            'ville_residence','type_contrat','frais_encaisses','restes_a_payer',
            'phase_traitement','identifiant_conseiller','notes'
        ] + COLONNES_BRUTES_ATTENDUES + ['crs_score', 'visa_decision']

        valeurs_archive = {c: donnees_fusionnees.get(c) for c in colonnes_communes}

        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO apprentissage_canada ({', '.join(colonnes_communes)})
                VALUES ({', '.join(':' + c for c in colonnes_communes)})
            """), valeurs_archive)
            conn.execute(text(
                "DELETE FROM predictions_canada WHERE id_client = :id"
            ), {"id": id_client})

        return {"statut": "Dossier cloture et archive dans apprentissage_canada", "id_client": id_client}

    # CAS 2 : mise a jour classique (dossier reste actif)
    profil_pour_prediction = {c: donnees_fusionnees.get(c) for c in COLONNES_BRUTES_ATTENDUES}
    
    resultat_prediction = predire_client(
        profil_pour_prediction, modele=etat_application['modele'], seuil=etat_application['seuil']
    )
    
    champs_modifies['probabilite_acceptation_ml'] = resultat_prediction['probabilite_acceptation']
    champs_modifies['decision_predite_ml'] = resultat_prediction['decision_predite']
    champs_modifies['date_derniere_prediction'] = datetime.now()

    if champs_modifies:
        set_clause = ', '.join(f"{c} = :{c}" for c in champs_modifies)
        with engine.connect() as conn:
            conn.execute(text(
                f"UPDATE predictions_canada SET {set_clause}, date_maj = NOW() WHERE id_client = :id_client"
            ), {**champs_modifies, "id_client": id_client})
            conn.commit()

    return {"statut": "Dossier mis a jour", "id_client": id_client, "prediction": resultat_prediction}


# NOUVEAU : suppression (uniquement dossiers EN COURS "les dossiers termines et clotures sont insupprimables")

@app.delete("/dossiers/{id_client}")
def supprimer_dossier(id_client: str, agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        existant = conn.execute(text(
            "SELECT phase_traitement FROM predictions_canada WHERE id_client = :id"
        ), {"id": id_client}).fetchone()

        if existant is None:
            raise HTTPException(
                status_code=404,
                detail="Dossier introuvable dans les dossiers actifs (peut-etre deja archive et donc insupprimable)."
            )

        conn.execute(text(
            "DELETE FROM predictions_canada WHERE id_client = :id"
        ), {"id": id_client})
        conn.commit()

    return {"statut": "Dossier supprime (client demissionnaire)", "id_client": id_client}


# NOUVEAU : CRUD des agents (reserve aux administrateurs)

class AgentCreation(BaseModel):
    nom_agent: str
    email_agent: str
    mot_de_passe: str
    identifiant_conseiller: str


@app.post("/admin/agents")
def creer_agent(agent_data: AgentCreation, admin: dict = Depends(_agent_est_admin)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO gestion_utilisateurs
                (identifiant_conseiller, nom_agent, email_agent, mot_de_passe_hache, statut_compte)
            VALUES (:id_cons, :nom, :email, :mdp, 'Actif')
        """), {
            "id_cons": agent_data.identifiant_conseiller, "nom": agent_data.nom_agent,
            "email": agent_data.email_agent, "mdp": hacher_mot_de_passe(agent_data.mot_de_passe)
        })
        conn.commit()
    return {"statut": "Agent cree", "identifiant_conseiller": agent_data.identifiant_conseiller}






# AJOUT dans main_api.py - remplace le GET /admin/agents existant
# et ajoute l'edition complete

@app.get("/admin/agents")
def lister_agents(terme: str = "", admin: dict = Depends(_agent_est_admin)):
    engine = etat_application['engine']
    condition = ""
    params = {}
    if terme:
        condition = ("WHERE nom_agent ILIKE :terme OR email_agent ILIKE :terme "
                     "OR identifiant_conseiller ILIKE :terme")
        params["terme"] = f"%{terme}%"
    with engine.connect() as conn:
        lignes = conn.execute(text(
            f"SELECT identifiant_conseiller, nom_agent, email_agent, statut_compte, est_admin, date_creation "
            f"FROM gestion_utilisateurs {condition} ORDER BY date_creation DESC"
        ), params).fetchall()
    return [dict(row._mapping) for row in lignes]


class AgentModification(BaseModel):
    nom_agent: Optional[str] = None
    email_agent: Optional[str] = None
    mot_de_passe: Optional[str] = None
    est_admin: Optional[bool] = None
    statut_compte: Optional[str] = None


@app.put("/admin/agents/{identifiant_conseiller}")
def modifier_agent(identifiant_conseiller: str, donnees: AgentModification,
                    admin: dict = Depends(_agent_est_admin)):
    engine = etat_application['engine']
    champs = {}
    if donnees.nom_agent is not None: champs['nom_agent'] = donnees.nom_agent
    if donnees.email_agent is not None: champs['email_agent'] = donnees.email_agent
    if donnees.mot_de_passe: champs['mot_de_passe_hache'] = hacher_mot_de_passe(donnees.mot_de_passe)
    if donnees.est_admin is not None: champs['est_admin'] = donnees.est_admin
    if donnees.statut_compte is not None: champs['statut_compte'] = donnees.statut_compte

    if not champs:
        raise HTTPException(status_code=400, detail="Aucun champ a modifier")

    set_clause = ', '.join(f"{c} = :{c}" for c in champs)
    with engine.connect() as conn:
        conn.execute(text(
            f"UPDATE gestion_utilisateurs SET {set_clause} WHERE identifiant_conseiller = :id"
        ), {**champs, "id": identifiant_conseiller})
        conn.commit()
    return {"statut": "Agent mis a jour", "identifiant_conseiller": identifiant_conseiller}

@app.put("/admin/agents/{identifiant_conseiller}/statut")
def modifier_statut_agent(identifiant_conseiller: str, statut: str, admin: dict = Depends(_agent_est_admin)):
    if statut not in ['Actif', 'Suspendu']:
        raise HTTPException(status_code=400, detail="Statut invalide (Actif ou Suspendu)")
    engine = etat_application['engine']
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE gestion_utilisateurs SET statut_compte = :s WHERE identifiant_conseiller = :id"
        ), {"s": statut, "id": identifiant_conseiller})
        conn.commit()
    return {"statut": f"Compte {identifiant_conseiller} mis a jour : {statut}"}


@app.delete("/admin/agents/{identifiant_conseiller}")
def supprimer_agent(identifiant_conseiller: str, admin: dict = Depends(_agent_est_admin)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        conn.execute(text(
            "DELETE FROM gestion_utilisateurs WHERE identifiant_conseiller = :id"
        ), {"id": identifiant_conseiller})
        conn.commit()
    return {"statut": f"Agent {identifiant_conseiller} supprime definitivement"}



@app.get("/moi")
def obtenir_mon_profil(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        ligne = conn.execute(text(
            "SELECT identifiant_conseiller, nom_agent, email_agent, est_admin "
            "FROM gestion_utilisateurs WHERE identifiant_conseiller = :id"
        ), {"id": agent['identifiant_conseiller']}).fetchone()
    return dict(ligne._mapping)



@app.get("/analytics/metriques-modele")
def endpoint_metriques_modele(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        # Récupérer le dernier modèle valide (meilleure précision)
        ligne = conn.execute(text("""
            SELECT * FROM historique_entrainement 
            WHERE modele_valide = TRUE 
            ORDER BY precision_score DESC 
            LIMIT 1
        """)).fetchone()
    
    if ligne is None:
        return {
            "accuracy": None, 
            "precision_score": None, 
            "recall_score": None,
            "specificity_score": None, 
            "f1_score": None, 
            "roc_auc": None, 
            "date_execution": None
        }
    
    result = dict(ligne._mapping)
    
    # S'assurer que la date est au bon format
    if result.get('date_execution'):
        # Si c'est un datetime, le convertir en string ISO
        if hasattr(result['date_execution'], 'isoformat'):
            result['date_execution'] = result['date_execution'].isoformat()
    
    return result


@app.get("/analytics/repartition-pays")
def endpoint_repartition_pays(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        lignes = conn.execute(text(
            "SELECT country_of_origin, COUNT(*) AS total FROM apprentissage_canada "
            "GROUP BY country_of_origin ORDER BY total DESC LIMIT 10"
        )).fetchall()
    return [dict(r._mapping) for r in lignes]


@app.get("/analytics/taux-par-secteur")
def endpoint_taux_secteur(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        lignes = conn.execute(text(
            "SELECT sector, ROUND(100.0*SUM(CASE WHEN visa_decision='Accepted' THEN 1 ELSE 0 END)/COUNT(*),1) AS taux, "
            "COUNT(*) AS total FROM apprentissage_canada GROUP BY sector ORDER BY total DESC"
        )).fetchall()
    return [dict(r._mapping) for r in lignes]


@app.get("/analytics/taux-par-education")
def endpoint_taux_education(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        lignes = conn.execute(text(
            "SELECT education_level, ROUND(100.0*SUM(CASE WHEN visa_decision='Accepted' THEN 1 ELSE 0 END)/COUNT(*),1) AS taux, "
            "COUNT(*) AS total FROM apprentissage_canada GROUP BY education_level ORDER BY total DESC"
        )).fetchall()
    return [dict(r._mapping) for r in lignes]


@app.get("/analytics/repartition-decision")
def endpoint_repartition_decision(agent: dict = Depends(verifier_identifiants)):
    engine = etat_application['engine']
    with engine.connect() as conn:
        lignes = conn.execute(text(
            "SELECT visa_decision, COUNT(*) AS total FROM apprentissage_canada GROUP BY visa_decision"
        )).fetchall()
    return [dict(r._mapping) for r in lignes]

# backend/main_api.py
import os


# Pour Vercel - le point d'entrée
app = app

