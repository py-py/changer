# coding: utf8
from datetime import datetime, timedelta
from itertools import zip_longest
from app import db, dec
from app.decorators import user_required
from app.models import Cashes, Role, User, Deals, TypeOfOperation, Currency, Transaction, Collections, Permission, \
    WalletCollector
from flask import render_template, request, flash, url_for, redirect, json
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from . import main

__author__ = 'py'


@main.route('/', methods=['GET', 'POST'])
@login_required
@user_required
def index():
    cash_state = Deals.query.filter_by(cash_id=current_user.cash_id).order_by(Deals.id.desc()).first()
    if request.method == 'POST':
        inputed_operation = str(request.form['oper'])
        inputed_currency = str(request.form['curren'])
        inputed_course = dec(request.form['course'])
        inputed_sum = dec(request.form['sum'])
        inputed_result = dec(request.form['result'])
        # Insert info in Transaction table;
        new_transaction = Transaction(user_id=current_user.id,
                                      cash=current_user.cash,
                                      currency=Currency.query.filter_by(name=inputed_currency).first(),
                                      oper=TypeOfOperation.query.filter_by(name=inputed_operation).first(),
                                      course=inputed_course,
                                      count=inputed_sum,
                                      result=inputed_result)
        db.session.add(new_transaction)
        # finish insert in Transaction table;
        if inputed_operation == 'BUY':
            if inputed_currency == 'USD':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_usd=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah - inputed_result),
                                 count_eur=dec(cash_state.count_eur),
                                 count_usd=dec(cash_state.count_usd + inputed_sum),
                                 count_rub=dec(cash_state.count_rub))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
            if inputed_currency == 'EUR':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_eur=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah - inputed_result),
                                 count_eur=dec(cash_state.count_eur + inputed_sum),
                                 count_usd=dec(cash_state.count_usd),
                                 count_rub=dec(cash_state.count_rub))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
            if inputed_currency == 'RUB':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_rub=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah - inputed_result),
                                 count_eur=dec(cash_state.count_eur),
                                 count_usd=dec(cash_state.count_usd),
                                 count_rub=dec(cash_state.count_rub + inputed_sum))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
        elif inputed_operation == 'SELL':
            if inputed_currency == 'USD':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_usd=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah + inputed_result),
                                 count_eur=dec(cash_state.count_eur),
                                 count_usd=dec(cash_state.count_usd - inputed_sum),
                                 count_rub=dec(cash_state.count_rub))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
            if inputed_currency == 'EUR':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_eur=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah + inputed_result),
                                 count_eur=dec(cash_state.count_eur - inputed_sum),
                                 count_usd=dec(cash_state.count_usd),
                                 count_rub=dec(cash_state.count_rub))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
            if inputed_currency == 'RUB':
                new_deal = Deals(user_id=current_user.id,
                                 cash=current_user.cash,
                                 currency_rub=dec(inputed_course),
                                 count_uah=dec(cash_state.count_uah + inputed_result),
                                 count_eur=dec(cash_state.count_eur),
                                 count_usd=dec(cash_state.count_usd),
                                 count_rub=dec(cash_state.count_rub - inputed_sum))
                db.session.add(new_deal)
                flash('Проведена операция. Обновлены остатки по кассе.', 'success')
                return redirect(url_for('main.index'))
        else:
            flash('Операция не проведена... Какие-то ошибки.')
            return redirect(url_for('main.index'))
    return render_template('main.html', cash_state=cash_state)


