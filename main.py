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
        rep = self.session.get(url, cookies=cookies, verify=False)
        idx = rep.text.index('"id":') + 6
        self.user_key = ''
        while rep.text[idx] != '"':
            self.user_key += rep.text[idx]
            idx += 1
        print(self.user_key)

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

    def get_contents(self, id):
        def get_children(root_id):
            url = self.url + \
                f'/learn/api/v1/courses/{id}/contents/{root_id}/children?@view=Summary&expand=assignedGroups,selfEnrollmentGroups.group,gradebookCategory&limit=10'
            cookies = {'BbRouter': self.BbRouter}
            rep = self.session.get(url, cookies=cookies, verify=False)
            contents = json.loads(rep.text)['results']
            return contents
        st = []
        st.append('ROOT')
        cases = ['resource/x-bb-folder', 'resource/x-bb-file',
                 'resource/x-bb-externallink']
        while len(st) != 0:
            for now in get_children(st.pop()):
                # print(now)
                if 'resource/x-bb-folder' in now['contentDetail']:
                    print(f'folder: {now["title"]}')
                    st.append(now['id'])
                elif 'resource/x-bb-file' in now['contentDetail']:
                    print(
                        f'file: {now["contentDetail"]["resource/x-bb-file"]["file"]["permanentUrl"]}')
                    # file download
                elif 'resource/x-bb-externallink' in now['contentDetail']:
                    print(
                        f'link: {now["contentDetail"]["resource/x-bb-externallink"]["url"]}')
                    # video download
                else:
                    print(f'unknown type resource: {now}')


blackboard = HYUBlackboard(BbRouter=input())
blackboard.get_user_key()
blackboard.get_courses()
blackboard.print_courses()
blackboard.get_contents("_29235_1")
