import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# Placeholder function for fetching player data
def fetch_player_data(player_name, start_date, end_date):
    # This is where you'd integrate with a football stats API
    # For now, we'll return dummy data
    dates = pd.date_range(start=start_date, end=end_date, freq='W')
    goals = np.random.randint(0, 3, size=len(dates))
    assists = np.random.randint(0, 2, size=len(dates))
    return pd.DataFrame({'Date': dates, 'Goals': goals, 'Assists': assists})

# Function to calculate performance metrics
def calculate_performance_metrics(data):
    total_goals = data['Goals'].sum()
    total_assists = data['Assists'].sum()
    games_played = len(data)
    goals_per_game = total_goals / games_played
    assists_per_game = total_assists / games_played
    
    return {
        'Total Goals': total_goals,
        'Total Assists': total_assists,
        'Games Played': games_played,
        'Goals per Game': f'{goals_per_game:.2f}',
        'Assists per Game': f'{assists_per_game:.2f}'
    }

# Function to plot player performance
def plot_player_performance(data):
    base = alt.Chart(data).encode(x='Date:T')
    
    goals_line = base.mark_line(color='blue').encode(y='Goals:Q')
    goals_points = base.mark_circle(color='blue').encode(y='Goals:Q')
    
    assists_line = base.mark_line(color='red').encode(y='Assists:Q')
    assists_points = base.mark_circle(color='red').encode(y='Assists:Q')
    
    chart = (goals_line + goals_points + assists_line + assists_points).properties(
        width=600,
        height=400,
        title='Player Performance Over Time'
    )
    
    return chart

# Streamlit app
st.title('Football Player Analysis Dashboard')

# Sidebar for user input
st.sidebar.header('User Input')
player_name = st.sidebar.text_input('Enter Player Name', value='Lionel Messi')
start_date = st.sidebar.date_input('Start Date', datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input('End Date', datetime.now())

# Fetch player data
data = fetch_player_data(player_name, start_date, end_date)

# Display player performance chart
st.subheader(f'{player_name} Performance Chart')
st.altair_chart(plot_player_performance(data), use_container_width=True)

# Display performance metrics
st.subheader('Performance Metrics')
metrics = calculate_performance_metrics(data)
col1, col2, col3 = st.columns(3)
col1.metric("Total Goals", metrics['Total Goals'])
col2.metric("Total Assists", metrics['Total Assists'])
col3.metric("Games Played", metrics['Games Played'])
col1.metric("Goals per Game", metrics['Goals per Game'])
col2.metric("Assists per Game", metrics['Assists per Game'])

# Player comparison
st.subheader('Player Comparison')
comparison_player = st.text_input('Enter another player name for comparison')
if comparison_player:
    comparison_data = fetch_player_data(comparison_player, start_date, end_date)
    comparison_metrics = calculate_performance_metrics(comparison_data)
    
    col1, col2 = st.columns(2)
    col1.subheader(player_name)
    col2.subheader(comparison_player)
    
    for metric in ['Total Goals', 'Total Assists', 'Games Played']:
        col1.metric(metric, metrics[metric])
        col2.metric(metric, comparison_metrics[metric])

# Historical trend analysis
st.subheader('Historical Trend Analysis')
trend_metric = st.selectbox('Select metric for trend analysis', ['Goals', 'Assists'])
trend_chart = alt.Chart(data).mark_line().encode(
    x='Date:T',
    y=f'{trend_metric}:Q',
    tooltip=['Date:T', f'{trend_metric}:Q']
).properties(
    width=600,
    height=300,
    title=f'{trend_metric} Trend Over Time'
)
st.altair_chart(trend_chart, use_container_width=True)

# Placeholder for advanced analytics
st.subheader('Advanced Analytics')
st.write('This section will contain more advanced statistical analysis and predictions.')

# User feedback
st.subheader('User Feedback')
feedback = st.text_area('Please provide any feedback or suggestions for improvement')
if st.button('Submit Feedback'):
    st.success('Thank you for your feedback!')