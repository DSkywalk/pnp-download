# utils for pnp download

# ps-downloader
    Usage: ps-downloader.py [options] <url> 

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit

      Download Options:
        These options control downloads.
    
        --filename=FILENAME
                            Use as base name ex: myname_0001, myname_0002, ...
        --username=USERNAME
                            your printerstudio username/email.
        --password=PASSWORD
                            your printerstudio password.

## Usage Examples:

Just download images from the site *(public shared - no user need it)*

    ps-downloader.py "http://www.printerstudio.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id=776206DB5DCF42B57BCE771A7E81A300901C5033E4F678D53001E1E930F6A6C765C02DBF2B90F1F4&ssid=33ADDB4C6F6F4830BA8B3A53500F709F"

Just download images from the site *(public shared)* and save images as "*test_0001.jpg*", "*test_0002.jpg*"

    ps-downloader.py --filename "test" "http://www.printerstudio.com/design/dn_show_parse.aspx?producttype=772E45C74E337CF36906FDBEFF230590&flow=868A4695A58AE09DFCB8D0AE100A93FF163EC7F6C8151841&id=E5997B120EFE58F2C15778485FE58D9AAEFCF816B3950DC3DBA0F7EEE4246A63F44AB90C58B90B39&projecttype=EFAE81EBDA27CF77EB9E00D7A1ACC4D5&projectfrom=EFAE81EBDA27CF77EB9E00D7A1ACC4D5&orderno=&ssid=BD8A9EF3E9C940018DB48E5A341B6469"

Download protected images from the site, **need a valid user**

    ps-downloader.py --username "foo@foo.com" --password "mypass" "http://www.printerstudio.com/products/pro_project_render.aspx?type=BAD7275F80A1BD73&order=E742257CA69120A06303245B264A3D83&id=A09CA5521B949F4396809EB370917E83322B4AE40C3EB279A58217F08BB57FE9E412121432C53FF7"
