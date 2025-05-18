import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.tools import tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

llm = LLM(
    model="azure/gpt-4o",
    base_url="https://cvent-dev2-azure-chatgpt.openai.azure.com/",
    api_key= os.environ.get("AZURE_OPENAI_KEY")
)


@tool("Code Generation", description="Generates code.")
def generate_code(specification: str, programming_language: str, context: str = "") -> str:
    if context:
        return f"``` {programming_language}\n# Context: {context}\n# Generated code for: {specification}\n# ... (Your generated code here) ...\n```"
    else:
        return f"``` {programming_language}\n# Generated code for: {specification}\n# ... (Your generated code here) ...\n```"


@tool("Code Refinement", description="Refines code.")
def refine_code(code: str, feedback: str) -> str:
    return f"```\n# Refined code:\n# Original code:\n{code}\n# Feedback: {feedback}\n# ... (Refined code based on feedback) ...\n```"


def create_agents():
    architect = Agent(
        role="Software Architect",
        goal="Design the overall structure and components of complex software systems.",
        backstory="You are an experienced software architect, focusing on scalable and maintainable designs.",
        verbose=True,
        llm=llm,
    )

    coder = Agent(
        role="Code Generator",
        goal="Generate complex code based on the architect's designs and user specifications.",
        backstory="You are a highly skilled code generator, specializing in creating robust and efficient code.",
        verbose=True,
        llm=llm,
        tools=[generate_code, refine_code],
    )

    code_reviewer = Agent(
        role="Code Reviewer",
        goal="Review generated code for quality, efficiency, and adherence to best practices.",
        backstory="You are a meticulous code reviewer, ensuring high-quality software development.",
        verbose=True,
        llm=llm,
    )
    return architect, coder, code_reviewer


def create_tasks(architect, coder, code_reviewer, app_specification, programming_language):
    task1 = Task(
        description=f"Design the architecture for the application with the following specification: {app_specification}. Consider scalability, maintainability, and best practices for {programming_language}.",
        agent=architect,
        expected_output="normal"
    )

    task2 = Task(
        description=f"Generate the code in {programming_language} based on the architecture and specification. The application should accomplish: {app_specification}.",
        agent=coder,
        context=[task1],
        expected_output="normal"
    )

    task3 = Task(
        description=f"Review the generated code for {app_specification} in {programming_language} for quality, efficiency, and adherence to best practices. Provide specific feedback for improvements.",
        agent=code_reviewer,
        context=[task1, task2],
        expected_output="normal"
    )

    task4 = Task(
        description=f"Refine the generated code based on the code reviewer's feedback. Apply the suggested improvements and ensure the code meets the specification for {app_specification} in {programming_language}.",
        agent=coder,
        context=[task1, task2, task3],
        expected_output="normal"
    )

    return [task1, task2, task3, task4]


def run_code_generation_crew(app_specification, programming_language):
    architect, coder, code_reviewer = create_agents()
    tasks = create_tasks(architect, coder, code_reviewer, app_specification, programming_language)

    crew = Crew(
        agents=[architect, coder, code_reviewer],
        tasks=tasks,
        verbose=True,
        process=Process.sequential,
    )
    result = crew.kickoff()
    return result


app_specification = """
Can you create a simple flask application
"""
programming_language = "Python"
generated_code = run_code_generation_crew(app_specification, programming_language)
print(f"Generated Code:\n{generated_code}")
with open("response.txt", "a") as file:
    file.write(str(generated_code))










