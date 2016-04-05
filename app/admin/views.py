from . import admin
import json
from app import db
from app.decorators import admin_required
from app.models import Role, User, Cashes, Deals, GroupOfCashes
from flask import request, url_for, redirect, render_template, flash
from flask.ext.login import login_required, current_user

__author__ = 'py'


# About Useres:
@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    groups = GroupOfCashes.query.order_by('group_branch').all()

    roles = Role.query.order_by('permissions').all()
    users = User.query.order_by('id').all()
    collector_permission = Role.query.filter_by(name='Collector').first().permissions

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['select_role']
        group_id = request.form.get('select_group')

        if not group_id:
            group_id = GroupOfCashes.query.filter_by(group_branch='GR00').first().id

        user_new = User.query.filter_by(username=username).first()
        if user_new is None:
            user_new = User(username=username,
                            password=password)
            user_new.group = GroupOfCashes.query.filter_by(id=group_id).first()
            user_new.role = Role.query.filter_by(id=role_id).first()
            db.session.add(user_new)
            flash('Пользователь с именем %s успешно добавлен в базу.' % username)
        else:
            flash('Пользователь с именем %s уже есть в базе. Выбирете другое имя.' % username)
        return redirect(url_for('admin.add_user'))
    return render_template('admin/add_user.html',
                           users=users,
                           roles=roles,
                           permission=collector_permission,
                           groups=groups)


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


@admin.route('/check_user')
@login_required
@admin_required
def check_user():
    username = request.args['name']

    if len(username) >= 2:
        user = User.query.filter_by(username=username).first()
        return json.dumps({'can': True}) if not user else json.dumps({'can': False})
    else:
        return json.dumps({'can': False})


@admin.route('/get_info_user')
@login_required
@admin_required
def get_info_user():
    username = request.args['user']
    u = User.query.filter_by(username=username).first()
    return json.dumps({'user': u.username, 'role': u.role.name})


@admin.route('/edit_user', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user():
    if request.method == 'POST':
        username = request.form['modal-username']

        password = request.form.get('modal-password')
        role_id = request.form.get('modal-select_role')
        group_id = request.form.get('modal-select_group')

        # Update checked user;
        user = User.query.filter_by(username=username).first()
        role_collector = Role.query.filter_by(name='Collector').first()
        role_current_user = Role.query.filter_by(id=role_id).first()

        user.role = role_current_user
        if role_current_user != role_collector:
            user.group_id = 0

        if password:
            user.password = password

        if group_id:
            user.group = GroupOfCashes.query.filter_by(id=group_id).first()
        db.session.add(user)

        return redirect(url_for('admin.add_user'))


# About Cashes:
@admin.route('/add_cash', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cash():
    cashes = Cashes.query.order_by('branch').all()
    groups = GroupOfCashes.query.order_by('group_branch').all()

    if request.method == 'POST':
        branch = request.form['branch'].upper()
        address = request.form['address']
        group = request.form['select_group']
        group = GroupOfCashes.query.filter_by(id=group).first()

        cash = Cashes(branch=branch, address=address, group=group)
        db.session.add(cash)

        deal = Deals(user_id=current_user.id,
                     cash=Cashes.query.filter_by(branch=branch).first(),
                     count_uah=0,
                     count_eur=0,
                     count_usd=0,
                     count_rub=0)
        db.session.add(deal)

        flash("Добавлена новая касса %s по адресу: %s" % (branch, address))
        return redirect(url_for('admin.add_cash'))
    return render_template('admin/add_cash.html', cashes=cashes, groups=groups)


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


@admin.route('/get_info_cash')
@login_required
@admin_required
def get_info_cash():
    branch = request.args['branch'].upper()
    b = Cashes.query.filter_by(branch=branch).first()
    return json.dumps({'branch': b.branch,
                       'address': b.address,
                       'status': b.status})


@admin.route('/edit_cash', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cash():
    if request.method == 'POST':
        branch = request.form['modal-branch']
        address = request.form['modal-address']
        group = request.form['modal-select_group']

        branch = Cashes.query.filter_by(branch=branch).first()
        branch.address = address
        branch.group = GroupOfCashes.query.filter_by(id=int(group)).first()

        db.session.add(branch)
        return redirect(url_for('admin.add_cash'))

# About Groupes:
@admin.route('/add_group', methods=['GET', 'POST'])
@login_required
@admin_required
def add_group():
    list_group = []
    groups = GroupOfCashes.query.order_by('group_branch').all()

    for g in groups:
        cashes = Cashes.query.filter_by(group=g).all()
        collectors = User.query.filter_by(group=g).all()
        list_group.append((g, cashes, collectors))

    if request.method == 'POST':
        group_branch = request.form['branch']
        description = request.form['description']
        group = GroupOfCashes(group_branch=group_branch,
                              group_description=description)
        db.session.add(group)
        flash('Добавлена новая группа %s c описание района %s' % (group_branch, description))
        return redirect(url_for('admin.add_group'))
    return render_template('admin/add_group.html', list_group=list_group)


@admin.route('/check_group')
@login_required
@admin_required
def check_group():
    group_name = request.args['branch'].upper()
    print(GroupOfCashes.query.filter_by(group_branch=group_name).first())
    if GroupOfCashes.query.filter_by(group_branch=group_name).first():
        return json.dumps({'can': False})
    else:
        return json.dumps({'can': True})
