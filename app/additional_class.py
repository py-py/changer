from datetime import datetime, timedelta
from itertools import zip_longest
from app import dec, db
from app.models import CashState, Currency, TypeOfOperation, Transaction, User, CollectorState, Cashes, Collection
from config import config

__author__ = 'py'

NATIONAL_CURRENCY = config['default'].NATIONAL_CURRENCY
TIME_BETWEEN_OPERATION = config['default'].TIME_BETWEEN_OPERATION


# Class for making operation in cash;
class OperationDeal:
    """Make operation with deals"""

    def __init__(self, user):
        self.user = user

    def update_for_making_deal(self, request):
        self.__oper_short = str(request.get('oper')).upper()
        self.__cur_short = str(request.get('curren')).upper()
        self.course = dec(request.get('course'))
        self.value = dec(request.get('sum'))
        self.result = dec(request.get('result'))

    @property
    def operation(self):
        return TypeOfOperation.query.filter_by(name=self.__oper_short).first()

    @property
    def currency(self):
        return Currency.query.filter_by(name=self.__cur_short).first()

    @staticmethod
    def __get_available_currency():
        return Currency.query.all()

    @staticmethod
    def __get_national_currency():
        return Currency.query.filter_by(name=NATIONAL_CURRENCY).first()

    def get_current_cash(self):
        return self.user.cash

    def get_last_state_each_currency(self):
        temp_state_cash = {}
        for i in self.__get_available_currency():
            temp_state_cash[i] = CashState.query. \
                filter_by(cash=self.get_current_cash()). \
                filter_by(currency=i).order_by(CashState.id.desc()).first()
        return temp_state_cash

    def get_last_state_each_currency_for_template(self):
        my_dict = {}
        for i, k in self.get_last_state_each_currency().items():
            my_dict[i.name] = k.value
        return my_dict

    # Check available money in DIFFERENT CURRENCY in cash for SELLING;
    def __differential_currency(self):
        return self.get_last_state_each_currency()[self.currency].value - self.value

    def __addition_national(self):
        return self.get_last_state_each_currency()[self.__get_national_currency()].value + self.result

    def check_available_currency(self):
        return True if self.__differential_currency() >= 0 else False

    def sell(self):
        if self.check_available_currency():
            update_cashstate_currency = CashState(user=self.user._get_current_object(),
                                                  cash=self.get_current_cash(),
                                                  currency=self.currency,
                                                  value=self.__differential_currency())
            update_cashstate_national = CashState(user=self.user._get_current_object(),
                                                  cash=self.get_current_cash(),
                                                  currency=self.__get_national_currency(),
                                                  value=self.__addition_national())
            db.session.add(update_cashstate_currency)
            db.session.add(update_cashstate_national)
        else:
            raise "Don't enough %s money in cash" % self.currency.name

    # Check available money in NATIONAL_CURRENCY in cash for BUYING other currency;
    def __addition_currency(self):
        return self.get_last_state_each_currency()[self.currency].value + self.value

    def __differential_national(self):
        return self.get_last_state_each_currency()[self.__get_national_currency()].value - self.result

    def check_available_national(self):
        return True if self.__differential_national() >= 0 else False

    def buy(self):
        if self.check_available_national():
            update_cashstate_currency = CashState(user=self.user._get_current_object(),
                                                  cash=self.get_current_cash(),
                                                  currency=self.currency,
                                                  value=self.__addition_currency())
            update_cashstate_national = CashState(user=self.user._get_current_object(),
                                                  cash=self.get_current_cash(),
                                                  currency=self.__get_national_currency(),
                                                  value=self.__differential_national())
            db.session.add(update_cashstate_currency)
            db.session.add(update_cashstate_national)
        else:
            raise "Don't enough %s money in cash" % self.__get_national_currency().name

    def comparing_transaction(self):
        last_transaction = Transaction.query\
            .filter_by(user=self.user)\
            .filter_by(status=True)\
            .order_by(Transaction.id.desc())\
            .first()
        print(last_transaction)

        permit_transaction = True
        if last_transaction:
            if (self.user._get_current_object() == last_transaction.user) \
                and (self.get_current_cash() == last_transaction.cash) \
                and (self.operation == last_transaction.oper) \
                and (self.currency == last_transaction.currency) \
                and (self.course == last_transaction.course) \
                and (self.value == last_transaction.count):

                if (datetime.utcnow() - last_transaction.date_trans).days == 0 \
                    and (datetime.utcnow() - last_transaction.date_trans).seconds <= TIME_BETWEEN_OPERATION:
                    permit_transaction = False
        return permit_transaction

    def make_transaction(self):
        transaction = Transaction(user=self.user._get_current_object(),
                                  cash=self.get_current_cash(),
                                  currency=self.currency,
                                  oper=self.operation,
                                  course=self.course,
                                  count=self.value,
                                  result=self.result)
        db.session.add(transaction)


