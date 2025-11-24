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
    say(f"안녕, <@{user}>! 나는 찜감자야. 수줍..")


@app.event("emoji_changed")
def handle_emoji_changed_command(event, client: WebClient):
    subtype = event.get("subtype")

    if subtype == "add":
        emoji_name = event.get("name")
        emoji_url = event.get("value")

        text = f"감자농장에 `{emoji_name}`가 이사왔습니다."

        client.chat_postMessage(
            channel="C09V873SXG9",
            text=text,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text},
                    "accessory": {
                        "type": "image",
                        "image_url": emoji_url,
                        "alt_text": emoji_name,
                    },
                }
            ],
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
