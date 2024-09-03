import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime, timedelta
from filemanager import open_file, save_file

# Set the app title from environment or use default
app_title = os.getenv("TAB_TITLE", "Discord Search")
st.set_page_config(layout="wide", page_title=app_title)

# Function to load data with caching
@st.cache_data
def load_data():
    df = open_file()
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="mixed", errors='coerce')
    df['formatted_date'] = df['timestamp'].dt.tz_convert('Europe/Madrid').dt.strftime('%d/%m/%Y %H:%M')
    df['date'] = df['timestamp'].dt.date
    df['year'] = df['timestamp'].dt.year  # Extract the year from the timestamp
    return df

# Load CSV data
df = load_data()

# Get the last timestamp from the data
last_timestamp = df['timestamp'].max().tz_convert('Europe/Madrid')

# Display the title with custom HTML styling
st.markdown(f"""
    <h1 style='text-align: center; font-size: 48px; background: -webkit-linear-gradient(#7289DA, #5865F2); -webkit-background-clip: text; color: transparent;'>
         {app_title} 👾
    </h1>
""", unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])

# Add "Actualizar" button
with col2:
    if st.button("Actualizar"):
        with st.spinner('Actualizando datos...'):
            try:
                # Run query.py to update the data
                result = subprocess.run(["python", "query/query.py"], check=True)
                st.success("Datos actualizados correctamente.")
                # Reload the data after updating
                st.cache_data.clear()  # Clear the cache to reload data
                df = load_data()  # Re-load the data after clearing the cache
                save_file(df)  # Save the updated data back to Google Drive
                last_timestamp = df['timestamp'].max().tz_convert('Europe/Madrid')
            except subprocess.CalledProcessError as e:
                st.error(f"Error al actualizar los datos: {e}")

# Layout: Button and last updated timestamp
col1, col2 = st.columns([5, 1])

with col2:
    # Display the last updated timestamp
    st.write(f"Última actualización: {last_timestamp.strftime('%d/%m/%Y %H:%M')}")

# Calculate default date range
end_date_default = datetime.today().date()
start_date_default = datetime(2020, 1, 1).date()

# Define the only tab/page now: Mensajes
st.title("Explorador _:red[de] vergüenzas_ 👺 😳")
st.write("_aka_ el shameador de Winnie 🐼")

# Spoilers toggle
spoilers_filter = st.checkbox("Mostrar spoilers")

# First row: Date range, Personitas
col1, col2 = st.columns(2)

with col1:
    date_range = st.date_input(
        "Desde", 
        value=[start_date_default, end_date_default], 
        key="message_date_range"
    )
    
    # Apply the date range filter directly
    start_date, end_date = date_range
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

with col2:
    name_filter = st.multiselect('Personita(s)', options=filtered_df['name'].unique(), key="explorer_name_filter")
    if name_filter:
        filtered_df = filtered_df[filtered_df['name'].isin(name_filter)]

# Second row: Canal, Hilos
col3, col4 = st.columns(2)

with col3:
    channel_filter = st.multiselect('Canal(es)', options=filtered_df['channel_name'].unique(), key="explorer_channel_filter")
    if channel_filter:
        filtered_df = filtered_df[filtered_df['channel_name'].isin(channel_filter)]

with col4:
    thread_filter = st.multiselect('Hilo(s)', options=filtered_df['thread_name'].unique(), key="explorer_thread_filter")
    if thread_filter:
        filtered_df = filtered_df[filtered_df['thread_name'].isin(thread_filter)]

# Third row: Mensaje contiene
message_filter = st.text_input('Mensaje contiene', key="explorer_message_filter")
if message_filter:
    filtered_df = filtered_df[filtered_df['message'].str.contains(rf'\b{message_filter}\b', case=False, na=False)]

# Apply spoiler filter only for display purposes
df_display = filtered_df.copy()
if not spoilers_filter:
    df_display = df_display[~df_display['message'].str.contains(r"\|\|", na=False)]

# Sort the DataFrame by timestamp in descending order
df_display = df_display.sort_values(by='timestamp', ascending=False)

# Display filtered data
st.subheader("Lista de mensajes")
columns_to_show = ["formatted_date", "name", "channel_name", "thread_name", "message", "message_link", "image_url", "has_spoilers", "max_reaction_count", "total_reactions"]
df_to_display = df_display.reset_index(drop=True)[columns_to_show]
st.dataframe(df_to_display)

# Group By Section
st.markdown("<hr style='border:2px solid #E44445;'>", unsafe_allow_html=True)
st.subheader("Recuento")

# Group By Filters
group_by_columns = st.multiselect(
    "Agrupar por",
    options=["year", "max_reaction_count", "name", "channel_name", "thread_name"],
    key="group_by_columns"
)

# Display Grouped Data
if group_by_columns:
    grouped_df = filtered_df.groupby(group_by_columns).size().reset_index(name='count').sort_values(by="count", ascending=False)
    st.dataframe(grouped_df)
else:
    st.write("Please select at least one field to group by.")

# Hall of Fame Simulation Section
with st.expander("Hall of Fame Simulation"):
    st.subheader("Simulación del Hall of Fame")
    
    # Filters for the simulation
    col5, col6 = st.columns(2)
    
    with col5:
        years_selected = st.multiselect("Años", options=df['year'].unique(), key="hof_years_filter")
    
    with col6:
        threshold = st.slider("Threshold", min_value=1, max_value=int(df['max_reaction_count'].max()), value=10, key="hof_threshold_filter")
    
    # Filter data for the Hall of Fame
    hof_df = df.copy()  # Use the original DataFrame, not filtered_df

    if years_selected:
        hof_df = hof_df[hof_df['year'].isin(years_selected)]
    
    hof_df = hof_df[hof_df['max_reaction_count'] >= threshold]
    
    # Calculate the total number of messages
    total_messages = len(hof_df)
    
    # Display the total number of messages
    st.write(f"Total amount of messages: {total_messages}")
    
    # Sort by max_reaction_count in descending order to create a leaderboard
    hof_df = hof_df.sort_values(by='max_reaction_count', ascending=False)
    
    # Add a Rank column
    hof_df['Rank'] = range(1, len(hof_df) + 1)
    
    # Select only the relevant columns for display
    hof_df = hof_df[['Rank', 'name', 'message', 'max_reaction_count', "message_link"]]
    
    st.subheader("Leaderboard")
    st.dataframe(hof_df)
