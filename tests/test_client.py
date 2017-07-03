# -*- coding: utf-8 -*- 

import unittest
import re
from app import create_app, db
from app.models import User, Role
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies = True)
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_home_page(self):
        response = self.client.get(url_for("main.index"))
        self.assertTrue(re.search("你好\s+!", response.get_data(as_text = True)))
        
    """
    def test_register_and_login(self):
        #register new account
        response = self.client.post(url_for("auth.register"), data = {
            "email": "john@example.com",
            "username": "john",
            "password": "cat",
            "password2": "cat"                                                              
        })
        self.assertTrue(response.status_code == 302)
        
        #log in with new register account
        response = self.client.post(url_for("auth.login"), data = {
            "email": "john@example.com",
            "password": "cat"                                                         
        }, follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertTrue(re.search(r"john", data))
        self.assertTrue("您还没有验证您的账户" in data)
        
        #send confir_token
        user = User.query.filter_by(email = "john@example.com").first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for("auth.confirm", token = token),
                                   follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertTrue("您现在已经确认了账户, 谢谢!" in data)
        
        #log out
        response = self.client.get(url_for("auth.logout"),
                                   follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertTrue("你已顺利退出" in data)
    """
        
        
        
        
        
        
        
        
        
        
        
