import pymongo as mdb
import config

KEY_UNIQUE = 'unique'
PREFIX_UNIQUE = 'unique_'


class DbClient:
    def __init__(self, keys={}):
        self.db = mdb.MongoClient(config.DB_HOST, config.DB_PORT)[config.DB_NAME]
        self.records_table = self.db[config.DB_PREFIX+'records']
        self.keys = keys

    def add_bulk_data(self, data):
        for datum in data:
            self.add_data(datum)

    def add_data(self, data):
        if KEY_UNIQUE in self.keys:
            fields = self.keys[KEY_UNIQUE]
            for field in fields:
                value = data[field]
                if type(value) == list:
                    for item in value:
                        if not (self.check_unique_key(field, item) is None):
                            data[field].remove(item)
                        else:
                            self.add_unique_key(field, item)

                        if len(data[field]) == 0:
                            print "Nope"
                            return
                else:
                    if not (self.check_unique_key(field, value) is None):
                        print "Nope"
                        return
                    else:
                        self.add_unique_key(field, value)

        self.records_table.insert(data)

    def add_unique_key(self, field_name, field_value):
        self.db[config.DB_PREFIX+PREFIX_UNIQUE+field_name].insert({"_id": field_value})

    def check_unique_key(self, field_name, field_value):
        return self.db[config.DB_PREFIX+PREFIX_UNIQUE+field_name].find_one({"_id": field_value})
