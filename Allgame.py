import altair as alt
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from datetime import datetime

import pymongo
# Replace these with your actual MongoDB connection details
# Modify the connection string with appropriate values
mongo_uri = "mongodb+srv://doadmin:p214zl0y9A86dq3B@db-mongodb-blr1-07793-dc565430.mongo.ondigitalocean.com/gamesmela_reports_db?tls=true&authSource=admin&replicaSet=db-mongodb-blr1-07793"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)

# Access a specific database (replace 'your-database' with your actual database name)
db = client['analytics_dashboard_data']

collection = db['all_game_dash_board_table_1']

# Fetch all documents from the collection
all_documents = collection.find()

# Convert the documents to a list of dictionaries
data = list(all_documents)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Dropping the "id" column
df = df.drop('_id', axis=1)

# Converting to int
df['game_id'] = df['game_id'].astype(float).astype(int)
df['game_id'] = df['game_id'].fillna(0).astype(int)

df['games_per_user'] = df['games_per_user'].fillna(0).astype(int)
df['games_per_user'] = df['games_per_user'].astype(float).astype(int)


# Convert the 'date' column to datetime.date objects
df['date'] = pd.to_datetime(df['date']).dt.date

# Date Filter
min_date = df['date'].min()
max_date = df['date'].max()

selected_start_date = st.date_input("Select start date:", min_value=min_date, max_value=max_date, value=min_date)
selected_end_date = st.date_input("Select end date:", min_value=min_date, max_value=max_date, value=max_date)

# Filter DataFrame based on the selected date range
filtered_df = df[(df['date'] >= selected_start_date) & (df['date'] <= selected_end_date)]

# Check if filtered DataFrame is empty
if filtered_df.empty:
    st.warning("No data available for the selected date.")
else:
    # Drop the "date" column before displaying the DataFrame
    filtered_df = filtered_df.drop(columns=['date'])

    # Add a row for Total at the bottom of the DataFrame
    total_row = {
        'game_id': 0,
        'game_name': 'Total',
        'games_played_by_user': filtered_df['games_played_by_user'].sum(),
        'unique_users': filtered_df['unique_users'].sum(),
        'games_won': filtered_df['games_won'].sum(),
        'unique_game_winners': filtered_df['unique_game_winners'].sum(),
        'winning_probability': 0,
        'games_per_user': 0
        # Add other columns here and update their values accordingly
    }
    filtered_df = filtered_df.append(total_row, ignore_index=True)

    # Show the filtered DataFrame using st.dataframe()
    # Display the filtered DataFrame without truncation
    # Show the DataFrame in Streamlit with a wider table
    st.dataframe(filtered_df, width=2500)

    # Save the filtered DataFrame to a CSV file
    csv_data = filtered_df.to_csv(index=False)
    with open("filtered_data.csv", "w", encoding="utf-8") as f:
        f.write(csv_data)

    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    #####
    # Grouping the data by 'game_name' and calculating the total number of games played
    games_played_total = df.groupby('game_name')['games_played_by_user'].sum()

    # Convert the result to a DataFrame for easy plotting
    df_games_played = pd.DataFrame(
        {'Game Name': games_played_total.index, 'Total Games Played': games_played_total.values})

    # Filter out the 'Total' row from the DataFrame
    df_games_played = df_games_played[df_games_played['Game Name'] != 'Total']

    # Sort the DataFrame by total games played in descending order
    df_games_played = df_games_played.sort_values(by='Total Games Played', ascending=False)

    # Plot the bar chart
    st.bar_chart(data=df_games_played, x='Game Name', y='Total Games Played')