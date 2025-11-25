import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from slack_sdk import WebClient


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("감자야")
def say_hello(message, say):
    user = message["user"]
    channel = message["channel"]

    if channel != "C09V873SXG9":
        return None

    say(f"안녕, <@{user}>! 나는 찜감자야. 수줍..")


@app.event("member_joined_channel")
def handle_channel_bot_greeting(event, say):
    user = event["user"]
    channel = event["channel"]

    if channel != "C09V0J81W1L":
        return None

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
            channel="C09V0J81W1L",
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
