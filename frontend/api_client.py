# api_client.py
# Couche unique de communication avec le backend FastAPI. Centralise l'authentification HTTPBasic et la gestion d'erreurs.

import httpx
from theme import API_BASE_URL


class ErreurAPI(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ClientAPI:
    def __init__(self):
        self.email = None
        self.mot_de_passe = None
        self.nom_agent = None
        self.identifiant_conseiller = None
        self.est_admin = False

    def _auth(self):
        return (self.email, self.mot_de_passe)

    def _traiter_reponse(self, reponse: httpx.Response):
        if reponse.status_code >= 400:
            try:
                detail = reponse.json().get("detail", reponse.text)
            except Exception:
                detail = reponse.text
            raise ErreurAPI(str(detail), reponse.status_code)
        return reponse.json()

    def connexion(self, email: str, mot_de_passe: str) -> dict:
        with httpx.Client(timeout=15) as client:
            reponse = client.get(f"{API_BASE_URL}/moi", auth=(email, mot_de_passe))
            if reponse.status_code == 401:
                raise ErreurAPI("Identifiants invalides ou compte suspendu", 401)
            if reponse.status_code >= 500:
                raise ErreurAPI("Erreur serveur lors de la connexion", reponse.status_code)
            donnees = reponse.json()

        self.email = email
        self.mot_de_passe = mot_de_passe
        self.nom_agent = donnees.get("nom_agent")
        self.identifiant_conseiller = donnees.get("identifiant_conseiller")
        self.est_admin = bool(donnees.get("est_admin", False))
        return {"statut": "connecte"}

    def predire(self, profil: dict) -> dict:
        with httpx.Client(timeout=20) as client:
            r = client.post(f"{API_BASE_URL}/predire", json=profil, auth=self._auth())
            return self._traiter_reponse(r)

    def diagnostic(self, profil: dict) -> dict:
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{API_BASE_URL}/diagnostic", json=profil, auth=self._auth())
            return self._traiter_reponse(r)

    def simulateur(self, profil: dict) -> dict:
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{API_BASE_URL}/simulateur-optimisation", json=profil, auth=self._auth())
            return self._traiter_reponse(r)

    def creer_dossier(self, dossier: dict) -> dict:
        with httpx.Client(timeout=20) as client:
            r = client.post(f"{API_BASE_URL}/dossiers/nouveau", json=dossier, auth=self._auth())
            return self._traiter_reponse(r)

    def obtenir_dossier(self, id_client: str) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/dossiers/{id_client}", auth=self._auth())
            return self._traiter_reponse(r)

    def modifier_dossier(self, id_client: str, dossier: dict) -> dict:
        with httpx.Client(timeout=20) as client:
            r = client.put(f"{API_BASE_URL}/dossiers/{id_client}", json=dossier, auth=self._auth())
            return self._traiter_reponse(r)

    def supprimer_dossier(self, id_client: str) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.delete(f"{API_BASE_URL}/dossiers/{id_client}", auth=self._auth())
            return self._traiter_reponse(r)

    def rechercher_dossiers(self, terme: str) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/dossiers/recherche", params={"terme": terme}, auth=self._auth())
            return self._traiter_reponse(r)

    def feature_importance(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/feature-importance", auth=self._auth())
            return self._traiter_reponse(r)

    def statistiques_globales(self) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/statistiques-globales", auth=self._auth())
            return self._traiter_reponse(r)

    def telecharger_pdf_url(self, id_client: str) -> str:
        return f"{API_BASE_URL}/dossiers/{id_client}/pdf"

    def envoyer_email(self, id_client: str) -> dict:
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{API_BASE_URL}/dossiers/{id_client}/envoyer-email", auth=self._auth())
            return self._traiter_reponse(r)

    def declencher_reentrainement(self) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.post(f"{API_BASE_URL}/admin/reentrainer", auth=self._auth())
            return self._traiter_reponse(r)

    def historique_entrainement(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/admin/historique-entrainement", auth=self._auth())
            return self._traiter_reponse(r)

    def lister_agents(self, terme: str = "") -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/admin/agents", params={"terme": terme}, auth=self._auth())
            return self._traiter_reponse(r)

    def creer_agent(self, donnees: dict) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.post(f"{API_BASE_URL}/admin/agents", json=donnees, auth=self._auth())
            return self._traiter_reponse(r)

    def modifier_statut_agent(self, identifiant_conseiller: str, statut: str) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.put(
                f"{API_BASE_URL}/admin/agents/{identifiant_conseiller}/statut",
                params={"statut": statut}, auth=self._auth()
            )
            return self._traiter_reponse(r)

    def supprimer_agent(self, identifiant_conseiller: str) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.delete(f"{API_BASE_URL}/admin/agents/{identifiant_conseiller}", auth=self._auth())
            return self._traiter_reponse(r)

    
    # NOUVELLES METHODES A AJOUTER
    
    def diagnostic_complet(self, id_client: str) -> dict:
        with httpx.Client(timeout=30) as client:
            r = client.get(f"{API_BASE_URL}/dossiers/{id_client}/diagnostic-complet", auth=self._auth())
            return self._traiter_reponse(r)

    def reouvrir_dossier(self, id_client: str) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.post(f"{API_BASE_URL}/dossiers/{id_client}/reouvrir", auth=self._auth())
            return self._traiter_reponse(r)

    def modifier_agent(self, identifiant_conseiller: str, donnees: dict) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.put(f"{API_BASE_URL}/admin/agents/{identifiant_conseiller}",
                            json=donnees, auth=self._auth())
            return self._traiter_reponse(r)

    def metriques_modele(self) -> dict:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/metriques-modele", auth=self._auth())
            return self._traiter_reponse(r)

    def repartition_pays(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/repartition-pays", auth=self._auth())
            return self._traiter_reponse(r)

    def taux_par_secteur(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/taux-par-secteur", auth=self._auth())
            return self._traiter_reponse(r)

    def taux_par_education(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/taux-par-education", auth=self._auth())
            return self._traiter_reponse(r)

    def repartition_decision(self) -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/analytics/repartition-decision", auth=self._auth())
            return self._traiter_reponse(r)

    
    # CORRECTION - lister_dossiers accepte "decision"
    
    def lister_dossiers(self, terme="", programme="", pays="", phase="", decision="") -> list:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE_URL}/dossiers/liste",
                            params={
                                "terme": terme,
                                "programme": programme,
                                "pays": pays,
                                "phase": phase,
                                "decision": decision
                            },
                            auth=self._auth())
            return self._traiter_reponse(r)
            