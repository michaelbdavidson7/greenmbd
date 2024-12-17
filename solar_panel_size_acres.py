import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Solar Panel Land Utilization Calculator"),
    html.Div([
        html.Label("Land Area (acres):"),
        dcc.Slider(id='land-area', min=1, max=10, step=0.1, value=3,
                   marks={i: f"{i} acres" for i in range(1, 11)}),
        html.Label("Panel Surface Area (sq meters per panel):"),
        dcc.Slider(id='panel-area', min=1, max=10, step=0.1, value=2,
                   marks={i: f"{i} m²" for i in range(1, 11)}),
        html.Label("Power Output per Panel (kW):"),
        dcc.Slider(id='panel-power', min=0.1, max=1, step=0.01, value=0.4,
                   marks={i/10: f"{i/10} kW" for i in range(1, 11)}),
        html.Label("Land Utilization Density (%):"),
        dcc.Slider(id='land-density', min=50, max=90, step=1, value=70,
                   marks={i: f"{i}%" for i in range(50, 91, 5)})
    ], style={"width": "50%", "padding": "20px"}),

    html.Div(id='output-results', style={"margin-top": "30px", "font-size": "20px"}),
    dcc.Graph(id='capacity-graph')
])

# Callback to update the results and graph
@app.callback(
    [
        Output('output-results', 'children'),
        Output('capacity-graph', 'figure')
    ],
    [
        Input('land-area', 'value'),
        Input('panel-area', 'value'),
        Input('panel-power', 'value'),
        Input('land-density', 'value')
    ]
)
def update_output(land_area_acres, panel_area, panel_power, land_density):
    # Convert acres to square meters (1 acre = 4046.86 sq meters)
    land_area_m2 = land_area_acres * 4046.86
    land_density_fraction = land_density / 100

    # Calculate number of panels and system capacity
    num_panels = (land_area_m2 * land_density_fraction) / panel_area
    total_capacity = num_panels * panel_power

    # Display results
    result_text = (
        f"\U0001F333 Land Area: {land_area_acres} acres ({land_area_m2:.2f} m²)\n"
        f"\U0001F4BB Number of Panels: {num_panels:.0f}\n"
        f"\U0001F50B Total System Capacity: {total_capacity:.2f} kW"
    )

    # Create a bar chart to visualize the results
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Panels", "Capacity (kW)"], y=[num_panels, total_capacity],
                         text=[f"{num_panels:.0f}", f"{total_capacity:.2f}"],
                         textposition='auto'))
    fig.update_layout(title="Solar Panel System Overview", yaxis_title="Value")

    return result_text.replace("\n", "  |  "), fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
