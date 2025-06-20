from typing import List, Pattern
import posixpath
from urllib.parse import urlparse

from tldextract import tldextract
from w3lib.url import canonicalize_url
from loguru import logger as log

import httpx
from parsel import Selector
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests
import json
import time




def extract_urls(response: httpx.Response) -> List[str]:
    tree = Selector(text=response.text)
    # using XPath
    urls = tree.xpath('//a/@href').getall()
    # or CSS
    urls = tree.css('a::attr(href)').getall()
    # we should turn all relative urls to absolute, e.g. /foo.html to https://domain.com/foo.html
    urls = [urljoin(str(response.url), url.strip()) for url in urls]
    return urls

#[
#  "https://www.bbcgoodfood.com/recipes/collection/vegan-recipes",
#  "https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page=3",
#  "https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page=4",
  #"https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page=2",
  #"https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page=5",
  #"https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page=6"
#]
urlList=[]
count = 0
page = 1
stringcount = "count "
while page < 7:
    if page ==1:
        response = httpx.get("https://www.bbcgoodfood.com/recipes/collection/vegan-recipes")
    else:
        response = httpx.get("https://www.bbcgoodfood.com/recipes/collection/vegan-recipes?page="+str(page))
    for url in extract_urls(response):
        if "recipes" in url:
            if "category" and "howto" and "collection" and "guide" and "category" and "collections" not in url:
                urlList.append(url)
                count= count+1

    #print(stringcount+str(count))
    #print(page)

    page += 1

urlList=list(set(urlList))
urlList.sort()
#print(urlList)
#print(len(urlList))

json.dumps(urlList)
with open('listofurls.json', 'w', encoding='utf-8') as f:
     json.dump(urlList, f, ensure_ascii=False, indent=4)

def scrape_recipe(urlList):
    try:
        response = requests.get(urlList)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1').text.strip()

        # Ingredient elements (BBC Good Food uses <li class="pb-xxs"> inside <section id="recipe-ingredients">)
        ingredients_section = soup.find('section', id='ingredients-list')
        ingredients = []
        if ingredients_section:
            for li in ingredients_section.find_all('li', class_='ingredients-list__item list-item'):
                #print("hi1")
                ingredients.append(li.get_text(strip=True))
            for li in ingredients_section.find_all('li', class_='ingredients-list__item list-item list-item--separator-top'):
                #print("hi2")
                ingredients.append(li.get_text(strip=True))

        return {
            'title': title,
            'url': url,
            'ingredients': ingredients
        }

    except Exception as e:
        print(f"Failed to scrape {urlList}: {e}")
        return None

# Scrape all recipes
recipes = []
for url in urlList:
    recipe = scrape_recipe(url)
    if recipe:
        recipes.append(recipe)
    time.sleep(1)  # be polite to the server

# Save to JSON
with open("vegan_recipes.json", "w") as f:
    json.dump(recipes, f, indent=2)
