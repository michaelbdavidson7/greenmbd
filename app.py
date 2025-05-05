import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd

# Constants
shading_factor = 0.8  # Fraction of usable area after accounting for shading (e.g., 80%)
access_paths_factor = 0.9  # Account for pathways (e.g., 90% of area usable for panels)
# Assume a revenue rate (e.g., $0.10 per kWh)
revenue_rate = 0.10  # USD per kWh
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP
])

# Check if running inside Docker
if os.environ.get("IN_DOCKER"):
    server = app.server  # Required for Gunicorn inside Docker
    
# REMOVE any HTTPS enforcement since Apache is handling it
if "IN_DOCKER" in os.environ or "DYNO" in os.environ:
    del app.server.config['PREFERRED_URL_SCHEME']  # Remove HTTPS enforcement
    
# Specific marks
land_area_marks = {i: str(i) for i in range(1, 11)}
land_area_marks.update({i: str(i) for i in range(20, 81, 10)})
sunlight_df = pd.read_csv("data/List_of_cities_by_sunshine_duration_4.csv")
sunlight_df = sunlight_df.sort_values(["Country", "City"])
city_options = [
    {'label': f"{row['Country']}, {row['City']}", 'value': row['avg']}
    for _, row in sunlight_df.iterrows()
]
default = "United States, Cleveland"
default_value = city_options[0]['value'] if city_options else None

# city dropdown component
city_dropdown = html.Div([
    html.Label("Select a City for Average Sunlight Hours:"),
    dcc.Dropdown(
    id='city-dropdown',
    options=city_options,
    value=default_value,
    placeholder="Choose a city...",
    style={"width": "50%"}
)
    ], style={"padding": "20px"}) # type: ignore


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
    f" Revenue rate: $", html.Span(id="revenue-rate"), "/kWH ",
        html.I(className="bi bi-info-circle", id="hover-icon3", style={"fontSize": "24px", "cursor": "pointer"}),
    dbc.Tooltip(
        "$0.10 cents is generally high and unachieveable in grade A sunshine states due to oversaturation, but in grade B and lower its still available. ",
        target="hover-icon3",
        placement="right"
    ), 
]),
    html.Div([
        html.Label(id='land-acres-value'),
        dcc.Slider(id='land-area-acres', min=1, max=80, value=13, step=1,
                   marks=land_area_marks),
        html.Label(id="land-cost-value"),
        dcc.Slider(id='land-cost', min=10000, max=200000, step=10000, value=90000,
                   marks={i: f"{i} acres" for i in range(1, 101)}),
        html.Label(id="panel-area-value"),
        dcc.Slider(id='panel-area', min=1, max=10, step=0.1, value=2,
                   marks={i: f"{i} m²" for i in range(1, 11)}),
        html.Label(id="panel-power-value"),
        dcc.Slider(id='panel-power', min=0.1, max=1, step=0.01, value=0.4,
                   marks={i/10: f"{i/10} kW" for i in range(1, 11)}),
        html.Label(id="land-density-value"),
        dcc.Slider(id='land-density', min=50, max=90, step=1, value=60,
                   marks={i: f"{i}%" for i in range(50, 91, 5)}),
        city_dropdown, 
        html.Label(id="sunlight-hours-value"),
        dcc.Slider(id='sunlight-hours', min=1, max=12, step=0.1, value=5.8,
                   marks={i: f"{i} hrs" for i in range(1, 13)}),
        html.Label(id="panel-cost-value"),
        dcc.Slider(id='panel-cost', min=100, max=1000, step=10, value=100,
                   marks={i: f"${i}" for i in range(100, 1100, 100)}),
        html.Label(id="maintenance-value"),
        dcc.Slider(id='maintenance', min=0, max=150000, step=15000, value=105000,
                   marks={i: f"${i}" for i in range(0, 150000, 15000)}),
        html.Label(id="kwh-payment-value"),
        dcc.Slider(id='kwh-payment', min=0, max=0.50, step=0.01, value=.06,
                   marks={round(i, 2): str(round(i, 2)) for i in [x / 100 for x in range(0, 101, 5)]}),
        html.Label(id="additional-costs-value"),
        dcc.Slider(id='additional-costs', min=1000, max=510000, step=500, value=200000,
                   marks={i: f"${i:,}" for i in range(10000, 510000, 50000)}),
        html.Label(id="contingency-percent-value"),
        dcc.Slider(id='contingency-percent', min=0, max=100, step=5, value=15,
                   marks={i: f"{i}%" for i in range(5, 101, 5)}),
    ], style={"width": "50%", "padding": "20px", 'display': 'inline-block'}),

    html.Div(id='output-results', style={"margin-top": "30px", "font-size": "20px", 'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),
    dcc.Graph(id='capacity-graph')
], className="container-fluid")

