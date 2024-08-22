import streamlit as st
import pandas as pd

# Load CSV data
df = pd.read_csv('data.csv')

# Sidebar filters
name_filter = st.sidebar.multiselect('Filter by Name', options=df['name'].unique())
channel_filter = st.sidebar.multiselect('Filter by Channel Name', options=df['channel_name'].unique())
thread_filter = st.sidebar.multiselect('Filter by Thread Name', options=df['thread_name'].unique())
message_filter = st.sidebar.text_input('Filter by Message Contains')

# Apply filters
filtered_df = df[
    (df['name'].isin(name_filter) if name_filter else pd.Series([True] * len(df))) &
    (df['channel_name'].isin(channel_filter) if channel_filter else pd.Series([True] * len(df))) &
    (df['thread_name'].isin(thread_filter) if thread_filter else pd.Series([True] * len(df))) &
    (df['message'].str.contains(message_filter, case=False, na=False) if message_filter else pd.Series([True] * len(df)))
]

# Display filtered data
st.write(filtered_df)

# Group By functionality
st.sidebar.markdown("### Group By Options")
group_by_columns = st.sidebar.multiselect('Select columns to group by', options=df.columns.tolist())

if group_by_columns:
    grouped_df = filtered_df.groupby(group_by_columns).size().reset_index(name='count')
    st.write("### Grouped Data")
    st.write(grouped_df.sort_values(by="count", ascending=False))
