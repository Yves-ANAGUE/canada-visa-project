# creer_premier_agent.py
# SCRIPT A USAGE UNIQUE - cree le premier compte administrateur

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from backend.utils import hacher_mot_de_passe

load_dotenv()
engine = create_engine(os.environ['NEON_DATABASE_URL'])

with engine.connect() as conn:
    conn.execute(text("""
        INSERT INTO gestion_utilisateurs
            (identifiant_conseiller, nom_agent, email_agent, mot_de_passe_hache, statut_compte, est_admin)
        VALUES
            (:id_cons, :nom, :email, :mdp_hache, 'Actif', TRUE)
    """), {
        "id_cons": "CONS-001",
        "nom": "Sporah Mbeng",
        "email": "hiciofficiel@gmail.com",
        "mdp_hache": hacher_mot_de_passe("ChangezMoiImmediatement123!")
    })
    conn.commit()

print("Premier compte administrateur cree : hiciofficiel@gmail.com")
print("Mot de passe temporaire : ChangezMoiImmediatement123! (a changer immediatement)")
