import streamlit as st

# Set page config
#st.set_page_config(page_title="Basic App", layout="centered")

# Title
st.title("Basic Streamlit App")

prompt =   st.chat_input("Ask something")

if prompt:
    st.chat_message("user").write(prompt)
    response = "This is a placeholder response."  # Replace with actual response logic
    st.chat_message("assistant").write(response)

