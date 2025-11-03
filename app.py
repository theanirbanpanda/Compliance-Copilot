# app.py
import os
import logging
import json # Make sure json is imported
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import the processor and helper function from your existing script
from scraper.process_documents import DocumentProcessor, split_into_chunks

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS

# Create a single, reusable instance of our processor
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.warning("⚠️ GEMINI_API_KEY not found in .env file. AI features will be disabled.")
processor = DocumentProcessor(api_key)

# --- API Endpoints ---

@app.route("/api/analyze", methods=['POST'])
def analyze_text():
    logger.info("Received request for /api/analyze")
    try:
        data = request.get_json()
        text_to_process = data.get('text')
        if not text_to_process:
            return jsonify({"error": "Request must include 'text' field."}), 400
        chunks = split_into_chunks(text_to_process)
        # Use the correct function name
        results = [processor.process_chunk(chunk, i + 1, use_live=True) for i, chunk in enumerate(chunks)]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in /api/analyze: {e}", exc_info=True) # Log traceback
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/api/ask", methods=['POST'])
def ask_question():
    """Endpoint to handle follow-up questions using RAG."""
    print("--- /api/ask START ---") # DEBUG 1
    logger.info("Received request for /api/ask")
    try:
        data = request.get_json()
        question = data.get('question')
        context = data.get('context') # The original text chunk
        
        print(f"Received Question: {question}") # DEBUG 2
        print(f"Received Context Snippet: {context[:100]}...") # DEBUG 3

        if not question or not context:
            print("Missing question or context.") # DEBUG 4
            return jsonify({"error": "Request must include 'question' and 'context' fields."}), 400

        # Create a specific RAG prompt for the AI
        rag_prompt = f"""
        You are a compliance assistant. Your task is to answer the user's question based *only* on the provided document context.
        If the answer is not in the context, say "I cannot answer that based on the provided text."

        ---
        DOCUMENT CONTEXT:
        {context}
        ---
        USER'S QUESTION:
        {question}
        ---
        ANSWER:
        """
        print("Constructed RAG prompt.") # DEBUG 5
        
        # Use the Gemini model from our processor
        if processor.gemini_available and processor.model:
            print("Attempting to call Gemini API...") # DEBUG 6
            response = processor.model.generate_content(rag_prompt)
            print("Gemini API call successful.") # DEBUG 7
            answer_text = response.text
            return jsonify({"answer": answer_text})
        else:
            print("Gemini is not available.") # DEBUG 8
            return jsonify({"answer": "The AI is not available to answer questions."})

    except Exception as e:
        print(f"--- ERROR IN /api/ask ---: {e}") # DEBUG 9
        logger.error(f"Error in /api/ask: {e}", exc_info=True) # Log traceback
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        print("--- /api/ask END ---") # DEBUG 10


# --- Main Execution ---
if __name__ == "__main__":
    # Use host='0.0.0.0' to make it accessible on your network if needed, but 127.0.0.1 is fine for local testing.
    app.run(port=5000, debug=True) # debug=True helps with auto-reloading and error details