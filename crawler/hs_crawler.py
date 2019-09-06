from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re
import json
import pandas as pd

"""
------------------------------
輸入卡片網址與request網址，獲得卡片的dict
------------------------------
"""
def get_cards_json(refer_url,request_url):

	cards_url = Request(request_url)

	cards_url.add_header("referer",refer_url)

	cards_url.add_header("Authorization","Bearer USs6q5AJWPytId5lOKwt4n2963cAJBQI1Y")

	cards_response = urlopen(cards_url)

	cards_bs4_object = BeautifulSoup(cards_response)

	#將bs4物件轉為dict
	cards_dict = json.loads(str(cards_bs4_object))

	return cards_dict

"""
------------------------------
輸入卡片的dict，獲得卡片的list
------------------------------
"""
def get_cards_list(cards_dict,card_series):

	cards_list = cards_dict.get('cards', [])

	cards = []

	for card in cards_list:

		card_info = {}

		#卡片名稱
		card_info["name"] = card["name"]

		#卡片圖片
		card_info["cardImage_url"] = card["image"]

		#法力水晶
		card_info["mana"] = card["manaCost"]

		#效果
		card_info["text"] = card["text"]
		card_info["text"] = card_info["text"].replace("<b>","").replace("</b>","")

		#職業
		card_info["class"] = card["classId"]

		#卡片系列
		card_info["series"] = card_series

		#卡片敘述
		card_info["introduction"] = card["flavorText"]
		card_info["introduction"] = card_info["introduction"].replace("<b>","").replace("</b>","")

		#依照手下與法術區分
		if card["cardTypeId"] == 5:

			card_info["type"] = 0 #類型為法術

		elif card["cardTypeId"] == 4:

			card_info["type"] = 1 #類型為手下
			card_info["health"] = card["health"]#生命值
			card_info["attack"] = card["attack"]#攻擊力

		elif card["cardTypeId"] == 7:

			card_info["type"] = 2 #類型為武器
			card_info["health"] = card["durability"]#耐久度
			card_info["attack"] = card["attack"]#攻擊力

		cards.append(card_info)

	return cards

"""
------------------------------
輸入卡片的list，輸出成 csv
------------------------------
"""
def save_cards_to_csv(cards,cardInfo_column,card_series):

	card_array = []

	#將dict資料轉為一筆csv的資料
	for card in cards:
		card_row = []
		for column in cardInfo_column:

			try:
				card_row.append(card[column])

			except KeyError:
				card_row.append("")

		card_array.append(card_row)

	dataframe = pd.DataFrame(card_array, columns = cardInfo_column)

	csvname = '{}.csv'.format(card_series)

	#輸出成 csv，選擇可與excel 相容的 'utf_8_sig'
	dataframe.to_csv(csvname,index=0, encoding='utf_8_sig')

if __name__ == '__main__':

	cardInfo_column = ["name","cardImage_url","mana","text","class","type","attack","health","series","introduction"]

	#經典系列，由於卡片較多，另外處理
	classic_refer = "https://playhearthstone.com/zh-tw/cards?set=classic"

	classic_url_p1 = "https://api.blizzard.com/hearthstone/cards?set=classic&class=all&sort=manaCost&order=asc&locale=zh_TW"

	classic_url_p2 = "https://api.blizzard.com/hearthstone/cards?set=classic&class=all&sort=manaCost&order=asc&page=2&locale=zh_TW"

	classic_cards_json_p1 = get_cards_json(classic_refer,classic_url_p1)

	classic_cards_p1 = get_cards_list(classic_cards_json_p1,"classic")

	classic_cards_json_p2 = get_cards_json(classic_refer,classic_url_p2)

	classic_cards_p2 = get_cards_list(classic_cards_json_p2,"classic")

	classic_cards = classic_cards_p1 + classic_cards_p2

	save_cards_to_csv(classic_cards,cardInfo_column,"classic")


	#其他系列
	card_series_list = ["basic","naxxramas","goblins-vs-gnomes","blackrock-mountain","the-grand-tournament"]

	for card_series in card_series_list:

		refer_url = "https://playhearthstone.com/zh-tw/cards?set={}".format(card_series)

		request_url = "https://api.blizzard.com/hearthstone/cards?set={}&class=all&sort=manaCost&order=asc&locale=zh_TW".format(card_series)

		cards_json = get_cards_json(refer_url,request_url)

		cards = get_cards_list(cards_json,card_series)

		save_cards_to_csv(cards,cardInfo_column,card_series)