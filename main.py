import requests
from bs4 import BeautifulSoup
import json
import re
from tqdm import tqdm
from fake_headers import Headers


HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'


def get_headers():
    return Headers(browser='chrome', os='linux').generate()


def vacancies_list(soup):
    vac_list = soup.find(
        class_='vacancy-serp-content').find_all(class_='serp-item')  # список вакансий
    vacancies = []
    for vac in tqdm(vac_list):
        parsed = vacancy_parsed(vac)
        vacancies.append(parsed)
    return vacancies


def vacancy_parsed(vac):
    my_list = []
    link = vac.find('a', class_='serp-item__title')['href']
    description_html = requests.get(
        link, headers=get_headers(), params={'only_with_salary': True}).text
    description_body = BeautifulSoup(
        description_html, features='lxml').find(class_='g-user-content').text
    # name = BeautifulSoup(
    #     description_html, features='lxml').find('a', class_='serp-item__title').text
    re_search = r'.*((D|d)jango)|.*((F|f)lask).*'
    if re.search(re_search, description_body):
        salary = vac.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}
                          ).text.replace('\u2009', '').replace('\xa0', ' ').replace('\u202f', ' ')
        city = vac.find(
            attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.replace('\xa0', '')
        company_name = vac.find('a', class_='bloko-link bloko-link_kind-tertiary',
                                attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text.replace('\xa0', ' ')
        result = {
            # 'name': name,
            'link': link,
            'city': city.split(',')[0],
            'company_name': company_name,
            'salary': salary
        }
        print(f'вакансия {company_name} {link} подходит')
        my_list.append(result)
        return result


if __name__ == '__main__':
    list_of_vac = []
    with open('vacancies.json', 'w') as f:
        for page in range(14, 20):
            print(f'Page {page} parsing:')
            html = requests.get(
                HOST, headers=get_headers(), params={'only_with_salary': True, 'page': page})
            html = html.text
            soup = BeautifulSoup(html, features='lxml')
            list_of_vac.extend(vacancies_list(soup))
        json.dump(list_of_vac, f, ensure_ascii=False, indent=4)