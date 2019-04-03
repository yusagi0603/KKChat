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
from config import config

app = Flask(__name__)

line_bot_api = LineBotApi(config.LINE_SETTING.get('TOKEN')) # TOKEN
handler = WebhookHandler(config.LINE_SETTING.get('SECRET')) # SECRET


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

    # recevice info from clinet
    user_id = event.source.user_id
    msg =  event.message.text

    # resp based on different scenario
    print('Message: {}'.format(msg))
    Bot = bot.YuBot.activate_bot()
    resp = Bot.get_resp(query=msg).get('answer') # (text, similarity) 

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=resp))


if __name__ == "__main__":
    
    app.run()