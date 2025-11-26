from peewee import *
from database.db_connection import db
import datetime


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = BigIntegerField(unique=True, index=True)
    username = CharField(null=True, max_length=255)
    first_name = CharField(max_length=255)
    last_name = CharField(null=True, max_length=255)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'users'


class SearchHistory(BaseModel):
    user = ForeignKeyField(User, backref='searches', on_delete='CASCADE')
    command = CharField(max_length=50)
    query = TextField(null=True)
    movie_data = TextField()
    created_at = DateTimeField(default=datetime.datetime.now, index=True)

    class Meta:
        table_name = 'search_history'
        indexes = ((('user', 'created_at'), False),)


def create_tables():
    with db:
        db.create_tables([User, SearchHistory], safe=True)
