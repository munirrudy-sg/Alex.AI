import streamlit as st
from helper import plantuml, formatImage, add_logo_test
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
import io
from streamlit_extras.row import row
from streamlit_extras.grid import grid
from streamlit_extras.app_logo import add_logo

import streamlit as st

# Define the page layout
st.set_page_config(page_title="About", layout="wide")
add_logo_test()

# Use the 'with' statement to create a container, then put your content inside it
with st.container():
    st.title("Hello, I am Alex.AI! 👋")
    st.write("""
    ### What am I?         
    Ever felt overwhelmed by UML diagrams? I hear you! That's why I'm here! 
             With the brainpower of GPT-4 Turbo, I turn the complex into the comprehensible.

    Here's what I can do:
             
    - **Use Case Diagram & Descriptions**
    - **Class Diagram**
    - **Component Diagram**
             
    I not only create the diagrams, but I also explain the reasoning behind them - so that students (like my creators) can finally understand what's going on.

    ### Why do I exist?
    My creators were in your shoes. They had awesome ideas but diagramming felt like a chore. They thought "There's gotta be a better way!" so 
             they then put their heads together and sparked me to life. 

    With me, you get to focus on the real deal - crafting killer software. Great ideas shouldn't be bogged down by diagramming, so let me streamline the process. 

    ### Who created me?
    Alex.AI is developed by a dedicated team of four undergraduates passionate in AI and Software Engineering.
             
    Got feedback or just wanna say hi? Contact them below!
             
    - Farhan Azmi ([GitHub](https://github.com/farhanazmiCS) | [LinkedIn](https://www.linkedin.com/in/farhanazmi0017/))
    - Munir Rudy ([GitHub](https://github.com/munirrudy-sg) | [LinkedIn](https://www.linkedin.com/in/munirrudy/))
    - Ang Jun Jie ([GitHub](https://github.com/buppanasu) | [LinkedIn](https://www.linkedin.com/in/ang-jun-jie-49a827174/))
    - Eugene Gan ([GitHub](https://github.com/eugenegancw) | [LinkedIn](https://www.linkedin.com/in/eugene-gan98/))

    ####     Ready to design? Let's get started with Alex.AI!
    """)
