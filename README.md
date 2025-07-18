# ChatBot
A Python-based chatbot built using natural language processing and machine learning. This project demonstrates how to create a conversational agent that can understand user input, respond intelligently, and be easily extended.

## Files
- **app.py** - Main Python file that runs the chatbot.
- **requirements.txt**: Lists all Python libraries needed to run the project.

## How app.py works
1. Loads an Excel file (.xlsx)
2. Converts it into a pandas DataFrame
3. Accepts natural language questions from the user
4. Sends the data + question to the LLM
5. Returns a relevant answer based on the content of the Excel sheet

## Technologies Used
- **pandas** - To read and process the Excel file
- **openrouter** - The API key is provided by OpenRouter
- **streamlit** - To build a simple UI
- **dotenv** - To store the API key securely