# Class for uploading the cashes;
class OperationCollection:
    """Make operation with collection"""

    def __init__(self, user):
        self.user = user

    def update_for_making_collection(self, request):
        self.__form_comment = request.form.get('comment')
        self.__form_collector_id = int(request.form.get('select_collector'))
        self.form_operation = request.form.get('oper')

        self.dict_request_currency = {}
        for i in self.__get_available_currency():
            if i.name in dict(request.form):
                self.dict_request_currency[i] = dec(request.form[i.name])

    @property
    def collector(self):
        return User.query.filter_by(id=self.__form_collector_id).first()

    @property
    def operation_get(self):
        return TypeOfOperation.query.filter_by(name='GET').first()

    @property
    def operation_give(self):
        return TypeOfOperation.query.filter_by(name='GIVE').first()

    @staticmethod
    def __get_available_currency():
        return Currency.query.all()

    def __create_collection_session(self, currency):
        operation = self.operation_get if self.form_operation == 'GET' else self.operation_give
        collection = Collection(user=self.user._get_current_object(),
                                cash=self.user.cash,
                                oper=operation,
                                currency=currency,
                                value=self.dict_request_currency[currency],
                                note=self.__form_comment)
        db.session.add(collection)

    def get_wallet_current_collector(self, person=None):
        person = person if person else self.collector
        wallet = OperationWalletCollection()
        wallet.collector = person
        return wallet.get_last_state_each_currency()

    def __getting_money(self, future_branch, future_collector):
        for i in self.dict_request_currency:
            if self.dict_request_currency[i] > 0:
                update_cash_state = CashState(user=self.user._get_current_object(),
                                              cash=self.user.cash,
                                              operation=self.operation_give,
                                              currency=i,
                                              value=future_branch[i],
                                              collector=self.collector)
                db.session.add(update_cash_state)
                update_collector_state = CollectorState(user=self.collector,
                                                        operation=self.operation_get,
                                                        currency=i,
                                                        value=future_collector[i])
                db.session.add(update_collector_state)
                self.__create_collection_session(i)

    def get_money_from_branch(self):
        future_result_for_branch = {}
        future_result_for_collector = {}
        money_branch = CashPlus().get_count_values_one_cash(self.user.cash)[1]

        for i in self.dict_request_currency:
            if money_branch[i.name].value >= self.dict_request_currency[i]:
                future_result_for_branch[i] = money_branch[i.name].value - self.dict_request_currency[i]
                future_result_for_collector[i] = self.get_wallet_current_collector()[i].value + \
                                                 self.dict_request_currency[i]
        self.__getting_money(future_result_for_branch, future_result_for_collector)

    def __giving_money(self, future_branch, future_collector):
        for i in self.dict_request_currency:
            if self.dict_request_currency[i] > 0:
                update_cash_state = CashState(user=self.user._get_current_object(),
                                              cash=self.user.cash,
                                              operation=self.operation_get,
                                              currency=i,
                                              value=future_branch[i],
                                              collector=self.collector)
                db.session.add(update_cash_state)
                update_collector_state = CollectorState(user=self.collector,
                                                        operation=self.operation_give,
                                                        currency=i,
                                                        value=future_collector[i])
                db.session.add(update_collector_state)
                self.__create_collection_session(i)

    def give_money_to_branch(self):
        future_result_for_branch = {}
        future_result_for_collector = {}
        money_branch = CashPlus().get_count_values_one_cash(self.user.cash)[1]

        for i in self.dict_request_currency:
            if self.get_wallet_current_collector()[i].value >= self.dict_request_currency[i]:
                future_result_for_branch[i] = money_branch[i.name].value + self.dict_request_currency[i]
                future_result_for_collector[i] = self.get_wallet_current_collector()[i].value - \
                                                 self.dict_request_currency[i]
        self.__giving_money(future_result_for_branch, future_result_for_collector)

    def __giving_to_other_collector(self, future_result_for_me, future_result_for_other):
        for i in self.dict_request_currency:
            if self.dict_request_currency[i] > 0:
                update_my_wallet = CollectorState(user=self.user,
                                                  operation=self.operation_give,
                                                  currency=i,
                                                  value=future_result_for_me[i])
                db.session.add(update_my_wallet)
                update_other_wallet = CollectorState(user=self.collector,
                                                     operation=self.operation_get,
                                                     currency=i,
                                                     value=future_result_for_other[i])
                db.session.add(update_other_wallet)


    def give_money_to_collector(self):
        future_result_for_me = {}
        future_result_for_other = {}

        my_wallet = self.get_wallet_current_collector(self.user)
        other_wallet = self.get_wallet_current_collector()

        for i in self.dict_request_currency:
            if my_wallet[i].value >= self.dict_request_currency[i]:
                future_result_for_me[i] = my_wallet[i].value - self.dict_request_currency[i]
                future_result_for_other[i] = other_wallet[i].value + self.dict_request_currency[i]

        self.__giving_to_other_collector(future_result_for_me, future_result_for_other)


