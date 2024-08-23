import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

ANAITERRA_COLOR = "#E44445"
MAX_ROWS = 1000
columns_to_show = ["name", "channel_name", "thread_name", "message","message_link"]
columns_to_group = ["name", "channel_name", "thread_name"]

# Load CSV data
df = pd.read_csv('data/data.csv')

st.title("Explorador _:red[de] vergüenzas_ 👺 😳")
st.write("_aka_ el shameador de Winnie 🐼")

st.markdown(
    f"""
    <hr style="border:2px solid {ANAITERRA_COLOR}">
    """,
    unsafe_allow_html=True
) 

# Sidebar filters

st.sidebar.image("images/anaiterra_logo_no_background.png", width=150) 
st.sidebar.header("Filtros")

name_filter = st.sidebar.multiselect('Personita(s)', options=df['name'].unique())
channel_filter = st.sidebar.multiselect('Canal(es)', options=df['channel_name'].unique())
thread_filter = st.sidebar.multiselect('Hilo(s)', options=df['thread_name'].unique())
message_filter = st.sidebar.text_input('Mensaje contiene')

# Create two columns
col1, col2 = st.columns([2,5])


# Apply filters
filtered_df = df[
    (df['name'].isin(name_filter) if name_filter else pd.Series([True] * len(df))) &
    (df['channel_name'].isin(channel_filter) if channel_filter else pd.Series([True] * len(df))) &
    (df['thread_name'].isin(thread_filter) if thread_filter else pd.Series([True] * len(df))) &
    (df['message'].str.contains(message_filter, case=False, na=False) if message_filter else pd.Series([True] * len(df)))
]


with col1:

    # Group By functionality
    group_by_columns = st.sidebar.multiselect('Agrupar por', options=df[columns_to_group].columns.tolist())
    st.write("### # Total de Mensajes")
    st.write("(elige al menos un campo para agrupar)")


    if group_by_columns:
        grouped_df = filtered_df.groupby(group_by_columns).size().reset_index(name='count')
        st.write(grouped_df.sort_values(by="count", ascending=False))


with col2:


    # Display filtered data
    df = filtered_df.reset_index()[columns_to_show]

    st.dataframe(df)

