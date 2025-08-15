from fastapi import FastAPI
from model import Request, Response

app = FastAPI()

@app.post('/chat', response_model=Response) 
def bot_response(request: Request): 
    user_msg = request.message.lower()

    if "hello" in user_msg:
        bot_reply = "Hey there! How can I help?"
    elif "weather" in user_msg:
        bot_reply = "It’s sunny outside!"
    else:
        bot_reply = "I’m not sure about that yet."

    return Response(reply=bot_reply)