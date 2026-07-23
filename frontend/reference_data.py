# reference_data.py
# Listes fermees pour tous les menus deroulants (saisie sans erreur. Doit rester synchronise avec backend/utils.py (memes valeurs techniques IRCC).


OPTIONS_SEXE = [("Male", "Homme (Male)"), ("Female", "Femme (Female)")]

OPTIONS_STATUT_MATRIMONIAL = [
    ("Single", "Celibataire (Single)"),
    ("Married", "Marie(e) (Married)"),
    ("Divorced", "Divorce(e) (Divorced)"),
    ("Widowed", "Veuf/Veuve (Widowed)"),
    ("Common-Law", "Union de fait (Common-Law)"),
]

OPTIONS_EDUCATION = [
    ("Less than secondary", "Inferieur au secondaire"),
    ("Secondary diploma", "Diplome secondaire"),
    ("One-year post-secondary", "Post-secondaire 1 an"),
    ("Two-year post-secondary", "Post-secondaire 2 ans"),
    ("Bachelor degree", "Licence (Bachelor)"),
    ("Master degree", "Master"),
    ("PhD", "Doctorat (PhD)"),
]

OPTIONS_OUI_NON = [("Yes", "Oui"), ("No", "Non")]

OPTIONS_TEST_ANGLAIS = [
    ("IELTS", "IELTS"), ("CELPIP", "CELPIP"), ("PTE", "PTE"), ("None", "Aucun test"),
]

OPTIONS_TEST_FRANCAIS = [
    ("TEF Canada", "TEF Canada"), ("TCF Canada", "TCF Canada"), ("None", "Aucun test"),
]

OPTIONS_SECTEUR = [
    ("STEM", "Sciences, technologies, ingenierie, maths"),
    ("Healthcare", "Sante"),
    ("Transport", "Transport"),
    ("Trades", "Metiers specialises"),
    ("Education", "Education"),
    ("Business", "Affaires"),
    ("Agriculture", "Agriculture"),
    ("Other", "Autre"),
]

OPTIONS_TEER = [
    ("TEER 0", "TEER 0 - Gestion"),
    ("TEER 1", "TEER 1 - Universitaire"),
    ("TEER 2", "TEER 2 - Collegial/apprentissage 2+ ans"),
    ("TEER 3", "TEER 3 - Collegial/apprentissage <2 ans"),
    ("TEER 4", "TEER 4 - Diplome secondaire"),
    ("TEER 5", "TEER 5 - Sans formation formelle"),
    ("None", "Sans objet"),
]

OPTIONS_CASIER = [
    ("None", "Aucun antecedent"), ("Minor", "Antecedent mineur"), ("Major", "Antecedent majeur"),
]

OPTIONS_PROGRAMME = [
    ("FSWP", "Travailleurs qualifies federal (FSWP)"),
    ("FSTP", "Metiers specialises federal (FSTP)"),
    ("CEC", "Categorie de l'experience canadienne (CEC)"),
    ("PNP", "Programme des candidats des provinces (PNP)"),
]

OPTIONS_PHASE_TRAITEMENT = [
    ("File Opened", "Dossier ouvert"),
    ("Awaiting Language Test", "En attente de test de langue"),
    ("Submitted in Pool", "Soumis dans le bassin"),
    ("Biometrics Requested", "Convocation biometrique"),
    ("Closed", "Cloture"),
]

OPTIONS_DECISION = [("Accepted", "Accepte"), ("Refused", "Refuse")]


