from datetime import datetime, timedelta
from app.decorators import permission_required
from app.models import Permission, Cashes, Deals, Transaction, TypeOfOperation, Currency
from flask import render_template, request
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
    return render_template('boss/boss_currency_state.html', d = currency_state_cashes)