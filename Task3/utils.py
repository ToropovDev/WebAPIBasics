from typing import Optional
import requests
from bs4 import BeautifulSoup
import time


def get_html(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Ошибка при запросе {url}: {response.status_code}")
    except Exception as e:
        raise Exception(f"Ошибка подключения: {e}")


def parse_products(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    products = []
    product_cards = soup.find_all("article", class_="l-product")

    for card in product_cards:
        try:
            product_name = card.find("div", class_="l-product__name").a.text.strip()
            price_block = card.find("div", class_="l-product__price-base")
            product_price = price_block.text.strip()
            products.append({"name": product_name, "price": product_price})
        except AttributeError:
            continue

    return products


def get_next_page(soup: BeautifulSoup) -> Optional[str]:
    next_button = soup.find("a", class_="pagination-next")
    if next_button and "href" in next_button.attrs:
        return next_button["href"]
    return None


def scrape_category(current_url: str) -> (list, str):
    products = []
    category_name = ""

    while current_url:
        html = get_html(current_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            category_name = soup.find(
                "h1", class_="flypage__product-header"
            ).text.strip()

            page_products = parse_products(html)
            products.extend(page_products)

            next_page = get_next_page(soup)
            if next_page:
                current_url = next_page
                time.sleep(2)
            else:
                current_url = None
        else:
            break

    return products, category_name
