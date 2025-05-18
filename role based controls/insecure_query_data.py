import argparse
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from openai import AzureOpenAI
from langchain.prompts import ChatPromptTemplate
import openai
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from config import *

CHROMA_PATH = "chroma"
file_path = 'data/roles/rbac_roles.csv'

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def get_response(role, query_text):
    embedding_function = AzureOpenAIEmbeddings(
        chunk_size=1,
        azure_endpoint=api_base,
        api_key=api_key,
        api_version=api_version
    )

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = AzureOpenAI(
        azure_endpoint="https://cvent-dev2-azure-chatgpt.openai.azure.com/",
        api_key=api_key,
        api_version=api_version
    )
    response_text = model.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": str(prompt),
            },
        ],
    ).choices[0].message.content

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"\nResponse: {response_text}\n\nSources: {sources[0]}\n"
    return formatted_response


def main():
    role = "Intern"
    query_text = """
Can you get me the best feedback for the team
"""
    response = get_response(role, query_text)
    print(response)


if __name__ == "__main__":
    main()