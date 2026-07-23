# main.py
# Point d'entree Flet - routage complet de l'application.
import flet as ft
import os

import time

from datetime import date

from sqlalchemy import Engine, text

from theme import construire_theme, ROUGE_CANADA, GRIS_TEXTE, GRIS_CLAIR, BLANC, VERT_SUCCES, GRIS_MOYEN, ENTREPRISE, BLEU_GLACIER, OR_ERABLE, ORANGE_ALERTE
from reference_data import (
    OPTIONS_SEXE, OPTIONS_STATUT_MATRIMONIAL, OPTIONS_EDUCATION, OPTIONS_OUI_NON,
    OPTIONS_TEST_ANGLAIS, OPTIONS_TEST_FRANCAIS, OPTIONS_SECTEUR, OPTIONS_TEER,
    OPTIONS_CASIER, OPTIONS_PROGRAMME, OPTIONS_PHASE_TRAITEMENT, OPTIONS_DECISION,
    OPTIONS_PAYS, OPTIONS_CLB_NCLC, OPTIONS_ANNEE
)
from api_client import ClientAPI, ErreurAPI
from components import (
    barre_laterale,
    carte,
    badge_decision,
    barre_confiance,
    notification,
    barre_navigation_haut,
    superposition_chargement,
    animation_ia_reflexion,
    texte_metriques,      # ← AJOUTER
    lancer_orbe_ia,       # ← AJOUTER
)
from theme import DRAPEAU_CANADA_URL, DRAPEAU_CAMEROUN_URL



# CORRECTION dans main.py - remplace toute la logique de navigation

