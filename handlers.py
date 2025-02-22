from telegram import Update
from telegram.ext import ContextTypes
from config import logger
from genai_client import generate_content
from utils import structure_message
from weather import get_weather

from PIL import Image
import pytesseract
import requests
from io import BytesIO

import cv2
import numpy as np



# Initialize chat histories with a limit to prevent memory bloat
CHAT_HISTORY_LIMIT = 10
chat_histories = {}

ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

def initialize_chat_history(user_id: int):
    """Initialize or reset chat history for a user."""
    chat_histories[user_id] = [
        structure_message(ROLE_SYSTEM, "You are QueryGenie, a Telegram bot integrated with the Gemini API to assist users on Telegram (developed by Vineet Kumar)."),
        structure_message(ROLE_SYSTEM, "I'm QueryGenie, ready to assist! Ask me anything."),
    ]

def trim_chat_history(user_id: int):
    """Ensure chat history does not exceed the limit."""
    if len(chat_histories[user_id]) > CHAT_HISTORY_LIMIT:
        chat_histories[user_id] = chat_histories[user_id][-CHAT_HISTORY_LIMIT:]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user_id = update.effective_user.id
    initialize_chat_history(user_id)

    welcome_message = "Hello! I'm QueryGenie. How can I assist you today?"
    await update.message.reply_text(welcome_message)
    logger.info(f"Initialized chat history for user ({user_id})")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /weather command."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Please provide a city name. Usage: /weather <city>")
        return
    
    city = ' '.join(context.args)
    
    try:
        weather_info = get_weather(city)
        logger.info(f"User ({user_id}) requested weather for {city}")
        await update.message.reply_text(weather_info)
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {str(e)}")
        await update.message.reply_text("Sorry, I couldn't fetch the weather. Please try again later.")






from telegram import Update
from telegram.ext import ContextTypes
from config import GEMINI_API_KEY
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO
import base64

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image input, sends it to Gemini AI for analysis, and returns a response."""
    
    photo = update.message.photo[-1]  # Get the highest resolution image
    photo_file = await photo.get_file()
    photo_bytes = requests.get(photo_file.file_path).content

    # Convert image to base64
    image_base64 = base64.b64encode(photo_bytes).decode("utf-8")

    # Generate response using Gemini AI
    try:
        model = genai.GenerativeModel("gemini-pro-vision")  # Gemini Vision model
        response = model.generate_content([{"mime_type": "image/jpeg", "data": image_base64}, 
                                           "Analyze the image and provide a detailed description, including objects, text, and context."])
        
        reply_text = response.text if response.text else "I couldn't analyze the image."
    except Exception as e:
        reply_text = f"Error analyzing image: {str(e)}"
    
    await update.message.reply_text(reply_text)




async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the chatbot conversation."""
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if not user_message:
        await update.message.reply_text("I didn't catch that. Please type a valid message.")
        return

    logger.info(f"User ({user_id}): {user_message}")

    # Ensure chat history exists
    if user_id not in chat_histories:
        initialize_chat_history(user_id)

    chat_histories[user_id].append(structure_message(ROLE_USER, user_message))
    trim_chat_history(user_id)  # Maintain history limit

    await update.message.chat.send_action(action="typing")  # Indicate bot is responding

    try:
        full_prompt = "\n".join([msg['content'] for msg in chat_histories[user_id]])
        response_text = generate_content(full_prompt)

        if not response_text:
            response_text = "I'm not sure how to respond. Can you rephrase your question?"

        chat_histories[user_id].append(structure_message(ROLE_ASSISTANT, response_text))
        trim_chat_history(user_id)

        logger.info(f"Bot response: {response_text}")
        await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Error generating response for user ({user_id}): {str(e)}")
        await update.message.reply_text("Oops! Something went wrong. Please try again later.")
