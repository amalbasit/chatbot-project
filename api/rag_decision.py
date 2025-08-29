from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from constants import RAG_DECISION_PROMPT
from llm import llm
from model import RagDecision

def rag_decision(chat_history, query):

    parser = JsonOutputParser(pydantic_object=RagDecision)

    prompt = PromptTemplate(
        input_variables=['chat_history', 'query'],
        template=RAG_DECISION_PROMPT,
        partial_variables={"format_instructions": parser.get_format_instructions})

    chain = prompt | llm | parser

    return chain.invoke({"chat_history": chat_history, "query": query})