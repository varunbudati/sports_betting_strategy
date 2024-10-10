import os
import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from cfbd import Configuration, ApiClient, TeamsApi, GamesApi, StatsApi, PlayersApi

# Load environment variables
load_dotenv()

# Set up CFBD API client
configuration = Configuration()
configuration.api_key['Authorization'] = os.getenv('CFBD_API_KEY')
configuration.api_key_prefix['Authorization'] = 'Bearer'

api_client = ApiClient(configuration)
teams_api = TeamsApi(api_client)
games_api = GamesApi(api_client)
stats_api = StatsApi(api_client)
players_api = PlayersApi(api_client)

st.title('College Football Statistics Dashboard')

# Sidebar for user input
st.sidebar.header('Filters')
year = st.sidebar.number_input('Year', min_value=2000, max_value=2023, value=2023)
team = st.sidebar.selectbox('Team', [team.school for team in teams_api.get_fbs_teams(year=year)])

# Team Season Stats
st.header(f'{team} Team Stats for {year}')
team_stats = stats_api.get_team_season_stats(year=year, team=team)
if team_stats:
    df_team_stats = pd.DataFrame([stat.to_dict() for stat in team_stats])
    st.dataframe(df_team_stats)

    # Visualize key stats
    key_stats = ['totalYards', 'rushingYards', 'passingYards', 'pointsFor', 'pointsAgainst']
    df_key_stats = df_team_stats[key_stats].melt()
    chart = alt.Chart(df_key_stats).mark_bar().encode(
        x='variable',
        y='value',
        color='variable'
    ).properties(width=600, height=400)
    st.altair_chart(chart)

# Team Schedule and Results
st.header(f'{team} Schedule and Results for {year}')
games = games_api.get_games(year=year, team=team)
if games:
    df_games = pd.DataFrame([{
        'date': game.start_date,
        'opponent': game.away_team if game.home_team == team else game.home_team,
        'result': f"{game.home_points}-{game.away_points}",
        'winner': game.home_team if game.home_points > game.away_points else game.away_team
    } for game in games])
    st.dataframe(df_games)

# Player Stats
st.header(f'Top Players for {team} in {year}')
player_stats = stats_api.get_player_season_stats(year=year, team=team)
if player_stats:
    df_player_stats = pd.DataFrame([stat.to_dict() for stat in player_stats])
    
    # Passing stats
    st.subheader('Top Passers')
    passing_stats = df_player_stats.nlargest(5, 'passing_yards')[['player', 'passing_yards', 'passing_tds', 'passing_int']]
    st.dataframe(passing_stats)

    # Rushing stats
    st.subheader('Top Rushers')
    rushing_stats = df_player_stats.nlargest(5, 'rushing_yards')[['player', 'rushing_yards', 'rushing_tds', 'rushing_att']]
    st.dataframe(rushing_stats)

    # Receiving stats
    st.subheader('Top Receivers')
    receiving_stats = df_player_stats.nlargest(5, 'receiving_yards')[['player', 'receiving_yards', 'receiving_tds', 'receptions']]
    st.dataframe(receiving_stats)

# Player Search
st.header('Player Search')
player_name = st.text_input('Enter player name')
if player_name:
    search_results = players_api.player_search(search_term=player_name)
    if search_results:
        player = search_results[0]
        st.write(f"Name: {player.first_name} {player.last_name}")
        st.write(f"Team: {player.team}")
        st.write(f"Position: {player.position}")
        st.write(f"Jersey: {player.jersey}")
        
        # Get player stats
        player_stats = stats_api.get_player_season_stats(year=year, player_id=player.id)
        if player_stats:
            df_player_stats = pd.DataFrame([stat.to_dict() for stat in player_stats])
            st.dataframe(df_player_stats)
    else:
        st.write("No player found with that name.")

# Add more sections as needed (e.g., team rankings, conference stats, etc.)