import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

app = Flask(__name__)
load_dotenv()

def send_slack_notifications(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        raise ValueError(f'Request to Slack failed: {response.status_code}, {response.text}')

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    data = request.json
    print("Received data:", data)
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Handle push event
        commits = data.get('commits', [])
        if commits:
            commit_messages = [commit.get('message', 'No message') for commit in commits]
            username = data.get('pusher', {}).get('name', 'Unknown')
            message = f"New commit(s) by {username}:\n" + '\n'.join(commit_messages)
            send_slack_notifications(message)
    
    elif event_type == 'pull_request':
        # Handle pull request event
        action = data.get('action', 'unknown')
        pr = data.get('pull_request', {})
        pr_title = pr.get('title', 'No title')
        pr_url = pr.get('html_url', 'No URL')
        username = pr.get('user', {}).get('login', 'Unknown')

        message = f"Pull Request {action}:\nTitle: {pr_title}\nURL: {pr_url}\nUser: {username}"
        send_slack_notifications(message)

    return jsonify({'status': 'success'})

if __name__ == "__main__":
    # send_slack_notifications("hi")
    port = int(os.environ.get('PORT', 5000))  # Use the 'PORT' environment variable if set, default to 5000
    app.run(debug=True, port=port)




