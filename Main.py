import os
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

url = 'https://www.indeed.com/jobs?'
site = 'https://www.indeed.com'
params = {
    'q':'Python Developer',
    'l':'New York State',
}

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

res = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(res.text,'html.parser')

def get_total_pages(query,location):
    params={
        'q' : query,
        'l' : location,

    }
    res = requests.get(url, params=params, headers=headers)

    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    with open('temp/res.html','w+',encoding="utf-8") as outfile:
        outfile.write(res.text,)
        outfile.close()

    total_pages = []
    #scraping step
    soup = BeautifulSoup(res.text,'html.parser')
    pagination = soup.find('ul','pagination-list')
    pages = pagination.find_all('li')
    for page in pages:
        total_pages.append(page.text)
    highest = int(max(total_pages))
    return highest

def get_all_items(query,location,start,page):

    params = {
        'q': query,
        'l': location,
        'start' : start,

    }
    res = requests.get(url, params=params, headers=headers)
    with open('temp/res.html','w+',encoding="utf-8") as outfile:
        outfile.write(res.text,)
        outfile.close()
    soup = BeautifulSoup(res.text, 'html.parser')
    job_list=[]
    contents=soup.find_all('table','jobCard_mainContent big6_visualChanges')
    for item in contents:
        title = item.find('h2','jobTitle').text
        company = item.find('span', 'companyName')
        company_name = company.text
        companyadd = item.find('div','companyLocation').text
        try:
            company_link = site + company.find('a')['href']
        except:
            company_link = 'Company link not available'
        try:
            salary = item.find('span', 'estimated-salary').text
        except:
            salary = 'Salary not available'
        data_dict={
            'Job Title' : title,
            'Company Name' : company_name,
            'Company Location' : companyadd,
            'Company Weblink' : company_link,
            'Salary' : salary
        }
        job_list.append(data_dict)
        #Create Json File
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass

    with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+', encoding='utf-8') as json_data:
        json.dump(job_list,json_data)

    return job_list

def create_document(dataFrame, filename):
    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    df = pd.DataFrame(dataFrame)
    df.to_csv(f'data_result/{filename}.csv', index=False)
    df.to_excel(f'data_result/{filename}.xlsx', index=False)
    print(f'{filename}.csv and {filename}.xlsx Created Succesfully')


def run():
    query = input('Input Job Title: ')
    location = input('Input Job Location: ')
    total = get_total_pages(query,location)
    counter=0
    total_data=[]
    for item in range(total):
        item += 1
        counter += 10
        total_data+=get_all_items(query, location, counter, item)


    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    with open('data_result/{}.json'.format(query), 'w+', encoding='utf-8') as json_data:
        json.dump(total_data, json_data)
    create_document(total_data,query+'_'+location)

if __name__ == '__main__':
    run()
