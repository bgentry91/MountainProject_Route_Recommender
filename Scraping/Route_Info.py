######----Scrapy Script to pull route text from mountainproject.com---------------------####
#####-----Could be altered to pull other info, but I preferred using the API for this---###
####------See API_Pull.py for this process---------------------------------------------######

import scrapy
import pandas as pd

class Route_Info(scrapy.Spider):

    name = 'route_info'

    # Be nice to MountainProject, they are a great resource!!!!!
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        "HTTPCACHE_ENABLED": True
    }

    #import URLs
    url_filepath = 'your_url_filepath'
    df = pd.read_csv(url_filepath)
    url_list = df.url.tolist()

    start_urls = url_list

    def parse(self, response):
        # regex is fun, right?
        # use this function to clean some of the non-sense unicode, html tags, etc
        import re
        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        # all routes are 9 digits
        # set everything to zero, because sometimes these sections don't exist
        route = str(response.request.url)[38:47]
        intro = 0
        desc = 0
        prot = 0
        loc = 0
        descent = 0
        esc = 0

        #figure out the number of sections that exist
        #iterate through and put the data where it should go according to the header name
        #often only some headers exist
        header_count = len(response.xpath('//*[@class="m-t-2 max-height max-height-md-800 max-height-xs-600"]/h2/text()').extract())
        for i in range(header_count):
            header = response.xpath('//*[@class="m-t-2 max-height max-height-md-800 max-height-xs-600"]/h2/text()').extract()[i].strip()
            text = response.xpath('//*[@class="m-t-2 max-height max-height-md-800 max-height-xs-600"][' + str(i+1) + ']').extract()[0]
            text = text.split("-->")[1]
            text = text.split('</div>')[0]
            text = cleanhtml(text)
            if header == 'Introduction':
                intro = text
            elif header == 'Description':
                desc = text
            elif header == 'Protection':
                prot = text
            elif header == 'Location':
                loc = text
            elif header == 'Descent':
                descent = text
            elif header == 'Escape':
                esc = text

        #getting the comments as well - going to dump them all into one long string
        comment = ""
        try:
            comment_count = len(response.xpath('//*[@class="comment-body max-height max-height-md-300 max-height-xs-150"]/text()').extract())
            for j in range(comment_count):
                comment += " " + response.xpath('//*[@class="comment-body max-height max-height-md-300 max-height-xs-150"]/text()').extract()[j]
        except:
            comment = ""

        yield {
        	'id': route,
            'Intro': intro,
            'Desc': desc,
            'Prot': prot,
            'Loc': loc,
            'Descent': descent,
            'Escape': esc,
            'Comment': comment
        }        