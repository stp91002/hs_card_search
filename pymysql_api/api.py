# -*- coding: UTF-8 -*-

# 製作flask環境
from flask import Flask, request, jsonify
import pymysql

# 呼叫出Flask
app = Flask(__name__)

# 建立與mysql的連線
conn = pymysql.connect(host='172.31.18.146', port=3306, user='root', passwd='1234', db='search_card', charset='utf8')

# 方便用來跟mysql互動
cur = conn.cursor()

#查詢卡片
@app.route('/card/<card_name>',methods=['GET'])
def search_card(card_name):
    cur.execute(
        "SELECT card_name,card_image_url,card_introduction FROM search_card.card WHERE card_name LIKE ('%{}%');".format(card_name)
        )

    #將剛剛execute的資料取出來
    cards = cur.fetchall()

    return jsonify(cards)

#職業的條件修正
def get_class_condition(class_name):

    class_dict = {"德魯伊":2,"獵人":3,"法師":4,"聖騎士":5,"牧師":6,"盜賊":7,"薩滿":8,"術士":9,"戰士":10,"中立":12}

    class_number = class_dict[class_name]

    return class_number

#查詢卡片-單一條件
@app.route('/one_condition/<condition>',methods=['GET'])
def search_one_condition_card(condition):


    condition_info = condition.split("-")

    if condition_info[0] == "card_class":

        condition_info[1] = get_class_condition(condition_info[1])

    query_condition = "{} = {}".format(condition_info[0],condition_info[1])

    cur.execute(
        "SELECT card_name,card_image_url,card_introduction FROM search_card.card WHERE {};".format(query_condition)
        )

    #將剛剛execute的資料取出來
    cards = cur.fetchall()

    return jsonify(cards)

#查詢卡片-多個條件
@app.route('/multi_conditions/<conditions>',methods=['GET'])
def search_multi_conditions_card(conditions):

    condition_list = conditions.split("&")

    query_num = 0

    for condition in condition_list:

        condition_info = condition.split("-")

        if condition_info[0] == "card_class":

            condition_info[1] = get_class_condition(condition_info[1])

        query_condition = "{} = {}".format(condition_info[0],condition_info[1])

        if query_num == 0:

            query_conditions = query_condition

        else:

            query_conditions = "{} AND {}".format(query_conditions,query_condition)

        query_num = query_num + 1

    cur.execute(
        "SELECT card_name,card_image_url,card_introduction FROM search_card.card WHERE {};".format(query_conditions)
        )

    #將剛剛execute的資料取出來
    cards = cur.fetchall()

    return jsonify(cards)

if __name__ == '__main__':
    # 運行flask server，運行在0.0.0.0:5000
    # 要特別注意假如運行在127.0.0.1的話，會變成只有本機連的到，外網無法
    app.run(host='0.0.0.0', port=5000)