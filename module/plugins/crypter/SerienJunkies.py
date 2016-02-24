import re

from bs4 import BeautifulSoup as Soup
import requests

from module.plugins.captcha.ReCaptcha import ReCaptcha
from module.plugins.internal.Crypter import Crypter


class SerienJunkies(Crypter):
    __name__ = 'SerienJunkies'
    __status__ = 'testing'
    __type__ = 'crypter'
    __pattern__ = r'http://(www\.)?download\.serienjunkies\.org/.*/(?P<ID>.+)\.html'
    __config__ = [
        ("activated", "bool", "Activated", True)
    ]

    # Here goes the websites recaptcha site-key. Should probably be dynamicaly scraped
    # from desired page via a respective pattern.
    # The key must always be an attribute of a special div element on the page, like:
    #
    #       <div class="g-recaptcha" data-sitekey="HERE IS THE SITE-KEY"><div>
    #
    SITE_KEY = '6LdmhRQTAAAAAAGfWQLCeCmT6CAVKKxu-TibpZ2h'

    def setup(self):
        self.urls = []

    def decrypt(self, pyfile):
        protectedPage = Soup(requests.get(pyfile.url).text, 'html5lib')
        s = protectedPage.find('input', {'name': 's'})['value']
        self.captcha = ReCaptcha(pyfile)
        recaptchaVerificationToken = self.captcha.challenge(key=self.SITE_KEY, version=2)
        unlockedPage = requests.post(
            pyfile.url,
            data={
                'g-recaptcha-response': recaptchaVerificationToken,
                's': s,
                'action': 'Download',
                'newcap': 'true'
            }
        )
        unlockedPage = Soup(unlockedPage.text, 'html5lib')

        for form in unlockedPage.findAll('form', {'action': re.compile(r'download.serienjunkies.org')}):
            downloadLink = requests.get(form['action']).url
            self.urls.append(downloadLink)

        self.packages = [(pyfile.package().name, self.urls, pyfile.package().folder)]
