import re

from flask import render_template
from model import Benchmark, CATEGORIES


def init_routes(app):

    spaces = re.compile('[\W_]+')

    @app.template_filter('to_id')
    def to_id(value):
        return spaces.sub('-', value.lower().strip())

    def get_top_benchmarks(category):
        return Benchmark.objects.only('title', 'uri', 'avg_load_time')(
            category=category, status="recent")

    @app.route('/')
    def index():
        categories = [(category, get_top_benchmarks(category))
                      for category in CATEGORIES]
        return render_template('index.html', categories=categories)
