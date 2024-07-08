import time
import streamlit as st
from helper import plantuml, formatImage, add_logo_test, mode_selection
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
from streamlit_extras.grid import grid
import io
from streamlit_extras.stateful_button import button
from streamlit_extras.app_logo import add_logo

add_logo_test()

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None

mode_selection()

if 'usecase_flag' not in st.session_state:
    st.session_state.usecase_flag = False
if 'table_data' not in st.session_state:
    st.session_state.table_data = ""    
if 'uml_code' not in st.session_state:
    st.session_state.uml_code = ""

def handle_requirements_input():
    """ Function for handling input pertaining to requirements. This includes adding new requirements. """
    # Dynamic text input fields for requirements
    if 'text_fields' not in st.session_state:
        st.session_state.text_fields = []

    for index, _ in enumerate(st.session_state.text_fields):
        st.session_state.text_fields[index] = st.text_input(f"Requirement {index + 1}", key=f"requirement_{index}")
        
    st.button("Add Field", on_click=add_text_field)

    if st.button("✨Generate", on_click=generate_diagram) and st.session_state.text_fields:
        st.session_state.requirements = st.session_state.text_fields

def handle_refinements_input():
    """ Function for handling input pertaining to refinements. This includes adding new refinements. """
    # Dynamic text input fields for refinements
    if 'refinement_text_fields' not in st.session_state or not st.session_state.refinement_text_fields:
        st.session_state.refinement_text_fields = [None]
       
    for index, _ in enumerate(st.session_state.refinement_text_fields):
        st.session_state.refinement_text_fields[index] = st.text_input(f"Change {index + 1}", key=f"change_{index}")    

    st.button("Add Field", on_click=add_refinement_text_field)

    st.button("Generate Use Case Descriptions", on_click=generate_usecase)

    if st.button("✨Re-generate") and st.session_state.refinement_text_fields:
        st.session_state.refinements = st.session_state.refinement_text_fields
        regenerate_diagram()


# Use Case Description Generation
def generate_usecase():
    """ Function to generate use case descriptions based on the PlantUML code. """
    st.session_state.usecase_flag = True
    plantuml = st.session_state.uml_code
    # Construct the prompt/template with the requirements for the chatbot
    template = f"""
                Based on this PlantUML code, I want you to generate the use case description for every use case. 
                Each description should have Name, Actors, Preconditions and Main Sucess Path. 
                If there is a lack of information, generate them to your best knowledge of the use case. For every use case, follow the table format below. 
                It is a Markdown table format suitable for display in a Streamlit app. Represent every new line in the point form as semicolon.

                Use Case Format:
                | Name              |                                |
                |-------------------|--------------------------------|
                | Description       | xxxxx                          |
                | Actors            | xxxxx                          |
                | Preconditions     | xxxxx (in point form)          |
                | Main Success Path | xxxxx (in number bullet points)|

                PlantUML code:

                {plantuml}
                 """
    # Assuming st.session_state.chatbot.invoke() method takes a string and returns an object or string as a response
    response = st.session_state.chatbot.invoke(template)  # Simulate invoking the chatbot with the template
    # Here, we directly handle the response without appending it to chat history
    if response:  # Ensure response is not None or empty
        st.session_state.table_data = response.content  # Assign the response to a variable
    else:
        st.session_state.table_data = "No response received from the chatbot."

# Function to add a new text field
def add_text_field():
    """ Function to add a new text field for requirements. """
    st.session_state.text_fields.append(None)

# Function to add a new text field
def add_refinement_text_field():
    """ Function to add a new text field for refinements. """
    st.session_state.refinement_text_fields.append(None)

