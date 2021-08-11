import requests

class SlackBot:
    token = "none"
    channel = "#test"

    def __init__(self, token):
        self.token = token

    def slack_post_message(self, channel, msg):
        self.channel = channel
        requests.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+self.token},
            data={"channel": self.channel, "text": msg})


if __name__ == "__main__":
    print("SlackBot Test Main")
    sl = SlackBot("xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX")
    sl.slack_post_message('#server', 'test')

