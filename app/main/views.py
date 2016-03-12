# coding: utf8
from datetime import datetime, timedelta
from app import db, dec
from app.decorators import permission_required, admin_required
from app.models import Cashes, Permission, Role, User, Deals, TypeOfOperation, Currency, Transaction, Inkass
from flask import render_template, request, flash, url_for, redirect
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError
from . import main

__author__ = 'py'


@main.route('/', methods=['GET', 'POST'])
@login_required
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


@main.route('/inkass', methods=['GET', 'POST'])
@login_required
def inkass():
    cash_state = Deals.query.filter_by(cash_id=current_user.cash_id).order_by(Deals.id.desc()).first()
    if request.method == 'POST':
        try:
            operation = str(request.form['oper'])
        except BadRequestKeyError:
            operation = None
        comment = str(request.form['comment'])
        UAH = dec(request.form['UAH'])
        EUR = dec(request.form['EUR'])
        USD = dec(request.form['USD'])
        RUB = dec(request.form['RUB'])

        new_inkass = Inkass(user_id=current_user.id,
                            cash_id=current_user.cash_id,
                            oper=TypeOfOperation.query.filter_by(name=operation).first(),
                            inkass_notes=comment,
                            count_uah=UAH,
                            count_eur=EUR,
                            count_usd=USD,
                            count_rub=RUB)
        db.session.add(new_inkass)

        if operation == 'GET':
            new_deal = Deals(user_id=current_user.id,
                             cash_id=current_user.cash_id,
                             inkass=True,
                             inkass_notes=comment,
                             count_uah=dec(cash_state.count_uah + UAH),
                             count_eur=dec(cash_state.count_eur + EUR),
                             count_usd=dec(cash_state.count_usd + USD),
                             count_rub=dec(cash_state.count_rub + RUB))
            db.session.add(new_deal)
            flash('Проведена инкассация. Обновлены остатки по кассе.', 'success')
            return redirect(url_for('main.inkass'))
        elif operation == 'GIVE':
            new_deal = Deals(user_id=current_user.id,
                             cash_id=current_user.cash_id,
                             inkass=True,
                             inkass_notes=comment,
                             count_uah=dec(cash_state.count_uah - UAH),
                             count_eur=dec(cash_state.count_eur - EUR),
                             count_usd=dec(cash_state.count_usd - USD),
                             count_rub=dec(cash_state.count_rub - RUB))
            db.session.add(new_deal)
            flash('Проведена инкассация. Обновлены остатки по кассе.', 'success')
            return redirect(url_for('main.inkass'))
        else:
            flash('Операция не проведена, не выбран тип инкассации: "Получить" или "Передать"', 'danger')
            return redirect(url_for('main.inkass'))
    return render_template('inkass.html', cash_state=cash_state)


@main.route('/user_transaction', methods=['GET', 'POST'])
@login_required
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


@main.route('/user_inkass', methods=['GET', 'POST'])
@login_required
def user_inkass():
    d_today = datetime.utcnow().date()
    list_inkass = Inkass.query.filter_by(user=current_user).all()

    # Список касс в которых инкассировался текущий сотрудник;
    cashes = [current_user.cash]
    for i in list_inkass:
        if i.cash not in cashes:
            cashes.append(i.cash)

    # Список инкассаций за текущий день;
    inkasses = []
    for i in list_inkass:
        if i.date_inkass.date() == d_today:
            inkasses.append(i)

    return render_template('user_inkass.html', inkasses=inkasses, cashes=cashes)


@main.route('/change_user', methods=['GET', 'POST'])
@login_required
def change_user():
    return render_template('change_user.html', user=current_user)

