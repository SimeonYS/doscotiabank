import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DoscotiabankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class DoscotiabankSpider(scrapy.Spider):
	name = 'doscotiabank'
	start_urls = ['https://do.scotiabank.com/acerca-de-scotiabank/comunicados-de-prensa.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="cmp cmp-text"]//a/@href').getall()
		for link in post_links:
			if not 'pdf' in link:
				yield response.follow(link, self.parse_post)


	def parse_post(self, response):
		date = "Not stated in article"

		try:
			title = response.xpath('//h1/b/text()').get().strip()
		except AttributeError:
			title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('(//div[@class="cmp cmp-text"])[position() >1]//text() | //div[@class="button--bellow-body-content"]//div[@class="row "]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "", ' '.join(content))

		item = ItemLoader(item=DoscotiabankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
