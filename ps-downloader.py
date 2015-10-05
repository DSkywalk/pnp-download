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

import sys, urllib, optparse
from BeautifulSoup import BeautifulSoup, CData
from urlparse import urlparse, parse_qs


""" fix ssl v1 problems - force TLSv1 """
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

""" virtual class for pnp sites """
class webpnp:
    def __init__(self, p_sUrl):
        self.m_dHeaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        self.m_sLoginUrl = ""
        self.m_sEditUrl = ""
        self.m_sDinamicUrl = ""
        self.m_dPayload = {}
        self.m_sFilenameCustom = lOptions.filename
        self.m_sUserUrl = p_sUrl
        self.m_needUser = False
        self.m_netloc = urlparse(p_sUrl).netloc[4:] # allow ps.de/.es/.com ...
        
        import requests
        self.m_oSession = requests.Session()
        self.m_oSession.mount('https://', MyAdapter()) # force ssl v1
        
        try: # remove windows warnings
            requests.packages.urllib3.disable_warnings()
        except:
            pass
            
        # finally call setup
        self.setup()
        
    
    def log_file(self, p_sFile, p_sTxt):
        with open(p_sFile, 'w') as file_:
            file_.write(p_sTxt.encode('utf-8'))
            file_.close()

    def setup(self):
        pass

    def download(self, p_sUrl):
        pass
    
    def prepare_url(self):
        return "unsupported yet", True
    
    def login(self):
        return False
        


class PrinterStudio(webpnp):

    """     setup with ps elements    """
    def setup (self):
        print "PS Class USED!"
        self.m_needUser = False
        self.m_sLoginUrl = "https://secure.%s/login.aspx"
        self.m_sEditUrl = "http://www.%s/products/pro_project_edit.aspx"
        self.m_sDinamicUrl = "http://www.%s/products/playingcard/design/dn_playingcards_front_dynamic.aspx?"
        self.m_dPayload = {
            '__EVENTTARGET' : 'btn_submit',
            '__EVENTARGUMENT' : '',
            'txt_email' : lOptions.username,
            'txt_password' : lOptions.password,
            'ckb_remember' : False,
            'btn_submit' : 'Login',
        }

   
    """     download images using final url    """
    def download(self, p_sURL):
        print "Downloading images..."
        #print p_oLogged.cookies.get_dict()
        request = self.m_oSession.get(p_sURL, headers=self.m_dHeaders)
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
            if self.m_sFilenameCustom:
                sFile = self.m_sFilenameCustom + "_" + "{0:04d}".format(iCounter) + "." + img['Exp']
                iCounter += 1
                
            urllib.urlretrieve (sUrl, sFile)


    """     from user URL to internal URL    """
    def prepare_url(self):
        oUrl = urlparse(self.m_sUserUrl)
        oQuery = parse_qs(oUrl.query)
        
        if "dn_playingcards_front_dynamic" in self.m_sUserUrl:
            print " Warning, trying use direct url without auth, if dont work please use 'pro_project_render.aspx' LINK"
            return self.m_sUserUrl, False

        if "dn_show_parse" in self.m_sUserUrl:
            return (self.m_sDinamicUrl % self.m_netloc) + "id=" + oQuery['id'][0] + "&ssid=" + oQuery['ssid'][0], False
        
        req = self.m_oSession.post(self.m_sEditUrl % self.m_netloc, data=oQuery, headers=self.m_dHeaders)
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

    """     login to https site and save cookies   """
    def login(self):
        response = self.m_oSession.get(self.m_sLoginUrl % self.m_netloc, headers=self.m_dHeaders, verify=False)
        # print response.headers
        html = BeautifulSoup(response.text)
        state = html.find(id='__VIEWSTATE')
        if not state['value']:
            return False

        self.m_dPayload['__VIEWSTATE'] = state['value']
        self.m_oSession.post(self.m_sLoginUrl % self.m_netloc, data=self.m_dPayload, headers=self.m_dHeaders)
        return True

class XCow(webpnp):
    def setup(self):
        print "CW Class USED!"
        self.m_needUser = True
        self.m_dHeaderJson = dict(self.m_dHeaders.items() + [('content-type', 'application/json')])
        self.m_sLoginUrl = "https://www.%s/default.aspx/Login"
        self.m_sDinamicUrl = "http://www.%s/SlideShow.aspx?f=Load&folder="
        self.m_sImageUrl = "http://c2.%s/img/12-" # -0-0-1
        self.m_dPayload = {
                'Email': lOptions.username,
                'Password': lOptions.password,
           }

    def prepare_url(self):
        request = self.m_oSession.get(self.m_sUserUrl, headers=self.m_dHeaders)
        page = BeautifulSoup(request.text)
        form = page.find('form')
        oQuery = parse_qs(form.get('action')[17:]) # remove "FileManager.aspx?"
        
        if not 'folder' in oQuery:
            print "ERROR! Folder URL not found..."
            print "action: " + form.get('action')
            return "", True
          
        return (self.m_sDinamicUrl % self.m_netloc) + oQuery['folder'][0], False

    def download(self, p_sURL):
        request = self.m_oSession.get(p_sURL, headers=self.m_dHeaders)
        # print response.headers
        # print response.status_code
        # self.log_file("cowcow.txt", request.text)
        lImages = request.text.split('\n')
        TotalImages = len(lImages)
        if TotalImages < 2:
            print " "
            print "ERROR! Images not found at " + p_sURL
            print " "
        
        print " Downloading: " + str(TotalImages) + " images."
        iCounter = 0
        for img in lImages[1:]: # first is project info, no need it atm
            lImgData = img.split(',')
            # print lImgData 
            sFile = lImgData[1]
            sUrl = (self.m_sImageUrl % self.m_netloc) + lImgData[0] + "-0-0-1"
            print "d: " + sFile
            if self.m_sFilenameCustom:
                sFile = self.m_sFilenameCustom + "_" + "{0:04d}".format(iCounter) + "." + sFile[-3:]
                iCounter += 1
                
            urllib.urlretrieve (sUrl, sFile)


    def login(self):
        import json
        response = self.m_oSession.post(self.m_sLoginUrl % self.m_netloc, data=json.dumps(self.m_dPayload), headers=self.m_dHeaderJson, verify=False)
        dResut = eval(response.text)
        if dResut['d'][0] != 'OK':
            print dResut['d'][1]
            return False
        return True

"""
****  MAIN 
"""

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


    oWeb = None
    if "printerstudio" in lArgs[0]:
        oWeb = PrinterStudio(lArgs[0])
    else:
        oWeb = XCow(lArgs[0])

    userLogged = False
    if lOptions.username and lOptions.password:
        userLogged = oWeb.login()

    if not oWeb.m_needUser:
        print " Warning, you are not logged. Some LINKS could not work ..."
    elif not userLogged:
        print "ERROR! This site needs a correct user/pass."
        sys.exit(0)
        

    print "Getting URL..."
    sUrl, bError = oWeb.prepare_url()
    
    if not bError:
        print "Using: %r" % sUrl
        oWeb.download(sUrl)
        
    sys.exit(0)

