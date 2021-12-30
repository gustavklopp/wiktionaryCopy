import requests
from bs4 import BeautifulSoup


class Wiktionary(object):
    """Define communication with Wiktionary."""

    def __init__(self, dest_lang, origin_lang):
        self.dest_lang = dest_lang 
        self.origin_lang = origin_lang
        self.url = "https://"+self.dest_lang+".wiktionary.org/wiki/{}?printable=yes"
        self.soup = None

    def word(self, word):
        """Fetch a word from Wiktionary."""

        # Request Wiktionary word page.
        response = requests.get(self.url.format(word))

        # Set a BeautifulSoup instance for that page from the request's encoding.
        encoding = response.encoding if "charset" in response.headers.get("content-type", "").lower() else None
        soup = BeautifulSoup(response.content, "html.parser", from_encoding=encoding)

        # Error page of wiktionary.org
        noarticle = soup.find('div', {'class': 'noarticletext'})
        if noarticle is not None:
            raise Exception(word + " entry does not exist.")

        # Find the language origin section:
        # for ex: <span class="mw-headline" id="Romanian">Romanian</span>
        lang_block = soup.find('span', {'class':'mw-headline', 'id':self.origin_lang})
        if not lang_block:
            raise Exception("Language `" + self.origin_lang + "` does not exist for this `" + word + "` entry.")
        content = ""
        for tag in lang_block.parent.find_next_siblings():
            if tag.name == 'h2': # this is another language
                break
            content += tag.prettify()

            content = content.replace('href="/wiki/', 'href="https://{}.wiktionary.org/wiki/'.format(self.dest_lang))
            content = content.replace('  ', ' ')
            content = content.replace('  ', '')

        return content

