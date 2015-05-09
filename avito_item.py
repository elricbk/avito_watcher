import bs4

import utils

AVITO_ROOT = 'http://m.avito.ru'

class AvitoItem(object):
    ''' Wrapper for single item (or article) in the avito response '''
    def __init__(self, item):
        self.item_id = self.__item_id(item)
        self.title = self.__title(item)
        self.price = self.__price(item)
        self.date = self.__date(item)
        self.url = self.__url(item)
        self._content = None

    def get_full_description(self):
        # FIXME(bkuchin): better to clean up this
        if self.url is None:
            return None
        if self._content == None:
            r = utils.retryable_get(AVITO_ROOT + self.url)
            if not r:
                return None
            soup = bs4.BeautifulSoup(r.content)
            description = soup\
                .find('div', class_='description-preview-wrapper')\
                .text\
                .strip()\
                .encode('utf8')
            img_list = [i['src'] for i in soup.select('li.photo-container img')] + \
                    [i['data-img-src'] for i in soup.select('li.photo-container span.img-pseudo')]
            self._content = {
                'desc': description,
                'img_list': img_list
            }
        return self._content

    def __item_id(self, item):
        form = item.find('form')
        if form is not None and 'data-item-id' in form.attrs:
            return form['data-item-id']
        return None

    def __title(self, item):
        header = item.find('span', class_='header-text')
        if header:
            return header.text.strip()
        return None

    def __price(self, item):
        price_list = item.select('div.item-price')
        if len(price_list) > 0:
            return price_list[0].text.strip()
        return None

    def __date(self, item):
        date_list = item.select('div.info-date')
        if len(date_list) > 0:
            return date_list[0].text.strip()
        return None

    def __url(self, item):
        url = item.find('a', class_='item-link')
        return url['href'] if url else None

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return u'ItemWrapper {id=%s, title="%s", price="%s", date="%s", url="%s"}' % (
            self.item_id,
            self.title,
            self.price,
            self.date,
            self.url
        )

