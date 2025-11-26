import os
import csv
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from slack_sdk import WebClient


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

NEWS_POTATO_CHANNEL = "C09V873SXG9"
FREE_POTATO_CHANNEL = "C09V0J81W1L"

KEYWORD_RESPONSES = {}
with open("responses.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        KEYWORD_RESPONSES[row["keyword"]] = row["response"]

keywords = list(KEYWORD_RESPONSES.keys())

pattern = "|".join(re.escape(k) for k in keywords)


@app.message(re.compile(pattern))
def reply_message(message, say):
    user = message["user"]
    channel = message["channel"]
    text = message["text"]

    if channel == NEWS_POTATO_CHANNEL:
        say(f"나는 `#소식감자`에서 부를 수 없어. 다른 곳에서 나를 불러줘 :히히감자:")
    else:
        for keyword, response in KEYWORD_RESPONSES.items():
            if keyword in text:
                say(response.format(user=user))
                break


@app.event("member_joined_channel")
def handle_channel_bot_greeting(event, say):
    user = event["user"]
    channel = event["channel"]

    if channel != NEWS_POTATO_CHANNEL:
        return

    text = f"안녕, <@{user}>! 나는 소식해서 시무룩한 찜감자봇이라고 해 :찜감자:"
    say(channel=channel, text=text)


@app.event("emoji_changed")
def handle_emoji_changed_command(event, client: WebClient):
    subtype = event.get("subtype")

    if subtype == "add":
        emoji_name = event.get("name")
        emoji_url = event.get("value")

        text = f"감자농장에 `{emoji_name}`가 이사왔습니다."

        client.chat_postMessage(
            channel=NEWS_POTATO_CHANNEL,
            text=text,
            blocks=[
                {"type": "image", "image_url": emoji_url, "alt_text": emoji_name},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text},
                },
            ],
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
