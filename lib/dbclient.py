import pymongo as mdb
import config

KEY_UNIQUE = 'unique'
PREFIX_UNIQUE = 'unique_'
RECORDS_TABLE_NAME = 'records'


class DbClient:
    def __init__(self, keys={}):
        self.db = mdb.MongoClient(config.DB_HOST, config.DB_PORT)[config.DB_NAME]
        self.records_table = self.db[config.DB_PREFIX+RECORDS_TABLE_NAME]
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
                        if self.check_unique_key(field, item) is not None:
                            data[field].remove(item)
                        else:
                            self.add_unique_key(field, item)

                        if len(data[field]) == 0:
                            return
                else:
                    if self.check_unique_key(field, value) is not None:
                        return
                    else:
                        self.add_unique_key(field, value)

        self.records_table.insert(data)

    def add_unique_key(self, field_name, field_value):
        self.db[config.DB_PREFIX+PREFIX_UNIQUE+field_name].insert({"_id": field_value})

    def check_unique_key(self, field_name, field_value):
        return self.db[config.DB_PREFIX+PREFIX_UNIQUE+field_name].find_one({"_id": field_value})

    def get_total_record_count(self):
        return self.records_table.count()

    def get_unique_key_counts(self):
        counts = []
        collections = self.db.collection_names()

        for collection_name in collections:
            if PREFIX_UNIQUE in collection_name:
                counts.append((collection_name.split(PREFIX_UNIQUE)[-1], self.db[collection_name].count()))

        return counts

    def get_filtered_count(self, filters):
        return self.records_table.find(filters).count()