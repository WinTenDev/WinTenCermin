# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

import re
import requests
import urllib.parse
from bot import LOGGER, UPTOBOX_TOKEN
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bs4 import BeautifulSoup
from js2py import EvalJs, PyJsException
from random import choice


def direct_link_generator(link: str):
    """ direct links generator """
    if not link:
        raise DirectDownloadLinkException("No links found!")
    elif 'zippyshare.com' in link:
        return zippy_share(link)
    elif 'yadi.sk' in link:
        return yandex_disk(link)
    elif 'mediafire.com' in link:
        return mediafire(link)
    elif 'uptobox.com' in link or 'uptostream.com' in link:
        return uptobox(link)
    elif 'osdn.net' in link:
        return osdn(link)
    elif 'github.com' in link:
        return github(link)
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')


def zippy_share(url: str) -> str:
    """ ZippyShare direct links generator
    Based on https://github.com/KenHV/Mirror-Bot
             https://github.com/jovanzers/WinTenCermin """
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak menemukan link ZippyShare, cek formatnya!")
    try:
        base_url = re.search('http.+.zippyshare.com', link).group()
        response = requests.get(link, verify=False).content
        pages = BeautifulSoup(response, "lxml")
        try:
            js_script = pages.find("div", {"class": "center"}).find_all("script")[3]
        except IndexError:
            js_script = pages.find("div", {"class": "right"}).find_all("script")[2]
        except AttributeError:
            raise DirectDownloadLinkException("Sorry, Zippyshare is dead.")
        var_a = re.findall(r"(var .*;)", js_script.string)[0]
        omg = re.findall(r"\.(omg .*;)", js_script.string)[0]
        js_var = f'{var_a} {omg} var b = omg * ((a + 3) % 3);'
        js_content = js_var + "var x = \"/" + re.findall(r'\.href    =."/(.*?)";', js_script.string)[0] + "\""
        evaljs = EvalJs()
        setattr(evaljs, "x", None)
        evaljs.execute(js_content)
        js_content = getattr(evaljs, "x")
        return base_url + js_content, '', ''
    except (TypeError, PyJsException) as e:
        LOGGER.error(e)
        raise DirectDownloadLinkException("Generate direct link failed, try again.")
    except IndexError:
        raise DirectDownloadLinkException("Can't find download button")


def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Yandex.Disk links found")
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        return requests.get(api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException("Error: File not found / Download limit reached")


def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found")
    page = BeautifulSoup(requests.get(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')


def uptobox(url: str) -> str:
    """ Uptobox direct links generator
    based on https://github.com/jovanzers/WinTenCermin """
    try:
        url = url.replace("uptostream.com", "uptobox.com").replace(".com/iframe/", ".com/")
        link = re.findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Uptobox links found")
    if UPTOBOX_TOKEN is None:
        LOGGER.error('UPTOBOX_TOKEN not provided!')
        dl_url = link
    else:
        try:
            link = re.findall(r'\bhttp?://.*uptobox\.com/dl\S+', url)[0]
            dl_url = link
        except IndexError:
            file_id = re.findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
            file_link = 'https://uptobox.com/api/link?token=%s&file_code=%s' % (UPTOBOX_TOKEN, file_id)
            req = requests.get(file_link)
            result = req.json()
            dl_url = result['data']['dlLink']
    return dl_url


def osdn(url: str) -> str:
    """ OSDN direct links generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No OSDN links found")
    page = BeautifulSoup(
        requests.get(link, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    link = urllib.parse.unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No GitHub Releases links found")
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("Error: Can't extract the link")


def useragent():
    """
    useragent random setter
    """
    useragents = BeautifulSoup(
        requests.get(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/').content,
        'lxml').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text
