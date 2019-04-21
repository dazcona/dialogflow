#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():

    data = request.get_json(silent=True)
    movie = data['queryResult']['parameters']['movie']
    
    print('Getting movie details for {}'.format(movie))
    
    api_key = os.getenv('OMDB_API_KEY')

    movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
    movie_detail = json.loads(movie_detail)
    response =  """
        Title: {0}
        Released: {1}
        Actors: {2}
        Plot: {3}
    """.format(movie_detail['Title'], 
            movie_detail['Released'], 
            movie_detail['Actors'], 
            movie_detail['Plot'])

    reply = {
        "fulfillmentText": response,
    }

    return jsonify(reply)


def detect_intent_texts(project_id, session_id, text, language_code):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        # Text Input
        text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
        # Query
        query_input = dialogflow.types.QueryInput(text=text_input)
        # Response
        response = session_client.detect_intent(session=session, query_input=query_input)

        return response.query_result.fulfillment_text


@app.route('/send_message', methods=['POST'])
def send_message():

    message = request.form['message']
    print('Sending message: {}'.format(message))

    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')

    print('Response: {}'.format(fulfillment_text))
    response_text = { "message":  fulfillment_text }

    return jsonify(response_text)


# run Flask app
if __name__ == "__main__":
    app.run()