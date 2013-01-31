from datetime import timedelta, datetime
import re

from flask import render_template
from model import Benchmark, CATEGORIES


def init_routes(app):

    spaces = re.compile('[\W_]+')

    @app.template_filter('to_id')
    def to_id(value):
        return spaces.sub('-', value.lower().strip())

    count = app.config['BENCHMARKS_BY_CATEGORY']
    delta = app.config['BENCHMARKS_DATETIME']

    def get_top_benchmarks(from_datetime, category):
        return Benchmark.objects.only('title', 'uri', 'avg_load_time')(
            timestamp__gte=from_datetime, category=category)[:count]

    @app.route('/')
    def index():
        from_datetime = datetime.now() - timedelta(**delta)
        categories = [(category, get_top_benchmarks(from_datetime, category))
                      for category in CATEGORIES]
        return render_template('index.html', categories=categories)
