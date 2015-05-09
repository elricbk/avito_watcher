from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import utils

__HTML_TEMPLATE = u'''
<html>
<head></head>
<body>
<p><b><a href="{url}">{title}</a>, {price}</b> {date}</p>
<p>{desc}</p>
{images}
</body>
</html>
'''

def __add_images(msg, full_description):
    img_list = []
    for idx, img_url in enumerate(full_description['img_list']):
        full_url = 'http:' + img_url
        r = utils.retryable_get(full_url)
        if r is None:
            continue
        msg_image = MIMEImage(r.content)
        cid = 'image%d' % (idx + 1)
        msg_image.add_header('Content-ID', '<' + cid + '>')
        img_list.append(cid)
        msg.attach(msg_image)
    return img_list

def __build_plain_text(item, full_description):
    return MIMEText(str(item) + '\n' + full_description['desc'], _subtype='plain', _charset='utf8')

def __build_html(item, full_description, img_list):
    img_template = '<img src="cid:{cid}">'
    html = __HTML_TEMPLATE.format(
        title=item.title,
        price=item.price,
        date=item.date,
        url='http://avito.ru' + item.url,
        desc=full_description['desc'].decode('utf8').replace('\n', '<br>'),
        images=''.join(img_template.format(cid=cid) for cid in img_list)
    ).encode('utf8')
    return MIMEText(html, _subtype='html', _charset='utf8')

def __build_text_part(item, full_description, img_list):
    msg_text = MIMEMultipart('alternative')
    msg_text.attach(__build_plain_text(item, full_description))
    msg_text.attach(__build_html(item, full_description, img_list))
    return msg_text

def build_email(item):
    full_description = item.get_full_description()
    if full_description is None:
        full_description = {
            'desc': 'Error getting full description',
            'img_list': []
        }

    msg = MIMEMultipart()
    img_list = __add_images(msg, full_description)
    msg.attach(__build_text_part(item, full_description, img_list))
    return msg

