# -*- coding: utf-8 -*-
import scrapy
from multiprocessing import Process
from bs4 import BeautifulSoup
import re


class Day027hwSpider(scrapy.Spider):
    name = 'Day027HW'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/Gossiping/M.1557928779.A.0C1.html']
    cookies = {'over18':'1'}
   
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        if response.status != 200:
            print('Error - {} is not available to access'.format(response.url))
            return
        
        soup = BeautifulSoup(response.text)
        
        main_content=soup.find(id='main-content')
        
        metas=main_content.select('div.article-metaline')
        author=''
        title=''
        date=''
        
        if metas:
            if metas[0].select('span.article-meta-value')[0]:
                author=metas[0].select('span-article-meta-value')[0].string
            if metas[1].select('span.article-meta-value')[0]:
                title=metas[1].select('span-article-meta-value')[0].string
            if metas[2].select('span.article-meta-value')[0]:
                date=metas[2].select('span-article-meta-value')[0].string
            
            
         
        # 取得留言區主體
        pushes = main_content.find_all('div', class_='push')
        for p in pushes:
            p.extract()
        
        # 假如文章中有包含「※ 發信站: 批踢踢實業坊(ptt.cc), 來自: xxx.xxx.xxx.xxx」的樣式
        # 透過 regular expression 取得 IP
        # 因為字串中包含特殊符號跟中文, 這邊建議使用 unicode 的型式 u'...'
        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except Exception as e:
            ip = ''
        
        # 移除文章主體中 '※ 發信站:', '◆ From:', 空行及多餘空白 (※ = u'\u203b', ◆ = u'\u25c6')
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        #
        # 透過 .stripped_strings 的方式可以快速移除多餘空白並取出文字, 可參考官方文件 
        #  - https://www.crummy.com/software/BeautifulSoup/bs4/doc/#strings-and-stripped-strings
        filtered = []
        for v in main_content.stripped_strings:
            # 假如字串開頭不是特殊符號或是以 '--' 開頭的, 我們都保留其文字
            if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--']:
                filtered.append(v)

        # 定義一些特殊符號與全形符號的過濾器
        expr = re.compile(u'[^一-龥。；，：“”（）、？《》\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])
        
        # 移除空白字串, 組合過濾後的文字即為文章本文 (content)
        filtered = [i for i in filtered if i]
        content = ' '.join(filtered)
        
        # 處理留言區
        # p 計算推文數量
        # b 計算噓文數量
        # n 計算箭頭數量
        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            # 假如留言段落沒有 push-tag 就跳過
            if not push.find('span', 'push-tag'):
                continue
             
        # 整理文章資訊
        data = Day027Item()
        article_id = str(Path(urlparse(response.url).path).stem)
        data['url'] = response.url
        data['article_id'] = article_id
        data['article_author'] = author
        data['article_title'] = title
        data['article_date'] = date
        data['article_content'] = content
        data['ip'] = ip
        data['messages'] = messages
        yield data

                