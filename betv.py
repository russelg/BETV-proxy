# This Python file uses the following encoding: utf-8
# BETV Proxy for japanese tv viewing.
from bottle import get, request, template, run
import requests
import xmltodict
import collections
import operator

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
reduce(operator.iadd, (x["channel"]
       for x in chn_doc if "channel" in x), chn)

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

for idx, channel in enumerate(chn):
    if not isinstance(channel, unicode):
        if korean_channels[channel["name"]] != "":
            name = channel["name"]
            channel["name"] = u"{} ({})".format(korean_channels[name], name)
            dict_xml["channels"]["group"][1]["channel"].append(channel)


def replace_url(request):
    headers = {}
    for x in dict(request.headers):
        if x != "Content-Length":
            headers[x] = dict(request.headers)[x].replace(
                'zzfdi.com', 'yyjbg.com')

    url = request.url.replace('zzfdi.com', 'yyjbg.com')

    return {"headers": headers, "url": url}


@get('/opsbetv/auth.action')
def auth_handler():
    info = replace_url(request)

    r = requests.get(
        info['url'], headers=info['headers'])

    return r.text


@get('/opsbetv/tv.action')
def channel_list():
    info = replace_url(request)

    return xmltodict.unparse(dict_xml)


@get('/opsbetv/tvitem.action')
def channel_list1():
    info = replace_url(request)

    r = requests.get(
        info['url'], headers=info['headers'])

    return r.text


@get('/opsbetv/pcad.action')
def channel_list1():
    info = replace_url(request)

    r = requests.get(
        info['url'], headers=info['headers'])

    return r.text

run(host='127.0.0.1', port=80, debug=True)
