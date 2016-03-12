from . import admin
import json
from app import db
from app.decorators import admin_required
from app.models import Role, User, Cashes, Deals
from flask import request, url_for, redirect, render_template, flash
from flask.ext.login import login_required, current_user

__author__ = 'py'




@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    roles = Role.query.order_by('permissions').all()
    users = User.query.order_by('id').all()
    if request.method == 'POST':
        username_new = request.form['username']
        password_new = request.form['password']
        role_id = request.form['select_role']
        user_new = User.query.filter_by(username=username_new).first()
        if user_new is None:
            user_new = User(username=username_new)
            user_new.password = password_new
            user_new.role = Role.query.filter_by(id=role_id).first()
        db.session.add(user_new)
        return redirect(url_for('admin.add_user'))
    return render_template('admin/add_user.html', roles=roles, users=users)


@admin.route('/add_cash', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cash():
    cashes = Cashes.query.order_by('branch').all()
    if request.method == 'POST':
        branch = request.form['branch'].upper()
        city = request.form['city']
        address = request.form['address']
        phone = request.form['phone']
        #
        cash = Cashes(branch=branch, city=city, address=address, phone=phone)
        db.session.add(cash)

        deal = Deals(user_id=current_user.id,
                     cash=Cashes.query.filter_by(branch=branch).first(),
                     count_uah=0,
                     count_eur=0,
                     count_usd=0,
                     count_rub=0)
        db.session.add(deal)

        flash("Добавлена новая касса %s в городе %s по адресу: %s" % (branch, city, address))
        return redirect(url_for('admin.add_cash'))
    return render_template('admin/add_cash.html', cashes=cashes)


@admin.route('/close_cash')
@login_required
@admin_required
def close_cash():
    cash_state = int(request.args['state'])
    cash_id = request.args['id']

    cash = Cashes.query.filter_by(id=cash_id).first()

    if cash.status == cash_state:
        cash.status = not cash_state
        db.session.add(cash)
        return json.dumps({'id': cash.id, 'state': cash.status})
    else:
        return json.dumps({'id': 0, 'state': 0})


@admin.route('/check_cash')
@login_required
@admin_required
def check_cash():
    cash_name = request.args['name'].upper()

    if cash_name[:2] == 'CH' and len(cash_name) == 4:
        cash = Cashes.query.filter_by(branch=cash_name).first()
        return json.dumps({'can': True}) if not cash else json.dumps({'can': False})
    else:
        return json.dumps({'can': False})


@admin.route('/close_user')
@login_required
@admin_required
def close_user():
    user_state = int(request.args['state'])
    user_id = request.args['id']

    user = User.query.filter_by(id=user_id).first()

    if user.status == user_state:
        user.status = not user_state
        db.session.add(user)
        return json.dumps({'id': user.id, 'state': user.status})
    else:
        return json.dumps({'id': 0, 'state': 0})


@admin.route('/check_login')
@login_required
@admin_required
def check_login():
    username = request.args['name']

    if len(username) >= 2:
        user = User.query.filter_by(username=username).first()
        return json.dumps({'can': True}) if not user else json.dumps({'can': False})
    else:
        return json.dumps({'can': False})
