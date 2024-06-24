# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)

options = [{'label': 'All Sites', 'value': 'ALL'}]
options += [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder="Select a launch site",
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(                                                                       
                                    dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0:'0',
                                                       100:'100'},
                                                value=[min_payload, max_payload],
                                                tooltip={"placement": "bottom", "always_visible": True}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success                                
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
        Output(component_id='success-pie-chart', component_property='figure'),
        Input(component_id='site-dropdown', component_property='value')
)

def get_pie_chart(entered_site):    
    if entered_site == 'ALL':
        filtered_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index() 
        filtered_data = filtered_data.rename(columns={'class':'count'})
        filtered_data.columns = ['Launch Site', 'count']
        fig = px.pie(filtered_data, 
                     values='count', 
                     names='Launch Site', 
                     color='Launch Site',
                     color_discrete_sequence=px.colors.qualitative.Vivid,
                     title='Total Successful Launches By Site')        
    else:
        pie_data = spacex_df.loc[spacex_df['Launch Site'] == entered_site]['class'].value_counts().reset_index()
        pie_data.columns = ['class', 'count']
        class_mapping = {1: 'Successful', 0: 'Not Successful'}
        pie_data['class'] = pie_data['class'].map(class_mapping)
        fig = px.pie(pie_data,                                                    
                     values='count',
                     names='class',
                     color='class',
                     category_orders= {'class':['Not Successful','Successful']},
                     color_discrete_sequence=['#FF6347', '#32CD32'],
                    #  color_discrete_map={'Not Successful':'firebrick', 
                    #                      'Successful':'green'},
                     title=f'Success vs. Failed Launches for site {entered_site}')
    return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# # Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
)

def get_scatter_chart(entered_site, entered_range):
    if entered_site == 'ALL':      
        scatter_data = spacex_df.loc[(spacex_df['Payload Mass (kg)'] >= entered_range[0]) & 
                                     (spacex_df['Payload Mass (kg)'] <= entered_range[1])]
        fig1 = px.scatter(scatter_data,
                         x='Payload Mass (kg)',
                         y='class',
                         color="Booster Version Category",
                         title='Correlation between Payload and Success for all Sites')
    else:
        scatter_data = spacex_df.loc[spacex_df['Launch Site'] == entered_site]
        scatter_data = scatter_data.loc[(scatter_data['Payload Mass (kg)'] >= entered_range[0]) & 
                                        (scatter_data['Payload Mass (kg)'] <= entered_range[1])]
        fig1 = px.scatter(scatter_data,
                         x='Payload Mass (kg)',
                         y='class',
                         color="Booster Version Category",
                         title=f'Correlation between Payload and Success for Site {entered_site}')
    return fig1

# Run the app
if __name__ == '__main__':
    app.run_server()
