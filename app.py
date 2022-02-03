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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
from time import sleep

from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary

# 打刻
def punch(message):  # money_fowardログイン
    browser = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver') 
    url = "https://attendance.moneyforward.com/my_page"
    browser.get(url)   # url取得
    print(url)

    company_id = browser.find_element_by_id("employee_session_form_office_account_name")
    company_id.send_keys(os.environ['ACCOUNT_ID']) # 会社id入力

    email = browser.find_element_by_id("employee_session_form_account_name_or_email") 
    email.send_keys(os.environ['EMAIL'])  # email入力

    password = browser.find_element_by_id("employee_session_form_password")
    password.send_keys(os.environ['PASSWORD'])  # password入力

    login_btn = browser.find_element_by_class_name("attendance-button-email")
    login_btn.click()   # ログインボタン押下
    sleep(1)
    
    attendence_cards = browser.find_elements_by_class_name("attendance-card-time-stamp-button")
    if message == "出勤":
        punch = attendence_cards[0] # 出勤ボタン取得
        punch.click()
        browser.quit()
        return "出勤登録完了しました。\n本日もがんばりましょう！"
    elif message == "退勤":
        punch = attendence_cards[1] # 退勤ボタン取得
        punch.click()
        browser.quit()
        return "退勤登録完了しました。\n今日も1日お疲れ様でした！"
    elif message == "入り":
        punch = attendence_cards[2] # 休憩入りボタン取得
        punch.click()
        browser.quit()
        return "休憩登録完了しました。\nしっかり休みましょう！"
    else:
        punch = attendence_cards[3] # 休憩戻りボタン取得
        punch.click()
        browser.quit()
        return "休憩戻り登録完了しました。\n　またがんばりましょう！"
            
app = Flask(__name__)

# YOUR_CHANNEL_ACCESS_TOKEN = "s3SzJskpRt9Lttutm2FVaTqfMsFxQSWkH50JcvK849reNBp8tcN/486CvhrR7ptNpG0n4AAzLfo7O+WZ2lObUk2Q3uSOeqVo7zQfzEoWgQRWgVKno0ZrGrWjFFZjEEuqtvDs32WAHw9WbjGy5+GHgwdB04t89/1O/w1cDnyilFU="
# YOUR_CHANNEL_SECRET = "acf3987b11018c44b2a1c0f974a0af92"

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
