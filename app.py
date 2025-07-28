import streamlit as st # This line imports the Streamlit library
import google.generativeai as genai # This imports the Gemini AI library
import redis # This imports the Redis library for memory
import json # This helps us save/load data in a structured way
import os # This helps us get information from your computer's environment

    # --- Configuration ---
    # IMPORTANT: Replace "YOUR_GEMINI_API_KEY" with the actual API key you copied from Google AI Studio.
    # For a quick start, you can paste it directly here. For better security in real projects,
    # you'd set it as an environment variable.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB1jyTSdoz7eDAYDMt4HgZWuEyvi9ottDI")

    # Configure Google Generative AI with your API key
genai.configure(api_key=GEMINI_API_KEY)

    # --- Redis Connection Setup ---
    # This part tries to connect to your Redis "memory box" running in Docker.
    # It connects to localhost:6379 because you mapped the Docker port.
try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping() # This sends a "ping" to Redis to see if it's alive
        st.success("Connected to Redis successfully! Your chatbot will remember conversations.")
except redis.exceptions.ConnectionError as e:
        st.error(f"Could not connect to Redis: {e}. Please ensure your Redis Docker container ('my-redis-server') is running.")
        st.stop() # Stop the Streamlit app if Redis connection fails

    # --- Chat History Management with Redis ---
    # This is the "label" for our chat history in Redis
CHAT_HISTORY_KEY = "gemini_streamlit_chat_history"

def load_chat_history():
        """Loads chat history from Redis (the memory box)."""
        history_json = r.get(CHAT_HISTORY_KEY) # Get the history from Redis
        if history_json:
            return json.loads(history_json) # Convert it from text back to a Python list
        return [] # If no history, return an empty list

def save_chat_history(history):
        """Saves chat history to Redis (the memory box)."""
        r.set(CHAT_HISTORY_KEY, json.dumps(history)) # Convert Python list to text and save to Redis

def clear_chat_history():
        """Clears chat history from Redis and from the current session."""
        r.delete(CHAT_HISTORY_KEY) # Delete the history from Redis
        st.session_state.messages = [] # Also clear the messages currently shown in the app
        st.experimental_rerun() # Reload the app to show the cleared history

    # --- Gemini Model Initialization ---
    # Initialize the Generative Model (the Gemini "brain")
    # 'gemini-pro' is a good general-purpose model for text.
model = genai.GenerativeModel('gemini-pro')

    # --- Streamlit User Interface (UI) Setup ---
    # This sets up how your chatbot app will look in the web browser.
st.set_page_config(page_title="My First Gemini Chatbot", layout="centered")
st.title("🤖 My Awesome Gemini Chatbot!")
st.write("Hello! I'm your personal AI assistant. Ask me anything, and I'll remember our chat!")

    # Initialize chat messages in Streamlit's session state
    # This makes sure messages persist while the app is open.
if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history() # Load history when app starts

    # Display existing chat messages in the UI
for message in st.session_state.messages:
        with st.chat_message(message["role"]): # 'user' or 'model'
            st.markdown(message["text"]) # Display the text

    # Input box for user's message
if prompt := st.chat_input("What's on your mind?"):
        # Add user message to chat history and display it
        st.session_state.messages.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare chat history for Gemini API
        # The Gemini API needs messages in a specific format (alternating user/model turns).
        chat_history_for_gemini = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                chat_history_for_gemini.append({"role": "user", "parts": [msg["text"]]})
            elif msg["role"] == "model":
                chat_history_for_gemini.append({"role": "model", "parts": [msg["text"]]})

        # Start a chat session with the Gemini model using the history
        chat = model.start_chat(history=chat_history_for_gemini)

        # Display the model's response
        with st.chat_message("model"):
            with st.spinner("Thinking..."): # Show a "Thinking..." message while Gemini processes
                try:
                    # Send the user's prompt to Gemini and get a response
                    response = chat.send_message(prompt, stream=True) # stream=True makes it type out character by character
                    response_text = ""
                    for chunk in response:
                        if chunk.text:
                            response_text += chunk.text
                            st.markdown(response_text + "▌") # Show a blinking cursor effect
                    st.markdown(response_text) # Display the final response

                    # Add model's response to chat history
                    st.session_state.messages.append({"role": "model", "text": response_text})

                    # Save the updated chat history to Redis
                    save_chat_history(st.session_state.messages)

                except Exception as e:
                    st.error(f"Oops! Something went wrong: {e}")
                    st.info("Please check your Gemini API key and ensure your Redis Docker container is running.")

    # Button to clear chat history
st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    # A little message in the sidebar
st.sidebar.markdown(
        """
        ---
        This chatbot uses Google's Gemini for conversations and Redis (running in Docker) for memory.
        """
    )
    