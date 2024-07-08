# Langchain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser

from langchain_anthropic import ChatAnthropic

# Imports pertaining to plantuml
from plantuml import PlantUML
from PIL import Image
import io
import streamlit as st

plantuml = PlantUML(url='http://www.plantuml.com/plantuml/img/')

def generatePlantUMLImage(plantuml_text):
    """ Function to generate plantuml image from plantuml text. Returns raw image data """
    return plantuml.processes(plantuml_text)

def formatImage(image):
    """ Function to format raw image data into an image object """
    return Image.open(io.BytesIO(image))

def retrieveOpenAIAPIKey(file_path):
    """ Function to retrieve OpenAI API key from the user """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Check if the line starts with API_KEY
                if line.startswith('API_KEY'):
                    # Extract the API key value
                    # Assuming the format is API_KEY="..."
                    api_key = line.strip().split('=')[1].strip('"')
                    return api_key
    except FileNotFoundError:
        print("The file was not found.")
        return None

def formatImage(image):
    """ Formats the image to an Image object, given the raw image data """
    return Image.open(io.BytesIO(image))

api_key = retrieveOpenAIAPIKey('keys.txt')

# Create a chatbot instance
# chatbot = ChatOpenAI(model="gpt-4-turbo-preview", api_key=api_key)
# gpt-4-turbo-preview > points to gpt-4-0125-preview
# gpt-3.5-turbo-0125 > a lot quicker than gpt 4 turbo but output is more messy
# History of messages
messages = ChatMessageHistory()

def add_logo_test():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.ibb.co/ZYXr2hq/alex-ai-logo.png);
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: 20px 20px;
                background-size: 300px auto;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def mode_selection():
    # Check if a chatbot is already selected
    if 'chatbot' in st.session_state and st.session_state.chatbot is not None:
        current_chatbot = st.session_state.chatbot
        if isinstance(current_chatbot, ChatAnthropic):
            st.sidebar.write('Current Chatbot: 🤖 Claude 3.5 Sonnet')
        elif isinstance(current_chatbot, ChatOpenAI):
            st.sidebar.write('Current Chatbot: 🧠 GPT-4o ChatGPT')
    else:
        st.sidebar.write('No chatbot selected')

    # Selection box for changing the chatbot
    option = st.sidebar.selectbox(
        'Select the mode:',
        options=['Claude', 'ChatGPT'],
        format_func=lambda x: '🤖 Claude 3.5 Sonnet' if x == 'Claude' else '🧠 GPT-4o ChatGPT'
    )

    api_key = st.sidebar.text_input("Enter API Key:", type="password")

    if st.sidebar.button("Change Chatbot"):
        if option == 'Claude':
            st.sidebar.success('Claude 3.5 Sonnet will be used')
            st.session_state.chatbot = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=api_key)
        elif option == 'ChatGPT':
            st.sidebar.info('GPT-4o will be used')
            st.session_state.chatbot = ChatOpenAI(model="gpt-4o", api_key=api_key)
