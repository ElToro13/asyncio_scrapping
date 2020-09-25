from tqdm import tqdm
import pymongo
from lxml import etree
import io
import asyncio
import aiohttp

loop = asyncio.new_event_loop()
client = pymongo.MongoClient("localhost", 27017)
db = client.trn
col = db.us
errors = []
urls = []


async def get_data(url):
    headers = {
        "Host": "projectreporter.nih.gov",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://projectreporter.nih.gov/reporter.cfm",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "99",
        "Origin": "https://projectreporter.nih.gov",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "ncbi_sid=8A1B5349F464F0C1_1779SID; pmc.article.report=; rxVisitor=159901868361580ENJ0U0PC5T1H8EEEFSCDRNAS3IJR3H; dtPC=2$18695989_937h-vPMBPKNBKBHFIFJACMRBVMHGAPLKOWACU-0; rxvt=1599074498934|1599072698934; dtSa=-; dtLatC=1; dtCookie=v_4_srv_2_sn_F5E0DF267FA30C09E7CFFC683D0C6BF2_perc_100000_ol_0_mul_1_app-3A01afd22cf2a961c1_1; JSESSIONID=744DF9B06CFEA89BA78991BFE5343463.RePORTER; CFID=28302527; CFTOKEN=14658150; REPORTERPORTFOLIO=""; RUPSID=71477365; TS017134cf=01f0618cebeec1af8ecc430e029639925e8cea98a062379aa81e7b1d4f8137c814ba6fc24e30808aaa21299e0b098fa54a59724679081fda09e0365072b3f32961f642a8c51f74f282df393e1cccdcfcc0357b3ded829461a9dfdf72cddcce2247c726fdbf; TS01d19e9d=01f0618ceba863ef20fc67359773c365925673925a0e63c6dfb94dcf8eccb7b5bc3e0d6d7ee34a5b6edb4682f58de74397842c99f36d117888d3fd726bcc2b8b667e6a530301dc7fe3fd55fd256cd15e800ce62d25ece5f2e6919d89c295d7f22428a9b924459e4890ae3c2974743165197310af3bec6f0d77fc59477860659ca562c7174a; mrExist; LIKEAID=""; REPORTERLF=""; REPORTERPAGING=sr%5Forderby%3Ddefault%7Csr%5Forder%3DASC%7Csr%5Fpagehit%3D25%7Csr%5Fstartrow%3D1%7Csr%5Fpagenum%3D1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, headers=headers) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="utf-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)
        if "project_info_description" in url:
            item = {}
            item['description'] = "".join(
                doc.xpath("//table[@class='proj_info_cont']/tbody/tr")[1].xpath(".//text()")).replace("\n", "").replace(
                "\t", "").replace("\r", "").strip()
            item['ProjectID'] = "".join(
                doc.xpath("//table[@summary='Details']/tbody/tr/td[2]")[0].xpath(".//text()")).replace("\n", "").replace("\t", "").replace("\r", "").strip()
            col.insert_one(item)
        else:
            item = {}
            try:
                item['Principal_Investigator'] = "".join(
                    doc.xpath("//table[@class='proj_info_cont']/tr")[1].xpath(".//td[1]/a[1]/text()")).replace("\n",
                                                                                                               "").replace(
                    "\r", "").replace("\t", "").strip()
            except:
                item['Principal_Investigator'] = " "

            try:
                item['ProjectID'] = "".join(
                    doc.xpath("//table[@summary='Details']/tbody/tr")[0].xpath(".//td[2]/text()")).replace("\n",
                                                                                                           "").replace("\r",
                                                                                                                       "").replace(
                    "\t", "").strip()
            except:
                item['ProjectID'] = " "

            try:
                item['Project_AddInvestigators'] = ["".join(
                    doc.xpath("//table[@summary='Project Leader Information']/tbody/tr")[0].xpath(
                        ".//td[3]//text()")).replace("\n", "").replace("\r", "").replace("\t", "").strip()]
            except:
                item['Project_AddInvestigators'] = " "

            try:
                item['Project_Area'] = "".join(
                    doc.xpath("//table[@summary='Project Leader Information']/tr")[5].xpath(".//td/span//text()")[
                    :-1]).strip()
            except:
                item['Project_Area'] = " "

            try:
                item['Project_Location'] = "".join(
                    doc.xpath("//table[@class='proj_info_cont']/tr")[3].xpath("./td[1]/text()")).replace("\n", "").replace(
                    "\r", "").replace("\t", "").replace("\xa0", "").strip()
            except:
                item['Project_Location'] = " "

            try:
                item['Project_Name'] = "".join(
                    doc.xpath("//table[@summary='Details']/tbody/tr")[-1].xpath("./td[2]//text()")).replace("\n",
                                                                                                            "").replace(
                    "\r", "").replace("\t", "").replace("\xa0", "").strip()
            except:
                item['Project_Name'] = " "

            item['description'] = ""

            try:
                item['fullName'] = item['Principal_Investigator']
            except:
                item['fullName'] = " "

            try:
                item['projectLink'] = ""
            except:
                item['projectLink'] = " "

            try:
                item['status'] = "".join([d.replace("\n", "").replace("\r", "").strip() for d in "".join(
                    doc.xpath("//table[@summary='Project Leader Information']/tr")[5].xpath(".//td[3]//text()")).split("\n")
                                          if "Project" in d])
            except:
                item['status'] = " "
    except:
        errors.append(url)


