from pydantic import BaseModel

class Request(BaseModel):
    uuid: str
    message: str

class Response(BaseModel):
    reply: str