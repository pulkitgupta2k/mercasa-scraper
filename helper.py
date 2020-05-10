import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import itertools


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
        product = []
        for item in s.findAll("div",{"class": "formProducto"}):
            p = {}
            i = item.find("input")
            p[i['id'].replace("checkbox-productos-", "")] = item.text.strip()
            product.append(p)
        products.append(product)

    products_dict = {}

    for (h,p) in zip(headings, products):
        products_dict[h] = p

    pprint(products_dict)

    with open("products.json", "w") as f:
        json.dump(products_dict, f, indent = 4)