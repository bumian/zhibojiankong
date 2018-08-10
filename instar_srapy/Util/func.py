#!/usr/bin/env python
# coding: utf-8
import hashlib
import time
from requests.api import request
import socket
import logging

__author__ = 'Danny'

def get_host_name():
    """
    主机名md5
    :return:
    """
    host_name = socket.gethostname()
    return host_name

def md5(string):
    """
    md5加密
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()


def dic_merge(dic1, dic2):
    """
    合并dic
    :param dic1:
    :param dic2:
    :return: dic
    """
    return dict(dic1, **dic2)

def s_get(s_dic,s_key):
    """
    从dict中获取某一key的value
    :param dic1:
    :param key:
    :return: value
    """
    return s_dic.get(s_key,"")

def get_city(city_num):
    table = {
    "2630000":"中国",
    "2630100":"安徽",
    "2630101":"安庆",
    "2630102":"蚌埠",
    "2630103":"亳州",
    "2630104":"巢湖",
    "2630105":"池州",
    "2630106":"滁州",
    "2630107":"阜阳",
    "2630108":"淮北",
    "2630109":"合肥",
    "2630110":"淮南",
    "2630111":"黄山",
    "2630112":"六安",
    "2630113":"马鞍山",
    "2630114":"宿州",
    "2630115":"铜陵",
    "2630116":"芜湖",
    "2630117":"宣城",
    "2630200":"中国澳门",
    "2630201":"大堂区",
    "2630202":"氹仔",
    "2630203":"风顺堂区",
    "2630204":"花地玛堂区",
    "2630205":"路环岛",
    "2630206":"圣安多尼堂区",
    "2630207":"望德堂区",
    "2630300":"北京",
    "2630301":"昌平",
    "2630302":"朝阳",
    "2630303":"东城",
    "2630304":"大兴",
    "2630305":"房山",
    "2630306":"丰台",
    "2630307":"海淀",
    "2630308":"怀柔",
    "2630309":"门头沟",
    "2630310":"密云",
    "2630311":"平谷",
    "2630312":"石景山",
    "2630313":"顺义",
    "2630314":"通州",
    "2630315":"西城",
    "2630316":"延庆",
    "2630400":"重庆",
    "2630401":"北碚",
    "2630402":"巴南",
    "2630403":"璧山",
    "2630404":"城口",
    "2630405":"长寿",
    "2630406":"大渡口",
    "2630407":"垫江",
    "2630408":"大足",
    "2630409":"丰都",
    "2630410":"奉节",
    "2630411":"涪陵",
    "2630412":"合川",
    "2630413":"江北",
    "2630414":"江津",
    "2630415":"九龙坡",
    "2630416":"开县",
    "2630417":"两江新区",
    "2630418":"梁平",
    "2630419":"南岸",
    "2630420":"南川",
    "2630421":"彭水",
    "2630422":"綦江",
    "2630423":"黔江",
    "2630424":"荣昌",
    "2630425":"沙坪坝",
    "2630426":"双桥",
    "2630427":"石柱",
    "2630428":"铜梁",
    "2630429":"潼南",
    "2630430":"武隆",
    "2630431":"万盛",
    "2630432":"巫山",
    "2630433":"巫溪",
    "2630434":"万州",
    "2630435":"秀山",
    "2630436":"渝北",
    "2630437":"永川",
    "2630438":"云阳",
    "2630439":"酉阳",
    "2630440":"渝中",
    "2630441":"忠县",
    "2630500":"福建",
    "2630501":"福州",
    "2630502":"龙岩",
    "2630503":"宁德",
    "2630504":"南平",
    "2630505":"莆田",
    "2630506":"泉州",
    "2630507":"三明",
    "2630508":"厦门",
    "2630509":"漳州",
    "2630600":"广东",
    "2630601":"潮州",
    "2630602":"东莞",
    "2630603":"佛山",
    "2630604":"广州",
    "2630605":"河源",
    "2630606":"惠州",
    "2630607":"江门",
    "2630608":"揭阳",
    "2630609":"茂名",
    "2630610":"梅州",
    "2630611":"清远",
    "2630612":"韶关",
    "2630613":"汕头",
    "2630614":"汕尾",
    "2630615":"深圳",
    "2630616":"云浮",
    "2630617":"阳江",
    "2630618":"珠海",
    "2630619":"湛江",
    "2630620":"肇庆",
    "2630621":"中山",
    "2630700":"甘肃",
    "2630701":"白银",
    "2630702":"定西",
    "2630703":"甘南",
    "2630704":"金昌",
    "2630705":"酒泉",
    "2630706":"嘉峪关",
    "2630707":"陇南",
    "2630708":"临夏",
    "2630709":"兰州市",
    "2630710":"平凉",
    "2630711":"庆阳",
    "2630712":"天水",
    "2630713":"武威",
    "2630714":"张掖",
    "2630800":"广西",
    "2630801":"北海",
    "2630802":"百色",
    "2630803":"崇左",
    "2630804":"防城港",
    "2630805":"贵港",
    "2630806":"桂林",
    "2630807":"河池",
    "2630808":"贺州",
    "2630809":"来宾",
    "2630810":"柳州",
    "2630811":"南宁",
    "2630812":"钦州",
    "2630813":"梧州",
    "2630814":"玉林",
    "2630900":"贵州",
    "2630901":"安顺",
    "2630902":"毕节",
    "2630903":"贵阳",
    "2630904":"六盘水",
    "2630905":"黔东南",
    "2630906":"黔南",
    "2630907":"黔西南",
    "2630908":"铜仁",
    "2630909":"遵义",
    "2631000":"湖北",
    "2631001":"恩施",
    "2631002":"鄂州",
    "2631003":"黄冈",
    "2631004":"黄石",
    "2631005":"荆门",
    "2631006":"荆州",
    "2631007":"潜江",
    "2631008":"神农架",
    "2631009":"十堰",
    "2631010":"随州",
    "2631011":"天门",
    "2631012":"武汉",
    "2631013":"孝感",
    "2631014":"咸宁",
    "2631015":"仙桃",
    "2631016":"襄阳",
    "2631017":"宜昌",
    "2631100":"河北",
    "2631101":"保定",
    "2631102":"承德",
    "2631103":"沧州",
    "2631104":"邯郸",
    "2631105":"衡水",
    "2631106":"廊坊",
    "2631107":"秦皇岛",
    "2631108":"石家庄",
    "2631109":"唐山",
    "2631110":"邢台",
    "2631111":"张家口",
    "2631200":"黑龙江",
    "2631201":"大庆",
    "2631202":"大兴安岭",
    "2631203":"哈尔滨",
    "2631204":"鹤岗",
    "2631205":"黑河",
    "2631206":"佳木斯",
    "2631207":"鸡西",
    "2631208":"牡丹江",
    "2631209":"齐齐哈尔",
    "2631210":"七台河",
    "2631211":"绥化",
    "2631212":"双鸭山",
    "2631213":"伊春",
    "2631300":"湖南",
    "2631301":"常德",
    "2631302":"长沙",
    "2631303":"郴州",
    "2631304":"怀化",
    "2631305":"衡阳",
    "2631306":"娄底",
    "2631307":"邵阳",
    "2631308":"湘潭",
    "2631309":"湘西",
    "2631310":"益阳",
    "2631311":"岳阳",
    "2631312":"永州",
    "2631313":"张家界",
    "2631314":"株洲",
    "2631400":"河南",
    "2631401":"安阳",
    "2631402":"鹤壁",
    "2631403":"济源",
    "2631404":"焦作",
    "2631405":"开封",
    "2631406":"漯河",
    "2631407":"洛阳",
    "2631408":"南阳",
    "2631409":"平顶山",
    "2631410":"濮阳",
    "2631411":"三门峡",
    "2631412":"商丘",
    "2631413":"许昌",
    "2631414":"新乡",
    "2631415":"信阳",
    "2631416":"周口",
    "2631417":"驻马店",
    "2631418":"郑州",
    "2631500":"海南",
    "2631501":"白沙",
    "2631502":"保亭",
    "2631503":"昌江",
    "2631504":"澄迈",
    "2631505":"定安",
    "2631506":"东方",
    "2631507":"儋州",
    "2631508":"海口",
    "2631509":"乐东",
    "2631510":"临高",
    "2631511":"陵水",
    "2631512":"南沙",
    "2631513":"琼海",
    "2631514":"琼中",
    "2631515":"三亚",
    "2631516":"屯昌",
    "2631517":"文昌",
    "2631518":"万宁",
    "2631519":"五指山",
    "2631520":"西沙",
    "2631521":"中沙",
    "2631600":"吉林",
    "2631601":"白城",
    "2631602":"白山",
    "2631603":"长春",
    "2631604":"吉林",
    "2631605":"辽源",
    "2631606":"四平",
    "2631607":"松原",
    "2631608":"通化",
    "2631609":"延边",
    "2631700":"江苏",
    "2631701":"常州",
    "2631702":"淮安",
    "2631703":"连云港",
    "2631704":"南京",
    "2631705":"南通",
    "2631706":"宿迁",
    "2631707":"苏州",
    "2631708":"泰州",
    "2631709":"无锡",
    "2631710":"徐州",
    "2631711":"盐城",
    "2631712":"扬州",
    "2631713":"镇江",
    "2631800":"江西",
    "2631801":"抚州",
    "2631802":"赣州",
    "2631803":"吉安",
    "2631804":"景德镇",
    "2631805":"九江",
    "2631806":"南昌",
    "2631807":"萍乡",
    "2631808":"上饶",
    "2631809":"新余",
    "2631810":"宜春",
    "2631811":"鹰潭",
    "2631900":"辽宁",
    "2631901":"鞍山",
    "2631902":"本溪",
    "2631903":"朝阳",
    "2631904":"丹东",
    "2631905":"大连",
    "2631906":"抚顺",
    "2631907":"阜新",
    "2631908":"葫芦岛",
    "2631909":"锦州",
    "2631910":"辽阳",
    "2631911":"盘锦",
    "2631912":"沈阳",
    "2631913":"铁岭",
    "2631914":"营口",
    "2632000":"内蒙古",
    "2632001":"阿拉善",
    "2632002":"包头",
    "2632003":"巴彦淖尔",
    "2632004":"赤峰",
    "2632005":"鄂尔多斯",
    "2632006":"呼和浩特",
    "2632007":"呼伦贝尔",
    "2632008":"通辽",
    "2632009":"乌海",
    "2632010":"乌兰察布",
    "2632011":"兴安",
    "2632012":"锡林郭勒",
    "2632100":"宁夏",
    "2632101":"固原",
    "2632102":"石嘴山",
    "2632103":"吴忠",
    "2632104":"银川",
    "2632105":"中卫",
    "2632200":"青海",
    "2632201":"果洛",
    "2632202":"海北",
    "2632203":"海东",
    "2632204":"黄南",
    "2632205":"海南",
    "2632206":"海西",
    "2632207":"西宁",
    "2632208":"玉树",
    "2632300":"四川",
    "2632301":"阿坝",
    "2632302":"巴中",
    "2632303":"成都",
    "2632304":"德阳",
    "2632305":"达州",
    "2632306":"广安",
    "2632307":"广元",
    "2632308":"甘孜",
    "2632309":"凉山",
    "2632310":"乐山",
    "2632311":"泸州",
    "2632312":"眉山",
    "2632313":"绵阳",
    "2632314":"南充",
    "2632315":"内江",
    "2632316":"攀枝花",
    "2632317":"遂宁",
    "2632318":"雅安",
    "2632319":"宜宾",
    "2632320":"自贡",
    "2632321":"资阳",
    "2632400":"山东",
    "2632401":"滨州",
    "2632402":"东营",
    "2632403":"德州",
    "2632404":"菏泽",
    "2632405":"济南",
    "2632406":"济宁",
    "2632407":"聊城",
    "2632408":"莱芜",
    "2632409":"临沂",
    "2632410":"青岛",
    "2632411":"日照",
    "2632412":"泰安",
    "2632413":"潍坊",
    "2632414":"威海",
    "2632415":"烟台",
    "2632416":"淄博",
    "2632417":"枣庄",
    "2632500":"上海",
    "2632501":"宝山",
    "2632502":"崇明",
    "2632503":"长宁",
    "2632504":"奉贤",
    "2632505":"虹口",
    "2632506":"黄浦",
    "2632507":"静安",
    "2632508":"嘉定",
    "2632509":"金山",
    "2632510":"卢湾",
    "2632511":"闵行",
    "2632512":"浦东新区",
    "2632513":"普陀",
    "2632514":"青浦",
    "2632515":"松江",
    "2632516":"徐汇",
    "2632517":"杨浦",
    "2632518":"闸北",
    "2632600":"陕西",
    "2632601":"安康",
    "2632602":"宝鸡",
    "2632603":"汉中",
    "2632604":"商洛",
    "2632605":"铜川",
    "2632606":"渭南",
    "2632607":"西安",
    "2632608":"咸阳",
    "2632609":"延安",
    "2632610":"榆林",
    "2632700":"山西",
    "2632701":"长治",
    "2632702":"大同",
    "2632703":"晋城",
    "2632704":"晋中",
    "2632705":"临汾",
    "2632706":"吕梁",
    "2632707":"朔州",
    "2632708":"太原",
    "2632709":"忻州",
    "2632710":"运城",
    "2632711":"阳泉",
    "2632800":"天津",
    "2632801":"北辰",
    "2632802":"宝坻",
    "2632803":"滨海新区",
    "2632804":"东丽",
    "2632805":"河北",
    "2632806":"河东",
    "2632807":"和平",
    "2632808":"红桥",
    "2632809":"河西",
    "2632810":"静海",
    "2632811":"津南",
    "2632812":"蓟县",
    "2632813":"宁河",
    "2632814":"南开",
    "2632815":"武清",
    "2632816":"西青",
    "2632900":"中国台湾",
    "2632901":"高雄市",
    "2632902":"花莲县",
    "2632903":"基隆市",
    "2632904":"金门县",
    "2632905":"嘉义市",
    "2632906":"嘉义县",
    "2632907":"连江县",
    "2632908":"苗栗县",
    "2632909":"南投县",
    "2632910":"屏东县",
    "2632911":"澎湖县",
    "2632912":"台北市",
    "2632913":"台东县",
    "2632914":"台南市",
    "2632915":"桃园县",
    "2632916":"台中市",
    "2632917":"新北市",
    "2632918":"新竹市",
    "2632919":"新竹县",
    "2632920":"云林县",
    "2632921":"宜兰县",
    "2632922":"彰化县",
    "2633000":"西藏",
    "2633001":"阿里",
    "2633002":"昌都",
    "2633003":"拉萨",
    "2633004":"林芝",
    "2633005":"那曲",
    "2633006":"日喀则",
    "2633007":"山南",
    "2633100":"中国香港",
    "2633101":"北区",
    "2633102":"大埔区",
    "2633103":"东区",
    "2633104":"观塘区",
    "2633105":"黄大仙区",
    "2633106":"九龙城区",
    "2633107":"葵青区",
    "2633108":"离岛区",
    "2633109":"南区",
    "2633110":"荃湾区",
    "2633111":"深水埗区",
    "2633112":"沙田区",
    "2633113":"屯门区",
    "2633114":"湾仔区",
    "2633115":"西贡区",
    "2633116":"油尖旺区",
    "2633117":"元朗区",
    "2633118":"中西区",
    "2633200":"新疆",
    "2633201":"阿克苏",
    "2633202":"阿拉尔",
    "2633203":"阿勒泰",
    "2633204":"博尔塔拉",
    "2633205":"巴音郭楞",
    "2633206":"昌吉",
    "2633207":"哈密",
    "2633208":"和田",
    "2633209":"克拉玛依",
    "2633210":"喀什",
    "2633211":"克孜勒苏",
    "2633212":"石河子",
    "2633213":"塔城",
    "2633214":"吐鲁番",
    "2633215":"图木舒克",
    "2633216":"五家渠",
    "2633217":"乌鲁木齐",
    "2633218":"伊犁",
    "2633300":"云南",
    "2633301":"保山",
    "2633302":"楚雄",
    "2633303":"德宏",
    "2633304":"大理",
    "2633305":"迪庆",
    "2633306":"红河",
    "2633307":"昆明",
    "2633308":"临沧",
    "2633309":"丽江",
    "2633310":"怒江",
    "2633311":"普洱",
    "2633312":"曲靖",
    "2633313":"文山",
    "2633314":"西双版纳",
    "2633315":"玉溪",
    "2633316":"昭通",
    "2633400":"浙江",
    "2633401":"湖州",
    "2633402":"杭州",
    "2633403":"金华",
    "2633404":"嘉兴",
    "2633405":"丽水",
    "2633406":"宁波",
    "2633407":"衢州",
    "2633408":"绍兴",
    "2633409":"台州",
    "2633410":"温州",
    "2633411":"舟山"
    }
    if str(city_num) == "0":
        return "在火星"
    return table.get(str(city_num),"海外")

def s_int(s_count):
    """
    转换带有中文单位的数字,如1.2亿
    :param str:
    :return: int
    """
    if not s_count:
        return 0

    s_count = str(s_count)
    cn_unit = {
        '\xe5\x8d\x81\xe4\xb8\x87': 100000,
        '\xe7\x99\xbe\xe4\xb8\x87': 1000000,
        '\xe5\x8d\x83\xe4\xb8\x87': 10000000,
        '\xe5\x8d\x81\xe4\xba\xbf': 1000000000,
        '\xe7\x99\xbe\xe4\xba\xbf': 10000000000,
        '\xe5\x8d\x81': 10,
        '\xe7\x99\xbe': 100,
        '\xe5\x8d\x83': 1000,
        '\xe4\xb8\x87': 10000,
        '\xe4\xba\xbf': 100000000,
        '\xe5\x85\x86': 1000000000000
    }
    s_count = s_count.encode('utf8')
    for key,value in cn_unit.items():
        if key in s_count:
            index = len(key)
            count = float(s_count[0:-index])
            return int(count * value)
    return int(s_count)


def cache_key():
    return time.strftime("%H%M", time.localtime())


def current_time():
    """
    当前时间
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def s_request(url,method='GET',retry=1,**param):
    """
    带有代理和重试的request
    :param url:
    :param method:
    :param params:
    :return: res
    """
    res = ""
    error=""
    self_timeout = 3 if retry == 1 else 10
    proxy_timeout = 3 if retry == 1 else 10
    proxy = {"http":"proxy.instarx.net:8080"}
    proxy2 = {"http":"proxy.instarx.net:8081"}
    config = {
        'timeout': param.get("timeout",proxy_timeout),
        'proxies': param.get("proxies",proxy)
    }
    config2 = {
	    'timeout': proxy_timeout,
        'proxies': proxy2
    }

    param1 = dict(config, **param)
    param2 = dict(config2, **param)
    pram_list = [param1,param2]
    for i in range(0,retry):
        s_param = pram_list[i]
        try:
            res =  request(method,url,**s_param)
            if str(res.status_code) in ["200","400"] :
                error = "proxy" + str(i + 1) + " code:" + str(res.status_code)
                return error,res
        except:
            continue
    try:
        res =  request(method,url,timeout=self_timeout,**param)
    except Exception,e:
        error = "local code:"+str(e)
    else:
        error = "local code:"+str(res.status_code)
    return error,res

def s_check(error,res,platform,api,log):
        res_json = ""
        message = {
            "platform" : platform,
            "api" : api,
            "error": error
        }

        if not res:
            log.error("{platform} {api},network error:{error}".format(**message))
            return res_json

        try:
            res_json = res.json()
        except:
            log.error("{platform} {api},error:no json".format(**message))

        return res_json