from flask import Flask, request, abort,render_template

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, FollowEvent, JoinEvent,PostbackEvent,
    TextSendMessage, TemplateSendMessage,ImagemapSendMessage,
    BaseSize,URIImagemapAction,ImagemapArea, MessageImagemapAction,
    TextMessage, ImageMessage, ButtonsTemplate,
    PostbackTemplateAction, MessageTemplateAction,PostbackAction,
    URITemplateAction,ImageSendMessage,CarouselTemplate,CarouselColumn,URIAction,
    CameraAction, CameraRollAction,QuickReply, QuickReplyButton,ConfirmTemplate
)

import json

try:
    from urllib.parse import urlparse,parse_qs
except ImportError:
    from urlparse import urlparse,parse_qs

import requests


secretFile=json.load(open("./line_key",'r'))

app = Flask(__name__)

line_bot_api = LineBotApi(secretFile.get("channel_access_token"))

handler = WebhookHandler(secretFile.get("secret_key"))

server_url = secretFile.get("server_url")

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
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
        abort(400)

    return 'OK'

#收到關注動作
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):

    menu_id = secretFile.get("home_page_id")

    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)

    # 將菜單綁定在用戶身上
    # 要到Line官方server進行這像工作，這是官方的指定接口
    linkMenuEndpoint='https://api.line.me/v2/bot/user/%s/richmenu/%s' % (user_profile.user_id, menu_id)
    
    # 官方指定的header
    linkMenuRequestHeader={'Content-Type':'image/jpeg','Authorization':'Bearer %s' % secretFile["channel_access_token"]}
    
    # 傳送post method封包進行綁定菜單到用戶上
    lineLinkMenuResponse=requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader)

    #推送訊息給官方Line
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="哈囉！\n歡迎使用卡片搜尋！" ))

#收到postback動作
@handler.add(PostbackEvent)
def handle_post_message(event):

    #抓取postback action的data
    data = event.postback.data

    #用query string 解析data
    data=parse_qs(data)

    if (data['type']==['example']):

        example_message = "輸入卡片名稱，獲得查詢結果\n以下為範例：\n    幽光"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=example_message))


    elif (data['type']==['author']):
        author_message = "作者：\n   張天陽\n\n電子郵件：\n   stp91002@gmail.com"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=author_message))

"""
清理查詢條件
"""
def get_card_condition(condition_item,condition_text):

    #搜尋條件列表
    condition_dict = {"名稱":"card_name","水晶":"card_mana","效果":"card_text","職業":"card_class","型態":"card_type","攻擊":"card_attack","生命":"card_health","血量":"card_health","系列":"card_series","資料片":"card_series"}

    if condition_item in condition_dict:

        #ex. 從(水晶,20) 轉為 "card_mana-20"
        query_message = "{}-{}".format(condition_dict[condition_item],condition_text)

    else:

        query_message = "error"

    return query_message

"""
根據不同文字訊息做條件處理
"""
def get_card_message(message_text):

    message_text = message_text.replace("\n","")

    find_plus = message_text.find("+") #訊息有無包含+

    find_minus = message_text.find("-") #訊息有無包含-

    """
    分析查詢，根據查詢結果回傳不同訊息
    """

    #若沒有設置條件，則直接查詢名稱
    if find_plus < 0 and find_minus < 0:

        Endpoint='http://pymysql:5000/card/%s' % (message_text)
        Header={'Content-Type':'application/json'}
        Response=requests.get(Endpoint,headers=Header)
        return_cards = Response.json()

        return return_cards

    #若只有一個查詢條件
    elif find_plus < 0 :

        condition_info = message_text.split("-")

        query_message = get_card_condition(condition_info[0],condition_info[1])

        if query_message == "error":

            return_cards = ["error",message_text]

            return return_cards

        else:

            Endpoint='http://pymysql:5000/one_condition/%s' % (query_message)
            Header={'Content-Type':'application/json'}
            Response=requests.get(Endpoint,headers=Header)
            return_cards = Response.json()

            return return_cards

    #有多個條件，但沒有使用-區別
    elif find_minus < 0:
        
        return_cards = ["error",message_text]

        return return_cards

    #多個條件
    else:
        conditions = message_text.split("+")

        condition_num = 0

        for condition in conditions:

            condition_info = condition.split("-")

            query_message = get_card_condition(condition_info[0],condition_info[1])

            if query_message == "error":

                return_cards = ["error",condition]

                return return_cards

            elif condition_num == 0:

                query_text = query_message

            else:

                query_text = "{}&{}".format(query_text,query_message)

            condition_num = condition_num + 1


        Endpoint='http://pymysql:5000/multi_conditions/%s' % (query_text)
        Header={'Content-Type':'application/json'}
        Response=requests.get(Endpoint,headers=Header)
        return_cards = Response.json()

        return return_cards

#收到文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #獲得文字訊息內容
    message_text = event.message.text

    return_cards = get_card_message(message_text)

    """
    完成查詢，根據查詢結果回傳不同訊息
    """

    #無符合結果，回傳查詢失敗
    if len(return_cards) == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="查無符合卡片！" ))

    elif return_cards[0] == "error":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="錯誤的查詢條件！-{}".format(return_cards[1]) ))

    #僅一筆結果，回傳圖片與卡片敘述
    elif len(return_cards) == 1:

        return_card = return_cards[0]

        card_image_url = return_card[1]

        card_introduction = "卡片敘述：\n   {}".format(return_card[2])

        line_bot_api.reply_message(event.reply_token,[ImageSendMessage(original_content_url=card_image_url, preview_image_url=card_image_url),TextSendMessage(text=return_card[2] )])

    #多筆結果，回傳所有卡片名稱
    else:
        answer_message = "經過查詢，多筆卡片符合查詢條件。\n以下為查詢結果：\n"

        for return_card in return_cards:
            answer_message = answer_message + "{}{}\n".format("  ",return_card[0])

        answer_message = answer_message + "請擇一再做查詢。"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=answer_message))


if __name__ == '__main__':
    app.run(debug=True,port=80)