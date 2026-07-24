
# components.py - VERSION COMPLETE FINALE

import flet as ft
from theme import (ROUGE_CANADA, GRIS_TEXTE, GRIS_CLAIR, BLANC, VERT_SUCCES, ORANGE_ALERTE,
                    GRIS_MOYEN, NOIR_DOUX, OR_ERABLE, BLEU_GLACIER, ENTREPRISE,
                    DRAPEAU_CANADA_URL, DRAPEAU_CAMEROUN_URL)


def entete_logo(page: ft.Page) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Image(src="logo_HICI.jpg", width=52, height=52, fit=ft.ImageFit.CONTAIN, border_radius=10),
                ft.Container(height=10),
                ft.Text("HI CONSULTING\nIMMIGRATION", size=12, weight=ft.FontWeight.BOLD, color=BLANC, max_lines=2),
                ft.Text(ENTREPRISE["slogan"], size=10, color="#FFD8DC", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(height=6),
                ft.Row([
                    ft.Image(src=DRAPEAU_CANADA_URL, width=26, height=17, fit=ft.ImageFit.CONTAIN,
                             border_radius=3, tooltip="Canada"),
                    ft.Image(src=DRAPEAU_CAMEROUN_URL, width=26, height=17, fit=ft.ImageFit.CONTAIN,
                             border_radius=3, tooltip="Cameroun"),
                ], spacing=8),
            ],
            spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START, tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=18),
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                                     colors=[ROUGE_CANADA, "#8A0018"]),
        width=250, height=170,
    )


def carte(contenu: ft.Control, largeur=None, padding_val=20) -> ft.Container:
    return ft.Container(
        content=contenu, bgcolor=BLANC, border_radius=18, padding=padding_val, width=largeur,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 6)),
        animate=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
        animate_opacity=300,
    )