# Class for uploading the wallet of collector;
class OperationWalletCollection:

    def upload_for_making_walletcollection(self, request):
        self.dict_request_currency = {}
        self.__form_collector_id = request.form.get('select_collector')
        self.__form_oper = request.form.get('oper')
        self._collector = User.query.filter_by(id=self.__form_collector_id).first()

        for i in self.__get_available_currency():
            if i.name in dict(request.form):
                self.dict_request_currency[i] = dec(request.form[i.name])

    @property
    def collector(self):
        return self._collector

    @collector.setter
    def collector(self, name):
        self._collector = name

    @property
    def operation(self):
        return TypeOfOperation.query.filter_by(name=self.__form_oper).first()

    @staticmethod
    def __get_available_currency():
        return Currency.query.all()

    @staticmethod
    def __get_national_currency():
        return Currency.query.filter_by(name=NATIONAL_CURRENCY).first()

    def get_last_state_each_currency(self):
        temp_state_cash = {}
        for i in self.__get_available_currency():
            temp_state_cash[i] = CollectorState.query. \
                filter_by(user=self.collector). \
                filter_by(currency=i).order_by(CollectorState.id.desc()).first()
        return temp_state_cash

    def get_from_boss(self):
        last_state = self.get_last_state_each_currency()
        for i in self.__get_available_currency():
            add_values = dec(self.dict_request_currency[i] + last_state[i].value)
            if add_values > 0:
                final_state = CollectorState(user=self.collector,
                                             operation=self.operation,
                                             currency=i,
                                             value=add_values)
                db.session.add(final_state)

    def give_to_boss(self):
        last_state = self.get_last_state_each_currency()
        for i in self.__get_available_currency():
            sub_values = dec(last_state[i].value - self.dict_request_currency[i])
            if sub_values > 0:
                final_state = CollectorState(user=self.collector,
                                             operation=self.operation,
                                             currency=i,
                                             value=sub_values)
                db.session.add(final_state)
            else:
                raise "Not enought %s currency" % i.name

    def get_wallet_of_one_for_template(self):
        dict_i = {}
        for c in self.__get_available_currency():
            dict_i[c.name] = CollectorState.query.filter_by(user=self.collector) \
                .filter_by(currency=c) \
                .order_by(CollectorState.id.desc()) \
                .first().value
        return dict_i

    def get_wallets_of_collectors_for_template(self, people):
        wallets_people_collector = []

        for i in people:
            dict_i = {}
            for c in self.__get_available_currency():
                dict_i[c.name] = CollectorState.query.filter_by(user=i) \
                    .filter_by(currency=c) \
                    .order_by(CollectorState.id.desc()) \
                    .first().value
            wallets_people_collector.append((i.username, dict_i))
        return wallets_people_collector


