import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db, fake
from app.models import User, Post, Tag, post_tags, Role, Permission, AnonymousUser

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome-stable'
        #options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(chrome_options=options, executable_path='/home/marshall/dev/chromedriver')
        except Exception as e:
            print(e)
        if not cls.client:
            cls.skipTest('Web browser not available')

        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        db.session.commit()
        #self.app_context = self.app.app_context()
        #self.app_context.push()

        #time.sleep(5)
        # suppress logging to keep unittest output clean
        import logging
        logger = logging.getLogger('werkzeug')
        logger.setLevel("ERROR")

        # create the database and populate with some fake data
        Role.insert_roles()
        fake.users(10)
        fake.posts(10)

        # add an administrator user
        admin_role = Role.query.filter_by(name='Administrator').first()
        admin = User(name='Admin', username='admin', password='adminpassword',
                     role=admin_role)
        db.session.add(admin)
        db.session.commit()

        os.environ.pop("FLASK_RUN_FROM_CLI")
        cls.server_thread = threading.Thread(target=cls.app.run,
                                             kwargs={'debug': 'false',
                                                     'use_reloader': False,
                                                     'use_debugger': False}
                                             )
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

        cls.client.quit()
        cls.server_thread.join()

    def setUp(self):
        if not self.client:
            self.skipTest('Browser not available')

    def tearDown(self):
        pass

    def test_app_exists(self):
        self.assertFalse(self.app is None)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_new_post_requires_login(self):
        self.client.get('http://localhost:5000/new_post')
        self.assertIn('Please log in to access this page.', self.client.page_source)

    def test_edit_post_requires_login(self):
        p = Post.query.first()
        url = 'http://localhost:5000/edit/' + str(p.id)
        self.client.get(url)
        self.assertIn('Please log in to access this page.', self.client.page_source)

    """
    def test_login_new_post(self):
        self.client.get('http://localhost:5000/')
        self.client.find_element(By.LINK_TEXT, 'Log In').click()

        self.assertIn('Username', self.client.page_source)
        e = self.client.find_element(By.ID, 'username')
        e.send_keys('admin')
        e = self.client.find_element(By.ID, 'password')
        e.send_keys('adminpassword')
        e = self.client.find_element(By.ID, 'submit')
        e.click()

        self.assertIn('New Post', self.client.page_source)

        self.client.find_element(By.LINK_TEXT, 'New Post').click()
        e = self.client.find_element(By.ID, 'title')
        e.send_keys('Selenium Test Post')

        iframe = self.client.find_element(By.CLASS_NAME, "#modal > iframe")
        self.client.switch_to.frame(iframe)
        e = self.client.find_element(By.TAG_NAME, 'body')
        e.send_keys('Selenium Test Post')

        self.client.find_element(By.ID, 'submit').click()
        self.assertIn('Selenium Test Post', self.client.page_source)

        self.assertIn('Log Out', self.client.page_source)
        self.client.find_element(By.LINK_TEXT, 'Log Out').click()
    """

    def test_login_logout(self):
        self.client.get('http://localhost:5000/')
        self.client.find_element(By.LINK_TEXT, 'Log In').click()
        self.assertIn('Username', self.client.page_source)
        e = self.client.find_element(By.ID, 'username')
        e.send_keys('admin')

        e = self.client.find_element(By.ID, 'password')
        e.send_keys('adminpassword')

        e = self.client.find_element(By.ID, 'submit')
        e.click()

        self.assertIn('Log Out', self.client.page_source)
        self.client.find_element(By.LINK_TEXT, 'Log Out').click()
        self.assertIn('Log In', self.client.page_source)



