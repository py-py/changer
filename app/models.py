from datetime import datetime
from flask import current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import login_manager

__author__ = 'py'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    MAKE_OPERATION = 0x01
    MAKE_COLLECTION = 0x02
    SHOW_STATUS = 0x04
    MODERATE = 0x08
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref='user')

    cash_id = db.Column(db.Integer, db.ForeignKey('cashes.id'))
    cash = db.relationship('Cashes', backref='user')

    group_id = db.Column(db.Integer, db.ForeignKey('group_cashes.id'), default=1)
    group = db.relationship('GroupOfCashes', backref='user')

    deals = db.relationship('Deals', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    collections = db.relationship('Collections', backref='user')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role == Role.query.filter_by(name='Collector').first():
            self.group_id = GroupOfCashes.query.filter_by(group_branch='GR00').first().id

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise "Password isn't readable attribute"

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def insert_user():
        check_user = User.query.filter_by(username='dadmin').first()
        check_role = Role.query.filter_by(permissions=0xff).first()
        if check_role is None:
            raise "No roles in db"
        if check_user is None:
            dadmin = User(username='dadmin',
                          password='dadmin01')
            dadmin.role = Role.query.filter_by(permissions=0xff).first()
            db.session.add(dadmin)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


# List of User;
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {'User': (Permission.MAKE_OPERATION |
                          Permission.MAKE_COLLECTION, True, 'Пользователь'),
                 'Boss': (Permission.SHOW_STATUS |
                          Permission.MODERATE, False, 'Руководитель'),
                 'Collector': (Permission.MAKE_OPERATION |
                               Permission.MAKE_COLLECTION |
                               Permission.SHOW_STATUS, False, 'Инкассатор'),
                 'Moderate': (Permission.MAKE_OPERATION |
                              Permission.MAKE_COLLECTION |
                              Permission.SHOW_STATUS |
                              Permission.MODERATE, False, 'Модератор'),
                 'Administrator': (0xff, False, 'Администратор')
                 }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            role.description = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


# List of Currency;
class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    @staticmethod
    def insert_currency():
        list_currency = ['UAH', 'EUR', 'USD', 'RUB']
        for c in list_currency:
            cur = Currency.query.filter_by(name=c).first()
            if cur is None:
                cur = Currency(name=c)
                db.session.add(cur)
        db.session.commit()

    def __repr__(self):
        return '<Currency %r>' % self.name


# List group of Cashes;
class GroupOfCashes(db.Model):
    __tablename__ = 'group_cashes'
    id = db.Column(db.Integer, primary_key=True)
    group_branch = db.Column(db.String(8), unique=True)
    group_description = db.Column(db.String(64))
    main = db.Column(db.Boolean, default=False)

    @staticmethod
    def insert_group():
        if not GroupOfCashes.query.filter_by(group_branch='GR00').first():
            first_group = GroupOfCashes(group_branch='GR00',
                                        group_description='Main Group',
                                        main=True)
            db.session.add(first_group)

    def __repr__(self):
        return '<Group %s>' % self.id


# List of Cashes;
class Cashes(db.Model):
    __tablename__ = 'cashes'
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(8))
    address = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_cashes.id'))

    group = db.relationship('GroupOfCashes', backref='cash')
    deals = db.relationship('Deals', backref='cash', lazy='dynamic')
    collections = db.relationship('Collections', backref='cash')
    transactions = db.relationship('Transaction', backref='cash')

    @staticmethod
    def insert_cashes():
        main_group = GroupOfCashes.query.filter_by(main=True).first()
        if not Cashes.query.filter_by(branch='CH00').first():
            cash = Cashes(branch='CH00',
                          address='HeadOffice',
                          group=main_group)
            db.session.add(cash)
            deal = Deals(user_id=User.query.filter_by(username='dadmin').first().id,
                         cash_id=Cashes.query.first().id,
                         count_uah=0,
                         count_eur=0,
                         count_usd=0,
                         count_rub=0)
            db.session.add(deal)
            db.session.commit()
            return 'CH00 added'

    def __repr__(self):
        return '<Branch %s %s>' % (self.branch, self.address)


# Сделки и остатки по кассам;
class Deals(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cash_id = db.Column(db.Integer, db.ForeignKey('cashes.id'))
    inkass = db.Column(db.Boolean, default=False)  # inkass = 1 - YES;
    inkass_notes = db.Column(db.String(64))
    date_operation = db.Column(db.DateTime, default=datetime.utcnow)
    count_uah = db.Column(db.Float)
    currency_usd = db.Column(db.Float, default=0)
    count_usd = db.Column(db.Float)
    currency_eur = db.Column(db.Float, default=0)
    count_eur = db.Column(db.Float)
    currency_rub = db.Column(db.Float, default=0)
    count_rub = db.Column(db.Float)

    def __repr__(self):
        return '<Deals %s>' % (self.id)


# Type Of Operation: SELL, BUY and other;
class TypeOfOperation(db.Model):
    __tablename__ = 'type_of_operation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    rusname = db.Column(db.String(8))

    @staticmethod
    def insert_operation():
        list_operation = [('BUY', 'Покупка'),
                          ('SELL', 'Продажа'),
                          ('GET', 'Получить'),
                          ('GIVE', 'Отдать')]
        for i in list_operation:
            checked_transaction = TypeOfOperation.query.filter_by(name=i[0]).first()
            if checked_transaction is None:
                oper = TypeOfOperation(name=i[0], rusname=i[1])
                db.session.add(oper)
        db.session.commit()

    def __repr__(self):
        return '<TypeOfOperation %s>' % self.name


# Список всех транзакций;
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cash_id = db.Column(db.Integer, db.ForeignKey('cashes.id'))
    date_trans = db.Column(db.DateTime, default=datetime.utcnow)
    oper_id = db.Column(db.Integer, db.ForeignKey('type_of_operation.id'))
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    course = db.Column(db.Float, nullable=False)
    count = db.Column(db.Float, nullable=False)
    result = db.Column(db.Float, nullable=False)

    currency = db.relationship('Currency')
    oper = db.relationship('TypeOfOperation')

    def __repr__(self):
        return '<Transaction %s>' % self.id


# Список всех инкассаций;
class Collections(db.Model):
    __tablename__ = "collections"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cash_id = db.Column(db.Integer, db.ForeignKey('cashes.id'))
    date_collection = db.Column(db.DateTime, default=datetime.utcnow)
    oper_id = db.Column(db.Integer, db.ForeignKey('type_of_operation.id'))
    collection_notes = db.Column(db.String(64))
    count_uah = db.Column(db.Float)
    count_usd = db.Column(db.Float)
    count_eur = db.Column(db.Float)
    count_rub = db.Column(db.Float)

    oper = db.relationship('TypeOfOperation')

    def __repr__(self):
        return '<Collections %s>' % self.id


class WalletCollector(db.Model):
    __tablename__ = "wallet_collector"

    id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_operation = db.Column(db.DateTime, default=datetime.utcnow)
    oper_id = db.Column(db.Integer, db.ForeignKey('type_of_operation.id'))

    def __repr__(self):
        return '<WalletCollector %s>' % self.id
