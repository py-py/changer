from datetime import datetime, timedelta
from app.decorators import permission_required
from app.models import Permission, Cashes, Deals, Transaction
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
        result_one = (i.branch, i.city, i.address, deal.count_uah, deal.count_usd, deal.count_eur, deal.count_rub)
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