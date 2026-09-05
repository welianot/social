import re
import httpx
from bs4 import BeautifulSoup


async def fetch_affiliate_product(url: str) -> dict:
    """Fetch product metadata from Amazon/Flipkart URL via OG tags."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    def og(prop: str) -> str | None:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return tag["content"] if tag and tag.get("content") else None

    title = og("og:title") or soup.title.string if soup.title else None
    image = og("og:image")
    price = _extract_price(soup, url)

    source = "amazon" if "amazon" in url else "flipkart" if "flipkart" in url else "other"

    return {
        "title": title,
        "image_url": image,
        "price_cents": price,
        "affiliate_url": url,
        "affiliate_source": source,
        "affiliate_meta": {"raw_url": url},
    }


def _extract_price(soup: BeautifulSoup, url: str) -> int | None:
    price_text = None
    if "amazon" in url:
        tag = soup.find("span", class_=re.compile(r"a-price-whole"))
        price_text = tag.get_text(strip=True) if tag else None
    elif "flipkart" in url:
        tag = soup.find("div", class_=re.compile(r"_30jeq3"))
        price_text = tag.get_text(strip=True) if tag else None

    if not price_text:
        return None
    digits = re.sub(r"[^\d.]", "", price_text)
    try:
        return int(float(digits) * 100)
    except ValueError:
        return None


def inject_affiliate_tag(url: str, amazon_tag: str, flipkart_id: str) -> str:
    if "amazon" in url and amazon_tag:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}tag={amazon_tag}"
    if "flipkart" in url and flipkart_id:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}affid={flipkart_id}"
    return url
