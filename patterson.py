from tqdm import tqdm
import pymongo
from lxml import etree
import io
import json
import asyncio
import aiohttp

loop = asyncio.new_event_loop()
client = pymongo.MongoClient("localhost", 27017)
db = client.medico
col = db.data2
col2 = db.patterson
col3 = db.henryschein
col4 = db.dentira
errors = []
urls = []
error_200 = []


async def get_data(url):

    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="utf-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)
        check = 10
        while check > 0:
            if raw_response.status == 200:
                parser = etree.HTMLParser(encoding="UTF-8")
                doc = etree.parse(io.StringIO(str(response_text)), parser)

                item = {}
                try:
                    item = json.loads(doc.xpath("//input[@id='ItemSkuDetail']/@value")[0])
                except:
                    pass
                try:
                    item['category'] = doc.xpath("//div[@class='catalogBreadcrumb']//*/a/text()")[0]
                except:
                    item['category'] = " "

                item['base_image_url'] = "https://content.pattersondental.com/items/LargeSquare/images/"
                col.insert_one(item)
                break
            else:
                check = check - 1
        if raw_response.status != 200:
            error_200.append(url)

    except:
        errors.append(url)


async def store_data(c):
    hen = col3.find({"ManufacturerItemNumber": c})[0]
    pat = col2.find({"ManufacturerItemNumber": c})[0]
    hen.pop("_id")
    pat.pop("_id")
    val = {}
    val['name_henryschein'] = hen['name']
    val['id_henryschein'] = hen['id_']
    val['data_henryschein'] = hen
    val['name_patterson'] = pat['ProductTitle']
    val['id_patterson'] = c
    val['data_patterson'] = pat
    col4.insert_one(val)


async def main(links):
    q = asyncio.Queue()
    # loop = asyncio.new_event_loop()
    producers = [loop.create_task(store_data(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()


if __name__ == "__main__":
    """
    with open("errors_patterson.txt", "r") as f:
        ff = f.read()
    urls = ff.split("\n")

    for i in tqdm(range(100, len(urls), 100)):
        loop.run_until_complete(main(urls[i:i + 100]))
    print(len(errors))
    print(len(error_200))

    with open("errors_patterson.txt", "w") as f:
        f.write("\n".join(errors))
    #with open("errors_200_patterson.txt", "w") as f:
    #    f.write("\n".join(error_200))
    """
    with open("common.txt") as f:
        js = f.read()
    f.close()

    ids = js.split("\n")
    for i in tqdm(range(0, len(ids), 100)):
        loop.run_until_complete(main(ids[i:i + 100]))











