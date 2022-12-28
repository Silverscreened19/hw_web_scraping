import requests
from bs4 import BeautifulSoup
from pprint import pprint
from fake_headers import Headers
import json
import re
from tqdm import tqdm


HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'


def get_headers():
    return Headers(browser='opera', os='macos').generate()


def vacancies_list(soup):
    vac_list = soup.find(
        class_='vacancy-serp-content').find_all(class_='serp-item')  # список вакансий
    vacancies = []
    for vac in tqdm(vac_list):
        parsed = vacancy_parsed(vac)
        if parsed != None:
            vacancies.append(parsed)
    return vacancies


def vacancy_parsed(vac):
    link = vac.find('a', class_='serp-item__title')['href']
    description_html = requests.get(
        link, headers=get_headers(), params={'only_with_salary': True}).text
    description_body = BeautifulSoup(
        description_html, features='lxml').find(class_='g-user-content').text
    re_search = r'.*((D|d)jango)|.*((F|f)lask).*'
    currency = r'.*(USD).*'
    if re.search(re_search, description_body):
        salary = vac.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}
                          ).text.replace('\u2009', '').replace('\xa0', ' ').replace('\u202f', ' ')
        if re.search(currency, salary):
            city = vac.find(
                attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.replace('\xa0', '')
            company_name = vac.find('a', class_='bloko-link bloko-link_kind-tertiary',
                                    attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text.replace('\xa0', ' ')
            result = {
                'link': link,
                'city': city.split(',')[0],
                'company_name': company_name,
                'salary': salary
            }
            print(f'вакансия {company_name} {link} подходит')
            return result


if __name__ == '__main__':
    list_of_vac = []
    with open('vacancies_usd.json', 'w') as f:
        for page in range(0, 20):
            print(f'Page {page} parsing:')
            html = requests.get(
                HOST, headers=get_headers(), params={'only_with_salary': True, 'page': page})
            html = html.text
            soup = BeautifulSoup(html, features='lxml')
            list_of_vac.extend(vacancies_list(soup))
        json.dump(list_of_vac, f, ensure_ascii=False, indent=4)
