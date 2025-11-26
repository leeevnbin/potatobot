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

CSV_RESPONSES_FILE = "responses.csv"

KEYWORD_RESPONSES = {}
with open(CSV_RESPONSES_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        KEYWORD_RESPONSES[row["keyword"]] = row["response"]

keywords = list(KEYWORD_RESPONSES.keys())

pattern = "|".join(re.escape(k) for k in keywords)

ADMIN_USER = "U09UNTJQUJX"


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


def load_keywords():
    keywords = []
    with open(CSV_RESPONSES_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keywords.append(row["keyword"])
    return keywords


@app.command("/감자어목록")
def list_keywords(ack, client: WebClient, body):
    ack()

    user_id = body["user_id"]
    keywords = load_keywords()

    dm = client.conversations_open(users=user_id)
    dm_channel = dm["channel"]["id"]

    if not keywords:
        client.chat_postEphemeral(
            channel=dm_channel, user=user_id, text="등록된 감자어가 없습니다."
        )
        return

    keywords_text = "\n".join(f"- {kw}" for kw in keywords)
    client.chat_postEphemeral(
        channel=dm_channel,
        user=user_id,
        text=f"현재 등록된 감자어 목록입니다:\n{keywords_text}",
    )


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


def delete_app_home_messages(client: WebClient, user_id: str):
    result = client.conversations_list(types="im")
    dm_channel_id = None
    for c in result["channels"]:
        if c["user"] == user_id:
            dm_channel_id = c["id"]
            break

    if not dm_channel_id:
        return 0

    history = client.conversations_history(channel=dm_channel_id, limit=200)
    deleted_count = 0
    for msg in history["messages"]:
        if msg.get("bot_id"):
            client.chat_delete(channel=dm_channel_id, ts=msg["ts"])
            deleted_count += 1
    return deleted_count


@app.command("/클린봇")
def delete_app_home(ack, body, client: WebClient):
    ack()
    user_id = body["user_id"]

    if user_id != ADMIN_USER:
        client.chat_postEphemeral(
            channel=user_id,
            user=user_id,
            text="권한이 없습니다. 이 기능은 관리자만 사용할 수 있습니다.",
        )
        return

    deleted_count = delete_app_home_messages(client, user_id)
    client.chat_postMessage(
        channel=user_id,
        text=f"찜감자봇 메시지 {deleted_count}개를 삭제했습니다.",
    )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
