from tqdm import tqdm
import pymongo
from lxml import etree
import io
import json
import asyncio
import aiohttp

loop = asyncio.new_event_loop()
client = pymongo.MongoClient("localhost", 27017)
db = client.testdb
col = db.data
errors = []


async def get_data(url):
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="utf-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)
        all_h1 = doc.xpath("//h1//text()")
        """
        
        Scrapping code goes here
        
        At the end, either return the data or store it in pymongo or any other db. 
        """

    except:
        errors.append(url)


async def main(links):
    q = asyncio.Queue()
    producers = [loop.create_task(get_data(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()


if __name__ == "__main__":

    # Load all the urls.
    with open("urls.txt") as f:
        js = f.read()
    f.close()

    ids = js.split("\n")

    # Feed urls in group of 100 urls. This way, the scrapping code will make 100 concurrent requests to get data from
    # respective url. You can change this number according to your laptop speed and internet connectivity. A simple
    # trial and error approach could be used to find the most efficient number for your machine.
    for i in tqdm(range(0, len(ids), 100)):
        loop.run_until_complete(main(ids[i:i + 100]))

    print(f"Total {round((len(ids) - len(errors)) / len(ids),2)} Urls successfully scraped! Remaining urls are "
          f"stored in errors.txt file.")

    with open("errors.txt", "w") as f:
        f.write("\n".join(errors))
    f.close()











