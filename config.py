import ConfigParser

class Config(object):
    def __init__(self, fname):
        self.__parser = ConfigParser.RawConfigParser({'max_items_to_send' : 20})
        self.__parser.read(fname)

    def query(self):
        return self.__parser.get('root', 'query')

    def smtp_host(self):
        return self.__parser.get('root', 'smtp_host')

    def smtp_user(self):
        return self.__parser.get('root', 'smtp_user')

    def smtp_password(self):
        return self.__parser.get('root', 'smtp_password')

    def mail_from(self):
        return self.__parser.get('root', 'mail_from')

    def mail_to(self):
        return self.__parser.get('root', 'mail_to')

    def mail_subject(self):
        return self.__parser.get('root', 'mail_subject')

    def known_id_list_file(self):
        return self.__parser.get('root', 'known_id_list_file')

    def max_items_to_send(self):
        return self.__parser.getint('root', 'max_items_to_send')
