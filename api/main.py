from fastapi import FastAPI
from model import Request, Response

app = FastAPI()

@app.post('/chat', response_model=Response) 
def bot_respond(request: Request): 
    user_msg = request.message # needed?
    bot_reply = 'Hi there!' 
    return Response(reply=bot_reply)