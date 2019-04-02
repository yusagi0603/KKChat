from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import bot
import config

app = Flask(__name__)

line_bot_api = LineBotApi(config.LINE_SETTING.get('TOKEN')) # TOKEN
handler = WebhookHandler(config.LINE_SETTING.get('SECRET')) # SECRET

line_bot = bot.LineBot()

@app.route("/callback", methods=['POST'])
def callback(): 
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as textb
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    text = line_bot.get_resp(event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()