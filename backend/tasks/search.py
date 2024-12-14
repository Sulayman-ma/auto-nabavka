import json
import logging
from rich import print
from typing import Any
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from curl_cffi import requests
from curl_cffi.requests import exceptions
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


from app.core.config import settings



def search_main(user: dict) -> Any:
    search_url = user['mobili_url']
    chat_id = user['chat_id']

    # Ads to be jsonified and returned by function
    ads: list[dict] = []

    # Request headers
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Priority': 'u=0, i',
        'Sec-Ch-Ua': '"Chromium";v="128", "Not;A=Brand";v="24", "DuckDuckGo";v="128"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    }

    page = 1
    while True:
        # Parse the existing URL
        parsed_url = urlparse(search_url)

        # Extract existing query parameters
        query_params = parse_qs(parsed_url.query)

        if page > 1:
            # Remove 'tag' parameter if page is greater than 1
            query_params.pop('tag', None)

            # Add city_distance=0 if page is greater than 1
            query_params['city_distance'] = ['0']
        
        # Add or update the 'page' parameter
        query_params['page'] = [str(page)]  # Ensure page is a string
        
        # Rebuild the URL with the updated query parameters
        paginated_url = urlunparse(
            parsed_url._replace(query=urlencode(query_params, doseq=True))
        )

        logging.debug(f"Searching page {page} with filters")
        try:
            response = requests.get(impersonate="chrome", url=paginated_url, headers=headers)
        except Exception as e:
            return f"Failed to fetch results page {page}: {str(e)}"

        # Parse response and search for results
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.select("article.classified")

        if not articles:
            break

        logging.debug(f"Found {len(articles)} ads for user: {chat_id} on page {page}")
        scripts = soup.find_all("script", {"type": "application/ld+json"})
        scripts = scripts[::2]
        for script in scripts:
            try:
                objects = json.loads(script.string)
                for data in objects:
                    try:
                        ad = {
                            'image': data['image'],
                            'name': data['name'].strip(),
                            'url': data['url'],
                            'production_date': data['productionDate'],
                        }
                        ads.append(ad)
                    except KeyError:
                        continue
            except IndexError:
                logging.warning("Failed to index result JSON")
                continue

        page += 1

    # No results found
    if not ads:
        return "No ads found"

    # Transform ads to caption only
    ads = [
        f"Name: {ad['name']}\nURL: {ad['url']}\nProduction Date: {ad['production_date']}"
        for ad in ads
    ]
    # Use API to send ads
    celery_auth = settings.CELERY_AUTH
    payload = {
        'celery_auth': celery_auth,
        'chat_id': chat_id,
        'ads': ads
    }
    try:
        res = requests.post(
            url="https://auto-nabavka.onrender.com/api/send-ads",
            # url="http://localhost:8000/api/send-ads",
            json=payload
        )
        return res.json()
    except exceptions.HTTPError as e:
        return str(e)


if __name__ == "__main__":
    # Logging configuration
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=logging.DEBUG
    )

    # Load environmental variables
    load_dotenv()

    search_main({
        'mobili_url': "https://www.polovniautomobili.com/auto-oglasi/pretraga?brand=&model%5B%5D=110&brand2=&price_from=&price_to=6000&year_from=&year_to=&flywheel=&atest=&region%5B%5D=2557&region%5B%5D=2554&door_num=&without_price=1&date_limit=&showOldNew=all&modeltxt=&engine_volume_from=&engine_volume_to=&power_from=&power_to=&mileage_from=&mileage_to=&emission_class=&seat_num=&wheel_side=&registration=&country=&country_origin=&city=&registration_price=&page=&sort=renewDate_desc&tag=true",
        'chat_id': 1234
    })
