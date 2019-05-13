from scrapy import cmdline

name = 'xh'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())