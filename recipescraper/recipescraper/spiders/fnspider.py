from scrapy.spider import Spider
from scrapy.selector import Selector
from recipescraper.items import RecipescraperItem
from scrapy.http import Request
import cleanrecipes as cr
import re
import csv
 
global crawledLinks
crawledLinks = []
global linkPattern 
linkPattern = re.compile("^(?:ftp|http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

#running spider for 11 min yields 733KB csv file

#f = open('recipedata.csv','wb')
#f.close

class MySpider(Spider):
    name = "fn"
    allowed_domains = ["www.foodnetwork.com"]
    start_urls = ["http://www.foodnetwork.com/recipes"]
 
    def parse(self, response):    
        links = response.xpath("//a/@href").extract()  
        titlelist = response.xpath('//title/text()').extract()
        #date = response.xpath('//div[@class="tier-3 title"]').extract()
        ings = response.xpath('//div[@class="col6 ingredients"]/ul/li[@itemprop="ingredients"]').extract() 
        chefline = response.xpath('//div[@class="avatar group"]/div[@class="media"]/p[@class="copyright"]/text()').extract()
        
        [title,chef] = cr.cleanTitle(titlelist)
        
        url = cr.cleanLink(str(response))
        cleanedLinks = []
        for link in links:
            cleanedLinks.append(cr.cleanLink(link))
        
        #print 'response:', url
        #print 'title:', title
        
        #if date:
        #    match = re.search(r'\d\d\d\d-\d\d-\d\d',date[0])
        #    if match:
        #        date = match.group()
        #    else: date = None
        #else:
        #    date = None
        #print 'date:', date
        
        #print 'chefline:', chefline
        if chefline and not chef:
            chef = cr.replaceAll(chefline[0], {'Recipe':'','courtesy':'','Courtesy':'','of':''}).strip()
        
        ingredients = cr.cleanIngs(ings)
        #print 'ingredients:', ingredients
        
        if not url in crawledLinks:
            crawledLinks.append(url)
            if ingredients:
                keys = ['title','url','chef','ingredients']
                f = open('recipedata.csv','ab')
                dict_writer = csv.DictWriter(f, keys)
        
                item = RecipescraperItem()
                item["title"] = title
                item["url"] = url
                #item["date"] = date
                item["chef"] = chef
                item["ingredients"] = ingredients
                dict_writer.writerow(item) 
        
            for link in cleanedLinks:
                if not link in crawledLinks and linkPattern.match(link):
                    yield Request(link, self.parse)
        