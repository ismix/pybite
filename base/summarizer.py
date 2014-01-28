from lib.dbclient import DbClient


class Summarizer:
    def __init__(self):
        self.db = DbClient()

    def run(self, filter_str=None):
        total_records = self.db.get_total_record_count()
        unique_key_counts = self.db.get_unique_key_counts()
        filtered_record_count = None

        if filter_str is not None:
            filters = self._process_filter_string(filter_str)
            filtered_record_count = self.db.get_filtered_count(filters)

        print 'Total: '+str(total_records)+' record(s)'

        if filtered_record_count is not None:
            print 'Filtered: '+str(filtered_record_count)+' record(s)'

        for key, c in unique_key_counts:
            print str(c)+' '+key+'(s)'

    def _process_filter_string(self, filter_str):
        filters = {}
        try:
            pairs = filter_str.split(',')
            for pair in pairs:
                [k, v] = pair.split('=')
                filters[k] = v
            return filters
        except:
            print "Invalid filter string, correct pattern is field1=value1,field2=value2"
            raise SystemExit