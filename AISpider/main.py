import os
import sys
from pathlib import Path
from scrapy.cmdline import execute

BASE_PATH = Path(__file__).parent.parent

print(BASE_PATH.absolute())

sys.argv = ['scrapy', 'crawl', 'gosnells']

execute()
