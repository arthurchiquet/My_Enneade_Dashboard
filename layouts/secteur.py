import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from server import app
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

layout=html.Div(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Button('Vue générale', color = 'dark', className="mr-1", href='/'),
                dbc.Button('Vue chantier', color = 'dark', className="mr-1", href='/chantier'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')
            ], justify='center'
        ),
        html.Hr(),
        html.Div(
        id='secteur-layout',
        children=[]
        )
    ]
)

@app.callback(
    Output('secteur-layout', 'children'),
    [Input('type-store', 'data'),
     Input('chantier-store', 'data'),
     Input('secteur-store', 'data')
    ])
def return_content(type_store, chantier, secteur):
    if type_store == 1:
        return utils_topo.layout
    elif type_store == 2:
        return utils_inclino.layout
    elif type_store == 3:
        return utils_tirant.layout
    elif type_store == 4:
        return utils_jauge.layout
    elif type_store == 5:
        return utils_piezo.layout

