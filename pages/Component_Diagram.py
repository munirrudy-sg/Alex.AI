import streamlit as st
from helper import mode_selection, plantuml, formatImage, add_logo_test
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
import io
from streamlit_extras.row import row
from streamlit_extras.grid import grid
from streamlit_extras.app_logo import add_logo

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None

def main():
    # Set wide page config
    st.set_page_config(layout="wide")
    add_logo_test()

    mode_selection()

    # Initialse chat message history
    if "messages" not in st.session_state:
        st.session_state.messages = ChatMessageHistory()

    # Initialise empty messages
    if "requirements" not in st.session_state:
        st.session_state.requirements = []

    # Initialise empty diagram
    if "diagram" not in st.session_state:
        st.session_state.diagram = None

    # Initialise "initialised"
    if "currentState" not in st.session_state:
        st.session_state.currentState = "Start"
        
    # Initialise "initialised"
    if "startAnew" not in st.session_state:
        st.session_state.startAnew = True

    # Initialise "component_diagram"
    if "component_diagram" not in st.session_state:
        st.session_state.component_diagram = True

    # Initialise var to take UML code from class diagram
    if 'classPlantUML' not in st.session_state:
        st.session_state.classPlantUML = ""

    st.title("Components, Ports and Lollipop! ")

    # Create two columns
    left_column, right_column = st.columns([1, 2], gap = "large")

    # Add content to the left column
    with left_column.container(height=900, border=False):

        st.header("Generate Components")

        def initialisiation():
            st.session_state.currentState = "Start"

        def useClassDiagram():
            """ Function to use the class diagram to generate the component diagram """
            classPlantUML = st.session_state.classPlantUML

            if classPlantUML == "":
                st.session_state.currentState = "No Diagram"
            else:
                st.session_state.currentState = "Use Diagram"
                template = f"""
                            Based on the requirements, I want you to generate the component diagram for it. 
                            You should first group the classes that can be logically combined into larger components and then afterwards define the interfaces between components. 
                            Label the boxes and the interfaces shall be named with an "i" infront like "iAccount". 
                            Every interface should be connected by at least 2 components. Follow the format below on how you should respond. 
                            
                            Response Format:
                            Explaination on the rationale behind the components created and the interfaces

                            @startuml
                            skinparam linetype ortho
                            uml code here
                            @enduml

                            ____

                            Class Diagram:
                            {classPlantUML}

                            Example of component diagram:
                            @startuml
                            DataAccess - [First Component]
                            [First Component] ..> HTTP : use
                            @enduml
                            """
                # Prompt the model
                st.session_state.messages.messages.append(HumanMessage(content=template))

                # Start and End markers
                uml_start_marker = "@startuml"
                uml_end_marker = "@enduml"

                # Invoke the chatbot and define the tags to find the uml code
                response = st.session_state.chatbot.invoke(st.session_state.messages.messages)
                start_index = response.content.find(uml_start_marker)
                end_index = response.content.find(uml_end_marker)

                # Find the uml diagram code and generate the diagram
                if start_index != -1 and end_index != -1:
                    uml_code = response.content[start_index + len(uml_start_marker):end_index].strip()
                    diagram = formatImage(plantuml.processes(uml_code))
                    st.session_state.component_diagram = uml_code
                    st.session_state.diagram = diagram

                # Generate the AI response and store it in the chat history
                ai_message = AIMessage(content=response.content)
                st.session_state.messages.messages.append(ai_message)
            

        def startNew():
            st.text(st.session_state.classPlantUML)
            st.session_state.currentState = "Start Anew"

        def addRefinements():
            """ Function to add refinements to the component diagram """

            st.write('''How would you refine your component diagram?''')
            # Initialise changes_fields
            if 'component_refinements' not in st.session_state or not st.session_state.component_refinements:
                st.session_state.component_refinements = [None]

            def add_refinements_field():
                st.session_state.component_refinements.append(None)

            # Display all changes fields
            for index, _ in enumerate(st.session_state.component_refinements):
                st.session_state.component_refinements[index] = st.text_input(f"Changes {index + 1}", st.session_state.component_refinements[index], key=f"change_{index+1}")

            # Button to add new change field
            st.button("Add Field", on_click=add_refinements_field)

            def make_changes_to_component_diagram():
                if st.session_state.component_refinements != []:
                    refinements = [f"{index}: {refinements}" for index, refinements in enumerate(st.session_state.component_refinements)]
                    st.session_state.component_refinements = []
                    template = f"""
                                Make the following changes to the component diagram that you have generated prior based on the changes listed below:

                                {refinements}

                                Below is the reference of the component diagram created in your previous response:
                                {st.session_state.component_diagram}

                                Follow this template:

                                <Explain the changes and justification>

                                @startuml
                                skinparam linetype ortho
                                <UML diagram here>

                                @enduml

                                In addition, explain the changes that you have made to the UML diagram, and provide your justification for each change made.
                                """
                    # Prompt the model
                    st.session_state.messages.messages.append(HumanMessage(content=template))

                    # Start and End markers
                    uml_start_marker = "@startuml"
                    uml_end_marker = "@enduml"

                    # Invoke the chatbot and define the tags to find the uml code
                    response = st.session_state.chatbot.invoke(st.session_state.messages.messages)
                    start_index = response.content.find(uml_start_marker)
                    end_index = response.content.find(uml_end_marker)

                    # Find the uml diagram code and generate the diagram
                    if start_index != -1 and end_index != -1:
                        uml_code = response.content[start_index + len(uml_start_marker):end_index].strip()
                        diagram = formatImage(plantuml.processes(uml_code))
                        st.session_state.component_diagram = uml_code
                        st.session_state.diagram = diagram

                    # Generate the AI response and store it in the chat history
                    ai_message = AIMessage(content=response.content)
                    st.session_state.messages.messages.append(ai_message)
                            
            st.button("✨Refine", on_click=make_changes_to_component_diagram)

        def addRequirements():
            """ Function to add requirements to the component diagram """

            # Initialise changes_fields
            if 'component_requirements' not in st.session_state or not st.session_state.component_requirements:
                st.session_state.component_requirements = [None]

            def add_requirements_field():
                st.session_state.component_requirements.append(None)

            # Display all changes fields
            for index, _ in enumerate(st.session_state.component_requirements):
                st.session_state.component_requirements[index] = st.text_input(f"Requirement {index + 1}", st.session_state.component_requirements[index], key=f"change_{index+1}")

            # Button to add new change field
            st.button("Add Field", on_click=add_requirements_field)

            def createComponentDiagram():
                """ Function to generate the component diagram """

                if st.session_state.component_requirements != []:
                    requirements = [f"{index}: {requirement}" for index, requirement in enumerate(st.session_state.component_requirements)]
                    st.session_state.component_requirements = []
                    template = f"""
                                Based on the requirements, I want you to generate the component diagram for it. 
                                You should first group the classes that can be logically combined into larger components and then afterwards define the interfaces between components. 
                                Label the boxes and the interfaces shall be named with an "i" infront like "iAccount". 
                                Every interface should be connected by at least 2 components. Follow the format below on how you should respond. 

                                Response Format:
                                Explaination on the rationale behind the components created and the interfaces

                                @startuml
                                skinparam linetype ortho    
                                uml code here
                                @enduml

                                ____

                                Requirements:
                                {requirements}

                                Example of component diagram:
                                @startuml
                                DataAccess - [First Component]
                                [First Component] ..> HTTP : use
                                @enduml
                                """
                    # Prompt the model
                    st.session_state.messages.messages.append(HumanMessage(content=template))

                    # Start and End markers
                    uml_start_marker = "@startuml"
                    uml_end_marker = "@enduml"

                    # Invoke the chatbot and define the tags to find the uml code
                    response = st.session_state.chatbot.invoke(st.session_state.messages.messages)
                    start_index = response.content.find(uml_start_marker)
                    end_index = response.content.find(uml_end_marker)

                    # Find the uml diagram code and generate the diagram
                    if start_index != -1 and end_index != -1:
                        uml_code = response.content[start_index + len(uml_start_marker):end_index].strip()
                        diagram = formatImage(plantuml.processes(uml_code))
                        st.session_state.component_diagram = uml_code
                        st.session_state.diagram = diagram

                    # Generate the AI response and store it in the chat history
                    ai_message = AIMessage(content=response.content)
                    st.session_state.messages.messages.append(ai_message)
                    #Upon creation
                    st.session_state.startAnew = False
                
            st.button("✨Generate", on_click=createComponentDiagram)

        if st.session_state.currentState == "Start":
            st.write('''Would you like to continue with your class diagram or start anew?''')
            grid_startbuttons = grid(2, vertical_align="bottom")
            grid_startbuttons.button("✨Evolve my class diagram!", on_click=useClassDiagram)
            grid_startbuttons.button("Fresh start!", on_click=startNew)
        
        elif st.session_state.currentState == "Use Diagram":
            addRefinements()
        
        elif st.session_state.currentState == "No Diagram":
            st.markdown('''Hold on! To build a component diagram, we'll need a class diagram first. Would you like to create one or start designing components directly?''')

            st.page_link("pages/Class_Diagram.py", label = "Go to Class Diagram")
            st.button("Fresh start!", on_click=startNew)
            st.button("Retry", on_click=initialisiation)
        
        elif st.session_state.currentState == "Start Anew":
            if st.session_state.startAnew:
                addRequirements()
                
            else:
                addRefinements()

    # Add content to the right column
    with right_column.container(height=800, border=False):
        row2 = grid([1,6], vertical_align="bottom")
        row2.header("Diagram")

        # Display output diagram
        if st.session_state.diagram:
            # Convert the Image object to bytes for the download button
            buffered = io.BytesIO()
            st.session_state.diagram.save(buffered, format="JPEG")
            # Reset buffer position to the beginning so `st.download_button` reads from start    
            buffered.seek(0)
            # Download button
            row2.download_button(
                    label="Download Image",
                    data=buffered,
                    file_name="diagram.jpg",
                    mime="image/jpeg"
                )
            st.image(st.session_state.diagram)
        else:
            st.image("https://i.ibb.co/8bCp0Ng/lolipopmeme.png")
        
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



if __name__ == "__main__":
    main()