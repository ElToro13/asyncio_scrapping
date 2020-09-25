from tqdm import tqdm
import pymongo
import json
import asyncio
import aiohttp

loop = asyncio.new_event_loop()
client = pymongo.MongoClient("localhost", 27017)
db = client.trn
col = db.euro
with open("codes.txt", "r") as f:
    js = f.read()
codes = eval(js)
errors = []
final = []
sector_name = {
    "indust": "Industrial Technologies",
    "funda" : "Fundamental Research",
    "trans" : "Transport and Mobility",
    "health" : "Health",
    "society": "Society",
    "secur" : "Security",
    "env" : "Climate Change and Environment",
    "ener": "Energy",
    "space": "Space",
    "ict": "Digital Economy",
    "agri": "Food and Natural Resources"
}

async def get_data(url):
    headers = {
        "Host": "cordis.europa.eu",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://cordis.europa.eu/search?q=contenttype%3D%27project%27%20AND%20applicationDomain%2Fcode%3D%27indust%27&p=2&num=10&srt=Relevance:decreasing",
        "Cookie": "PHPSESSID=2caafcff3c7b4b33c9c14855246d4112",
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, headers=headers) as raw_response:
                response_text = await raw_response.text()
        js = json.loads(response_text)
        item = {}
        try:
            item['Principal_Investigator'] = js['payload']['organizations']['coordinator'][0]['contacts'][0]['title'] + " " + \
                                             js['payload']['organizations']['coordinator'][0]['contacts'][0]['name']
        except:
            item['Principal_Investigator'] = " "

        try:
            item['ProjectID'] = js['payload']['information']['id']
        except:
            item['ProjectID'] = " "

        aI = []
        for name in js['payload']['organizations']['participants']:
            aI.append(name['name'])
        item['Project_AddInvestigators'] = aI

        try:
            item['Project_Area'] = sector_name[codes[url.split("rcn=")[-1].split("&")[0]].split("code=")[-1].split("&")[0]]
        except:
            item['Project_Area'] = " "

        try:
            item['Project_Location'] = js['payload']['organizations']['coordinator'][0]['name']
        except:
            item['Project_Location'] = " "

        try:
            item['Project_Name'] = js['payload']['information']['title']
        except:
            item['Project_Name'] = " "

        try:
            item['source_link'] = codes[url.split("rcn=")[-1].split("&")[0]]
        except:
            item['source_link'] = " "

        try:
            item['description'] = js['payload']['objective']['objective']
        except:
            item['description'] = " "

        try:
            item['fullName'] = item['Principal_Investigator']
        except:
            item['fullName'] = " "

        try:
            item['projectLink'] = url
        except:
            item['projectLink'] = " "

        try:
            item['status'] = "Ends: " + js['payload']['information']['endDateCode']
        except:
            item['status'] = " "
        col.insert_one(item)
    except:
        errors.append(url)


async def main(links):
    q = asyncio.Queue()
    # loop = asyncio.new_event_loop()
    producers = [loop.create_task(get_data(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()

if __name__ == "__main__":
    with open("errors.txt", "r") as f:
        ff = f.read()
    urls = ff.split("\n")
    # urls =["https://cordis.europa.eu/api/details?contenttype=project&rcn=323495&lang=en&paramType=id"]
    print(len(urls))
    for i in tqdm(range(0, len(urls), 100)):
        loop.run_until_complete(main(urls[i:i+100]))
    print(len(errors))

    #with open("proj.txt", "w") as e:
    #    e.write("\n".join(final))
    #e.close()

    with open("errors.txt", "w") as e:
        e.write("\n".join(errors))
    e.close()

    #with open("codes3.txt", "w") as e:
    #    e.write(str(codes))
    #e.close()










