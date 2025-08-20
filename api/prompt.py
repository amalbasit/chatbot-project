from langchain.prompts import PromptTemplate

def build_prompt(template: str) -> PromptTemplate: 
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template
    )
    return prompt