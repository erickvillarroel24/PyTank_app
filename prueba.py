import base64
import io
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import pytank as pt

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = html.Div([
    # Location component to track the current URL
    dcc.Location(id='url', refresh=False),
    # Navbar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Well",
                                    href="/well")),
            dbc.NavItem(dbc.NavLink("Fluid Models",
                                    href="/fluid-models")),
            dbc.NavItem(dbc.NavLink("Tank",
                                    href="/tank")),
            dbc.NavItem(dbc.NavLink("Analysis",
                                    href="/analysis")),
        ],
        brand="Pytank App",
        brand_href="#",
        color="primary",
        dark=True,
    ),

    # Content area where the module content will be displayed
    html.Div(id='page-content')
])

# Layout for the Well module
well_layout = html.Div([
    dcc.Store(id='store-well', data={}),
    html.H1(
        "Well Module",
        style={
            'textAlign': 'center',
            'marginTop': '10px',
            'backgroundColor': '#f0f0f0',
            'padding': '10px',
            'borderRadius': '5px'
        }
    ),

    html.Div([
        html.Div([
            html.H2(
                "Well data upload and configuration",
                style={
                    'textAlign': 'center',
                    'marginTop': '0px',
                    'fontSize': '20px',
                    'width': '100%',
                    'padding': '10px',
                    'boxSizing': 'border-box',
                    'backgroundColor': '#2172F9'
                }
            ),

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
                html.Div(
                    id='prod-upload-status',
                    style={
                        'marginTop': '10px',
                        'padding': '10px',
                        'backgroundColor': '#d4edda',
                        'border': '1px solid #c3e6cb',
                        'borderRadius': '5px'
                    }
                ),
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
                html.Div(
                    id='press-upload-status',
                    style={
                        'marginTop': '10px',
                        'padding': '10px',
                        'backgroundColor': '#d4edda',
                        'border': '1px solid #c3e6cb',
                        'borderRadius': '5px'
                    }
                ),
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.Label("Production Frequency"),
                dcc.Input(
                    id='freq-prod',
                    type='text',
                    placeholder='Enter production frequency',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Pressure Frequency"),
                dcc.Input(
                    id='freq-press',
                    type='text',
                    placeholder='Enter pressure frequency',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

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
                    'Add Another Well Name',
                    id='add-well-button',
                    n_clicks=0,
                    style={'width': '100%', 'marginTop': '10px'}
                )
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
            'height': 'calc(100vh - 60px)',
            'overflowY': 'auto',
            'backgroundColor': '#f8f9fa'
        }),

        html.Div([
            html.H2(
                "Results Area",
                style={
                    'textAlign': 'center',
                    'marginBottom': '10px',
                    'backgroundColor': '#f0f0f0'
                }
            ),
            html.P(
                "This section shows the production and pressure"
                " information for each well according to time. Make sure "
                "you enter the correct parameters.",
                style={
                    'fontSize': '16px',
                    'lineHeight': '1.5',
                    'textAlign': 'justify',
                    'marginBottom': '20px'
                }
            ),
            html.Div(
                id='well-info-content',
                style={
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 140px)',
                    'padding': '10px'
                }
            )
        ], id='well-info', style={
            'width': '75%',
            'padding': '20px',
            'boxSizing': 'border-box',
            'backgroundColor': '#f8f9fa',
            'marginBottom': '80px',
        })
    ], style={
        'display': 'flex',
        'height': 'calc(90vh - 60px)',
        'overflow': 'hidden'
    })
])

