import os
import requests
from flask import Flask, request
from google.cloud import pubsub_v1

project_id = os.environ.get('PROJECT_ID')
subscription_name = os.environ.get('SUBSCRIPTION_NAME')
webhook_url = os.environ.get('WEBHOOK_URL')

app = Flask(__name__)
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

def callback(message):
    print(f"Received message: {message.data}")
    requests.post(webhook_url, data=message.data)
    message.ack()

@app.route('/hook', methods=['POST'])
def handle_message():
    """Handle incoming HTTP POST request."""
    message_data = request.get_data()
    requests.post(webhook_url, data=message_data)
    return '', 204

if __name__ == '__main__':
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...\n")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
