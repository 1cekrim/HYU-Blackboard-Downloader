import requests
from bs4 import BeautifulSoup

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
        print(rep.text)
        soup = BeautifulSoup(rep.text)
        lst = soup.findAll("id")
        print(lst)

blackboard = HYUBlackboard(BbRouter='')
blackboard.get_user_key()