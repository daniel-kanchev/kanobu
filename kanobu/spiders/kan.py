import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from kanobu.items import Article
from datetime import datetime
import time


class KanSpider(scrapy.Spider):
    name = 'kan'
    allowed_domains = ['kanobu.ru']
    start_urls = ['http://kanobu.ru/']

    def parse(self, response):
        links = response.xpath("//a[@class='d-b t-t-u f-w-b']/@href").getall()
        yield from response.follow_all(links, self.parse_category)

    def parse_category(self, response):
        articles = response.xpath("//a[@class='aV_hm']/@href").getall()
        yield from response.follow_all(articles, self.parse_article, cb_kwargs=dict(category=response.url))

    def parse_article(self, response, category):
        item = ItemLoader(Article(), response)
        item.default_output_processor = TakeFirst()

        category = category.split('/')
        category = category[-2].capitalize()
        tags = response.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' aL_em a_hT ')]/a/text()").getall()
        if not tags:
            tags = response.xpath("//div[@class='aL_em a_hT a_hU']/a/text()").getall()

        for i, tag in enumerate(tags):
            if i != 0:
                tags[i] = tag[2:]

        tags = ", ".join(tags)
        title = response.xpath("//h1/text()").get()
        date = response.xpath("//span[@class='bu_gs']//text()").get()
        date = format_date(date)
        author = response.xpath("//div[@class='bn_by']//a//text()").get()
        if not author:
            author = response.xpath("(//div[@class='bu_in']//text())[2]").get()
        content = response.xpath("//div[@class='c-detail_content']//text()").getall()
        content = [text for text in content if not text.strip().startswith(".bg")]
        content = " ".join(content)

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('author', author)
        item.add_value('category', category)
        item.add_value('tags', tags)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()


def format_date(date):
    if date.lower() == 'вчера':
        date = datetime.fromtimestamp(time.time() - 86400).strftime('%Y/%m/%d')
        return date

    elif date.lower() == 'сегодня':
        date = datetime.utcnow().strftime('%Y/%m/%d')
        return date

    date_dict = {
        "Января": "January",
        "Февраля": "February",
        "Март": "March",
        "Апреля": "April",
        "Май": "May",
        "Июня": "June",
        "Июля": "July",
        "Август": "August",
        "Сентября": "September",
        "Октября": "October",
        "Ноября": "November",
        "Декабря": "December",
    }

    date = date.split(" ")
    for key in date_dict.keys():
        if date[1].capitalize() == key:
            date[1] = date_dict[key]
    date = " ".join(date)
    date_time_obj = datetime.strptime(date, '%d %B %Y')
    date = date_time_obj.strftime("%Y/%m/%d")
    return date