def generate_diagram():
    """ Function to generate the use case diagram based on the requirements. """

    # Check if requirements are available to generate a diagram
    if st.session_state.requirements:
        # Construct the requirements string to be included in the template
        requirements = [f"{index + 1}: {requirement}" for index, requirement in enumerate(st.session_state.requirements, 1)]

        # Construct the prompt/template with the requirements for the chatbot
        template = f"""
            Based on these requirements, I will like you to generate for me a use case diagram.
            
            Here are the requirements:
            {requirements}
 
            In addition, explain the use cases and actors in the following format:

            Use case to requirements mapping:

            Use Case 1: Satisfies requirements 1 and 2 as ...
            Use Case 2: Satisfies requirements 3 as ...
            ...

            Actor to use case mapping:

            Actor 1: Uses Use Case 1 and 2 as ...
            Actor X: ...

            @startuml

            <PlantUML code here>

            @enduml 

        """

        # Append the user's message with the template to the message history
        st.session_state.messages.messages.append(HumanMessage(content=template))

        # Invoke the chatbot to generate the response
        response = st.session_state.chatbot.invoke(st.session_state.messages.messages)

        # Extract UML code from the response
        uml_start_marker = "@startuml"
        uml_end_marker = "@enduml"
        start_index = response.content.find(uml_start_marker)
        end_index = response.content.find(uml_end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Extract and process the UML code
            uml_code = response.content[start_index:end_index + len(uml_end_marker)].strip()
            st.session_state.uml_code = uml_code
            diagram = formatImage(plantuml.processes(uml_code))
            
            # Update the session state with the new diagram
            st.session_state.ucd_diagram = diagram

            # Generate the AI response and store it in the chat history
            ai_message = AIMessage(content=response.content)
            st.session_state.messages.messages.append(ai_message)

                # After successfully generating the diagram, set the flag to True
            st.session_state['diagram_generated'] = True

            # # After updating, rerun the app to refresh the UI
            # st.rerun()

    else:
        st.empty()

def regenerate_diagram():
    """ Function to regenerate the use case diagram based on the refinements that the user has input. """

    # Check if there are any refinements to process
    if st.session_state.refinements:

        # You might need to adapt this to your context. For instance, if refinements are 
        # supposed to modify the requirements or provide additional details for the diagram generation:
        refinements = [f"{index + 1}: {refinement}" for index, refinement in enumerate(st.session_state.refinements, 1)]
        formatted_refinements = "\n".join(refinements)
        newline = "\n"
        # Assuming you would adapt the template or the request to your chatbot based on refinements
        template = f"""
        I will like you to update the use case diagram based on these changes, with the original, following the template:

        @startuml

        <UML diagram here>

        @enduml
            
        Here are the refinements to be made
        {formatted_refinements}

        Original requirements were:
        {newline.join([f"{index + 1}: {req}" for index, req in enumerate(st.session_state.requirements, 1)])}

        Same as before,please explain the use cases and actors in the following format:
        
        Use case to requirements mapping:

        Use Case 1: Satisfies requirements 1 and 2 as ...
        Use Case 2: Satisfies requirements 3 as ...
        ...

        Actor to use case mapping:

        Actor 1: Uses Use Case 1 and 2 as ...
        Actor X: ...
        """

        #To add the refinements to the original reuqirements, for iterative refinement of the diagram
        st.session_state.requirements.extend(st.session_state.refinements)
        # Append the user's message with the refinements to the message history
        st.session_state.messages.messages.append(HumanMessage(content=template))

        # Invoke the chatbot to generate the updated response
        response = st.session_state.chatbot.invoke(st.session_state.messages.messages)

        # Assume the response contains an updated UML section to be processed
        uml_start_marker = "@startuml"
        uml_end_marker = "@enduml"
        start_index = response.content.find(uml_start_marker)
        end_index = response.content.find(uml_end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Extract and process the updated UML code
            uml_code = response.content[start_index:end_index + len(uml_end_marker)].strip()
            st.session_state.uml_code = uml_code
            diagram = formatImage(plantuml.processes(uml_code))
            
            # Update the session state with the new diagram
            st.session_state.ucd_diagram = diagram

            # Generate the AI response and store it in the chat history
            ai_message = AIMessage(content=response.content)
            st.session_state.messages.messages.append(ai_message)

            # After updating, rerun the app to refresh the UI
            st.rerun()
        
        else:
            st.empty()
    

def handle_right_column():    
    """ Function to handle the right column of the page. """

    # Display output diagram
    row2 = grid([1,6], vertical_align="bottom")
    row2.header("Diagram")
    if st.session_state.ucd_diagram != None:
        st.image(st.session_state.ucd_diagram)
        #st.rerun()
        # Display output diagram
        if st.session_state.ucd_diagram:
            # Convert the Image object to bytes for the download button
            buffered = io.BytesIO()
            st.session_state.ucd_diagram.save(buffered, format="JPEG")
            # Reset buffer position to the beginning so `st.download_button` reads from start    
            buffered.seek(0)    
            # Download button
            row2.download_button(
                    label="Download Image",
                    data=buffered,
                    file_name="ucd_diagram.jpg",
                    mime="image/jpeg"
                )
    else:
        st.image("https://www.modernanalyst.com/Portals/0/Public%20Uploads%205/Fin257-UML-Diagrams-Training.jpg") 
    
    st.header("Explanation")
    # Display the message
    for message in st.session_state.messages.messages:
        if isinstance(message, AIMessage) and st.session_state.messages.messages[-1] == message:
            lines = message.content.splitlines()
            uml_start_index = next((i for i, line in enumerate(lines) if "@startuml" in line), -1)
            uml_end_index = next((i for i, line in enumerate(lines) if "@enduml" in line), -1)

            if uml_start_index > 0 and uml_end_index > uml_start_index:
                # Remove one line before "@startuml" and lines until "@enduml" inclusive
                part_before_uml = "\n".join(lines[:uml_start_index-3]).strip()
                if part_before_uml:
                    st.markdown(part_before_uml)
            else:
                # Display the entire message content if no UML block is found
                st.markdown(message.content)
    
    if st.session_state.usecase_flag:
        st.header("Use Case Description")
        # Remove all occurrences of <br> tags
        no_br_data = st.session_state.table_data.replace("<br>", "")
        # Find the first occurrence of "###"
        first_hash_index = no_br_data.find("###")
        # Check if "###" is found
        if first_hash_index != -1:
            # Remove everything before the first occurrence of "###"
            cleaned_data = no_br_data[first_hash_index:]
            # Display the cleaned table data
            st.markdown(cleaned_data)
        else:
            # If "###" is not found, display the data without <br> tags
            st.markdown(no_br_data)

def main():
    # Initialse chat message history
    if "messages" not in st.session_state:
        st.session_state.messages = ChatMessageHistory()

    # Initialise empty messages
    if "requirements" not in st.session_state:
        st.session_state.requirements = []

    # Initialise messages regarding changes
    if "refinements" not in st.session_state:
        st.session_state.refinements = []

    # Initialise empty diagram
    if "ucd_diagram" not in st.session_state:
        st.session_state.ucd_diagram = None

    # Initialize the diagram_generated flag in session state if it's not present
    if 'diagram_generated' not in st.session_state:
        st.session_state['diagram_generated'] = False

    st.title("Spill the Beans! What Can Your Software Do?")

# Create two columns
    left_column, right_column = st.columns([1, 2], gap = "large")
    # left_column, right_column = st.columns(2, gap="large")
    with left_column.container(height=800, border=False):
        # Check the diagram_generated flag instead of st.session_state.ucd_diagram
        if not st.session_state.diagram_generated:
            st.header("Generate Use Cases")
            st.write("Enter your software requirements and let Uncle Alex do the rest 😉")
            handle_requirements_input()
        else:
            st.header("What can I do better?")
            handle_refinements_input()

    with right_column.container(height=800, border=False):
        handle_right_column()


if __name__ == "__main__":
    main()
