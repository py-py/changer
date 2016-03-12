# coding: utf8
from flask.ext.login import login_user, login_required, logout_user, current_user
from ..models import User, Cashes
from flask import render_template, request, url_for, redirect, flash
from . import auth
__author__ = 'py'

@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    cashes = Cashes.query.filter_by(status=True).order_by('branch').all()
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        selected_cash = request.form['select_ch'].upper()

        user = User.query.filter_by(username=username).first()

        if user is not None and user.verify_password(password) and user.status:
            login_user(user)
            current_user.cash = Cashes.query.filter(Cashes.branch == selected_cash).first()
            current_user.ping()
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Неверный пользователь или пароль. Попробуйте еще раз.')

    return render_template('auth/login.html', cashes=cashes)


@login_required
@auth.route('/logout')
def logout():
    current_user.cash_id = 0
    logout_user()
    flash('Вы успешно вышли.')
    return redirect(url_for('auth.login'))
