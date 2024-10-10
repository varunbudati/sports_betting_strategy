import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from cfbd import Configuration, ApiClient, PlayersApi, StatsApi

# Set up CFBD API client
configuration = Configuration()
configuration.api_key['Authorization'] = st.secrets["cfbd_api_key"]
configuration.api_key_prefix['Authorization'] = 'Bearer'

api_client = ApiClient(configuration)
players_api = PlayersApi(api_client)
stats_api = StatsApi(api_client)

def fetch_player_data(player_name, start_year, end_year):
    try:
        # Search for the player
        search_results = players_api.player_search(search_term=player_name)
        if not search_results:
            st.error(f"No player found with name: {player_name}")
            return None

        player = search_results[0]
        player_id = player.id

        # Fetch player statistics for each year
        all_stats = []
        for year in range(start_year, end_year + 1):
            stats = stats_api.get_player_season_stats(year=year, player_id=player_id)
            if stats:
                all_stats.extend(stats)

        if not all_stats:
            st.warning(f"No statistics found for {player_name} in the specified date range.")
            return None

        # Convert to DataFrame
        df = pd.DataFrame([stat.to_dict() for stat in all_stats])
        df['year'] = pd.to_datetime(df['year'], format='%Y')
        return df

    except Exception as e:
        st.error(f"An error occurred while fetching data: {str(e)}")
        return None

def calculate_performance_metrics(data):
    if data is None or data.empty:
        return None

    total_games = data['games'].sum()
    total_rushing_yards = data['rushing_yards'].sum()
    total_passing_yards = data['passing_yards'].sum()
    total_touchdowns = data['rushing_td'].sum() + data['passing_td'].sum()
    
    return {
        'Total Games': total_games,
        'Total Rushing Yards': total_rushing_yards,
        'Total Passing Yards': total_passing_yards,
        'Total Touchdowns': total_touchdowns,
        'Avg Rushing Yards/Game': f'{total_rushing_yards / total_games:.2f}',
        'Avg Passing Yards/Game': f'{total_passing_yards / total_games:.2f}',
        'Avg Touchdowns/Game': f'{total_touchdowns / total_games:.2f}'
    }

def plot_player_performance(data):
    if data is None or data.empty:
        return None

    rushing_chart = alt.Chart(data).mark_line(color='blue').encode(
        x='year:T',
        y='rushing_yards:Q',
        tooltip=['year:T', 'rushing_yards:Q']
    ).properties(title='Rushing Yards Over Time')

    passing_chart = alt.Chart(data).mark_line(color='red').encode(
        x='year:T',
        y='passing_yards:Q',
        tooltip=['year:T', 'passing_yards:Q']
    ).properties(title='Passing Yards Over Time')

    return rushing_chart & passing_chart

# Streamlit app
st.title('College Football Player Analysis Dashboard')

# Sidebar for user input
st.sidebar.header('User Input')
player_name = st.sidebar.text_input('Enter Player Name', value='Trevor Lawrence')
start_year = st.sidebar.number_input('Start Year', min_value=2000, max_value=datetime.now().year, value=2018)
end_year = st.sidebar.number_input('End Year', min_value=2000, max_value=datetime.now().year, value=datetime.now().year)

# Fetch player data
data = fetch_player_data(player_name, start_year, end_year)

if data is not None:
    # Display player performance chart
    st.subheader(f'{player_name} Performance Chart')
    chart = plot_player_performance(data)
    if chart:
        st.altair_chart(chart, use_container_width=True)

    # Display performance metrics
    st.subheader('Performance Metrics')
    metrics = calculate_performance_metrics(data)
    if metrics:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Games", metrics['Total Games'])
        col2.metric("Total Rushing Yards", metrics['Total Rushing Yards'])
        col3.metric("Total Passing Yards", metrics['Total Passing Yards'])
        col1.metric("Total Touchdowns", metrics['Total Touchdowns'])
        col2.metric("Avg Rushing Yards/Game", metrics['Avg Rushing Yards/Game'])
        col3.metric("Avg Passing Yards/Game", metrics['Avg Passing Yards/Game'])

    # Player comparison
    st.subheader('Player Comparison')
    comparison_player = st.text_input('Enter another player name for comparison')
    if comparison_player:
        comparison_data = fetch_player_data(comparison_player, start_year, end_year)
        if comparison_data is not None:
            comparison_metrics = calculate_performance_metrics(comparison_data)
            if comparison_metrics:
                col1, col2 = st.columns(2)
                col1.subheader(player_name)
                col2.subheader(comparison_player)
                
                for metric in ['Total Games', 'Total Rushing Yards', 'Total Passing Yards', 'Total Touchdowns']:
                    col1.metric(metric, metrics[metric])
                    col2.metric(metric, comparison_metrics[metric])

    # Historical trend analysis
    st.subheader('Historical Trend Analysis')
    trend_metric = st.selectbox('Select metric for trend analysis', ['rushing_yards', 'passing_yards', 'rushing_td', 'passing_td'])
    if trend_metric in data.columns:
        trend_chart = alt.Chart(data).mark_line().encode(
            x='year:T',
            y=f'{trend_metric}:Q',
            tooltip=['year:T', f'{trend_metric}:Q']
        ).properties(
            width=600,
            height=300,
            title=f'{trend_metric} Trend Over Time'
        )
        st.altair_chart(trend_chart, use_container_width=True)

# User feedback
st.subheader('User Feedback')
feedback = st.text_area('Please provide any feedback or suggestions for improvement')
if st.button('Submit Feedback'):
    st.success('Thank you for your feedback!')