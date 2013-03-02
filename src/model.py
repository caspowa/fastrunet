from flask.ext.mongoengine import Document
from mongoengine import StringField, URLField, FloatField, DateTimeField, IntField


class Benchmark(Document):
    title = StringField()
    uri = URLField()
    category = StringField()
    avg_load_time = FloatField()
    timestamp = DateTimeField()
    status = StringField()
    rank = IntField()

    def __unicode__(self):
        return self.uri

    meta = {
        'allow_inheritance': False,
        'collection': 'benchmarks',
        'ordering': ['avg_load_time'],
    }
