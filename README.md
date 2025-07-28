# Gemini Chatbot with Streamlit and Redis

This project demonstrates how to build a simple, interactive chatbot using Google's Gemini AI, a Streamlit web interface, and Redis for chat history persistence. Redis is run in a Docker container for easy management and isolation.

Features
- Interactive Chat Interface: Built with Streamlit for a user-friendly web experience.

- AI-Powered Responses: Utilizes Google's Gemini API for intelligent conversational replies.

- Persistent Chat History: Stores conversation history in Redis, ensuring messages are remembered even after the application is closed and reopened.

- Dockerized Redis: Redis runs in a Docker container, providing a clean, portable, and easily manageable database solution without direct system installation.

Technologies Used
- Python: The core programming language.

- Streamlit: For building the web application UI.

- Google Gemini API: For AI model integration.

- Redis: For in-memory data storage (chat history).

- Docker: For containerizing the Redis database.
