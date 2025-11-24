import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("감자야")
def say_hello(message, say):
    user = message["user"]
    say(f"안녕, <@{user}>! 나는 찜감자야. 수줍..")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
