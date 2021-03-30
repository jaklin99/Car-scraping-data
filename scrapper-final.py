from tkinter import INSERT

from bs4 import BeautifulSoup as soup
from requests import get
import json
import requests
import re
import mysql.connector
from datetime import date

data = { 'cars': [] }
_cars = {}
datas = {}


def has_next_page(car_soup):
    paginator_container = car_soup.find("table", {"class": "ver13black"}).find("table")
    pages = paginator_container.findAll("td")
    pages = list(map(lambda x: x.text, pages))

    if pages is None:
        return False

    if pages[-1] == 'Следваща':
        return True

    return False


def get_all_data():
    search_url = 'https://www.cars.bg/index.php?go=cars&search=1&advanced=1&fromhomeu=1&publishedTime=0&filterOrderBy=1&showPrice=0&autotype=1&stateId=1&brandId=0&modelId=&yearFrom=&yearTo=&priceFrom=&priceTo=&currencyId=1&locationId=0&radius=1&conditionId=0&photos=0&barter=0&dcredit=0&leasing=0&fuelId=0&gearId=0&usageId=0&steering_weel=0&categoryId=0&offerFromA=0&offerFromB=0&offerFromC=0&offerFromD=0&offersForA=1&offersForB=0&offersForC=0&offersForD=1&doorId=0&manual_price=0&man_priceFrom=0&man_priceTo=0'

    result = get(search_url)
    search_soup = soup(result.text, "html.parser")

    cmbInfo = search_soup.find("select", {"id": "BrandId"}).find_all("option")

    for car in cmbInfo:
        if car.text == '- Всички -' or car.text == '':
            continue

        brand_id = car['value']
        brand_name = car.text

