from lib.dbclient import DbClient


class Summarizer:
    def __init__(self):
        self.db = DbClient()

    def run(self, filters=None):
        total_records = self.db.get_total_record_count()
        unique_key_counts = self.db.get_unique_key_counts()
        filtered_record_count = None

        if filters is not None:
            filtered_record_count = self.db.get_filtered_count(filters)

        print 'Total: '+str(total_records)+' record(s)'

        if filtered_record_count is not None:
            print 'Filtered: '+str(filtered_record_count)+' record(s)'

        for key, c in unique_key_counts:
            print str(c)+' '+key+'(s)'