@main.route('/collections', methods=['GET', 'POST'])
@login_required
@user_required
def collections():
    cash_state = Deals.query.filter_by(cash_id=current_user.cash_id).order_by(Deals.id.desc()).first()
    collectors = User.query.filter_by(role=Role.query.filter_by(name='Collector').first()).all()

    if request.method == 'POST':
        try:
            oper = str(request.form['oper'])
        except BadRequestKeyError:
            oper = None
        comment = str(request.form['comment'])

        UAH = dec(request.form['UAH'])
        EUR = dec(request.form['EUR'])
        USD = dec(request.form['USD'])
        RUB = dec(request.form['RUB'])
        collector_id = str(request.form['select_collector'])

        current_collector = User.query.filter_by(id=collector_id).first()
        current_wallet = WalletCollector.query.filter_by(collector=current_collector).order_by(
            WalletCollector.id.desc()).first()

        new_collection = Collections(user_id=current_user.id,
                                     cash_id=current_user.cash_id,
                                     oper=TypeOfOperation.query.filter_by(name=oper).first(),
                                     collection_notes=comment,
                                     count_uah=UAH,
                                     count_eur=EUR,
                                     count_usd=USD,
                                     count_rub=RUB)
        db.session.add(new_collection)

        if oper == 'GET':
            new_deal = Deals(user_id=current_user.id,
                             cash_id=current_user.cash_id,
                             inkass=True,
                             inkass_notes=comment,
                             collector_id=current_collector.id,
                             count_uah=dec(cash_state.count_uah + UAH),
                             count_eur=dec(cash_state.count_eur + EUR),
                             count_usd=dec(cash_state.count_usd + USD),
                             count_rub=dec(cash_state.count_rub + RUB))
            db.session.add(new_deal)
            wallet_collector = WalletCollector(collector=current_collector,
                                               oper=TypeOfOperation.query.filter_by(name='GIVE').first(),
                                               count_uah=dec(current_wallet.count_uah - UAH),
                                               count_usd=dec(current_wallet.count_usd - USD),
                                               count_eur=dec(current_wallet.count_eur - EUR),
                                               count_rub=dec(current_wallet.count_rub - RUB))
            db.session.add(wallet_collector)
            flash('Проведена инкассация. Обновлены остатки по кассе.', 'success')
            return redirect(url_for('main.collections'))
        elif oper == 'GIVE':
            new_deal = Deals(user_id=current_user.id,
                             cash_id=current_user.cash_id,
                             inkass=True,
                             inkass_notes=comment,
                             collector_id=current_collector.id,
                             count_uah=dec(cash_state.count_uah - UAH),
                             count_eur=dec(cash_state.count_eur - EUR),
                             count_usd=dec(cash_state.count_usd - USD),
                             count_rub=dec(cash_state.count_rub - RUB))
            db.session.add(new_deal)
            wallet_collector = WalletCollector(collector=current_collector,
                                               oper=TypeOfOperation.query.filter_by(name='GET').first(),
                                               count_uah=dec(current_wallet.count_uah + UAH),
                                               count_usd=dec(current_wallet.count_usd + USD),
                                               count_eur=dec(current_wallet.count_eur + EUR),
                                               count_rub=dec(current_wallet.count_rub + RUB))
            db.session.add(wallet_collector)
            flash('Проведена инкассация. Обновлены остатки по кассе.', 'success')
            return redirect(url_for('main.collections'))
        else:
            flash('Операция не проведена, не выбран тип инкассации: "Получить" или "Передать"', 'danger')
            return redirect(url_for('main.collections'))
    return render_template('collections.html', cash_state=cash_state, collectors=collectors)


@main.route('/collections_collector')
@login_required
# temp
# @user_required
def collections_collector():
    collector_id = request.args['name_id']
    current_collector = User.query.filter_by(id=collector_id).first()
    current_wallet = WalletCollector.query.filter_by(collector=current_collector).order_by(
        WalletCollector.id.desc()).first()
    return json.dumps({'collector': current_collector.username,
                       'UAH': current_wallet.count_uah,
                       'USD': current_wallet.count_usd,
                       'EUR': current_wallet.count_eur,
                       'RUB': current_wallet.count_rub})


@main.route('/user_transaction', methods=['GET', 'POST'])
@login_required
@user_required
def user_transaction():
    d_today = datetime.utcnow().date()

    # Список касс в которых работал текущий сотрудник;
    list_transactions = Transaction.query.filter_by(user=current_user).all()
    cashes = [current_user.cash]
    for i in list_transactions:
        if i.cash not in cashes:
            cashes.append(i.cash)

    # Список транзакций за текущий день;
    trans = []
    for i in list_transactions:
        if i.date_trans.date() == d_today:
            trans.append(i)

    if request.method == 'POST':
        d_start = request.form['data-start']
        dt_start = datetime.strptime(d_start, '%d-%m-%Y') + timedelta(seconds=-120 * 60)
        d_finish = request.form['data-finish']
        dt_finish = datetime.strptime(d_finish, '%d-%m-%Y') + timedelta(seconds=1440 * 60) + timedelta(
            seconds=-120 * 60)
        inputed_cash = request.form['select_ch'].upper()
        cash = Cashes.query.filter(Cashes.branch == inputed_cash).first()
        all_trans = Transaction.query.filter_by(user=current_user).filter_by(cash=cash)
        trans = all_trans.filter(Transaction.date_trans <= dt_finish).filter(Transaction.date_trans >= dt_start).all()
        return render_template("user_transaction.html", cashes=cashes, trans=trans)
    return render_template("user_transaction.html", cashes=cashes, trans=trans)


