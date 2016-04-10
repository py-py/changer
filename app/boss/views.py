from datetime import datetime, timedelta
from app import dec, db
from app.decorators import permission_required
from app.models import Permission, Cashes, Deals, Transaction, TypeOfOperation, Currency, User, Role, WalletCollector
from flask import render_template, request, redirect, url_for
from flask.ext.login import login_required
from . import boss
__author__ = 'py'



@boss.route('/boss_state')
@login_required
@permission_required(Permission.SHOW_STATUS)
def boss_state():
    result_branches = []
    for i in Cashes.query.order_by('id').all():
        deal = Deals.query.filter_by(cash_id=i.id).order_by(Deals.id.desc()).first()
        result_one = (i.branch, i.address, deal.count_uah, deal.count_usd, deal.count_eur, deal.count_rub)
        result_branches.append(result_one)
    return render_template('boss/boss_state.html', result_branches=result_branches)


@boss.route('/boss_trans', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.SHOW_STATUS)
def boss_trans():
    cashes = Cashes.query.order_by('branch').all()
    if request.method == 'POST':
        d_start = request.form['data-start']
        dt_start = datetime.strptime(d_start, '%d-%m-%Y') + timedelta(seconds=-120 * 60)
        d_finish = request.form['data-finish']
        dt_finish = datetime.strptime(d_finish, '%d-%m-%Y') + timedelta(seconds=1440 * 60) + timedelta(
            seconds=-120 * 60)
        inputed_cash = request.form['select_ch'].upper()

        cash = Cashes.query.filter(Cashes.branch == inputed_cash).first()
        all_trans = Transaction.query.filter_by(cash=cash)
        trans = all_trans.filter(Transaction.date_trans <= dt_finish).filter(Transaction.date_trans >= dt_start).all()
        return render_template('boss/boss_trans.html', cashes=cashes, trans=trans)
    return render_template('boss/boss_trans.html', cashes=cashes)



def recognize(transaction):
    oper = transaction.oper
    currency = transaction.currency
    course = transaction.course
    sum = transaction.count
    cash = transaction.cash
    return oper.name, currency.name, (course, sum), cash


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


@boss.route('/boss_currency_state')
@login_required
@permission_required(Permission.SHOW_STATUS)
def boss_currency_state():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    transaction_today = Transaction.query. \
        filter(Transaction.date_trans > today).all()
    currency_state_cashes = get_dict(transaction_today)
    return render_template('boss/boss_currency_state.html', d=currency_state_cashes)


@boss.route('/boss_money_collector')
@login_required
@permission_required(Permission.SHOW_STATUS)
def boss_money_collector():
    role_collector = Role.query.filter_by(name='Collector').first()
    collectors = User.query.filter_by(role=role_collector).filter_by(status=True).order_by('id').all()
    list_wallet_collector =[]

    for i in collectors:
        wallet_i = WalletCollector.query.filter_by(collector=i).order_by(WalletCollector.id.desc()).first()
        list_wallet_collector.append((i, wallet_i))

    # if request.method == 'POST':
    #     collector_id = request.form['collector_id']
    #     oper = request.form['oper']
    #     UAH = request.form['UAH']
    #     USD = request.form['USD']
    #     EUR = request.form['EUR']
    #     RUB = request.form['RUB']
    #     collector = User.query.filter_by(id=int(collector_id)).first()
    #     operation = TypeOfOperation.query.filter_by(name=oper).first()
    #     current_wallet = WalletCollector.query.filter_by(collector=collector).order_by(WalletCollector.id.desc()).first()
    #     if oper == 'GET':
    #         wallet_collector = WalletCollector(collector=collector,
    #                                        oper=operation,
    #                                        count_uah=dec(current_wallet.count_uah+UAH),
    #                                        count_usd=dec(current_wallet.count_usd+USD),
    #                                        count_eur=dec(current_wallet.count_eur+EUR),
    #                                        count_rub=dec(current_wallet.count_rub+RUB))
    #         db.session.add(wallet_collector)
    #     elif oper == 'GIVE':
    #         wallet_collector = WalletCollector(collector=collector,
    #                                        oper=operation,
    #                                        count_uah=dec(current_wallet.count_uah-UAH),
    #                                        count_usd=dec(current_wallet.count_usd-USD),
    #                                        count_eur=dec(current_wallet.count_eur-EUR),
    #                                        count_rub=dec(current_wallet.count_rub-RUB))
    #         db.session.add(wallet_collector)
    #     return redirect(url_for('boss.boss_money_collector'))

    return render_template('boss/boss_money_collector.html', list_wallet_collector=list_wallet_collector)


