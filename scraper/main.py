import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from functools import partial, reduce
import time
import multiprocessing
from collections import defaultdict
from gatheringMethods import *
from time import localtime, strftime
import jinja2
import ftplib
import random
import config_local as cfg
from config import *
from pathlib import Path

webs = {
    'sobieraj': {'url': 'http://www.sobieraj-nieruchomosci.pl/', 'url_suffix': '', 'func': sobieraj_parse,
                 'pagination': False},
    'florczyk': {'url': 'http://florczyk.nieruchomosci.pl/category/mieszkania/', 'url_suffix': '',
                 'func': florczyk_parse,
                 'pagination': False},
    'abakus': {'url': "http://abakus.konin.pl/mieszkania", 'url_suffix': "", 'func': abakus_parse, 'pagination': False},
    'invicus': {'url': "http://invicus.pl/pl/ogloszenia-w-serwisie/4/mieszkania/", 'url_suffix': "",
                'func': invicus_parse, 'pagination': True},
    'lider': {'url': "http://www.liderkonin.pl/100-mieszkania", 'url_suffix': "", 'func': lider_parse,
              'pagination': False},
    'tok': {'url': "https://www.toknieruchomosci.com.pl/mieszkania", 'url_suffix': "", 'func': tok_parse,
            'pagination': False},
    'aba': {
        'url': "https://www.abanieruchomosci.pl/szukaj-oferty.html?estate_type=Mieszkania&ad_type=Sprzeda%C5%BC&locality=Konin&searching=yes&page_index=0",
        'url_suffix': "", 'func': aba_parse,
        'pagination': False},
    'zaroda': {
        'url': "http://www.zaroda-nieruchomosci.pl/oferta/szukaj?search%5Blocalization%5D=konin&search%5Btransaction%5D=1&search%5Btypes%5D=1",
        'url_suffix': "", 'func': zaroda_parse,
        'pagination': False},
    'trado': {
        'url': "http://tradonieruchomosci.pl/wyniki-wyszukiwania/?property_location=any&property_type=mieszkania&title=konin&property_feature=na-sprzedaz&search_nonce=479c85afba",
        'url_suffix': "", 'func': trado_parse, 'pagination': False},
    'lm': {'url': "https://www.lm.pl/ogloszenia/lista/85/", 'url_suffix': "/32454206", 'func': lm_parse,
           'pagination': True},
}


def main():
    starting_time = time.time()
    try:
        data = pd.DataFrame()
        for web in webs:
            data = pd.concat([data, scrap(web)], ignore_index=True, sort=False)
        if len(data):
            save_new_data(data)
        render_html()
        export_html_by_ftp()
    except Exception as e:
        print(e)
        logging.error(e)
    logging.info("Running time %ds using %d threads" % ((time.time() - starting_time), THREADS_COUNT))


# execute all the functions for one website and return data in dataframe
def scrap(web):
    pages_urls = prepare_pages_urls(web)
    init_results = iterate_urls(pages_urls, web, 1)
    # go to more detailed results of just new content
    new_content = extract_new_content(init_results)
    if new_content.empty:
        return pd.DataFrame()
    ads_urls = new_content['Url'].tolist()
    detailed_ads = iterate_urls(ads_urls, web, 2)
    results = new_content.merge(detailed_ads, on="Url")
    return results


# get last page from website (if there is any pagination) else return 1
def get_last_page(web):
    if not webs[web]['pagination']:
        return 1
    url = webs[web]['url'] + "1" + webs[web]['url_suffix']
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            raise r.raise_for_status()
        soup = BeautifulSoup(r.content, features="lxml")
        if web == 'lm':
            last_page = soup.find(class_='multicont_news_stronicowanie').find_all('a')[-2].get_text()
        elif web == 'invicus':
            last_page = soup.find(class_='perPage clear').find(class_='links').find_all('a')[-1].get_text()
        else:
            last_page = 1
        return int(last_page)
    except Exception as e:
        logging.info(e)
        return 1


# prepare list of urls for each page (if there is any pagination)
def prepare_pages_urls(web):
    url = webs[web]['url']
    url_suffix = webs[web]['url_suffix']
    last_page = get_last_page(web)
    if last_page == 1:
        return [url + url_suffix]
    else:
        pages = range(1, last_page + 1)
        return list(map(lambda x: url + str(x) + url_suffix, pages))


# using multiprocessing scrap all the urls from list (loop until all are done)
def iterate_urls(urls, web, step):
    request_timeout = INIT_REQUEST_TIMEOUT
    results = []
    # breaks when there are no failed requests or timeout rise to maxReqTime
    while len(urls) != 0 and request_timeout <= MAX_REQUEST_TIMEOUT:
        logging.info(web)
        if len(urls) > 8:
            p = multiprocessing.Pool(THREADS_COUNT)
            results += p.map(partial(get_page_soup, timeout=request_timeout, web=web, step=step), urls,
                             chunksize=CHUNK_SIZE)  # play with chunksize for better performance
            p.terminate()
            p.join()
        else:
            results += map(lambda x: get_page_soup(x, request_timeout, web, step), urls)
        results = [r for r in results if type(r) != str]
        # try again with failed results
        urls = [r for r in results if type(r) == str]
        request_timeout += 1
    return merge_to_dataframe(results)


# listOfListsOfDicts -> Dataframe
def merge_to_dataframe(lists):
    lists = [x for x in lists if x is not None]
    if len(lists) > 0:
        return pd.DataFrame(reduce(lambda x, y: x + y, lists))
    else:
        return pd.DataFrame(
            {'Url': [], 'Nazwa': [], 'Telefon': [], 'Cena': [], 'Zdjecie': [], 'Powierzchnia': 0.0, 'Piętro': [],
             'Tresc': [], 'Zrodlo': []})


