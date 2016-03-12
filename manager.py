from app import create_app
from app import db
from app.models import User, Role, Cashes, Deals, Currency, Transaction, TypeOfOperation
from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager, Shell
__author__ = 'py'


app = create_app(conf_name='default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db,
                User=User,
                Role=Role,
                Cashes=Cashes,
                Deals=Deals,
                Transaction=Transaction,
                Currency=Currency,
                TypeOfOperation=TypeOfOperation)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()


