import pandas as pd
import numpy as np
import matplotlib
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json
from urllib.request import urlopen
from sodapy import Socrata

client = Socrata("data.cdc.gov", None)

# Returns results as JSON from API / converted to Python list of dictionaries by sodapy.
results = client.get("3nnm-4jni", limit=10000000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
results_df.to_csv('out.csv', index=False)

app = Dash(__name__)


def create_map():
    df = pd.read_csv('out.csv', dtype={"county_fips": str}) 
    data = df[['county_fips', 'covid_cases_per_100k']]

    f_geojson = open('../geojson_data/counties_fips.json')
    geojson_data = json.load(f_geojson)
    
    fig = px.choropleth(data, 
                            geojson=geojson_data, 
                            locations='county_fips', 
                            locationmode='geojson-id', 
                            scope='usa', 
                            color='covid_cases_per_100k', 
                            range_color=(0, 300),
                            labels={"covid_cases_per_100k":"COVID-19 cases per 100k"}, 
                            color_continuous_scale='ice_r')
         
    last_updated = df['date_updated'].iloc[-1]

    fig.update_layout(
        title_text="New COVID-19 cases per 100,000 population (7-day total), by FIPS county (last updated: " + last_updated[0:10] + ")",
        margin={"r":0,"t":100,"l":100,"b":0}
    )

    fig.show()
    
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])
    
    app.run_server(debug=True)

create_map()