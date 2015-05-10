from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

import utils

__HTML_TEMPLATE = u'''
<html>
    <head></head>
    <body>
        <div>
            {main_image}
            <p>
                <a href="{url}">{title}</a><br>
                <b>{price}</b><br>
                {date}
            </p>
        </div>

        <div style="clear: left; margin-top: 40px;">
            <hr>
            <p><small>{desc}</small></p>
        </div>

        <hr>

        {images}

        <hr>
    </body>
</html>
'''
__IMG_TEMPLATE = '<img src="{src}" hspace="5">'
__MAIN_IMAGE_TEMPLATE = '<img src="{src}" style="float: left; margin-right: 10px;" width="75" height="75">'

def __full_url(img_url):
    return re.sub(r'\d+x\d+', '100x75', 'http:' + img_url)

def __embed_images(msg, full_description):
    ''' Allows to embed images in the email
    Returns list of img src's in form of 'cid:image1'
    '''
    img_src_list = []
    for idx, img_url in enumerate(full_description['img_list']):
        full_url = __full_url(img_url)
        r = utils.retryable_get(full_url)
        if r is None:
            continue
        msg_image = MIMEImage(r.content)
        cid = 'image%d' % (idx + 1)
        msg_image.add_header('Content-ID', '<' + cid + '>')
        img_src_list.append('cid:' + cid)
        msg.attach(msg_image)
    return img_src_list

def __link_images(msg, full_description):
    ''' Builds a list of full links to the images to allow use in <img> tag '''
    return [__full_url(u) for u in full_description['img_list']]

def __build_plain_text(item, full_description):
    return MIMEText(str(item) + '\n' + full_description['desc'], _subtype='plain', _charset='utf8')

def __build_html(item, full_description, img_src_list):
    main_image = ''
    if len(img_src_list) > 0:
        main_image = __MAIN_IMAGE_TEMPLATE.format(src=img_src_list[0])
    html = __HTML_TEMPLATE.format(
        main_image=main_image,
        title=item.title,
        price=item.price,
        date=item.date,
        url='http://avito.ru' + item.url,
        desc=full_description['desc'].decode('utf8').replace('\n', '<br>'),
        images=''.join(__IMG_TEMPLATE.format(src=src) for src in img_src_list[1:])
    ).encode('utf8')
    return MIMEText(html, _subtype='html', _charset='utf8')

def __build_text_part(item, full_description, img_src_list):
    msg_text = MIMEMultipart('alternative')
    msg_text.attach(__build_plain_text(item, full_description))
    msg_text.attach(__build_html(item, full_description, img_src_list))
    return msg_text

def build_email(item):
    full_description = item.get_full_description()
    if full_description is None:
        full_description = {
            'desc': 'Error getting full description',
            'img_list': []
        }

    msg = MIMEMultipart()
    img_src_list = __link_images(msg, full_description)
    msg.attach(__build_text_part(item, full_description, img_src_list))
    return msg

