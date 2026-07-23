-- SCHEMA SQL - BASE DE DONNEES CANADA VISA PREDICTION

-- TABLE 3 : gestion_utilisateurs (creee en premier, referencee
--           logiquement par identifiant_conseiller, sans FK physique)

CREATE TABLE gestion_utilisateurs (
    id_agent               SERIAL PRIMARY KEY,
    identifiant_conseiller VARCHAR(20) UNIQUE NOT NULL,   -- ex: 'CONS-001'
    nom_agent              VARCHAR(100) NOT NULL,
    email_agent            VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe_hache     VARCHAR(64) NOT NULL,          -- SHA-256 = 64 caracteres hexadecimaux
    statut_compte          VARCHAR(20) DEFAULT 'Actif',   -- 'Actif' / 'Suspendu'
    date_creation          TIMESTAMP DEFAULT NOW()
);


-- FONCTION SQL REUTILISABLE : structure miroir des 2 tables de faits
-- (on la definit une fois, appliquee 2 fois via les CREATE TABLE ci-dessous)



-- TABLE 1 : apprentissage_canada (historique - dossiers clotures)

CREATE TABLE apprentissage_canada (
    -- --- 14 colonnes administratives ---
    id_client              VARCHAR(20) PRIMARY KEY,        -- ex: 'CAN-2026-001'
    nom                    VARCHAR(100),
    prenom                 VARCHAR(100),
    numero_document        VARCHAR(50),                    -- passeport ou CNI
    date_naissance         DATE,
    email                  VARCHAR(150),
    telephone              VARCHAR(30),                    -- WhatsApp
    ville_residence        VARCHAR(100),
    type_contrat           VARCHAR(50),
    frais_encaisses        NUMERIC(10,2) DEFAULT 0,
    restes_a_payer         NUMERIC(10,2) DEFAULT 0,
    phase_traitement       VARCHAR(50) DEFAULT 'Closed',    -- ici toujours Closed (historique)
    identifiant_conseiller VARCHAR(20),                     -- pas de FK physique (cf. section 4.3.2)
    notes                  TEXT,

    -- --- 34 colonnes scientifiques (33 criteres IRCC + decision) ---
    application_year          INTEGER,
    age                        INTEGER,
    sex                        VARCHAR(10),
    marital_status             VARCHAR(20),
    country_of_origin          VARCHAR(60),
    education_level            VARCHAR(40),
    eca_obtained                VARCHAR(5),
    english_test                VARCHAR(20),
    clb_speaking_english        INTEGER,
    clb_listening_english       INTEGER,
    clb_reading_english         INTEGER,
    clb_writing_english         INTEGER,
    french_test                 VARCHAR(20),
    nclc_speaking_french        INTEGER,
    nclc_listening_french       INTEGER,
    nclc_reading_french         INTEGER,
    nclc_writing_french         INTEGER,
    years_foreign_experience    INTEGER,
    years_canadian_experience   INTEGER,
    sector                      VARCHAR(30),
    teer_category                VARCHAR(10),
    job_offer_canada             VARCHAR(5),
    job_offer_teer                VARCHAR(10),
    provincial_nomination        VARCHAR(5),
    studied_in_canada            VARCHAR(5),
    family_in_canada              VARCHAR(5),
    funds_available_cad          NUMERIC(10,2),
    dependants                    INTEGER,
    medical_exam_ok               VARCHAR(5),
    criminal_record                VARCHAR(10),
    inadmissibility                 VARCHAR(5),
    program                         VARCHAR(10),
    crs_score                        INTEGER,
    visa_decision                    VARCHAR(10) NOT NULL,   -- obligatoire ici (historique clos)

    date_creation TIMESTAMP DEFAULT NOW(),
    date_maj      TIMESTAMP DEFAULT NOW()
);


-- TABLE 2 : predictions_canada (dossiers actifs - architecture
--           miroir identique, visa_decision reste NULL tant que
--           le dossier n'est pas clos)

CREATE TABLE predictions_canada (
    id_client              VARCHAR(20) PRIMARY KEY,
    nom                    VARCHAR(100),
    prenom                 VARCHAR(100),
    numero_document        VARCHAR(50),
    date_naissance         DATE,
    email                  VARCHAR(150),
    telephone              VARCHAR(30),
    ville_residence        VARCHAR(100),
    type_contrat           VARCHAR(50),
    frais_encaisses        NUMERIC(10,2) DEFAULT 0,
    restes_a_payer         NUMERIC(10,2) DEFAULT 0,
    phase_traitement       VARCHAR(50) DEFAULT 'File Opened',
    identifiant_conseiller VARCHAR(20),
    notes                  TEXT,

    application_year          INTEGER,
    age                        INTEGER,
    sex                        VARCHAR(10),
    marital_status             VARCHAR(20),
    country_of_origin          VARCHAR(60),
    education_level            VARCHAR(40),
    eca_obtained                VARCHAR(5),
    english_test                VARCHAR(20),
    clb_speaking_english        INTEGER,
    clb_listening_english       INTEGER,
    clb_reading_english         INTEGER,
    clb_writing_english         INTEGER,
    french_test                 VARCHAR(20),
    nclc_speaking_french        INTEGER,
    nclc_listening_french       INTEGER,
    nclc_reading_french         INTEGER,
    nclc_writing_french         INTEGER,
    years_foreign_experience    INTEGER,
    years_canadian_experience   INTEGER,
    sector                      VARCHAR(30),
    teer_category                VARCHAR(10),
    job_offer_canada             VARCHAR(5),
    job_offer_teer                VARCHAR(10),
    provincial_nomination        VARCHAR(5),
    studied_in_canada            VARCHAR(5),
    family_in_canada              VARCHAR(5),
    funds_available_cad          NUMERIC(10,2),
    dependants                    INTEGER,
    medical_exam_ok               VARCHAR(5),
    criminal_record                VARCHAR(10),
    inadmissibility                 VARCHAR(5),
    program                         VARCHAR(10),
    crs_score                        INTEGER,
    visa_decision                    VARCHAR(10),           -- NULL autorise (en cours)

    -- Colonnes propres a cette table (resultat du modele, pas dans l'historique)
    probabilite_acceptation_ml       NUMERIC(5,4),
    decision_predite_ml              VARCHAR(10),
    date_derniere_prediction         TIMESTAMP,

    date_creation TIMESTAMP DEFAULT NOW(),
    date_maj      TIMESTAMP DEFAULT NOW()
);


-- INDEX POUR ACCELERER LA RECHERCHE MULTICRITERE (section 5.1/5.3)

CREATE INDEX idx_pred_nom       ON predictions_canada (nom, prenom);
CREATE INDEX idx_pred_document  ON predictions_canada (numero_document);
CREATE INDEX idx_pred_telephone ON predictions_canada (telephone);
CREATE INDEX idx_pred_phase     ON predictions_canada (phase_traitement);
CREATE INDEX idx_appr_annee     ON apprentissage_canada (application_year);
