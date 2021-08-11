import requests

token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
channel = "#test"
text = "Check your stock crawler."

requests.post("https://slack.com/api/chat.postMessage",
    headers={"Authorization": "Bearer "+token},
    data={"channel": channel,"text": text})
