# This Python file uses the following encoding: utf-8
# BETV Proxy for japanese tv viewing.
from bottle import get, request, template, run
import requests
import xmltodict
import collections
import operator
import sys
import shutil
import logging

logging.basicConfig(format="  %(levelname)-2s | %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)

logging.info("BETV Proxy Starting...")

if "update" not in sys.argv:
    # Channel mapping for Korean channels (mostly correct?)
    korean_channels = {
        u"CCTV5+体育赛事": "OCN",
        u"CCTV5体育频道": "JTBC",
        u"STAR SPORTS": "",
        u"CCTV风云足球": "KBS drama HD",
        u"欧洲足球": "MBC",
        u"劲爆体育": "",
        u"高尔夫网球": "KBS 1",
        u"CCTV13新闻频道": "KBS 2",
        u"鳳凰衛視資訊臺": "SBS",
        u"鳳凰衛視中文臺": "YTN",
        u"CNN": "",
        u"BBC": "KBS N SPORTS",
        u"浙江卫视高清": "TV N",
        u"CCTV1综合频道": "SBS Plus",
        u"湖南卫视高清": "EBS 1",
        u"江苏卫视高清": "MBC Drama",
        u"CCTV3综艺频道": "",
        u"东方卫视高清": "",
        u"北京卫视高清": "MBC",
        u"广东卫视高清": "",
        u"黑龙江卫视高清": "SBS Golf",
        u"CCTV11戏曲频道": "J Golf HD",
        u"浙江卫视高清": "",
        u"CCTV1综合频道": "SBS Plus",
        u"湖南卫视高清": "",
        u"CCTV6电影频道": "",
        u"HBO": "",
        u"CCTV4中文国际频道": "TV N",
        u"國家地理": "",
        u"探索頻道": "",
        u"CCTV10科教频道": "MBS SPORTS",
        u"CCTV12社会与法频道": "SBS Sports",
        u"CCTV2财经频道": "KBS2",
        u"第一财经": "KBS N SPORTS",
        u"CCTV14少儿频道": "KBS1"
    }

    xmldoc_jp = xmltodict.parse(open('jp_response.xml'))
    xmldoc_cn = xmltodict.parse(open('chn_response.xml'))

    jp = xmldoc_jp["groups"]["group"]["channel"]
    chn_doc = [y for y in xmldoc_cn["channels"]["group"]]
    chn = []
    # Do some magic to flatten the chinese channel XML.
    reduce(operator.iadd, (x["channel"]
           for x in chn_doc if "channel" in x), chn)

    # XML to be constructed
    dict_xml = {
        "channels": {
            "@version": "",
            "@info_time": "",
            "@adsurl": "",
            "group": [
                {
                    "@id": "1",
                    "@type": "1",
                    "@name": "Japanese",
                    "@description": "Japanese",
                    "@deploy": "0",
                    "channel": []
                },
                {
                    "@id": "2",
                    "@type": "1",
                    "@name": "Korean",
                    "@description": "Korean",
                    "@deploy": "0",
                    "channel": []
                }
            ]
        }
    }

    # Add all the Japanese channels
    for idx, channel in enumerate(jp):
        formed_channel = collections.OrderedDict((
            ("name", channel["name"]),
            ("id", idx + 1),
            ("status", "1"),
            ("vip", "0"),
            ("sop_address", {
                "item": channel["sop_address"]["item"]
            }),
            ("description", ""),
            ("logo", "")
        ))
        dict_xml["channels"]["group"][0]["channel"].append(formed_channel)

    # Parse the chinese XML for the Korean channels
    for idx, channel in enumerate(chn):
        if not isinstance(channel, unicode):
            if korean_channels[channel["name"]] != "":
                name = channel["name"]
                channel["name"] = u"{} ({})".format(
                    korean_channels[name], name)
                dict_xml["channels"]["group"][1]["channel"].append(channel)

    # Replaces the default URL with an alternative, since
    # the host file will not allow the main domain to be reached. (we're using
    # it)
    def replace_url(request):
        headers = {}
        for x in dict(request.headers):
            if x != "Content-Length":
                headers[x] = dict(request.headers)[x].replace(
                    'zzfdi.com', 'yyjbg.com')

        url = request.url.replace('zzfdi.com', 'yyjbg.com')

        return {"headers": headers, "url": url}

    # Just passes a request to the original service.
    def proxy(request):
        info = replace_url(request)

        r = requests.get(
            info['url'], headers=info['headers'])

        return r.text

    # Just plain forward auth request.
    @get('/opsbetv/auth.action')
    def auth_handler():
        info = replace_url(request)

        r = requests.get(
            info['url'], headers=info['headers'])

        return r.text

    # Respond with our own XML for the channel list.
    @get('/opsbetv/tv.action')
    def channel_list():
        info = replace_url(request)

        return xmltodict.unparse(dict_xml)

    # Forward this request (useless it seems, unless someone can prove
    # otherwise)
    @get('/opsbetv/tvitem.action')
    def channel_list1():
        return proxy(request)

    # Also useless.
    @get('/opsbetv/pcad.action')
    def channel_list1():
        return proxy(request)

if __name__ == "__main__":
    if "update" in sys.argv:
        logger.info("Updating XML...")

        # BETV config grab
        auth = requests.get(
            "http://pclist.yyjbg.com/opsbetv/auth.action?type=1&ack=0000007400010000000000000075")
        uuid = xmltodict.parse(auth.text)["Auth"]["Uuid"]
        chn_xml = requests.get(
            "http://pclist.yyjbg.com/opsbetv/tv.action?type=1&uuid={0}".format(uuid), headers={"User-Agent": "BETV"}, stream=True)

        if chn_xml.status_code == 200:
            with open("chn_response.xml", 'wb') as f:
                chn_xml.raw.decode_content = True
                shutil.copyfileobj(chn_xml.raw, f)
                logger.info("BETV response saved")

        # NIJI config grab
        niji = requests.get(
            "http://nebox.myniji.tv:7006/xml/tv1/2/tv.xml", stream=True)

        if niji.status_code == 200:
            with open("jp_response.xml", 'wb') as f:
                niji.raw.decode_content = True
                shutil.copyfileobj(niji.raw, f)
                logger.info("NIJI response saved")
    else:
        run(host='127.0.0.1', port=80, debug=False)
