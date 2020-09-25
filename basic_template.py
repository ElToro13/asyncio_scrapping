from tqdm import tqdm
import pymongo
from lxml import etree
import io
import json
import asyncio
import aiohttp

loop = asyncio.new_event_loop()
client = pymongo.MongoClient("localhost", 27017)
errors = []

async def get_data(url):

    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="utf-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)
    except:
        errors.append(url)


async def main(links):
    q = asyncio.Queue()
    # loop = asyncio.new_event_loop()
    producers = [loop.create_task(get_data(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()


if __name__ == "__main__":
    with open("textfile.txt") as f:
        js = f.read()
    f.close()

    ids = js.split("\n")
    for i in tqdm(range(0, len(ids), 100)):
        loop.run_until_complete(main(ids[i:i + 100]))











