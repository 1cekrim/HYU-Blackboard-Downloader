import requests
import json

class HYUBlackboard:
    def __init__(self, **kwargs):
        self.BbRouter = kwargs['BbRouter']
        self.url = 'https://learn.hanyang.ac.kr'
        self.api_url = 'https://api.hanyang.ac.kr'
        self.session = requests.Session()

    def get_user_key(self):
        url = self.url + '/ultra/course'
        print(url)
        cookies = {'BbRouter': self.BbRouter}
        rep = self.session.get(url, cookies = cookies, verify=False)
        idx = rep.text.index('"id":') + 6
        self.user_key = ''
        while rep.text[idx] != '"':
            self.user_key += rep.text[idx]
            idx += 1
        print(self.user_key)

    def get_courses(self):
        url = self.url+ f'/learn/api/v1/users/{self.user_key}/memberships?expand=course.effectiveAvailability,course.permissions,courseRole&includeCount=true&limit=10000'
        print(url)
        cookies = {'BbRouter': self.BbRouter}
        rep = self.session.get(url, cookies = cookies, verify=False)
        self.courses = []
        for course in json.loads(rep.text)['results']:
            print(course)
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


blackboard = HYUBlackboard(BbRouter=input())
blackboard.get_user_key()
blackboard.get_courses()
blackboard.print_courses()