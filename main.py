import os
import ssl
import certifi
import csv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient


ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("감자야")
def say_hello(message, say):
    user = message["user"]
    say(f"안녕, <@{user}>! 나는 찜감자야. 수줍..")


@app.command("/끄적")
def handle_submit_command(ack, body, client):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submit_view",
            "private_metadata": body["channel_id"],
            "title": {"type": "plain_text", "text": "오늘의 감자"},
            "submit": {"type": "plain_text", "text": "감자심기"},
            "close": {"type": "plain_text", "text": "취소"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "goal_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "목표",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": False,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "목표를 입력해주세요.",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "contents_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "내용",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "내용을 입력해주세요.",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "comment_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "응원 한마디",
                    },
                    "optional": True,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "응원 한마디를 자유롭게 남겨주세요.",
                        },
                    },
                },
            ],
        },
    )


@app.view("submit_view")
def handle_view_submission_events(ack, body, client):
    channel_id = body["view"]["private_metadata"]

    if channel_id != "C09RSAVUVEH":
        ack(
            response_action="errors",
            errors={"contents_block_id": "#끄적감자 채널에서만 제출할 수 있습니다"},
        )
        return None

    contents = body["view"]["state"]["values"]["contents_block_id"]["input_action_id"][
        "value"
    ]

    if len(contents) < 3:
        ack(
            response_action="errors",
            errors={"contents_block_id": "내용은 세 글자 이상 입력해주세요."},
        )
        return None

    ack()

    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["real_name"]
    goal = body["view"]["state"]["values"]["goal_block_id"]["input_action_id"]["value"]
    comment = body["view"]["state"]["values"]["comment_block_id"]["input_action_id"][
        "value"
    ]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists("data"):
        os.makedirs("data")

    with open("data/contents.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not os.path.getsize("data/contents.csv") > 0:
            writer.writerow(
                [
                    "user_id",
                    "user_name",
                    "goal",
                    "contents",
                    "comment",
                    "created_at",
                ]
            )

        writer.writerow([user_id, user_name, goal, contents, comment, created_at])

    text = f">>> *<@{user_id}>님의 오늘의 목표*\n\n'{goal}'"

    client.chat_postMessage(channel=channel_id, text=text)


@app.command("/기록보기")
def handle_submission_history_command(ack, body, client: WebClient):
    ack()
    user_id = body["user_id"]

    response = client.conversations_open(users=user_id)
    dm_channel_id = response["channel"]["id"]

    if not os.path.exists("data/contents.csv"):
        client.chat_postMessage(channel=dm_channel_id, text="기록이 없습니다.")
        return None

    submission_list = []

    with open("data/contents.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["user_id"] == user_id:
                submission_list.append(row)

    if not submission_list:
        client.chat_postMessage(channel=dm_channel_id, text="기록이 없습니다.")
        return None

    temp_dir = "data/temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    temp_file_path = f"{temp_dir}/{user_id}.csv"
    with open(temp_file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(submission_list)

    client.files_upload_v2(
        channel=dm_channel_id,
        file=temp_file_path,
        initial_comment=f"<@{user_id}> 님의 기록입니다.",
    )

    os.remove(temp_file_path)


@app.command("/관리자")
def handle_admin_command(ack, body, client: WebClient):
    ack()

    user_id = body["user_id"]
    if user_id != "U09RTKUL7GE":
        client.chat_postEphemeral(
            channel=body["channel_id"],
            user=user_id,
            text="관리자만 사용 가능한 명령어입니다.",
        )
        return None

    client.chat_postEphemeral(
        channel=body["channel_id"],
        user=user_id,
        text="관리자 메뉴를 선택해주세요.",
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "전체 기록 조회",
                            "emoji": True,
                        },
                        "value": "admin_value_1",
                        "action_id": "fetch_all_submissions",
                    }
                ],
            }
        ],
    )


@app.action("fetch_all_submissions")
def handle_some_action(ack, body, client: WebClient):
    ack()
    user_id = body["user"]["id"]
    response = client.conversations_open(users=user_id)
    dm_channel_id = response["channel"]["id"]
    dm_channel_name = body["channel"]["name"]

    file_path = "data/contents.csv"

    if not os.path.exists(file_path):
        client.chat_postMessage(channel=dm_channel_id, text="기록이 없습니다.")
        return None

    client.files_upload_v2(
        channel=dm_channel_id,
        file=file_path,
        initial_comment=f"#{dm_channel_name} 전체 기록입니다.",
    )


@app.event("emoji_changed")
def handle_emoji_changed_command(event, client: WebClient):
    subtype = event.get("subtype")

    if subtype == "add":
        emoji_name = event.get("name")
        emoji_url = event.get("value")

        text = f"감자농장에 {emoji_name}가 이사왔습니다."

        client.chat_postMessage(
            channel="C09U99B3V7D",
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