def main(page: ft.Page):
    page.title = "HI Consulting Immigration - Systeme Predictif Visa Canada"
    page.theme = construire_theme()
    page.bgcolor = GRIS_CLAIR
    page.padding = 0
    page.window.width = 1400
    page.window.height = 860
    page.window.min_width = 1000
    page.window.min_height = 650
    page.scroll = None

    client_api = ClientAPI()
    historique_nav = {"pile": [], "position": -1}

    def aller_vers(route: str, empiler: bool = True):
        if empiler:
            if historique_nav["position"] < len(historique_nav["pile"]) - 1:
                historique_nav["pile"] = historique_nav["pile"][:historique_nav["position"] + 1]
            if not historique_nav["pile"] or historique_nav["pile"][-1] != route:
                historique_nav["pile"].append(route)
                historique_nav["position"] = len(historique_nav["pile"]) - 1
        page.go(route)

    def retour_navigation(e=None):
        if historique_nav["position"] > 0:
            historique_nav["position"] -= 1
            page.go(historique_nav["pile"][historique_nav["position"]])
            page.update()

    def avancer_navigation(e=None):
        if historique_nav["position"] < len(historique_nav["pile"]) - 1:
            historique_nav["position"] += 1
            page.go(historique_nav["pile"][historique_nav["position"]])
            page.update()

    
    # PAGE : CONNEXION
    
    
    # CORRECTION dans main.py - page_connexion() : centrage vertical/horizontal,
    # alignement des textes, logo agrandi
    
    def page_connexion():
        champ_email = ft.TextField(label="Adresse e-mail", width=360, border_radius=12,
                                    prefix_icon=ft.icons.EMAIL_OUTLINED)
        champ_mdp = ft.TextField(label="Mot de passe", width=360, border_radius=12, password=True,
                                can_reveal_password=True, prefix_icon=ft.icons.LOCK_OUTLINE)
        texte_erreur = ft.Text("", color=ROUGE_CANADA, size=13)
        indicateur = ft.ProgressRing(width=18, height=18, visible=False)

        def se_connecter(e):
            texte_erreur.value = ""
            indicateur.visible = True
            page.update()
            try:
                client_api.connexion(champ_email.value.strip(), champ_mdp.value)
                notification(page, f"Connexion reussie - bienvenue {client_api.nom_agent or ''}.")
                historique_nav["pile"] = ["/dashboard"]
                historique_nav["position"] = 0
                page.go("/dashboard")  # ou aller_vers("/dashboard") si vous voulez
            except ErreurAPI as err:
                texte_erreur.value = err.message
            except Exception:
                texte_erreur.value = "Impossible de contacter le serveur. Verifiez votre connexion."
            finally:
                indicateur.visible = False
                page.update()

        
        panneau_gauche = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="logo_HICI.jpg", width=140, height=140, fit=ft.ImageFit.CONTAIN, border_radius=20),
                    ft.Container(height=16),
                    ft.Text(ENTREPRISE["nom"], size=24, weight=ft.FontWeight.BOLD, color=BLANC,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(ENTREPRISE["slogan"], size=15, color="#FFD8DC", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.Text(ENTREPRISE["mission"], size=13, color="#FFEBEC", width=340,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    ft.Row([
                        ft.Image(src=DRAPEAU_CANADA_URL, width=38, height=25, border_radius=4),
                        ft.Image(src=DRAPEAU_CAMEROUN_URL, width=38, height=25, border_radius=4),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=460, gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                                    colors=[ROUGE_CANADA, "#7A0015"]),
            alignment=ft.alignment.center, expand=True,
        )

        panneau_droit = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Connexion agent", size=26, weight=ft.FontWeight.BOLD, color=GRIS_TEXTE,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Systeme predictif de decision visa - Entree Express", size=13, color=GRIS_MOYEN,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=30),
                    champ_email, champ_mdp,
                    ft.Container(height=8), texte_erreur, ft.Container(height=12),
                    ft.ElevatedButton(
                        content=ft.Row([indicateur, ft.Text("Se connecter", weight=ft.FontWeight.BOLD)],
                                        alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        width=360, height=48, bgcolor=ROUGE_CANADA, color=BLANC, on_click=se_connecter,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True, alignment=ft.alignment.center, bgcolor=BLANC,
        )

        return ft.View("/", controls=[ft.Row([panneau_gauche, panneau_droit], expand=True)], padding=0)

    
    # LAYOUT COMMUN (sidebar + contenu) pour les pages authentifiees
    
    
    
    
# CORRECTION dans main.py - mise_en_page() passe desormais
# aller_vers, retour_navigation, avancer_navigation

    def mise_en_page(route_active: str, titre: str, construire_contenu) -> ft.View:
        corps = ft.Column([superposition_chargement()], expand=True)
        conteneur_page = ft.Column(
            [barre_navigation_haut(historique_nav, retour_navigation, avancer_navigation, titre),
            ft.Container(height=16), corps],
            scroll=ft.ScrollMode.AUTO, expand=True,
        )
        vue = ft.View(route_active, controls=[ft.Row([
            barre_laterale(page, client_api, route_active, aller_vers),
            ft.Container(content=conteneur_page, expand=True, padding=28, bgcolor=GRIS_CLAIR),
        ], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH, spacing=0)],
            padding=0, spacing=0, scroll=None)

        def charger():
            try:
                corps.controls = [construire_contenu()]
            except ErreurAPI as err:
                corps.controls = [ft.Text(f"Erreur : {err.message}", color=ROUGE_CANADA)]
            except Exception as err:
                corps.controls = [ft.Text(f"Erreur inattendue : {err}", color=ROUGE_CANADA)]
            try:
                page.update()
            except Exception:
                pass

        import threading
        threading.Thread(target=charger, daemon=True).start()
        return vue
    
    # PAGE : TABLEAU DE BORD (graphiques natifs animes)
    
    
    # REMPLACE entierement le construire() de page_dashboard()
    
    def page_dashboard():
        def construire_graphique_importance(donnees: list) -> ft.Column:
            couleurs_cycle = [ROUGE_CANADA, "#111318", "#8A8F98", "#E08A00", "#1E8E5A"]
            groupes = []
            legende = []

            for i, item in enumerate(donnees):
                couleur = couleurs_cycle[i % len(couleurs_cycle)]
                groupes.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=item["importance"] * 100,
                                width=16,
                                color=couleur,
                                border_radius=4,
                                tooltip=f"{item['variable']} : {item['importance'] * 100:.1f}%",
                            )
                        ],
                    )
                )
                legende.append(
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=couleur, border_radius=3),
                        ft.Text(item["variable"], size=11, expand=True),
                        ft.Text(f"{item['importance'] * 100:.1f}%", size=11, weight=ft.FontWeight.BOLD),
                    ], spacing=8)
                )

            graphique = ft.BarChart(
                bar_groups=groupes,
                border=ft.border.all(1, "#E5E7EB"),
                left_axis=ft.ChartAxis(labels_size=40),
                bottom_axis=ft.ChartAxis(labels_size=0),
                horizontal_grid_lines=ft.ChartGridLines(color="#EDEEF1", width=1),
                animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
                height=280,
            )

            return ft.Column([graphique, ft.Container(height=10), ft.Column(legende, spacing=6, scroll=ft.ScrollMode.AUTO, height=180)])

        def construire_courbe_taux(donnees: list) -> ft.LineChart:
            points = [
                ft.LineChartDataPoint(i, float(item["taux_acceptation"] or 0))
                for i, item in enumerate(donnees)
            ]
            return ft.LineChart(
                data_series=[
                    ft.LineChartData(
                        data_points=points,
                        stroke_width=3,
                        color=ROUGE_CANADA,
                        curved=True,
                        stroke_cap_round=True,
                        below_line_gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=["#33D80621", "#00D80621"],
                        ),
                    )
                ],
                border=ft.border.all(1, "#E5E7EB"),
                left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Taux d'acceptation (%)", size=10)),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(value=i, label=ft.Text(str(item["application_year"]), size=10))
                        for i, item in enumerate(donnees)
                    ],
                    labels_size=32,
                ),
                horizontal_grid_lines=ft.ChartGridLines(color="#EDEEF1", width=1),
                tooltip_bgcolor="#15171C",
                animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
                height=280,
            )

        def construire_camembert_programmes(donnees: list) -> ft.PieChart:
            couleurs_cycle = [ROUGE_CANADA, "#111318", "#8A8F98", "#E08A00"]
            sections = []
            total = sum(item["total"] for item in donnees) or 1
            for i, item in enumerate(donnees):
                pourcentage = item["total"] / total * 100
                sections.append(
                    ft.PieChartSection(
                        value=item["total"],
                        title=f"{item['program']}\n{pourcentage:.0f}%",
                        title_style=ft.TextStyle(size=11, color=BLANC, weight=ft.FontWeight.BOLD),
                        color=couleurs_cycle[i % len(couleurs_cycle)],
                        radius=90,
                    )
                )
            return ft.PieChart(sections=sections, sections_space=2, center_space_radius=40, height=280)

        def barres_horizontales(donnees, cle_label, cle_valeur, couleur, suffixe="%"):
            maxi = max((d[cle_valeur] or 0) for d in donnees) or 1
            lignes = []
            for d in donnees:
                valeur = float(d[cle_valeur] or 0)
                lignes.append(
                    ft.Column([
                        ft.Row([
                            ft.Text(str(d[cle_label]), size=11, expand=True),
                            ft.Text(f"{valeur:.1f}{suffixe}", size=11, weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Container(
                            height=8,
                            border_radius=4,
                            bgcolor="#EDEEF1",
                            content=ft.Container(
                                height=8,
                                width=None,
                                border_radius=4,
                                bgcolor=couleur,
                                animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
                            ),
                            padding=ft.padding.only(right=max(0, 100 - (valeur / maxi * 100))),
                            alignment=ft.alignment.center_left,
                        ),
                    ], spacing=3)
                )
            return ft.Column(lignes, spacing=10)

        def texte_metriques(m: dict) -> str:
            if not m or m.get('accuracy') is None:
                return "Metriques du modele non disponibles."
            return (f"Accuracy {float(m['accuracy'])*100:.1f}% - Precision {float(m['precision_score'])*100:.1f}% - "
                    f"Recall {float(m['recall_score'])*100:.1f}% - Specificity {float(m.get('specificity_score') or 0)*100:.1f}% - "
                    f"F1-Score {float(m['f1_score'])*100:.1f}% - ROC-AUC {float(m['roc_auc']):.4f}")

        def construire():
            
            # CHARGEMENT DES DONNEES
            
            importance = client_api.feature_importance()
            stats = client_api.statistiques_globales()
            metriques = client_api.metriques_modele()
            pays_data = client_api.repartition_pays()
            secteur_data = client_api.taux_par_secteur()
            education_data = client_api.taux_par_education()
            decision_data = client_api.repartition_decision()

            repartition = stats["repartition_par_programme"]
            total_dossiers = sum(item["total"] for item in repartition)
            taux_annees = [float(item["taux_acceptation"] or 0) for item in stats["taux_acceptation_par_annee"]]
            taux_moyen = sum(taux_annees) / len(taux_annees) if taux_annees else 0

            def carte_kpi(titre, valeur, icone, couleur):
                return carte(
                    ft.Column([
                        ft.Row([ft.Icon(icone, color=couleur, size=22), ft.Text(titre, size=12, color=GRIS_MOYEN)], spacing=8),
                        ft.Text(valeur, size=22, weight=ft.FontWeight.BOLD, color=GRIS_TEXTE),
                    ], spacing=6),
                    largeur=230,
                    padding_val=16
                )

            ligne_kpi = ft.Row([
                carte_kpi("Dossiers analyses", f"{total_dossiers:,}".replace(",", " "), ft.icons.FOLDER_COPY_OUTLINED, ROUGE_CANADA),
                carte_kpi("Taux d'acceptation moyen", f"{taux_moyen:.1f}%", ft.icons.TRENDING_UP, VERT_SUCCES),
                carte_kpi("Accuracy du modele", f"{float(metriques['accuracy'])*100:.1f}%" if metriques.get('accuracy') else "-", ft.icons.INSIGHTS, BLEU_GLACIER),
                carte_kpi("F1-Score du modele", f"{float(metriques['f1_score'])*100:.1f}%" if metriques.get('f1_score') else "-", ft.icons.ANALYTICS_OUTLINED, OR_ERABLE),
            ], wrap=True, spacing=16)

            
            # METRIQUES AVEC DATE DE DERNIERE MISE A JOUR
            
            date_execution = metriques.get('date_execution', '')
            if date_execution:
                try:
                    from datetime import datetime
                    if isinstance(date_execution, str):
                        dt = datetime.fromisoformat(date_execution.replace('Z', '+00:00'))
                    else:
                        dt = date_execution
                    date_formatee = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    date_formatee = str(date_execution)[:16]
            else:
                date_formatee = "inconnue"

            return ft.ResponsiveRow([
                ft.Column([ligne_kpi], col=12),
                ft.Column([ft.Container(height=20)], col=12),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Evolution du taux d'acceptation par annee", size=15, weight=ft.FontWeight.BOLD),
                        construire_courbe_taux(stats["taux_acceptation_par_annee"])
                    ]))
                ], col=12),
                ft.Column([ft.Container(height=20)], col=12),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Facteurs les plus influents du modele", size=15, weight=ft.FontWeight.BOLD),
                        construire_graphique_importance(importance)
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Repartition par programme", size=15, weight=ft.FontWeight.BOLD),
                        construire_camembert_programmes(repartition)
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([ft.Container(height=20)], col=12),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Top 10 pays d'origine (historique)", size=15, weight=ft.FontWeight.BOLD),
                        barres_horizontales(pays_data, "country_of_origin", "total", ROUGE_CANADA, "")
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Taux d'acceptation par secteur", size=15, weight=ft.FontWeight.BOLD),
                        barres_horizontales(secteur_data, "sector", "taux", VERT_SUCCES)
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([ft.Container(height=20)], col=12),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Taux d'acceptation par niveau d'etudes", size=15, weight=ft.FontWeight.BOLD),
                        barres_horizontales(education_data, "education_level", "taux", BLEU_GLACIER)
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    carte(ft.Column([
                        ft.Text("Repartition globale des decisions", size=15, weight=ft.FontWeight.BOLD),
                        ft.PieChart(
                            sections=[
                                ft.PieChartSection(
                                    value=d["total"],
                                    title=f"{d['visa_decision']}\n{d['total']}",
                                    title_style=ft.TextStyle(size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                    color=VERT_SUCCES if d["visa_decision"] == "Accepted" else ROUGE_CANADA,
                                    radius=90
                                )
                                for d in decision_data
                            ],
                            sections_space=2,
                            center_space_radius=40,
                            height=260,
                        )
                    ]))
                ], col={"sm": 12, "md": 6}),
                ft.Column([ft.Container(height=20)], col=12),
                ft.Column([
                    carte(ft.Column([
                        ft.Row([
                            ft.Text("Metriques et performances actuelles du modele", size=15, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.REFRESH,
                                icon_size=20,
                                tooltip="Rafraichir les metriques",
                                on_click=lambda e: page.go("/dashboard")
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(texte_metriques(metriques), size=13, color=GRIS_MOYEN),
                        ft.Text(
                            f"Derniere mise a jour : {date_formatee}",
                            size=11,
                            color=GRIS_MOYEN,
                            italic=True
                        ),
                    ]))
                ], col=12),
            ], columns=12)

        return mise_en_page("/dashboard", "Tableau de bord analytique", construire)

    

    # formulaire par onglets, tout en menus deroulants - aucune saisie libre pour les criteres IRCC
    
    def dropdown(label, options, valeur=None, width=280):
        """
        Crée un dropdown avec gestion correcte des clés vides.
        options : liste de tuples (key, text) ou liste de strings
        """
        if isinstance(options[0], tuple):
            options_list = [ft.dropdown.Option(key=str(k), text=v) for k, v in options]
        else:
            options_list = [ft.dropdown.Option(key=str(o), text=o) for o in options]
        
        return ft.Dropdown(
            label=label, 
            width=width, 
            border_radius=10, 
            value=str(valeur) if valeur is not None else None,
            options=options_list,
        )

    
    # REMPLACE entierement page_nouveau_dossier() dans main.py
    
    def page_nouveau_dossier():
        def construire():
            id_dossier_courant = {"valeur": None}

            nom_f = ft.TextField(label="Nom", width=270)
            prenom_f = ft.TextField(label="Prenom", width=270)
            numero_doc_f = ft.TextField(label="Numero passeport / CNI", width=270)
            date_naissance_f = ft.TextField(label="Date de naissance (AAAA-MM-JJ)", width=270, hint_text="1998-03-15")
            age_f = ft.TextField(label="Age (calcule auto si date fournie)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
            email_f = ft.TextField(label="E-mail", width=270)
            telephone_f = ft.TextField(label="Telephone / WhatsApp", width=270)
            ville_f = ft.TextField(label="Ville de residence", width=270)
            type_contrat_f = ft.TextField(label="Type de contrat", width=270)
            frais_encaisses_f = ft.TextField(label="Frais encaisses (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER, value="0")
            restes_a_payer_f = ft.TextField(label="Restes a payer (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER, value="0")
            identifiant_conseiller_f = ft.TextField(label="Conseiller en charge", width=200,
                                                    value=getattr(client_api, "identifiant_conseiller", "") or "", disabled=True)
            notes_f = ft.TextField(label="Notes", width=560, multiline=True, min_lines=2, max_lines=4)

            annee_f = dropdown("Annee de la demande", OPTIONS_ANNEE, "2026")
            sexe_f = dropdown("Sexe", OPTIONS_SEXE)
            statut_f = dropdown("Statut matrimonial", OPTIONS_STATUT_MATRIMONIAL)
            pays_f = dropdown("Pays d'origine", OPTIONS_PAYS)
            dependants_f = dropdown("Personnes a charge", [str(n) for n in range(0, 8)], "0")

            statut_general_f = dropdown("Statut du dossier (table cible)", [
                ("en_cours", "Dossier en cours -> predictions_canada"),
                ("termine", "Dossier historique termine -> apprentissage_canada")
            ], "en_cours")
            phase_traitement_f = dropdown("Phase de traitement", OPTIONS_PHASE_TRAITEMENT, "File Opened")
            decision_finale_f = dropdown("Decision finale du visa", OPTIONS_DECISION)
            decision_finale_f.visible = False
            crs_score_f = ft.TextField(label="Score CRS (optionnel, informatif)", width=200, keyboard_type=ft.KeyboardType.NUMBER)

            def on_change_statut(e):
                termine = statut_general_f.value == "termine"
                decision_finale_f.visible = termine
                phase_traitement_f.disabled = termine
                if termine:
                    phase_traitement_f.value = "Closed"
                page.update()
            statut_general_f.on_change = on_change_statut

            education_f = dropdown("Niveau d'etudes", OPTIONS_EDUCATION)
            eca_f = dropdown("Equivalence obtenue (ECA)", OPTIONS_OUI_NON)
            etudes_canada_f = dropdown("Etudes faites au Canada", OPTIONS_OUI_NON, "No")
            test_anglais_f = dropdown("Type de test d'anglais", OPTIONS_TEST_ANGLAIS)
            clb_s_f = dropdown("CLB Expression orale", OPTIONS_CLB_NCLC)
            clb_l_f = dropdown("CLB Comprehension orale", OPTIONS_CLB_NCLC)
            clb_r_f = dropdown("CLB Comprehension ecrite", OPTIONS_CLB_NCLC)
            clb_w_f = dropdown("CLB Expression ecrite", OPTIONS_CLB_NCLC)
            test_francais_f = dropdown("Type de test de francais", OPTIONS_TEST_FRANCAIS, "None")
            nclc_s_f = dropdown("NCLC Expression orale", OPTIONS_CLB_NCLC, "0")
            nclc_l_f = dropdown("NCLC Comprehension orale", OPTIONS_CLB_NCLC, "0")
            nclc_r_f = dropdown("NCLC Comprehension ecrite", OPTIONS_CLB_NCLC, "0")
            nclc_w_f = dropdown("NCLC Expression ecrite", OPTIONS_CLB_NCLC, "0")
            exp_etranger_f = dropdown("Experience a l'etranger (annees)", [str(n) for n in range(0, 21)], "0")
            exp_canada_f = dropdown("Experience au Canada (annees)", [str(n) for n in range(0, 21)], "0")
            secteur_f = dropdown("Secteur d'activite", OPTIONS_SECTEUR)
            teer_f = dropdown("Categorie professionnelle (TEER)", OPTIONS_TEER)
            offre_emploi_f = dropdown("Offre d'emploi au Canada", OPTIONS_OUI_NON, "No")
            offre_teer_f = dropdown("Categorie TEER de l'offre", OPTIONS_TEER, "None")
            pnp_f = dropdown("Nomination provinciale (PNP)", OPTIONS_OUI_NON, "No")
            famille_canada_f = dropdown("Famille au Canada", OPTIONS_OUI_NON, "No")
            fonds_f = ft.TextField(label="Fonds disponibles (CAD)", width=270, keyboard_type=ft.KeyboardType.NUMBER)
            examen_medical_f = dropdown("Examen medical", OPTIONS_OUI_NON, "Yes")
            casier_f = dropdown("Casier judiciaire", OPTIONS_CASIER, "None")
            inadmissibilite_f = dropdown("Inadmissibilite", OPTIONS_OUI_NON, "No")
            programme_f = dropdown("Programme cible", OPTIONS_PROGRAMME)

            label_id_courant = ft.Text("", size=12, color=GRIS_MOYEN, italic=True)
            resultat_zone = ft.Column([])
            indicateur = ft.ProgressRing(width=18, height=18, visible=False)

            def valeur_ou_none(champ):
                return champ.value if champ.value not in (None, "") else None
            
            def valeur_int(champ):
                v = valeur_ou_none(champ)
                return int(v) if v is not None else None
            
            def valeur_float(champ):
                v = valeur_ou_none(champ)
                return float(v) if v is not None else None

            def construire_payload():
                return {
                    "nom": valeur_ou_none(nom_f),
                    "prenom": valeur_ou_none(prenom_f),
                    "numero_document": valeur_ou_none(numero_doc_f),
                    "date_naissance": valeur_ou_none(date_naissance_f),
                    "email": valeur_ou_none(email_f),
                    "telephone": valeur_ou_none(telephone_f),
                    "ville_residence": valeur_ou_none(ville_f),
                    "type_contrat": valeur_ou_none(type_contrat_f),
                    "frais_encaisses": valeur_float(frais_encaisses_f),
                    "restes_a_payer": valeur_float(restes_a_payer_f),
                    "notes": valeur_ou_none(notes_f),  # ← AJOUTÉ
                    "phase_traitement": "Closed" if statut_general_f.value == "termine" else phase_traitement_f.value,
                    "visa_decision": decision_finale_f.value if statut_general_f.value == "termine" else None,
                    "profil": {
                        "application_year": valeur_int(annee_f),
                        "age": valeur_int(age_f),
                        "sex": sexe_f.value,
                        "marital_status": statut_f.value,
                        "country_of_origin": pays_f.value,
                        "education_level": education_f.value,
                        "eca_obtained": eca_f.value,
                        "english_test": test_anglais_f.value,
                        "clb_speaking_english": valeur_int(clb_s_f),
                        "clb_listening_english": valeur_int(clb_l_f),
                        "clb_reading_english": valeur_int(clb_r_f),
                        "clb_writing_english": valeur_int(clb_w_f),
                        "french_test": test_francais_f.value,
                        "nclc_speaking_french": valeur_int(nclc_s_f),
                        "nclc_listening_french": valeur_int(nclc_l_f),
                        "nclc_reading_french": valeur_int(nclc_r_f),
                        "nclc_writing_french": valeur_int(nclc_w_f),
                        "years_foreign_experience": valeur_int(exp_etranger_f),
                        "years_canadian_experience": valeur_int(exp_canada_f),
                        "sector": secteur_f.value,
                        "teer_category": teer_f.value,
                        "job_offer_canada": offre_emploi_f.value,
                        "job_offer_teer": offre_teer_f.value,
                        "provincial_nomination": pnp_f.value,
                        "studied_in_canada": etudes_canada_f.value,
                        "family_in_canada": famille_canada_f.value,
                        "funds_available_cad": valeur_float(fonds_f),
                        "dependants": valeur_int(dependants_f),
                        "medical_exam_ok": examen_medical_f.value,
                        "criminal_record": casier_f.value,
                        "inadmissibility": inadmissibilite_f.value,
                        "program": programme_f.value,
                        "crs_score": valeur_int(crs_score_f),  # ← AJOUTÉ
                    }
                }

            def afficher_resultat(id_client, pred):
                if isinstance(pred, dict):
                    resultat_zone.controls = [
                        ft.Container(height=10),
                        carte(ft.Column([
                            ft.Row([
                                ft.Text(f"Dossier {id_client}", weight=ft.FontWeight.BOLD),
                                badge_decision(pred["decision_predite"])
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(
                                f"Probabilite d'acceptation : {pred['probabilite_acceptation']*100:.1f}%"
                                + (" (estimee - dossier partiel)" if pred.get('estime') else ""),
                                size=13
                            ),
                            barre_confiance(pred["niveau_confiance"]),
                        ]))
                    ]

            def enregistrer(e):
                indicateur.visible = True
                page.update()
                payload = construire_payload()
                try:
                    if id_dossier_courant["valeur"] is None:
                        reponse = client_api.creer_dossier(payload)
                        id_dossier_courant["valeur"] = reponse["id_client"]
                        label_id_courant.value = f"Dossier en cours d'edition : {reponse['id_client']}"
                        notification(page, f"Dossier {reponse['id_client']} cree avec succes.")
                        afficher_resultat(reponse["id_client"], reponse.get("prediction"))
                    else:
                        reponse = client_api.modifier_dossier(id_dossier_courant["valeur"], payload)
                        notification(page, f"Dossier {id_dossier_courant['valeur']} mis a jour.")
                        afficher_resultat(id_dossier_courant["valeur"], reponse.get("prediction"))
                except ErreurAPI as err:
                    notification(page, f"Erreur : {err.message}", succes=False)
                finally:
                    indicateur.visible = False
                    page.update()

            def nouveau_formulaire(e):
                id_dossier_courant["valeur"] = None
                label_id_courant.value = ""
                for champ in [nom_f, prenom_f, numero_doc_f, date_naissance_f, age_f, email_f,
                            telephone_f, ville_f, type_contrat_f, fonds_f]:
                    champ.value = ""
                resultat_zone.controls = []
                notification(page, "Formulaire reinitialise.")
                page.update()

            onglets = ft.Tabs(selected_index=0, animation_duration=250, height=460, tabs=[
                ft.Tab(text="Civil et statut", icon=ft.icons.PERSON_OUTLINE, content=ft.Container(padding=20, content=ft.Column([
                    ft.Row([nom_f, prenom_f, numero_doc_f, date_naissance_f, age_f], wrap=True, spacing=16),
                    ft.Row([email_f, telephone_f, ville_f, type_contrat_f], wrap=True, spacing=16),
                    ft.Row([annee_f, sexe_f, statut_f, pays_f, dependants_f], wrap=True, spacing=16),
                    ft.Divider(),
                    ft.Row([statut_general_f, phase_traitement_f, decision_finale_f, crs_score_f], wrap=True, spacing=16),
                ], scroll=ft.ScrollMode.AUTO))),
                ft.Tab(text="Etudes", icon=ft.icons.SCHOOL_OUTLINED, content=ft.Container(padding=20,
                    content=ft.Row([education_f, eca_f, etudes_canada_f], wrap=True, spacing=16))),
                ft.Tab(text="Langues", icon=ft.icons.TRANSLATE, content=ft.Container(padding=20, content=ft.Column([
                    ft.Row([test_anglais_f, clb_s_f, clb_l_f, clb_r_f, clb_w_f], wrap=True, spacing=16),
                    ft.Row([test_francais_f, nclc_s_f, nclc_l_f, nclc_r_f, nclc_w_f], wrap=True, spacing=16),
                ], scroll=ft.ScrollMode.AUTO))),
                ft.Tab(text="Experience et offres", icon=ft.icons.WORK_OUTLINE, content=ft.Container(padding=20,
                    content=ft.Row([exp_etranger_f, exp_canada_f, secteur_f, teer_f, offre_emploi_f, offre_teer_f, pnp_f],
                                    wrap=True, spacing=16))),
                ft.Tab(text="Garanties, statut et paiement", icon=ft.icons.VERIFIED_OUTLINED, content=ft.Container(padding=20,
                    content=ft.Column([
                        ft.Row([famille_canada_f, fonds_f, examen_medical_f, casier_f, inadmissibilite_f, programme_f], wrap=True, spacing=16),
                        ft.Divider(),
                        ft.Row([frais_encaisses_f, restes_a_payer_f, identifiant_conseiller_f], wrap=True, spacing=16),
                        notes_f,
                    ], scroll=ft.ScrollMode.AUTO))),
            ])

            return ft.Column([
                ft.Text("La saisie peut etre progressive. Un premier enregistrement cree le dossier ; "
                        "les suivants sur ce meme formulaire le mettent a jour.", size=13, color=GRIS_MOYEN),
                label_id_courant,
                ft.Container(height=10),
                carte(onglets),
                ft.Row([
                    ft.OutlinedButton("Nouveau formulaire (vide)", on_click=nouveau_formulaire),
                    ft.ElevatedButton(
                        content=ft.Row([
                            indicateur,
                            ft.Icon(ft.icons.SAVE_OUTLINED, color="#FFFFFF"),
                            ft.Text("Enregistrer le dossier", weight=ft.FontWeight.BOLD)
                        ], spacing=8),
                        bgcolor=ROUGE_CANADA,
                        color="#FFFFFF",
                        height=46,
                        on_click=enregistrer
                    ),
                ], alignment=ft.MainAxisAlignment.END),
                resultat_zone,
            ], scroll=ft.ScrollMode.AUTO)

        return mise_en_page("/nouveau-dossier", "Nouveau dossier", construire)
    

    


    
    # CORRECTION dans page_recherche() - remplace la construction
    # des dropdowns de filtres et ajoute le filtre decision
    
    def page_recherche():
        def construire():
            champ_recherche = ft.TextField(
                label="Nom, prenom, document, telephone, e-mail, ID ou conseiller",
                width=380,
                prefix_icon=ft.icons.SEARCH
            )
            
            # FILTRES AVEC OPTIONS CLAIRES
            
            filtre_programme = dropdown("Programme", [("", "-- Choisir --")] + OPTIONS_PROGRAMME, "")
            filtre_phase = dropdown("Phase de traitement",
                [("", "-- Choisir --"), ("Closed", "Archives (Closed)")] + OPTIONS_PHASE_TRAITEMENT, "")
            filtre_pays = dropdown("Pays d'origine", [("", "-- Choisir --")] + [(p, p) for p in OPTIONS_PAYS], "")
            filtre_decision = dropdown("Decision visa", [("", "-- Choisir --")] + OPTIONS_DECISION, "")
            liste_resultats = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

            def ouvrir_dossier(id_client):
                def handler(e):
                    aller_vers(f"/dossier/{id_client}")
                return handler

            def rechercher(e=None):
                liste_resultats.controls = [ft.ProgressRing()]
                page.update()
                try:
                    prog_val = filtre_programme.value or ""
                    phase_val = filtre_phase.value or ""
                    pays_val = filtre_pays.value or ""
                    dec_val = filtre_decision.value or ""
                    
                    print(f"Recherche : terme={champ_recherche.value}, programme={prog_val}, pays={pays_val}, phase={phase_val}, decision={dec_val}")
                    
                    resultats = client_api.lister_dossiers(
                        terme=champ_recherche.value or "",
                        programme=prog_val,
                        pays=pays_val,
                        phase=phase_val,
                        decision=dec_val,
                    )
                    if not resultats:
                        liste_resultats.controls = [ft.Text("Aucun dossier trouve.", color=GRIS_MOYEN)]
                    else:
                        blocs = []
                        for r in resultats:
                            badge_origine = ft.Container(
                                content=ft.Text(r["origine"], size=10, color="#FFFFFF"),
                                bgcolor=GRIS_MOYEN if r["origine"] == "Archive" else VERT_SUCCES,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=12,
                            )
                            blocs.append(carte(
                                ft.Row([
                                    ft.Column([
                                        ft.Row([
                                            ft.Text(
                                                f"{r.get('nom', '(sans nom)')} {r.get('prenom', '')}",
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            badge_origine
                                        ], spacing=8),
                                        ft.Text(
                                            f"{r['id_client']} - {r.get('program', '-')} - "
                                            f"{r.get('country_of_origin', '-')} - {r.get('phase_traitement', '-')}",
                                            size=12, color=GRIS_MOYEN
                                        ),
                                    ], spacing=2, expand=True),
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_FORWARD_IOS,
                                        icon_size=16,
                                        on_click=ouvrir_dossier(r['id_client'])
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                padding_val=14,
                            ))
                        liste_resultats.controls = blocs
                except ErreurAPI as err:
                    liste_resultats.controls = [ft.Text(err.message, color=ROUGE_CANADA)]
                page.update()

            # Auto-recherche lors du changement des filtres
            for champ in (filtre_programme, filtre_phase, filtre_pays, filtre_decision):
                champ.on_change = rechercher

            
            # FONCTION REINITIALISER LES FILTRES
            
            def reinitialiser_filtres(e):
                champ_recherche.value = ""
                filtre_programme.value = ""
                filtre_phase.value = ""
                filtre_pays.value = ""
                filtre_decision.value = ""
                page.update()
                rechercher()

            # Charge la liste complete au premier affichage
            rechercher()

            return ft.Column([
                ft.Text(
                    "Recherche sur les dossiers en cours ET archives. Liste complete par defaut, "
                    "du plus recent au plus ancien.",
                    size=12, color=GRIS_MOYEN
                ),
                ft.Container(height=16),
                ft.Row([
                    champ_recherche,
                    filtre_programme,
                    filtre_phase,
                    filtre_pays,
                    filtre_decision,
                    ft.ElevatedButton(
                        "Rechercher",
                        bgcolor=ROUGE_CANADA,
                        color="#FFFFFF",
                        height=48,
                        on_click=rechercher
                    ),
                    
                    # BOUTON REINITIALISER LES FILTRES
                    
                    ft.OutlinedButton(
                        "Réinitialiser les filtres",
                        icon=ft.icons.REFRESH,
                        on_click=reinitialiser_filtres,
                        style=ft.ButtonStyle(
                            color=GRIS_MOYEN,
                            side=ft.BorderSide(1, GRIS_MOYEN),
                        ),
                    ),
                ], wrap=True, spacing=12),
                ft.Container(height=20),
                liste_resultats,
            ], scroll=ft.ScrollMode.AUTO, expand=True)

        return mise_en_page("/recherche", "Rechercher un dossier", construire)
    
    # PAGE : DETAIL / EDITION D'UN DOSSIER
    

    
    # REMPLACE entierement page_detail_dossier() dans main.py
    
    def page_detail_dossier(id_client: str):
        def construire():
            dossier = client_api.obtenir_dossier(id_client)
            est_archive = dossier.get("archive", False)

            try:
                complet = client_api.diagnostic_complet(id_client)
                resultat = complet.get("resultat") or {}
                diagnostic_texte = complet.get("diagnostic_ia") or "Diagnostic non disponible."
                scenarios = complet.get("scenarios") or []
                erreur_simulation = complet.get("erreur_simulation")
            except ErreurAPI:
                resultat = {
                    "decision_predite": dossier.get("decision_predite_ml") or "Non calculee",
                    "probabilite_acceptation": float(dossier.get("probabilite_acceptation_ml") or 0),
                    "niveau_confiance": "-"
                }
                diagnostic_texte = "Diagnostic non disponible."
                scenarios = []
                erreur_simulation = "Erreur de chargement."

            bloc_scenarios = []
            if scenarios:
                for s in scenarios[:6]:
                    gain = s["gain_absolu"] * 100
                    bloc_scenarios.append(
                        ft.Row([
                            ft.Text(s["levier"], size=12, expand=True),
                            ft.Text(f"{s['probabilite_apres']*100:.1f}%", size=12),
                            ft.Text(
                                f"({'+' if gain>=0 else ''}{gain:.1f} pts)",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=VERT_SUCCES if gain > 0 else GRIS_MOYEN
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
            else:
                bloc_scenarios = [
                    ft.Text(
                        erreur_simulation or "Simulation indisponible pour ce dossier.",
                        size=12,
                        color=ORANGE_ALERTE
                    )
                ]

            def confirmer_action(titre, message, callback_oui):
                def fermer(e):
                    dialogue.open = False
                    page.update()
                
                def confirmer(e):
                    dialogue.open = False
                    page.update()
                    callback_oui()
                
                dialogue = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(titre),
                    content=ft.Text(message),
                    actions=[
                        ft.TextButton("Annuler", on_click=fermer),
                        ft.ElevatedButton("Confirmer", bgcolor=ROUGE_CANADA, color="#FFFFFF", on_click=confirmer)
                    ]
                )
                page.overlay.append(dialogue)
                dialogue.open = True
                page.update()

            def action_pdf(e):
                page.launch_url(client_api.telecharger_pdf_url(id_client))

            def action_email(e):
                try:
                    client_api.envoyer_email(id_client)
                    notification(page, "Rapport envoye par e-mail avec succes.")
                except ErreurAPI as err:
                    notification(page, f"Erreur envoi e-mail : {err.message}", succes=False)

            def action_supprimer(e):
                def faire():
                    try:
                        client_api.supprimer_dossier(id_client)
                        notification(page, "Dossier supprime avec succes.")
                        aller_vers("/recherche")
                    except ErreurAPI as err:
                        notification(page, f"Erreur suppression : {err.message}", succes=False)
                confirmer_action("Supprimer ce dossier ?", "Action definitive pour un dossier en cours. Continuer ?", faire)

            def action_reouvrir(e):
                def faire():
                    try:
                        client_api.reouvrir_dossier(id_client)
                        notification(page, "Dossier reouvert - modifiable de nouveau.")
                        page.go(f"/dossier/{id_client}")
                    except ErreurAPI as err:
                        notification(page, f"Erreur : {err.message}", succes=False)
                confirmer_action("Reouvrir ce dossier archive ?", "Il redeviendra actif et modifiable.", faire)

            def action_cloturer(decision):
                def faire():
                    try:
                        client_api.modifier_dossier(id_client, {"phase_traitement": "Closed", "visa_decision": decision})
                        notification(page, f"Dossier cloture - visa {decision}.")
                        aller_vers("/recherche")
                    except ErreurAPI as err:
                        notification(page, f"Erreur cloture : {err.message}", succes=False)
                
                def handler(e):
                    confirmer_action(f"Cloturer avec visa {decision} ?", "Le dossier sera archive. Continuer ?", faire)
                return handler

            def action_modifier(e):
                aller_vers(f"/modifier-dossier/{id_client}")

            actions_disponibles = []
            if est_archive:
                actions_disponibles.append(
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.LOCK_OPEN, color="#FFFFFF"),
                            ft.Text("Reouvrir (remettre en cours)")
                        ], spacing=8),
                        bgcolor=BLEU_GLACIER,
                        color="#FFFFFF",
                        on_click=action_reouvrir
                    )
                )
            else:
                actions_disponibles += [
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, color=VERT_SUCCES),
                            ft.Text("Cloturer : Visa Accepte")
                        ], spacing=8),
                        on_click=action_cloturer("Accepted")
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.CANCEL_OUTLINED, color=ROUGE_CANADA),
                            ft.Text("Cloturer : Visa Refuse")
                        ], spacing=8),
                        on_click=action_cloturer("Refused")
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.DELETE_OUTLINE, color=ROUGE_CANADA),
                            ft.Text("Supprimer")
                        ], spacing=8),
                        on_click=action_supprimer
                    ),
                ]

            return ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(
                            f"{dossier.get('nom') or '(sans nom)'} {dossier.get('prenom') or ''}",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            f"{id_client} - {dossier.get('email') or 'pas d e-mail'} - "
                            f"{dossier.get('telephone') or 'pas de telephone'}",
                            size=13,
                            color=GRIS_MOYEN
                        ),
                    ], expand=True),
                    ft.Container(
                        content=ft.Text(
                            "ARCHIVE" if est_archive else "EN COURS",
                            color="#FFFFFF",
                            size=11,
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=GRIS_MOYEN if est_archive else VERT_SUCCES,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=20,
                    ),
                ]),
                ft.Container(height=16),
                carte(
                    ft.Column([
                        ft.Row([
                            ft.Text("Decision predite :", weight=ft.FontWeight.BOLD, size=14),
                            badge_decision(resultat.get("decision_predite", "Refused"))
                        ]),
                        ft.Text(
                            f"Probabilite d'acceptation : {resultat.get('probabilite_acceptation', 0) * 100:.1f}%",
                            size=13
                        ),
                        barre_confiance(resultat.get("niveau_confiance", "-")),
                        ft.Divider(),
                        ft.Text(
                            f"Programme : {dossier.get('program') or '-'}   |   Pays : {dossier.get('country_of_origin') or '-'}   |   "
                            f"Phase : {dossier.get('phase_traitement') or '-'}",
                            size=12,
                            color=GRIS_MOYEN
                        ),
                        
                        # METRIQUES DYNAMIQUES - remplace le texte statique
                        
                        ft.Text(
                            texte_metriques(client_api.metriques_modele()),
                            size=11,
                            color=GRIS_MOYEN
                        ),
                    ])
                ),
                ft.Container(height=16),
                carte(
                    ft.Column([
                        ft.Text("Diagnostic Data Analyst (IA)", size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(diagnostic_texte, size=13)
                    ])
                ),
                ft.Container(height=16),
                carte(
                    ft.Column([
                        ft.Text("Simulateur d'optimisation prescriptive", size=15, weight=ft.FontWeight.BOLD),
                        *bloc_scenarios
                    ])
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.PICTURE_AS_PDF_OUTLINED, color="#FFFFFF"),
                            ft.Text("Telecharger le PDF")
                        ], spacing=8),
                        bgcolor="#111318",
                        color="#FFFFFF",
                        on_click=action_pdf
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.MAIL_OUTLINE, color="#FFFFFF"),
                            ft.Text("Envoyer par e-mail")
                        ], spacing=8),
                        bgcolor=ROUGE_CANADA,
                        color="#FFFFFF",
                        on_click=action_email
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.EDIT_OUTLINED, color="#FFFFFF"),
                            ft.Text("Modifier")
                        ], spacing=8),
                        bgcolor="#111318",
                        color="#FFFFFF",
                        on_click=action_modifier
                    ),
                    *actions_disponibles,
                ], wrap=True, spacing=12),
            ])

        return mise_en_page(f"/dossier/{id_client}", "Detail du dossier", construire)

    
    # PAGE : SIMULATEUR D'OPTIMISATION PRESCRIPTIVE


    
    # CORRECTION dans page_modifier_dossier() - ajoute les nouveaux champs
    # pour etre coherent avec page_nouveau_dossier()
    
    def page_modifier_dossier(id_client: str):
        def construire():
            dossier = client_api.obtenir_dossier(id_client)

            # ---- Champs de base ----
            nom_f = ft.TextField(label="Nom", width=270, value=dossier.get("nom") or "")
            prenom_f = ft.TextField(label="Prenom", width=270, value=dossier.get("prenom") or "")
            numero_doc_f = ft.TextField(label="Numero passeport / CNI", width=270, value=dossier.get("numero_document") or "")
            date_naissance_f = ft.TextField(label="Date de naissance (AAAA-MM-JJ)", width=270,
                                            value=str(dossier.get("date_naissance") or ""))
            age_f = ft.TextField(label="Age", width=200, keyboard_type=ft.KeyboardType.NUMBER,
                                value=str(dossier.get("age") or ""))
            email_f = ft.TextField(label="E-mail", width=270, value=dossier.get("email") or "")
            telephone_f = ft.TextField(label="Telephone / WhatsApp", width=270, value=dossier.get("telephone") or "")
            ville_f = ft.TextField(label="Ville de residence", width=270, value=dossier.get("ville_residence") or "")
            type_contrat_f = ft.TextField(label="Type de contrat", width=270, value=dossier.get("type_contrat") or "")
            
            # ---- Nouveaux champs (paiement et notes) ----
            frais_encaisses_f = ft.TextField(label="Frais encaisses (FCFA)", width=200,
                                            keyboard_type=ft.KeyboardType.NUMBER,
                                            value=str(dossier.get("frais_encaisses") or "0"))
            restes_a_payer_f = ft.TextField(label="Restes a payer (FCFA)", width=200,
                                            keyboard_type=ft.KeyboardType.NUMBER,
                                            value=str(dossier.get("restes_a_payer") or "0"))
            identifiant_conseiller_f = ft.TextField(label="Conseiller en charge", width=200,
                                                    value=dossier.get("identifiant_conseiller") or "", disabled=True)
            notes_f = ft.TextField(label="Notes", width=560, multiline=True, min_lines=2, max_lines=4,
                                value=dossier.get("notes") or "")

            # ---- Dropdowns ----
            annee_f = dropdown("Annee de la demande", OPTIONS_ANNEE, str(dossier.get("application_year") or "2026"))
            sexe_f = dropdown("Sexe", OPTIONS_SEXE, dossier.get("sex"))
            statut_f = dropdown("Statut matrimonial", OPTIONS_STATUT_MATRIMONIAL, dossier.get("marital_status"))
            pays_f = dropdown("Pays d'origine", OPTIONS_PAYS, dossier.get("country_of_origin"))
            dependants_f = dropdown("Personnes a charge", [str(n) for n in range(0, 8)], str(dossier.get("dependants") or "0"))

            # ---- Statut et phase ----
            statut_general_f = dropdown("Statut du dossier", [
                ("en_cours", "Dossier en cours -> predictions_canada"),
                ("termine", "Dossier historique termine -> apprentissage_canada")
            ], "termine" if dossier.get("archive") else "en_cours")
            
            phase_traitement_f = dropdown("Phase de traitement", OPTIONS_PHASE_TRAITEMENT,
                                        dossier.get("phase_traitement") or "File Opened")
            decision_finale_f = dropdown("Decision finale du visa", OPTIONS_DECISION,
                                        dossier.get("visa_decision") or "")
            decision_finale_f.visible = (statut_general_f.value == "termine")
            
            crs_score_f = ft.TextField(label="Score CRS (optionnel, informatif)", width=200,
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        value=str(dossier.get("crs_score") or ""))

            def on_change_statut(e):
                termine = statut_general_f.value == "termine"
                decision_finale_f.visible = termine
                phase_traitement_f.disabled = termine
                if termine:
                    phase_traitement_f.value = "Closed"
                page.update()
            statut_general_f.on_change = on_change_statut

            # ---- Reste des champs ----
            education_f = dropdown("Niveau d'etudes", OPTIONS_EDUCATION, dossier.get("education_level"))
            eca_f = dropdown("Equivalence obtenue (ECA)", OPTIONS_OUI_NON, dossier.get("eca_obtained"))
            etudes_canada_f = dropdown("Etudes faites au Canada", OPTIONS_OUI_NON, dossier.get("studied_in_canada") or "No")
            test_anglais_f = dropdown("Type de test d'anglais", OPTIONS_TEST_ANGLAIS, dossier.get("english_test"))
            clb_s_f = dropdown("CLB Expression orale", OPTIONS_CLB_NCLC, str(dossier.get("clb_speaking_english") or ""))
            clb_l_f = dropdown("CLB Comprehension orale", OPTIONS_CLB_NCLC, str(dossier.get("clb_listening_english") or ""))
            clb_r_f = dropdown("CLB Comprehension ecrite", OPTIONS_CLB_NCLC, str(dossier.get("clb_reading_english") or ""))
            clb_w_f = dropdown("CLB Expression ecrite", OPTIONS_CLB_NCLC, str(dossier.get("clb_writing_english") or ""))
            test_francais_f = dropdown("Type de test de francais", OPTIONS_TEST_FRANCAIS, dossier.get("french_test") or "None")
            nclc_s_f = dropdown("NCLC Expression orale", OPTIONS_CLB_NCLC, str(dossier.get("nclc_speaking_french") or "0"))
            nclc_l_f = dropdown("NCLC Comprehension orale", OPTIONS_CLB_NCLC, str(dossier.get("nclc_listening_french") or "0"))
            nclc_r_f = dropdown("NCLC Comprehension ecrite", OPTIONS_CLB_NCLC, str(dossier.get("nclc_reading_french") or "0"))
            nclc_w_f = dropdown("NCLC Expression ecrite", OPTIONS_CLB_NCLC, str(dossier.get("nclc_writing_french") or "0"))
            exp_etranger_f = dropdown("Experience a l'etranger (annees)", [str(n) for n in range(0, 21)],
                                    str(dossier.get("years_foreign_experience") or "0"))
            exp_canada_f = dropdown("Experience au Canada (annees)", [str(n) for n in range(0, 21)],
                                    str(dossier.get("years_canadian_experience") or "0"))
            secteur_f = dropdown("Secteur d'activite", OPTIONS_SECTEUR, dossier.get("sector"))
            teer_f = dropdown("Categorie professionnelle (TEER)", OPTIONS_TEER, dossier.get("teer_category"))
            offre_emploi_f = dropdown("Offre d'emploi au Canada", OPTIONS_OUI_NON, dossier.get("job_offer_canada") or "No")
            offre_teer_f = dropdown("Categorie TEER de l'offre", OPTIONS_TEER, dossier.get("job_offer_teer") or "None")
            pnp_f = dropdown("Nomination provinciale (PNP)", OPTIONS_OUI_NON, dossier.get("provincial_nomination") or "No")
            famille_canada_f = dropdown("Famille au Canada", OPTIONS_OUI_NON, dossier.get("family_in_canada") or "No")
            fonds_f = ft.TextField(label="Fonds disponibles (CAD)", width=270, keyboard_type=ft.KeyboardType.NUMBER,
                                value=str(dossier.get("funds_available_cad") or ""))
            examen_medical_f = dropdown("Examen medical", OPTIONS_OUI_NON, dossier.get("medical_exam_ok") or "Yes")
            casier_f = dropdown("Casier judiciaire", OPTIONS_CASIER, dossier.get("criminal_record") or "None")
            inadmissibilite_f = dropdown("Inadmissibilite", OPTIONS_OUI_NON, dossier.get("inadmissibility") or "No")
            programme_f = dropdown("Programme cible", OPTIONS_PROGRAMME, dossier.get("program"))

            indicateur = ft.ProgressRing(width=18, height=18, visible=False)

            def valeur_ou_none(champ):
                return champ.value if champ.value not in (None, "") else None
            
            def valeur_int(champ):
                v = valeur_ou_none(champ)
                return int(v) if v is not None else None
            
            def valeur_float(champ):
                v = valeur_ou_none(champ)
                return float(v) if v is not None else None

            def enregistrer(e):
                indicateur.visible = True
                page.update()
                payload = {
                    "nom": valeur_ou_none(nom_f),
                    "prenom": valeur_ou_none(prenom_f),
                    "numero_document": valeur_ou_none(numero_doc_f),
                    "date_naissance": valeur_ou_none(date_naissance_f),
                    "email": valeur_ou_none(email_f),
                    "telephone": valeur_ou_none(telephone_f),
                    "ville_residence": valeur_ou_none(ville_f),
                    "type_contrat": valeur_ou_none(type_contrat_f),
                    "frais_encaisses": valeur_float(frais_encaisses_f),
                    "restes_a_payer": valeur_float(restes_a_payer_f),
                    "notes": valeur_ou_none(notes_f),  # ← AJOUTÉ
                    "phase_traitement": "Closed" if statut_general_f.value == "termine" else phase_traitement_f.value,
                    "visa_decision": decision_finale_f.value if statut_general_f.value == "termine" else None,
                    "profil": {
                        "application_year": valeur_int(annee_f),
                        "age": valeur_int(age_f),
                        "sex": sexe_f.value,
                        "marital_status": statut_f.value,
                        "country_of_origin": pays_f.value,
                        "education_level": education_f.value,
                        "eca_obtained": eca_f.value,
                        "english_test": test_anglais_f.value,
                        "clb_speaking_english": valeur_int(clb_s_f),
                        "clb_listening_english": valeur_int(clb_l_f),
                        "clb_reading_english": valeur_int(clb_r_f),
                        "clb_writing_english": valeur_int(clb_w_f),
                        "french_test": test_francais_f.value,
                        "nclc_speaking_french": valeur_int(nclc_s_f),
                        "nclc_listening_french": valeur_int(nclc_l_f),
                        "nclc_reading_french": valeur_int(nclc_r_f),
                        "nclc_writing_french": valeur_int(nclc_w_f),
                        "years_foreign_experience": valeur_int(exp_etranger_f),
                        "years_canadian_experience": valeur_int(exp_canada_f),
                        "sector": secteur_f.value,
                        "teer_category": teer_f.value,
                        "job_offer_canada": offre_emploi_f.value,
                        "job_offer_teer": offre_teer_f.value,
                        "provincial_nomination": pnp_f.value,
                        "studied_in_canada": etudes_canada_f.value,
                        "family_in_canada": famille_canada_f.value,
                        "funds_available_cad": valeur_float(fonds_f),
                        "dependants": valeur_int(dependants_f),
                        "medical_exam_ok": examen_medical_f.value,
                        "criminal_record": casier_f.value,
                        "inadmissibility": inadmissibilite_f.value,
                        "program": programme_f.value,
                        "crs_score": valeur_int(crs_score_f),  # ← AJOUTÉ
                    }
                }
                try:
                    reponse = client_api.modifier_dossier(id_client, payload)
                    notification(page, f"Dossier {id_client} mis a jour.")
                    aller_vers(f"/dossier/{id_client}")
                except ErreurAPI as err:
                    notification(page, f"Erreur : {err.message}", succes=False)
                finally:
                    indicateur.visible = False
                    page.update()

            onglets = ft.Tabs(selected_index=0, animation_duration=250, height=460, tabs=[
                ft.Tab(text="Civil et statut", icon=ft.icons.PERSON_OUTLINE, content=ft.Container(padding=20, content=ft.Column([
                    ft.Row([nom_f, prenom_f, numero_doc_f, date_naissance_f, age_f], wrap=True, spacing=16),
                    ft.Row([email_f, telephone_f, ville_f, type_contrat_f], wrap=True, spacing=16),
                    ft.Row([annee_f, sexe_f, statut_f, pays_f, dependants_f], wrap=True, spacing=16),
                    ft.Divider(),
                    ft.Row([statut_general_f, phase_traitement_f, decision_finale_f, crs_score_f], wrap=True, spacing=16),
                ], scroll=ft.ScrollMode.AUTO))),
                ft.Tab(text="Etudes", icon=ft.icons.SCHOOL_OUTLINED, content=ft.Container(padding=20,
                    content=ft.Row([education_f, eca_f, etudes_canada_f], wrap=True, spacing=16))),
                ft.Tab(text="Langues", icon=ft.icons.TRANSLATE, content=ft.Container(padding=20, content=ft.Column([
                    ft.Row([test_anglais_f, clb_s_f, clb_l_f, clb_r_f, clb_w_f], wrap=True, spacing=16),
                    ft.Row([test_francais_f, nclc_s_f, nclc_l_f, nclc_r_f, nclc_w_f], wrap=True, spacing=16),
                ], scroll=ft.ScrollMode.AUTO))),
                ft.Tab(text="Experience et offres", icon=ft.icons.WORK_OUTLINE, content=ft.Container(padding=20,
                    content=ft.Row([exp_etranger_f, exp_canada_f, secteur_f, teer_f, offre_emploi_f, offre_teer_f, pnp_f],
                                    wrap=True, spacing=16))),
                ft.Tab(text="Garanties, statut et paiement", icon=ft.icons.VERIFIED_OUTLINED, content=ft.Container(padding=20,
                    content=ft.Column([
                        ft.Row([famille_canada_f, fonds_f, examen_medical_f, casier_f, inadmissibilite_f, programme_f],
                            wrap=True, spacing=16),
                        ft.Divider(),
                        ft.Row([frais_encaisses_f, restes_a_payer_f, identifiant_conseiller_f], wrap=True, spacing=16),
                        notes_f,
                    ], scroll=ft.ScrollMode.AUTO))),
            ])

            return ft.Column([
                ft.Text(f"Modification du dossier {id_client}", size=14, color=GRIS_MOYEN),
                ft.Container(height=10),
                carte(onglets),
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([
                            indicateur,
                            ft.Icon(ft.icons.SAVE_OUTLINED, color="#FFFFFF"),
                            ft.Text("Enregistrer les modifications", weight=ft.FontWeight.BOLD)
                        ], spacing=8),
                        bgcolor=ROUGE_CANADA,
                        color="#FFFFFF",
                        height=46,
                        on_click=enregistrer,
                    )
                ], alignment=ft.MainAxisAlignment.END),
            ], scroll=ft.ScrollMode.AUTO)

        return mise_en_page(f"/modifier-dossier/{id_client}", "Modifier le dossier", construire)


    
    # CORRECTION dans page_simulateur() - utilisation de l'orbe IA
    

    def page_simulateur():
        def construire():
            champ_recherche = ft.TextField(
                label="Nom, prenom, document, telephone ou ID du client",
                width=420,
                prefix_icon=ft.icons.SEARCH
            )
            liste_candidats = ft.Column([])
            zone_resultats = ft.Column([])

            def finaliser_et_afficher(id_client: str, zone: ft.Column):
                """Fonction callback appelée après l'animation de l'orbe IA."""
                try:
                    complet = client_api.diagnostic_complet(id_client)
                    resultat = complet.get("resultat") or {}
                    scenarios = complet.get("scenarios") or []
                    diagnostic_texte = complet.get("diagnostic_ia") or "Non disponible."
                    erreur_simulation = complet.get("erreur_simulation")

                    blocs = [
                        ft.Row([
                            ft.Text(f"Situation actuelle - {id_client}", weight=ft.FontWeight.BOLD, expand=True),
                            badge_decision(resultat.get("decision_predite", "Refused")),
                            ft.Text(f"{resultat.get('probabilite_acceptation', 0) * 100:.1f}%"),
                        ])
                    ]
                    
                    if scenarios:
                        for s in scenarios:
                            gain = s["gain_absolu"] * 100
                            blocs.append(ft.Divider())
                            blocs.append(
                                ft.Row([
                                    ft.Text(s["levier"], expand=True, size=13),
                                    ft.Text(f"{s['probabilite_apres'] * 100:.1f}%", size=13),
                                    ft.Text(
                                        f"({'+' if gain >= 0 else ''}{gain:.1f} pts)",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=VERT_SUCCES if gain > 0 else GRIS_MOYEN
                                    ),
                                    badge_decision(s["nouvelle_decision"]),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                        
                        blocs.append(
                            ft.Container(height=10)
                        )
                        blocs.append(
                            ft.Row([
                                ft.Icon(ft.icons.INFO_OUTLINE, color=GRIS_MOYEN, size=16),
                                ft.Text(
                                    "Note : Les gains sont des estimations individuelles, une modification à la fois, en partant du profil actuel."
                                    "L'effet combiné de plusieurs modifications peut être différent (interactions non-linéaires).",
                                    size=12,
                                    color=GRIS_MOYEN,
                                    italic=True,
                                    expand=True
                                ),
                            ], spacing=8)
                        )
                    else:
                        blocs.append(
                            ft.Text(
                                erreur_simulation or "Simulation indisponible.",
                                color=ORANGE_ALERTE,
                                size=12
                            )
                        )

                    metriques = client_api.metriques_modele()
                    
                    zone.controls = [
                        carte(ft.Column(blocs)),
                        ft.Container(height=16),
                        carte(
                            ft.Column([
                                ft.Text("Diagnostic Data Analyst (IA)", size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(diagnostic_texte, size=13)
                            ])
                        ),
                        ft.Container(height=16),
                        carte(
                            ft.Column([
                                ft.Text("Metriques et performances du modele", size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    texte_metriques(metriques),
                                    size=12,
                                    color=GRIS_MOYEN
                                ),
                                ft.Text(
                                    f"Derniere mise a jour : {str(metriques.get('date_execution', ''))[:16] or 'inconnue'}",
                                    size=11,
                                    color=GRIS_MOYEN,
                                    italic=True
                                ),
                            ])
                        ),
                    ]
                    page.update()
                except ErreurAPI as err:
                    zone.controls = [ft.Text(f"Erreur : {err.message}", color=ROUGE_CANADA)]
                    page.update()

            def lancer_simulation_pour(id_client):
                def handler(e):
                    
                    # OVERLAY AVEC FOND SEMI-TRANSPARENT + FLOU LÉGER
                    
                    overlay = ft.Container(
                        content=ft.Stack(
                            controls=[
                                # Fond semi-transparent + flou léger
                                ft.Container(
                                    expand=True,
                                    bgcolor="#0A0A14BB",
                                    blur=ft.Blur(4, 4),
                                ),
                                # Contenu centré
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Container(expand=True),
                                            ft.Column(
                                                controls=[
                                                    # Orbe avec effet tourbillon simplifié
                                                    ft.Stack(
                                                        controls=[
                                                            # Anneaux concentriques (effet tourbillon)
                                                            ft.Container(
                                                                width=260,
                                                                height=260,
                                                                border_radius=130,
                                                                border=ft.border.all(3, "#4F46E5"),
                                                                opacity=0.2,
                                                            ),
                                                            ft.Container(
                                                                width=220,
                                                                height=220,
                                                                border_radius=110,
                                                                border=ft.border.all(2.5, "#7C3AED"),
                                                                opacity=0.3,
                                                            ),
                                                            ft.Container(
                                                                width=180,
                                                                height=180,
                                                                border_radius=90,
                                                                border=ft.border.all(2, "#DB2777"),
                                                                opacity=0.4,
                                                            ),
                                                            # Orbe principale
                                                            ft.Container(
                                                                width=140,
                                                                height=140,
                                                                border_radius=70,
                                                                gradient=ft.RadialGradient(
                                                                    center=ft.alignment.center,
                                                                    radius=0.8,
                                                                    colors=["#4F46E5", "#7C3AED", "#DB2777"]
                                                                ),
                                                                shadow=ft.BoxShadow(
                                                                    blur_radius=50,
                                                                    spread_radius=10,
                                                                    color="#664F46E5"
                                                                ),
                                                                scale=1.0,
                                                            ),
                                                        ],
                                                        alignment=ft.alignment.center,
                                                    ),
                                                    ft.Container(height=30),
                                                    ft.Text(
                                                        "🔮 Analyse du profil en cours...",
                                                        size=26,
                                                        color="#111827",
                                                        weight=ft.FontWeight.W_600,
                                                        text_align=ft.TextAlign.CENTER,
                                                    ),
                                                    ft.Container(height=10),
                                                    ft.Text(
                                                        "Le Data Analyst IA examine votre dossier d'immigration",
                                                        size=15,
                                                        color="#1E3A5F",
                                                        text_align=ft.TextAlign.CENTER,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                spacing=0,
                                            ),
                                            ft.Container(expand=True),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                    alignment=ft.alignment.center,
                                ),
                            ]
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        opacity=0,
                        animate_opacity=500,
                        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                    )
                    
                    page.overlay.append(overlay)
                    overlay.opacity = 1
                    page.update()

                    messages = [
                        ("Analyse du profil en cours...", "Le Data Analyst IA examine votre dossier d'immigration"),
                        ("Calcul des scénarios d'optimisation...", "Le modèle ML évalue les leviers d'amélioration"),
                        ("Consultation du Data Analyst IA...", "Génération des recommandations personnalisées"),
                        ("Préparation du rapport final...", "Synthèse des résultats et des actions prioritaires")
                    ]

                    couleurs_tourbillon = [
                        ["#4F46E5", "#7C3AED", "#DB2777"],
                        ["#7C3AED", "#DB2777", "#F59E0B"],
                        ["#DB2777", "#F59E0B", "#10B981"],
                        ["#F59E0B", "#10B981", "#3B82F6"],
                        ["#10B981", "#3B82F6", "#4F46E5"],
                        ["#3B82F6", "#4F46E5", "#7C3AED"],
                    ]

                    resultats_charges = {"value": False}

                    def afficher_resultats():
                        try:
                            # Récupérer les éléments depuis l'overlay
                            stack = overlay.content.controls[1].content.controls[1].controls[0]
                            orbe = stack.controls[3]
                            anneau1 = stack.controls[0]
                            anneau2 = stack.controls[1]
                            anneau3 = stack.controls[2]
                            texte_principal = overlay.content.controls[1].content.controls[1].controls[1]
                            texte_sous = overlay.content.controls[1].content.controls[1].controls[2]
                            
                            # Tourbillon devient vert
                            orbe.gradient = ft.RadialGradient(
                                center=ft.alignment.center,
                                radius=0.8,
                                colors=["#10B981", "#34D399", "#6EE7B7"]
                            )
                            orbe.scale = 1.0
                            
                            anneau1.border = ft.border.all(3, "#10B981")
                            anneau1.opacity = 0.5
                            anneau2.border = ft.border.all(2.5, "#34D399")
                            anneau2.opacity = 0.4
                            anneau3.border = ft.border.all(2, "#6EE7B7")
                            anneau3.opacity = 0.3
                            
                            texte_principal.value = "Analyse terminée !"
                            texte_principal.color = "#065F46"
                            texte_sous.value = "Affichage des résultats..."
                            texte_sous.color = "#065F46"
                            
                            try:
                                page.update()
                            except Exception:
                                pass
                            
                            time.sleep(0.5)
                            
                            overlay.opacity = 0
                            try:
                                page.update()
                            except Exception:
                                pass
                            
                            time.sleep(0.3)
                            page.overlay.remove(overlay)
                            try:
                                page.update()
                            except Exception:
                                pass
                        except Exception as e:
                            print(f"Erreur afficher_resultats: {e}")
                            try:
                                page.overlay.remove(overlay)
                            except Exception:
                                pass

                    def animer():
                        import time
                        import math
                        
                        stack = overlay.content.controls[1].content.controls[1].controls[0]
                        orbe = stack.controls[3]
                        anneau1 = stack.controls[0]
                        anneau2 = stack.controls[1]
                        anneau3 = stack.controls[2]
                        texte_principal = overlay.content.controls[1].content.controls[1].controls[1]
                        texte_sous = overlay.content.controls[1].content.controls[1].controls[2]
                        
                        etapes = len(messages)
                        temps_par_etape = 0.6
                        
                        i = 0
                        angle = 0
                        while not resultats_charges["value"]:
                            # Effet tourbillon : rotation
                            angle += 0.12
                            
                            # Changement des couleurs de l'orbe
                            couleurs = couleurs_tourbillon[i % len(couleurs_tourbillon)]
                            orbe.gradient = ft.RadialGradient(
                                center=ft.alignment.center,
                                radius=0.8,
                                colors=couleurs
                            )
                            
                            # Pulsation de l'orbe
                            orbe.scale = 1.15 + 0.08 * math.sin(i * 0.3)
                            
                            # Anneaux qui tournent en sens opposés
                            anneau1.scale = 1.0 + 0.04 * math.sin(i * 0.15)
                            anneau2.scale = 1.0 + 0.03 * math.sin(i * 0.2 + 1)
                            anneau3.scale = 1.0 + 0.02 * math.sin(i * 0.25 + 0.5)
                            
                            # Changer les couleurs des anneaux
                            coul = couleurs_tourbillon[i % len(couleurs_tourbillon)]
                            anneau1.border = ft.border.all(3, coul[0])
                            anneau2.border = ft.border.all(2.5, coul[1])
                            anneau3.border = ft.border.all(2, coul[2])
                            
                            # Changer les textes
                            texte_principal.value = messages[i % etapes][0]
                            texte_sous.value = messages[i % etapes][1]
                            
                            try:
                                page.update()
                            except Exception:
                                pass
                            
                            time.sleep(temps_par_etape)
                            i += 1
                        
                        afficher_resultats()

                    def charger_resultats():
                        finaliser_et_afficher(id_client, zone_resultats)
                        resultats_charges["value"] = True

                    import threading
                    
                    threading.Thread(target=animer, daemon=True).start()
                    threading.Thread(target=charger_resultats, daemon=True).start()
                    
                return handler

            def rechercher_candidats(e):
                liste_candidats.controls = [ft.ProgressRing()]
                page.update()
                try:
                    resultats = client_api.lister_dossiers(terme=champ_recherche.value or "")
                    if not resultats:
                        liste_candidats.controls = [ft.Text("Aucun dossier trouve.", color=GRIS_MOYEN)]
                    else:
                        liste_candidats.controls = [
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(
                                        f"{r.get('nom') or '(sans nom)'} {r.get('prenom') or ''} ({r['id_client']})",
                                        expand=True,
                                        size=13
                                    ),
                                    ft.ElevatedButton(
                                        "Simuler",
                                        bgcolor=ROUGE_CANADA,
                                        color="#FFFFFF",
                                        on_click=lancer_simulation_pour(r['id_client'])
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                padding=10,
                                bgcolor="#FFFFFF",
                                border_radius=10,
                                margin=ft.margin.only(bottom=6)
                            )
                            for r in resultats
                        ]
                except ErreurAPI as err:
                    liste_candidats.controls = [ft.Text(err.message, color=ROUGE_CANADA)]
                page.update()

            return ft.Column([
                ft.Text(
                    "Recherchez un client par nom, telephone, document ou ID - aucun ID requis a l'avance.",
                    size=13,
                    color=GRIS_MOYEN
                ),
                ft.Container(height=16),
                ft.Row([
                    champ_recherche,
                    ft.ElevatedButton(
                        "Rechercher",
                        bgcolor="#111318",
                        color="#FFFFFF",
                        on_click=rechercher_candidats
                    )
                ]),
                ft.Container(height=12),
                liste_candidats,
                ft.Container(height=20),
                zone_resultats,
            ], scroll=ft.ScrollMode.AUTO)

        return mise_en_page("/simulateur", "Simulateur d'optimisation prescriptive", construire)

    
    # PAGE : ADMINISTRATION (agents + console MLOps)
    
    
    # REMPLACE entierement page_admin() dans main.py
    
    def page_admin():
        def construire():
            if not client_api.est_admin:
                return ft.Text("Acces reserve aux administrateurs.", color=ROUGE_CANADA)

            zone_mlops = ft.Column(
                [ft.ProgressRing()],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=8,
            )
            
            zone_agents = ft.Column(
                [ft.ProgressRing()],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=8,
            )
            
            champ_recherche_agent = ft.TextField(
                label="Rechercher un agent (nom, e-mail, identifiant)",
                width=380,
                prefix_icon=ft.icons.SEARCH
            )

            def charger_historique():
                try:
                    historique = client_api.historique_entrainement()
                    if not historique:
                        zone_mlops.controls = [ft.Text("Aucun entrainement enregistre.", color=GRIS_MOYEN)]
                    else:
                        lignes = []
                        
                        # Charger les top features
                        top_features = []
                        try:
                            import json
                            import os
                            chemins_possibles = [
                                'backend/top_features.json',
                                '../backend/top_features.json',
                                'top_features.json',
                                os.path.join(os.path.dirname(__file__), '..', 'backend', 'top_features.json'),
                                os.path.join(os.path.dirname(__file__), 'top_features.json'),
                            ]
                            for chemin in chemins_possibles:
                                if os.path.exists(chemin):
                                    with open(chemin, 'r') as f:
                                        top_features = json.load(f)
                                    break
                        except Exception:
                            top_features = ["Non disponibles"]

                        # Récupérer le meilleur modèle
                        meilleur_modele = None
                        try:
                            metriques = client_api.metriques_modele()
                            if metriques and metriques.get('precision_score') is not None:
                                meilleur_modele = {
                                    'accuracy': metriques.get('accuracy', 0),
                                    'precision': metriques.get('precision_score', 0),
                                    'recall': metriques.get('recall_score', 0),
                                    'specificity': metriques.get('specificity_score', 0),
                                    'f1': metriques.get('f1_score', 0),
                                    'roc_auc': metriques.get('roc_auc', 0),
                                    'date': metriques.get('date_execution', '')
                                }
                        except Exception:
                            pass

                        for h in historique:
                            # Déterminer le statut
                            if h.get("modele_valide", False):
                                badge_statut = ft.Container(
                                    content=ft.Text("ACCEPTE", color="#FFFFFF", size=10, weight=ft.FontWeight.BOLD),
                                    bgcolor=VERT_SUCCES,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=10,
                                )
                                couleur_statut = VERT_SUCCES
                                couleur_fond = "#F0FDF4"
                                bordure = "#D1FAE5"
                            else:
                                badge_statut = ft.Container(
                                    content=ft.Text("REJETE", color="#FFFFFF", size=10, weight=ft.FontWeight.BOLD),
                                    bgcolor=ORANGE_ALERTE,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=10,
                                )
                                couleur_statut = ORANGE_ALERTE
                                couleur_fond = "#FFF7ED"
                                bordure = "#FDE68A"

                            precision_actuelle = h.get('precision_score', 0)
                            
                            # CORRECTION : Récupérer nb_dossiers_train correctement
                            
                            nb_dossiers = h.get('nb_dossiers_train', 0)
                            modele_choisi = h.get('modele_choisi', 'inconnu')
                            
                            if h.get("modele_valide", False):
                                message_statut = f"Modele ACCEPTE avec Precision {precision_actuelle*100:.1f}%"
                            else:
                                if meilleur_modele:
                                    message_statut = (
                                        f"Modele REJETE : Precision {precision_actuelle*100:.1f}% "
                                        f"(ancien meilleur : {meilleur_modele['precision']*100:.1f}%)"
                                    )
                                else:
                                    message_statut = f"Modele REJETE : Precision {precision_actuelle*100:.1f}%"

                            # Métriques de l'ancien modèle conservé
                            metriques_ancien = None
                            if meilleur_modele and not h.get("modele_valide", False):
                                metriques_ancien = ft.Container(
                                    content=ft.Column([
                                        ft.Text("Ancien modele conserve :", size=11, color=GRIS_TEXTE, weight=ft.FontWeight.W_600),
                                        ft.Text(
                                            f"Accuracy: {meilleur_modele['accuracy']*100:.1f}% | "
                                            f"Precision: {meilleur_modele['precision']*100:.1f}% | "
                                            f"Recall: {meilleur_modele['recall']*100:.1f}% | "
                                            f"Specificity: {meilleur_modele['specificity']*100:.1f}% | "
                                            f"F1: {meilleur_modele['f1']*100:.1f}% | "
                                            f"ROC-AUC: {meilleur_modele['roc_auc']:.4f}",
                                            size=10,
                                            color=GRIS_MOYEN,
                                        ),
                                    ], spacing=2),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=6),
                                    bgcolor="#F1F5F9",
                                    border_radius=6,
                                )

                            lignes.append(
                                ft.Container(
                                    width=680,
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Column([
                                                ft.Text(
                                                    h.get("date_execution", "")[:19],
                                                    size=11,
                                                    color=GRIS_TEXTE,
                                                    weight=ft.FontWeight.W_600,
                                                ),
                                                ft.Text(
                                                    f"Declenchement : {h.get('declenchement', 'inconnu')}",
                                                    size=9,
                                                    color=GRIS_MOYEN,
                                                ),
                                                
                                                # AJOUT : Modele choisi et nombre de dossiers
                                                
                                                ft.Row([
                                                    ft.Text(
                                                        f"Modele : {modele_choisi}",
                                                        size=9,
                                                        color=BLEU_GLACIER,
                                                        weight=ft.FontWeight.W_500,
                                                    ),
                                                    ft.Text(
                                                        f" | {nb_dossiers} dossiers",
                                                        size=9,
                                                        color=GRIS_MOYEN,
                                                    ),
                                                ], spacing=4),
                                            ], spacing=2, expand=1),
                                            ft.Column([
                                                badge_statut,
                                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                                        ]),
                                        ft.Row([
                                            ft.Text(f"Accuracy: {h.get('accuracy', 0)*100:.1f}%", size=10, weight=ft.FontWeight.W_500),
                                            ft.Text(f"Precision: {h.get('precision_score', 0)*100:.1f}%", size=10, weight=ft.FontWeight.W_500),
                                            ft.Text(f"Recall: {h.get('recall_score', 0)*100:.1f}%", size=10, weight=ft.FontWeight.W_500),
                                            ft.Text(f"F1: {h.get('f1_score', 0)*100:.1f}%", size=10, weight=ft.FontWeight.W_500),
                                            ft.Text(f"ROC-AUC: {h.get('roc_auc', 0):.4f}", size=10, weight=ft.FontWeight.W_500),
                                        ], wrap=True, spacing=6),
                                        ft.Text(
                                            message_statut,
                                            size=11,
                                            color=couleur_statut,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        metriques_ancien if metriques_ancien else ft.Container(),
                                        ft.Column([
                                            ft.Text(
                                                "Top 10 features les plus influentes :",
                                                size=10,
                                                color=GRIS_TEXTE,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                            ft.Text(
                                                " -> ".join(top_features[:10]) if top_features else "Non disponibles",
                                                size=9,
                                                color=GRIS_TEXTE,
                                                italic=True,
                                            ),
                                            ft.Text(
                                                "Ces variables ont le plus d'impact sur la decision du modele ML",
                                                size=9,
                                                color=GRIS_MOYEN,
                                                italic=True,
                                            ),
                                        ], spacing=3),
                                    ], spacing=6),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                    bgcolor=couleur_fond,
                                    border_radius=10,
                                    border=ft.border.all(1, bordure),
                                )
                            )
                        zone_mlops.controls = lignes
                except ErreurAPI as err:
                    zone_mlops.controls = [ft.Text(err.message, color=ROUGE_CANADA)]
                page.update()

            def charger_agents(e=None):
                try:
                    agents = client_api.lister_agents(champ_recherche_agent.value or "")
                    lignes = []
                    for a in agents:
                        lignes.append(
                            ft.Container(
                                width=680,
                                content=ft.Row([
                                    ft.Column([
                                        ft.Text(a["nom_agent"], weight=ft.FontWeight.BOLD, size=13),
                                        ft.Text(a["email_agent"], size=11, color=GRIS_MOYEN),
                                    ], spacing=2, expand=True),
                                    ft.Text(a["identifiant_conseiller"], size=12, color=GRIS_MOYEN),
                                    ft.Container(
                                        content=ft.Text(a["statut_compte"], color="#FFFFFF", size=11, weight=ft.FontWeight.BOLD),
                                        bgcolor=VERT_SUCCES if a["statut_compte"] == "Actif" else ROUGE_CANADA,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=10,
                                    ),
                                    ft.Icon(
                                        ft.icons.ADMIN_PANEL_SETTINGS,
                                        color=OR_ERABLE,
                                        size=18,
                                    ) if a.get("est_admin") else ft.Container(width=18),
                                    ft.IconButton(
                                        icon=ft.icons.EDIT_OUTLINED,
                                        icon_size=18,
                                        on_click=lambda e, ag=a: formulaire_edition_agent(ag)
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                bgcolor="#FFFFFF",
                                border_radius=8,
                                border=ft.border.all(1, "#E5E7EB"),
                            )
                        )
                    zone_agents.controls = lignes if lignes else [ft.Text("Aucun agent trouve.", color=GRIS_MOYEN)]
                except ErreurAPI as err:
                    zone_agents.controls = [ft.Text(err.message, color=ROUGE_CANADA)]
                page.update()

            def formulaire_edition_agent(agent=None):
                est_nouveau = agent is None
                nom_f = ft.TextField(label="Nom complet", width=260, value=(agent or {}).get("nom_agent", ""))
                email_f = ft.TextField(label="E-mail", width=260, value=(agent or {}).get("email_agent", ""))
                id_cons_f = ft.TextField(
                    label="Identifiant conseiller",
                    width=200,
                    value=(agent or {}).get("identifiant_conseiller", ""),
                    disabled=not est_nouveau
                )
                mdp_f = ft.TextField(
                    label="Mot de passe" + ("" if est_nouveau else " (laisser vide pour ne pas changer)"),
                    width=260,
                    password=True,
                    can_reveal_password=True
                )
                admin_f = ft.Checkbox(label="Administrateur", value=(agent or {}).get("est_admin", False))
                statut_f = dropdown(
                    "Statut",
                    [("Actif", "Actif"), ("Suspendu", "Suspendu")],
                    (agent or {}).get("statut_compte", "Actif")
                )

                def fermer(e):
                    dialogue.open = False
                    page.update()

                def enregistrer_agent(e):
                    try:
                        if est_nouveau:
                            client_api.creer_agent({
                                "nom_agent": nom_f.value,
                                "email_agent": email_f.value,
                                "mot_de_passe": mdp_f.value,
                                "identifiant_conseiller": id_cons_f.value,
                            })
                            notification(page, "Agent cree avec succes.")
                        else:
                            donnees = {
                                "nom_agent": nom_f.value,
                                "email_agent": email_f.value,
                                "est_admin": admin_f.value,
                                "statut_compte": statut_f.value
                            }
                            if mdp_f.value:
                                donnees["mot_de_passe"] = mdp_f.value
                            client_api.modifier_agent(agent["identifiant_conseiller"], donnees)
                            notification(page, "Agent mis a jour avec succes.")
                        dialogue.open = False
                        page.update()
                        charger_agents()
                    except ErreurAPI as err:
                        notification(page, f"Erreur : {err.message}", succes=False)

                dialogue = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Nouvel agent" if est_nouveau else "Modifier l'agent"),
                    content=ft.Column([nom_f, email_f, id_cons_f, mdp_f, admin_f, statut_f], tight=True, spacing=10),
                    actions=[
                        ft.TextButton("Annuler", on_click=fermer),
                        ft.ElevatedButton("Enregistrer", bgcolor=ROUGE_CANADA, color="#FFFFFF", on_click=enregistrer_agent)
                    ],
                )
                page.dialog = dialogue
                dialogue.open = True
                page.update()

            def declencher(e):
                try:
                    client_api.declencher_reentrainement()
                    notification(page, "Reentrainement lance en arriere-plan. L'historique se mettra a jour sous peu.")
                    import threading
                    def recharger_apres_delai():
                        import time
                        time.sleep(3)
                        charger_historique()
                    threading.Thread(target=recharger_apres_delai, daemon=True).start()
                except ErreurAPI as err:
                    notification(page, f"Erreur : {err.message}", succes=False)

            champ_recherche_agent.on_change = charger_agents
            charger_agents()
            charger_historique()

            return ft.Column([
                carte(
                    ft.Column([
                        ft.Row([
                            ft.Text("Console MLOps", size=16, weight=ft.FontWeight.BOLD, expand=True),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.SYNC, color="#FFFFFF"),
                                    ft.Text("Synchroniser et recalculer l'intelligence systeme")
                                ], spacing=8),
                                bgcolor=ROUGE_CANADA,
                                color="#FFFFFF",
                                on_click=declencher
                            )
                        ]),
                        ft.Text(
                            "Reentrainement automatique planifie le 1er de chaque mois. "
                            "Ce bouton force un recalcul immediat.",
                            size=12,
                            color=GRIS_MOYEN
                        ),
                        ft.Divider(),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(
                                        content=zone_mlops,
                                        width=700,
                                        height=420,
                                        border=ft.border.all(1, "#E5E7EB"),
                                        border_radius=8,
                                        padding=8,
                                        bgcolor="#FAFBFC",
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                            ]),
                        ),
                    ])
                ),
                ft.Container(height=20),
                carte(
                    ft.Column([
                        ft.Row([
                            ft.Text("Comptes agents", size=16, weight=ft.FontWeight.BOLD, expand=True),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.PERSON_ADD, color="#FFFFFF"),
                                    ft.Text("Nouvel agent")
                                ], spacing=8),
                                bgcolor=BLEU_GLACIER,
                                color="#FFFFFF",
                                on_click=lambda e: formulaire_edition_agent(None)
                            )
                        ]),
                        champ_recherche_agent,
                        ft.Divider(),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(
                                        content=zone_agents,
                                        width=700,
                                        height=350,
                                        border=ft.border.all(1, "#E5E7EB"),
                                        border_radius=8,
                                        padding=8,
                                        bgcolor="#FAFBFC",
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                            ]),
                        ),
                    ])
                ),
            ], scroll=ft.ScrollMode.AUTO)

        return mise_en_page("/admin", "Administration", construire)

    
    # ROUTAGE
    
    # ROUTAGE
    def route_change(e):
        page.views.clear()
        route = page.route

        if route == "/" or not client_api.email:
            page.views.append(page_connexion())
        elif route == "/dashboard":
            page.views.append(page_dashboard())
        elif route == "/nouveau-dossier":
            page.views.append(page_nouveau_dossier())
        elif route == "/recherche":
            page.views.append(page_recherche())
        elif route.startswith("/dossier/"):
            id_client = route.split("/dossier/")[1]
            page.views.append(page_detail_dossier(id_client))
        elif route == "/simulateur":
            page.views.append(page_simulateur())
        elif route == "/admin":
            page.views.append(page_admin())
        elif route.startswith("/modifier-dossier/"):
            id_client = route.split("/modifier-dossier/")[1]
            page.views.append(page_modifier_dossier(id_client))
        else:
            page.views.append(page_connexion())

        page.update()

    page.on_route_change = route_change
    # Démarrer sur la page de connexion
    page.go("/")



# CORRECTION TEMPORAIRE DE DIAGNOSTIC - remplace la derniere ligne du fichier le temps de confirmer que tout s'affiche

import traceback

def main_avec_diagnostic(page: ft.Page):
    try:
        main(page)
    except Exception:
        print("=" * 60)
        print("ERREUR CAPTUREE DANS main() :")
        traceback.print_exc()
        print("=" * 60)


# ============================================================
# POUR RENDER - Lancement de l'application Flet
# ============================================================

if __name__ == "__main__":
    import os
    import flet as ft

    # Récupérer le port fourni par Render (ou 8000 par défaut pour le développement local)
    port = int(os.environ.get("PORT", 8000))

    # Lancer l'application Flet en mode web sur le port attribué
    ft.app(
        target=main_avec_diagnostic,
        assets_dir="assets",
        port=port,
        view=ft.WEB_BROWSER
    )