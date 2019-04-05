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

Bot = bot.YuBot.activate_bot()

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
    
    if msg != '聽歌': # not relife
        resp = Bot.get_resp(query=msg).get('answer') # (text, similarity) 

    else: # relife
        resp = '"你可以透過輸入以下的關鍵字來讓我推薦你不一樣的歌喔: 「心情」、「現在在做的事」、「國家」、「歌手」、「曲風」、「語言」，或是輸入「來聊天」來告訴我透過你的故事推薦你不同的歌"'
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=resp))


if __name__ == "__main__":
    
    app.run()