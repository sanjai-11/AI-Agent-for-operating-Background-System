from flask import Flask, render_template, request, redirect
import google.generativeai as genai
import os
import json
from database import init_db, fetch_records, backend  # Import database functions

# Configure Google Gemini API
os.environ['GOOGLE_API_KEY'] = "AIzaSyBB_ibeXwZTSQKj_XnjMLOvXHt9bW1ygkc"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')

app = Flask(__name__)

# Process Gemini model output
def process_gemini_output(output):
    if isinstance(output, dict):  # Single operation
        backend(output['action'], output['key'], output.get('value'))
    elif isinstance(output, list):  # Multiple operations
        for operation in output:
            backend(operation['action'], operation['key'], operation.get('value'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get natural language prompt from user
        prompt = request.form['prompt']
        
        # Generate structured output from Gemini model
        total_prompt = f"""
        Please extract the action word, key, and value from the following input. Provide the output exactly in the JSON file specified and do not include any additional information.

        Input: {prompt}
        """
        response = model.generate_content(total_prompt)
        
        json_text = response.text  # Replace this with your actual response

        if json_text.startswith("```json"):
            json_text = json_text.lstrip("```json").rstrip("```").strip()

        try:
            json_object = json.loads(json_text)
            '''print("Parsed JSON Object:", json_object)
    print("Action:", json_object.get("action"))
    print("Key:", json_object.get("key"))
    print("Value:", json_object.get("value"))'''
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
            backend(action,key,value)

        return redirect('/')
    
    # Fetch and display records
    records = fetch_records()
    return render_template('index.html', records=records)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)