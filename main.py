import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
gimini_api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=gimini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash-002")

@cl.on_chat_start
async def handle_chat_start():
    # Initialize chat history in the user session
    cl.user_session.set("chat_history", [])
    await cl.Message(content="Welcome to my GPT-2.0. How may I help you?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    prompt = message.content

    # Handle specific questions
    if prompt.lower() in ["who built you?", "who are you?"]:
        await cl.Message(content="I was created by Muhammad Ismail.").send()
        return

    # Retrieve the chat history from the user session
    chat_history = cl.user_session.get("chat_history", [])

    # Append the user's message to the chat history
    chat_history.append({"role": "user", "parts": [prompt]})

    # Format the chat history for the API
    formatted_history = []
    for msg in chat_history:
        formatted_history.append({
            "role": msg["role"],
            "parts": [{"text": part} for part in msg["parts"]]
        })

    # Generate a response using the model with the chat history as context
    response_request = model.generate_content(formatted_history, stream=True)

    # Prepare the response message
    response = cl.Message(content="")

    # Stream the response tokens and append them to the chat history
    response_text = ""
    for chunk in response_request:
        if chunk.text:
            response_text += chunk.text
            await response.stream_token(chunk.text)

    # Append the model's response to the chat history
    chat_history.append({"role": "assistant", "parts": [response_text]})

    # Update the chat history in the user session
    cl.user_session.set("chat_history", chat_history)

    # Send the final response
    await response.send()