# utils for pnp download

# ps-downloader

![ps-downloader](http://i.imgur.com/QKPuxDp.png)

    Usage: ps-downloader.py [options] <url> 

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      Download Options:
        These options control downloads.
    
        --filename=FILENAME
                            Use as base name ex: myname_0001, myname_0002, ...
        --username=USERNAME
                            your site username/email.
        --password=PASSWORD
                            your site password.

## Usage Examples:

Just download images from the site *(public shared - no user need it)*

    ps-downloader.py "http://www.printerstudio.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id=E0000000000000000000000000&ssid=F00000000000000000000000"

Just download images from the site *(public shared)* and save images as "*test_0001.jpg*", "*test_0002.jpg*"

    ps-downloader.py --filename "test" "http://www.printerstudio.com/design/dn_show_parse.aspx?producttype=772E45C74E337CF36906FDBEFF230590&flow=E0000000000000000000&id=E00000000000000000&projecttype=E0000000000000000&projectfrom=E0000000000000000&orderno=&ssid=FEO"

Download protected images from the site, **need a valid user**

    ps-downloader.py --username "foo@foo.com" --password "mypass" "http://www.printerstudio.com/products/pro_project_render.aspx?type=BADE0000000000000&order=E00000000000000000000&id=E00000000000000000000000000000000"

Download cowcow/artscow *public shared* project

    ps-downloader.py "http://www.artscow.com/gallery/card/bit-mini-foooo"

Download cowcow/artscow shared project, **need a valid user**

    ps-downloader.py --username "foo@foo.com" --password "mypass" "http://www.artscow.com/ShareAlbum.aspx?Key=fooooo"