#insert the make into the db
        connection=''
        cursor=''
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='carcatalog',
                                                 user='root',
                                                 password='',
                                                 )
            if connection.is_connected():
                cursor = connection.cursor()
                print('Connected to the database')
                make_query = f"INSERT INTO car_make(make) values ('{brand_name}')"
                cursor.execute(make_query)
                connection.commit()

            # cursor = connection.cursor()
            # result = cursor.execute(db_query)
            # print("Table created successfully ")

        except mysql.connector.Error as error:
            print("Failed to create table in MySQL: {}".format(error))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

        _cars[brand_id] = brand_name
        datas[brand_name] = {}

        models_url = f"https://www.cars.bg/?ajax=multimodel&brandId={brand_id}"
        req = requests.get(models_url)
        brand_soup = soup(req.content, 'html.parser')
        brands = brand_soup.find_all("ul", {"id": "models_list"})

        # if brand_name != 'Alfa Romeo':
        #     continue
        #
        # print(brand_name)

        for item in brands:
            model_names = map(lambda el: el.text, item.findAll('li'))
            model_names = list(model_names)

            model_ids = map(lambda el: el.input['value'], item.findAll('li'))
            model_ids = list(model_ids)

            models = []

            for i in range(len(model_ids)):
                if not model_ids[i].isnumeric():
                    continue

                models.append({
                    'id': model_ids[i],
                    'name': model_names[i].strip()
                })

            for model in models:
                if model['name'] != '156':
                    continue

                car_url = f"https://www.cars.bg/?go=cars&search=1&advanced=0&fromhomeu=1&publishedTime=0&filterOrderBy=1&showPrice=0&autotype=1&stateId=1&section=cars&categoryId=0&doorId=0&brandId={brand_id}&modelId=0&models%5B%5D={model['id']}&fuelId=0&gearId=0&yearFrom=&yearTo=&priceFrom=&priceTo=&currencyId=1&man_priceFrom=0&man_priceTo=0&man_currencyId=1&location=&locationId=0&radius=1&offersForD=1&offersForA=1"
                car_req = requests.get(car_url)
                page_soup = soup(car_req.content, 'html.parser')

                model_name = model['name']

                datas[brand_name][model_name] = []

                page = 1

                while True:
                    # grab each product
                    allCars = page_soup.find('table', class_='tableListResults')
                    if allCars is None:
                        break

                    allCars = allCars.findAll('tr')

                    #take the information for a certain car from the catalog
                    for c in allCars:
                        ml = c.text.split(" ")
                        ml = [ele for ele in ml if ele != '']
                        ml = ml[5:20]
                        ml = ml[:-1]

                        fuel = ''
                        if 'дизел' in ml or 'дизел,' in ml:
                            fuel = 'дизел'
                        elif 'бензин' in ml or 'бензин,' in ml:
                            fuel = 'бензин'
                        elif 'газ/бензин' in ml or 'газ/бензин,' in ml:
                            fuel = 'газ/бензин'
                        elif 'хибрид' in ml or 'хибрид,' in ml:
                            fuel = 'хибрид'
                        elif 'метан/бензин' in ml or 'метан/бензин,' in ml:
                            fuel = 'метан/бензин'
                        elif 'електричество' in ml or 'електричество,' in ml:
                            fuel = 'електричество'

                        result = re.search(r"[0-9]+[\s\,]*[0-9]+\s?км", c.text, re.MULTILINE)

                        if result:
                            car_make=brand_name
                            car_model=model_name
                            url="https://www.cars.bg/" + c.find('a', {'class': 'ver15black'})['href']
                            price= c.find('span', class_='ver20black').text if c.find('span', class_='ver20black') is not None else ''
                            mileage=result.group(0)
                            fuel=fuel
                            year=c.find('span', class_='year').text
                            today=date.today()
                            
                            try:
                                connection = mysql.connector.connect(host='localhost',
                                                                     database='carcatalog',
                                                                     user='root',
                                                                     password='',
                                                                     )
                                if connection.is_connected():
                                    cursor = connection.cursor()
                                    print('Connected to the database')

                                    #value = f"({car_make}, {car_model}, {url}, {price}, {mileage}, {fuel}, {year}, {today})"

                                    insert_query = f"INSERT INTO `car_catalog` (`make`, `model`, `url`, `price`, `mileage`, `fuel`, `year`, `issue_date`) VALUES ('{car_make}', '{car_model}', '{url}', {price.replace(',', '').replace(' ', '')}, '{mileage.replace(',', '').replace(' км', '')}', '{fuel}', {year}, '{today}')"
                                    print(insert_query)
                                    #m="INSERT INTO car_catalog (`make`, `model`, `url`, `price`, `mileage`, `fuel`, `year`, `issue_date') values (%s,%s,%s,%s,%s,%s,%s,%s)"
                                    #v=('Acura', 'fdsxz','vgfds',65,543,'бензин',2000,'09/01/01')
                                    cursor.execute(insert_query)
                                    connection.commit()

                            except mysql.connector.Error as error:
                                print("Failed to create table in MySQL: {}".format(error))
                            finally:
                                if (connection.is_connected()):
                                    cursor.close()
                                    connection.close()
                                    print("MySQL connection is closed")

                            # datas[brand_name][model_name].append({
                            #     'make': brand_name,
                            #     'model': model_name,
                            #     'url': "https://www.cars.bg/" + c.find('a', {'class': 'ver15black'})['href'],
                            #     'price': c.find('span', class_='ver20black').text if c.find('span', class_='ver20black') is not None else '',
                            #     'mileage': result.group(0),
                            #     'fuel': fuel,
                            #     'year: ': c.find('span', class_='year').text
                            # })
                        else:
                            print("No information for the mileage.")

                    if not has_next_page(page_soup):
                        break

                    #go to the next page
                    page += 1
                    car_url = f"https://www.cars.bg/?go=cars&search=1&advanced=0&fromhomeu=1&publishedTime=0&filterOrderBy=1&showPrice=0&autotype=1&stateId=1&section=cars&categoryId=0&doorId=0&brandId={brand_id}&modelId=0&models%5B0%5D={model['id']}&fuelId=0&gearId=0&yearFrom=&yearTo=&priceFrom=&priceTo=&currencyId=1&man_priceFrom=0&man_priceTo=0&man_currencyId=1&location=&locationId=0&radius=1&offersForD=1&offersForA=1&p=home&colorId=0&conditionId=0&usageId=0&barter=0&dcredit=0&leasing=0&offerFromA=0&offerFromB=0&offerFromC=0&offerFromD=0&offersForB=0&offersForC=0&cref=92&&page={page}"
                    car_req = requests.get(car_url)
                    page_soup = soup(car_req.content, 'html.parser')

            with open('dataCarFromPage.json', 'w+') as outfile:
                json.dump(datas, outfile, ensure_ascii=False, indent=4)


get_all_data()


exit()