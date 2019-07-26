import scrapy

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class HeroResponseItem(scrapy.Item):
    name = scrapy.Field()  # Hero name, announcer pack name, etc
    text = scrapy.Field()
    sound_url = scrapy.Field()
    category = scrapy.Field()
    wiki_url = scrapy.Field()


class HeroResponseItemLoader(ItemLoader):
    default_item_class = HeroResponseItem
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    name_in = MapCompose(lambda v: v.replace('/Responses', ''), str.strip)

class Dota2WikiResponsesSpider(scrapy.Spider):
    name = 'dota2-wiki-responses'

    start_urls = ['https://dota2.gamepedia.com/Category:Responses']

    def parse(self, response):
        for link in LinkExtractor(restrict_css='.mw-content-ltr').extract_links(response):
            yield response.follow(link, callback=self.parse_hero_responses)

    def parse_hero_responses(self, response):
        name = response.css('#firstHeading::text').get()

        for sel_audio in response.css('.mw-parser-output audio.ext-audiobutton'):
            loader = HeroResponseItemLoader(selector=sel_audio)
            loader.add_value('name', name)
            loader.add_value('wiki_url', response.url)
            loader.add_xpath('sound_url', 'source/@src')
            loader.add_xpath('text', 'parent::li/text()[last()]')
            loader.add_xpath('category', 'preceding::h2[1]/span/text()')
            yield loader.load_item()
