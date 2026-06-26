# coding:utf-8
import re
import json
import os
import threading
import time
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_proble_set(url):
    try:
        # response = requests.get(url)
        response = requests.get(url, headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }, verify=False)
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
    url = "https://leetcode.cn/problems/" + problemTitle + "/"
    # print(url)
    get_proble_content(url, problemTitle)

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
    response = requests.get('https://leetcode.cn/graphql/', data = '''{"operationName":"userPremiumInfo","variables":{},"query":"query userPremiumInfo {\n  userStatus {\n    isPremium\n    subscriptionPlanType\n    __typename\n  }\n}\n"}''')
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
        url = "https://leetcode.cn/graphql"
        data = {
            "operationName":"questionData",
            "variables":{"titleSlug":title},
            "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    categoryTitle\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    envInfo\n    book {\n      id\n      bookName\n      pressName\n      source\n      shortDescription\n      fullDescription\n      bookImgUrl\n      pressImgUrl\n      productUrl\n      __typename\n    }\n    isSubscribed\n    isDailyQuestion\n    dailyRecordStatus\n    editorType\n    ugcQuestionId\n    style\n    exampleTestcases\n    __typename\n  }\n}\n"
        }
        headers = {
            'x-csrftoken': csrftoken.group(1),
            'referer':problemUrl,
            'content-type':'application/json',
            'origin':'https://leetcode.cn',
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

def get_solutions_only(title_slug):
    """仅获取题解的入口函数"""
    sess = requests.Session()
    resp = sess.get('https://leetcode.cn/graphql/', data='''{"operationName":"userPremiumInfo","variables":{},"query":"query userPremiumInfo {\n  userStatus {\n    isPremium\n    subscriptionPlanType\n    __typename\n  }\n}\n"}''')
    setCookie = resp.headers.get("set-cookie")
    if not setCookie:
        print("  [题解获取失败] {}: 无法获取csrf_token".format(title_slug))
        return
    pattern = re.compile(".*?csrftoken=(.*?);.*?", re.S)
    csrftoken = re.search(pattern, setCookie)
    if csrftoken:
        get_solutions_and_save(title_slug, csrftoken.group(1), sess)
    else:
        print("  [题解获取失败] {}: 无法解析csrf_token".format(title_slug))

def get_solutions_and_save(title_slug, csrftoken, sess=None):
    """获取官方题解完整内容（两步：列表→discussTopic）并保存"""
    url = "https://leetcode.cn/graphql/"

    # ========== Step 1：获取题解列表，找出官方题解 ==========
    list_query = """\n    query questionTopicsList($questionSlug: String!, $skip: Int, $first: Int, $orderBy: SolutionArticleOrderBy, $userInput: String, $tagSlugs: [String!]) {\n  questionSolutionArticles(\n    questionSlug: $questionSlug\n    skip: $skip\n    first: $first\n    orderBy: $orderBy\n    userInput: $userInput\n    tagSlugs: $tagSlugs\n  ) {\n    totalNum\n    edges {\n      node {\n        uuid\n        title\n        slug\n        byLeetcode\n      }\n    }\n  }\n}\n    """

    list_data = {
        "operationName": "questionTopicsList",
        "variables": {
            "questionSlug": title_slug,
            "skip": 0,
            "first": 15,
            "orderBy": "DEFAULT",
            "userInput": "",
            "tagSlugs": []
        },
        "query": list_query
    }

    headers = {
        'x-csrftoken': csrftoken,
        'x-operation-name': 'questionTopicsList',
        'content-type': 'application/json',
        'origin': 'https://leetcode.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
        'referer': 'https://leetcode.cn/problems/{}/solutions/'.format(title_slug),
        'DNT': '1',
    }

    # ========== Step 2：获取题解完整正文 ==========
    discuss_query = """\n    query discussTopic($slug: String) {\n  solutionArticle(slug: $slug, orderBy: DEFAULT) {\n    ...solutionArticle\n    content\n    next {\n      slug\n      title\n    }\n    prev {\n      slug\n      title\n    }\n  }\n}\n    \n    fragment solutionArticle on SolutionArticleNode {\n  ipRegion\n  rewardEnabled\n  canEditReward\n  uuid\n  title\n  content\n  slateValue\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  canSee\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    tagType\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    certificationLevel\n    isDiscussAdmin\n    isDiscussStaff\n    profile {\n      userAvatar\n      userSlug\n      realName\n      reputation\n    }\n  }\n  summary\n  topic {\n    id\n    subscribed\n    commentCount\n    viewCount\n    post {\n      id\n      status\n      voteStatus\n      isOwnPost\n    }\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  favoriteCount\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n  }\n  question {\n    titleSlug\n    questionFrontendId\n  }\n}\n    """

    try:
        # ---------- Step 1 ----------
        if sess:
            resp = sess.post(url, data=json.dumps(list_data), headers=headers)
        else:
            cookies = {'csrftoken': csrftoken}
            resp = requests.post(url, data=json.dumps(list_data), headers=headers, cookies=cookies)

        if resp.status_code != 200:
            print("  [题解列表请求失败] {}: status_code={}".format(title_slug, resp.status_code))
            return

        result = json.loads(resp.text)
        edges = result.get("data", {}).get("questionSolutionArticles", {}).get("edges", [])

        official_solutions = []
        for edge in edges:
            node = edge.get("node", {})
            if node.get("byLeetcode"):
                uuid = node.get("uuid")
                slug = node.get("slug")
                if uuid:
                    official_solutions.append({'uuid': uuid, 'slug': slug})

        if not official_solutions:
            # 写占位文件标记无官方题解，下次跳过请求
            answer_dir = "answer/{}".format(title_slug)
            if not os.path.exists(answer_dir):
                os.makedirs(answer_dir)
            placeholder = "{}/.no_official_solution".format(answer_dir)
            if not os.path.exists(placeholder):
                with open(placeholder, 'w') as f:
                    f.write("No official solution")
            print("  [官方题解] 无官方题解")
            return

        answer_dir = "answer/{}".format(title_slug)
        if not os.path.exists(answer_dir):
            os.makedirs(answer_dir)

        # ---------- Step 2 ----------
        for sol in official_solutions:
            uuid = sol['uuid']
            slug = sol.get('slug')
            if not slug:
                print("  [官方题解] {} 无slug，跳过".format(uuid))
                continue

            discuss_data = {
                "operationName": "discussTopic",
                "variables": {"slug": slug},
                "query": discuss_query
            }

            discuss_headers = headers.copy()
            discuss_headers['x-operation-name'] = 'discussTopic'
            discuss_headers['referer'] = 'https://leetcode.cn/problems/{}/solutions/{}/'.format(title_slug, slug)

            if sess:
                discuss_resp = sess.post(url, data=json.dumps(discuss_data), headers=discuss_headers)
            else:
                discuss_resp = requests.post(url, data=json.dumps(discuss_data), headers=discuss_headers, cookies=cookies)

            if discuss_resp.status_code == 200:
                discuss_result = json.loads(discuss_resp.text)
                saveJSON(discuss_result, "{}/{}.json".format(answer_dir, uuid))
                print("  [官方题解] saved: {}/{}.json".format(answer_dir, uuid))
            else:
                print("  [官方题解完整内容获取失败] {}: status_code={}".format(slug, discuss_resp.status_code))

    except Exception as e:
        print("  [题解请求异常] {}: {}".format(title_slug, e))

def fetch_all_solutions(problemSet):
    """在所有题目获取完成后，依次获取官方题解"""
    total = len(problemSet)
    print("=" * 40)
    print("开始获取全部官方题解，共 {} 道题目".format(total))
    print("=" * 40)
    for i in range(total):
        title = problemSet[i]["stat"]["question__title_slug"]
        # 检查题目是否已获取
        if not os.path.exists("originData/{}.json".format(title)) and not os.path.exists("originData/[no content]{}.json".format(title)):
            print(i, "题目未获取，跳过题解获取.")
            continue
        # 检查题解是否已存在（有 json 文件或 .no_official_solution 占位都跳过）
        answer_dir = "answer/{}".format(title)
        no_solution_placeholder = "{}/.no_official_solution".format(answer_dir)
        if os.path.exists(answer_dir) and (any(f.endswith('.json') for f in os.listdir(answer_dir)) or os.path.exists(no_solution_placeholder)):
            print(i, "题解已存在或已标记无题解，跳过.")
            continue
        time.sleep(1)
        t = threading.Thread(target=get_solutions_only, args=(title,))
        t.start()
        print(i, "题解获取中...")


def main():
    url = "https://leetcode.cn/api/problems/all/"
    jsonContent = get_proble_set(url)
    if jsonContent == None:
        print('列表请求失败！')
        return
    html = json.loads(jsonContent)
    saveJSON(html, "origin-data.json")

    # html = json.load(open("origin-data.json", 'r', encoding='utf-8'))

    problemset = html["stat_status_pairs"]
    parse_proble_set(problemset)

    # 所有题目获取完成后，再依次获取官方题解
    fetch_all_solutions(problemset)


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
    if not os.path.exists(folderName + "/answer"):
        os.mkdir(folderName + "/answer")
    os.chdir(folderName)
    main()
