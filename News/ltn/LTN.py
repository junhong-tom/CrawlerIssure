import pandas as pd
import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import timedelta
import re
import json
import time

url = r"https://ec.ltn.com.tw/article/breakingnews/3485576"
url = r"https://ec.ltn.com.tw/article/breakingnews/3485097"

url = r"https://ec.ltn.com.tw/list_ajax/international/2"

BaseUrl = r"https://ec.ltn.com.tw/list_ajax/international"

#<a title="財經首頁" href="https://ec.ltn.com.tw" class="half" target="_self">財經首頁</a>

# title:  財經首頁  href:  https://ec.ltn.com.tw
# title:  財經政策  href:  https://ec.ltn.com.tw/list/strategy       https://ec.ltn.com.tw/list_ajax/international/2
# title:  影音專區  href:  https://ec.ltn.com.tw/video
# title:  國際財經  href:  https://ec.ltn.com.tw/list/international
# title:  證券產業  href:  https://ec.ltn.com.tw/list/securities     https://ec.ltn.com.tw/list_ajax/securities/2
# title:  房產資訊  href:  https://ec.ltn.com.tw/list/estate
# title:  財經週報  href:  https://ec.ltn.com.tw/list/weeklybiz
# title:  基金查詢  href:  https://ec.ltn.com.tw/fund
# title:  投資理財  href:  https://ec.ltn.com.tw/list/investment     https://ec.ltn.com.tw/list_ajax/investment/2
# title:  匯率查詢  href:  https://ec.ltn.com.tw/exchangeRate
# title:  粉絲團  href:  https://www.facebook.com/ec.ltn.tw

CategoryType = {
    u'財經政策':r'https://ec.ltn.com.tw/list_ajax/strategy',
    u'國際財經':r'https://ec.ltn.com.tw/list_ajax/international',
    u'證券產業': r'https://ec.ltn.com.tw/list_ajax/securities',
    u'房產資訊':r'https://ec.ltn.com.tw/list_ajax/estate',
    u'財經週報':r'https://ec.ltn.com.tw/list_ajax/weeklybiz',
    u'投資理財':r'https://ec.ltn.com.tw/list_ajax/investment'
 }

def CreateDataRecod():
    DataFieldsNameList = ['Title','No','Group','Url','Date','Content']
    return pd.DataFrame(columns=DataFieldsNameList)

#  need to fix it
def test():
    Res=CreateDataRecod()
    temp_dict ={}
    for issue, url in CategoryType.items():
        print(issue, ' Start ')
        try:
            CategoryNews = GetMoreNews(url, LoopTimes=5)
            temp_dict.update({issue: CategoryNews})
            Res = Res.append(CategoryNews, ignore_index=True)
        except:
            print(issue ,'Error',url)
            print('STOP Collect News Data')
            break

        print(issue, ' End ')
        time.sleep(5)
    return Res


def GetNewsFromLTN():
    HomeUrl = r"https://ec.ltn.com.tw"
    res = requests.get(HomeUrl)
    if res.status_code == 200:
        content = res.content
        soup = BeautifulSoup(content, "html.parser")
        # 側邊選單:自由財經
        item = soup.findAll("div", class_="channel partner boxTitle boxText")
        Category = item[0].findAll('a')
        for _  in Category:
            print('title: ',_.get('title'))
            print('href: ', _.get('href'))


def GetMoreNews(BaseUrl,LoopTimes=5):
    Res = CreateDataRecod()
    #Today = datetime.datetime.today().date()-timedelta(days=1)
    Today = datetime.datetime.today().date()
    print(Today)
    LoopStatus = True
    init_loop = 0
    while LoopStatus:
        url = '/'.join([BaseUrl,str(init_loop)])
        print(url)
        PageNews = CollectPageNews(BaseUrl, init_loop)
        PageNews['Date'] = pd.to_datetime(PageNews['Date'])

        PageNews['IsToday'] =  PageNews['Date'].dt.date == Today
        if PageNews[PageNews['IsToday']]['IsToday'].count() == 0 :
            LoopStatus = False
            print('NO today Data')
        else:
            PageNews = PageNews.drop('IsToday', 1)
            Res = Res.append(PageNews, ignore_index=True)
            print('Add Data')

        init_loop = init_loop + 1
        if not(init_loop < LoopTimes) :
            LoopStatus = False
            print('Over limit Times')
        time.sleep(5)
    return Res


def CollectPageNews(BaseUrl,page=0):
    '''
    範例:  page_url='https://ec.ltn.com.tw/list_ajax/securities/2'
    :param BaseUrl:  BaseUrl = 'https://ec.ltn.com.tw/list_ajax/securities
    :param page:     page = 2
    :return:
    '''
    page_url = '/'.join([BaseUrl,str(page)])
    print(page_url)
    #res = requests.get(url)
    res = requests.get(page_url)
    temp_dict = []
    DataPageNews = CreateDataRecod()
    if res.status_code == 200:
        json_content = json.loads(res.content)
        #print(json_content)

        for _ in json_content:
            print('---------------------------------')
            #print(type(_))
            if bool(_):

                PageNews = CreateDataRecod()

                PageNews['Title'] = [_['LTNA_Title']]
                PageNews['No'] = [_['LTNA_No']]
                PageNews['Group'] = [_['LTNA_Group']]
                PageNews['Url'] = [_['url']]
                PageNews['Date'] = [_['createTime']]
                # Content = GetHtmlNewsTextOfLTN(_['url'],'\n','All')

                Content = GetHtmlNewsTextOfLTN(_['url'], '\n', 'Text')
                PageNews['Content'] = [Content]

                DataPageNews = DataPageNews.append(PageNews,ignore_index=True)

            #temp_dict.append({'Title':Title,'No':No,'Group':Group,'Url':Text_Url,'Date':Time,'Content':Content})
            time.sleep(5)
            pass
        pass
    else:
        assert not(res.status_code ==403), f'403 Error: {page_url} 禁止訪問 '
        # if res.status_code ==403 :
        #     print('403: 禁止訪問')
        #     raise Exception('403: 禁止訪問')
    return DataPageNews  #json_content









# 自由時報 (step 1)
def GetHtmlNewsTextOfLTN(url,join_token='\n', OutPutType='All'):
    '''
    :param url: 範例: url = 'https://ec.ltn.com.tw/article/breakingnews/3485576'
    :param join_token: 文章端落串接符號。預設 \n
    :param OutPutType: All: 輸出 [標題,內文] 的 List, Text: 數書內文 的字串
    :return:
    '''
    paragraph_list = []
    res = requests.get(url)
    if res.status_code == 200:
        content = res.content
        soup = BeautifulSoup(content, "html.parser")
        # 文章 div
        item = soup.findAll("div", class_="whitecon boxTitle boxText")
        # 內文:item
        # 標題
        title_text = item[0].findAll('h1')
        paragraph_list.append(title_text[0].text)

        # 內文
        item_sub2 = item[0].findAll('div', class_='text')
        item_sub3 = item_sub2[0].findAll('p')
        # 內文段落

        for paragraph in item_sub3:
            if not paragraph.attrs:
                # p tag 有其他的屬性, 要捨棄
                # 內文
                #print(paragraph.contents)
                if len(paragraph.contents) == 1:
                    paragraph_list.append(paragraph.text)
                    pass
                pass
            pass
        pass
    #  paragraph_list[0]: title
    #  paragraph_list[1:-1]: context
    if OutPutType == 'All':
        return  [paragraph_list[0],join_token.join(paragraph_list[1:])]
    elif OutPutType == 'Text':
        return join_token.join(paragraph_list[1:])
