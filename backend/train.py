# train.py - version avec comparaison de plusieurs modeles

import os
import logging
import json
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, TargetEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from backend.utils import (
    FUNDS_BY_YEAR, EXTRA_FUNDS_PER_DEPENDANT, FRANCOPHONE_COUNTRIES,
    COLONNES_BRUTES_ATTENDUES
)

load_dotenv()

logging.basicConfig(
    filename='train_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('train_canada')

DATABASE_URL = os.environ['NEON_DATABASE_URL']


# COLONNES POUR LE PREPROCESSING

NUMERICAL_COLS = [
    'application_year', 'age', 'clb_speaking_english', 'clb_listening_english',
    'clb_reading_english', 'clb_writing_english', 'nclc_speaking_french',
    'nclc_listening_french', 'nclc_reading_french', 'nclc_writing_french',
    'years_foreign_experience', 'years_canadian_experience',
    'funds_available_cad', 'dependants',
    'clb_english_min', 'clb_english_mean', 'nclc_french_min',
    'nclc_french_mean', 'ratio_fonds', 'experience_totale'
]

LOW_CARDINALITY_COLS = [
    'sex', 'marital_status', 'education_level', 'english_test', 'french_test',
    'sector', 'teer_category', 'job_offer_canada', 'job_offer_teer',
    'provincial_nomination', 'studied_in_canada', 'family_in_canada',
    'medical_exam_ok', 'criminal_record', 'inadmissibility', 'eca_obtained',
    'program', 'is_francophone_country'
]

HIGH_CARDINALITY_COLS = ['country_of_origin']

SMOTE_PARAMS = {'sampling_strategy': 0.5, 'k_neighbors': 3, 'random_state': 42}


# GRILLES DE RECHERCHE PAR MODELE

MODELS_CONFIG = {
    'LogisticRegression': {
        'model': LogisticRegression(max_iter=5000, random_state=42),
        'params': {
            'classifier__C': [0.01, 0.1, 1, 10],
            'classifier__penalty': ['l2'],
            'classifier__solver': ['lbfgs']
        }
    },
    'RandomForest': {
        'model': RandomForestClassifier(random_state=42),
        'params': {
            'classifier__n_estimators': [100, 200],
            'classifier__max_depth': [3, 5, 7],
            'classifier__min_samples_split': [10, 20],
            'classifier__min_samples_leaf': [5, 10],
            'classifier__max_features': ['sqrt', 0.5]
        }
    },
    'GradientBoosting': {
        'model': GradientBoostingClassifier(random_state=42),
        'params': {
            'classifier__n_estimators': [100, 150, 200, 300],
            'classifier__learning_rate': [0.03, 0.05, 0.08, 0.1],
            'classifier__max_depth': [3, 4, 5, 6],
            'classifier__subsample': [0.7, 0.8, 0.9],
            'classifier__min_samples_leaf': [5, 10, 15]
        }
    },
    'XGBoost': {
        'model': XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False),
        'params': {
            'classifier__n_estimators': [100, 150, 200, 300],
            'classifier__max_depth': [3, 4, 5, 6],
            'classifier__learning_rate': [0.03, 0.05, 0.08, 0.1],
            'classifier__subsample': [0.7, 0.8, 0.9],
            'classifier__colsample_bytree': [0.6, 0.7, 0.8],
            'classifier__min_child_weight': [1, 3, 5],
            'classifier__reg_alpha': [0, 0.1, 0.5],
            'classifier__reg_lambda': [1, 2, 5]
        }
    },
    'SVC': {
        'model': SVC(probability=True, random_state=42),
        'params': {
            'classifier__C': [0.01, 0.1, 1],
            'classifier__kernel': ['rbf'],
            'classifier__gamma': ['scale', 0.01]
        }
    },
    'KNN': {
        'model': KNeighborsClassifier(),
        'params': {
            'classifier__n_neighbors': [15, 25, 35],
            'classifier__weights': ['uniform', 'distance']
        }
    }
}


# CHARGEMENT DES DONNEES

def charger_donnees_apprentissage() -> pd.DataFrame:
    logger.info("Connexion a Neon PostgreSQL...")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)
    try:
        df = pd.read_sql(
            "SELECT * FROM apprentissage_canada WHERE visa_decision IS NOT NULL",
            engine
        )
    finally:
        engine.dispose()
    logger.info(f"{len(df)} dossiers historiques charges.")
    return df


# FEATURE ENGINEERING

