#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app, mail, db
from app.models import User, Role, Permissions, Post, Follow, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, mail=mail,
                Permissions=Permissions, Post=Post, Follow=Follow,
                Comment = Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
#database migration
manager.add_command("db", MigrateCommand)

@manager.command
def test():
    """Run the unit test."""
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == "__main__":
    manager.run()