def badge_decision(decision: str) -> ft.Container:
    est_accepte = decision == "Accepted"
    couleur = VERT_SUCCES if est_accepte else ROUGE_CANADA
    texte = "Accepte" if est_accepte else "Refuse"
    icone = ft.icons.CHECK_CIRCLE if est_accepte else ft.icons.CANCEL
    return ft.Container(
        content=ft.Row([ft.Icon(icone, color=BLANC, size=16),
                         ft.Text(texte, color=BLANC, weight=ft.FontWeight.BOLD, size=13)],
                        spacing=6, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=couleur, border_radius=24, padding=ft.padding.symmetric(horizontal=14, vertical=6),
    )


def barre_confiance(niveau: str) -> ft.Row:
    couleurs = {"Elevee": VERT_SUCCES, "Moyenne": ORANGE_ALERTE, "Faible (dossier limite)": ROUGE_CANADA}
    couleur = couleurs.get(niveau, GRIS_MOYEN)
    return ft.Row([ft.Icon(ft.icons.SPEED, color=couleur, size=18),
                   ft.Text(f"Confiance : {niveau}", color=couleur, weight=ft.FontWeight.W_600, size=13)], spacing=6)


def notification(page: ft.Page, message: str, succes: bool = True):
    page.snack_bar = ft.SnackBar(content=ft.Text(message, color="#FFFFFF"),
                                   bgcolor=VERT_SUCCES if succes else ROUGE_CANADA, duration=3500)
    page.snack_bar.open = True
    page.update()


def superposition_chargement(message: str = "Chargement en cours...") -> ft.Container:
    """Overlay plein ecran avec spinner - a afficher pendant les appels API."""
    return ft.Container(
        content=ft.Column(
            [ft.ProgressRing(width=44, height=44, stroke_width=4, color=ROUGE_CANADA),
             ft.Container(height=14), ft.Text(message, size=14, color=GRIS_TEXTE, weight=ft.FontWeight.W_600)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0), expand=True, bgcolor="#F4F5F7",
        animate_opacity=250,
    )



# CORRECTION dans components.py - barre_navigation_haut() utilise
# les fonctions retour/avancer passees en parametre, avec etat disabled correct

def barre_navigation_haut(historique: dict, retour_fn, avancer_fn, titre: str) -> ft.Row:
    peut_reculer = historique['position'] > 0
    peut_avancer = historique['position'] < len(historique['pile']) - 1
    return ft.Row([
        ft.IconButton(
            icon=ft.icons.ARROW_BACK_IOS_NEW,
            icon_size=16,
            on_click=retour_fn,
            disabled=not peut_reculer,
            tooltip="Page precedente"
        ),
        ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_IOS,
            icon_size=16,
            on_click=avancer_fn,
            disabled=not peut_avancer,
            tooltip="Page suivante"
        ),
        ft.Container(width=10),
        ft.Text(titre, size=22, weight=ft.FontWeight.BOLD, color=GRIS_TEXTE),
    ])


# CORRECTION dans components.py - barre_laterale() recoit aller_vers

def barre_laterale(page: ft.Page, client_api, route_active: str, aller_vers) -> ft.Container:
    def naviguer(route):
        def handler(e):
            aller_vers(route)  # Changé : page.go(route) → aller_vers(route)
        return handler

    def deconnexion(e):
        client_api.email = None
        client_api.mot_de_passe = None
        client_api.est_admin = False
        page.go("/")

    try:
        items = [
            ("/dashboard", ft.icons.DASHBOARD_OUTLINED, "Tableau de bord"),
            ("/nouveau-dossier", ft.icons.PERSON_ADD_ALT_OUTLINED, "Nouveau dossier"),
            ("/recherche", ft.icons.SEARCH, "Rechercher un dossier"),
            ("/simulateur", ft.icons.TRENDING_UP, "Simulateur"),
        ]
        if getattr(client_api, "est_admin", False):
            items.append(("/admin", ft.icons.ADMIN_PANEL_SETTINGS_OUTLINED, "Administration"))

        boutons = []
        for route, icone, libelle in items:
            actif = route == route_active
            boutons.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(icone, color=BLANC if actif else "#C9CDD4", size=20),
                            ft.Text(libelle, color=BLANC if actif else "#C9CDD4",
                                    weight=ft.FontWeight.W_600 if actif else ft.FontWeight.NORMAL,
                                    size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ROUGE_CANADA if actif else None,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    on_click=naviguer(route),
                    ink=True,
                    width=222,
                )
            )

        corps_menu = ft.Column(boutons, spacing=4)

    except Exception as err:
        # Si une erreur se produit, on l'affiche EN TOUTES LETTRES
        # dans la sidebar elle-meme, impossible de la manquer.
        corps_menu = ft.Container(
            content=ft.Text(f"ERREUR MENU : {type(err).__name__} - {err}",
                             color="#FFFF00", size=11, selectable=True),
            bgcolor="#FF0000", padding=10,
        )

    return ft.Container(
        content=ft.Column(
            [
                entete_logo(page),
                ft.Container(height=10),
                corps_menu,
                ft.Container(expand=True),
                ft.Divider(color="#2A2D34"),
                ft.Container(
                    content=ft.Row(
                        [ft.Icon(ft.icons.LOGOUT, color="#C9CDD4", size=18),
                         ft.Text("Deconnexion", color="#C9CDD4", size=13)],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    on_click=deconnexion,
                    ink=True,
                ),
            ],
            spacing=4,
            expand=True,
        ),
        width=250,
        bgcolor="#15171C",
        padding=ft.padding.only(bottom=16),
    )


# A AJOUTER dans components.py

import threading, time, math

def texte_metriques(m: dict) -> str:
    if not m or m.get('accuracy') is None:
        return "Metriques du modele non disponibles."
    return (f"Accuracy {float(m['accuracy'])*100:.1f}% - Precision {float(m['precision_score'])*100:.1f}% - "
            f"Recall {float(m['recall_score'])*100:.1f}% - Specificity {float(m.get('specificity_score') or 0)*100:.1f}% - "
            f"F1-Score {float(m['f1_score'])*100:.1f}% - ROC-AUC {float(m['roc_auc']):.4f}")


def lancer_orbe_ia(conteneur: ft.Column, page: ft.Page, callback_final, duree_secondes: float = 3.0):
    """
    Orbe fluide multicolore avec fond sombre et flouté.
    L'animation dure jusqu'à ce que les résultats soient chargés.
    """
    import threading
    import time
    
    # Créer un overlay avec fond semi-transparent et flou
    overlay = ft.Container(
        content=ft.Stack(
            controls=[
                # Fond avec flou (backdrop blur)
                ft.Container(
                    expand=True,
                    bgcolor="#0A0A14CC",  # Semi-transparent
                    blur=ft.Blur(10, 10),  # Flou
                ),
                # Particules en arrière-plan
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(width=4, height=4, border_radius=2, bgcolor="#4F46E5", animate_opacity=300),
                                    ft.Container(width=6, height=6, border_radius=3, bgcolor="#7C3AED", animate_opacity=300),
                                    ft.Container(width=3, height=3, border_radius=1.5, bgcolor="#DB2777", animate_opacity=300),
                                    ft.Container(width=5, height=5, border_radius=2.5, bgcolor="#2563EB", animate_opacity=300),
                                    ft.Container(width=4, height=4, border_radius=2, bgcolor="#4F46E5", animate_opacity=300),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(width=6, height=6, border_radius=3, bgcolor="#DB2777", animate_opacity=300),
                                    ft.Container(width=4, height=4, border_radius=2, bgcolor="#4F46E5", animate_opacity=300),
                                    ft.Container(width=5, height=5, border_radius=2.5, bgcolor="#7C3AED", animate_opacity=300),
                                    ft.Container(width=3, height=3, border_radius=1.5, bgcolor="#2563EB", animate_opacity=300),
                                    ft.Container(width=6, height=6, border_radius=3, bgcolor="#DB2777", animate_opacity=300),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(width=5, height=5, border_radius=2.5, bgcolor="#2563EB", animate_opacity=300),
                                    ft.Container(width=3, height=3, border_radius=1.5, bgcolor="#DB2777", animate_opacity=300),
                                    ft.Container(width=6, height=6, border_radius=3, bgcolor="#4F46E5", animate_opacity=300),
                                    ft.Container(width=4, height=4, border_radius=2, bgcolor="#7C3AED", animate_opacity=300),
                                    ft.Container(width=5, height=5, border_radius=2.5, bgcolor="#2563EB", animate_opacity=300),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                        ],
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    opacity=0.3,
                ),
                # Contenu principal (orbe + textes)
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(expand=True),
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        width=220,
                                        height=220,
                                        border_radius=150,
                                        gradient=ft.RadialGradient(
                                            center=ft.Alignment(0, 0),
                                            radius=0.8,
                                            colors=["#4F46E5", "#7C3AED", "#DB2777"]
                                        ),
                                        shadow=ft.BoxShadow(
                                            blur_radius=80,
                                            spread_radius=15,
                                            color="#664F46E5"
                                        ),
                                        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
                                        animate_scale=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
                                        scale=1.0,
                                    ),
                                    ft.Container(height=24),
                                    ft.Text(
                                        "🔮 Analyse du profil en cours...",
                                        size=28,
                                        color="#FFFFFF",
                                        weight=ft.FontWeight.W_600,
                                        text_align=ft.TextAlign.CENTER,
                                        animate_opacity=300,
                                    ),
                                    ft.Container(height=10),
                                    ft.Text(
                                        "Le Data Analyst IA examine votre dossier d'immigration",
                                        size=16,
                                        color="#9CA3AF",
                                        text_align=ft.TextAlign.CENTER,
                                        animate_opacity=300,
                                    ),
                                    ft.Container(height=12),
                                    ft.ProgressRing(
                                        width=28,
                                        height=28,
                                        stroke_width=3,
                                        color="#4F46E5",
                                        bgcolor="#1A1A2E",
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
                    alignment=ft.Alignment(0, 0),
                ),
            ]
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        opacity=0,
        animate_opacity=500,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    
    page.overlay.append(overlay)
    overlay.opacity = 1
    page.update()

    messages = [
        ("🔮 Analyse du profil en cours...", "Le Data Analyst IA examine votre dossier d'immigration"),
        ("🧠 Calcul des scénarios d'optimisation...", "Le modèle ML évalue les leviers d'amélioration"),
        ("🤖 Consultation du Data Analyst IA...", "Génération des recommandations personnalisées"),
        ("📊 Préparation du rapport final...", "Synthèse des résultats et des actions prioritaires")
    ]

    couleurs_cycle = [
        ["#4F46E5", "#7C3AED", "#DB2777"],
        ["#7C3AED", "#DB2777", "#2563EB"],
        ["#DB2777", "#2563EB", "#4F46E5"],
        ["#2563EB", "#4F46E5", "#7C3AED"],
    ]

    # Variable pour savoir si le chargement est terminé
    chargement_termine = {"value": False}

    def animer():
        orbe = overlay.content.controls[1].content.controls[1].controls[0]
        texte = overlay.content.controls[1].content.controls[1].controls[1]
        sous_texte = overlay.content.controls[1].content.controls[1].controls[2]
        spinner = overlay.content.controls[1].content.controls[1].controls[3]
        
        etapes = len(messages)
        temps_par_etape = duree_secondes / etapes
        
        for i in range(etapes):
            orbe.gradient = ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.8,
                colors=couleurs_cycle[i % len(couleurs_cycle)]
            )
            orbe.scale = 1.2 if i % 2 == 0 else 0.85
            texte.value = messages[i][0]
            sous_texte.value = messages[i][1]
            spinner.color = couleurs_cycle[i % len(couleurs_cycle)][0]
            
            try:
                page.update()
            except Exception:
                pass
            
            time.sleep(temps_par_etape)
        
        # L'animation est terminée, mais on attend que le chargement soit fini
        texte.value = "⏳ Finalisation..."
        sous_texte.value = "Les résultats sont en cours de préparation"
        try:
            page.update()
        except Exception:
            pass
        
        # Attendre que le chargement soit terminé (callback)
        # Le callback va appeler afficher_resultats() qui mettra fin à l'animation
        callback_final()

    def afficher_resultats():
        """Appelé par le callback pour afficher les résultats et retirer l'overlay."""
        try:
            orbe = overlay.content.controls[1].content.controls[1].controls[0]
            texte = overlay.content.controls[1].content.controls[1].controls[1]
            sous_texte = overlay.content.controls[1].content.controls[1].controls[2]
            spinner = overlay.content.controls[1].content.controls[1].controls[3]
            
            # Orbe verte
            orbe.gradient = ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.8,
                colors=["#10B981", "#34D399", "#6EE7B7"]
            )
            orbe.scale = 1.0
            texte.value = "✅ Analyse terminée !"
            sous_texte.value = "Affichage des résultats..."
            spinner.color = "#10B981"
            spinner.value = 1.0
            
            try:
                page.update()
            except Exception:
                pass
            
            time.sleep(0.5)
            
            # Disparition en fondu
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
        except Exception:
            pass

    # Démarrer l'animation
    thread = threading.Thread(target=animer, daemon=True)
    thread.start()
    
    # Retourner la fonction pour afficher les résultats
    return afficher_resultats

def animation_ia_reflexion(page_container: ft.Column, messages: list, callback_final):
    """Affiche une sequence animee style chatbot IA avant de reveler les resultats,
    puis appelle callback_final() qui doit remplacer le contenu."""
    import threading, time

    def sequence():
        for i, msg in enumerate(messages):
            page_container.controls = [
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(width=22, height=22, stroke_width=3, color=OR_ERABLE),
                        ft.Text(msg, size=14, color=GRIS_MOYEN, italic=True),
                    ], spacing=14),
                    padding=20, bgcolor="#FFF9EC", border_radius=14,
                    animate_opacity=300,
                )
            ]
            try:
                page_container.update()
            except Exception:
                pass
            time.sleep(0.6)
        callback_final()

    threading.Thread(target=sequence, daemon=True).start()

