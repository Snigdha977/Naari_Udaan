from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import pipeline
from api.auth import auth_bp, User
from config import app, db
import re
import os

# Configure static file serving
app.static_folder = os.path.abspath(os.path.dirname(__file__))
app.static_url_path = ''

# Initialize AI pipeline with smaller model for efficiency
qa_pipeline = pipeline('text-generation', model='gpt2')

# Function to clean repetitive responses
def remove_repetitions(text):
    return re.sub(r'(.)1{2,}', r'\1', text)

CORS(app)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/api')

# Create database tables
with app.app_context():
    db.create_all()

# Load AI model (FLAN-T5)
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

# To store previous questions and responses
previous_conversations = []

# Simple route for testing
@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/<path:path>')
def serve_file(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'home.html')

# Function to remove repetitive answers
def remove_repetitions(response_text):
    # Split the response into sentences
    response_sentences = response_text.split(". ")
    
    # Remove duplicate sentences by converting the list to a set and back to a list
    unique_sentences = list(set(response_sentences))
    
    # Join the unique sentences back into a string
    return ". ".join(unique_sentences)

# AI Copilot endpoint
@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    language = data.get("language", "English")
    
    # Add instruction to the question for structured response
    question = "Provide detailed and unique steps for the following: " + question

    try:
        # Get response from the AI model
        result = qa_pipeline(question, max_length=200)
        response_text = result[0]['generated_text']
        
        # Remove repetitive responses
        cleaned_response = remove_repetitions(response_text)
        
        # Save the new question and response to the conversation history
        previous_conversations.append({'question': question, 'response': cleaned_response})
        
    except Exception as e:
        print("AI Error:", e)
        fallback = {
            "Hindi": "माफ कीजिए, मैं उसे समझ नहीं पाया।",
            "Bengali": "দুঃখিত, আমি বুঝতে পারিনি।",
            "Marathi": "माफ करा, मला समजले नाही।"
        }
        cleaned_response = fallback.get(language, "Sorry, I couldn't understand that.")

    return jsonify({"answer": cleaned_response})

if __name__ == "__main__":
    app.run(debug=True)
