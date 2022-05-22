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
        response = requests.get(url, headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"
        })
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_proble_set(problemSet):
    # print(len(problemSet)) # 2218
    for i in range(len(problemSet)):
    # for i in range(930, len(problemSet)):
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
    url = "https://leetcode.com/problems/"+ problemTitle + "/description/"
    # print(url)
    get_proble_content(url,problemTitle)

def save_problem(title,content):
    #content = bytes(content,encoding = 'utf8')
    filename = title + ".html"
    with open(filename,'w+',encoding="utf-8")as f:
        f.write(content)

def get_proble_content(problemUrl,title):
    response = requests.get(problemUrl, headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    })
    setCookie = response.headers["Set-Cookie"]
    '''
    print(setCookie)
    setCookie = json.loads(setCookie)
    print(type(setCookie))
    '''
    try:
        pattern = re.compile("csrftoken=(.*?);.*?",re.S)
        csrftoken = re.search(pattern, setCookie)
        url = "https://leetcode.com/graphql"
        data = {
            #"operationName":"getQuestionDetail",
            "operationName":"questionData",
            "variables":{"titleSlug":title},
            # "query":"query getQuestionDetail($titleSlug: String!) {\n  isCurrentUserAuthenticated\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    questionTitle\n    translatedTitle\n    questionTitleSlug\n    content\n    translatedContent\n    difficulty\n    stats\n    allowDiscuss\n    contributors\n    similarQuestions\n    mysqlSchemas\n    randomQuestionUrl\n    sessionId\n    categoryTitle\n    submitUrl\n    interpretUrl\n    codeDefinition\n    sampleTestCase\n    enableTestMode\n    metaData\n    enableRunCode\n    enableSubmit\n    judgerAvailable\n    infoVerified\n    envInfo\n    urlManager\n    article\n    questionDetailUrl\n    libraryUrl\n    companyTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    __typename\n  }\n  interviewed {\n    interviewedUrl\n    companies {\n      id\n      name\n      slug\n      __typename\n    }\n    timeOptions {\n      id\n      name\n      __typename\n    }\n    stageOptions {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  subscribeUrl\n  isPremium\n  loginUrl\n}\n"
            "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    exampleTestcases\n    categoryTitle\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      paidOnly\n      hasVideoSolution\n      paidOnlyVideo\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    enableDebugger\n    envInfo\n    libraryUrl\n    adminUrl\n    challengeQuestion {\n      id\n      date\n      incompleteChallengeCount\n      streakCount\n      type\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        headers = {
            'x-csrftoken': csrftoken.group(1),
            'referer':problemUrl,
            'content-type':'application/json',
            'origin':'https://leetcode.com',
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
        if dictInfo["data"]["question"].get("content") is not None:
            saveJSON(dictInfo, "originData/" + title + ".json")
            content = dictInfo["data"]["question"]["content"]
            save_problem("problem/" + title, content)
            # soup = BeautifulSoup(content, 'lxml')
            # save_problem(title,soup.prettify())
        else:
            saveJSON(dictInfo, "originData/[no content]" + title + ".json")
            # print("no content")
    except Exception as e:
        print("[error] ", e, problemUrl)

def saveJSON(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    url = "https://leetcode.com/api/problems/all/"
    html = json.loads(get_proble_set(url))
    saveJSON(html, "origin-data.json")

    # html = json.load(open("origin-data.json", 'r', encoding='utf-8'))

    problemset = html["stat_status_pairs"]
    parse_proble_set(problemset)


if __name__=='__main__':
    folderName = "leetcode"
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    if not os.path.exists(folderName + "/originData"):
        os.mkdir(folderName + "/originData")
    if not os.path.exists(folderName + "/problem"):
        os.mkdir(folderName + "/problem")
    os.chdir(folderName)
    main()