OPTIONS_PAYS = sorted([
    "Afghanistan", "Afrique du Sud", "Albanie", "Algerie", "Allemagne", "Andorre",
    "Angola", "Antigua-et-Barbuda", "Arabie saoudite", "Argentine", "Armenie",
    "Australie", "Autriche", "Azerbaidjan", "Bahamas", "Bahrein", "Bangladesh",
    "Barbade", "Belgique", "Belize", "Benin", "Bhoutan", "Bielorussie", "Birmanie",
    "Bolivie", "Bosnie-Herzegovine", "Botswana", "Bresil", "Brunei", "Bulgarie",
    "Burkina Faso", "Burundi", "Cambodge", "Cameroun", "Canada", "Cap-Vert",
    "Chili", "Chine", "Chypre", "Colombie", "Comores", "Congo-Brazzaville",
    "Coree du Nord", "Coree du Sud", "Costa Rica", "Cote d'Ivoire", "Croatie",
    "Cuba", "Danemark", "Djibouti", "Dominique", "Egypte", "Emirats arabes unis",
    "Equateur", "Erythree", "Espagne", "Estonie", "Eswatini", "Etats-Unis",
    "Ethiopie", "Fidji", "Finlande", "France", "Gabon", "Gambie", "Georgie",
    "Ghana", "Grece", "Grenade", "Guatemala", "Guinee", "Guinee equatoriale",
    "Guinee-Bissau", "Guyana", "Haiti", "Honduras", "Hongrie", "Inde",
    "Indonesie", "Irak", "Iran", "Irlande", "Islande", "Israel", "Italie",
    "Jamaique", "Japon", "Jordanie", "Kazakhstan", "Kenya", "Kirghizistan",
    "Kiribati", "Koweit", "Laos", "Lesotho", "Lettonie", "Liban", "Liberia",
    "Libye", "Liechtenstein", "Lituanie", "Luxembourg", "Macedoine du Nord",
    "Madagascar", "Malaisie", "Malawi", "Maldives", "Mali", "Malte", "Maroc",
    "Marshall (iles)", "Maurice", "Mauritanie", "Mexique", "Micronesie",
    "Moldavie", "Monaco", "Mongolie", "Montenegro", "Mozambique", "Namibie",
    "Nauru", "Nepal", "Nicaragua", "Niger", "Nigeria", "Norvege",
    "Nouvelle-Zelande", "Oman", "Ouganda", "Ouzbekistan", "Pakistan", "Palaos",
    "Palestine", "Panama", "Papouasie-Nouvelle-Guinee", "Paraguay", "Pays-Bas",
    "Perou", "Philippines", "Pologne", "Portugal", "Qatar",
    "Republique centrafricaine", "Republique democratique du Congo",
    "Republique dominicaine", "Republique tcheque", "Roumanie", "Royaume-Uni",
    "Russie", "Rwanda", "Saint-Christophe-et-Nieves", "Saint-Marin",
    "Saint-Vincent-et-les-Grenadines", "Sainte-Lucie", "Salomon (iles)",
    "Salvador", "Samoa", "Sao Tome-et-Principe", "Senegal", "Serbie",
    "Seychelles", "Sierra Leone", "Singapour", "Slovaquie", "Slovenie",
    "Somalie", "Soudan", "Soudan du Sud", "Sri Lanka", "Suede", "Suisse",
    "Suriname", "Syrie", "Tadjikistan", "Tanzanie", "Tchad", "Thailande",
    "Timor oriental", "Togo", "Tonga", "Trinite-et-Tobago", "Tunisie",
    "Turkmenistan", "Turquie", "Tuvalu", "Ukraine", "Uruguay", "Vanuatu",
    "Vatican", "Venezuela", "Vietnam", "Yemen", "Zambie", "Zimbabwe"
])


from datetime import date

OPTIONS_CLB_NCLC = [str(n) for n in range(0, 13)]   # 0 a 12 inclus (echelle officielle)

# Dynamique : ne necessite plus jamais de mise a jour manuelle du code
# quand les annees passent (contrairement a une borne figee comme 2030)
_ANNEE_COURANTE = date.today().year
OPTIONS_ANNEE = [str(a) for a in range(2015, _ANNEE_COURANTE + 5)]

# A AJOUTER dans reference_data.py

OPTION_VIDE = ("", "-- Aucun filtre --")