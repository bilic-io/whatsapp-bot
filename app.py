from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests
import json
import datetime
import random
import re
import os
import openai
from dotenv import load_dotenv, find_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(find_dotenv())

# Set up OpenAI API client
openai.api_key = os.getenv('OPENAI')

app = Flask(__name__)

@app.route('/bot', methods=['POST'])
def bot():
    # add webhook logic here and return a response
    incoming_msg = request.values.get('Body', '').lower()

    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    response1 = """
        *Hi! I am the Bilic Bot* 👋
        Ask me anything ?

        to get wallet intel, type score + wallet address
        """

    if incoming_msg:

        # Retrieve user input from request
        user_input = incoming_msg

        try:
            # Use ChatGPT to generate response
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=user_input,
                max_tokens=1024,
                temperature=0.5,
            )
            # Return response as JSON

            data = response["choices"][0]["text"].replace('\n', '')

            result = jsonify(data)
            return jsonify(data)
        except Exception as error:
            # Handle other errors
            return jsonify({'error': str(error)}), 500

    msg.body(result)
    responded = True

    if not responded:
        msg.body(response1)
    return str(resp)

@app.route('/chat', methods=['POST'])
def chat():
    # Retrieve user input from request
    user_input = request.json['user_input']

    # Use ChatGPT to generate response
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=user_input,
        max_tokens=1024,
        temperature=0.5,
    )

    # Return response as JSON
    return jsonify(response)

if __name__ == '__main__':
    app.run()
