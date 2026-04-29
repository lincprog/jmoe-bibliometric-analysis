import time
from typing import List, Optional

from loguru import logger
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from requests_html import HTMLSession

# TODO: trocar manualmente ano, volume e numero
# TODO: pode pedir pra LLM pra salvar direto em csv. tá com mongo por causa da estrutura que eu ja tinha

XPATH_DATA = {
    "article_title": "//*[@id='standalonearticle']/section/div/div/h1",
    "article_authors": "/html/head/meta[@name='citation_author']/@content",
    "article_keywords": "//*[@id='articleText']/div[1]/p[2]",
    "article_abstract": "//*[@id='articleText']/div[1]/p[1]",
    "article_references": "//*[@id='articleText']/div/div/div/ul/li",
    "article_links": "//*[@id='issueIndex']/div/div[2]/table/tbody/tr/td/ul/li[2]/a/@href",
}


class ArticleCrawler:
    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "scielo_db",
        collection_name: str = "articles",
    ):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.collection.create_index("link", unique=True)
        self.session = HTMLSession()

    def _safe_find_element(self, r, xpath: str) -> Optional[str]:
        try:
            elements = r.html.xpath(xpath)
            if elements:
                return elements[0] if isinstance(elements[0], str) else elements[0].text
            return None
        except Exception as e:
            logger.warning(f"Error finding element with xpath {xpath}: {e}")
            return None

    def _safe_find_elements(self, r, xpath: str) -> List[str]:
        try:
            elements = r.html.xpath(xpath)
            return [
                elem.text if hasattr(elem, "text") else str(elem)
                for elem in elements
                if elem
            ]
        except Exception as e:
            logger.warning(f"Error finding elements with xpath {xpath}: {e}")
            return []

    def _extract_title(self, r) -> Optional[str]:
        title = self._safe_find_element(r, XPATH_DATA["article_title"])
        return title.strip() if title else None

    def _extract_authors(self, r) -> str:
        authors = r.html.xpath('//meta[@name="citation_author"]/@content')
        autores = [author.strip() for author in authors if author.strip()]
        return ", ".join(autores) if autores else ""

    def _extract_keywords(self, r) -> str:
        keywords = self._safe_find_elements(r, XPATH_DATA["article_keywords"])
        palavras_chave = [kw.strip() for kw in keywords if kw.strip()]
        return ", ".join(palavras_chave) if palavras_chave else ""

    def _extract_abstract(self, r) -> str:
        abstract = self._safe_find_element(r, XPATH_DATA["article_abstract"])
        return abstract.strip() if abstract else ""

    def _extract_references(self, r) -> str:
        references = self._safe_find_elements(r, XPATH_DATA["article_references"])
        referencias = [ref.strip() for ref in references if ref.strip()]
        return "\n".join(referencias) if referencias else ""

    def _get_page(
        self, url: str, timeout: int = 300, retries: int = 3, render: bool = False
    ):
        for attempt in range(retries):
            try:
                r = self.session.get(url, timeout=timeout)
                r.raise_for_status()
                if render:
                    r.html.render(timeout=20)
                return r
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2**attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    raise

    def _save_to_mongo(self, article: dict):
        try:
            self.collection.insert_one(article)
            logger.success(f"Saved to MongoDB: {article['link']}")
        except DuplicateKeyError:
            logger.info(f"Duplicate skipped: {article['link']}")

    def collect_article_links(self, edition_url: str) -> List[str]:
        article_links = []
        try:
            r = self._get_page(edition_url, render=True)
            links = r.html.xpath(XPATH_DATA["article_links"])
            for href in links:
                if href:
                    article_links.append("https://www.scielo.br" + href)
        except Exception as e:
            logger.error(f"Error collecting article links from {edition_url}: {e}")
        return article_links

    def parse_articles(self, article_urls: List[str]):
        parsed_counter = 0
        for i, url in enumerate(article_urls, start=1):
            try:
                logger.info(f"Parsing article {i}/{len(article_urls)}: {url}")
                r = self._get_page(url)
                time.sleep(1)
                parsed_article = {
                    "ano": "2025",  # TODO: Trocar manualmente
                    "volume": "24",  # TODO: Trocar manualmente
                    "numero": "1",  # TODO: Trocar manualmente
                    "titulo": self._extract_title(r),
                    "autores": self._extract_authors(r),
                    "palavras_chave": self._extract_keywords(r),
                    "abstract": self._extract_abstract(r),
                    "referencias": self._extract_references(r),
                    "link": url,
                }
                self._save_to_mongo(parsed_article)
                parsed_counter += 1
                yield parsed_article
            except Exception as e:
                logger.error(f"Error parsing article {url}: {e}")
                continue
        logger.success(f"Parsed {parsed_counter} of {len(article_urls)} articles.")

    def crawl_edition(self, edition_url: str):
        logger.info(f"Starting crawl for edition: {edition_url}")
        article_links = self.collect_article_links(edition_url)
        logger.info(f"Found {len(article_links)} articles in edition")
        articles = list(self.parse_articles(article_links))
        return articles

    def close(self):
        self.session.close()
        self.client.close()


if __name__ == "__main__":
    crawler = ArticleCrawler()
    try:
        edition_url = "https://www.scielo.br/j/jmoea/i/2025.v24n1/"  # TODO: trocar manualmente o link das edições
        articles = crawler.crawl_edition(edition_url)
        logger.info(f"Crawl completed. Total articles processed: {len(articles)}")
    finally:
        crawler.close()

