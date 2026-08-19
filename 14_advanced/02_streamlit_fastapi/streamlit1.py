import streamlit as st

# Set page config
#st.set_page_config(page_title="Basic App", layout="centered")

# Title
st.title("Basic Streamlit App")

# Sidebar
st.sidebar.header("Configuration")
name = st.sidebar.text_input("Enter your name:")

# Main content
if name:
    st.write(f"Hello, {name}! 👋")