# Operation Boss Avarage Currency;
class OperationBossAverageCurrency:
    def __init__(self, transaction):
        self.transaction = transaction

    def __recognize(self, transaction):
        oper = transaction.oper
        currency = transaction.currency
        course = transaction.course
        sum = transaction.count
        cash = transaction.cash
        return oper.name, currency.name, (course, sum), cash

    def __get_average(self, data):
        for cash, level01 in data.items():
            for currency, level02 in level01.items():
                for oper, every in level02.items():
                    d = {'sum': 0, 'avarage_course': 0}
                    for c, r in every:
                        if not d['avarage_course']:
                            d['sum'] += r
                            d['avarage_course'] = c
                        else:
                            first_sum = d['sum']
                            first_avarage = d['avarage_course']
                            second_sum = r
                            second_avarage = c
                            result_sum = first_sum + second_sum
                            result_avarage = first_avarage * (first_sum / result_sum) + \
                                             second_avarage * (second_sum / result_sum)
                            d['sum'] = result_sum
                            d['avarage_course'] = result_avarage
                    data[cash][currency][oper] = d
        return data

    def get_list_average_course(self):
        access_operation = TypeOfOperation.query.all()
        access_currency = Currency.query.all()
        list_branches = Cashes.query.all()
        d_full = {cash:
                      {x.name:
                           {x.name: []
                            for x in access_operation if x.name in ('BUY', 'SELL')}
                       for x in access_currency}
                  for cash in list_branches}
        for i in self.transaction:
            r = self.__recognize(i)
            d_full[r[3]][r[1]][r[0]].append(r[2])
        return self.__get_average(d_full)


class Report:
    def __init__(self, branch):
        self.branch = branch

    # Disassemble each transaction;
    def __recognize(self, transaction):
        operation = transaction.oper
        currency = transaction.currency
        course = transaction.course
        sum = transaction.count
        branch = transaction.cash
        return operation.name, currency.name, (course, sum), branch

    def __get_avarage(self, data):
        for cash, level01 in data.items():
            for currency, level02 in level01.items():
                for oper, every in level02.items():
                    d = {'sum': 0, 'avarage_course': 0}
                    for c, r in every:
                        if not d['avarage_course']:
                            d['sum'] += r
                            d['avarage_course'] = c
                        else:
                            first_sum = d['sum']
                            first_avarage = d['avarage_course']
                            second_sum = r
                            second_avarage = c
                            result_sum = first_sum + second_sum
                            result_avarage = first_avarage * (first_sum / result_sum) + \
                                             second_avarage * (second_sum / result_sum)
                            d['sum'] = result_sum
                            d['avarage_course'] = result_avarage
                    data[cash][currency][oper] = d
        return data

    # Main method for creating report;
    def create_report(self, data):
        access_operation = TypeOfOperation.query.all()
        access_currency = Currency.query.all()
        list_branches = Cashes.query.all()
        d_full = {cash:
                      {x.name:
                           {x.name: [] for x in access_operation if x.name in ('BUY', 'SELL')}
                       for x in access_currency}
                  for cash in list_branches}
        for i in data:
            r = self.__recognize(i)
            d_full[r[3]][r[1]][r[0]].append(r[2])
        return self.__get_avarage(d_full)

    def __summing_currency(self, data):
        for k1, _ in data.items():
            for k2, i in _.items():
                d = {}
                for x, y in i:
                    if x in d:
                        d[x] = d[x] + y
                    else:
                        d[x] = y
                data[k1][k2] = d

    def main_list_states(self, data):
        access_operation = TypeOfOperation.query.all()
        access_currency = Currency.query.all()
        my_dict = {x.name: {x.name: [] for x in access_operation if x.name in ('BUY', 'SELL')} for x in access_currency}
        for i in data:
            r = self.__recognize(i)
            my_dict[r[1]][r[0]].append(r[2])
        self.__summing_currency(my_dict)
        for i in my_dict:
            a = my_dict[i]['BUY'].items()
            b = my_dict[i]['SELL'].items()
            my_dict[i]['OPERATION'] = list(zip_longest(a, b, fillvalue=(0, 0)))
        return my_dict


