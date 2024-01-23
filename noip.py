#!/usr/bin/env python

# coding:utf-8
# 20240122
import base64
import requests
import numpy as np
import time

username = 'your Enail'
password = 'your password'
time_interval = 30  # 时间间隔(分钟)
hostname = 'your noip.com domain'  # DDNS主机名
user_agent = 'no-ip shell script/1.0 mail@mail.com'
noip_host = 'https://dynupdate.no-ip.com/nic/update?'  # noip接口地址
icanhaz_probe_v4 = 'https://ipv4.icanhazip.com/'  # ipv4探针地址
icanhaz_probe_v6 = 'https://ipv6.icanhazip.com/'  # ipv6探针地址
ipw_probe_v4 = 'https://4.ipw.cn/'  # ipv4探针地址
ipw_probe_v6 = 'https://6.ipw.cn/'  # ipv6探针地址
np.random.seed(2024)  # 随机数种子


def getIP():
    ip_v4 = ip_v6 = None
    probes = [(icanhaz_probe_v4, ipw_probe_v6), (ipw_probe_v4, icanhaz_probe_v6)]
    probe_v4, probe_v6 = probes[np.random.randint(0, 2)]
    try:
        ip_v4 = requests.get(probe_v4).text
    except requests.exceptions.ConnectionError:
        ip_v4 = None
    except requests.exceptions.URLRequired:
        print('ip探针地址设置错误')

    try:
        ip_v6 = requests.get(probe_v6).text
    except requests.exceptions.ConnectionError:
        ip_v6 = None
    except requests.exceptions.URLRequired:
        print('ip探针地址设置错误')

    return ','.join(filter(None, [ip_v4, ip_v6])).replace("\n", "")


def updateIP(my_ip):
    base64_encoded_auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        'Authorization': f"Basic {base64_encoded_auth_string}",
        'User-Agent': user_agent
    }
    try:
        res = requests.get(noip_host + 'hostname=' + hostname + '&myip=' + my_ip, headers=headers)
        error_status = ['nohost', 'badauth', 'badagent', '!donator', 'abuse']
        if res.text in error_status:
            print(res.text)
            return False
        elif res.text == '911':
            print('noip 911,30分钟后重试')
            time.sleep(1801)
            return updateIP(my_ip)
        else:
            print(res.text)
            return True
    except requests.exceptions.ConnectionError:
        print('与noip连接失败')
        time.sleep(600)
        return updateIP(my_ip)
    except requests.exceptions.Timeout:
        print('连接超时')
        time.sleep(600)
        return updateIP(my_ip)
    except Exception as e:
        print(f'未知异常{e}')
        return False


if __name__ == '__main__':
    current_ip = ''
    while True:
        try:
            new_ip = getIP()
        except Exception as e:
            print(f'获取ip失败{e}')
            continue
        if current_ip != new_ip:
            print(f'新ip:{new_ip}, 正在更新ddns')
            current_ip = new_ip
            result = updateIP(new_ip)
            if result is False:
                break
        else:
            print('ip未发生变化')
        time.sleep(time_interval*60)
