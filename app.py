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

import os
from dotenv import load_dotenv

load_dotenv()

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager 
from time import sleep

# 打刻
def punch(message):  # money_fowardログイン
    # browser = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver') 
    browser = webdriver.Chrome(ChromeDriverManager().install()) 
    url = "https://ssl.jobcan.jp/login/mb-employee-global?redirect_to=%2Fm%2Fwork%2Faccessrecord%3F_m%3Dadit"
    browser.get(url)   # url取得
    print(url)

    company_id = browser.find_element_by_id("client_id")
    company_id.send_keys(os.environ['ACCOUNT_ID']) # 会社id入力
    # company_id.send_keys("seattle") # 会社id入力

    email = browser.find_element_by_id("email") 
    email.send_keys(os.environ['EMAIL'])  # email入力
    # email.send_keys("kentaro.hirano@seattleconsulting.co.jp")  # email入力

    password = browser.find_element_by_id("password")
    password.send_keys(os.environ['PASSWORD'])  # password入力
    # password.send_keys("2gf9qELL")  # password入力

    login_btn = browser.find_element_by_class_name("btn-block")
    login_btn.click()   # ログインボタン押下

    sleep(1)

    stamping_btn = browser.find_element_by_class_name("adit_item")
    stamping_btn.click()

    browser.implicitly_wait(10) # 秒
    targetElement = browser.find_element_by_id("yes")
    targetElement.click():
    
    if message == "出勤":
        return "出勤登録完了しました。\n本日もがんばりましょう！"
    elif message == "退勤":
        return "退勤登録完了しました。\n今日も1日お疲れ様でした！"

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

@app.route("/")
def hello_world():
    return "hello World"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "出勤" or event.message.text == "退勤" or event.message.text == "入り" or event.message.text == "戻り":
        return_message = punch(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            
            TextSendMessage(text=return_message))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="こちらは出退勤を管理するbotです。\n正しい入力をしてください。"))

if __name__ == "__main__":
    port = os.getenv("PORT")
    app.run(host="0.0.0.0", port=port)
