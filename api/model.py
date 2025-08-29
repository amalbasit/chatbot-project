from pydantic import BaseModel

class UserInput(BaseModel):
    uuid: str
    message: str

class BotReply(BaseModel):
    reply: str

class RagDecision(BaseModel):
    rag_flag: bool
    msg: str