def appliquer_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df['clb_english_min'] = df[['clb_speaking_english','clb_listening_english',
                                  'clb_reading_english','clb_writing_english']].min(axis=1)
    df['clb_english_mean'] = df[['clb_speaking_english','clb_listening_english',
                                  'clb_reading_english','clb_writing_english']].mean(axis=1)
    df['nclc_french_min'] = df[['nclc_speaking_french','nclc_listening_french',
                                  'nclc_reading_french','nclc_writing_french']].min(axis=1)
    df['nclc_french_mean'] = df[['nclc_speaking_french','nclc_listening_french',
                                  'nclc_reading_french','nclc_writing_french']].mean(axis=1)

    df['fonds_minimum_requis'] = (
        df['application_year'].map(FUNDS_BY_YEAR).fillna(15263) +
        df['dependants'].map(EXTRA_FUNDS_PER_DEPENDANT).fillna(6500)
    )
    df['ratio_fonds'] = df['funds_available_cad'] / df['fonds_minimum_requis']

    df['is_francophone_country'] = df['country_of_origin'].isin(FRANCOPHONE_COUNTRIES).astype(int)
    df['experience_totale'] = df['years_foreign_experience'] + df['years_canadian_experience']

    return df


# PREPROCESSOR

def construire_preprocessor() -> ColumnTransformer:
    numerical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    low_card_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='if_binary', handle_unknown='ignore'))
    ])
    high_card_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('target_enc', TargetEncoder(random_state=42))
    ])

    return ColumnTransformer([
        ('num',       numerical_pipeline, NUMERICAL_COLS),
        ('low_card',  low_card_pipeline,  LOW_CARDINALITY_COLS),
        ('high_card', high_card_pipeline, HIGH_CARDINALITY_COLS)
    ])


# ENTRAINEMENT DE TOUS LES MODELES ET COMPARAISON

def entrainer_et_comparer_modeles(X_train, y_train, X_test, y_test, preprocessor):
    """
    Entraine tous les modeles avec RandomizedSearchCV et retourne
    le meilleur modele avec ses metriques.
    """
    results = []
    fitted_models = {}
    
    for nom_modele, config in MODELS_CONFIG.items():
        logger.info(f"Entrainement de {nom_modele}...")
        
        pipeline = ImbPipeline([
            ('preprocessor', preprocessor),
            ('smote', SMOTE(**SMOTE_PARAMS)),
            ('classifier', config['model'])
        ])
        
        random_search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=config['params'],
            n_iter=30,
            scoring='precision',
            cv=5,
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        
        random_search.fit(X_train, y_train)
        
        y_pred = random_search.predict(X_test)
        y_proba = random_search.predict_proba(X_test)[:, 1]
        
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        metrics = {
            'modele': nom_modele,
            'meilleurs_params': random_search.best_params_,
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'accuracy': accuracy_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_proba),
            'n_train': len(X_train),  # ← AJOUTER CETTE LIGNE
            'n_test': len(X_test)     # ← AJOUTER CETTE LIGNE (optionnel)
        }
        
        results.append(metrics)
        fitted_models[nom_modele] = random_search.best_estimator_
        
        logger.info(f"  {nom_modele} - Precision: {metrics['precision']:.4f}, F1: {metrics['f1']:.4f}")
    
    
    # SELECTION DU MEILLEUR MODELE
    
    results_df = pd.DataFrame(results)
    
    candidats = results_df[results_df['precision'] >= 0.65]
    
    if candidats.empty:
        logger.warning("Aucun modele n'atteint Precision >= 0.65, on prend le meilleur F1")
        meilleur = results_df.loc[results_df['f1'].idxmax()]
    else:
        meilleur = candidats.loc[candidats['f1'].idxmax()]
    
    nom_meilleur = meilleur['modele']
    meilleur_modele = fitted_models[nom_meilleur]
    meilleurs_params = meilleur['meilleurs_params']
    
    logger.info(f"MODELE FINAL RETENU : {nom_meilleur}")
    logger.info(f"  Precision: {meilleur['precision']:.4f}")
    logger.info(f"  Recall: {meilleur['recall']:.4f}")
    logger.info(f"  F1: {meilleur['f1']:.4f}")
    logger.info(f"  ROC-AUC: {meilleur['roc_auc']:.4f}")
    logger.info(f"  Meilleurs parametres: {meilleurs_params}")
    logger.info(f"  Nombre dossiers train: {meilleur.get('n_train', 0)}")  # ← AJOUTER CETTE LIGNE
    
    # Sauvegarder la comparaison des modeles
    try:
        results_df.to_csv('comparaison_modeles.csv', index=False)
        logger.info("Comparaison des modeles sauvegardee dans comparaison_modeles.csv")
    except Exception as e:
        logger.warning(f"Impossible de sauvegarder la comparaison : {e}")
    
    # Sauvegarder les meilleurs parametres
    try:
        with open('meilleurs_hyperparametres.json', 'w') as f:
            json.dump(meilleurs_params, f, indent=2)
        logger.info("Meilleurs hyperparametres sauvegardes dans meilleurs_hyperparametres.json")
    except Exception as e:
        logger.warning(f"Impossible de sauvegarder les hyperparametres : {e}")
    
    return meilleur_modele, meilleur


