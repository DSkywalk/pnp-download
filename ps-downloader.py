#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
ps-downloader.py.

Python library to download PS sites content
https://github.com/dskywalk/pnp-download

Copyright (C)  2015 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys, urllib, urllib2, cookielib
from BeautifulSoup import BeautifulSoup, CData
from urlparse import urlparse, parse_qs
import optparse

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
LOGIN_URL = "https://secure.printerstudio.com/login.aspx"
EDIT_URL = "http://www.printerstudio.com/products/pro_project_edit.aspx"
DINAMIC_URL = "http://www.printerstudio.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?"
FINAL_PATH = "/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id="

from requests.adapters import HTTPAdapter
try:
    from requests.packages.urllib3.poolmanager import PoolManager
except:
    from urllib3.poolmanager import PoolManager
import ssl

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)
def download(p_oLogged, p_sURL, p_sBaseName):
    print "Downloading images..."
    #print p_oLogged.cookies.get_dict()
    request = p_oLogged.get(p_sURL, headers=USER_AGENT)
    page = BeautifulSoup(request.text)
    imgs = page.find(id='hidd_images_info')
    try:
        oImgs = eval( imgs['value'] )
    except:
        print " "
        print "ERROR! Can not enter in: " + p_sURL
        print " "
        print " Try to logged in PS and retry again..."
        return

    iCounter = 0
    for img in oImgs:
        sFile = img['ID'] + "." + img['Exp']
        sUrl = img['Path'] + "/" + sFile
        print "d: " + sFile
        if p_sBaseName:
            sFile = p_sBaseName + "_" + "{0:04d}".format(iCounter) + "." + img['Exp']
            iCounter += 1
            
        urllib.urlretrieve (sUrl, sFile)


def prepare_url(p_oLogged, p_sUrl):
    oUrl = urlparse(p_sUrl)
    oQuery = parse_qs(oUrl.query)
    
    if "dn_playingcards_front_dynamic" in p_sUrl:
        print " Warning, trying use direct url without auth, if dont work please use 'pro_project_render.aspx' LINK"
        return p_sUrl, False

    if "dn_show_parse" in p_sUrl:
        return DINAMIC_URL + "id=" + oQuery['id'][0] + "&ssid=" + oQuery['ssid'][0], False
    
    req = p_oLogged.post(EDIT_URL, data=oQuery, headers=USER_AGENT)
    jsval = BeautifulSoup(req.text)
    for cdata in jsval.findAll(text=True):
        if isinstance(cdata, CData):
            response = eval("%r" % cdata)
            if response[:4] == 'http':
                return response, False
            else:
                print response + " ??"

    print " ERROR! Can not get final url, please use pro_project_render.aspx or dn_playingcards_front_dynamic.aspx LINKS"
    print " Also you would try to use user/pass args..."
    return "", True

def login_ps(p_oLogin, p_oPayload):
    p_oLogin.mount('https://', MyAdapter())
    response = p_oLogin.get(LOGIN_URL, headers=USER_AGENT, verify=False)
    # print response.headers
    html = BeautifulSoup(response.text)
    state = html.find(id='__VIEWSTATE')
    if not state['value']:
        return False

    p_oPayload['__VIEWSTATE'] = state['value'];
    p_oLogin.post(LOGIN_URL, data=p_oPayload, headers=USER_AGENT)
    return p_oLogin

if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog [options] <url> ',
                               version='0.1',)
    install_opts  = optparse.OptionGroup( parser, 'Download Options',
                                          'These options control downloads.', )
                                          
    install_opts.add_option('--filename', action='store', default=False,
                        help='Use as base name ex: myname_0001, myname_0002, ...')

    
    install_opts.add_option('--username', action='store', default=False,
                        help='your printerstudio username/email.')
    
    install_opts.add_option('--password', action='store', default=False,
                        help='your printerstudio password.')
    

    
    parser.add_option_group(install_opts)
    lOptions, lArgs = parser.parse_args()
    if not len(lArgs):
        parser.print_help()
        sys.exit(1)

    import requests
    oSession = requests.Session()

    if lOptions.username and lOptions.password:
        # login
        print "Login auth..."
        try:
            requests.packages.urllib3.disable_warnings()
        except:
            pass

        payload = {
            '__EVENTTARGET' : 'btn_submit',
            '__EVENTARGUMENT' : '',
            'txt_email' : lOptions.username,
            'txt_password' : lOptions.password,
            'ckb_remember' : False,
            'btn_submit' : 'Login',
        }

        login_ps(oSession, payload)
    else:
        print " Warning, you are not logged in PS. Some LINKS could not work ..."

    print "Getting URL..."
    sUrl, bError = prepare_url(oSession, lArgs[0])
    print "Using: %r" % sUrl
    
    if not bError:
        download(oSession, sUrl, lOptions.filename)
        
    sys.exit(0)
