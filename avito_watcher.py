#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import smtplib
import logging
import sys

from email.mime.multipart import MIMEMultipart

import avito_item
import id_list
import utils
import mail_builder
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

AVITO_ROOT = 'http://m.avito.ru'

def get_item_list(cfg):
    r = utils.retryable_get(AVITO_ROOT + cfg.query())
    soup = BeautifulSoup(r.content)
    item_list = []
    for article in soup.select('article.b-item'):
        if 'item-vip' in article['class']:
            continue
        item_list.append(avito_item.AvitoItem(article))
    return item_list

def send_email(cfg, outer):
    smtp = smtplib.SMTP_SSL(cfg.smtp_host())
    smtp.login(cfg.smtp_user(), cfg.smtp_password())
    smtp.sendmail(cfg.mail_from(), [cfg.mail_to()], outer.as_string())

def setup_email_root(cfg):
    outer = MIMEMultipart()
    outer['From'] = cfg.mail_from()
    outer['To'] = cfg.mail_to()
    outer['Subject'] = cfg.mail_subject()
    return outer

def check_avito(cfg):
    known_ids = id_list.KnownIdList(cfg.known_id_list_file())
    known_ids.load()
    item_list = get_item_list(cfg)
    outer = setup_email_root(cfg)
    new_items_found = False
    for item in item_list:
        if not known_ids.contains(item.item_id):
            new_items_found = True
            logger.debug("Going to attach %s", item)
            outer.attach(mail_builder.build_email(item))
            known_ids.add_id(item.item_id)
    if new_items_found:
        logger.info("New items found, will send a notification")
        send_email(cfg, outer)
        known_ids.save()
    else:
        logger.info("No new items found, no notification would be sent")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s config-file' % sys.argv[0])
    cfg = config.Config(sys.argv[1])
    check_avito(cfg)
