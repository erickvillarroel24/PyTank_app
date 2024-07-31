import base64
import io
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import pytank as pt
from pytank import Fetkovich, CarterTracy
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from scipy.stats import stats

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%favicon%}
        {%css%}
        <link rel="icon" href="/assets/tank.png" type="image/png" />
        <title>Pytank App</title>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# app
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Pytank View", style={
                'margin': '0',
                'display': 'inline-block',
                'verticalAlign': 'middle'
            }),
            html.Img(src='/assets/logo.png', style={
                'height': '50px',
                'float': 'right',
                'verticalAlign': 'middle'
            })
        ], style={
            'width': '100%',
            'backgroundColor': '#007BFF',
            'color': 'white',
            'padding': '10px',
            'borderRadius': '0px',
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center'
        })
    ], style={
        'width': '100%',
        'borderBottom': '2px solid #000',
        'paddingBottom': '0px'
    }),
    # Well module
    html.Div([
        html.Div([
            html.H1("Well Module", style={
                'textAlign': 'center',
                'marginTop': '10px',
                'backgroundColor': '#F7FF4F',
                'padding': '10px',
                'borderRadius': '0px'
            }),
            html.Div([
                html.Div([
                    html.H2("Configuration", style={
                        'textAlign': 'center',
                        'marginTop': '0px',
                        'fontSize': '30px',
                        'width': '100%',
                        'padding': '20px',
                        'boxSizing': 'border-box',
                        # 'backgroundColor': '#F7FF4F',
                        'color': 'black',
                    }),

                    html.Div([
                        html.Label("Upload Production CSV"),
                        dcc.Upload(
                            id='upload-prod-data',
                            children=html.Div([html.A('Select Files')]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(id='prod-upload-status', style={
                            'marginTop': '10px',
                            'padding': '10px',
                            'backgroundColor': '#d4edda',
                            'border': '1px solid #c3e6cb',
                            'borderRadius': '5px'
                        }),
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.Label("Upload Pressure CSV"),
                        dcc.Upload(
                            id='upload-press-data',
                            children=html.Div([html.A('Select Files')]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(id='press-upload-status', style={
                            'marginTop': '10px',
                            'padding': '10px',
                            'backgroundColor': '#d4edda',
                            'border': '1px solid #c3e6cb',
                            'borderRadius': '5px'
                        }),
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.Label("Production frequency"),
                        dcc.Dropdown(
                            id='freq-prod',
                            options=[
                                {'label': 'None', 'value': 'None'},
                                {'label': 'Daily', 'value': 'D'},
                                #{'label': 'Monthly', 'value': 'M'},
                                {'label': 'Monthly', 'value': 'MS'},
                                {'label': 'Four-month period', 'value': 'Q'},
                                {'label': 'Annual', 'value': 'Y'},
                            ],
                            placeholder='Select frequency',
                            style={'width': '100%'}
                        ),

                        html.Label("Pressure frequency"),
                        dcc.Dropdown(
                            id='freq-press',
                            options=[
                                {'label': 'None', 'value': 'None'},
                                {'label': 'Daily', 'value': 'D'},
                                # {'label': 'Monthly', 'value': 'M'},
                                {'label': 'Monthly', 'value': 'MS'},
                                {'label': 'Four-month period', 'value': 'Q'},
                                {'label': 'Annual', 'value': 'Y'},
                            ],
                            placeholder='Select frequency',
                            style={'width': '100%'}
                        ),

                        html.Label("Enter Well Names Below"),
                        html.Div(
                            id='dynamic-well-inputs',
                            children=[
                                dcc.Input(
                                    id={'type': 'well-name', 'index': 0},
                                    type='text',
                                    placeholder='Enter well name',
                                    style={'width': '100%'}
                                ),
                            ]
                        ),
                        html.Button(
                            'Add Well',
                            id='add-well-button',
                            n_clicks=0,
                            style={'width': '50%',
                                   'marginTop': '10px',
                                   'backgroundColor': 'green',
                                   'color': 'white', }
                        ),
                        html.Button(
                            'Remove Well',
                            id='remove-well-button',
                            n_clicks=0,
                            style={'width': '50%',
                                   'marginTop': '10px',
                                   'backgroundColor': 'red',
                                   'color': 'white'}
                        ),
                    ]),

                    html.Div([
                        html.Button(
                            'Submit',
                            id='well-submit-button',
                            n_clicks=0,
                            style={
                                'width': '70%',
                                'marginTop': '20px',
                                'backgroundColor': '#ff551b',
                                'color': 'white',
                                'padding': '10px'
                            }
                        )
                    ], style={'textAlign': 'center', 'marginTop': '10px',
                              'marginBottom': '80px'}),
                ], style={
                    'width': '20%',
                    'padding': '20px',
                    'borderRight': '1px solid black',
                    'boxSizing': 'border-box',
                    'height': '100vh',
                    'overflowY': 'auto',
                    'backgroundColor': '#E5E5E5'
                }),

                html.Div([
                    html.H2(
                        "Results Area",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '10px',
                            'backgroundColor': '#C2C2C2',
                            'padding': '7px',
                            'marginTop': '-20px'
                        }
                    ),
                    html.P(
                        "This section shows the production and "
                        "pressure information for each well according "
                        "to time. Make sure you enter the correct parameters.",
                        style={
                            'fontSize': '16px',
                            'lineHeight': '1.5',
                            'textAlign': 'justify',
                            'marginBottom': '20px'
                        }
                    ),
                    html.Div(
                        [
                            html.Div([
                                "Instruction 1: Make sure to upload the ",
                                html.Span(
                                    "correct file",
                                    style={
                                        'fontStyle': 'italic',
                                        'fontWeight': 'bold'
                                    }
                                ),
                                " with the production and pressure information in its corresponding section."
                            ],
                                style={
                                    'border': '1px solid black',
                                    'padding': '5px',
                                    'margin': '5px',
                                    'borderRadius': '5px',
                                    'backgroundColor': '#F0F0F0',
                                    'width': '100%'
                                }
                            ),
                            html.Div([
                                "Instruction 2: The frequencies of the information must be correct  ",
                                html.Span(
                                    "according to the data",
                                    style={
                                        'fontStyle': 'italic',
                                        'fontWeight': 'bold'
                                    }
                                ),
                                "  that each file has.",
                            ],
                                style={
                                    'border': '1px solid black',
                                    'padding': '5px',
                                    'margin': '5px',
                                    'borderRadius': '5px',
                                    'backgroundColor': '#F0F0F0',
                                    'width': '100%'
                                }
                            ),
                            html.Div([
                                "Instruction 3: It must add the well names ",
                                html.Span(
                                    "exactly as they are written",
                                    style={
                                        'fontStyle': 'italic',
                                        'fontWeight': 'bold'
                                    }
                                ),
                                "  in the uploaded files and does not leave ",
                                html.Span(
                                    "empty boxes",
                                    style={
                                        'fontStyle': 'italic',
                                        'fontWeight': 'bold'
                                    }
                                ),
                                " in case you do not write a well."
                            ],
                                style={
                                    'border': '1px solid black',
                                    'padding': '5px',
                                    'margin': '5px',
                                    'borderRadius': '5px',
                                    'backgroundColor': '#F0F0F0',
                                    'width': '100%'
                                }
                            ),
                        ],
                    ),
                    html.Div(
                        id='well-info-content',
                        style={
                            'overflowY': 'auto',
                            'maxHeight': 'calc(100vh - 300px)',
                            'padding': '10px'
                        }
                    )
                ], id='well-results', style={
                    'width': '80%',
                    'padding': '20px',
                    'boxSizing': 'border-box',
                    'height': '100vh',
                    'overflowY': 'hidden',
                    'marginTop': '0px',

                }),
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'height': '100vh',
                'marginBottom': '20px'
            })
        ], style={
            'height': '100vh',
            'overflow': 'hidden'
        }),

        # Fluid Models module
        html.Div([
            html.Div([
                html.H1("Fluid Models Module", style={
                    'textAlign': 'center',
                    'marginTop': '10px',
                    'backgroundColor': '#F7FF4F',
                    'padding': '10px',
                    'borderRadius': '5px'
                }),
                html.Div([
                    html.Div([
                        html.H2("Configuration", style={
                            'textAlign': 'center',
                            'marginTop': '0px',
                            'fontSize': '30px',
                            'width': '100%',
                            'padding': '10px',
                            'boxSizing': 'border-box',
                            # 'backgroundColor': '#2172F9'
                        }),
                        html.Label("Upload Fluid Models CSV"),
                        dcc.Upload(
                            id='upload-fluid-data',
                            children=html.Div([html.A('Select Files')]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),
                        html.Div(
                            id='fluid-upload-status',
                            style={
                                'marginTop': '10px',
                                'padding': '10px',
                                'backgroundColor': '#d4edda',
                                'border': '1px solid #c3e6cb',
                                'borderRadius': '5px'
                            }
                        ),
                        html.Div([
                            html.Label("Oil Temperature [°F]"),
                            dcc.Input(
                                id='temp-oil',
                                type='number',
                                placeholder='Enter oil temperature [°F]',
                                style={'width': '100%'}
                            ),
                            html.Div(style={'height': '10px'}),

                            html.Label("Water Salinity [ppm]"),
                            dcc.Input(
                                id='salinity-water',
                                type='number',
                                placeholder='Enter water salinity [ppm]',
                                style={'width': '100%'}
                            ),
                            html.Div(style={'height': '10px'}),

                            html.Label("Water Temperature [°F]"),
                            dcc.Input(
                                id='temp-water',
                                type='number',
                                placeholder='Enter water temperature [°F]',
                                style={'width': '100%'}
                            ),
                            html.Div(style={'height': '10px'}),

                            html.Label("Units"),
                            dcc.Dropdown(
                                id='units',
                                options=[
                                    {'label': 'Field', 'value': 'Field'},
                                    {'label': 'English', 'value': 'English'},
                                ],
                                placeholder='Select unit system',
                                style={'width': '100%'}
                            ),
                        ]),

                        html.Div([
                            html.Button(
                                'Submit',
                                id='fluid-submit-button',
                                n_clicks=0,
                                style={
                                    'width': '70%',
                                    'marginTop': '20px',
                                    'backgroundColor': '#ff551b',
                                    'color': 'white',
                                    'padding': '10px'
                                }
                            )
                        ], style={'textAlign': 'center', 'marginTop': '10px',
                                  'marginBottom': '80px'}),
                    ], style={
                        'width': '20%',
                        'padding': '20px',
                        'borderRight': '1px solid black',
                        'boxSizing': 'border-box',
                        'height': '100vh',
                        'overflowY': 'auto',
                        'backgroundColor': '#E5E5E5'
                    }),

                    html.Div([
                        html.H2(
                            "Results Area",
                            style={
                                'textAlign': 'center',
                                'marginBottom': '10px',
                                'backgroundColor': '#C2C2C2',
                                'padding': '7px',
                                'marginTop': '-20px'
                            }
                        ),
                        html.P(
                            "This section shows the results for fluid "
                            "models based on the uploaded CSV and input "
                            "parameters. Make sure you enter the correct "
                            "parameters.",
                            style={
                                'fontSize': '16px',
                                'lineHeight': '1.5',
                                'textAlign': 'justify',
                                'marginBottom': '20px'
                            }
                        ),
                        html.Div(
                            [
                                html.Div([
                                    "Instruction 1: It is mandatory to upload a file with the ",
                                    html.Span(
                                        "PVT information for the oil.",
                                        style={
                                            'fontStyle': 'italic',
                                            'fontWeight': 'bold'
                                        }
                                    ),
                                    " The other values will be for water."
                                ],
                                    style={
                                        'border': '1px solid black',
                                        'padding': '5px',
                                        'margin': '5px',
                                        'borderRadius': '5px',
                                        'backgroundColor': '#F0F0F0',
                                        'width': '100%'
                                    }
                                ),
                                html.Div([
                                    "Instruction 2: Make sure to place the ",
                                    html.Span(
                                        "corresponding units:",
                                        style={
                                            'fontStyle': 'italic',
                                            'fontWeight': 'bold'
                                        }
                                    ),
                                    " Field or English ",
                                    html.Span(
                                        "(water).",
                                        style={
                                            'fontStyle': 'italic',
                                            'fontWeight': 'bold'
                                        }
                                    ),
                                ],
                                    style={
                                        'border': '1px solid black',
                                        'padding': '5px',
                                        'margin': '5px',
                                        'borderRadius': '5px',
                                        'backgroundColor': '#F0F0F0',
                                        'width': '100%'
                                    }
                                ),
                            ],
                        ),
                        html.Div(
                            id='fluid-info-content',
                            style={
                                'overflowY': 'auto',
                                'maxHeight': 'calc(100vh - 140px)',
                                'padding': '10px'
                            }
                        )
                    ], id='fluid-models-results', style={
                        'width': '80%',
                        'padding': '20px',
                        'boxSizing': 'border-box',
                        'height': '100vh',
                        'overflowY': 'hidden'
                    }),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'row',
                    'height': '100vh',
                    'marginBottom': '20px'
                })
            ], style={
                'height': '100vh',
                'overflow': 'hidden'
            }),

            # Tank module
            html.Div([
                html.Div([
                    html.H1("Tank Module", style={
                        'textAlign': 'center',
                        'marginTop': '10px',
                        'backgroundColor': '#F7FF4F',
                        'padding': '10px',
                        'borderRadius': '5px'
                    }),
                    html.Div([
                        html.Div([
                            html.H2("Configuration", style={
                                'textAlign': 'center',
                                'marginTop': '0px',
                                'fontSize': '30px',
                                'width': '100%',
                                'padding': '10px',
                                'boxSizing': 'border-box',
                                # 'backgroundColor': '#2172F9'
                            }),
                            html.Div([
                                html.Label("Tank name"),
                                dcc.Input(
                                    id='tank-name',
                                    type='text',
                                    placeholder='Enter name of tank',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Initial Pressure"),
                                dcc.Input(
                                    id='initial-pressure',
                                    type='number',
                                    placeholder='Enter initial pressure [PSI]',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Initial water saturation"),
                                dcc.Input(
                                    id='initial-water-saturation',
                                    type='number',
                                    placeholder='Enter initial water'
                                                ' saturation [dec]',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Water compressibility"),
                                dcc.Input(
                                    id='water-compressibility',
                                    type='number',
                                    placeholder='Enter water compressibility '
                                                '[dec]',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Formation compressibility"),
                                dcc.Input(
                                    id='formation-compressibility',
                                    type='number',
                                    placeholder='Enter formation'
                                                ' compressibility [dec]',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Aquifer Model"),
                                dcc.Dropdown(
                                    id='aquifer-model',
                                    options=[
                                        {'label': 'None', 'value': 'None'},
                                        {'label': 'Fetkovich',
                                         'value': 'Fetkovich'},
                                        {'label': 'Carter Tracy',
                                         'value': 'Carter Tracy'},
                                    ],
                                    placeholder='Select Aquifer Model',
                                    style={'width': '100%'}
                                ),

                                html.Div(id='additional-inputs', children=[
                                    html.Div(id='fetkovich-inputs', children=[
                                        html.Label("Aquifer Radius [ft]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-aq-radius',
                                                  type='number',
                                                  placeholder='Enter aquifer'
                                                              ' radius',
                                                  style={'width': '60%'}),

                                        html.Label("Reservoir Radius [ft]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-res-radius',
                                                  type='number',
                                                  placeholder='Enter reservoir'
                                                              ' radius',
                                                  style={'width': '60%'}),

                                        html.Label("Aquifer Thickness [ft]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-aq-thickness',
                                                  type='number',
                                                  placeholder='Enter aquifer'
                                                              ' thickness',
                                                  style={'width': '60%'}),

                                        html.Label("Aquifer Porosity [dec]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-aq-por',
                                                  type='number',
                                                  placeholder='Enter aquifer'
                                                              ' porosity',
                                                  style={'width': '60%'}),

                                        html.Label("Total "
                                                   "Compressibility",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-ct',
                                                  type='number',
                                                  placeholder=
                                                  'Enter compressibility',
                                                  style={'width': '60%'}),

                                        html.Label("Theta "
                                                   "[sexagesimal]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-theta',
                                                  type='number',
                                                  placeholder='Enter theta',
                                                  style={'width': '60%'}),

                                        html.Label("Permeability "
                                                   "[darcy]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-k',
                                                  type='number',
                                                  placeholder=
                                                  'Enter permeability',
                                                  style={'width': '60%'}),

                                        html.Label("Water Viscosity [cp]",
                                                   style={'width': '100%'}),
                                        dcc.Input(id='fetkovich-water-visc',
                                                  type='number',
                                                  placeholder=
                                                  'Enter water viscosity',
                                                  style={'width': '60%'}),
                                    ], style={'display': 'none'}),

                                    html.Div(id='carter-tracy-inputs',
                                             children=[
                                                 html.Label(
                                                     "Water Porosity [dec]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id='carter-tracy-aq-por',
                                                     type='number',
                                                     placeholder='Enter '
                                                                 'porosity',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Total "
                                                     "Compressibility",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id='carter-tracy-ct',
                                                     type='number',
                                                     placeholder=
                                                     'Enter compressibility',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Reservoir Radius"
                                                     " [ft]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id=
                                                     'carter-tracy-res-radius',
                                                     type='number',
                                                     placeholder=
                                                     'Enter reservoir radius',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Aquifer "
                                                     "Thickness"
                                                     " [ft]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id=
                                                     'carter-tracy-aq-'
                                                     'thickness',
                                                     type='number',
                                                     placeholder=
                                                     'Enter aquifer thickness',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Theta "
                                                     "[sexagesimal]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id='carter-tracy-theta',
                                                     type='number',
                                                     placeholder=
                                                     'Enter theta',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Permeability"
                                                     " [darcy]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id='carter-tracy-aq-perm',
                                                     type='number',
                                                     placeholder=
                                                     'Enter permeability',
                                                     style={'width': '60%'}),

                                                 html.Label(
                                                     "Water Viscosity "
                                                     "[cp]",
                                                     style={'width': '100%'}),
                                                 dcc.Input(
                                                     id=
                                                     'carter-tracy-water-visc',
                                                     type='number',
                                                     placeholder=
                                                     'Enter water viscosity',
                                                     style={'width': '60%'}),
                                             ], style={'display': 'none'}),
                                ]),

                                html.Div(style={'height': '10px'}),
                            ]),

                            html.Div([
                                html.Button(
                                    'Submit',
                                    id='tank-submit-button',
                                    n_clicks=0,
                                    style={
                                        'width': '70%',
                                        'marginTop': '20px',
                                        'backgroundColor': '#ff551b',
                                        'color': 'white',
                                        'padding': '10px'
                                    }
                                )
                            ], style={'textAlign': 'center',
                                      'marginTop': '10px',
                                      'marginBottom': '80px'}),
                        ], style={
                            'width': '20%',
                            'padding': '20px',
                            'borderRight': '1px solid black',
                            'boxSizing': 'border-box',
                            'height': '100vh',
                            'overflowY': 'auto',
                            'backgroundColor': '#E5E5E5'
                        }),

                        html.Div([
                            html.H2(
                                "Results Area",
                                style={
                                    'textAlign': 'center',
                                    'marginBottom': '10px',
                                    'backgroundColor': '#C2C2C2',
                                    'padding': '7px',
                                    'marginTop': '-20px'
                                }
                            ),
                            html.P(
                                "This section displays the tank "
                                "configuration with specific properties "
                                "selected. Make sure you put the correct"
                                " properties",
                                style={
                                    'fontSize': '16px',
                                    'lineHeight': '1.5',
                                    'textAlign': 'justify',
                                    'marginBottom': '20px'
                                }
                            ),
                            html.Div(
                                [
                                    html.Div([
                                        "Instruction 1: Be sure to place the values in the ",
                                        html.Span(
                                            "specific units",
                                            style={
                                                'fontStyle': 'italic',
                                                'fontWeight': 'bold'
                                            }
                                        ),
                                        " in each section."
                                    ],
                                        style={
                                            'border': '1px solid black',
                                            'padding': '5px',
                                            'margin': '5px',
                                            'borderRadius': '5px',
                                            'backgroundColor': '#F0F0F0',
                                            'width': '100%'
                                        }
                                    ),
                                    html.Div([
                                        "Instruction 2: First work assuming that there is ",
                                        html.Span(
                                            "no aquifer.",
                                            style={
                                                'fontStyle': 'italic',
                                                'fontWeight': 'bold'
                                            }
                                        ),
                                        " If an aquifer exists, make sure to place the appropriate model with its correct properties in the specific units.",
                                    ],
                                        style={
                                            'border': '1px solid black',
                                            'padding': '5px',
                                            'margin': '5px',
                                            'borderRadius': '5px',
                                            'backgroundColor': '#F0F0F0',
                                            'width': '100%'
                                        }
                                    ),
                                    html.Div([
                                        "Instruction 3: ",
                                        html.Span(
                                            "Check",
                                            style={
                                                'fontStyle': 'italic',
                                                'fontWeight': 'bold'
                                            }
                                        ),
                                        "  in the results section if the values entered are correct."
                                    ],
                                        style={
                                            'border': '1px solid black',
                                            'padding': '5px',
                                            'margin': '5px',
                                            'borderRadius': '5px',
                                            'backgroundColor': '#F0F0F0',
                                            'width': '100%'
                                        }
                                    ),
                                ],
                            ),
                            html.Div(
                                id='tank-info-content',
                                style={
                                    'overflowY': 'auto',
                                    'maxHeight': 'calc(100vh - 140px)',
                                    'padding': '10px',
                                }
                            )
                        ], id='tank-results', style={
                            'width': '80%',
                            'padding': '20px',
                            'boxSizing': 'border-box',
                            'height': '100vh',
                            'overflowY': 'hidden'
                        }),
                    ], style={
                        'display': 'flex',
                        'flexDirection': 'row',
                        'height': '100vh',
                        'marginBottom': '20px'
                    })
                ], style={
                    'height': '100vh',
                    'overflow': 'hidden'
                }),
                # Analysis Module
                html.Div([
                    html.Div([
                        html.H1("Analysis Module", style={
                            'textAlign': 'center',
                            'marginTop': '10px',
                            'backgroundColor': '#F7FF4F',
                            'padding': '10px',
                            'borderRadius': '5px'
                        }),
                        html.Div([
                            html.Div([
                                html.H2("Configuration",
                                        style={
                                            'textAlign': 'center',
                                            'marginTop': '0px',
                                            'fontSize': '30px',
                                            'width': '100%',
                                            'padding': '10px',
                                            'boxSizing': 'border-box',
                                            '#backgroundColor': '#2172F9'
                                        }),
                                html.Label("Analysis frequency"),
                                dcc.Dropdown(
                                    id='freq-analysis',
                                    options=[
                                        {'label': 'Quarterly (3 months)',
                                         'value': '3M'},
                                        {'label': 'Biannual (6 months)',
                                         'value': '6M'},
                                        {'label': 'Annual (12 months)',
                                         'value': '12M'},
                                    ],
                                    placeholder='Select frequency',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label("Position Date frequency"),
                                dcc.Dropdown(
                                    id='position',
                                    options=[
                                        {'label': 'begin', 'value': 'begin'},
                                        {'label': 'middle', 'value': 'middle'},
                                        {'label': 'end', 'value': 'end'},
                                    ],
                                    placeholder='Position of the month according to frequency',
                                    style={'width': '100%'}
                                ),
                                html.Div(style={'height': '10px'}),

                                html.Label('Pressure adjustment'),
                                dcc.Dropdown(
                                    id='smooth',
                                    options=[
                                        {'label': 'Yes', 'value': 'Yes'},
                                        {'label': 'No', 'value': 'no'},
                                    ],
                                    placeholder='Adjusted',
                                    style={'width': '100%'}
                                ),

                                html.Div(
                                    id='aditional-adjusted', children=[
                                        html.Div(id='adjusted-input',
                                                 children=[
                                                     html.Label('Degree',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='k',
                                                               type='number',
                                                               placeholder=
                                                               'Enter degree',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('Smoothing'
                                                                ' factor',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='s',
                                                               type='number',
                                                               placeholder=
                                                               'Enter factor',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                 ], style={'display': 'none'}),
                                        html.Div(style={'height': '10px'}),
                                    ],

                                ),

                                html.Label('Campbell (Custom Line)'),
                                dcc.Dropdown(
                                    id='campbell-custom',
                                    options=[
                                        {'label': 'Yes', 'value': 'Yes'},
                                        {'label': 'No', 'value': 'no'},
                                    ],
                                    placeholder='Adjusted',
                                    style={'width': '90%'}
                                ),

                                html.Div(
                                    id='aditional-campbell', children=[
                                        html.Div(id='campbell-input',
                                                 children=[
                                                     html.Label('X1',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='x1-c',
                                                               type='number',
                                                               placeholder=
                                                               'Enter X1 '
                                                               '(Point 1)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('Y1',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='y1-c',
                                                               type='number',
                                                               placeholder=
                                                               'Enter Y1 '
                                                               '(Point 1)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('X2',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='x2-c',
                                                               type='number',
                                                               placeholder=
                                                               'Enter X2 '
                                                               '(Point 2)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('Y2',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='y2-c',
                                                               type='number',
                                                               placeholder=
                                                               'Enter Y2 '
                                                               '(Point 2)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                 ], style={'display': 'none'}),
                                        html.Div(style={'height': '10px'}),
                                    ],

                                ),

                                html.Label('Havlena (Custom Line)'),
                                dcc.Dropdown(
                                    id='havlena-custom',
                                    options=[
                                        {'label': 'Yes', 'value': 'Yes'},
                                        {'label': 'No', 'value': 'no'},
                                    ],
                                    placeholder='Adjusted',
                                    style={'width': '90%'}
                                ),

                                html.Div(
                                    id='aditional-havlena', children=[
                                        html.Div(id='havlena-input',
                                                 children=[
                                                     html.Label('X1',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='x1-h',
                                                               type='number',
                                                               placeholder=
                                                               'Enter X1 '
                                                               '(Point 1)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('Y1',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='y1-h',
                                                               type='number',
                                                               placeholder=
                                                               'Enter Y1 '
                                                               '(Point 1)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('X2',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='x2-h',
                                                               type='number',
                                                               placeholder=
                                                               'Enter X2 '
                                                               '(Point 2)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                     html.Label('Y2',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='y2-h',
                                                               type='number',
                                                               placeholder=
                                                               'Enter Y2 '
                                                               '(Point 2)',
                                                               style=
                                                               {'width':
                                                                    '60%'}),
                                                 ], style={'display': 'none'}),
                                        html.Div(style={'height': '10px'}),
                                    ],

                                ),

                                html.Label("Analytic Method"),
                                dcc.Dropdown(
                                    id='analytic-method',
                                    options=[
                                        {'label': 'Yes', 'value': 'Yes'},
                                        {'label': 'No', 'value': 'No'},
                                    ],
                                    placeholder='Select option',
                                    style={'width': '90%'}
                                ),

                                html.Div(
                                    id='aditional-analytic', children=[
                                        html.Div(id='analytic-input',
                                                 children=[
                                                     html.Label('Inferred'
                                                                ' POES',
                                                                style={
                                                                    'width':
                                                                        '100%',
                                                                }),
                                                     dcc.Input(id='inferred-'
                                                                  'POES',
                                                               type='number',
                                                               placeholder=
                                                               'Enter POES',
                                                               style=
                                                               {'width':
                                                                    '60%'})
                                                 ], style={'display': 'none'}),
                                        html.Div(style={'height': '10px'}),
                                    ]
                                ),
                                html.Label("Graphic"),
                                dcc.Dropdown(
                                    id='graphic',
                                    options=[
                                        {'label': 'None',
                                         'value': 'None'},
                                        {'label': 'Observed Pressure vs Time',
                                         'value': 'Observed Pressure vs Time'},
                                        {'label': 'Flow Rate vs Time (Tank)',
                                         'value': 'Flow Rate vs Time (Tank)'},
                                        {'label': 'Cumulative Production '
                                                  'vs Pressure',
                                         'value': 'Cumulative Production '
                                                  'vs Pressure'},
                                        {'label': 'Cumulative Production vs '
                                                  'Time (Tank)',
                                         'value': 'Cumulative Production vs '
                                                  'Time (Tank)'},
                                        {'label': 'Flow Rate vs Time '
                                                  '(by Well)',
                                         'value': 'Flow Rate vs Time '
                                                  '(by Well)'},
                                        {'label': 'Cumulative Production per '
                                                  'well',
                                         'value': 'Cumulative Production per '
                                                  'well'}
                                    ],
                                    placeholder='Select graphic',
                                    style={'width': '90%'}
                                ),
                                html.Div([
                                    html.Button(
                                        'Submit',
                                        id='analysis-submit-button',
                                        n_clicks=0,
                                        style={
                                            'width': '70%',
                                            'marginTop': '20px',
                                            'backgroundColor': '#ff551b',
                                            'color': 'white',
                                            'padding': '10px'
                                        }
                                    )
                                ], style={'textAlign': 'center',
                                          'marginTop': '10px',
                                          'marginBottom': '80px',
                                          'width': '100%',
                                          'padding': '20px',
                                          'boxSizing': 'border-box',
                                          'height': '100vh',
                                          'overflowY': 'auto',
                                          'backgroundColor': '#E5E5E5',
                                          'flexDirection': 'column',
                                          'justifyContent': 'space-between'
                                          }),
                            ], style={
                                'width': '20%',
                                'padding': '20px',
                                'borderRight': '1px solid black',
                                'boxSizing': 'border-box',
                                'height': '100vh',
                                'overflowY': 'auto',
                                'backgroundColor': '#E5E5E5'
                            }),

                            html.Div([
                                html.H2(
                                    "Results Area",
                                    style={
                                        'textAlign': 'center',
                                        'marginBottom': '10px',
                                        'backgroundColor': '#C2C2C2',
                                        'padding': '7px',
                                        'marginTop': '-20px'
                                    }
                                ),
                                html.P(
                                    "This section shows graphs of"
                                    " Campbell, Havlena an Odeh and real and "
                                    "synthetic pressures to be able to "
                                    "calculate reserves using the graphical "
                                    "and analytical method. In addition, it "
                                    "shows graphs that describe the behavior "
                                    "of the tank or reservoir.",
                                    style={
                                        'fontSize': '16px',
                                        'lineHeight': '1.5',
                                        'textAlign': 'justify',
                                        'marginBottom': '10px'
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Div([
                                            "Instruction 1: It is advisable to select 'No' in the ",
                                            html.Span(
                                                "Pressure adjusted",
                                                style={
                                                    'fontStyle': 'italic',
                                                    'fontWeight': 'bold'
                                                }
                                            ),
                                            " option until you know if your model needs an adjustment in pressures."
                                        ],
                                            style={
                                                'border': '1px solid black',
                                                'padding': '5px',
                                                'margin': '5px',
                                                'borderRadius': '5px',
                                                'backgroundColor': '#F0F0F0',
                                                'width': '100%'
                                            }
                                        ),
                                        html.Div([
                                            "Instruction 2: It is advisable to select 'No' in ",
                                            html.Span(
                                                "Campbell (custom line)",
                                                style={
                                                    'fontStyle': 'italic',
                                                    'fontWeight': 'bold'
                                                }
                                            ), " and ",
                                            html.Span(
                                                "Havlena (custom line)",
                                                style={
                                                    'fontStyle': 'italic',
                                                    'fontWeight': 'bold'
                                                }
                                            ),
                                            " options until you define which points of the graph you want to work on."
                                        ],
                                            style={
                                                'border': '1px solid black',
                                                'padding': '5px',
                                                'margin': '5px',
                                                'borderRadius': '5px',
                                                'backgroundColor': '#F0F0F0',
                                                'width': '100%'
                                            }
                                        ),
                                        html.Div([
                                            "Instruction 3: If an aquifer model does not exist, select 'No' in ",
                                            html.Span(
                                                "Analytical Method",
                                                style={
                                                    'fontStyle': 'italic',
                                                    'fontWeight': 'bold'
                                                }
                                            ),
                                            " option. If it exists, select 'Yes'."
                                        ],
                                            style={
                                                'border': '1px solid black',
                                                'padding': '5px',
                                                'margin': '5px',
                                                'borderRadius': '5px',
                                                'backgroundColor': '#F0F0F0',
                                                'width': '100%'
                                            }
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id='analysis-info-content',
                                    style={
                                        'overflowY': 'auto',
                                        'height': '150vh',
                                    }
                                )
                            ], id='analysis-results', style={
                                'width': '80%',
                                'padding': '20px',
                                'boxSizing': 'border-box',
                                'height': '100vh',
                                'overflowY': 'hidden'
                            }),
                        ], style={
                            'display': 'flex',
                            'flexDirection': 'row',
                            'height': '100Vh',
                            'marginBottom': '20px'
                        })
                    ], style={
                        'height': '100vh',
                        'overflow': 'hidden'
                    })
                ]),
            ])
        ])
    ], style={
        'height': '100vh',
        'overflow': 'auto'
    }),
], style={
    'height': '100vh',
    'overflow': 'hidden'
})

"------------------------ Callback Files CSVs --------------------------------"


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return None
    except Exception as e:
        return None
    return df


@app.callback(
    [Output('prod-upload-status',
            'children'),
     Output('press-upload-status', 'children'),
     Output('fluid-upload-status', 'children')],
    [Input('upload-prod-data', 'contents'),
     Input('upload-press-data', 'contents'),
     Input('upload-fluid-data', 'contents')],
    [State('upload-prod-data', 'filename'),
     State('upload-press-data', 'filename'),
     State('upload-fluid-data', 'filename')]
)
def update_upload_status(upload_prod, upload_press, upload_fluid,
                         filename_prod, filename_press, filename_fluid):
    # Initial statuses
    prod_status = 'Upload production data to start.'
    press_status = 'Upload pressure data to start.'
    fluid_status = 'Upload fluid models data to start.'

    # Process production data
    if upload_prod:
        df_prod = parse_data(upload_prod, filename_prod)
        if df_prod is not None:
            prod_status = f'{filename_prod} uploaded successfully!'
        else:
            prod_status = 'There was an error processing the production data.'

    # Process pressure data
    if upload_press:
        df_press = parse_data(upload_press, filename_press)
        if df_press is not None:
            press_status = f'{filename_press} uploaded successfully!'
        else:
            press_status = 'There was an error processing the pressure data.'

    # Process PVT data
    if upload_fluid:
        df_fluid = parse_data(upload_fluid, filename_fluid)
        if df_fluid is not None:
            fluid_status = f'{filename_fluid} uploaded successfully!'
        else:
            fluid_status = ('There was an error processing the '
                            'fluid models data.')

    return prod_status, press_status, fluid_status


def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))


"----------------------------- Callback Well ---------------------------------"


@app.callback(
    Output('dynamic-well-inputs', 'children'),
    [Input('add-well-button', 'n_clicks'),
     Input('remove-well-button', 'n_clicks')],
    State('dynamic-well-inputs', 'children'),
    prevent_initial_call=True
)
def update_well_inputs(add_clicks, remove_clicks, current_children):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_children

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-well-button' and add_clicks > 0:
        new_index = len([child for child in current_children if
                         isinstance(child, dcc.Input)])
        new_input = dcc.Input(
            id={'type': 'well-name', 'index': new_index},
            type='text',
            placeholder='Enter well name',
            style={'width': '100%'}
        )
        return current_children + [new_input]

    if button_id == 'remove-well-button' and remove_clicks > 0 and len(
            current_children) > 1:
        return current_children[:-1]

    return current_children


# Global variables
global_wells_info = None
global_oil_model = None
global_water_model = None
global_tank = None
global_analysis = None


@app.callback(
    Output('well-info-content', 'children'),
    Input('well-submit-button', 'n_clicks'),
    State('upload-prod-data', 'contents'),
    State('upload-press-data', 'contents'),
    State('freq-prod', 'value'),
    State('freq-press', 'value'),
    State('dynamic-well-inputs', 'children')
)
def update_output_well(n_clicks, prod_content, press_content, freq_prod,
                       freq_press, well_inputs):
    if n_clicks > 0 and prod_content is not None and press_content is not None:
        # Process production and pressure data
        prod_data = parse_contents(prod_content)
        press_data = parse_contents(press_content)

        # Ensure frequencies are handled as strings
        freq_prod = str(
            freq_prod) if freq_prod and freq_prod != 'None' else None
        freq_press = str(
            freq_press) if freq_press and freq_press != 'None' else None

        # Create wells
        wells = pt.create_wells(
            df_prod=prod_data,
            df_press=press_data,
            freq_prod=freq_prod,
            freq_press=freq_press
        )

        # Get well names from input fields
        my_wells = [input['props']['value'] for input
                    in well_inputs if input['props']['value']
                    and input['props']['value'].strip()]

        # Search wells
        global global_wells_info
        global_wells_info = pt.search_wells(
            wells=wells,
            well_names=my_wells
        )

        well_info_display = []

        for well in global_wells_info:
            # Check if prod_data and press_data exist and are not None
            prod_data_df = well.prod_data.data if well.prod_data is not None \
                else pd.DataFrame()
            press_data_df = well.press_data.data if (well.press_data is not
                                                     None) else pd.DataFrame()

            well_info_display.append(html.H4(f"Well: {well.name}"))

            # Container for both production and pressure graphs
            row_layout = []

            # Check if production data exists
            if not prod_data_df.empty:
                prod_graph = dcc.Graph(
                    figure={
                        'data': [
                            {'x': prod_data_df.index,
                             'y': prod_data_df[col],
                             'type': 'line', 'name': col}
                            for col in ['OIL_CUM', 'WATER_CUM', 'LIQ_CUM']
                            if col in prod_data_df.columns
                        ],
                        'layout': {
                            'title': {
                                'text': 'Production vs Time',
                                'font': {
                                    'size': 18,
                                    'family': 'Arial, sans-serif',
                                    'color': 'black',
                                    'weight': 'bold'
                                }
                            },
                            'xaxis': {'title': 'Date',
                                      'titlefont': {'size': 14,
                                                    'family': 'Arial, sans-serif'},
                                      'tickfont': {'size': 12,
                                                   'family': 'Arial, sans-serif'},
                                      'showgrid': True,
                                      'gridcolor': '#D1D1D1',
                                      'gridwidth': 1,
                                      'griddash': 'dash',
                                      'linecolor': 'black',
                                      'mirror': True,
                                      'type': 'date'
                                      },
                            'yaxis': {'title': 'Production [BBL]',
                                      'titlefont': {'size': 14,
                                                    'family': 'Arial, sans-serif'},
                                      'tickfont': {'size': 12,
                                                   'family': 'Arial, sans-serif'},
                                      'showgrid': True,
                                      'gridcolor': '#D1D1D1',
                                      'gridwidth': 1,
                                      'griddash': 'dash',
                                      'linecolor': 'black',
                                      'mirror': True
                                      },
                            'template': 'plotly_white',
                        }
                    }
                )
                row_layout.append(
                    dbc.Col(
                        html.Div([
                            prod_graph
                        ]),
                        width=6
                    )
                )
            else:
                row_layout.append(
                    dbc.Col(
                        html.Div([
                            html.P("No production data available.")
                        ]),
                        width=6
                    )
                )

            # Check if pressure data exists
            if not press_data_df.empty:
                press_graph = dcc.Graph(
                    figure={
                        'data': [
                            {'x': press_data_df.index,
                             'y': press_data_df[col],
                             'type': 'line', 'name': col}
                            for col in press_data_df.columns
                        ],
                        'layout': {
                            'title': {
                                'text': 'Pressure vs Time',
                                'font': {
                                    'size': 18,
                                    'family': 'Arial, sans-serif',
                                    'color': 'black',
                                    'weight': 'bold'
                                }
                            },
                            'xaxis': {'title': 'Date',
                                      'titlefont': {'size': 14,
                                                    'family': 'Arial, sans-serif'},
                                      'tickfont': {'size': 12,
                                                   'family': 'Arial, sans-serif'},
                                      'showgrid': True,
                                      'gridcolor': '#D1D1D1',
                                      'gridwidth': 1,
                                      'griddash': 'dash',
                                      'linecolor': 'black',
                                      'mirror': True,
                                      'type': 'date'
                                      },
                            'yaxis': {'title': 'Pressure [PSI]',
                                      'titlefont': {'size': 14,
                                                    'family': 'Arial, sans-serif'},
                                      'tickfont': {'size': 12,
                                                   'family': 'Arial, sans-serif'},
                                      'showgrid': True,
                                      'gridcolor': '#D1D1D1',
                                      'gridwidth': 1,
                                      'griddash': 'dash',
                                      'linecolor': 'black',
                                      'mirror': True
                                      },
                            'template': 'plotly_white',
                        }
                    }
                )
                row_layout.append(
                    dbc.Col(
                        html.Div([
                            press_graph
                        ]
                        ),
                        width=6
                    )
                )
            else:
                if len(row_layout) == 1:
                    row_layout.append(
                        dbc.Col(
                            html.Div([
                                html.P("No pressure data available.")
                            ]),
                            width=6
                        )
                    )

            # Append the row of columns to well_info_display
            well_info_display.append(
                dbc.Row(row_layout)
            )

            found_wells = [well.name for well in global_wells_info]
            not_found_wells = [well_name for well_name in my_wells if
                               well_name not in found_wells]

            if not_found_wells:
                well_info_display.append(
                    dbc.Alert(
                        f"The following wells were not found: {', '.join(not_found_wells)}. Check the name carefully.",
                        color="warning",
                        dismissable=True,
                        is_open=True,
                        style={'margin-top': '20px'}
                    )
                )

        return well_info_display if well_info_display else [
            html.P("No well data available.")]


"-------------------------- Callback Fluid Models --------------------------"


@app.callback(
    Output('fluid-info-content',
           'children'),
    Input('fluid-submit-button', 'n_clicks'),
    State('upload-fluid-data', 'contents'),
    State('temp-oil', 'value'),
    State('salinity-water', 'value'),
    State('temp-water', 'value'),
    State('units', 'value')
)
def display_fluid_models_data(n_clicks, fluid_contents, temp_oil,
                              salinity_water, temp_water, units):
    if n_clicks > 0:
        if not (fluid_contents and temp_oil and salinity_water
                and temp_water and units):
            return html.Div("Please ensure all fields are filled out "
                            "correctly.",
                            style={'color': 'red'})

        fluid_df = parse_contents(fluid_contents)

        if fluid_df is None or fluid_df.empty:
            return html.Div("Error in reading uploaded files or file"
                            " is empty. Please try again.",
                            style={'color': 'red'})

        global global_oil_model, global_water_model
        # Create oil and water models
        global_oil_model = pt.OilModel(
            data_pvt=fluid_df,
            temperature=temp_oil
        )

        # Units
        if units == 'Field':
            units = 1
        elif units == 'English':
            units = 0

        global_water_model = pt.WaterModel(
            salinity=salinity_water,
            temperature=temp_water,
            unit=units
        )

        df = global_oil_model.data_pvt

        # Add units to columns
        df = df.rename(columns={
            'Pressure': 'Pressure [PSI]',
            'GOR': 'GOR [SCF/STB]',
            'Bo': 'Bo [bbl/STB]',
            'uo': 'uo',
            'Bg': 'Bg [ft3/SCF]',
        })

        df = df.drop(columns=['uo'])

        return html.Div([
            html.H3("Fluid Models Data Results"),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlignn': 'center'
                },
                style_cell={
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            )
        ])
    return ""


"------------------------ Callback Aquifer Model ---------------------------"


@app.callback(
    [Output('fetkovich-inputs', 'style'),
     Output('carter-tracy-inputs', 'style')],
    Input('aquifer-model', 'value')
)
def update_additional_inputs(aquifer_model):
    if aquifer_model == 'Fetkovich':
        return {'display': 'block'}, {'display': 'none'}
    elif aquifer_model == 'Carter Tracy':
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'none'}, {'display': 'none'}


"----------------------------- Callback Tank -------------------------------"


@app.callback(
    Output('tank-info-content', 'children'),
    [Input('tank-submit-button', 'n_clicks')],
    [State('tank-name', 'value'),
     State('initial-pressure', 'value'),
     State('initial-water-saturation', 'value'),
     State('water-compressibility', 'value'),
     State('formation-compressibility', 'value'),
     State('aquifer-model', 'value'),

     # Fetkovich parameters
     State('fetkovich-aq-radius', 'value'),
     State('fetkovich-res-radius', 'value'),
     State('fetkovich-aq-thickness', 'value'),
     State('fetkovich-aq-por', 'value'),
     State('fetkovich-ct', 'value'),
     State('fetkovich-theta', 'value'),
     State('fetkovich-k', 'value'),
     State('fetkovich-water-visc', 'value'),

     # Carter Tracy parameters
     State('carter-tracy-aq-por', 'value'),
     State('carter-tracy-ct', 'value'),
     State('carter-tracy-res-radius', 'value'),
     State('carter-tracy-aq-thickness', 'value'),
     State('carter-tracy-theta', 'value'),
     State('carter-tracy-aq-perm', 'value'),
     State('carter-tracy-water-visc', 'value')]
)
def update_output_tank(n_clicks,
                       tank_name,
                       initial_pressure,
                       initial_water_saturation,
                       water_compressibility,
                       formation_compressibility,
                       aquifer_model,

                       # Fetkovich parameters
                       fetkovich_aq_radius,
                       fetkovich_res_radius,
                       fetkovich_aq_thickness,
                       fetkovich_aq_por,
                       fetkovich_ct,
                       fetkovich_theta,
                       fetkovich_k,
                       fetkovich_water_visc,

                       # Carter Tracy parameters
                       carter_tracy_aq_por,
                       carter_tracy_ct,
                       carter_tracy_res_radius,
                       carter_tracy_aq_thickness,
                       carter_tracy_theta,
                       carter_tracy_aq_perm,
                       carter_tracy_water_visc):
    if n_clicks > 0:
        if not all([tank_name,
                    initial_pressure,
                    initial_water_saturation,
                    water_compressibility,
                    formation_compressibility,
                    aquifer_model,
                    ]):
            return html.Div(
                "Please ensure all fields are filled out correctly.",
                style={'color': 'red'}
            )

        global global_wells_info, global_oil_model, global_water_model, global_tank, global_tank_df_press

        # Set aquifer to None if 'None' is selected
        if aquifer_model == 'None':
            aquifer_model = None
            name_aquifer = 'Without aquifer model'
        elif aquifer_model == 'Fetkovich':
            aquifer_model = pt.Fetkovich(
                aq_radius=fetkovich_aq_radius,
                res_radius=fetkovich_res_radius,
                aq_thickness=fetkovich_aq_thickness,
                aq_por=fetkovich_aq_por,
                ct=fetkovich_ct,
                theta=fetkovich_theta,
                k=fetkovich_k,
                water_visc=fetkovich_water_visc,
            )
            name_aquifer = 'Fetkovich Model'
        elif aquifer_model == 'Carter Tracy':
            aquifer_model = pt.CarterTracy(
                aq_por=carter_tracy_aq_por,
                ct=carter_tracy_ct,
                res_radius=carter_tracy_res_radius,
                aq_thickness=carter_tracy_aq_thickness,
                theta=carter_tracy_theta,
                aq_perm=carter_tracy_aq_perm,
                water_visc=carter_tracy_water_visc,
            )
            name_aquifer = 'Carter Tracy Model'

        global_tank = pt.Tank(
            name=tank_name,
            wells=global_wells_info,
            oil_model=global_oil_model,
            water_model=global_water_model,
            pi=initial_pressure,
            swo=initial_water_saturation,
            cw=water_compressibility,
            cf=formation_compressibility,
            aquifer=aquifer_model
        )

        # Tank Information Display
        tank_info_display = html.Div(
            [
                html.Div(
                    [
                        # Title Section
                        html.H4(
                            f"{global_tank.name}",
                            style={
                                'textAlign': 'center',
                                'marginBottom': '20px',
                                'fontSize': '28px',
                                'fontWeight': 'bold',
                                'color': '#1f2937',
                                'borderBottom': '2px solid #60a5fa'
                            }
                        ),

                        # Info Content Section
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Strong("Initial Pressure:"),
                                        html.Span(f" {initial_pressure}"),
                                    ],
                                    style={
                                        'padding': '15px',
                                        'borderBottom': '1px solid #e2e8f0',
                                        'fontSize': '18px',
                                        'color': '#4b5563'
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Strong(
                                            "Initial Water Saturation:"),
                                        html.Span(
                                            f" {initial_water_saturation}"),
                                    ],
                                    style={
                                        'padding': '15px',
                                        'borderBottom': '1px solid #e2e8f0',
                                        'fontSize': '18px',
                                        'color': '#4b5563'
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Strong("Water Compressibility:"),
                                        html.Span(
                                            f" {water_compressibility} "
                                            f"1/PSI"),
                                    ],
                                    style={
                                        'padding': '15px',
                                        'borderBottom': '1px solid #e2e8f0',
                                        'fontSize': '18px',
                                        'color': '#4b5563'
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Strong(
                                            "Formation Compressibility:"),
                                        html.Span(
                                            f" {formation_compressibility}"
                                            f"1/PSI"),
                                    ],
                                    style={
                                        'padding': '15px',
                                        'borderBottom': '1px solid #e2e8f0',
                                        'fontSize': '18px',
                                        'color': '#4b5563'
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Strong("Aquifer Model:"),
                                        html.Span(f" {name_aquifer}"),
                                    ],
                                    style={
                                        'padding': '15px',
                                        'fontSize': '18px',
                                        'color': '#4b5563'
                                    }
                                )
                            ],
                            style={
                                'backgroundColor': '#ffffff',
                                'borderRadius': '12px',
                                'boxShadow': '0px 8px 16px rgba(0, 0, 0, 0.1)',
                                'padding': '20px',
                                'width': '78%',
                                'maxWidth': '900px',
                                'margin': '0 auto',
                                'maxHeight': 'calc(100vh - 140px)',
                                'overflowY': 'auto',
                                'position': 'relative'
                            }
                        )
                    ],
                    style={
                        'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                        'borderRadius': '12px',
                        'boxShadow': '0px 8px 16px rgba(0, 0, 0, 0.2)',
                        'padding': '20px',
                        'width': '95%',
                        'maxWidth': '950px',
                        'margin': '0 auto',
                        'maxHeight': 'calc(100vh - 140px)',
                        'position': 'relative'
                    }
                )
            ],
            style={
                'textAlign': 'center',
                'position': 'relative',
                'backgroundImage': 'url(/assets/reservoir.png)',
                'backgroundSize': 'cover',
                'backgroundPosition': 'center',
                'backgroundRepeat': 'no-repeat',
                'width': '100%',
                'height': '100%',
                'maxHeight': 'calc(100vh - 140px)',
                'overflowY': 'auto'
            }
        )

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            tank_info_display,
                            style={
                                'background': 'rgba(255, 255, 255, 0.8)',
                                'borderRadius': '8px',
                                'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                                'padding': '20px',
                                'margin': 'auto',
                                'position': 'relative',
                                'maxHeight': 'calc(100vh - 140px)',
                            }
                        )
                    ],
                    style={
                        'position': 'relative',
                        'backgroundImage': 'url(/assets/reservoir.png)',
                        'backgroundSize': 'contain',
                        'backgroundPosition': 'center',
                        'backgroundRepeat': 'no-repeat',
                        'width': '100%',
                        'height': '100%',
                        'maxHeight': 'calc(100vh - 140px)',
                        'overflowY': 'auto',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    }
                )
            ]
        )
    return ""


"--------------------------- Callback Analysis -----------------------------"


@app.callback(
    Output('adjusted-input', 'style'),
    Input('smooth', 'value')
)
def update_additional_inputs_campbell(analytic_model):
    if analytic_model == 'Yes':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('campbell-input', 'style'),
    Input('campbell-custom', 'value')
)
def update_additional_inputs_campbell(analytic_model):
    if analytic_model == 'Yes':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('havlena-input', 'style'),
    Input('havlena-custom', 'value')
)
def update_additional_inputs_havlena(analytic_model):
    if analytic_model == 'Yes':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('analytic-input', 'style'),
    Input('analytic-method', 'value')
)
def update_additional_inputs_poes(analytic_model):
    if analytic_model == 'Yes':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('analysis-info-content',
           'children'),
    Input('analysis-submit-button', 'n_clicks'),
    State('freq-analysis', 'value'),
    State('position', 'value'),
    State('smooth', 'value'),
    State('k', 'value'),
    State('s', 'value'),
    State('campbell-custom', 'value'),
    State('x1-c', 'value'),
    State('y1-c', 'value'),
    State('x2-c', 'value'),
    State('y2-c', 'value'),
    State('havlena-custom', 'value'),
    State('x1-h', 'value'),
    State('y1-h', 'value'),
    State('x2-h', 'value'),
    State('y2-h', 'value'),
    State('analytic-method', 'value'),
    State('inferred-POES', 'value'),
    State('graphic', 'value')
)
def display_analysis_data(n_clicks,
                          freq_analysis,
                          position,
                          smooth,
                          k,
                          s,
                          campbell_custom,
                          x1_c,
                          y1_c,
                          x2_c,
                          y2_c,
                          havlena_custom,
                          x1_h,
                          y1_h,
                          x2_h,
                          y2_h,
                          analytic_method,
                          inferred_POES,
                          graphic):
    if n_clicks > 0:
        if not (freq_analysis and position and smooth):
            return html.Div("Please ensure all fields are filled out "
                            "correctly.",
                            style={'color': 'red'})

        # Tank
        global global_tank, global_analysis

        # Frequency and position
        freq_analysis = str(freq_analysis) if freq_analysis else None
        position = str(position) if position else None

        # smooth
        if smooth == 'Yes':
            smooth = True

        elif smooth == 'No':
            smooth = False

        global_analysis = pt.Analysis(
            tank_class=global_tank,
            freq=freq_analysis,
            position=position,
            smooth=smooth,
            s=s,
            k=k
        )

        name_aquifer = ''
        if isinstance(global_analysis.tank_class.aquifer, Fetkovich):
            name_aquifer = 'Fetkovich Model'
        elif isinstance(global_analysis.tank_class.aquifer, CarterTracy):
            name_aquifer = 'Carter Tracy Model'

        '--------------------- Campbell Plot ---------------------------'
        data2 = global_analysis.campbell_data()
        # Campbell Plot
        fig_campbell = go.Figure()
        if campbell_custom == 'Yes':
            fig_campbell.add_trace(go.Scatter(
                x=data2["Np"],
                y=data2["F/Eo+Efw"],
                mode='markers',
                marker=dict(color='blue', size=10),
                name='Data Points'
            ))
            # Custom line
            slope = (y2_c - y1_c) / (x2_c - x1_c)
            intercept = y1_c - slope * x1_c
            x_values = np.linspace(min(data2["Np"]), max(data2["Np"]), 100)
            y_values = slope * x_values + intercept
            fig_campbell.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                line=dict(color='red'),
                name='Custom Line'
            ))

            fig_campbell.update_layout(
                title='Campbell Graph',
                xaxis=dict(
                    title='Np Cumulative Oil Production [MMStb]',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                yaxis=dict(
                    title='F/Eo+Efw',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                template='plotly_white',
                annotations=[
                    go.layout.Annotation(
                        x=data2["Np"].min(),
                        y=data2["F/Eo+Efw"].max(),
                        text="Graph that gives an<br>idea of the energy<br>"
                             "contribution of an aquifer",
                        showarrow=True,
                        font=dict(size=12, color='black'),
                        bgcolor='grey',
                        bordercolor='black'
                    ),
                    go.layout.Annotation(
                        text=f"Campbell of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        xanchor="center",
                        y=1.15,
                        yanchor="top",
                        showarrow=False,
                        font=dict(size=22)
                    )
                ]
            )
        else:
            fig_campbell.add_trace(go.Scatter(
                x=data2["Np"],
                y=data2["F/Eo+Efw"],
                mode='markers',
                marker=dict(color='blue', size=10),
                name='Data Points'
            ))

            slope2, intercept2, r, p, se = stats.linregress(data2["Np"],
                                                            data2["F/Eo+Efw"])
            fig_campbell.add_trace(go.Scatter(
                x=data2["Np"],
                y=slope2 * np.array(data2["Np"]) + intercept2,
                mode='lines',
                line=dict(color='green'),
                name='Regression Line'
            ))

            fig_campbell.update_layout(
                title='Campbell Graph',
                xaxis=dict(
                    title='Np Cumulative Oil Production [MMStb]',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                yaxis=dict(
                    title='F/Eo+Efw',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                template='plotly_white',
                annotations=[
                    go.layout.Annotation(
                        x=data2["Np"].min(),
                        y=data2["F/Eo+Efw"].max(),
                        text="Graph that gives an<br>idea of the energy"
                             "<br>contribution of an aquifer",
                        showarrow=True,
                        font=dict(size=12, color='black'),
                        bgcolor='skyblue',
                        bordercolor='black'
                    ),
                    go.layout.Annotation(
                        text=f"Campbell of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        xanchor="center",
                        y=1.15,
                        yanchor="top",
                        showarrow=False,
                        font=dict(size=22)
                    )
                ]
            )

        '---------------------- Havlena and Odeh --------------------------'
        # Havlena Plot
        fig_havlena = go.Figure()
        data = global_analysis.havlena_oded_data()
        if havlena_custom == 'Yes':
            fig_havlena.add_trace(go.Scatter(
                x=data["Eo+Efw"],
                y=data["F-We"],
                mode='markers',
                marker=dict(color='blue', size=10),
                name='Data Points'
            ))
            # Custom line with selected points
            slope = (y2_h - y1_h) / (x2_h - x1_h)
            intercept = y1_h - slope * x1_h
            x_values = np.linspace(min(data["Eo+Efw"]), max(data["Eo+Efw"]),
                                   100)
            y_values = slope * x_values + intercept

            fig_havlena.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                line=dict(color='green', width=3, dash='dash'),
                name='Custom Line'
            ))

            fig_havlena.update_layout(
                title=f'Graphical Method - {name_aquifer}',
                xaxis=dict(
                    title='Eo+Efw',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                yaxis=dict(
                    title='F-We',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                template='plotly_white',
                annotations=[
                    go.layout.Annotation(
                        x=data["Eo+Efw"].min(),
                        y=data["F-We"].max(),
                        text="N [MMStb]: {:.2f}".format(slope / 1000000),
                        showarrow=True,
                        font=dict(size=12, color='black'),
                        bgcolor='yellow',
                        bordercolor='black'
                    ),
                    go.layout.Annotation(
                        text=f"Havlena and Odeh of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        xanchor="center",
                        y=1.15,
                        yanchor="top",
                        showarrow=False,
                        font=dict(size=22)
                    )
                ]
            )
        else:
            fig_havlena.add_trace(go.Scatter(
                x=data["Eo+Efw"],
                y=data["F-We"],
                mode='markers',
                marker=dict(color='blue', size=10),
                name='Data Points'
            ))

            slope, intercept, r, p, se = stats.linregress(data["Eo+Efw"],
                                                          data["F-We"])
            fig_havlena.add_trace(go.Scatter(
                x=data["Eo+Efw"],
                y=slope * np.array(data["Eo+Efw"]) + intercept,
                mode='lines',
                line=dict(color='red'),
                name='Regression Line'
            ))

            fig_havlena.update_layout(
                title=f'Graphical Method - {name_aquifer}',
                xaxis=dict(
                    title='Eo+Efw',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                yaxis=dict(
                    title='F-We',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True
                ),
                template='plotly_white',
                annotations=[
                    go.layout.Annotation(
                        x=data["Eo+Efw"].min(),
                        y=data["F-We"].max(),
                        text="N [MMStb]: {:.2f}".format(slope / 1000000),
                        font=dict(size=12, color='black'),
                        bgcolor='yellow',
                        bordercolor='black'
                    ),
                    go.layout.Annotation(
                        text=f"Havlena and Odeh of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        xanchor="center",
                        y=1.15,
                        yanchor="top",
                        showarrow=False,
                        font=dict(size=22)
                    )
                ]
            )
        '--------------- Observed Pressure vs Time Plot --------------------'
        df_press = global_analysis.tank_class.get_pressure_df()
        df_press["START_DATETIME"] = pd.to_datetime(df_press['START_DATETIME'])
        df_press = df_press.sort_values(by='START_DATETIME')

        fig_p_vs_t = go.Figure()

        fig_p_vs_t.add_trace(go.Scatter(
            x=df_press['START_DATETIME'],
            y=df_press['PRESSURE_DATUM'],
            mode='markers',
            marker=dict(color='green'),
            name='Observed Pressure',
        ))

        fig_p_vs_t.update_layout(
            title=f"Pressure per Date",
            xaxis=dict(
                title='Date',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                linecolor='black',
                gridwidth=1,
                griddash='dash',
                mirror=True,
                type='date'
            ),
            yaxis=dict(
                title='Pressure [PSI]',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"Observed Pressure vs Time fof {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )
        "-------------------- Avg Pressure vs Time ------------------------"
        # Average Pressure Data
        df_press_avg = global_analysis.mat_bal_df()
        df_press_avg['START_DATETIME'] = pd.to_datetime(
            df_press_avg['START_DATETIME'])
        df_press_avg = df_press_avg.sort_values(by='START_DATETIME')

        fig_avg_vs_t = go.Figure()

        if global_analysis.smooth:
            fig_avg_vs_t.add_trace(go.Scatter(
                x=df_press_avg['START_DATETIME'],
                y=df_press_avg['AVG_PRESS'],
                mode='markers',
                marker=dict(color='red'),
                name='Avg Pressure'
            ))
            fig_avg_vs_t.add_trace(go.Scatter(
                x=df_press_avg['START_DATETIME'],
                y=df_press_avg['PRESSURE_DATUM'],
                mode='lines',
                line=dict(color='blue'),
                name='Avg Pressure (Smoothed)'
            ))
        else:
            fig_avg_vs_t.add_trace(go.Scatter(
                x=df_press_avg['START_DATETIME'],
                y=df_press_avg['PRESSURE_DATUM'],
                mode='markers',
                marker=dict(color='red'),
                name='Avg Pressure'
            ))

        fig_avg_vs_t.update_layout(
            title=f"Average Pressure per Date",
            xaxis=dict(
                title='Date',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True,
                type='date'
            ),
            yaxis=dict(
                title='Average Pressure [PSI]',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"Average Pressure vs Time of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        '-------------- Flow rate vs Time (Tank) --------------'
        df_prod = global_analysis.mat_bal_df()
        df_prod['START_DATETIME'] = pd.to_datetime(df_prod['START_DATETIME'])
        df_prod = df_prod.sort_values(by='START_DATETIME')

        df_prod['OIL_RATE'] = df_prod['OIL_CUM_TANK'].diff().fillna(0)
        df_prod['WATER_RATE_COL'] = df_prod['WATER_CUM_TANK'].diff().fillna(0)

        fig_fr_time = go.Figure()

        fig_fr_time.add_trace(go.Scatter(
            x=df_prod['START_DATETIME'],
            y=df_prod['OIL_RATE'],
            mode='lines',
            line=dict(color='black'),
            name='Oil Flow Rate'
        ))

        fig_fr_time.add_trace(go.Scatter(
            x=df_prod['START_DATETIME'],
            y=df_prod['WATER_RATE_COL'],
            mode='lines',
            line=dict(color='blue'),
            name='Water Flow Rate'
        ))

        fig_fr_time.update_layout(
            title="Production Rates vs Time",
            xaxis=dict(
                title='Date',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True,
                type='date'
            ),
            yaxis=dict(
                title='Flow Rate [Stb/year]',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"Flow Rate vs Time (Tank) of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        "----------------- Cumulative vs Pressure -----------------------"
        df_press_avg = global_analysis.mat_bal_df()
        df_press_avg['START_DATETIME'] = pd.to_datetime(
            df_press_avg['START_DATETIME'])
        df_press_avg = df_press_avg.sort_values(by='PRESSURE_DATUM')

        colors = ["black", "blue"]
        columns = ['OIL_CUM_TANK', 'WATER_CUM_TANK']

        fig_avg_pressure = go.Figure()

        for i, col in enumerate(columns):
            fig_avg_pressure.add_trace(go.Scatter(
                x=df_press_avg['PRESSURE_DATUM'],
                y=df_press_avg[col],
                mode='markers',
                marker=dict(color=colors[i]),
                name=col
            ))

        fig_avg_pressure.update_layout(
            title=f"Average Pressure vs Cumulative Production",
            xaxis=dict(
                title='Average Pressure',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            yaxis=dict(
                title='Cumulative Production',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"AVG Pressure vs Cumulative Production of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        "---------------- Cumulative vs Time (Tank) --------------------"
        df_press_avg = global_analysis.mat_bal_df()
        df_press_avg['START_DATETIME'] = pd.to_datetime(
            df_press_avg['START_DATETIME'])
        df_press_avg = df_press_avg.sort_values(by='START_DATETIME')

        fig_cum_time = go.Figure()

        colors = ["black", "blue"]
        columns = ["OIL_CUM_TANK", "WATER_CUM_TANK"]

        for i, col in enumerate(columns):
            fig_cum_time.add_trace(go.Scatter(
                x=df_press_avg['START_DATETIME'],
                y=df_press_avg[col],
                mode='lines',
                line=dict(color=colors[i]),
                name=col
            ))

        fig_cum_time.update_layout(
            title=f"Cumulative Production per Date - {global_analysis.tank_class.name.replace('_', ' ').upper()}",
            xaxis=dict(
                title='Date',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True,
                type='date'
            ),
            yaxis=dict(
                title='Cumulative Production',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f" Cumulative vs Time (Tank) of  {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        "--------------- Flow rate vs Time (by Well) -------------------"
        # Production Data
        df_prod = global_analysis.tank_class.get_production_df()
        df_prod['START_DATETIME'] = pd.to_datetime(df_prod['START_DATETIME'])
        df_prod = df_prod.sort_values(by='START_DATETIME')

        df_prod['OIL_RATE'] = df_prod.groupby('WELL_BORE')[
            'OIL_CUM'].diff().fillna(
            0)
        df_prod['WATER_RATE'] = df_prod.groupby('WELL_BORE')[
            'WATER_CUM'].diff().fillna(0)

        fig_fr_well = go.Figure()
        wells = df_prod['WELL_BORE'].unique()
        colors = px.colors.qualitative.T10

        for i, well in enumerate(wells):
            well_data = df_prod[df_prod['WELL_BORE'] == well]
            dates = well_data['START_DATETIME']

            fig_fr_well.add_trace(go.Scatter(
                x=dates,
                y=well_data['OIL_RATE'],
                mode='lines',
                line=dict(color=colors[i % len(colors)]),
                name=f"Oil Rate - {well}"
            ))

            fig_fr_well.add_trace(go.Scatter(
                x=dates,
                y=well_data['WATER_RATE'],
                mode='lines',
                line=dict(color=colors[i % len(colors)], dash='dash'),
                name=f"Water Rate - {well}"
            ))

        fig_fr_well.update_layout(
            title=f"Flow Rate vs Time by Well - {global_analysis.tank_class.name.replace('_', ' ').upper()}",
            xaxis=dict(
                title='Date',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True,
                type='date'
            ),
            yaxis=dict(
                title='Flow Rate [Stb/year]',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"Flow rate vs Time (by Well) of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        "------------------- Cumulative per Well --------------------"
        df_prod = global_analysis.tank_class.get_production_df()
        df_prod['START_DATETIME'] = pd.to_datetime(df_prod['START_DATETIME'])
        df_prod = df_prod.sort_values(by='START_DATETIME')

        df_prod_well = df_prod.groupby('WELL_BORE')[
            ['OIL_CUM', 'WATER_CUM']].sum().reset_index()

        fig_cum_well = go.Figure()

        bar_width = 0.35
        r1 = list(range(len(df_prod_well)))
        r2 = [x + bar_width for x in r1]

        fig_cum_well.add_trace(go.Bar(
            x=df_prod_well['WELL_BORE'],
            y=df_prod_well['OIL_CUM'],
            name='Oil Cumulative',
            marker=dict(color='black'),
            width=bar_width
        ))

        fig_cum_well.add_trace(go.Bar(
            x=df_prod_well['WELL_BORE'],
            y=df_prod_well['WATER_CUM'],
            name='Water Cumulative',
            marker=dict(color='blue'),
            width=bar_width
        ))

        fig_cum_well.update_layout(
            title=f"Cumulative Production per Well - {global_analysis.tank_class.name.replace('_', ' ').upper()}",
            xaxis=dict(
                title='Well',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            yaxis=dict(
                title='Cumulative Production [Stb]',
                titlefont=dict(size=18, family='Arial, sans-serif'),
                tickfont=dict(size=14, family='Arial, sans-serif'),
                showgrid=True,
                gridcolor='#D1D1D1',
                gridwidth=1,
                griddash='dash',
                linecolor='black',
                mirror=True
            ),
            barmode='group',
            template='plotly_white',
            annotations=[
                go.layout.Annotation(
                    text=f"Cumulative Production per Well of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    xanchor="center",
                    y=1.15,
                    yanchor="top",
                    showarrow=False,
                    font=dict(size=22)
                )
            ]
        )

        '----------------------- OPTIONS ------------------------------------'
        if analytic_method == 'Yes':
            # Analytic Method
            data_analytic = global_analysis.analytic_method(inferred_POES,
                                                            option='data')

            fig_analytic = go.Figure()

            # Observed Pressure
            fig_analytic.add_trace(go.Scatter(
                x=data_analytic["START_DATETIME"],
                y=data_analytic["PRESSURE_DATUM"],
                mode='markers',
                marker=dict(color='blue', size=10),
                name='Observed Pressure'
            ))

            # Calculated Pressure
            fig_analytic.add_trace(go.Scatter(
                x=data_analytic["START_DATETIME"],
                y=data_analytic['PRESS_CALC'],
                mode='lines',
                line=dict(color='green'),
                name='Calculated Pressure'
            ))
            fig_analytic.update_layout(
                title=f"Analytic Method of {global_analysis.tank_class.name.replace('_', ' ').upper()}",
                xaxis=dict(
                    title='Time (Years)',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True,
                    type='date'
                ),
                yaxis=dict(
                    title='Pressure (PSI)',
                    titlefont=dict(size=18, family='Arial, sans-serif'),
                    tickfont=dict(size=14, family='Arial, sans-serif'),
                    showgrid=True,
                    gridcolor='#D1D1D1',
                    gridwidth=1,
                    griddash='dash',
                    linecolor='black',
                    mirror=True,
                    range=[0, 4000]
                ),
                template='plotly_white',
                annotations=[
                    go.layout.Annotation(
                        text=f"Pressure vs Time with {name_aquifer}",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        xanchor="center",
                        y=1.15,
                        yanchor="top",
                        showarrow=False,
                        font=dict(size=22)
                    )
                ]
            )
            if graphic == 'None':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Observed Pressure vs Time':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_p_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Pressure':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_avg_pressure),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (by Well)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production per well':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_analytic),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })

        elif analytic_method == 'No' and global_analysis.tank_class.aquifer is None:
            if graphic == 'None':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Observed Pressure vs Time':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_p_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Pressure':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_avg_pressure),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (by Well)':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production per well':
                return html.Div([
                    dcc.Graph(figure=fig_campbell),
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })

        elif (analytic_method == 'No'
              and (isinstance(global_analysis.tank_class.aquifer, Fetkovich)
                   or isinstance(global_analysis.tank_class.aquifer,
                                 CarterTracy))):
            if graphic == 'None':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Observed Pressure vs Time':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_p_vs_t),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Pressure':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_avg_pressure),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production vs Time (Tank)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_time),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Flow Rate vs Time (by Well)':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_fr_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })
            elif graphic == 'Cumulative Production per well':
                return html.Div([
                    dcc.Graph(figure=fig_havlena),
                    dcc.Graph(figure=fig_avg_vs_t),
                    dcc.Graph(figure=fig_cum_well),
                ], style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 400px)'
                })

    return html.Div(['Submit the form to see the analysis results.'])


"----------------------------------- Run -----------------------------------"
# server
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
