import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
import openai
import os
import json
import re

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY") # get the API key from the environment variable

class ProductInput(BaseModel):
    """Inputs for analyse_product"""
    content: str = Field(description="Content for Amazon Aplus Content")

app = FastAPI()

# Define a function to read a prompt from a file
def read_prompt_from_file(filename):
    try:
        # Attempt to open the file and read its content
        with open(filename, 'r') as file:
            content = file.read()
            # Remove special characters
            cleaned_content = re.sub('[^a-zA-Z0-9 \n.]', '', content)
            return cleaned_content
    except FileNotFoundError:
        # Print an error message if the file is not found
        print(f"File {filename} not found.")
        return None

# read the rules from file
rules_content = read_prompt_from_file('rules.txt')

def analyse_product_function(product_input: ProductInput):
    content = product_input.content

    query = f"Please Create Amazon Aplus Content Standard Image Sidebar Module using the following information: {content} "

    system_message = read_prompt_from_file('Aplus.txt')

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": "Here is a product listing:"},
        {"role": "user", "content": content},
        {"role": "user", "content": "Please Create Amazon A+ Content Standard Image Sidebar Module using the following information."}
    ]

    # Log the messages that are being sent
    print("Sending the following messages to OpenAI:")
    for message in messages:
        print(f"Role: {message['role']}, Content: {message['content']}")

    function_descriptions = [
        {
            "name": "Create_Amazon_Aplus_Content",
            "description": "create Amazon Aplus Content Standard Image Sidebar Module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Rules": {
                        "type": "string",
                        "description": "ensure that the following rules are followed for: " + (rules_content if rules_content else "No rules provided.")
                    },  
                    "Headline": {
                        "type": "string",
                        "description": "Create a headline for the module no longer than 160 characters."
                    },                        
                    "subheadline": {
                        "type": "string",
                        "description": "Create a sub-headline for the module no longer than 200 characters."
                    },
                    "body": {
                        "type": "string",
                        "description": "Create a body for the module no longer than 500 characters."
                    },
                    "mainbulletpoints": {
                        "type": "string",
                        "description": "Create 3 bullet points for the module no longer than 60 characters each."
                    },
                    "sidebarheadline": {
                        "type": "string",
                        "description": "Create a sidebar headline for the module no longer than 200 characters."
                    },
                    "sidebarbody": {
                        "type": "string",
                        "description": "Create a sidebar body for the module no longer than 500 characters."
                    },
                    "sidebarbulletpoints": {
                        "type": "string",
                        "description": "Create 3 sidebar bullet points for the module no longer than 60 characters each."
                    }    
                },
                "required": ["Headline", "subheadline", "body", "mainbulletpoints", "sidebarheadline", "sidebarbody", "sidebarbulletpoints"]
            }
        }
    ]
   
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto"
    )

    # Extract the content from the response
    assistant_message = response['choices'][0]['message']
    function_call = assistant_message['function_call']
    arguments_json = function_call['arguments']

    # Convert the JSON string to a Python dictionary
    arguments_dict = json.loads(arguments_json)

    # Extract the individual variables
    headline = arguments_dict['Headline']
    subheadline = arguments_dict['subheadline']
    body = arguments_dict['body']
    mainbulletpoints = arguments_dict['mainbulletpoints']
    sidebarheadline = arguments_dict['sidebarheadline']
    sidebarbody = arguments_dict['sidebarbody']
    sidebarbulletpoints = arguments_dict['sidebarbulletpoints']

    print(f"Headline: {headline}")
    print(f"Subheadline: {subheadline}")
    print(f"Body: {body}")
    print(f"Main Bullet Points: {mainbulletpoints}")
    print(f"Sidebar Headline: {sidebarheadline}")
    print(f"Sidebar Body: {sidebarbody}")
    print(f"Sidebar Bullet Points: {sidebarbulletpoints}")

    return {
        "Headline": headline,
        "Subheadline": subheadline,
        "Body": body,
        "Main Bullet Points": mainbulletpoints,
        "Sidebar Headline": sidebarheadline,
        "Sidebar Body": sidebarbody,
        "Sidebar Bullet Points": sidebarbulletpoints
    }


@app.post("/")
def analyse_product_endpoint(product_input: ProductInput):
    return analyse_product_function(product_input)
