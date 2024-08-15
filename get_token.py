import os
import webbrowser
import requests
from flask import Flask, request

# Configuration
client_id = 'Your client ID'
client_secret = 'Your client secret'
redirect_uri = 'http://localhost:8080/callback'
scopes = ['chat:read', 'chat:edit']
token_url = 'https://id.twitch.tv/oauth2/token'

# Placeholder for the token file path
# You can update this path as needed
token_file_path = r'your file path\twitch_access_token.txt'

app = Flask(__name__)

@app.route('/')
def home():
    return 'Twitch OAuth Authentication in Progress...'

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        if not code:
            return "Authorization code not found. Please try again.", 400

        token_response = requests.post(token_url, data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        })

        if token_response.status_code == 200:
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            if access_token:
                # Ensure the directory exists before writing the file
                os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
                try:
                    with open(token_file_path, 'w') as token_file:
                        token_file.write(access_token)
                    return 'Access Token obtained successfully! You can close this window.'
                except IOError as e:
                    return f"Failed to write access token to file: {str(e)}", 500
            else:
                return "Failed to obtain access token. Please check the response and try again.", 400
        else:
            return f"Error in response from Twitch: {token_response.text}", token_response.status_code
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    # Check if the token file already exists
    if not os.path.exists(token_file_path):
        auth_url = f"https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={' '.join(scopes)}"
        webbrowser.open(auth_url)
        app.run(port=8080)
    else:
        print(f"Token file already exists at {token_file_path}.")
