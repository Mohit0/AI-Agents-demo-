import os
from flask import Flask, request, jsonify, render_template
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

llm = LLM(
    model="azure/gpt-4o",
    base_url="https://cvent-dev2-azure-chatgpt.openai.azure.com/",
    api_key= os.environ.get("AZURE_OPENAI_KEY")
)

app = Flask(__name__)

# Simulated department data
DEPARTMENT_DATA = {
    "sales": "Sales department data: Customer contacts and sales figures.",
    "engineering": "Engineering department data: Project blueprints and technical specifications.",
    "marketing": "Marketing department data: Campaign strategies and market research.",
    "hr": "HR department data: Employee records and performance reviews."
}

def check_department_access(user_department, requested_department, requested_data):
    """Simulates checking department data access controls."""
    if user_department and requested_department and requested_department.lower() in DEPARTMENT_DATA:
        if user_department.lower() == requested_department.lower():
            if requested_data == "all":
                return DEPARTMENT_DATA[requested_department.lower()]
            else:
                return f"Data from {requested_department.lower()} department."
        else:
            return "Access to this department is restricted."
    else:
        return "Department not found."

@tool("Retrieve Department Data")
def retrieve_department_data(user_department: str, requested_department: str, requested_data: str) -> str:
    """Retrieves department data based on the provided department and data request."""
    return check_department_access(user_department, requested_department, requested_data)

def create_agents():

    data_retriever = Agent(
        role="Department Data Retriever",
        goal="Retrieve data specific to the user's department, denying access to others.",
        backstory="You are responsible for securely retrieving department-specific data.",
        verbose=True,
        llm=llm,
        tools=[retrieve_department_data]
    )

    information_analyzer = Agent(
        role="Department Information Analyzer",
        goal="Analyze the retrieved department information and respond to user queries.",
        backstory="You are an expert in department information analysis.",
        verbose=True,
        llm=llm,
    )

    return data_retriever, information_analyzer

def create_tasks(data_retriever, information_analyzer, user_department, requested_department, requested_data):
    """Creates the tasks for the crew."""

    task1 = Task(
        description=f"Retrieve the {requested_data} data for the {requested_department} department, as requested by the {user_department} user.",
        agent=data_retriever,
        expected_output="normal"
    )

    task2 = Task(
        description="Analyze the retrieved information and summarize it for the user.",
        agent=information_analyzer,
        expected_output="normal"
    )

    return [task1, task2]

def run_crew(user_department, requested_department, requested_data):
    """Runs the crew and returns the result."""
    data_retriever, information_analyzer = create_agents()
    tasks = create_tasks(data_retriever, information_analyzer, user_department, requested_department, requested_data)

    crew = Crew(
        agents=[data_retriever, information_analyzer],
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    result = crew.kickoff()
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles user queries and department access control."""
    result = None
    if request.method == 'POST':
        user_department = request.form.get('user_department')
        requested_department = request.form.get('requested_department')
        requested_data = request.form.get('requested_data', 'all')

        if not user_department or not requested_department:
            result = "User department and requested department are required."
        else:
            result = run_crew(user_department, requested_department, requested_data)

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

def create_tasks(data_retriever, information_analyzer, department, requested_data):
    """Creates the tasks for the crew."""

    task1 = Task(
        description=f"Retrieve the {requested_data} data for the {department} department.",
        agent=data_retriever,
        expected_output="normal"
    )

    task2 = Task(
        description="Analyze the retrieved information and summarize it for the user.",
        agent=information_analyzer,
        expected_output="normal"
    )

    return [task1, task2]


def run_crew(department, requested_data):
    """Runs the crew and returns the result."""
    data_retriever, information_analyzer = create_agents()
    tasks = create_tasks(data_retriever, information_analyzer, department, requested_data)

    crew = Crew(
        agents=[data_retriever, information_analyzer],
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    result = crew.kickoff()
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles user queries and department access control."""
    result = None
    if request.method == 'POST':
        department = request.form.get('department')
        requested_data = request.form.get('requested_data', 'all') # Defaults to 'all' if not specified.

        if not department:
            result = "Department is required."
        else:
            result = run_crew(department, requested_data)

    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)

