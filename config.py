import os

# grabs the folder where the script runs
basedir = os.path.abspath(os.path.dirname(__file__))
BASEDIR = basedir

# enable debug mode
DEBUG = False

# secret key for session management
#   put the key in secret-key.txt and don't add that file to the repository
#   if others might have access to the repository, e.g. on github
SECRET_KEY = file(os.path.join(basedir,'secret-key.txt')).read().strip()

ADMIN_MAIL_RECIPIENTS = ['d0b13b8d6e3bc7f6@markusdobler.de']

LOGS_TO_BROWSE = {
    u'demo': {
        'log_line_pattern': "".join(s.strip() for s in 
                            """(?P<host>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<logtime>[^"]+)\s[+-]\d\d\d\d\]\s+
                            "(?P<method>[A-Z]+)\s(?P<requesturi>.+)\sHTTP/(?P<httpversion>[0-9.]+)"
                            \s+(?P<status>[0-9]+)\s+(?P<size>\S+)\s+"(?P<referer>.*)"\s+"(?P<agent>.*)"\s*\Z""".split('\n')),
        'time_parse_format': "%d/%b/%Y:%H:%M:%S",
        'file_names': ('access_log.processed', 'access_log'),
    }
}

