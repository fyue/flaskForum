from selenium import webdriver
from app import create_app, db
from app.models import Role, User, Post
import threading, re, time, unittest, ipdb

class SeleniumTestCase(unittest.TestCase):
    client = None
    
    @classmethod
    def setUpClass(cls):
        """run fierfox"""
        try:
            cls.client = webdriver.Firefox()
            ipdb.set_trace()
        except:
            pass
        """if can't run client, then skips these tests"""
        if cls.client:
            """create program"""
            cls.app = create_app("testing")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            """logging forbidden for clear output"""
            import logging
            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")
            
            """create db and generate fake data"""
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)
            
            """add an Admin"""
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email = "john@example.com",
                         username = "john",
                         password = "cat",
                         role = admin_role,
                         confirmed = True)
            db.session.add(admin)
            db.session.commit()
            
            """run server in a thread"""
            threading.Thread(target=cls.app.run).start()
            
            """give a second to ensure the server is up"""
            time.sleep(1)
            
    @classmethod
    def testDownClass(cls):
        if cls.client:
            """shutdown server and browser"""
            cls.client.get("http://localhost:5000/shutdown")
            cls.client.close()
            
            """remove db"""
            db.drop_all()
            de.session.remove()
            
            """remove app context"""
            cls.app_context.pop()
            
    def setUp(self):
        if not self.client:
            self.skipTest("web browser not available")
            
    def tearDown(self):
        pass
    
    
    def test_admin_home_page(self):
        """navigate to home page"""
        self.client.get("http://localhost:5000/")
        self.assertTrue(re.search("你好,\s+熟悉的陌生人!", self.client.page_source))
        
        """navigate to log-in websides"""
        self.client.find_element_by_link_text("登陆").click()
        self.assertTrue("<h1>登陆</h1>" in self.client.page_source)
        
        """log in"""
        self.client.find_element_by_name("email").\
            send_keys("john@example.com")
        self.client.find_element_by_name("password").send_keys("cat")
        self.client.find_element_by_name("submit").click()
        self.assertTrue(re.search("你好,\s+john!", self.client.page_source))
        
        """enter profile"""
        self.client.find_element_by_link_text("个人信息").click()
        self.assertTrue("<h1>john</h1>" in self.client.page_source)
            