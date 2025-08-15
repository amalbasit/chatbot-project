from pydantic import BaseModel

class Request(BaseModel):
    message: str

class Response(BaseModel):
    reply: str