from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import Post, User

def posts(count=100):
    fake = Faker()

    for i in range(count):
        p=Post(body=fake.text(max_nb_chars=3000),
            title=fake.text(max_nb_chars=20),
            time=fake.past_date(),
            author=fake.name())
        db.session.add(p)
    db.session.commit()

def users(count=100):
    fake = Faker()

    admin = User(name='admin', username='admin', password='password')
    db.session.add(admin)

    for i in range(count):
        u = User(name=fake.name(),
        username=fake.word(),
        password=fake.word())
        db.session.add(u)

    db.session.commit()