# Callback to update the results and graph
@app.callback(
    [
        Output('output-results', 'children'),
        Output('revenue-rate', 'children'),
        Output('capacity-graph', 'figure')
    ],
    [
        Input('land-area-acres', 'value'),
        Input('panel-area', 'value'),
        Input('panel-power', 'value'),
        Input('land-density', 'value'),
        Input('sunlight-hours', 'value'),
        Input('panel-cost', 'value'),
        Input('maintenance', 'value'),
        Input('kwh-payment', 'value'),
        Input('additional-costs', 'value'),
        Input('land-cost', 'value'),
        Input('contingency-percent', 'value'),
        
    ]
)
def update_output(land_area_acres, panel_area, panel_power, land_density, sunlight_hours, panel_cost, maintenance, kwh_payment, additional_costs, land_cost, contingency_percent):
    

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

    annual_revenue = (annual_energy * kwh_payment) - maintenance

    # Calculate initial cost (panels + additional costs)
    initial_cost = (num_panels * panel_cost) + additional_costs + land_cost
    # add contingency percent
    initial_cost = initial_cost + (initial_cost * (contingency_percent / 100))
    
    payoff_years = initial_cost / annual_revenue

    # Display results
    result_text = (
        f"\U0001F333 Land Area: {land_area_acres} acres ({land_area_m2:,.2f} m²)\n"
        f"\U0001F4BB Number of Panels: {num_panels:,.0f}\n"
        f"\U0001F50B Total System Capacity: {total_capacity:,.2f} kW\n"
        f"☀️ Daily Energy Production: {daily_energy:,.2f} kWh\n"
        f"\U0001F4B0 Annual Revenue: ${annual_revenue:,.2f}\n"
        f"⚡️ kWH Payment: ${kwh_payment:,.2f}\n"
        f"\U0001F4B8 Initial Cost: ${initial_cost:,.2f}\n"
        f"📆 Years Until Payoff: {payoff_years:.1f}"
    )
    summary_text = html.Div([
        html.P(f"🌲 Land Area: {land_area_acres} acres ({land_area_m2:,.2f} m²)"),
        html.P(f"💻 Number of Panels: {num_panels:,.0f}"),
        html.P(f"🔋 Total System Capacity: {total_capacity:,.2f} kW"),
        html.P(f"☀️ Average Daily Energy Production: {daily_energy:,.2f} kWh"),
        html.P([f"💰", html.Strong(f"Annual Revenue: ${annual_revenue:,.2f}")]),
        html.P(f"⚡️ kWH Payment: ${kwh_payment:,.2f}"),
        html.P(f"💸 Initial Cost: ${initial_cost:,.2f}"),
        html.P([f"📆 ", html.Strong(f"Years Until Payoff: {payoff_years:.1f}")]),
    ], style={
        'border': '1px solid #ddd',
        'padding': '15px',
        'margin-left': '20px',
        'width': '500px',
        'background-color': '#f9f9f9',
        'border-radius': '8px',
        'box-shadow': '2px 2px 10px rgba(0, 0, 0, 0.1)'
    })
    # Create a bar chart to visualize the results
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Panels", "Capacity (kW)", "Daily Energy (kWh)", "Annual Revenue ($)"],
                         y=[num_panels, total_capacity, daily_energy, annual_revenue],
                         text=[f"{num_panels:,.0f}", f"{total_capacity:,.2f}", f"{daily_energy:,.2f}", f"${annual_revenue:,.2f}"],
                         textposition='auto'))
    fig.update_layout(title="Solar Panel System Overview", yaxis_title="Value")

    return summary_text, str(kwh_payment), fig

@app.callback(
    [
        Output('land-acres-value', 'children'),
        Output('land-cost-value', 'children'),
        Output('panel-area-value', 'children'),
        Output('panel-power-value', 'children'),
        Output('land-density-value', 'children'),
        Output('sunlight-hours-value', 'children'),
        Output('panel-cost-value', 'children'),
        Output('maintenance-value', 'children'),
        Output('kwh-payment-value', 'children'),
        Output('additional-costs-value', 'children'),
        Output('contingency-percent-value', 'children'),
    ],
    [
        Input('land-area-acres', 'value'),
        Input('land-cost', 'value'),
        Input('panel-area', 'value'),
        Input('panel-power', 'value'),
        Input('land-density', 'value'),
        Input('sunlight-hours', 'value'),
        Input('panel-cost', 'value'),
        Input('maintenance', 'value'),
        Input('kwh-payment', 'value'),
        Input('additional-costs', 'value'),
        Input('contingency-percent', 'value'),
    ]
)
def update_labels(land_area_acres, 
                  land_cost, 
                  panel_area, 
                  panel_power, 
                  land_density,
                  sunlight_hours,
                  panel_cost,
                  maintenance,
                  kwh_payment,
                  additional_costs,
                  contingency_percent):
    return (
        badge_factory("Land Area ", str(land_area_acres) + " (acres)"),
        badge_factory("Land Cost ", f"${land_cost}"),
        badge_factory("Panel Surface Area ", f"{panel_area}  (sq meters per panel)"),
        badge_factory("Power Output per Panel ", f"{panel_power}  (kW)"),
        badge_factory("Land Utilization Density ", f"{land_density}%"),
        badge_factory("Daily Hours of Sunlight ", f"{sunlight_hours}  (hours)"),
        badge_factory("Cost per Panel ", f"${panel_cost}"),
        badge_factory("Annual Maintenance/Insurance ", f"${maintenance}/year"),
        badge_factory("Revenue per kWH ", f"${kwh_payment}"),
        badge_factory("Additional Costs (Inverters, Wiring, Labor, etc.) ", f"${additional_costs}"),
        badge_factory("Contingency Percent:  ", f"{contingency_percent}%"),
            )
    
def badge_factory(label:str, value, value_post_script=""):
    return html.Div([
        label,
        dbc.Badge(
            [html.Strong(value), html.Span(value_post_script)], 
            color="white",
            text_color="success",
            className="border me-1",
        )
    ])


@app.callback(
    Output('sunlight-hours', 'value'),
    Input('city-dropdown', 'value'),
    prevent_initial_call=True
)
def update_sunlight_from_city(city_sunlight_hours):
    print("Dropdown selected:", city_sunlight_hours)
    if city_sunlight_hours:
        return round(city_sunlight_hours, 1)
    return dash.no_update
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
