import logging
import pickle

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class KnownIdList(object):
    ''' Very simple abstraction for collection with save/load support '''

    def __init__(self, fname):
        self.__id_list = []
        self.__fname = fname

    def load(self):
        ''' Load id list from fname passed in ctor '''
        try:
            with open(self.__fname) as fin:
                self.__id_list = pickle.load(fin)
        except:
            logger.exception('Unable to load known ID list')
            self.__id_list = []

    def add_id(self, item_id):
        self.__id_list.append(item_id)

    def save(self):
        ''' Save id list to fname passed in ctor '''
        with open(self.__fname, 'wb') as fout:
            pickle.dump(self.__id_list, fout, -1)

    def contains(self, item_id):
        return item_id in self.__id_list