# Additional Class for working with datetime_module;
class DatePlus:
    start_full_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    finish_full_today = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    today = datetime.utcnow().date()

    def use_tz(self, tz_minute):
        return datetime.utcnow() + timedelta(minutes=int(tz_minute))

    def start_used_tz(self, d_start, tz_minute):
        start_date = datetime.strptime(d_start, '%d-%m-%Y').replace(hour=0, minute=0, second=0, microsecond=0)
        return start_date - timedelta(minutes=int(tz_minute))

    def finish_used_tz(self, d_finish, tz_minute):
        finish_date = datetime.strptime(d_finish, '%d-%m-%Y').replace(hour=23, minute=59, second=59, microsecond=999999)
        return finish_date - timedelta(minutes=int(tz_minute))

    def today_start_user_tz(self, tz_minute):
        start_date = self.start_full_today
        return start_date + timedelta(minutes=int(tz_minute))

    def today_finish_user_tz(self, tz_minute):
        finish_date = self.finish_full_today
        return finish_date + timedelta(minutes=int(tz_minute))


# Additional Class for working with CASH;
class CashPlus:
    """Additional Class for branches"""

    def get_count_values_one_cash(self, branch):
        dict_currencies_current_cash = {}
        for i in self.__get_currencies():
            dict_currencies_current_cash[i.name] = CashState.query \
                .filter_by(cash=branch) \
                .filter_by(currency=i) \
                .order_by(CashState.id.desc()) \
                .first()
        return branch, dict_currencies_current_cash

    def get_count_values_many_cashes(self):
        full_list_of_many_cashes = []
        for cash in self.get_list_active_cashes():
            full_list_of_many_cashes.append(self.get_count_values_one_cash(cash))
        return full_list_of_many_cashes

    @staticmethod
    def __get_currencies():
        return Currency.query.all()

    @staticmethod
    def get_list_active_cashes():
        return Cashes.query.filter_by(status=True).all()

    def create_cash_currencies(self, user, branch):
        cash = Cashes.query.filter_by(branch=branch).first()
        operation = TypeOfOperation.query.filter_by(name='GET').first()
        for i in self.__get_currencies():
            cashstate_i = CashState(user=user,
                                    cash=cash,
                                    operation=operation,
                                    currency=i,
                                    value=0)
            db.session.add(cashstate_i)

    def state_start_day(self, branch, start_day, tz):
        start_day = DatePlus().start_used_tz(start_day, tz)
        state_start_dict = {}
        for i in self.__get_currencies():
            try:
                state_start_dict[i.name] = CashState.query \
                    .filter_by(cash=branch) \
                    .filter_by(currency=i) \
                    .filter(CashState.date_operation < start_day) \
                    .order_by(CashState.id.desc()) \
                    .first().value
            except AttributeError:
                state_start_dict[i.name] = 0
        return state_start_dict

    def state_finish_day(self, branch, finish_day, tz):
        finish_day = DatePlus().finish_used_tz(finish_day, tz)
        state_finish_dict = {}
        for i in self.__get_currencies():
            try:
                state_finish_dict[i.name] = CashState.query \
                    .filter_by(cash=branch) \
                    .filter_by(currency=i) \
                    .filter(CashState.date_operation < finish_day) \
                    .order_by(CashState.id.desc()) \
                    .first().value
            except AttributeError:
                state_finish_dict[i.name] = 0
        return state_finish_dict


