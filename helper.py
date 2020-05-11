import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import itertools

def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def getHTML(link):
    req = requests.get(link)
    html = req.content
    return html

def getProducts():
    html = getHTML("https://www.mercasa.es/red-de-mercas/precios-y-mercados-mayoristas/grafica")
    soup = BeautifulSoup(html, "html.parser")
    headings = []
    products = []

    for heading in soup.findAll("a",{"class" : "tipo"}):
        headings.append(heading.text.strip())

    for s in soup.findAll("div",{"class" : "formProductos"}):
        product = {}
        for item in s.findAll("div",{"class": "formProducto"}):
            i = item.find("input")
            product[i['id'].replace("checkbox-productos-", "")] = item.text.strip()
        products.append(product)

    products_dict = {}

    for (h,p) in zip(headings, products):
        products_dict[h] = p

    pprint(products_dict)

    with open("products.json", "w") as f:
        json.dump(products_dict, f, indent = 4)


def getData(product_no):
    link = "https://www.mercasa.es/red-de-mercas/precios-y-mercados-mayoristas/grafica"

    date_start = "2015-01-01"
    date_end = "2020-05-10"
    productos = product_no
    headers = {'Host' : 'www.mercasa.es', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0', 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language' : 'en-US,en;q=0.5', 'Accept-Encoding' : 'gzip, deflate', 'Content-Type' : 'application/x-www-form-urlencoded', 'Connection' : 'close', 'Referer' : 'https://www.mercasa.es/red-de-mercas/precios-y-mercados-mayoristas/grafica', 'Upgrade-Insecure-Requests' : '1', 'DNT' : '1'}
    payload = "mayoristas=1%2C2%2C3%2C4%2C5&productos={}&media=on&fechaInicio={}&fechaFin={}".format(productos, date_start, date_end)
    # print(payload)
    req = requests.post(link, data=payload, headers = headers)
    html = req.content
    soup = BeautifulSoup(html,"html.parser")
    # print(soup)
    chart = soup.find("div",{"class" : "mychart dentroSeccion"})
    script = chart.find("script").text.strip()[16:-2]
    # print(script)
    script = find_between(script, "data: [", "]").strip()
    script = script.replace("fecha", "\"fecha\"")
    script = script.replace("null", "0")
    # print(script)
    script = eval(script)
    return script

def single_detail(product_no):
    product_no = str(product_no)
    with open("product_details.json") as f:
        products_details = json.load(f)

    with open("products.json") as g:
        products = json.load(g)
    heading = ""
    product_name = ""
    for h, p in products.items():
        for no, name in p.items():
            if no == product_no:
                heading = h
                product_name = name
    print(heading)
    print(product_name)
    products_details[heading][product_no] = {}
    products_details[heading][product_no]['product_name'] = product_name
    products_prices = getData(product_no)
    products_details[heading][product_no]['prices'] = {}
    for products_price in products_prices:
        products_price =  {k.upper(): v for k, v in products_price.items()}
        try:
            products_details[heading][product_no]['prices'][products_price['FECHA']] = products_price[product_name]
        except Exception as e:
            pass

    with open('product_details.json', "w") as f:
        json.dump(products_details, f, indent=4)

def generateDates():
    dates = []
    with open("product_details.json") as f:
        products_details = json.load(f)
    for headings, details in products_details.items():
        for number, products_detail in details.items():
            # print(products_detail['prices'])
            for date, names in products_detail['prices'].items():
                if date not in dates:
                    dates.append(date)
    dates.sort()
    d = {}
    d['dates'] = dates
    with open('dates.json', "w") as f:
        json.dump(d, f, indent=4)

def driver():
    with open("products.json") as f:
        products_json = json.load(f)
    # print(products)
    products_details = {}
    for heading,products in products_json.items():
        products_details[heading] = {}
        for product_no, product_name in products.items():
            try:
                products_details[heading][product_no] = {}
                products_details[heading][product_no]['product_name'] = product_name
                products_prices = getData(product_no)
                products_details[heading][product_no]['prices'] = {}
                print(product_name)
                for products_price in products_prices:
                    products_price =  {k.upper(): v for k, v in products_price.items()}
                    try:
                        products_details[heading][product_no]['prices'][products_price['FECHA']] = products_price[product_name]
                    except Exception as e:
                        pass
                        # print(e)
                        # products_details[heading][product_no]['prices'][products_price['FECHA']] = ""
                # pprint(products_details)
            except:
                print ("error")
    with open('product_details.json', "w") as f:
        json.dump(products_details, f, indent=4)