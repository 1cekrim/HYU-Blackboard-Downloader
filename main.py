import requests
import json
import os
import sys
import colorama
import urllib3
urllib3.disable_warnings()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

WEB_DRIVER = 'C:\chromedriver.exe'

class HYUBlackboard:
    def __init__(self, **kwargs):
        self.BbRouter = kwargs['BbRouter']
        self.path = kwargs['path']
        self.url = 'https://learn.hanyang.ac.kr'
        self.api_url = 'https://api.hanyang.ac.kr'
        self.session = requests.Session()

    def get_user_key(self):
        url = self.url + '/ultra/course'
        cookies = {'BbRouter': self.BbRouter}
        rep = self.session.get(url, cookies=cookies, verify=False)
        idx = rep.text.index('"id":') + 6
        self.user_key = ''
        while rep.text[idx] != '"' and rep.text[idx] != '?':
            self.user_key += rep.text[idx]
            idx += 1
        print(
            f'{colorama.Fore.GREEN}[+]{colorama.Fore.RESET} user_key: {colorama.Fore.CYAN}{self.user_key}')

    def get_courses(self):
        url = self.url + \
            f'/learn/api/v1/users/{self.user_key}/memberships?expand=course.effectiveAvailability,course.permissions,courseRole&includeCount=true&limit=10000'
        cookies = {'BbRouter': self.BbRouter}
        rep = self.session.get(url, cookies=cookies, verify=False)
        self.courses = []
        for course in json.loads(rep.text)['results']:
            course = course['course']
            dic = {}
            dic['name'] = course['name']
            dic['id'] = course['id']
            dic['courseId'] = course['courseId']
            dic['term'] = course['term']['name'] if 'term' in course else 'None'
            self.courses.append(dic)

    def print_courses(self):
        for course in self.courses:
            print(course, sep=' ')

    def get_contents(self, name, id):
        def get_children(root_id):
            url = self.url + \
                f'/learn/api/v1/courses/{id}/contents/{root_id}/children?@view=Summary&expand=assignedGroups,selfEnrollmentGroups.group,gradebookCategory&limit=10000'
            cookies = {'BbRouter': self.BbRouter}
            rep = self.session.get(url, cookies=cookies, verify=False)
            contents = json.loads(rep.text)['results']
            return contents
        invalid_chars = '\/:*?"<>|'
        name = ''.join(c for c in name if c not in invalid_chars)
        path = os.path.join(self.path, name)
        if not os.path.exists(path):
            os.mkdir(path)
        st = []
        trace = []
        st.append(['ROOT', []])
        cases = ['resource/x-bb-folder', 'resource/x-bb-file',
                 'resource/x-bb-externallink']
        while len(st) != 0:
            item = st.pop()
            parent = item[1]
            for now in get_children(item[0]):
                if 'contentDetail' not in now:
                    print(
                        f'{colorama.Fore.RED}[-] contentDetail does not exist\n{now}')
                    continue
                if 'resource/x-bb-folder' in now['contentDetail']:
                    print(
                        f'{colorama.Fore.GREEN}[+] Check folder: {colorama.Fore.RESET}{now["title"]}')
                    now["title"] = ''.join(
                        c for c in now["title"] if c not in invalid_chars)
                    folders = parent + [now["title"]]
                    st.append([now['id'], folders])

                    target = path
                    for i in folders:
                        target = os.path.join(target, i)
                    if not os.path.exists(target):
                        os.mkdir(target)
                        print(
                            f'{colorama.Fore.GREEN}[+] Mkdir: {colorama.Fore.RESET}{now["title"]}')
                elif 'resource/x-bb-file' in now['contentDetail']:
                    print(
                        f'{colorama.Fore.GREEN}[+] Check file: {colorama.Fore.RESET}{now["title"]}')
                    # file download
                    now["title"] = ''.join(
                        c for c in now["title"] if c not in invalid_chars)
                    print(f'title: {now["title"]}')

                    target = path
                    for i in parent:
                        target = os.path.join(target, i)
                    target = os.path.join(target, now['title'])
                    if os.path.exists(target):
                        print(
                            f'{colorama.Fore.YELLOW}[*] Already exists: {colorama.Fore.RESET}{target}')
                    else:
                        self.download(self.url + now["contentDetail"]["resource/x-bb-file"]
                                      ["file"]["permanentUrl"], target)
                elif 'resource/x-bb-externallink' in now['contentDetail']:
                    print(
                        f'{colorama.Fore.GREEN}[+] Check video: {colorama.Fore.RESET}{now["title"]}')
                    # video download
                    cookies = {'BbRouter': self.BbRouter}
                    rep = self.session.get(
                        now["contentDetail"]["resource/x-bb-externallink"]["url"], cookies=cookies, verify=False)
                    target = '<meta property="og:url" content="https://hycms.hanyang.ac.kr/em/'
                    if target not in rep.text:
                        print(f'{colorama.Fore.RED}[-] Invalid video')
                        continue
                    idx = rep.text.index(target) + len(target)
                    result = ''
                    while rep.text[idx] != '"' and rep.text[idx] != '?':
                        result += rep.text[idx]
                        idx += 1
                    target = path
                    for i in parent:
                        target = os.path.join(target, i)
                    sp = now['title'].split('/')
                    if not len(sp) == 1:
                        filename = sp[:-1]
                    else:
                        filename = now['title']
                    filename = ''.join(c for c in filename if c not in invalid_chars) + '.mp4'
                    target = os.path.join(target, filename)
                    if os.path.exists(target):
                        print(
                            f'{colorama.Fore.YELLOW}[*] Already exists: {colorama.Fore.RESET}{target}')
                    else:
                        self.download(
                            f'https://hycms.hanyang.ac.kr/contents/hanyang101/{result}/contents/media_files/mobile/ssmovie.mp4', target)

                else:
                    print(
                        f'{colorama.Fore.RED}[-] Unknown type resource:\n{now}')

    def download(self, url, path):
        print(
            f'{colorama.Fore.GREEN}[+] Download: {colorama.Fore.RESET}\n{url}\n->\n{path}')
        cookies = {'BbRouter': self.BbRouter}
        with open(path, 'wb') as file:
            rep = self.session.get(url, cookies=cookies,
                                   verify=False, stream=True)
            total = rep.headers.get("content-length")
            if total == None:
                file.write(rep.content)
            else:
                progress = 0
                total = int(total)
                for data in rep.iter_content(chunk_size=4096):
                    progress += len(data)
                    file.write(data)
                    done = int(50 * progress / total)
                    sys.stdout.write(
                        f'\r{colorama.Fore.GREEN}[+] Progress: {colorama.Fore.RESET}[{"=" * done}{" " * (50-done)}] {int(progress / total * 100)}%')
                    sys.stdout.flush()
        print()

