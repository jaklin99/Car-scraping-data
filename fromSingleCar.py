from bs4 import BeautifulSoup as soup
from requests import get
import json

my_url = 'https://www.cars.bg/offer/5e9f1e587587df0ded0c54b3'

result = get(my_url)

page_soup = soup(result.text, "html.parser")
make_soup = page_soup.find_all("table")
car = page_soup.find("table", {"class": "ver13black"})

fromSingleCar = {}
fromSingleCar['car'] = []

make = car.find('td', class_='ver30black line-bottom-border').strong.text
_make = make.split()

production = car.td.text.split(" ")
production = [ele for ele in production if ele != '']
production = production[5:20]
print(_make)

fromSingleCar['car'].append({
    'make': _make[0],
    'model': car.find('td', class_='ver30black line-bottom-border').strong.text,
    'price': car.find('span', class_='ver20black').text,
    'mileage': car.td.text,
})
with open('fromSingleCar.json', 'w') as outfile:
    json.dump(fromSingleCar, outfile)
