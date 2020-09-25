from lxml import etree
import requests
import aiohttp
import asyncio
import time
import io


loop = asyncio.get_event_loop()
errors = []


async def get_data(url):

    headers = {
        "Host": "www.dnb.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.dnb.com/business-directory/company-search.html?term=facebook&page=1",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="utf-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)
        print("".join(doc.xpath("//h1[@class='title']/text()")))
    except:
        errors.append(url)


async def main(links):
    q = asyncio.Queue()
    producers = [loop.create_task(get_data(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()

if __name__ == "__main__":
    s = time.perf_counter()

    urls = ["https://www.dnb.com/business-directory/company-profiles.alphabet_inc.81d5fd5ef421561d27e09c42d4991805.html",
            "https://www.dnb.com/business-directory/company-profiles.facebook_inc.fd6b4047a896c55afdb1a1330a52af1d.html",
            "https://www.dnb.com/business-directory/company-profiles.google_llc.f4ec1c3d05baae3ee36b8bd2f282b210.html",
            "https://www.dnb.com/business-directory/company-profiles.amazoncom_inc.1d6aec28aff542b40d3c2193a9a258f4.html"]
    loop.run_until_complete(main(urls))
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