# Layout for the Fluid Models module
fluid_models_layout = html.Div([
    dcc.Store(id='store-fluid', data={}),
    html.H1(
        "Fluid Models Module",
        style={
            'textAlign': 'center',
            'marginTop': '10px',
            'backgroundColor': '#f0f0f0',
            'padding': '10px',
            'borderRadius': '5px'
        }
    ),
    html.Div([
        html.Div([
            html.H2(
                "Fluid Models data upload and configuration",
                style={
                    'textAlign': 'center',
                    'marginTop': '0px',
                    'fontSize': '20px',
                    'width': '100%',
                    'padding': '10px',
                    'boxSizing': 'border-box',
                    'backgroundColor': '#2172F9'
                }
            ),

            html.Div([
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
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.Label("Oil Temperature"),
                dcc.Input(
                    id='temp-oil',
                    type='number',
                    placeholder='Enter oil temperature',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Water Salinity"),
                dcc.Input(
                    id='salinity-water',
                    type='number',
                    placeholder='Enter water salinity',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Water Temperature"),
                dcc.Input(
                    id='temp-water',
                    type='number',
                    placeholder='Enter water temperature',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Units"),
                dcc.Input(
                    id='units',
                    type='number',
                    placeholder='Enter units',
                    style={'width': '100%'}
                )
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
            'height': 'calc(100vh - 60px)',
            'overflowY': 'auto',
            'backgroundColor': '#f8f9fa'
        }),

        html.Div([
            html.H2(
                "Results Area",
                style={
                    'textAlign': 'center',
                    'marginBottom': '10px',
                    'backgroundColor': '#f0f0f0'
                }
            ),
            html.P(
                "This section shows the results for fluid models based"
                " on the uploaded CSV and input parameters. Make sure you "
                "enter the correct parameters.",
                style={
                    'fontSize': '16px',
                    'lineHeight': '1.5',
                    'textAlign': 'justify',
                    'marginBottom': '20px'
                }
            ),
            html.Div(
                id='fluid-info-content',
                style={
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 140px)',
                    'padding': '10px'
                }
            )
        ], id='fluid-info', style={
            'width': '75%',
            'padding': '20px',
            'boxSizing': 'border-box',
            'backgroundColor': '#f8f9fa'
        })
    ], style={
        'display': 'flex',
        'height': 'calc(90vh - 60px)',
        'overflow': 'hidden'
    })
])

tank_layout = html.Div([
    dcc.Store(id='store-tank', data={}),
    html.H1(
        "Tank Module",
        style={
            'textAlign': 'center',
            'marginTop': '10px',
            'backgroundColor': '#f0f0f0',
            'padding': '10px',
            'borderRadius': '5px'
        }
    ),
    html.Div([
        html.Div([
            html.H2(
                "Tank data configuration",
                style={
                    'textAlign': 'center',
                    'marginTop': '0px',
                    'fontSize': '20px',
                    'width': '100%',
                    'padding': '10px',
                    'boxSizing': 'border-box',
                    'backgroundColor': '#2172F9'
                }
            ),
            # Tank properties
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
                    placeholder='Enter initial water saturation [dec]',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Water compressibility"),
                dcc.Input(
                    id='water-compressibility',
                    type='number',
                    placeholder='Enter water compressibility [dec]',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Formation compressibility"),
                dcc.Input(
                    id='formation-compressibility',
                    type='number',
                    placeholder='Enter formation compressibility [dec]',
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '10px'}),

                html.Label("Aquifer Model"),
                dcc.Dropdown(
                    id='aquifer-model',
                    options=[
                        {'label': 'None', 'value': 'None'},
                        {'label': 'Fetkovich', 'value': 'Fetkovich'},
                        {'label': 'Carter Tracy', 'value': 'Carter Tracy'},
                    ],
                    placeholder='Select Aquifer Model',
                    style={'width': '100%'}
                ),
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
            ], style={'textAlign': 'center', 'marginTop': '10px',
                      'marginBottom': '80px'}),
        ], style={
            'width': '20%',
            'padding': '20px',
            'borderRight': '1px solid black',
            'boxSizing': 'border-box',
            'height': 'calc(100vh - 60px)',
            'overflowY': 'auto',
            'backgroundColor': '#f8f9fa'
        }),

        html.Div([
            html.H2(
                "Results Area",
                style={
                    'textAlign': 'center',
                    'marginBottom': '10px',
                    'backgroundColor': '#f0f0f0'
                }
            ),
            html.P(
                "This section displays the tank configuration with "
                "specific properties selected. Make sure you put the correct "
                "properties",
                style={
                    'fontSize': '16px',
                    'lineHeight': '1.5',
                    'textAlign': 'justify',
                    'marginBottom': '20px'
                }
            ),
            html.Div(
                id='tank-info-content',
                style={
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 140px)',
                    'padding': '10px'
                }
            )
        ], id='tank-info', style={
            'width': '75%',
            'padding': '20px',
            'boxSizing': 'border-box',
            'backgroundColor': '#f8f9fa'
        })
    ], style={
        'display': 'flex',
        'height': 'calc(90vh - 60px)',
        'overflow': 'hidden'
    })
])


# Callback to switch between modules based on URL
# Update the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/fluid-models':
        return fluid_models_layout
    elif pathname == '/tank':
        return tank_layout
    elif pathname == '/analysis':
        pass
    else:
        return well_layout


# Helper function to parse uploaded CSV data
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


# Callback for handling the production CSV upload
@app.callback(
    Output('prod-upload-status', 'children'),
    Input('upload-prod-data', 'contents'),
    State('upload-prod-data', 'filename')
)
def update_prod_output(contents, filename):
    if contents is not None:
        df = parse_data(contents, filename)
        if df is not None:
            return html.Div([f'{filename} uploaded successfully!'])
        else:
            return html.Div(
                ['There was an error processing the production data.'])
    return html.Div(['Upload production data to start.'])


# Callback for handling the pressure CSV upload
@app.callback(
    Output('press-upload-status', 'children'),
    Input('upload-press-data', 'contents'),
    State('upload-press-data', 'filename')
)
def update_press_output(contents, filename):
    if contents is not None:
        df = parse_data(contents, filename)
        if df is not None:
            return html.Div([f'{filename} uploaded successfully!'])
        else:
            return html.Div(
                ['There was an error processing the pressure data.'])
    return html.Div(['Upload pressure data to start.'])


# Callback for handling the fluid models CSV upload
@app.callback(
    Output('fluid-upload-status', 'children'),
    Input('upload-fluid-data', 'contents'),
    State('upload-fluid-data', 'filename')
)
def update_fluid_output(contents, filename):
    if contents is not None:
        df = parse_data(contents, filename)
        if df is not None:
            return html.Div([f'{filename} uploaded successfully!'])
        else:
            return html.Div(
                ['There was an error processing the fluid models data.'])
    return html.Div(['Upload fluid models data to start.'])


# Helper function to parse the uploaded files
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))


