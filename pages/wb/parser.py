from cmath import log
import logging
import collections
import csv

from urllib.parse import ParseResult
import bs4
import requests
import lxml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParsResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
)

class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'accept-language': 'ru',
        }
        self.result = []

    def load_page(self):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/rubashki'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text
    
    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product-card.j-card-item.j-good-for-listing-event')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        logger.info(block)
        logger.info('-' * 100)

        url_block = block.select('a.product-card__main j-card-link')
        if not url_block:
            logger.error('no url_block')
            return 

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return
        
        name_block = block.select_one('dev.product-card__brand-name')
        if not name_block:
            logger.error(f'no name_block on {url}')
            return

        brand_name = block.select_one('strong.brand_name')
        if not brand_name:
            logger.error(f'no brand_name {url}')
            return

        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = block.select_one('span.goods-name')
        if not goods_name:
            logger.error(f'no goods_name on {url}')
            return
        
        goods_name = goods_name.text.strip()

         

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        logger.debug('%s, %s, %s',url, brand_name, goods_name) 
        logger.debug('='* 100)  

    def seve_result(self):
        path = '/Users/admin/auto_test/pages/wb/test.csv'
        with open(path, 'w') as f:
           writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
           writer.writerow(HEADERS)
           for item in self.result:
               writer.writerow(item)


    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')
        self.seve_result()
    
if __name__=='__main__':
    parser = Client()
    parser.run()
