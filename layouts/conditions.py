import warnings
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from server import app
import dash_table as dt
from user_mgmt import show_users, add_user
import warnings

warnings.filterwarnings("ignore")

conditions = html.Div(
    [
        dcc.Markdown('''
## **Conditions générales d’utilisation du site MyEnneade**

**Article 1 : Objet**

Les présentes CGU ou Conditions Générales d’Utilisation encadrent juridiquement
l’utilisation des services du site MyEnneade.com (ci-après dénommé « le site »).
Constituant le contrat entre la société La Petite Perle, l’Utilisateur, l’accès au site doit être précédé de l’acceptation de ces CGU. L’accès à cette plateforme signifie l’acceptation des présentes CGU.

**Article 2 : Mentions légales**

L’édition du site MyEnneade est assurée par la société Ennéade inscrite au RCS sous le numéro 8399 0165 9901, dont le siège social est localisé au 8 avenue Vaillant 06200 NICE, France
L’hébergeur du site MyEnneade.fr est la société IONOS, sise 7 PL DE LA GARE 57200 SARREGUEMINES

**Article 3 : Accès au site**

Le site MyEnneade.com permet d’accéder aux services suivants :
Visualisation de données
Analyse de données
Extraction et diffusion de données' ])
Le site est accessible depuis n’importe où par tout utilisateur disposant d’un accès à Internet. Tous les frais nécessaires pour l’accès aux services (matériel informatique, connexion Internet…) sont à la charge de l’utilisateur.
L’accès aux services dédiés aux membres s’effectue à l’aide d’un identifiant et d’un mot de passe.
Pour des raisons de maintenance ou autres, l’accès au site peut être interrompu ou suspendu par l’éditeur sans préavis ni justification.

**Article 4 : Collecte des données**

Pour la création du compte de l’Utilisateur, la collecte des informations au moment de l’inscription sur le site est nécessaire et obligatoire. Conformément à la loi n°78-17 du 6 janvier relative à l’informatique, aux fichiers et aux libertés, la collecte et le traitement d’informations personnelles s’effectuent dans le respect de la vie privée.
Suivant la loi Informatique et Libertés en date du 6 janvier 1978, articles 39 et 40, l’Utilisateur dispose du droit d’accéder, de rectifier, de supprimer et d’opposer ses données personnelles. L’exercice de ce droit s’effectue par :
Le formulaire de contact ;
Son espace client.

**Article 5 : Propriété intellectuelle**

Les marques, logos ainsi que les contenus du site myEnneade.com (illustrations graphiques, textes…) sont protégés par le Code de la propriété intellectuelle et par le droit d’auteur.
La reproduction et la copie des contenus par l’Utilisateur requièrent une autorisation préalable du site. Dans ce cas, toute utilisation à des usages commerciaux ou à des fins publicitaires est proscrite.

**Article 6 : Responsabilité**

Bien que les informations publiées sur le site soient réputées fiables, le site se réserve la faculté d’une non-garantie de la fiabilité des sources.
Les informations diffusées sur le site myEnneade.com sont présentées à titre purement informatif et sont sans valeur contractuelle. En dépit des mises à jour régulières, la responsabilité du site ne peut être engagée en cas de modification des dispositions administratives et juridiques apparaissant après la publication. Il en est de même pour l’utilisation et l’interprétation des informations communiquées sur la plateforme.
Le site décline toute responsabilité concernant les éventuels virus pouvant infecter le matériel informatique de l’Utilisateur après l’utilisation ou l’accès à ce site.
Le site ne peut être tenu pour responsable en cas de force majeure ou du fait imprévisible et insurmontable d’un tiers.
La garantie totale de la sécurité et la confidentialité des données n’est pas assurée par le site. Cependant, le site s’engage à mettre en œuvre toutes les méthodes requises pour le faire au mieux.
Le site ne peut être tenu responsable des actions et décisions qui pourraient être engagées vis-à-vis des données et/ou commentaires visibles sur le site.

**Article 7 : Liens hypertextes**

Le site peut être constitué de liens hypertextes. En cliquant sur ces derniers, l’Utilisateur sortira de la plateforme. Cette dernière n’a pas de contrôle et ne peut pas être tenue responsable du contenu des pages web relatives à ces liens.

**Article 8 : Cookies**

Lors des visites sur le site, l’installation automatique d’un cookie sur le logiciel de navigation de l’Utilisateur peut survenir.
Les cookies correspondent à de petits fichiers déposés temporairement sur le disque dur de l’ordinateur de l’Utilisateur. Ces cookies sont nécessaires pour assurer l’accessibilité et la navigation sur le site. Ces fichiers ne comportent pas d’informations personnelles et ne peuvent pas être utilisés pour l’identification d’une personne.
L’information présente dans les cookies est utilisée pour améliorer les performances de navigation sur le site myEnneade.com
En naviguant sur le site, l’Utilisateur accepte les cookies. Leur désactivation peut s’effectuer via les paramètres du logiciel de navigation mais pourra entrainer un disfonctionnement de fonctionnalités internes au site.

**Article 9 : Publication par l’Utilisateur**

Le site myEnneade.com permet aux membres de publier des commentaires privés vis-à-vis des instruments et/ou mesures réalisées.
Dans ses publications, le membre est tenu de respecter les règles de la Netiquette ainsi que les règles de droit en vigueur.
Le site dispose du droit d’exercer une modération à priori sur les publications et peut refuser leur mise en ligne sans avoir à fournir de justification.
Le membre garde l’intégralité de ses droits de propriété intellectuelle. Toutefois, toute publication sur le site implique la délégation du droit non exclusif et gratuit à la société éditrice de représenter, reproduire, modifier, adapter, distribuer et diffuser la publication n’importe où et sur n’importe quel support pour la durée de la propriété intellectuelle. Cela peut se faire directement ou par l’intermédiaire d’un tiers autorisé. Cela concerne notamment le droit d’utilisation de la publication sur le web et sur les réseaux de téléphonie mobile.
À chaque utilisation, l’éditeur s’engage à mentionner le nom du membre à proximité de la publication.
L’Utilisateur est tenu responsable de tout contenu qu’il met en ligne. L’Utilisateur s’engage à ne pas publier de contenus susceptibles de porter atteinte aux intérêts de tierces personnes. Toutes procédures engagées en justice par un tiers lésé à l’encontre du site devront être prises en charge par l’Utilisateur.
La suppression ou la modification par le site du contenu de l’Utilisateur peut s’effectuer à tout moment, pour n’importe quelle raison et sans préavis.

**Article 11 : Durée du contrat**

Le présent contrat est valable pour une durée définie contractuellement. Le début de l’utilisation des services du site marque l’application du contrat à l’égard de l’Utilisateur.

**Article 12 : Droit applicable et juridiction compétente**

Le présent contrat est soumis à la législation française. L’absence de résolution à l’amiable des cas de litige entre les parties implique le recours aux tribunaux français compétents pour régler le contentieux.''')
])

