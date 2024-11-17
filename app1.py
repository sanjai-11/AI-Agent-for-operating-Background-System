from flask import Flask, render_template, request, redirect
import google.generativeai as genai
import os
import json
from database import init_db, fetch_records, backend  # Import database functions

app1 = Flask(__name__)

class BackendAgent:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')
    
    def process_gemini_output(self, output):
        if isinstance(output, dict):  # Single operation
            action = output.get('action')
            key = output.get('key')
            value = output.get('value')
            backend(action, key, value)
            print(output)
            print(action, key, value)
        elif isinstance(output, list):  # Multiple operations
            print(output)
            for operation in output:
                backend(operation['action'], operation['key'], operation.get('value'))

    @staticmethod
    @app1.route('/', methods=['GET', 'POST'])
    def index():
        agent = BackendAgent()  # Create an instance of BackendAgent
        if request.method == 'POST':
            # Get natural language prompt from user
            prompt = request.form['prompt']
    
            # Generate structured output from Gemini model
            total_prompt = f"""
            Please extract the action word, key, and value from the following input. Provide the output exactly in the JSON file specified and do not include any additional information.
    
            Input: {prompt}
            """
            response = agent.model.generate_content(total_prompt)
    
            json_text = response.text  # Replace this with your actual response
    
            if json_text.startswith("```json"):
                json_text = json_text.lstrip("```json").rstrip("```").strip()
    
            try:
                json_object = json.loads(json_text)
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                print("Invalid JSON:", json_text)
    
            print(json_object)
        
            if type(json_object) == list:
                def process_operations(operations):
                    for operation in operations:
                        action = operation.get("action")
                        key = operation.get("key")
                        value = operation.get("value")
                        backend(action.lower(), key, value)
                process_operations(json_object)
            else:
                action = json_object.get("action")
                key = json_object.get("key")
                value = json_object.get("value")
                backend(action, key, value)
    
            return redirect('/')
    
        # Fetch and display records
        records = fetch_records()
        return render_template('home.html', records=records)

if __name__ == '__main__':
    init_db()
    app1.run(debug=True)
