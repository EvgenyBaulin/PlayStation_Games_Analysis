import requests
from bs4 import BeautifulSoup
import json


class DataParser:
    def __init__(self, url):
        self.url = url
        self.data = {}
        self.errors = False

    def fetch_html(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Не удалось загрузить сайт. Ошибка: {response.status_code}")
            self.errors = True
            return None

    def parse_html(self, html):
        if html:
            soup = BeautifulSoup(html, 'html.parser')

            title_element = soup.find('h1', {'data-qa': 'mfe-game-title#name'})
            title = title_element.text.strip() if title_element else "Title Not Found"

            platforms_elements = soup.find_all('span', class_ = 'psw-t-tag')
            platforms = list(
                set([span.text.strip() for span in platforms_elements if 'PS' in span.text]))

            rating_element = soup.find('div', {'data-qa': 'mfe-game-title#average-rating'})
            rating = self.parse_float(rating_element.text.strip()) if rating_element else 0.0

            developer_element = soup.find('dd', {
                'data-qa': 'gameInfo#releaseInformation#publisher-value'})
            developer = developer_element.text.strip() if developer_element else "Developer Not Found"

            release_date_element = soup.find('dd', {
                'data-qa': 'gameInfo#releaseInformation#releaseDate-value'})
            release_date = release_date_element.text.strip() if release_date_element else "Release Date Not Found"

            price_element = soup.find('span', {'data-qa': 'mfeCtaMain#offer0#finalPrice'})
            price = self.parse_price(
                price_element.text.strip()) if price_element else "Price Not Found"

            votes_element = soup.find('span',
                                      {'data-qa': 'mfe-star-rating#overall-rating#total-ratings'})
            votes_text = votes_element.text.strip().replace(' ratings', '').replace(' rating',
                                                                                    '') if votes_element else "0"
            votes = self.parse_votes(votes_text)

            genres_element = soup.find('dd', {'data-qa': 'gameInfo#releaseInformation#genre-value'})
            genres = genres_element.text.strip().split(', ') if genres_element else []

            self.data = {
                "title": title,
                "platforms": platforms,
                "rating": rating,
                "votes": votes,
                "developer": developer,
                "release_date": release_date,
                "price": price,
                "genres": genres,
            }

    def parse_votes(self, votes_text):
        try:
            if 'K' in votes_text:
                return int(float(votes_text.replace('K', '')) * 1000)
            elif 'M' in votes_text:
                return int(float(votes_text.replace('M', '')) * 1000000)
            else:
                return int(votes_text)
        except ValueError:
            self.errors = True
            return 0

    def parse_price(self, price_text):
        if 'Free' in price_text:
            return 0.0
        try:
            return float(price_text.replace('$', ''))
        except ValueError:
            self.errors = True
            return "Price Not Found"

    def parse_float(self, float_string):
        try:
            return float(float_string)
        except ValueError:
            self.errors = True
            return 0.0

    def append_data_to_json(self, filename = 'output.json'):
        if not self.errors:
            try:
                with open(filename, 'r', encoding = 'utf-8') as json_file:
                    existing_data = json.load(json_file)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = {}

            existing_data[self.url] = self.data

            with open(filename, 'w', encoding = 'utf-8') as json_file:
                json.dump(existing_data, json_file, ensure_ascii = False, indent = 4)
            # print(f"Добавлена игра {self.data['title']} в файл {filename}")

    def run(self):
        html = self.fetch_html()
        if html:
            self.parse_html(html)
            self.append_data_to_json()
