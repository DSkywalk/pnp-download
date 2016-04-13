#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
ps-downloader.py.

Python library to download Printing sites content
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

    def is_jpg(self, p_fHeader):
        if (p_fHeader[:3] == "\xff\xd8\xff"):
            return True
        elif (p_fHeader[6:] == 'JFIF\0'):
            return True
        else:
            return False
        
    
    def clean_filename(self, value):
        for c in '\/:*?"<>|':
            value = value.replace(c,'-')
        return value.encode('ascii',errors='ignore') # force remove special chars

    def log_file(self, p_sFile, p_sTxt):
        with open(p_sFile, 'w') as file_:
            file_.write(p_sTxt)
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
        self.m_needUser = False
        self.m_sLoginUrl = "https://secure.%s/login.aspx"
        self.m_sEditUrl = "http://www.%s/products/pro_project_edit.aspx"
        self.m_sDinamicUrl = "http://www.%s/products/playingcard/design/dn_playingcards_%s_dynamic.aspx"
        self.m_sSSID = None
        self.m_dPayload = {
            '__EVENTTARGET' : 'btn_submit',
            '__EVENTARGUMENT' : '',
            'txt_email' : lOptions.username,
            'txt_password' : lOptions.password,
            'ckb_remember' : False,
            'btn_submit' : 'Login',
        }

    """     download images using final url    """
    def download_design (self, p_sURL):
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
            return False

        iCounter = 0
        for img in oImgs:
            sFile = img['ID'] + "." + img['Exp']
            sUrl = img['Path'] + "/" + sFile
            print "d: " + sFile
            if self.m_sFilenameCustom:
                sFile = self.m_sFilenameCustom + "_" + "{0:04d}".format(iCounter) + "." + img['Exp']
                iCounter += 1
                
            urllib.urlretrieve (sUrl, sFile)
        return True

    """ download images """
    def download(self, p_sURL):
        print "Downloading front images..."
        if not self.download_design(p_sURL):
            return

        try:
            oUrl = urlparse(p_sURL)
            oQuery = parse_qs(oUrl.query)
            self.m_sSSID = oQuery['ssid'][0]
            sUrl = self.m_sDinamicUrl % (self.m_netloc, "back")
            print "Downloading back images..."
            self.download_design(sUrl + "?ssid=" + str(self.m_sSSID))
        except:
            pass
    
    """     from user URL to internal URL    """
    def prepare_url(self):
        oUrl = urlparse(self.m_sUserUrl)
        oQuery = parse_qs(oUrl.query)
        
        if "dn_playingcards_" in self.m_sUserUrl:
            print " Warning, trying use direct url without auth, if dont work please use 'pro_project_render.aspx' LINK"
            return self.m_sUserUrl, False

        if "dn_show_parse" in self.m_sUserUrl:
            sUrl = self.m_sDinamicUrl % (self.m_netloc, "front")
            return sUrl + "?id=" + oQuery['id'][0] + "&ssid=" + self.m_sSSID, False
        
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


class XCowShared(webpnp):
    def setup(self):
        self.m_needUser = True
        self.m_dHeaderJson = dict(self.m_dHeaders.items() + [('content-type', 'application/json')])
        self.m_sLoginUrl = "https://www.%s/default.aspx/Login"
        self.m_sDinamicUrl = "http://www.%s/SlideShow.aspx?f=Load&folder="
        self.m_sImageUrl = "http://c1.%s/img/12-" # -0-0-1
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
        
        print " Downloading: " + str(TotalImages - 1) + " images."
        iCounter = 0
        for img in lImages[1:]: # first is project info, no need it atm
            lImgData = img.split(',')
            if len(lImgData) < 4:
                continue

            sUrl = (self.m_sImageUrl % self.m_netloc) + lImgData[0] + "-0-0-1"
            if self.m_sFilenameCustom:
                sFile = self.m_sFilenameCustom + "_" + "{0:04d}".format(iCounter) + "." + lImgData[1][-3:]
                iCounter += 1
                print "d: " + sFile
                urllib.urlretrieve (sUrl, sFile)
            else:
                try:
                    sFile = lImgData[1]
                    urllib.urlretrieve (sUrl, sFile)
                    print "d: " + sFile
                except IOError: # avoid malformed filenames
                    sFile = self.clean_filename(lImgData[1])
                    print "d: " + sFile + " (cleaned filename)"
                    urllib.urlretrieve (sUrl, sFile)
                except UnicodeEncodeError:
                    try:
                        print "d: " + sFile.encode('utf-8',errors='ignore') + " (utf8)"
                    except:
                        print "d: " + sFile.encode('latin-1',errors='ignore') + " (latin-1)"



    def login(self):
        import json
        response = self.m_oSession.post(self.m_sLoginUrl % self.m_netloc, data=json.dumps(self.m_dPayload), headers=self.m_dHeaderJson, verify=False)
        dResut = eval(response.text)
        if dResut['d'][0] != 'OK':
            print dResut['d'][1]
            return False
        return True


