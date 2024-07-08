import streamlit as st
from helper import mode_selection, plantuml, formatImage, add_logo_test
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
import io
from streamlit_extras.row import row
from streamlit_extras.grid import grid
from streamlit_extras.app_logo import add_logo

if 'classPlantUML' not in st.session_state:
    st.session_state.classPlantUML = ""

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

    # Initialise "identified"
    if "identified" not in st.session_state:
        st.session_state.identified = False
    
    # Initialise "generate class diagram"
    if "class_diagram_generated" not in st.session_state:
        st.session_state.class_diagram_generated = False

    # Initialise changes to be made
    if "changes" not in st.session_state:
        st.session_state.changes = []

    st.title("It's Design Time!")

    # Create two columns
    left_column, right_column = st.columns([1, 2], gap = "large")

    # Add content to the left column
    with left_column.container(height=900, border=False):
        
        st.header("Generate Class Diagram")
        
        if not st.session_state.identified:
            st.write("Enter your software requirements and classes it shall become...")

            # Initialize text_fields if it doesn't exist in session state
            if 'text_fields' not in st.session_state or not st.session_state.text_fields:
                st.session_state.text_fields = [None]  # Start with one empty text field

            # Function to add a new text field
            def add_text_field():
                st.session_state.text_fields.append(None)

            # Display all text fields
            for index, _ in enumerate(st.session_state.text_fields):
                st.session_state.text_fields[index] = st.text_input(f"Requirement {index + 1}", st.session_state.text_fields[index], key=f"requirement_{index+1}")

            # Button to add a new text field
            st.button("Add Field", on_click=add_text_field)

            def identify_candidate_classes():
                #Function to identify the candidate classes for a class diagram
                st.session_state.requirements = st.session_state.text_fields
                st.session_state.identified = True
                # Prompt the model
                if st.session_state.requirements != []:
                    requirements = [f"{index}: {requirement}" for index, requirement in enumerate(st.session_state.requirements)]
                    template = f"""
                        You are a tool designed to take in software requirements and help software engineers identify the candidate classes for a class diagram.
                        
                        Based on these requirements, I will like you highlight the possible the candidate classes:
                        
                        Here are the requirements:
                        {requirements}

                        Explain the candidate classes that you have identified, provide your justification for each class identified, and which requirement(s) it satisfies. The design of this software system is only concerned with the backend of the system, any candidate classes that pertains to the user interface should be ignored. 
                        
                        Follow this response template:

                        Example (Social media app example)

                        Candidate Classes:
                        
                        1. User: The user class was identified as a candidate class because it is a key entity in the system. It is responsible for creating and managing posts, following other users, and managing their profile. It fulfils requirement 1, and 2.
                        2. Post: The post class was identified as a candidate class because it is a key entity in the system. It allows users to create and share posts. It fulfils requirement 3.
                        
                        In addition, I would like you to generate for me the UML class diagram, without establishing the relationships between the candidate classes. Each class MUST have their attributes and methods. Generate the UML class diagram code in this format:
                        
                        @startuml

                            <UML diagram here>

                        @enduml

                        Example UML code:

                        @startuml

                            class User {{
                                - username: String
                                - password: String
                                - email: String
                                - profilePicture: Image
                                - bio: String
                                - followers: List<User>
                                - following: List<User>
                                + login(username: String, password: String): Boolean
                                + logout(): Void
                                + updateProfile(username: String, email: String, bio: String, picture: Image): Boolean
                            }}

                            class Post {{
                                - id: Integer
                                - image: Image
                                - caption: String
                                - likes: Integer
                                - comments: List<Comment>
                                + addLike(): Void
                                + addComment(comment: Comment): Void
                            }}


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
                        st.session_state.classPlantUML = uml_code
                        diagram = formatImage(plantuml.processes(uml_code))
                        st.session_state.diagram = diagram

                    # Generate the AI response and store it in the chat history
                    ai_message = AIMessage(content=response.content)
                    st.session_state.messages.messages.append(ai_message)
                    
        
            st.button("✨Identify Candidate Classes", on_click=identify_candidate_classes)
                
        elif not st.session_state.class_diagram_generated:
                st.write("Back to the drawing boards or generate the class diagram?")

                # Initialise changes_fields
                if 'changes_fields' not in st.session_state or not st.session_state.changes_fields:
                    st.session_state.changes_fields = [None] # Start with one empty text field
                
                def add_changes_field():
                    st.session_state.changes_fields.append(None)

                # Display all changes fields
                for index, _ in enumerate(st.session_state.changes_fields):
                    st.session_state.changes_fields[index] = st.text_input(f"Changes {index + 1}", st.session_state.changes_fields[index], key=f"change_{index+1}")

                # Button to add new change field
                st.button("Add Field", on_click=add_changes_field)

                def make_changes_to_identified_classes():
                    #Function to make changes to the identified classes
                    st.session_state.changes = st.session_state.changes_fields

                    if st.session_state.changes != []:
                        changes = [f"{index}: {changes}" for index, changes in enumerate(st.session_state.changes)]
                        template = f""" 
                            Make the following changes to the UML diagram that you have generated prior based on the changes listed below:

                            {changes}

                            Follow this template:

                            @startuml

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
                            st.session_state.classPlantUML = uml_code
                            diagram = formatImage(plantuml.processes(uml_code))
                            st.session_state.diagram = diagram

                        # Generate the AI response and store it in the chat history
                        ai_message = AIMessage(content=response.content)
                        st.session_state.messages.messages.append(ai_message)

                st.button("✨Refine Classes", on_click=make_changes_to_identified_classes)
                    
                def generate_class_diagram():
                    #Function to generate the class diagram based on the identified classes
                    template = """
                                Your task now is to refine a UML class diagram by introducing proper relationships between the previously identified candidate classes in your previous response. Do NOT change or remove the methods and attributes inside the candidate classes.

                                Based on the candidate classes and their descriptions provided earlier, your goal is to:

                                1. Identify the Types of Relationships: For each pair of classes, determine the most appropriate relationship type. Consider the nature of their interaction based on the software requirements. Only use the relationships below:

                                **Association** 

                                * **Syntax:** 
                                ```plantuml
                                classOne -- classTwo
                                ```
                                **Inheritance:**

                                * **Syntax:**
                                ```plantuml
                                class Subclass <|-- Superclass 
                                ```

                                **Realization (Interface)**

                                * **Syntax:**
                                ```plantuml
                                interface InterfaceName <|.. ImplementingClass 
                                ```

                                **Dependency:**

                                * **Syntax:**
                                ```plantuml
                                class DependentClass ..> IndependentClass
                                ```

                                **Aggregation:**

                                * **Syntax:**
                                ```plantuml
                                class Whole o-- Part 
                                ```

                                **Composition:**

                                * **Syntax:**
                                ```plantuml
                                class Whole *-- Part
                                ```

                                2. Specify Multiplicity: Only when it is needed to clarify, provide multiplicity for the relationships. This will clarify how many instances of a class can be associated with instances of another class. Follow the guideline below:

                                In class diagrams, multiplicity symbols (like "0..*" or "1") explain how many objects of one class can link to another. Show multiplicity when it clarifies the relationship's meaning, especially for ownership (aggregation/composition) or cardinality (one-to-one, one-to-many). For clear, simple relationships, you can sometimes omit it for better readability.

                                After updating the UML diagram, please provide a summary of the class diagram, including the type of relationship established between each pair of classes and your rationale for these decisions.

                                Follow this response template:

                                <Summary of relationships here>

                                <Rationale>

                                @startuml
                                skinparam linetype ortho
                                <UML diagram here>
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
                        st.session_state.diagram = diagram

                    # Generate the AI response and store it in the chat history
                    ai_message = AIMessage(content=response.content)
                    st.session_state.messages.messages.append(ai_message)
                    
                st.button("✨Generate Class Diagram ", on_click=generate_class_diagram)
        else:
            st.write("Enter the changes you would like to make to the class diagram")

            # Initialise changes_fields
            if 'changes_fields' not in st.session_state:
                st.session_state.changes_fields = []

            def add_changes_field():
                st.session_state.changes_fields.append(None)

            # Display all changes fields
            for index, _ in enumerate(st.session_state.changes_fields):
                st.session_state.changes_fields[index] = st.text_input(f"Changes {index + 1}", st.session_state.changes_fields[index], key=f"change_{index+1}")

            # Button to add new change field
            st.button("Add Field", on_click=add_changes_field)

            def make_changes_to_class_diagram():
                #Function to make changes to the class diagram
                st.session_state.changes = st.session_state.changes_fields
                st.session_state.changes_fields = []
            
            st.button("✨Refine Class Diagram", on_click=make_changes_to_class_diagram)

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
            st.image("https://i.redd.it/y0wptuzuqfn21.jpg", width=500)
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