import json, time, requests
from bs4 import BeautifulSoup
from config import HEADERS
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver = webdriver.Chrome('./chromedriver', options=options)

#We initialize the Excel workbook and sheet
workbook = xlsxwriter.Workbook('cies.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write('B2', 'NOM')
worksheet.write('C2', 'VILLE')
worksheet.write('D2', 'DESCRIPTION')
worksheet.write('E2', 'ICE')
worksheet.write('F2', 'REGISTRE COMMERCE')
worksheet.write('G2', 'IDENTIFIANT FISCAL')
worksheet.write('H2', 'CREATION')
worksheet.write('I2', 'ACTIVITE')

def write_in_excel(worksheet,line,  nom, ville, desc, ice, reg, fisc, creation, activite):
    worksheet.write(f'B{line}', f'{nom}')
    worksheet.write(f'C{line}', f'{ville}')
    worksheet.write(f'D{line}', f'{desc}')
    worksheet.write(f'E{line}', f'{ice}')
    worksheet.write(f'F{line}', f'{reg}')
    worksheet.write(f'G{line}', f'{fisc}')
    worksheet.write(f'H{line}', f'{creation}')
    worksheet.write(f'I{line}', f'{activite}')

def search_city(driver, city_value, page):
    url = f"https://maroc.welipro.com/recherche-avancee?name=&ice=&rc=&cnss=&acro=&if=&patente=&v={city_value}&rs=&cp=1&cp_max=2035272260000&et=&page={page}"
    got_source = False
    i = 0
    #If there is an error loading the page, we retry 5 times
    while not got_source and i<5:
        driver.get(url)
        html = driver.page_source
        if "Aucun Résultat trouvé " in html:
            got_source = False
            time.sleep(2)
            print("No result, retrying")
        else:
            got_source = True
        i = i+1

    return html

#LOADING VARS
with open("cities_names.json", "r") as f:
    cities_names = json.load(f)

with open("cities_values.json", 'r') as f:
    cities_vals = json.load(f)

i = 0
line_index = 1 #to determine what line we should write on in our excel sheet

while i<len(cities_vals):
    city_name = cities_names[i]
    city_value = cities_vals[i] #We use it to search on the website
    page = 1
    explore = True

    while explore:
        html = search_city(driver, city_value, page)
        if "La page que vous cherchez est introuvable" in html:
            print(f"Explored all pages for {city_name}")
            explore = False
        else:
            page_source = html
            parser = BeautifulSoup(page_source, 'html.parser')
            companies = parser.find_all("div", {"class": "card border-bottom-1 border-bottom-success rounded-bottom-0"})
            for company in companies:
                ville = city_name
                line = line_index + 2
                company_name = company.find("h3").find("a").text.strip()
                try:
                    company_description = company.find("div", {"class":"card-body"}).text.strip()
                except:
                    company_description = "-"
                details = company.find_all("div", {"class": "ml-auto"})

                ice = details[0].text.strip()
                if not "-" in ice: # If there is an ICE
                    if len(details)>4: #If there are +4 fields, we get all info
                        registre = details[1].text.strip().split(" ")[0]
                        id_fisc = details[2].text.strip()
                        date = details[3].text.strip()
                        active = details[4].text.strip()
                        write_in_excel(worksheet, line, company_name, ville, company_description, ice, registre, id_fisc, date, active)
                    else: #else we just get 3 fields
                        write_in_excel(worksheet, line, company_name, ville, company_description, ice, "-", "-", "-", "-")
                    line_index= line_index + 1
            page += 1
            time.sleep(0.5)
    i = i+1

workbook.close()