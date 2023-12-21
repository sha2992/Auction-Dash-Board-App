import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

df = pd.read_csv('IPL_2022_Sold_Players.csv')

df['Price Paid'] = df['Price Paid'].str.replace(',', '').astype(int)

# histogram
fig = px.histogram(df,x='Team', title='Number of Player Each Team Purchased')
fig.update_xaxes(title_text='Team Name')
fig.update_yaxes(title_text='No. of Players')
fig.show()

# Pie chart
fig1 = px.pie(df, names='Team', values='Price Paid'
       , title='% Team Used in Total Spent')
fig1.show()

# bar chart 
grouped_data = df.groupby(['Team', 'Type']).size().reset_index(name='Count')

color_map = {'Batsman': '#3498db', 'Bowler': '#2ecc71', 'Wicket Keeper':'#e74c3c','All-Rounder':'#f39c12'}

fig2 = px.bar(data_frame=grouped_data,
       x='Team',
       y='Count',
       color='Type',
       color_discrete_map=color_map,
       title='Different Types of Players in Each Team'
)

fig2.update_xaxes(title_text='Team Name')
fig2.update_yaxes(title_text='No of Players of Each Type')

fig2.show()

# final dash board
# Create a Dash web application
AuctionApp = dash.Dash(__name__, title="IPL Auction Dash Board")
server = AuctionApp.server

# Define the layout
AuctionApp.layout = html.Div([
    html.H1("IPL Player Auction Dashboard", style={'text-align': 'center'}),

    # Filters
    html.Div([
        html.Label("Select Country"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in df['Nationality'].unique()] + [
                {'label': 'Overall', 'value': 'Overall'}],
            value=None,  # df['Nationality'].unique()[0]
            style={'width': '50%', 'margin-left': '15px'}
        ),

        html.Label("Select Type"),
        dcc.Dropdown(
            id='type-dropdown',
            options=[{'label': player_type, 'value': player_type} for player_type in df['Type'].unique()] + [
                {'label': 'Overall', 'value': 'Overall'}],
            value=None,
            style={'width': '50%'}
        ),

        html.Label("Select Team"),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in df['Team'].unique()] + [
                {'label': 'Overall', 'value': 'Overall'}],
            value=None,
            style={'width': '50%'}
        ),
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

    # Charts and Cards
    html.Div([
        # Highest Paid Player Card
        html.Div([
            html.Div([
                html.H3("Highest Paid Player"),
                html.P(id="highest-paid-player")
            ], className="card", style={'width': '50%', 'float': 'left', 'margin-left': '15px'}),

            html.Div([
                html.H3("Lowest Paid Player"),
                html.P(id="lowest-paid-player")
            ], className="card", style={'width': '50%', 'float': 'right'}),
        ], style={"display": "flex", "justify-content": "space-between", 'margin-bottom': '20px'}),
    ]),

    # Histogram
    html.Div([
        dcc.Graph(id='histogram', figure=fig, style={'width': '100%', 'margin-top': '20px', 'margin-bottom': '20px'}),
    ], style={'width': '100%', 'margin-top': '20px', 'margin-bottom': '20px'}),

    # Pie chart and Bar chart on the same row
    html.Div([
        dcc.Graph(id='pie-chart', figure=fig1, style={'width': '50%', 'float': 'left'}),
        dcc.Graph(id='bar-chart', figure=fig2, style={'width': '50%', 'float': 'right'}),
    ], style={"display": "flex", "justify-content": "space-between"})
], style={'width': '100%', 'margin': 'auto'})


# Define callback to update the charts based on filters
@AuctionApp.callback(
    [Output("histogram", "figure"),
     Output("pie-chart", "figure"),
     Output("bar-chart", "figure"),
     Output("highest-paid-player", "children"),
     Output("lowest-paid-player", "children")],
    [Input("country-dropdown", "value"),
     Input("type-dropdown", "value"),
     Input("team-dropdown", "value")]
)
def update_charts_and_highest_paid_player(selected_country, selected_type, selected_team):
    filtered_df = df.copy()

    if selected_country and selected_country != 'Overall':
        filtered_df = filtered_df[filtered_df['Nationality'] == selected_country]

    if selected_type and selected_type != 'Overall':
        filtered_df = filtered_df[filtered_df['Type'] == selected_type]

    if selected_team and selected_team != 'Overall':
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]

    if filtered_df.empty:
        return fig, fig1, fig2, "No data for the selected filters", "No data for the selected filters"

    # Update histograms
    updated_histogram = px.histogram(filtered_df, x='Team', title='Number of Players Each Team Purchased')
    updated_histogram.update_xaxes(title_text='Team Name')
    updated_histogram.update_yaxes(title_text='No. of Players')

    # Update pie chart
    updated_pie_chart = px.pie(filtered_df, names='Team', values='Price Paid', title='% Team Used in Total Spent')

    # Update bar chart
    grouped_data = filtered_df.groupby(['Team', 'Type']).size().reset_index(name='Count')
    updated_bar_chart = px.bar(data_frame=grouped_data, x='Team', y='Count', color='Type', color_discrete_map=color_map,
                               title='Different Types of Players in Each Team')
    updated_bar_chart.update_xaxes(title_text='Team Name')
    updated_bar_chart.update_yaxes(title_text='No of Players of Each Type')

    # Update highest and lowest paid players
    max_price_player_name = filtered_df.sort_values(by='Price Paid', ascending=False).iloc[0]['Players']
    min_price_player_name = filtered_df.sort_values(by='Price Paid', ascending=True).iloc[0]['Players']

    return updated_histogram, updated_pie_chart, updated_bar_chart, max_price_player_name, min_price_player_name


if __name__ == '__main__':
    AuctionApp.run_server(debug=False)