check = dbc.Checklist(
    options=[
        {"label": "Accepter les conditions", "value": 1},
    ],
    value=[],
    id="check",
    inline=True,
)

collapse = html.Div(
    [
        dbc.Button(
            "Lire et accepter les conditions générales d'utilisation",
            id="collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([conditions, html.Br(), check])),
            id="collapse",
        ),
    ]
)

layout = dbc.Container(
    [
        dcc.Location(id="url_conditions", refresh=True),
        html.Br(),
        html.H3("Création du compte utilisateur"),
        html.Br(),
        dbc.Input(placeholder="Email", id="mail", n_submit=0),
        html.Br(),
        dbc.Input(placeholder="Nom d'utilisateur", id="id", n_submit=0),
        html.Br(),
        dbc.Input(
            placeholder="Mot de passe",
            id="mdp",
            n_submit=0,
            type="password",
        ),
        html.Br(),
        dbc.Input(
            placeholder="Saisir à nouveau mot de passe",
            id="mdp2",
            n_submit=0,
            type="password",
        ),
        html.Br(),
        collapse,
        html.Br(),
        dbc.Row(
            [
                dbc.Button("Confirmer", id="button", n_clicks=0),
                dbc.Button("Annuler", href="/", color="link"),
            ]
        ),
        html.Div(id="success"),
    ]
)


@app.callback(
    Output("url_conditions", "pathname"),
    [Input("button", "n_clicks")],
    [State("check", "value")],
)
def login(n_clicks, check):
    if check == [1] and n_clicks > 0:
        return "/"
    else:
        pass


###############################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE USERNAME
################################################################################
@app.callback(
    Output("id", "className"),
    [
        Input("button", "n_clicks"),
        Input("id", "n_submit"),
        Input("mdp", "n_submit"),
        Input("mdp2", "n_submit"),
        Input("mail", "n_submit"),
    ],
    [State("id", "value")],
)
def validateUsername(
    n_clicks,
    usernameSubmit,
    newPassword1Submit,
    newPassword2Submit,
    newEmailSubmit,
    newUsername,
):

    if (
        (n_clicks > 0)
        or (usernameSubmit > 0)
        or (newPassword1Submit > 0)
        or (newPassword2Submit > 0)
        or (newEmailSubmit > 0)
    ):

        if newUsername == None or newUsername == "":
            return "form-control is-invalid"
        else:
            return "form-control is-valid"
    else:
        return "form-control"


