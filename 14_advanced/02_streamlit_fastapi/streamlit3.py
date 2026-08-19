import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load environment variables
load_dotenv()

# Create an OpenAI client
# os.getenv needs the variable name as a string inside quotes
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit page configuration must be called before other Streamlit elements
st.set_page_config(
    page_title="Chatbot" ,
    layout="wide", 
    page_icon="🤖"
)
st.title("AI chat assistant with Streamlit and FastAPI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("Ask something")

if prompt:
    # 1. Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    st.write("Generating response after user input...")

    # 2. Generate and display assistant response stream
    with st.chat_message("assistant"):
        # Correct OpenAI streaming syntax for chat completions
        stream = client.chat.completions.create(
            model="gpt-4o",  # Updated to a valid model name
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        # st.write_stream automatically handles the OpenAI stream iterator
        response = st.write_stream(stream)

    # 3. Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