@main.route('/user_collection', methods=['GET', 'POST'])
@login_required
@user_required
def user_collection():
    d_today = datetime.utcnow().date()
    list_collections = Collections.query.filter_by(user=current_user).all()

    # Список касс в которых инкассировался текущий сотрудник;
    cashes = [current_user.cash]
    for i in list_collections:
        if i.cash not in cashes:
            cashes.append(i.cash)

    # Список инкассаций за текущий день;
    inkasses = []
    for i in list_collections:
        if i.date_collection.date() == d_today:
            inkasses.append(i)

    return render_template('user_collection.html', inkasses=inkasses, cashes=cashes)


@main.route('/change_user', methods=['GET', 'POST'])
@login_required
def change_user():
    if request.method == 'POST':
        pass1 = request.form['new-pass']
        pass2 = request.form['new-pass-repeat']
        if pass1 == pass2:
            flash('Password has updated correctly.')
            user = current_user._get_current_object();
            user.password = pass1;
            db.session.add(user)
            return redirect(url_for('main.change_user'))
        else:
            flash('Password has n\'t updated')
    return render_template('change_user.html', user=current_user)


#############################
def recognize(transaction):
    oper = transaction.oper
    currency = transaction.currency
    course = transaction.course
    sum = transaction.count
    cash = transaction.cash
    return oper.name, currency.name, (course, sum), cash


def summing_currency(data):
    for k1, _ in data.items():
        for k2, i in _.items():
            d = {}
            for x, y in i:
                if x in d:
                    d[x] = d[x] + y
                else:
                    d[x] = y
            data[k1][k2] = d


def ziping(data):
    access_operation = TypeOfOperation.query.all()
    access_currency = Currency.query.all()
    my_dict = {x.name: {x.name: [] for x in access_operation if x.name in ('BUY', 'SELL')} for x in access_currency}
    for i in data:
        r = recognize(i)
        my_dict[r[1]][r[0]].append(r[2])
    summing_currency(my_dict)
    for i in my_dict:
        a = my_dict[i]['BUY'].items()
        b = my_dict[i]['SELL'].items()
        my_dict[i]['OPERATION'] = list(zip_longest(a, b, fillvalue=(0, 0)))
    return my_dict


def get_avarage(data):
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


def get_dict(data):
    access_operation = TypeOfOperation.query.all()
    access_currency = Currency.query.all()
    list_branches = Cashes.query.all()
    d_full = {cash:
                  {x.name:
                       {x.name: []
                        for x in access_operation if x.name in ('BUY', 'SELL')}
                   for x in access_currency}
              for cash in list_branches}
    for i in data:
        r = recognize(i)
        d_full[r[3]][r[1]][r[0]].append(r[2])
    return get_avarage(d_full)


@main.route('/report')
@login_required
@user_required
def report():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    transaction_today = Transaction.query. \
        filter(Transaction.date_trans > today). \
        filter(Transaction.user == current_user._get_current_object()).all()

    start_cash_state = Deals.query. \
        filter(Deals.user == current_user._get_current_object()). \
        filter(Deals.date_operation < today). \
        order_by(Deals.id.desc()).first()

    finish_cash_state = Deals.query. \
        filter(Deals.cash == current_user.cash). \
        order_by(Deals.id.desc()).first()

    # if not start_cash_state:
    #    start_cash_state = finish_cash_state

    my_cash = current_user.cash
    currency_state_cash = get_dict(transaction_today)[my_cash]

    return render_template('report.html',
                           today=today,
                           d=ziping(transaction_today),
                           d_state=currency_state_cash,
                           start_cash_state=start_cash_state,
                           finish_cash_state=finish_cash_state)
