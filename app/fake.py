from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import Post

def posts(count=100):
    fake = Faker()

    for i in range(count):
        p=Post(body=fake.text(),
            time=fake.past_date(),
            author=fake.name()).
        db.session.add(p)
    db.session.commit()