class XCowDesigner(XCowShared):
    def setup(self):
        self.m_needUser = False
        self.m_dHeaderJson = dict(self.m_dHeaders.items() + [('content-type', 'application/json')])
        self.m_sLoginUrl = "https://www.%s/default.aspx/Login"
        self.m_sDinamicUrl = "http://www.%s/ClientDesigner/ClientDesigner.ashx?f=Design&DesignId="
        self.m_sImageUrl = "http://%s/img/12-" # -0-0-1
        self.m_dPayload = {
                'Email': lOptions.username,
                'Password': lOptions.password,
           }
        
    def prepare_url(self):
        if "Design" in self.m_sUserUrl:
            try:
                dsnId = parse_qs(urlparse(self.m_sUserUrl).query)['DesignId'][0]
                return (self.m_sDinamicUrl % self.m_netloc) + dsnId, False
            except:
                print "unknown url..."
                return "", True
        request = self.m_oSession.get(self.m_sUserUrl)
        page = BeautifulSoup(request.text)
        lImages = page.findAll('img')
        try:
            for img in lImages:
                sFile = urlparse(img.get('src')).path[5:]
                if sFile[:2] == "4-":
                    sFile = sFile[2:]
                    return (self.m_sDinamicUrl % self.m_netloc) + sFile[:sFile.index('-')], False
            
        except:
            pass
        
        print "ERROR! unknown design, sorry..."
        return "", True

    def download(self, p_sURL):
        request = self.m_oSession.get(p_sURL, headers=self.m_dHeaders, stream=True)
        page = None
        try:
            import zipfile, StringIO
            z=zipfile.ZipFile(StringIO.StringIO(request.raw.read()))
            page = BeautifulSoup(z.read("1.xml"))
        except (RuntimeError, zipfile.BadZipfile):
            print "ERROR! unknown album, sorry..."
            return

        lInfo = page.find('alldesign')
        sCacheServer = lInfo.get('cacheserver')
        lImages = page.findAll('imagedesign')
        lImages = set([x.get('filesystemid') for x in lImages ]) #get id and remove duplicated using a set
        TotalImages = len(lImages)
        print " Downloading: " + str(TotalImages) + " images from " + sCacheServer
        iCounter = 0

        import imghdr
        for imgId in lImages:
            if not imgId:
                continue
            sFile = imgId
            print "d: " + sFile
            sUrl = (self.m_sImageUrl % sCacheServer) + sFile + "-0-0-1"
            sExt = ".jpg"
            rImg = self.m_oSession.get(sUrl, headers=self.m_dHeaders, stream=True)
            # print rImg.headers # siempre manda que es jpeg, no valen de nada las cabeceras...
            fData = rImg.raw.read()
            sExt = imghdr.what("", fData[:32]) # only need first 32 bytes (header) to get image type
            if self.m_sFilenameCustom:
                sFile = self.m_sFilenameCustom + "_" + "{0:04d}".format(iCounter)
                iCounter += 1
                
            with open(sFile + "." + sExt, 'wb') as file_:
                file_.write(fData)
                file_.close()

"""
****  MAIN 
"""

if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog [options] <url> ',
                               version='0.8',)
    install_opts  = optparse.OptionGroup( parser, 'Download Options',
                                          'These options control downloads.', )
    
    install_opts.add_option('--filename', action='store', default=False,
                        help='Use as base name ex: myname_0001, myname_0002, ...')

    
    install_opts.add_option('--username', action='store', default=False,
                        help='your site username/email.')
    
    install_opts.add_option('--password', action='store', default=False,
                        help='your site password.')
    
    
    parser.add_option_group(install_opts)
    lOptions, lArgs = parser.parse_args()
    if not len(lArgs):
        parser.print_help()
        sys.exit(1)


    oWeb = None
    if "printerstudio" in lArgs[0]:
        oWeb = PrinterStudio(lArgs[0])
    elif not "ShareAlbum" in lArgs[0]:
        oWeb = XCowDesigner(lArgs[0])
    else:
        oWeb = XCowShared(lArgs[0])

    userLogged = False
    if lOptions.username and lOptions.password:
        print "Login..."
        userLogged = oWeb.login()
    else:
        print " "

    if not userLogged:
        if not oWeb.m_needUser:
            print " Warning, you are not logged. Some LINKS could not work ..."
        else:
            print "ERROR! This site needs a correct user/pass."
            sys.exit(0)

    print "Getting URL..."
    sUrl, bError = oWeb.prepare_url()
    
    if not bError:
        print "Using: %r" % sUrl
        oWeb.download(sUrl)
        
    sys.exit(0)

