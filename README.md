LLM-Powered Web Automation Tool
This project demonstrates how to use a Large Language Model (LLM) to translate natural language commands into browser automation steps. The tool takes a high-level task, uses the Groq API with Llama 3 to generate a structured automation plan, and then executes that plan using Playwright to control a web browser in real-time.


**terminal commands**
-python3 -m venv venv
-source venv/bin/activate
-pip install -r requirements.txt
-playwright install

Create a free account at GroqCloud and generate an API key.
Create a file named .env in the root of your project folder.
Add your API key to the .env file

-python main.py

**Technologies Used**
Python: Core programming language.
Playwright: For robust browser automation and control.
Groq API: Provides fast, free access to powerful LLMs (Llama 3).
python-dotenv: For managing environment variables securely.
