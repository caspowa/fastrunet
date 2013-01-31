from datetime import datetime

from flask.ext.mongoengine import Document
from mongoengine import StringField, URLField, FloatField, DateTimeField


CATEGORIES = (
    'Adult',
    'Arts',
    'Business',
    'Computers',
    'Games',
    'Health',
    'Home',
    'Kids and Teens',
    'News',
    'Recreation',
    'Reference',
    'Regional',
    'Science',
    'Shopping',
    'Society',
    'Sports',
    'World',
)


class Benchmark(Document):
    title = StringField(max_length=64, required=True)
    uri = URLField(max_length=64, required=True)
    category = StringField(choices=CATEGORIES)
    avg_load_time = FloatField(default=0)
    timestamp = DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.uri

    meta = {
        'collection': 'benchmarks',
        'ordering': ['avg_load_time'],
    }