# SAUVEGARDE DES TOP FEATURES

def sauvegarder_top_features(pipeline):
    try:
        classifier = pipeline.named_steps['classifier']
        if hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            preprocessor = pipeline.named_steps['preprocessor']
            feature_names = preprocessor.get_feature_names_out()
            
            feature_importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            feature_importance_df['Variable_origine'] = feature_importance_df['feature'].str.replace(
                r'(low_card__|high_card__|num__)', '', regex=True
            )
            feature_importance_df.to_csv('feature_importance_finale.csv', index=False)
            
            top_features = feature_importance_df.head(10)['Variable_origine'].tolist()
            with open('top_features.json', 'w') as f:
                json.dump(top_features, f)
            
            logger.info(f"Top 10 features sauvegardees : {top_features}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des features : {e}")


# SAUVEGARDE CONDITIONNELLE

def _convertir_en_python(valeur):
    if hasattr(valeur, 'item'):
        return valeur.item()
    return valeur

def sauvegarder_si_qualite_suffisante(pipeline, meilleur, seuil_decision=0.5, declenchement='planifie'):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)
    
    with engine.connect() as conn:
        ancien = conn.execute(text("""
            SELECT precision_score FROM historique_entrainement 
            WHERE modele_valide = TRUE 
            ORDER BY precision_score DESC 
            LIMIT 1
        """)).fetchone()
        ancienne_precision = ancien[0] if ancien else 0
    
    nouvelle_precision = meilleur['precision']
    est_meilleur = nouvelle_precision > ancienne_precision
    valide = est_meilleur
    
    if valide:
        joblib.dump(pipeline, 'modele_canada.pkl')
        joblib.dump(seuil_decision, 'seuil_decision.pkl')
        logger.info(f"✅ Nouveau modèle sauvegardé : Precision {nouvelle_precision:.3f} (vs ancien {ancienne_precision:.3f})")
    else:
        logger.info(f"❌ Modèle rejeté : Precision {nouvelle_precision:.3f} (ancien meilleur : {ancienne_precision:.3f})")

    with engine.connect() as conn:
        
        # IMPORTANT : date_execution est automatiquement SET par DEFAULT
        # dans la base de données (CURRENT_TIMESTAMP)
        
        conn.execute(text("""
            INSERT INTO historique_entrainement
                (declenchement, accuracy, precision_score, recall_score, specificity_score, f1_score, roc_auc, modele_valide, nb_dossiers_train, modele_choisi)
            VALUES (:d, :a, :p, :r, :sp, :f, :auc, :v, :n, :m)
        """), {
            "d": declenchement,
            "a": float(meilleur['accuracy']),
            "p": float(meilleur['precision']),
            "r": float(meilleur['recall']),
            "sp": float(meilleur.get('specificity', 0)),
            "f": float(meilleur['f1']),
            "auc": float(meilleur['roc_auc']),
            "v": valide,
            "n": int(meilleur.get('n_train', 0)),
            "m": meilleur.get('modele', 'inconnu')
        })
        conn.commit()
    engine.dispose()
    return valide


# POINT D'ENTREE PRINCIPAL

def main(declenchement: str = 'planifie'):
    logger.info("="*60)
    logger.info(f"DEBUT DU CYCLE D'ENTRAINEMENT ({declenchement.upper()})")
    logger.info("="*60)

    try:
        df = charger_donnees_apprentissage()

        if len(df) < 100:
            logger.warning(f"Seulement {len(df)} dossiers disponibles - entrainement annule (minimum requis : 100).")
            return

        df = appliquer_feature_engineering(df)
        
        
        # PREPARATION DES DONNEES
        
        X = df.drop(columns=['visa_decision', 'crs_score'], errors='ignore')
        y = (df['visa_decision'] == 'Accepted').astype(int)
        
        strat_key = df['application_year'].astype(str) + '_' + df['visa_decision']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=strat_key
        )
        
        preprocessor = construire_preprocessor()
        
        
        # ENTRAINEMENT DE TOUS LES MODELES
        
        pipeline, meilleur = entrainer_et_comparer_modeles(
            X_train, y_train, X_test, y_test, preprocessor
        )
        
        
        # SAUVEGARDE DES FEATURES
        
        sauvegarder_top_features(pipeline)
        
        
        # SAUVEGARDE CONDITIONNELLE
        
        sauvegarder_si_qualite_suffisante(pipeline, meilleur, declenchement=declenchement)

        logger.info("Cycle d'entrainement termine avec succes.")

    except Exception as e:
        logger.error(f"ERREUR durant l'entrainement : {str(e)}", exc_info=True)


if __name__ == '__main__':
    main(declenchement='manuel_terminal')

