import re

from flask import render_template
from model import Benchmark, CATEGORIES


def init_routes(app):

    spaces = re.compile('[\W_]+')

    @app.template_filter('to_id')
    def to_id(value):
        return spaces.sub('-', value.lower().strip())

    def get_top_benchmarks(category):
        fields = ("rank", "title", "uri", "avg_load_time")
        benchmarks = Benchmark.objects.only(*fields)(category=category,
                                                     status="recent")
        return sorted(benchmarks, key=lambda b: float(b["avg_load_time"]))

    @app.route('/')
    def index():
        categories = [(category, get_top_benchmarks(category))
                      for category in CATEGORIES]
        return render_template('index.html', categories=categories)
