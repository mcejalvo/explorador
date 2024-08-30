import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime, timedelta
from filemanager import open_file

# Set the app title from environment or use default
app_title = os.getenv("TAB_TITLE", "Discord Search")
st.set_page_config(layout="wide", page_title=app_title)

# Load CSV data
df = open_file("data/data.csv")

# Ensure the 'timestamp' column is in datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], format="mixed", errors='coerce')
df['formatted_date'] = df['timestamp'].dt.tz_convert('Europe/Madrid').dt.strftime('%d/%m/%Y %H:%M')

# Create a new 'date' column containing only the date part (no time, no timezone)
df['date'] = df['timestamp'].dt.date

# Get the last timestamp from the data
last_timestamp = df['timestamp'].max()

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
                df = open_file("data/data.csv")
                df['timestamp'] = pd.to_datetime(df['timestamp'], format="mixed", errors='coerce')
                df['formatted_date'] = df['timestamp'].dt.tz_convert('Europe/Madrid').dt.strftime('%d/%m/%Y %H:%M')
                df['date'] = df['timestamp'].dt.date  # Re-create the 'date' column
                last_timestamp = df['timestamp'].max()
            except subprocess.CalledProcessError as e:
                st.error(f"Error al actualizar los datos: {e}")

# Layout: Button and last updated timestamp
col1, col2 = st.columns([5, 1])

with col2:
    # Display the last updated timestamp
    st.write(f"Última actualización: {pd.to_datetime(last_timestamp, format='mixed').strftime('%d/%m/%Y %H:%M')}")

# Calculate default date range
end_date_default = datetime.today().date()
start_date_default = datetime(2020, 1, 1).date()

# Define tabs/pages
tab1, tab2 = st.tabs(["Mensajes", "Imágenes"])

# Message Explorer Page
with tab1:
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

    # Display filtered data
    st.subheader("Lista de mensajes")
    columns_to_show = ["formatted_date", "timestamp", "name", "channel_name", "thread_name", "message", "message_link"]
    df_to_display = df_display.reset_index()[columns_to_show]
    st.dataframe(df_to_display)

    # Group By Section
    st.markdown("<hr style='border:2px solid #E44445;'>", unsafe_allow_html=True)
    st.subheader("Recuento")

    # Group By Filters
    group_by_columns = st.multiselect(
        "Agrupar por",
        options=["name", "channel_name", "thread_name"],
        key="group_by_columns"
    )

    # Display Grouped Data
    if group_by_columns:
        grouped_df = filtered_df.groupby(group_by_columns).size().reset_index(name='count').sort_values(by="count", ascending=False)
        st.dataframe(grouped_df)
    else:
        st.write("Please select at least one field to group by.")

# Image Gallery Page
with tab2:
    st.title("Galería _:red[de] vergüenzas_ 📷😳")

    # First row: Date range, Personitas
    col1, col2 = st.columns(2)

    with col1:
        date_range = st.date_input(
            "Desde", 
            value=[start_date_default, end_date_default], 
            key="gallery_date_range"
        )
        
        # Apply the date range filter directly
        start_date, end_date = date_range
        image_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]


    with col2:
        user_filter = st.multiselect('Personita(s)', options=image_df['name'].unique(), key="gallery_user_filter")
        if user_filter:
            image_df = image_df[image_df['name'].isin(user_filter)]

    # Second row: Canal, Hilos, Excluir canales/hilos
    col3, col4, col5 = st.columns(3)

    with col3:
        channel_filter = st.multiselect('Canal(es)', options=image_df['channel_name'].unique(), key="gallery_channel_filter")
        if channel_filter:
            image_df = image_df[image_df['channel_name'].isin(channel_filter)]

    with col4:
        thread_filter = st.multiselect('Hilo(s)', options=image_df['thread_name'].unique(), key="gallery_thread_filter")
        if thread_filter:
            image_df = image_df[image_df['thread_name'].isin(thread_filter)]

    with col5:
        exclude_filter = st.multiselect('Excluir canales/hilos', options=list(image_df['channel_name'].unique()) + list(image_df['thread_name'].unique()), key="gallery_exclude_filter")
        if exclude_filter:
            image_df = image_df[~image_df['channel_name'].isin(exclude_filter)]
            image_df = image_df[~image_df['thread_name'].isin(exclude_filter)]

    # Fourth row: Number of columns (buttons)
    st.markdown("<hr style='border:2px solid #E44445;'>", unsafe_allow_html=True)
    col6 = st.columns(10)
    with col6[-1]:
        if st.button("Grande"):
            num_columns = 1
    with col6[-2]:
        if st.button("Mediano"):
            num_columns = 2
    with col6[-3]:
        if st.button("Pequeño"):
            num_columns = 3

    # Ensure num_columns has a default value
    if 'num_columns' not in locals():
        num_columns = 3

    # Filter to only rows with images
    image_df = image_df[image_df['has_image'] == 'yes']

    # Initialize session state for pagination if not already present
    if 'image_offset' not in st.session_state:
        st.session_state.image_offset = 20

    # Display only the current batch of images in the selected number of columns
    current_images = image_df.head(st.session_state.image_offset)
    total_images = len(image_df)
    st.write(f"Mostrando {len(current_images)} imágenes de un total de {total_images}")

    if num_columns == 1:
        for idx, row in current_images.iterrows():
            st.image(row['image_url'], caption=f"{row['name']} - {row['formatted_date']} - {row['channel_name']}", use_column_width=True)
    else:
        cols = st.columns(num_columns)
        for idx, row in enumerate(current_images.iterrows()):
            with cols[idx % num_columns]:
                st.image(row[1]['image_url'], caption=f"{row[1]['name']} - {row[1]['formatted_date']} - {row[1]['channel_name']}", use_column_width=True)

    # Load more images on button click
    if len(image_df) > st.session_state.image_offset:
        load_more = st.button("Load 20 more images")
        if load_more:
            # Increase the image offset by 20, but don't exceed the number of available images
            st.session_state.image_offset = min(st.session_state.image_offset + 20, len(image_df))
            st.session_state["force_rerun"] = not st.session_state.get("force_rerun", False)  # Toggle a dummy variable to force rerun
