import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def word_to_number(self, number: str) -> int | None:
        words = ["One", "Two", "Three", "Four", "Five"]
        return words.index(number) + 1

    def parse_book(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p::text").get().replace("£", "")),
            "amount_in_stock": int(response.css("p.instock.availability::text").re_first(r"\d+")),
            "rating": self.word_to_number(response.css("p.star-rating::attr(class)").get().replace("star-rating ", "")),
            "category": response.css("ul.breadcrumb a::text").getall()[-1],
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("table.table-striped td::text").get(),
        }

    def parse(self, response: Response):
        for book in response.css(".product_pod"):
            yield response.follow(
                book.css("a::attr(href)").get(),
                callback=self.parse_book
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