async def get_urls(fd):
    url = "https://projectreporter.nih.gov/reporter_searchresults.cfm"
    fdata = fd
    headers = {
        "Host": "projectreporter.nih.gov",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://projectreporter.nih.gov/reporter.cfm",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "888",
        "Origin": "https://projectreporter.nih.gov",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "ncbi_sid=8A1B5349F464F0C1_1779SID; pmc.article.report=; rxVisitor=159901868361580ENJ0U0PC5T1H8EEEFSCDRNAS3IJR3H; dtPC=2$18695989_937h-vPMBPKNBKBHFIFJACMRBVMHGAPLKOWACU-0; rxvt=1599074498934|1599072698934; dtSa=-; dtLatC=1; dtCookie=v_4_srv_2_sn_F5E0DF267FA30C09E7CFFC683D0C6BF2_perc_100000_ol_0_mul_1_app-3A01afd22cf2a961c1_1; JSESSIONID=744DF9B06CFEA89BA78991BFE5343463.RePORTER; CFID=28302527; CFTOKEN=14658150; REPORTERPORTFOLIO=""; RUPSID=71477365; TS017134cf=01f0618cebeec1af8ecc430e029639925e8cea98a062379aa81e7b1d4f8137c814ba6fc24e30808aaa21299e0b098fa54a59724679081fda09e0365072b3f32961f642a8c51f74f282df393e1cccdcfcc0357b3ded829461a9dfdf72cddcce2247c726fdbf; TS01d19e9d=01f0618ceba863ef20fc67359773c365925673925a0e63c6dfb94dcf8eccb7b5bc3e0d6d7ee34a5b6edb4682f58de74397842c99f36d117888d3fd726bcc2b8b667e6a530301dc7fe3fd55fd256cd15e800ce62d25ece5f2e6919d89c295d7f22428a9b924459e4890ae3c2974743165197310af3bec6f0d77fc59477860659ca562c7174a; mrExist; LIKEAID=""; REPORTERLF=""; REPORTERPAGING=sr%5Forderby%3Ddefault%7Csr%5Forder%3DASC%7Csr%5Fpagehit%3D25%7Csr%5Fstartrow%3D1%7Csr%5Fpagenum%3D1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(url=url, data=fdata, headers=headers) as raw_response:
                response_text = await raw_response.text()
        parser = etree.HTMLParser(encoding="UTF-8")
        doc = etree.parse(io.StringIO(str(response_text)), parser)

        divs = doc.xpath("//table[@id='main-table']/tbody/tr")
        for div in divs:
            val = {}
            try:
                urls.append("https://projectreporter.nih.gov/" +div.xpath(".//a[@title='Click to view Project  Details']/@href")[0])
                urls.append("https://projectreporter.nih.gov/" +div.xpath(".//a[@title='Click to view Project  Details']/@href")[0].replace("project_info_details", "project_info_description"))
            except:
                pass
    except:
        errors.append(fd)


async def main(links):
    q = asyncio.Queue()
    # loop = asyncio.new_event_loop()
    producers = [loop.create_task(get_urls(link)) for link in links]
    await asyncio.gather(*producers)
    await q.join()


if __name__ == "__main__":
    with open("fds.txt", "r") as f:
        ff = f.read()
    urls = ff.split("\n")

    loop.run_until_complete(main(['selRTE=&sr_pagehit=25&sr_pagetogo=2&sr_pagetogoBottom=3&api_applids=&sr_orderby=default&sr_order=ASC&sr_startrow=26&sr_pagenum=2&sr_maxpagenum=1145&sr_qsval=51517510&ddparam=&ddvalue=&ddsub=&hdnSelProjects=&hdnPagingtxt=1&pball=&hICDE=51517510&hsq=']))
    print(urls)
    #for i in tqdm(range(0, len(urls), 100)):
    #    loop.run_until_complete(main(urls[i:i + 100]))
    #print(len(errors))











