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


def create_agents():
    summarizer = Agent(
        role="Meeting Summarizer",
        goal="""
        Analyze the provided meeting transcript and extract important, actionable tasks or issues. 
        The goal is to break down the meeting content into well-structured, detailed issues that can be easily understood.
        """,
        backstory="""
        You are an expert in analyzing meeting transcripts and summarizing the discussions into actionable tasks. 
        Your ability to identify important issues helps ensure teams can follow up and address key points effectively.
        """,
        verbose=False,
        llm=llm,
    )

    action_item_extractor = Agent(
        role="Action Item Extractor",
        goal="Extract action items and tasks from meeting transcripts.",
        backstory="You are skilled at identifying tasks and responsibilities discussed in meetings.",
        verbose=False,
        llm=llm,
    )

    return summarizer, action_item_extractor


def create_tasks(summarizer, action_item_extractor, transcript):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(transcript)

    summarization_tasks = []
    for chunk in chunks:
        summarization_tasks.append(Task(
            description=f"Summarize the following section of the meeting transcript: '{chunk}'",
            agent=summarizer,
            expected_output="normal"
        ))

    action_item_task = Task(
        description="""
                Analyze the provided meeting transcript and generate a set of detailed, well-organized issues based on the discussion.
                Focus on breaking down the transcript into manageable tasks or issues, making sure to document each task thoroughly with relevant details.
                """,
        agent=action_item_extractor,
        expected_output="""
                A list of discussion points with titles, key discuss points and future actions.
                For task successfully completed the action should be none.
            """
    )

    return summarization_tasks, action_item_task


def run_meeting_crew(transcript):
    summarizer, action_item_extractor = create_agents()
    summarization_tasks, action_item_task = create_tasks(summarizer, action_item_extractor, transcript)

    crew = Crew(
        agents=[summarizer, action_item_extractor],
        tasks=summarization_tasks + [action_item_task],
        verbose=False,
        process=Process.sequential
    )
    result = crew.kickoff()
    return result


with open("notes", "r") as file:
    transcript = file.read()
    result = run_meeting_crew(transcript)
    print(f"Meeting Summarization and Action Items:\n{result}")
