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
        Role.insert_roles()
        u1 = User(name='Test User', username='test_user1')
        u2 = User(name='Test User 2', username='test_user2')
        db.session.add_all([u1, u2])
        db.session.commit()
        guest = Role.query.filter_by(name='Guest').first()
        users = guest.users
        self.assertTrue(len(users) == 2 and users[0].name == 'Test User' and
                            users[1].name == 'Test User 2')


    def test_password_is_not_readable(self):
        u = User(name='Test User', username='test_user', password='password')

        with self.assertRaises(AttributeError):
            u.password

    def test_password_is_hashed(self):
        u = User(name='Test User', username='test_user', password='password')
        self.assertFalse(u.password_hash == 'password')

    def test_password_verification(self):
        u = User(name='Test User', username='test_user', password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('wordpass'))

    def test_hashes_are_random(self):
        u1 = User(name='Test User', username='test_user1', password='password')
        u2 = User(name='Test User', username='test_user2', password='password')
        self.assertFalse(u1.password_hash == u2.password_hash)

    def guest_is_default(self):
        Role.insert_roles()
        guest = Role.query.filter_by(name='Guest').first()
        default = Role.query.filter_by(default=True).first()
        self.assertTrue(guest.id == default.id)

    def test_default_user_role_is_guest(self):
        Role.insert_roles()
        u = User(username='Test Guest', password='password')
        guest = Role.query.filter_by(name='Guest').first()
        self.assertTrue(u.role_id == guest.id)

    def test_guest_role(self):
        Role.insert_roles()
        u = User(username='Test Guest', password='password')
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.is_admin())
        self.assertFalse(u.can(Permission.ADMIN))

