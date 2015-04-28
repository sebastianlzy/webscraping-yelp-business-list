__author__ = 'sebastianlee'




from bs4 import BeautifulSoup
from urllib import urlencode
from urllib2 import urlopen
from selenium import webdriver
import unicodecsv as csv
import datetime
import sys
import re
import time
import pdb


# HOME_URL= "http://my.openrice.com"

# 1. CHANGE THE HOME URL
HOME_URL= "http://www.yelp.co.uk"
BROWSER = webdriver.Firefox()
LAST_PAGE = 10
CURRENT_PAGE = 0
SERVICES = ["Roofing", "Security+Systems", "Tiling", "Swimming+Pool+Services", "Upholstering", "Water+Heaters", "Waterproofing", "Windows"]




def main():
    global CURRENT_PAGE
    global LAST_PAGE
    global SERVICE
    for service in SERVICES:
        SERVICE = service
        CURRENT_PAGE = 0
        print SERVICE
        while True:
            BROWSER.get(get_url_for_(HOME_URL, CURRENT_PAGE * 10))
            time.sleep(5)
            soup = BeautifulSoup(BROWSER.page_source )
            if (CURRENT_PAGE + 1) >= LAST_PAGE:
                break
            if CURRENT_PAGE == 0:
                try:
                    LAST_PAGE = get_last_page(soup)
                except ValueError as err:
                    print(err.args)
                    break
            print "Scraping page {number} of {last_page}".format(number=CURRENT_PAGE + 1,last_page=LAST_PAGE)
            CURRENT_PAGE = CURRENT_PAGE + 1
            write_services_to_csv(soup)
    BROWSER.quit()

def get_url_for_(home_url, number):
    global SERVICE
    return HOME_URL + "/search?find_desc={service}&find_loc=Singapore&ns=1#start={number}".format(number=number, service=SERVICE)

def get_last_page(soup):
    try:
        page_text = soup.find(class_="page-of-pages").text
        pages = re.findall(r"(\d+)", page_text)
        return int(pages[1])
    except:
        raise ValueError('No last page', HOME_URL)




def write_services_to_csv(soup):
    global CURRENT_PAGE
    global SERVICES
    try:
        results = soup.find_all(class_="search-result")
        service_data = [["Name", "Phone", "Ratings", "Reviews", "Address Line 1", "Postal Code", "Img Src"]]
        for index, result in enumerate(results):
            service_datum = []
            service_datum.extend(get_biz_name(result))
            service_datum.extend(get_biz_phone(result))
            service_datum.extend(get_biz_rating(result))
            service_datum.extend(get_address(result))
            service_datum.extend(get_biz_img_src(result))

            service_data.append(service_datum)
        write_to_csv("{service}_{number}.csv".format(number=CURRENT_PAGE, service=SERVICE), service_data)
    except:
        print "Unexpected error:", sys.exc_info()[0]

def get_address(result):
    try:
        biz_address = result.find(class_="secondary-attributes").find("address").text.split("Singapore")
        return [biz_address[0], biz_address[1]]
    except:
        print "No rating/review count"
        return ["nil", "nil"]

def get_biz_rating(result):
    try:
        biz_rating = result.find(class_="biz-rating").find(class_="star-img").attrs["title"]
        biz_review_count = result.find(class_="biz-rating").find(class_="review-count").text
        return [biz_rating, biz_review_count]
    except:
        print "No rating/review count"
        return ["nil", "nil"]

def get_biz_phone(result):
    try:
        return [result.find(class_="biz-phone").text]
    except:
        print "No phone"
        return [""]
def get_biz_name(result):
    try:
        return [result.find(class_="biz-name").text]
    except:
        print "No Name"
        return [""]
def get_biz_img_src(result):
    try:
        return [result.find(class_="photo-box").find("img").attrs["src"]]
    except:
        print "No Image"
        return [""]




def write_to_csv(file_name, arr_objs):
    with open(file_name, 'wb') as csvfile:
        csv_writer = csv.writer(csvfile, encoding="utf-8")
        for arr_obj in arr_objs:
            try:
                csv_writer.writerow(arr_obj)
            except UnicodeEncodeError:
                print "cant write ", arr_obj, " into file"



if __name__ == '__main__':
    main()