# Callback to add new input fields for well names dynamically
@app.callback(
    Output('dynamic-well-inputs', 'children'),
    Input('add-well-button', 'n_clicks'),
    State('dynamic-well-inputs', 'children')
)
def add_well_input(n_clicks, current_children):
    if n_clicks > 0:
        new_input = dcc.Input(
            id={'type': 'well-name', 'index': len(current_children)},
            type='text',
            placeholder='Enter well name',
            style={'width': '100%'}
        )
        return current_children + [new_input]
    return current_children


# Global variables
global_wells_info = None
global_oil_model = None
global_water_model = None
global_tank = None


# Callback to process the uploaded CSV files and user inputs
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
        global_wells_info = pt.search_wells(
            wells=wells,
            well_names=my_wells
        )

        # Display wells information
        well_info_display = []
        for well in global_wells_info:
            prod_data_df = well.prod_data.data
            press_data_df = well.press_data.data

            well_info_display.append(html.H4(f"Well: {well.name}"))

            if not prod_data_df.empty or not press_data_df.empty:
                well_info_display.append(
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.H5("Production Data"),
                                dcc.Graph(
                                    figure={
                                        'data': [
                                            {'x': prod_data_df.index,
                                             'y': prod_data_df[col],
                                             'type': 'line', 'name': col}
                                            for col in ['OIL_CUM',
                                                        'WATER_CUM',
                                                        'LIQ_CUM']
                                            if col in prod_data_df.columns
                                        ],
                                        'layout': {
                                            'title': 'Production Data'
                                        }
                                    }
                                )
                            ]),
                            width=6
                        ),
                        dbc.Col(
                            html.Div([
                                html.H5("Pressure Data"),
                                dcc.Graph(
                                    figure={
                                        'data': [
                                            {'x': press_data_df.index,
                                             'y': press_data_df[col],
                                             'type': 'line', 'name': col}
                                            for col in press_data_df.columns
                                        ],
                                        'layout': {
                                            'title': 'Pressure Data'
                                        }
                                    }
                                )
                            ]),
                            width=6
                        )
                    ])
                )

        return well_info_display
    return []

@app.callback(
    Output('store-well', 'data'),
    Input('well-submit-button', 'n_clicks'),
    State('upload-prod-data', 'contents'),
    State('upload-press-data', 'contents'),
    State('freq-prod', 'value'),
    State('freq-press', 'value'),
    State('dynamic-well-inputs', 'children'))
def store_well_data(n_clicks, prod_content, press_content, freq_prod,
                    freq_press, well_inputs):
    if n_clicks > 0 and prod_content is not None and press_content is not None:
        # Process production and pressure data
        prod_data = parse_contents(prod_content)
        press_data = parse_contents(press_content)

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
        global_wells_info = pt.search_wells(
            wells=wells,
            well_names=my_wells
        )

        return {
            'global_wells_info': global_wells_info
        }
    return {}

def store_wells_data(n_clicks, prod_contents, press_contents, freq_prod,
                    freq_press, well_inputs):
    if n_clicks > 0:
        return {
            'prod_contents': prod_contents,
            'press_contents': press_contents,
            'freq_prod': freq_prod,
            'freq_press': freq_press,
            'well_inputs': well_inputs
        }
    return dash.no_update