def get_BbRouter(id, pw):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--disable-gpu')
    option.add_argument('lang=ko_KR')
    driver = webdriver.Chrome(WEB_DRIVER, chrome_options=option)
    driver.get('https://learn.hanyang.ac.kr/ultra/institution-page')
    driver.implicitly_wait(10)
    driver.find_element_by_id('entry-login-custom').send_keys(Keys.ENTER)
    driver.find_element_by_id('uid').send_keys(id)
    driver.find_element_by_id('upw').send_keys(pw)
    driver.find_element_by_id('login_btn').click()
    driver.switch_to.alert.accept()
    for cookie in driver.get_cookies():
        if cookie['name'] == 'BbRouter':
            return cookie['value']
    print(f'{colorama.Fore.RED}[-] login failed')
    assert(False)

def main():
    workspace = os.path.join(os.getcwd(), 'Blackboard')
    if not os.path.exists(workspace):
        os.mkdir(workspace)

    colorama.init(autoreset=True)

    print(f'{colorama.Fore.LIGHTBLACK_EX}Blackboard Downloader')
    id = input('ID: ')
    pw = input('PASSWORD: ')

    BbRouter = get_BbRouter(id, pw)

    blackboard = HYUBlackboard(BbRouter=BbRouter, path=workspace)
    blackboard.get_user_key()
    blackboard.get_courses()

    targets = select_download(blackboard)

    download_courses(blackboard, targets)


def download_courses(blackboard, targets):
    for target in targets:
        print(
            f'{colorama.Fore.GREEN}[+] Download {colorama.Fore.RESET}{target[0]}')
        blackboard.get_contents(*target)
        print(f'{colorama.Fore.GREEN}[+] Success')


def select_download(blackboard):
    courses = {}
    for course in blackboard.courses:
        if not course['term'] in courses:
            courses[course['term']] = []
        courses[course['term']].append({'course': course, 'selected': False})
    courses = sorted(courses.items())
    while True:
        start_code = print_list(courses)
        select = int(input('> '))
        if select <= 0 or select > start_code:
            print(f'{colorama.Fore.RED}[-] Invalid input.')
            input()
            continue
        if select == start_code:
            break
        code = 1
        for lst in courses:
            for course in lst[1]:
                if code == select:
                    course['selected'] = not course['selected']
                code += 1
    targets = []
    for lst in courses:
        for course in lst[1]:
            if course['selected']:
                targets.append(
                    [course['course']['name'], course['course']['id']])
    return targets


def print_list(courses):
    code = 1
    print(f'{colorama.Fore.YELLOW}[*] Please select courses to download')
    for lst in courses:
        print(f"{colorama.Fore.CYAN}[*] {lst[0]}")
        for course in lst[1]:
            if course['selected']:
                print(
                    f'{colorama.Fore.GREEN}[{code:>3}]   {course["course"]["name"]}')
            else:
                print(
                    f'{colorama.Fore.RED}[{code:>3}]   {course["course"]["name"]}')
            code += 1
    print(f'\n{colorama.Fore.YELLOW}[{code:>3}] Start downloading')
    return code


if __name__ == '__main__':
    main()
