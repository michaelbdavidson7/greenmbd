import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Constants
shading_factor = 0.8  # Fraction of usable area after accounting for shading (e.g., 80%)
access_paths_factor = 0.9  # Account for pathways (e.g., 90% of area usable for panels)
# Assume a revenue rate (e.g., $0.10 per kWh)
revenue_rate = 0.10  # USD per kWh
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP
])

# Layout of the app
app.layout = html.Div([
    html.H1("Solar Panel Land Utilization Calculator"),
    html.H4(f"Constants:"),
    html.H5([f"Shading factor: {shading_factor * 100}% ",
    html.I(className="bi bi-info-circle", id="hover-icon", style={"fontSize": "24px", "cursor": "pointer"}),
    dbc.Tooltip(
        "This is an example multiplier when factoring in the shading of other panels/distant trees",
        target="hover-icon",
        placement="right"
    ),
    f" Access paths factor: {access_paths_factor * 100}% ",
        html.I(className="bi bi-info-circle", id="hover-icon2", style={"fontSize": "24px", "cursor": "pointer"}),
    dbc.Tooltip(
        "Access paths are ways to get around the farm, some space must be made for these",
        target="hover-icon2",
        placement="right"
    ), 
    f" Revenue rate: {revenue_rate}/kWH ",
        html.I(className="bi bi-info-circle", id="hover-icon3", style={"fontSize": "24px", "cursor": "pointer"}),
    dbc.Tooltip(
        "$0.10 cents is generally high and unachieveable in grade A sunshine states due to oversaturation, but in grade B and lower its still available. ",
        target="hover-icon3",
        placement="right"
    ), 
]),
    html.Div([
        html.Label("Land Area (acres):"),
        dcc.Slider(id='land-area', min=1, max=15, step=0.1, value=3,
                   marks={i: f"{i} acres" for i in range(1, 16)}),
        html.Label("Land Cost:"),
        dcc.Slider(id='land-cost', min=10000, max=200000, step=10000, value=40000,
                   marks={i: f"{i} acres" for i in range(1, 101)}),
        html.Label("Panel Surface Area (sq meters per panel):"),
        dcc.Slider(id='panel-area', min=1, max=10, step=0.1, value=2,
                   marks={i: f"{i} m²" for i in range(1, 11)}),
        html.Label("Power Output per Panel (kW):"),
        dcc.Slider(id='panel-power', min=0.1, max=1, step=0.01, value=0.4,
                   marks={i/10: f"{i/10} kW" for i in range(1, 11)}),
        html.Label("Land Utilization Density (%):"),
        dcc.Slider(id='land-density', min=50, max=90, step=1, value=60,
                   marks={i: f"{i}%" for i in range(50, 91, 5)}),
        html.Label("Daily Hours of Sunlight (hours):"),
        dcc.Slider(id='sunlight-hours', min=1, max=12, step=0.1, value=3.8,
                   marks={i: f"{i} hrs" for i in range(1, 13)}),
        html.Label("Cost per Panel ($):"),
        dcc.Slider(id='panel-cost', min=100, max=1000, step=10, value=300,
                   marks={i: f"${i}" for i in range(100, 1100, 100)}),
        html.Label("Annual Maintenance/Insurance ($):"),
        dcc.Slider(id='maintenance', min=1000, max=50000, step=5000, value=3000,
                   marks={i: f"${i}" for i in range(1000, 60000, 3000)}),
        html.Label("Additional Costs (Inverters, Wiring, Labor, etc.) ($):"),
        dcc.Slider(id='additional-costs', min=1000, max=510000, step=500, value=200000,
                   marks={i: f"${i:,}" for i in range(10000, 510000, 50000)})
    ], style={"width": "50%", "padding": "20px"}),

    html.Div(id='output-results', style={"margin-top": "30px", "font-size": "20px"}),
    dcc.Graph(id='capacity-graph')
], className="container-fluid")

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
        Input('land-density', 'value'),
        Input('sunlight-hours', 'value'),
        Input('panel-cost', 'value'),
        Input('maintenance', 'value'),
        Input('additional-costs', 'value'),
        Input('land-cost', 'value')
    ]
)
def update_output(land_area_acres, panel_area, panel_power, land_density, sunlight_hours, panel_cost, maintenance, additional_costs, land_cost):
    

    # # Convert acres to square meters (1 acre = 4046.86 sq meters)
    land_area_m2 = land_area_acres * 4046.86  # Convert acres to square meters
    land_density_fraction = land_density / 100  # Convert percentage to fraction
    # Effective usable land area for panels
    usable_area_m2 = land_area_m2 * land_density_fraction * shading_factor * access_paths_factor

    # Calculate number of panels and system capacity
    num_panels = usable_area_m2 / panel_area  # Total panels based on panel area
    total_capacity = num_panels * panel_power  # Total system capacity in watts

    # Calculate daily and annual energy production
    daily_energy = total_capacity * sunlight_hours  # kWh per day
    annual_energy = daily_energy * 365  # kWh per year

    annual_revenue = (annual_energy * revenue_rate) - maintenance

    # Calculate initial cost (panels + additional costs)
    initial_cost = (num_panels * panel_cost) + additional_costs + land_cost
    
    payoff_years = initial_cost / annual_revenue

    # Display results
    result_text = (
        f"\U0001F333 Land Area: {land_area_acres} acres ({land_area_m2:,.2f} m²)\n"
        f"\U0001F4BB Number of Panels: {num_panels:,.0f}\n"
        f"\U0001F50B Total System Capacity: {total_capacity:,.2f} kW\n"
        f"☀️ Daily Energy Production: {daily_energy:,.2f} kWh\n"
        f"\U0001F4B0 Annual Revenue: ${annual_revenue:,.2f}\n"
        f"\U0001F4B8 Initial Cost: ${initial_cost:,.2f}\n"
        f"Years Until Payoff: {payoff_years:.1f}"
    )

    # Create a bar chart to visualize the results
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Panels", "Capacity (kW)", "Daily Energy (kWh)", "Annual Revenue ($)"],
                         y=[num_panels, total_capacity, daily_energy, annual_revenue],
                         text=[f"{num_panels:,.0f}", f"{total_capacity:,.2f}", f"{daily_energy:,.2f}", f"${annual_revenue:,.2f}"],
                         textposition='auto'))
    fig.update_layout(title="Solar Panel System Overview", yaxis_title="Value")

    return result_text.replace("\n", "  |  "), fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
