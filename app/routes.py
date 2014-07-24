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

bp = Blueprint('logviewer', __name__, template_folder='templates',
              static_folder='static')
bp.before_app_first_request(models.init)
blueprints = [bp]

LogLine = namedtuple("LogLine", "ip timestamp ")

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/<handle>")
def log_view(handle, filters=()):
    flash(request.args)
    filters = models.logs[handle].default_filters + tuple(filters)
    flash(filters)
    return log_view_raw(handle, filters)

@bp.route("/<handle>/raw")
def log_view_raw(handle, filters=()):
    log = models.logs[handle]
    entries = log.entries(filters)
    return render_template("log_view.html", entries=entries, handle=handle)

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
    return render_template('500.html'), 500

@bp.route('/<path:invalid_path>')
def internal_error(invalid_path):
    return render_template('404.html'), 404