# scraping data from single page (webfunc states for the function to be used to gather data)
def get_page_soup(page_url, timeout, web, step):
    gather_method = webs[web]['func']
    logging.info(page_url)
    # in case requests fails
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200:
            raise r.raise_for_status()
        soup = BeautifulSoup(r.content, features="lxml")
        return gather_method(web, soup, step, page_url)
    except Exception as e:
        logging.info(e)
        logging.info('failed...')
        return page_url


def extract_new_content(new_data):
    old_data = pd.read_pickle(DATABASE_FILE)
    new_content = get_new_lines(new_data, old_data)
    new_content = new_content.dropna(axis=1, how='all')
    return new_content


# get just new content from scraped data and save it on top of CSV file
def save_new_data(new_data):
    timestamp = strftime("%H:%M %d-%m-%Y", localtime())
    timestamp_row = pd.DataFrame(
        {'Url': [''], 'Nazwa': [''], 'Telefon': [''], 'Cena': [0], 'Zdjecie': [''], 'Powierzchnia': 0.0, 'Piętro': [''],
         'Tresc': ['---'], 'Zrodlo': [timestamp], 'Galeria': [['']]})
    old_data = pd.read_pickle(DATABASE_FILE)
    data = pd.concat([timestamp_row, new_data, old_data], ignore_index=True, sort=False)
    data.to_pickle(DATABASE_FILE)
    return data


# Merge data delivered in form of list of lists of dictionaries [[], [], [{},{},{}], [{},{},{}], ...]
def merge_results(list_of_dicts):
    whole_data = defaultdict(list)
    for r in list(filter(lambda x: len(x) > 0, list_of_dicts)):
        for dic in r:
            if type(dic) == dict:
                for key, value in dic.items():
                    whole_data[key].append(value)
    df = pd.DataFrame(whole_data)
    return df


def export_to_excel(path: Path, data):
    path = path.joinpath('output.xlsx')
    os.system("TASKKILL /F /IM excel.exe")
    writer = pd.ExcelWriter(str(path), engine="xlsxwriter", date_format='dd.mmm.yyyy')
    data.to_excel(writer, sheet_name='Sheet1', index=False, freeze_panes=(1, 0))
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # format excel
    format1 = workbook.add_format({'num_format': '000 000 000', 'align': 'center'})
    worksheet.set_column('A:A', 20)  # id
    worksheet.set_column('B:B', 15)  # adres
    worksheet.set_column('C:C', 16)  # kategoria
    worksheet.set_column('D:D', 12, format1)  # telefon
    worksheet.set_column('E:E', 50)  # link
    worksheet.set_column('F:F', 50)  # link google

    writer.save()
    # os.startfile(fileName)


# def export_to_csv(path: Path, data):
#     path = path.joinpath('output.csv')
#     data.to_csv(path, sep=",", header=True, index=False)
#
#
# def read_from_csv(path: Path):
#     path = path.joinpath('output.csv')
#     try:
#         df = pd.read_csv(path)
#         return df
#     except Exception as e:
#         logging.info(e)
#         return pd.DataFrame(
#             {'Url': [], 'Nazwa': [], 'Telefon': [], 'Cena': [], 'Zdjecie': [], 'Powierzchnia': float, 'Piętro': [],
#              'Tresc': [], 'Zrodlo': []})
#
#
# def export_to_json(path: Path, data):
#     path = path.joinpath('output.json')
#     data.to_json(path, orient='records')


def get_new_lines(df1, df2):
    df3 = pd.concat([df1, df2, df2], ignore_index=True, sort=False).drop_duplicates(subset=['Url'], keep=False)
    df4 = pd.concat([df3, df2, df2], ignore_index=True, sort=False).drop_duplicates(subset=['Nazwa'], keep=False)

    logging.info(f'{len(df4)} new lines')
    return df4


def render_html():
    data = pd.read_pickle(DATABASE_FILE)
    data = data.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
    data = data.fillna("")

    # calc square meter unit prices
    m2_price = []
    for i, r in data.iterrows():
        try:
            price = float(r['Cena'])
            area = float(r['Powierzchnia'])
            if area > 0:
                m2_price.append(int(price / area))
            else:
                m2_price.append("")
        except ValueError:
            m2_price.append("")
    data['CenaMetr'] = m2_price

    # limit to 270 chars
    data.Tresc = data.Tresc.str[:270]

    # if str consist 'ynaj' its probably rent ad
    data = data[~data.Nazwa.str.contains('ynaj')]

    template_loader = jinja2.FileSystemLoader(INDEX_TEMPLATE_PATH)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('index_template.html')
    rendered = template.render(data=data.to_dict('records'),
                               version=random.randint(0, 10000))  # version to avoid getting css and js from cache
    with open(OUTPUT_INDEX_PATH, "w", encoding='utf-8') as fp:
        fp.write(rendered)


def export_html_by_ftp():
    try:
        logging.info('Connecting FTP...')
        session = ftplib.FTP(cfg.FTP_SERVER, cfg.FTP_LOGIN, cfg.FTP_PASSWORD)
        logging.info('''Connected
            Sending file...''')
        file = open(OUTPUT_INDEX_PATH, 'rb')  # file to send
        session.storbinary(f'STOR {cfg.FTP_PATH}index.html', file, 102400)  # send the file
        file.close()  # close file and FTP
        session.quit()
    except Exception as e:
        logging.info(e)


if __name__ == '__main__':
    main()