################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@app.callback(
    Output("mdp", "className"),
    [
        Input("button", "n_clicks"),
        Input("id", "n_submit"),
        Input("mdp", "n_submit"),
        Input("mdp2", "n_submit"),
        Input("mail", "n_submit"),
    ],
    [State("mdp", "value"), State("mdp2", "value")],
)
def validatePassword1(
    n_clicks,
    usernameSubmit,
    newPassword1Submit,
    newPassword2Submit,
    newEmailSubmit,
    newPassword1,
    newPassword2,
):

    if (
        (n_clicks > 0)
        or (usernameSubmit > 0)
        or (newPassword1Submit > 0)
        or (newPassword2Submit > 0)
        or (newEmailSubmit > 0)
    ):

        if newPassword1 == newPassword2 and len(newPassword1) > 7:
            return "form-control is-valid"
        else:
            return "form-control is-invalid"
    else:
        return "form-control"


################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@app.callback(
    Output("mdp2", "className"),
    [
        Input("button", "n_clicks"),
        Input("id", "n_submit"),
        Input("mdp", "n_submit"),
        Input("mdp2", "n_submit"),
        Input("mail", "n_submit"),
    ],
    [State("mdp", "value"), State("mdp2", "value")],
)
def validatePassword2(
    n_clicks,
    usernameSubmit,
    newPassword1Submit,
    newPassword2Submit,
    newEmailSubmit,
    newPassword1,
    newPassword2,
):

    if (
        (n_clicks > 0)
        or (usernameSubmit > 0)
        or (newPassword1Submit > 0)
        or (newPassword2Submit > 0)
        or (newEmailSubmit > 0)
    ):

        if newPassword1 == newPassword2 and len(newPassword2) > 7:
            return "form-control is-valid"
        else:
            return "form-control is-invalid"
    else:
        return "form-control"


################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE EMAIL
################################################################################
@app.callback(
    Output("mail", "className"),
    [
        Input("button", "n_clicks"),
        Input("id", "n_submit"),
        Input("mdp", "n_submit"),
        Input("mdp2", "n_submit"),
        Input("mail", "n_submit"),
    ],
    [State("mail", "value")],
)
def validateEmail(
    n_clicks,
    usernameSubmit,
    newPassword1Submit,
    newPassword2Submit,
    newEmailSubmit,
    newEmail,
):

    if (
        (n_clicks > 0)
        or (usernameSubmit > 0)
        or (newPassword1Submit > 0)
        or (newPassword2Submit > 0)
        or (newEmailSubmit > 0)
    ):

        if newEmail == None or newEmail == "":
            return "form-control is-invalid"
        else:
            return "form-control is-valid"
    else:
        return "form-control"


################################################################################
# CREATE USER BUTTON CLICKED / ENTER PRESSED - UPDATE DATABASE WITH NEW USER
################################################################################
@app.callback(
    Output("success", "children"),
    [
        Input("button", "n_clicks"),
        Input("check", "value"),
        Input("id", "n_submit"),
        Input("mdp", "n_submit"),
        Input("mdp2", "n_submit"),
        Input("mail", "n_submit"),
    ],
    [
        State("id", "value"),
        State("mdp", "value"),
        State("mdp2", "value"),
        State("mail", "value"),
    ],
)
def createUser(
    n_clicks,
    check,
    usernameSubmit,
    newPassword1Submit,
    newPassword2Submit,
    newEmailSubmit,
    newUser,
    newPassword1,
    newPassword2,
    newEmail,
):
    if (
        (n_clicks > 0)
        or (usernameSubmit > 0)
        or (newPassword1Submit > 0)
        or (newPassword2Submit > 0)
        or (newEmailSubmit > 0)
        or (check == [1])
    ):

        if newUser and newPassword1 and newPassword2 and newEmail != "":
            if newPassword1 == newPassword2:
                if len(newPassword1) > 7:
                    try:
                        if check == [1]:
                            add_user(newUser, newPassword1, newEmail, 4)
                            return html.Div(
                                children=["Nouvel utilisateur crée"],
                                className="text-success",
                            )
                        else:
                            return html.Div(
                                children=[
                                    "Vous devez accepter les conditions pour continuer"
                                ],
                                className="text-danger",
                            )
                    except Exception as e:
                        return html.Div(
                            children=["Echec: {e}".format(e=e)], className="text-danger"
                        )
                else:
                    return html.Div(
                        children=["Le mot de passe doit contenir plus de 8 caractères"],
                        className="text-danger",
                    )
            else:
                return html.Div(
                    children=["Le mot de passe ne correspond pas"],
                    className="text-danger",
                )
        else:
            return html.Div(
                children=["Informations incorrectes"], className="text-danger"
            )


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
