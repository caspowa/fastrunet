from flask import render_template

from model import Benchmark


CATEGORIES = (
    'Развлечения',
    'Hi-Tech',
    'Авто',
    'Бизнес',
    'Отдых',
    'Спорт',
    'Игровая',
    'СМИ',
    'Порталы',
    'Дом',
    'Работа',
    'Учёба',
    'Справки',
    'Общество',
    'Культура',
)


def init_routes(app):

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
