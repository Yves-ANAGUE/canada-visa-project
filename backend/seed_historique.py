# seed_historique.py
# SCRIPT A USAGE UNIQUE - a executer UNE SEULE FOIS pour peupler la table apprentissage_canada avec le dataset historique de 4750 dossiers. Ne fait PAS partie du cycle de production normal.

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ['NEON_DATABASE_URL']
CHEMIN_CSV = '../data/canada_visa_prediction_dataset.csv'


def preparer_donnees_pour_import(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute les colonnes administratives manquantes (avec des valeurs
    neutres, ce dataset etant un historique anonyme de reference)
    et genere un id_client unique pour chaque ligne.
    """
    df = df.copy()

    # Generation d'un id_client sequentiel unique : CAN-{annee}-{numero}
    df = df.reset_index(drop=True)
    df['id_client'] = df.apply(
        lambda row: f"CAN-{row['application_year']}-{row.name+1:05d}", axis=1
    )

    # Colonnes administratives : valeurs neutres (donnees non disponibles
    # pour ce dataset historique de reference)
    df['nom'] = None
    df['prenom'] = None
    df['numero_document'] = None
    df['date_naissance'] = None
    df['email'] = None
    df['telephone'] = None
    df['ville_residence'] = None
    df['type_contrat'] = None
    df['frais_encaisses'] = 0
    df['restes_a_payer'] = 0
    df['phase_traitement'] = 'Closed'          # historique = toujours cloture
    df['identifiant_conseiller'] = None
    df['notes'] = 'Import initial - dataset historique de reference'

    return df


def importer_dans_neon(df: pd.DataFrame):
    engine = create_engine(DATABASE_URL)
    try:
        # Verification : la table doit etre vide avant le premier import
        with engine.connect() as conn:
            resultat = conn.execute(text("SELECT COUNT(*) FROM apprentissage_canada"))
            nb_existant = resultat.scalar()

        if nb_existant > 0:
            print(f"ATTENTION : la table contient deja {nb_existant} lignes.")
            reponse = input("Voulez-vous vraiment ajouter les 4750 nouvelles lignes ? (oui/non) : ")
            if reponse.lower() != 'oui':
                print("Import annule.")
                return

        df.to_sql(
            'apprentissage_canada',
            engine,
            if_exists='append',   # ajoute sans supprimer la structure de table
            index=False,
            method='multi',       # insertion par lots (plus rapide)
            chunksize=500
        )
        print(f"{len(df)} dossiers importes avec succes dans apprentissage_canada.")

    finally:
        engine.dispose()


def main():
    print("Chargement du dataset historique...")
    df = pd.read_csv(CHEMIN_CSV, keep_default_na=False, na_values=[])

    print(f"{len(df)} lignes chargees. Preparation des colonnes administratives...")
    df_pret = preparer_donnees_pour_import(df)

    # Verification finale des colonnes attendues par la table SQL
    colonnes_attendues = [
        'id_client', 'nom', 'prenom', 'numero_document', 'date_naissance',
        'email', 'telephone', 'ville_residence', 'type_contrat',
        'frais_encaisses', 'restes_a_payer', 'phase_traitement',
        'identifiant_conseiller', 'notes',
        'application_year', 'age', 'sex', 'marital_status', 'country_of_origin',
        'education_level', 'eca_obtained', 'english_test',
        'clb_speaking_english', 'clb_listening_english', 'clb_reading_english', 'clb_writing_english',
        'french_test', 'nclc_speaking_french', 'nclc_listening_french',
        'nclc_reading_french', 'nclc_writing_french',
        'years_foreign_experience', 'years_canadian_experience', 'sector', 'teer_category',
        'job_offer_canada', 'job_offer_teer', 'provincial_nomination', 'studied_in_canada',
        'family_in_canada', 'funds_available_cad', 'dependants', 'medical_exam_ok',
        'criminal_record', 'inadmissibility', 'program', 'crs_score', 'visa_decision'
    ]
    manquantes = set(colonnes_attendues) - set(df_pret.columns)
    if manquantes:
        raise ValueError(f"Colonnes manquantes avant import : {manquantes}")

    df_pret = df_pret[colonnes_attendues]  # on aligne l'ordre exact

    print("Import vers Neon PostgreSQL en cours...")
    importer_dans_neon(df_pret)


if __name__ == '__main__':
    main()
