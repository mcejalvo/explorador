import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

app_title = os.getenv("TAB_TITLE", "Discord Search")
st.set_page_config(
    layout="wide",
    page_title=app_title
)

# Load CSV data
df = pd.read_csv('data/data.csv')

# Convert timestamp to a readable date format and add it as a new column
df['formatted_date'] = pd.to_datetime(df['timestamp'], format='ISO8601').dt.strftime('%d/%m/%Y %H:%M')

# Calculate default date range (last year)
end_date_default = datetime.today()
start_date_default = datetime(2020, 1, 1)

st.markdown(f"""
    <h1 style='text-align: center; font-size: 48px; background: -webkit-linear-gradient(#7289DA, #5865F2); -webkit-background-clip: text; color: transparent;'>
         {app_title} 👾
    </h1>
""", unsafe_allow_html=True)

# Define tabs/pages
tab1, tab2 = st.tabs(["Mensajes", "Imágenes"])

# Message Explorer Page
with tab1:
    st.title("Explorador _:red[de] vergüenzas_ 👺 😳")
    st.write("_aka_ el shameador de Winnie 🐼")

    # First row: Date range, Personitas
    col1, col2 = st.columns(2)

    with col1:
        date_range = st.date_input(
            "Desde", 
            value=[start_date_default, end_date_default], 
            key="message_date_range"
        )
        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range)
            filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        elif isinstance(date_range, pd.Timestamp):
            filtered_df = df[df['timestamp'] >= pd.to_datetime(date_range)]
        else:
            filtered_df = df.copy()

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

    # Display filtered data
    st.subheader("Lista de mensajes")
    columns_to_show = ["formatted_date", "name", "channel_name", "thread_name", "message", "message_link"]
    df_to_display = filtered_df.reset_index()[columns_to_show]
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
        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range)
            image_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        elif isinstance(date_range, pd.Timestamp):
            image_df = df[df['timestamp'] >= pd.to_datetime(date_range)]
        else:
            image_df = df.copy()

    with col2:
        user_filter = st.multiselect('Personita(s)', options=image_df['name'].unique(), key="gallery_user_filter")
        if user_filter:
            image_df = image_df[image_df['name'].isin(user_filter)]

    # Second row: Canal, Hilos
    col3, col4 = st.columns(2)

    with col3:
        channel_filter = st.multiselect('Canal(es)', options=image_df['channel_name'].unique(), key="gallery_channel_filter")
        if channel_filter:
            image_df = image_df[image_df['channel_name'].isin(channel_filter)]

    with col4:
        thread_filter = st.multiselect('Hilo(s)', options=image_df['thread_name'].unique(), key="gallery_thread_filter")
        if thread_filter:
            image_df = image_df[image_df['thread_name'].isin(thread_filter)]

    # Fourth row: Number of columns (buttons)
    st.markdown("<hr style='border:2px solid #E44445;'>", unsafe_allow_html=True)
    col5 = st.columns(10)
    with col5[-1]:
        if st.button("Grande"):
            num_columns = 1
    with col5[-2]:
        if st.button("Mediano"):
            num_columns = 2
    with col5[-3]:
        if st.button("Pequeño"):
            num_columns = 3

    # Ensure num_columns has a default value
    if 'num_columns' not in locals():
        num_columns = 2

    # Filter to only rows with images
    image_df = image_df[image_df['has_image'] == 'yes']

    # Display images in the selected number of columns
    st.write(f"Displaying {len(image_df)} images")

    if num_columns == 1:
        for idx, row in image_df.iterrows():
            st.image(row['image_url'], caption=f"{row['name']} - {row['formatted_date']} - {row['channel_name']}", use_column_width=True)
    else:
        cols = st.columns(num_columns)
        for idx, row in enumerate(image_df.iterrows()):
            with cols[idx % num_columns]:
                st.image(row[1]['image_url'], caption=f"{row[1]['name']} - {row[1]['formatted_date']} - {row[1]['channel_name']}", use_column_width=True)
