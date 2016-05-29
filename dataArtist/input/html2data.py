import lxml.html
import urllib
import tempfile

from fancytools.os.PathStr import PathStr


TMP_IMG_DIR = PathStr(tempfile.mkdtemp('tmpImgDir'))



def html2data(html):
    '''
    extract either tables or images from html code
    '''
    paths = []
    data = []
    doc = lxml.html.fromstring(html)
    #images in html
    for img in doc.xpath('img'):
        #get the scr-path of the image:
        imgsrc = img.get('src')
        fname = PathStr(imgsrc).basename()
        fpath = TMP_IMG_DIR.join(fname)
        #download the image in a temporary folder:
        urllib.urlretrieve(imgsrc, fpath)
        paths.append(fpath)
    #tables
    table = _html2PyTable(doc)
    if table:
        data.append(table)
    return paths, data


def _html2PyTable(doc):
    table = []
    try:
        rows = doc.cssselect("tr")
            #TODO:
    except: # lxml.cccselect uses __import__ which doesnt work with pyinstaller
        print 'dynamic import error in lxml.cccselect'
        return []
    for row in rows:
        table.append(list())
        for td in row.cssselect("td"):
            table[-1].append(unicode(td.text_content()))
    return table