class TransactionPlus:
    def __init__(self, user):
        self.user = user

    def all_transaction(self):
        return Transaction\
            .query\
            .filter_by(user=self.user)\
            .filter_by(status=True)\
            .all()

    def get_working_user_place(self):
        working_places = [self.user.cash]
        for i in self.all_transaction():
            if i.cash not in working_places:
                working_places.append(i.cash)
        return working_places

    def get_trans_for_one_day(self):
        transaction_current_user = Transaction.query \
            .filter_by(cash=self.user.cash) \
            .filter_by(user=self.user) \
            .filter_by(status=True) \
            .filter(Transaction.date_trans >= DatePlus().today_start_user_tz(self.user.tz)) \
            .filter(Transaction.date_trans <= DatePlus().today_finish_user_tz(self.user.tz)) \
            .all()
        return transaction_current_user

    def get_trans_between_dates_for_user(self,
                                         start_date,
                                         finish_date,
                                         cash=None):
        cash = cash if cash else self.user.cash
        return Transaction.query \
            .filter_by(status=True)\
            .filter(Transaction.date_trans > start_date) \
            .filter(Transaction.date_trans < finish_date) \
            .filter(Transaction.user == self.user) \
            .filter(Transaction.cash == cash) \
            .all()

    def get_trans_between_dates_for_cash(self,
                                         cash,
                                         start_date,
                                         finish_date):
        return Transaction.query \
            .filter_by(status=True)\
            .filter(Transaction.date_trans > start_date) \
            .filter(Transaction.date_trans < finish_date) \
            .filter(Transaction.cash == cash) \
            .all()


class CollectionPlus:
    def __init__(self, user):
        self.user = user

    def all_collection(self):
        return Collection.query.filter_by(user=self.user).all()

    def get_working_user_place(self):
        working_places = [self.user.cash]
        for i in self.all_collection():
            if i.cash not in working_places:
                working_places.append(i.cash)
        return working_places

    def get_collections_for_one_day(self):
        collection_current_user = Collection.query \
            .filter_by(cash=self.user.cash) \
            .filter_by(user=self.user) \
            .filter(Collection.date_collection >= DatePlus().today_start_user_tz(self.user.tz)) \
            .filter(Collection.date_collection <= DatePlus().today_finish_user_tz(self.user.tz)) \
            .all()
        return collection_current_user

    def get_collections_between_dates_for_user(self,
                                               start_date,
                                               finish_date):
        collection_current_user = Collection.query \
            .filter_by(cash=self.user.cash) \
            .filter_by(user=self.user) \
            .filter(Collection.date_collection >= start_date) \
            .filter(Collection.date_collection <= finish_date) \
            .all()
        return collection_current_user


class CancelTransaction():
    """Cancel Transaction - operation for canceling transaction in available time...
    Available time - time which is determined time in config.config"""

    def __init__(self, user, id, branch):
        self.user = user
        self.__transaction = Transaction.query.filter_by(id=id).first()
        self.count_national = self.__transaction.result
        self.currency = self.__transaction.currency.name
        self.count_currency = self.__transaction.count
        self.branch = Cashes.query.filter_by(branch=branch).first()
        self.operation = self.__transaction.oper

    @property
    def national(self):
        return Currency.query.filter_by(name=NATIONAL_CURRENCY).first()

    @property
    def foreign(self):
        return self.__transaction.currency

    @property
    def return_money(self):
        return TypeOfOperation.query.filter_by(name='RETURN').first()

    def __update_cash_state(self, currency, value_of_currency):
        c = CashState(user=self.user,
                      cash=self.branch,
                      operation=self.return_money,
                      currency=currency,
                      value=value_of_currency)
        db.session.add(c)

    def __check_available_money_in_cash(self):
        branch, state_cash = CashPlus().get_count_values_one_cash(self.branch)
        if self.operation.name == 'BUY':
            if (state_cash[self.currency].value - self.count_currency) >= 0:
                different_foreign = state_cash[self.currency].value - self.count_currency
                different_national = state_cash[self.national.name].value + self.count_national
                self.__update_cash_state(self.national, different_national)
                self.__update_cash_state(self.foreign, different_foreign)
                return True

        elif self.operation.name == 'SELL':
            if (state_cash[self.national.name].value - self.count_national) >= 0:
                different_foreign = state_cash[self.currency].value + self.count_currency
                different_national = state_cash[self.national.name].value - self.count_national
                self.__update_cash_state(self.national, different_national)
                self.__update_cash_state(self.foreign, different_foreign)
                return True
        else:
            raise "Don't enough money for making this operation"

    def make_cancel(self):
        state = True if self.__check_available_money_in_cash() else False
        return state

    def __str__(self):
        return 'Transaction № {0}: UAH is {1}, {2} is {3} in {4}'\
            .format(self.__transaction.id,
                    self.count_UAH,
                    self.currency,
                    self.count_currency,
                    self.branch.branch)
