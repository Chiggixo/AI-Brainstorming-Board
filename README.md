🚀 AIdea Board: Your AI-Powered Brainstorming Companion
Welcome to AIdea Board, a dynamic and intelligent web application designed to supercharge your brainstorming sessions. Move beyond simple note-taking with a smart Kanban-style board that leverages the power of Google's Gemini AI to provide suggestions, summaries, and thematic clustering of your ideas in real-time.

This full-stack application combines a sleek, drag-and-drop React frontend with a robust Python Flask backend, all connected to a live Firebase database.

✨ Key Features
📝 Real-Time Kanban Board: Organize your ideas with a classic "To Do," "In Progress," and "Done" workflow.

🖱️ Intuitive Drag & Drop: Seamlessly move your ideas between columns to track your progress.

🤖 AI-Powered Suggestions: As you type, our AI Assistant provides creative and relevant ideas to keep your momentum going.

🖼️ Instant Visualization: Generate a dynamic, relevant image for any idea with a single click to make your board more engaging.

📊 Smart Clustering: Automatically group similar ideas together with colored tags, helping you identify key themes at a glance.

✍️ Quick Summaries: Get an AI-generated summary of all the ideas on your board, perfect for reports or reviews.

🔒 Persistent Storage: Your board is automatically saved to a Firebase Firestore database, so you'll never lose your work.

💻 Tech Stack
This project is built with a modern, full-stack architecture:

🚀 Getting Started
Follow these steps to get the AIdea Board running on your local machine.

Prerequisites
Python 3.8+ and Pip

A Google AI API Key

A Firebase project with a serviceAccountKey.json file

1. Backend Setup
# Clone the repository
git clone <your-repository-url>

# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt

# Create a .env file and add your Google AI API key
echo "GOOGLE_API_KEY='your-google-ai-api-key'" > .env

# Make sure your serviceAccountKey.json file is in this directory

# Run the Flask server
python -m flask --app app run

Your backend will now be running at http://127.0.0.1:5000.

2. Frontend Setup
Navigate to the frontend directory.

Open the index.html file in your web browser.

That's it! The application should be fully functional on your local machine.

☁️ Deployment
This application is ready for deployment. For a detailed walkthrough on how to deploy the frontend to Netlify and the backend to Render, please see the Deployment Guide.

📸 Application in Action
Here's a look at the AIdea Board's clean and modern user interface:

The main board view, showing cards organized into columns and the AI Assistant panel.