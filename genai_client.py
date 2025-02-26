import google.generativeai as genai
from config import API_KEY
import base64

# Configure the generative model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_content(full_prompt):
    try:
        response = model.generate_content(full_prompt)
        return response.text if hasattr(response, 'text') else "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"There was an error generating the response: {str(e)}"

def analyze_image(photo_bytes, user_prompt=None):
    """Analyzes an image using Gemini AI Vision and returns a meaningful response."""
    image_base64 = base64.b64encode(photo_bytes).decode("utf-8")
    prompt = user_prompt if user_prompt else "Analyze the image and provide a meaningful description."

    try:
        response = model.generate_content([{"mime_type": "image/jpeg", "data": image_base64}, prompt])
        return response.text if response.text else "I couldn't analyze the image properly. Try again with a different image."
    except Exception as e:
        return "There was an issue processing your image. Please try again later."