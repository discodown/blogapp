import unittest
from flask import current_app
from app import create_app, db
from app.models import *

class TagTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_tag(self):
        t = Tag(name="test")
        db.session.add(t)
        self.assertTrue(Tag.query.get("test") is not None)

    def test_add_tag_to_post(self):
        p = Post(body="Test Post")
        db.session.add(p)
        p.tag("test_post_tag")
        post = Tag.query.get("test_post_tag").get_posts().first()
        self.assertTrue(post.body=="Test Post")

    def test_get_all_tags(self):
        p = Post(body="Test Post 2")
        db.session.add(p)
        p.tag("test_post_tag1")
        p.tag("test_post_tag2")
        p.tag("test_post_tag3")
        tags = Tag.query.all()
        self.assertTrue(len(tags) == 3)
        self.assertTrue(tags[0].name == "test_post_tag1")
        self.assertTrue(tags[1].name == "test_post_tag2")
        self.assertTrue(tags[2].name == "test_post_tag3")

    def test_get_tagged_posts(self):
        p1 = Post(body="Test Post 3")
        p2 = Post(body="Test Post 4")
        p3 = Post(body="Test Post 5")
        db.session.add_all([p1, p2, p3])
        p1.tag("test_post_tag4")
        p2.tag("test_post_tag4")
        p3.tag("test_post_tag4")

        posts = Tag.query.get("test_post_tag4").get_posts().all()
        self.assertTrue(len(posts) == 3)
        self.assertTrue(posts[0].body == "Test Post 3")
        self.assertTrue(posts[1].body == "Test Post 4")
        self.assertTrue(posts[2].body == "Test Post 5")

    def test_get_post_tags(self):
        p = Post(body="Test Post 6")
        db.session.add(p)
        p.tag("test_post_tag5")
        p.tag("test_post_tag6")
        p.tag("test_post_tag7")
        post = Tag.query.get("test_post_tag5").get_posts().first()
        self.assertTrue(len(post.tags) == 3)
        self.assertTrue(post.tags[0].name == "test_post_tag5")
        self.assertTrue(post.tags[1].name == "test_post_tag6")
        self.assertTrue(post.tags[2].name == "test_post_tag7")