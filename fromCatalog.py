
from bs4 import BeautifulSoup as soup
from requests import get
import json

my_url = 'https://www.cars.bg/?go=cars&search=1&fromhomeu=1&currencyId=1&autotype=1&stateId=1&offersForD=1&offersForA=1&filterOrderBy=1&radius=1'

result=get(my_url)

# html parsing
page_soup = soup(result.text, "html.parser")

# grab each product
allCars = page_soup.findAll("tr", {"class": "odd"})
car = allCars[0]
cars = []

data = {}
data['cars'] = []

make=car.b.text
_make=make.split()
print(_make)

for c in allCars:
    ml=c.text.split(" ")
    ml=[ele for ele in ml if ele != '']
    ml=ml[5:20]
    index=ml.index('км')-1

    data['cars'].append({
        'make': _make[0] + _make[1],
        'model': c.b.text,
        'price': c.find('span', class_='ver20black').text,
        'mileage': ml[index],
        'year: ': c.find('span', class_='year').text
    })
    with open('fromCatalog.json', 'w') as outfile:
      json.dump(data, outfile)
