# Alex.AI

**1st Prize in the National AI Student Challenge 2024, Track 3**

Greetings! I am Alex, a tool that is used to assist students and working software engineers in speeding up their software engineering needs!

## 1 - What is Alex.AI?

Alex.AI is an application powered by a large-language model (LLM) that assists software engineers with their needs in the early stages of the software development lifecycle (SDLC).

## 2 - The Problem

- The “analysis” and “design” phases in the software development lifecycle (SDLC) are phases whereby developers take the requirements gathered in the planning phase, analyse these requirements to software use cases, and then translate them into plans to implement the solution.
  
- In these phases, several diagrams are typically created, such as use-case diagrams and use-case descriptions to illustrate the use cases of the software product,  as well as other diagrams that represent the entire architecture of the software, such as class diagrams and component diagrams, allowing developers to get a proper overview of how software components interact with one another.
  
- These deliverables necessitate days of examining requirements documents and frequent discussions and debates between engineers, which can be time-consuming and mentally draining. In addition, these diagrams are time-consuming to produce manually (through the use of tools such as draw.io or Lucidchart)

## 3 - The Solution

The solution is an application powered by an LLM - using the power of prompt engineering and deep learning to enhance the analysis and design phases of the SDLC. The application is capable of performing the following tasks:

1. Use Case Description generation
2. Use Case Diagram generation
3. Identifying potential candidate classes
4. Class diagram generation
5. Component diagram generation

## 4 - App Features

### 1. Home Page

The home page provides users with an introduction to **Alex.AI**. The app's features, functionalities, as well as its contributors are displayed here. The sidebar allows users to navigate between the various functionalities described in the previous section.

![Something](https://i.ibb.co/P15rgGz/Screenshot-2024-05-27-at-9-18-24-AM.png)

### 2. Use Case Description and Use Case Diagram Generation

This feature allows users to generate **Use Case Descriptions** and **Use Case Diagrams** for a software system. For context, **Use Case Description** and **Use Case Diagrams** define the use cases of a software system from the perspective of an *actor* or *user*. Without these, the question of *"What should we build?"* remains unanswered. 

Typically, these software use cases are defined from a set of *requirements*, typically specified from the software client. A team of software engineers would then need to analyse each of these requirements manually, looking for the nouns and verbs that can correlate to software use cases. For a small scale software (i.e., such as a school project or prototype) product, there would be an estimate of ~20+ requirements, but for larger scale software, such as those deployed in production, the number of requirements grows exponentially, especially when more software stakeholders are involved and more security and privacy-related requirements come into play. As such, analysing each of these requirements will take up plenty of valuable time!

But, don't fret! We have a solution to this. Alex.AI solves this with the ability to generate **both** Use Case Descriptions and Use Case Diagrams from a input set of requirements. An example will be shown below. 

#### Example

For the showcase, we will be using a subset of software requirements from a school project to develop a workload management system for security staff. In the interest of simplicity, a subset of the functional requirements (FR) will be used for generation of the software use cases.

|FR|Requirement|
|---|---|
|FR1|Users must be able to register for an account using their email address, phone number, or through third-party authentication services (e.g., Google, Facebook).|
|FR2|The system must authenticate users before allowing access to the app functionalities.|
|FR3|The system should provide options for password recovery and account verification through email or SMS.|
|FR4|Users must be able to create and edit their profile, including setting a profile picture, bio, and personal information.|
|FR5|Users should have the option to set their profiles as public or private.|
|FR6|The system should allow users to manage their privacy settings, including who can see their posts, send them messages, and follow them.|
|FR7|Users must be able to post content, including text, photos, and videos.|
|FR8|The system should support tagging of other users and adding locations to posts.|
|FR9|Users must be able to like, comment on, and share posts.|
|FR10|The system should provide notifications to users when their posts are liked, commented on, or sifared.|
|FR11|Users should be able to report content that violates the app's community guidelines.|

***Todos***
- Insert image of use case diagram / use case description generated by the app
- Explanation
   
### 3. Candidate Class Identification

***Todos***

- Description of why this stage is important
- How this feature tackles this problem
- Example

### 4. Class Diagram Generation

***Todos***

- Premise of class diagram
- 'Changes' feature

### 5. Component Disagram Generation

***Todos***

- Premise of component diagram
- Example 

## 6 - Prompt Engineering Techniques Used

### 1. Few-shot prompting

Few-shot prompting was for generating use case diagrams based on the requirements. As shown below, several "example" outputs are used as prompts to inform the model of generating the use case to requirements mapping and the actor to use case mappings:

```
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
```
### 2. Chain-of-thought prompting

Chain-of-thought prompting is used to generate the class diagram based on the requirements, necessitating a breakdown of complex task of creating a class diagram into smaller steps, such as identifying relationships between classes, providing examples of relationship types, as well as explaining the rationale of the relationship types chosen.

```
template = f"""
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
```

## 7 - Advantages of Alex.AI

1. Saves time by eliminating trial-and-error in crafting prompts for complex diagrams.
2. Reduces knowledge barrier as allowing users of any proficiency level to create quality diagrams.
3. Explains the rationale behind the diagrams generated which indirectly teaches software design principles.


## 8 - Usage

- Before running the program, ensure that you have the following libraries (more details on the requirements can be found in the `requirements.txt` file):
  - streamlit
  - streamlit_extras
  - langchain-openai
  - plantuml
  - validators

- Clone the repository
- In the `keys.txt` file, replace `YOUR_API_KEY` with your own OpenAI API key
- Run the program using `streamlit run Home.py`
- Once the program is running, you can access it through your web browser. Streamlit applications should be accessible at `localhost:8501`.
- Follow the on-screen instructions and interact with the application depending on whether you are dealing with a class diagram, component diagram, or User-centered design (UCD) with your prompt. <br />

Should you encounter any issues or have feedback, please share it with us.

## 9 - Technologies Used

- Python
- Langchain
- Streamlit
- GPT-4 Turbo Model
