from flask import current_app, flash
from os.path import join as os_join_path
import re
from datetime import datetime, timedelta


class Log(object):
    def __init__(self, file_names, time_parse_format, log_line_pattern):
        self.file_names = file_names
        self.parse_time = lambda time: datetime.strptime(time, time_parse_format)
        self.time_parse_format = time_parse_format
        self.pattern = re.compile(log_line_pattern)
        self.load()

    def load(self):
        self.log_entries = []
        basedir = current_app.config['BASEDIR']
        for fname in self.file_names:
            for line in file(os_join_path(basedir, fname)):
                try:
                    processed = self.process_line(line)
                    self.log_entries.append(processed)
                except Exception as ex:
                    flash("Failed to process log line %r"%line, "error")
                    flash(ex, "error")

    def process_line(self, line):
        entry = self.pattern.match(line).groupdict()
        entry['time'] = self.parse_time(entry['logtime'])
        entry['timestamp'] = datetime.strftime(entry['time'], '%Y-%m-%d %H:%M:%S')
        return entry

    default_filters = {
        '-requesturi': (
            '^/static/(css|img|js)/',
            '^/favicon.ico$',
        ),
        'time': '5 days',
    }
    def entries(self, filters):
        log_entries = self.entries_filtered_by_time(
                                        filters.pop('time', '9999 days'),
                                        filters.pop('-time', '0 seconds'))
        for field, pattern in filters.iteritems(multi=True):
            pattern = re.compile(pattern)
            if field.startswith('-'):
                field = field[1:]
                test = lambda txt: not pattern.search(txt)
            else:
                test = lambda txt: pattern.search(txt)
            log_entries = [e for e in log_entries if test(e[field])]
        return log_entries

    def entries_filtered_by_time(self, not_before_pattern, not_after_pattern):
        log_entries = self.log_entries
        now = datetime.now()
        def to_threshold_datetime(delta_pattern):
            value, unit = delta_pattern.split()
            return now - timedelta(**{str(unit): int(value)})
        not_before = to_threshold_datetime(not_before_pattern)
        not_after = to_threshold_datetime(not_after_pattern)
        log_entries = [e for e in log_entries
                       if not_before < e['time'] < not_after]
        return log_entries


logs = {}

def init():
    for handle, config in current_app.config['LOGS_TO_BROWSE'].items():
        logs[handle] = Log(**config)
