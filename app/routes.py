from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask import current_app
from os.path import join as os_join_path
from collections import namedtuple
import apachelog
import re
import models

#------------------------------------------------------------------------------#
# Controllers
#------------------------------------------------------------------------------#

bp = Blueprint('logbrowser', __name__, template_folder='templates',
              static_folder='static', static_url_path='/static.logbrowser')
bp.before_app_first_request(models.init)
blueprints = [bp]

@bp.route("/")
def index():
    return render_template("logbrowser/index.html")

@bp.route("/<handle>")
@bp.route("/<handle>/raw", defaults={'use_default_filters': False})
def log_view(handle, use_default_filters=True):
    log = models.logs[handle]
    filters = request.args.copy()
    if use_default_filters:
        for k,val in log.default_filters.items():
            if isinstance(val, (str, unicode)):
                filters.add(k, val)
            else:
                for v in val:
                    filters.add(k, v)
    entries = log.entries(filters)
    return render_template("logbrowser/log_view.html", entries=entries, handle=handle)

@bp.route("/<handle>/refresh")
def refresh_log(handle):
    log = models.logs[handle]
    log.load()
    flash("Refreshed", "success")
    redirect_to = request.referrer or url_for('.log_view', handle=handle)
    return redirect(redirect_to)


# Error Handlers

@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('logbrowser/500.html'), 500

@bp.route('/<path:invalid_path>')
def internal_error(invalid_path):
    return render_template('logbrowser/404.html'), 404
