import unittest
from flask import current_app
from app import create_app, db
from app.models import *
from sqlalchemy.exc import IntegrityError

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        u = User(name='Test User', username='test_user')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(User.query.get(u.id) is not None)

    def test_username_must_be_unique(self):
        u1 = User(name='Test User', username='test_user')
        db.session.add(u1)
        db.session.commit()
        u2 = User(name='Test User 2', username='test_user')
        db.session.add(u2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_create_role(self):
        r = Role(name='Tester')
        db.session.add(r)
        db.session.commit()
        self.assertTrue(Role.query.get(r.id) is not None)

    def test_role_must_be_unique(self):
        r1 = Role(name='Tester')
        db.session.add(r1)
        db.session.commit()
        r2 = Role(name='Tester')
        db.session.add(r2)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    #def test_get_user_role(self):

    def test_get_role_users(self):
        r = Role(name='Tester')
        db.session.add(r)
        db.session.commit()
        u1 = User(name='Test User', username='test_user1')
        u2 = User(name='Test User 2', username='test_user2')
        u1.role_id = r.id
        u2.role_id = r.id
        db.session.add_all([u1, u2])
        db.session.commit()
        users = r.users
        self.assertTrue(len(users) == 2 and users[0].name == 'Test User' and
                            users[1].name == 'Test User 2')

