import logging
from pathlib import Path
from gatheringMethods import *

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 ' \
             '(KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
HEADERS = {'User-Agent': USER_AGENT,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
ROOT_PATH = Path(__file__).parent.parent
OUTPUT_PATH = ROOT_PATH.joinpath('output')
OUTPUT_INDEX_PATH = ROOT_PATH.joinpath('outputHtml', 'index.html')
DATABASE_FILE = OUTPUT_PATH.joinpath('db')
INDEX_TEMPLATE_PATH = ROOT_PATH.joinpath('scraper')
LOG_FILE_PATH = ROOT_PATH.joinpath('log.log')
# set initial and max requests timeout
INIT_REQUEST_TIMEOUT = 3
MAX_REQUEST_TIMEOUT = 6
# set threads amount (be careful, too high amount may lead to crush)
THREADS_COUNT = 4
# chunkSize how many elements pick every thread in one loop (MANIPULATE IT FOR BETTER PERFORMANCE)
CHUNK_SIZE = 1

logging.basicConfig(filename=LOG_FILE_PATH,
                    level=logging.INFO,
                    format='%(asctime)s |  %(levelname)s | %(message)s')