# Callback to process the uploaded CSV files and user inputs (Fluid Models)
@app.callback(
    Output('fluid-info-content', 'children'),
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

        # Create oil and water models
        global_oil_model = pt.OilModel(
            data_pvt=fluid_df,
            temperature=temp_oil
        )

        global_water_model = pt.WaterModel(
            salinity=salinity_water,
            temperature=temp_water,
            unit=units
        )

        # Get the DataFrame from the oil model
        df = global_oil_model.data_pvt

        return html.Div([
            html.H3("Fluid Models Data Results"),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            )
        ])
    return ""

@app.callback(
    Output('store-fluid', 'data'),
    Input('fluid-submit-button', 'n_clicks'),
    State('upload-fluid-data', 'contents'),
    State('temp-oil', 'value'),
    State('salinity-water', 'value'),
    State('temp-water', 'value'),
    State('units', 'value'))
def store_fluid_data(n_clicks, fluid_contents, temp_oil,
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

        # Create oil and water models
        global_oil_model = pt.OilModel(
            data_pvt=fluid_df,
            temperature=temp_oil
        )

        global_water_model = pt.WaterModel(
            salinity=salinity_water,
            temperature=temp_water,
            unit=units
        )
        return {
            'oil_model': global_oil_model,
            'water_model': global_water_model
        }
    return {}
def store_fluid_models_data(n_clicks, fluid_info, temp_oil, salinity_water,
                            temp_water, units):
    if n_clicks > 0:
        return {
            'fluid_contents': fluid_info,
            'temp_oil': temp_oil,
            'salinity_water': salinity_water,
            'temp_water': temp_water,
            'units': units
        }
    return dash.no_update


@app.callback(
    Output('tank-info-content', 'children'),
    [Input('tank-submit-button', 'n_clicks')],
    [State('store-well', 'data'),
     State('tank-name', 'value'),
     State('initial-pressure', 'value'),
     State('initial-water-saturation', 'value'),
     State('water-compressibility', 'value'),
     State('formation-compressibility', 'value'),
     State('aquifer-model', 'value')]
)
def update_output_tank(n_clicks, store_well, store_fluid, tank_name, initial_pressure,
                       initial_water_saturation, water_compressibility,
                       formation_compressibility, aquifer_model):
    if n_clicks > 0:
        if not all([tank_name, initial_pressure, initial_water_saturation,
                    water_compressibility, formation_compressibility,
                    aquifer_model]):
            return html.Div(
                "Please ensure all fields are filled out correctly.",
                style={'color': 'red'})

        if store_well and 'global_wells_info' in store_well:
            global_wells_info = store_well['global_wells_info']
        else:
            return html.Div(
                "No well data available. Please submit well data first.",
                style={'color': 'red'})

        if not store_fluid or not all(key in store_fluid for key in ['oil_model', 'water_model']):
            return html.Div("No fluid model data available. Please submit fluid data first.",
                            style={'color': 'red'})

        global_oil_model = store_fluid.get('oil_model')
        global_water_model = store_fluid.get('water_model')

        # Set aquifer to None if 'None' is selected
        if aquifer_model == 'None':
            aquifer_model = None

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
        # Process the tank properties
        tank_info_display = [html.H4(f"Tank: {tank_name}"),
                             html.P(f"Initial Pressure: "
                                    f"{initial_pressure} PSI"),
                             html.P(f"Initial Water Saturation:"
                                    f" {initial_water_saturation} dec"),
                             html.P(f"Water Compressibility: "
                                    f"{water_compressibility} dec"),
                             html.P(f"Formation Compressibility: "
                                    f"{formation_compressibility} dec"),
                             html.P(f"Aquifer Model: {aquifer_model}")]

        return tank_info_display
    return ""


# Callback to store data for Tank module
@app.callback(
    Output('store-tank', 'data'),
    [Input('tank-submit-button', 'n_clicks')],
    [State('tank-info-content', 'children'),
     State('tank-name', 'value'),
     State('initial-pressure', 'value'),
     State('initial-water-saturation', 'value'),
     State('water-compressibility', 'value'),
     State('formation-compressibility', 'value'),
     State('aquifer-model', 'value')]
)
def store_tank_data(n_clicks, tank_info, tank_name, initial_pressure,
                    water_sat, water_comp, form_comp, aquifer):
    if n_clicks > 0:
        return {
            'tank_info': tank_info,
            'tank_name': tank_name,
            'initial_pressure': initial_pressure,
            'water_sat': water_sat,
            'water_comp': water_comp,
            'formation_compressibility': form_comp,
            'aquifer_model': aquifer
        }
    return dash.no_update


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

