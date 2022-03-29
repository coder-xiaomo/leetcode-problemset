# coding:utf-8
import re
import json
import os
import threading
import time
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

def get_proble_set(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_proble_set(problemSet):
    # print(len(problemSet)) # 2573
    for i in range(len(problemSet)):
        title = problemSet[i]["stat"]["question__title_slug"]
        if os.path.exists("originData/[no content]{}.json".format(title)) or os.path.exists("originData/{}.json".format(title)):
            print(i, "has been parsed.")
            # print("The question has been parsed: {}".format(title))
            continue
        #construct_url(title)
        # time.sleep(0.5)
        time.sleep(1)
        t =threading.Thread(target=construct_url,args=(title,))
        t.start()
        print(i, "is done.")
        continue

def construct_url(problemTitle):
    url = "https://leetcode-cn.com/problems/"+ problemTitle + "/"
    # print(url)
    get_proble_content(url,problemTitle)

def save_problem(title,content, editorType = ""):
    #content = bytes(content,encoding = 'utf8')
    filename = title + ".html"
    if editorType == "MARKDOWN":
        filename = title + ".md"
    # else if editorType = "CKEDITOR":
    with open(filename,'w+',encoding="utf-8")as f:
        f.write(content)

def get_proble_content(problemUrl,title):
    # 随便请求一个页面，获取csrf_token
    response = requests.get('https://leetcode-cn.com/graphql/', data = '''{"operationName":"userPremiumInfo","variables":{},"query":"query userPremiumInfo {\n  userStatus {\n    isPremium\n    subscriptionPlanType\n    __typename\n  }\n}\n"}''')
    setCookie = response.headers["set-cookie"]
    # print(setCookie)
    '''
    print(setCookie)
    setCookie = json.loads(setCookie)
    print(type(setCookie))
    '''
    try:
        pattern = re.compile(".*?csrftoken=(.*?);.*?",re.S)
        csrftoken = re.search(pattern, setCookie)
        # print(csrftoken.group(1))
        url = "https://leetcode-cn.com/graphql"
        data = {
            "operationName":"questionData",
            "variables":{"titleSlug":title},
            "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    categoryTitle\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    envInfo\n    book {\n      id\n      bookName\n      pressName\n      source\n      shortDescription\n      fullDescription\n      bookImgUrl\n      pressImgUrl\n      productUrl\n      __typename\n    }\n    isSubscribed\n    isDailyQuestion\n    dailyRecordStatus\n    editorType\n    ugcQuestionId\n    style\n    exampleTestcases\n    __typename\n  }\n}\n"
        }
        headers = {
            'x-csrftoken': csrftoken.group(1),
            'referer':problemUrl,
            'content-type':'application/json',
            'origin':'https://leetcode-cn.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        cookies = {
            '__cfduid':'d9ce37537c705e759f6bea15fffc9c58b1525271602',
            '_ga':'GA1.2.5783653.1525271604',
            '_gid':'GA1.2.344320119.1533189808',
            'csrftoken':csrftoken.group(1),
            ' _gat':'1'
        }
        #payload表单为json格式

        dumpJsonData = json.dumps(data)
        response = requests.post(url,data = dumpJsonData, headers = headers,cookies = cookies)
        dictInfo = json.loads(response.text)
        # print(response.text)
        if dictInfo["data"]["question"].get("content") is not None:
            saveJSON(dictInfo, "originData/" + title + ".json")
            # 英文版
            content = dictInfo["data"]["question"]["content"]
            title = dictInfo["data"]["question"]["title"]

            # 中文版
            translatedContent = dictInfo["data"]["question"]["translatedContent"]
            translatedTitle = dictInfo["data"]["question"]["translatedTitle"]
            titleSlug = dictInfo["data"]["question"]["titleSlug"]
            editorType = dictInfo["data"]["question"]["editorType"] # 分为 MARKDOWN 和 CKEDITOR 两种编辑器

            # 中文版
            save_problem("problem (Chinese)/" + translatedTitle + " [{}]".format(titleSlug), translatedContent, editorType)
            # 英文版
            if content != "" and content != "<p>English description is not available for the problem. Please switch to Chinese.</p>":
                save_problem("problem (English)/" + translatedTitle + "(English) [{}]".format(titleSlug), content)
            else:
                pass # 有一些题目没有英文，那么就不保存
        else:
            saveJSON(dictInfo, "originData/[no content]" + title + ".json")
            # print("no content")
    except Exception as e:
        print("[error] ", e, problemUrl)

def saveJSON(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    url = "https://leetcode-cn.com/api/problems/all/"
    html = json.loads(get_proble_set(url))
    saveJSON(html, "origin-data.json")

    # html = json.load(open("origin-data.json", 'r', encoding='utf-8'))

    problemset = html["stat_status_pairs"]
    parse_proble_set(problemset)


if __name__=='__main__':
    folderName = "leetcode-cn"
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    if not os.path.exists(folderName + "/originData"):
        os.mkdir(folderName + "/originData")
    if not os.path.exists(folderName + "/problem (Chinese)"):
        os.mkdir(folderName + "/problem (Chinese)")
    if not os.path.exists(folderName + "/problem (English)"):
        os.mkdir(folderName + "/problem (English)")
    os.chdir(folderName)
    main()