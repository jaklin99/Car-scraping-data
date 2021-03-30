from bs4 import BeautifulSoup as soup, SoupStrainer
from requests import get
import json
import requests

url = "https://www.cars.bg/?ajax=multimodel&brandId={}"
req = requests.get(url)
brand_soup = soup(req.content, 'html.parser')
brands = brand_soup.find_all("ul", {"id": "models_list"})

bmw = []
data = {}
data['cars'] = []

cars = {}

def getBrands():
    search_url = 'https://www.cars.bg/index.php?go=cars&search=1&advanced=1&fromhomeu=1&publishedTime=0&filterOrderBy=1&showPrice=0&autotype=1&stateId=1&brandId=0&modelId=&yearFrom=&yearTo=&priceFrom=&priceTo=&currencyId=1&locationId=0&radius=1&conditionId=0&photos=0&barter=0&dcredit=0&leasing=0&fuelId=0&gearId=0&usageId=0&steering_weel=0&categoryId=0&offerFromA=0&offerFromB=0&offerFromC=0&offerFromD=0&offersForA=1&offersForB=0&offersForC=0&offersForD=1&doorId=0&manual_price=0&man_priceFrom=0&man_priceTo=0'

    result = get(search_url)
    search_soup = soup(result.text, "html.parser")

    cmbInfo = search_soup.find("select", {"id": "BrandId"}).find_all("option")
    #cmbModel=search_soup.find("select", {"id": "ModelId"}).find_all("option")
    #for model in cmbModel:
        #if model
    for car in cmbInfo:
        if car.text != '- Всички -' and car.text != '':
            cars[car['value']] = car.text

            models_url = f"https://www.cars.bg/?ajax=multimodel&brandId={car['value']}"
            req = requests.get(models_url)
            brand_soup = soup(req.content, 'html.parser')
            brands = brand_soup.find_all("ul", {"id": "models_list"})

            for item in brands:
                modelsArr = item.find('li').text.split()
                model_id = item.find('li').input['value']
                #print(model_id)
                #print(modelsArr)

                for index in modelsArr:
                    #print(index)
                    car_url=f"https://www.cars.bg/?go=cars&search=1&&fromhomeu=1&section=cars&brandId={car['value']}&models[]={index}"
                    car_req=requests.get(car_url)
                    car_soup=soup(car_req.content, 'html.parser')

                    odd = car_soup.findAll("tr", {"class": "odd"})
                    even=car_soup.findAll("tr", {"class": "even"})
                    odd_last=car_soup.findAll("tr", {"class": "odd last"})
                    even_last=car_soup.findAll("tr", {"class": "even last"})
                    #print(odd[0])
                    # if odd == None:

                    # elif even== None:

                    # elif odd == None:

                    # elif even_last ==None:

                    for od in odd:
                        if od == None:
                            print('none')
                        if od == '':
                            print('nada')
                        data['cars'].append({
                            'brand': index,
                            #'link': od.find("a",{"class":"ver15black"})
                        })
                    with open('brands.json', 'w') as outfile:
                        json.dump(data, outfile)
            #print(cars[car['value']])


getBrands()


