import os
import json
import httpx
import asyncio
import logging
from rich import print
from typing import Any
from telegram import Bot
from bs4 import BeautifulSoup
from curl_cffi import requests
from dotenv import load_dotenv



def search_main(user_data: dict[str, int | str]) -> Any:
    search_url = user_data['mobili_url']
    chat_id = user_data['chat_id']

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

    # Send request
    logging.debug(f"Searching with filters")
    try:
        response = requests.get(impersonate="chrome", url=search_url, headers=headers)
    except Exception as e:
        return f"Failed to fetch results page: {str(e)}"

    # Parse response and search for results 
    logging.debug("Parsing response content")
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.select("article.classified")

    # Parse results found for their image and contact
    logging.debug(f"Found {len(articles)} ads for user: {chat_id}")
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

    # No reuslts found
    if not articles:
        return "No ads found"

    # Bot token
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token)

    # Send single ads alone and exit
    # if len(ads) < 2:
    #     ad = ads[0]
    #     ad_string = f"Name: {ad['name']}\nURL: {ad['url']}\nProduction Date: {ad['production_date']}"
    #     res = asyncio.run(bot.send_message(chat_id=chat_id, text=ad_string))
    #     return res

    # Send ads in chunks of 10 as media galleries
    for i in range(0, len(ads), 20):
        group = ads[i:i + 20]
        for ad in group:
            try:
                caption=f"Name: {ad['name']}\nURL: {ad['url']}\nProduction Date: {ad['production_date']}"
                asyncio.run(bot.send_message(chat_id=chat_id, text=caption))
            except httpx.HTTPError as e:
                logging.error(f"Failed to send an ad: {str(e)}")
                continue
    return f"{len(ads)} ads sent to {chat_id}"


if __name__ == "__main__":
    # Logging configuration
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=logging.INFO
    )

    # Load environmental variables
    load_dotenv()

    search_main("https://www.polovniautomobili.com/auto-oglasi/pretraga?brand=baw", 1234)
