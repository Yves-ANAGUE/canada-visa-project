# HI Consulting Immigration – Système prédictif de visa Canada

## Description
Application web de prédiction de décision de visa (Entrée Express) utilisant le Machine Learning. Elle aide les conseillers en immigration à évaluer les dossiers, générer des diagnostics IA et simuler des optimisations.

## Fonctionnalités
- Authentification des conseillers
- Création et suivi de dossiers clients (saisie progressive des critères IRCC)
- Prédiction (Accepté/Refusé) avec probabilité et niveau de confiance
- Diagnostic IA personnalisé via OpenRouter
- Simulateur d’optimisation prescriptive (leviers d’amélioration)
- Export PDF et envoi par email du rapport complet
- Tableau de bord analytique (importance des features, taux d’acceptation, etc.)
- Administration des agents et réentraînement automatique du modèle (GitHub Actions)

## Architecture
- **Frontend** : Flet (Python) – interface responsive
- **Backend** : FastAPI (Python) avec Uvicorn
- **Base de données** : PostgreSQL (Neon.tech)
- **Modèle ML** : GradientBoosting (scikit-learn), entraîné mensuellement
- **Hébergement** : Render (frontend et backend)
- **Intelligence IA** : OpenRouter (LLM)

## Installation et déploiement

### Prérequis
- Python 3.11+
- Compte Neon.tech (base PostgreSQL)
- Compte Render (hébergement)
- Clé API OpenRouter
- Compte Gmail avec mot de passe d’application (pour les emails)

### Variables d’environnement (Render)
- `NEON_DATABASE_URL` : URL de connexion PostgreSQL
- `OPENROUTER_API_KEY` : clé API OpenRouter
- `GMAIL_ADDRESS` : adresse Gmail expéditrice
- `GMAIL_APP_PASSWORD` : mot de passe application Gmail
- `SEUIL_MIN_QUALITE_PRECISION` (optionnel) : seuil de qualité pour le réentraînement

### Lancement local
```bash
# Backend
pip install -r backend/requirements.txt
uvicorn backend.main_api:app --reload --port 8000

# Frontend (dans un autre terminal)
pip install -r frontend/requirements.txt
python frontend/main.py
```

### Déploiement sur Render

    Backend : Web Service, commande uvicorn backend.main_api:app --host 0.0.0.0 --port 10000

    Frontend : Web Service, commande cd frontend && python main.py

### Utilisation

    Connectez‑vous avec les identifiants d’un conseiller.

    Créez un dossier, saisissez les informations du candidat.

    Visualisez la prédiction, le diagnostic IA et les scénarios d’optimisation.

    Générez le PDF ou envoyez‑le par email.

### Maintenance

    Le modèle est réentraîné automatiquement le 1er de chaque mois via GitHub Actions.

    Un réentraînement manuel peut être déclenché depuis l’interface administrateur.

### Contribuer

Les contributions sont les bienvenues. Merci de respecter PEP8.
### Licence

Propriétaire – HI Consulting Immigration.