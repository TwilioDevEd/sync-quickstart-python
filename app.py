import os
from flask import Flask, jsonify, request, send_from_directory
from faker import Factory
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import SyncGrant

app = Flask(__name__)
fake = Factory.create()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route('/token')
def token():
    # get credentials for environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY']
    api_secret = os.environ['TWILIO_API_SECRET']
    service_sid = os.environ['TWILIO_SYNC_SERVICE_SID']

    # create a randomly generated username for the client
    identity = fake.user_name()

    # Create access token with credentials
    token = AccessToken(account_sid, api_key, api_secret, identity)

    # Create a Sync grant and add to token
    sync_grant = SyncGrant(service_sid=service_sid)
    token.add_grant(sync_grant)

    # Return token info as JSON
    return jsonify(identity=identity, token=token.to_jwt())

if __name__ == '__main__':
    app.run(port=4567, debug=True, threaded=True)
