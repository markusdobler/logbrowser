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

    default_filters = (
        ('-requesturi', '^/static/(css|img|js)/'),
        ('-requesturi', '^/favicon.ico$'),
        ('time', '5 days'),
    )
    def entries(self, filters):
        log_entries = self.entries_filtered_by_time(filters.poplist('time'),
                                                    filters.poplist('-time'))
        for field, pattern in filters.iteritems(multi=True):
            pattern = re.compile(pattern)
            if field.startswith('-'):
                field = field[1:]
                test = lambda txt: not pattern.search(txt)
            else:
                test = lambda txt: pattern.search(txt)
            log_entries = [e for e in log_entries if test(e[field])]
        return log_entries

    def entries_filtered_by_time(self, not_before_patterns, not_after_patterns):
        log_entries = self.log_entries
        now = datetime.now()
        def to_datetime_delta(pattern):
            value, unit = pattern.split()
            return timedelta(**{str(unit): int(value)})
        if not_before_patterns:
            not_before = now - max(to_datetime_delta(p) for p in not_before_patterns)
            log_entries = [e for e in log_entries if e['time'] > not_before]
        if not_after_patterns:
            not_after = now - min(to_datetime_delta(p) for p in not_after_patterns)
            log_entries = [e for e in log_entries if not_after > e['time']]
        return log_entries


logs = {}

def init():
    for handle, config in current_app.config['LOGS_TO_BROWSE'].items():
        logs[handle] = Log(**config)
