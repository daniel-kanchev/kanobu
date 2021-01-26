BOT_NAME = 'kanobu'
SPIDER_MODULES = ['kanobu.spiders']
NEWSPIDER_MODULE = 'kanobu.spiders'
ROBOTSTXT_OBEY = True
LOG_LEVEL = 'WARNING'
ITEM_PIPELINES = {
   'kanobu.pipelines.DatabasePipeline': 300,
}

