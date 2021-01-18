import traceback
import re
from config import *


def lm_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_="ogloszenie_kontener")
            for ad in ads:
                ad_url = 'https://www.lm.pl' + ad.find('a', class_="link_tytul").get('href')
                ad_name = ad.find('a', class_="link_tytul").get_text().strip()
                ad_info = ad.find(class_="ogloszenie_kontener_info").get_text()
                ad_info = ad_info.split('Telefon: ')
                ad_phone = ad_info[-1] if len(ad_info) > 1 else None
                ad_info = ad_info[0].split('Cena: ')
                if len(ad_info) > 1:
                    ad_price = ad_info[-1].replace("zł", "").strip()
                    if ad_price.isdigit() and int(ad_price) < 400:
                        ad_price = str(ad_price) + '000'
                else:
                    ad_price = 0
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text = soup.find(class_="ogloszenie_tresc").get_text().strip()
            ad_info_bar = soup.find(class_="ogloszenie_infobar")
            ad_area = 0
            ad_level = ""
            if ad_info_bar:
                infos = ad_info_bar.get_text().split(', ')
                for info in infos:
                    if "Powierzchnia" in info:
                        try:
                            ad_area = float(info.split(': ')[-1].replace("m2", "").replace(" ", "").replace(",", "."))
                        except:
                            logging.info('error in parsing area from lm_parse')
                            pass
                    elif "Piętro" in info:
                        ad_level = info.split(': ')[-1]
            ad_gallery = soup.find(class_="ogl_galeria")
            if ad_gallery:
                ad_photos = list(map(lambda x: x['href'], ad_gallery.find_all('a')))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def sobieraj_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_="item")
            for ad in ads:
                ad_type = ad.find(class_="value Rodzaj transakcji").get_text()
                if ad_type != "Sprzedaż":
                    continue
                ad_url = 'http://www.sobieraj-nieruchomosci.pl/' + ad.find('a')['href']
                ad_name = ad.find(class_="Tytuł").a.get_text().strip()
                ad_price = ad.find(class_='Cena').font.get_text().split(',')[0].replace(' ', '')
                ad_phone = '665 028 033'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text = soup.find(class_="Opis").find_all(text=True)
            ad_text = ''.join(ad_text)
            try:
                ad_area = float(soup.find(class_='Powierzchnia').get_text().split('m')[0].replace(',', '.'))
            except:
                ad_area = 0.
            ad_level = ""
            ad_gallery = soup.find_all(class_="image")
            if ad_gallery:
                ad_photos = list(map(lambda x: 'http://www.sobieraj-nieruchomosci.pl/' + x.a['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def florczyk_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find(class_='col-xs-12 hidden-xs').find_all(class_="link-opacity")
            for ad in ads:
                ad_url = ad['href']
                ad_name = ad.find(class_="img-list-opis").h4.get_text().strip()
                ad_price = ad.find(class_='img-list-opis').p.get_text().split(' ')[-2].replace('.', '')
                ad_phone = '609 192 788'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text_box = soup.find(class_="single-oferta-tresc").find_all('li')
            if ad_text_box:
                ad_text = ad_text_box[0].get_text()
                if len(ad_text_box) > 1:
                    ad_text += ' ' + ad_text_box[1].get_text()
            else:
                ad_text = ""
            ad_info = soup.find(class_='szczegoly-oferty').find_all('tr')[2]
            ad_level = ad_info.find_all('td')[1].get_text().replace("Piętro: ", "")
            try:
                ad_area = float(ad_info.find('td').get_text().split(' ')[-2].replace(',', '.'))
            except:
                ad_area = 0.
            ad_gallery = soup.find_all(class_="zdjecie-galeria")
            if ad_gallery:
                ad_photos = list(map(lambda x: 'http://florczyk.nieruchomosci.pl' + x['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def abakus_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_='oferta_boks')
            for ad in ads:
                ad_url = ad.a['href']
                ad_name = ad.find(class_="padding_boks").h2.get_text().strip()
                ad_price = \
                    ad.find(class_="padding_boks").get_text().split("Numer")[0].replace("\n", " ").replace("\xa0",
                                                                                                           " ").replace(
                        " zł", "").split(" ")[-2].replace("zł", "").replace(".", "")
                ad_phone = '691 717 771'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text = soup.find('tbody').find_all('tr')[-2].find_all('td')[-1].get_text().strip().replace('\n', " ")
            rows = soup.find('tbody').find_all('tr')
            ad_level = ''
            ad_area = 0.
            for row in rows:
                r = row.find('strong')
                if r:
                    if r.get_text().strip() in ['Usytuowanie:', 'Usytuowane:', 'Kondygnacja:']:
                        ad_level = row.find_all('td')[-1].get_text().strip()
                    elif r.get_text().strip() == 'Powierzchnia:':
                        try:
                            ad_area = float(
                                row.find_all('td')[-1].get_text().strip().replace('m2', '').replace(",", "."))
                        except:
                            ad_area = 0.
            ad_gallery = soup.find_all(rel="fancygal")
            if ad_gallery:
                ad_photos = list(map(lambda x: 'http://abakus.konin.pl/' + x['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def invicus_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find(id='itemsList').find_all(class_='item')
            for ad in ads:
                ad_type = ad.find(class_='type').get_text().strip()
                ad_sold = ad.find(class_="sold")
                if ad_type == 'Wynajem Mieszkania' or ad_sold:
                    continue
                ad_url = ad.find(class_="photo").a['href']
                ad_name = ad.find(class_="title").h2.get_text().strip()
                ad_price = ad.find(class_="last").h3.get_text().replace(" ", "")
                ad_phone = '797 017 786'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text = ''
            rows = soup.find(class_='right').find_all(class_='section')
            ad_level = ''
            ad_area = 0.
            for row in rows:
                r = row.find(class_='l')
                span = row.find('span')
                if r:
                    if r.get_text().strip() == 'POWIERZCHNIA:':
                        try:
                            ad_area = float(row.find(class_="r").get_text().strip().split(' ')[0].replace(',', '.'))
                        except:
                            ad_area = 0.
                if span:
                    if span.get_text().strip() == 'Opis:':
                        divided_description = row.get_text().split('\n')
                        ad_text = max(divided_description, key=len)
            ad_gallery = soup.find_all(class_="thumb")
            if ad_gallery:
                ad_photos = list(map(lambda x: x['big'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def lider_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find(class_='product_list').find_all(class_='product-container')
            for ad in ads:
                ad_price = ad.find(class_="product-price").get_text().split('zł')[0].replace(" ", "")
                try:
                    if ad_price.isdigit() and int(ad_price) < 5000:
                        continue
                except:
                    traceback.logging.info_exc()
                ad_url = ad.a['href']
                ad_name = ad.find(class_="product-name").get_text().strip()
                ad_phone = '695 233 900'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_text = soup.find(class_='pa_content').find('p').get_text().strip()
            try:
                ad_area = float(
                    soup.find(id='short_description_content').p.get_text().replace("m2", '').split(" ")[1].replace(",",
                                                                                                                   "."))
            except:
                ad_area = 0.
                traceback.logging.info_exc()
            ad_gallery = soup.find_all(class_="fancybox")
            if ad_gallery:
                ad_photos = list(map(lambda x: x['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            ad_level = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def trado_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find(class_='listings').find_all('li')
            for ad in ads:
                ad_url = ad.find_all('a')[-1]['href']
                ad_price = ad.find(itemprop="price").get_text().replace(".", "")
                ad_name = ad.find(class_="entry-title").a.get_text().strip()
                ad_phone = '604 053 500'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            divided_description = soup.find(class_='entry-content').find('p').get_text().split('\n')
            ad_text = max(divided_description, key=len)
            try:
                ad_area = float(ad_text.split(" m2")[0].split(" ")[-1].replace(",", "."))
            except:
                ad_area = 0.
                traceback.logging.info_exc()
            ad_gallery = soup.find_all(class_="listing-gallery-popup")
            if ad_gallery:
                ad_photos = list(map(lambda x: x['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            ad_level = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def zaroda_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_='offerts-block')
            for ad in ads:
                ad_url = 'http://www.zaroda-nieruchomosci.pl' + ad.find('a')['href']
                ad_price = ad.find(class_="last").find(class_='right').b.find_all(text=True)[0].replace(' ', '')
                ad_name = ad.find(class_="first").find(class_='left').b.get_text().strip()
                ad_phone = '782 097 847'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            divided_description = soup.find(class_='single-offer-description-text').get_text().split('\n')
            ad_text = ''.join(divided_description[0:4])
            ad_text = re.sub(" +", ' ', ad_text)
            try:
                ad_area = float(
                    soup.find(class_='bottom clearfix').find(class_='left').b.get_text().replace(" ", "").replace(",",
                                                                                                                  "."))
            except:
                ad_area = 0.
                traceback.logging.info_exc()
            ad_gallery = soup.find_all(class_="swiper-slide")
            if ad_gallery:
                ad_photos = list(map(lambda x: x.img['src'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            ad_level = ''
            infos = soup.find(class_='single-offer-description-list').find_all('li')
            for info in infos:
                if info.span.get_text().strip() == "Piętro:":
                    ad_level = info.b.get_text()
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def aba_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_='thumbnail')
            for ad in ads:
                ad_url = 'https://www.abanieruchomosci.pl' + ad.find('a')['href']
                ad_price = ad.find(class_="thumbnail-price").find_all(text=True)[0].strip().replace('PLN', "").replace(
                    ' ', '')
                ad_name = ad.find(class_="caption").a.get_text().strip()
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            rows = soup.find_all(class_='row')
            ad_text = ''
            ad_area = ''
            ad_level = ''
            for row in rows:
                r = row.div.get_text().strip()
                if r == 'Pomieszczenia':
                    ad_text = row.find_all('div')[-1].get_text()
                elif r == 'Powierzchnia':
                    try:
                        ad_area = float(
                            row.find_all('div')[-1].get_text().replace('m2', '').replace(' ', '').replace(',', '.'))
                    except:
                        traceback.logging.info_exc()
                elif r == 'Położenie mieszkania':
                    ad_level = row.find_all('div')[-1].get_text()
            ad_gallery = soup.find_all(class_="item")
            if ad_gallery:
                ad_photos = list(
                    map(lambda x: 'https://www.abanieruchomosci.pl' + x.img['src'].replace('\r', ''), ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            ad_phone = soup.find(class_='media-body').a.get_text().replace("+48 ", "")
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Telefon': ad_phone, 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None


def tok_parse(web, soup, step, url):
    results = []
    try:
        if step == 1:
            ads = soup.find_all(class_='ip-overview-row')
            for ad in ads:
                ad_url = 'https://www.toknieruchomosci.com.pl' + ad.find('a')['href']
                ad_price = ad.find(class_="ip-overview-price").get_text().strip().split('zł ')[-1].split(" zł")[
                    0].replace('.', '')
                try:
                    if ad_price.isdigit() and int(ad_price) < 5000:
                        continue
                except:
                    traceback.logging.info_exc()
                ad_name = 'https://www.toknieruchomosci.com.pl' + ad.find(
                    class_='ip-overview-title').a.get_text().strip()
                ad_phone = '605 618 289'
                results.append({'Url': ad_url, 'Nazwa': ad_name, 'Telefon': ad_phone, 'Cena': ad_price, 'Zrodlo': web})
            return results
        elif step == 2:
            ad_level = ''
            ad_text = soup.find(class_='ip-desc-wrapper').find_all(text=True)
            ad_text = ''.join(ad_text[:2]).strip()
            try:
                ad_area = float(soup.find(class_='ip-mapright-formattedsqft').find(class_='pull-right').get_text())
            except:
                ad_area = 0.
                traceback.logging.info_exc()
            ad_gallery = soup.find(id="ip-image-tab").find_all('a')
            if ad_gallery:
                ad_photos = list(map(lambda x: 'https://www.toknieruchomosci.com.pl' + x['href'], ad_gallery))
                ad_photo = ad_photos[0]
            else:
                ad_photos = []
                ad_photo = ''
            results.append(
                {'Url': url, 'Tresc': ad_text, 'Powierzchnia': ad_area, 'Piętro': ad_level, 'Galeria': ad_photos,
                 'Zdjecie': ad_photo})
            return results
    except:
        traceback.logging.info_exc()
        return None
