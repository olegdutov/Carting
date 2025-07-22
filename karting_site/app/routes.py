from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Kart, Reservation
from app.forms import RegistrationForm, LoginForm, ReservationForm
from datetime import datetime
from urllib.parse import urlparse, urljoin
from functools import wraps

main_bp = Blueprint('main', __name__)

def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Войдите в систему.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))

from flask_login import current_user

@main_bp.route('/dashboard')
@login_required
def dashboard():
    reservations = current_user.reservations
    return render_template('dashboard.html', user=current_user, reservations=reservations)


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Kart, Reservation
from app.forms import ReservationForm
from datetime import datetime

@main_bp.route('/karts')
@login_required
def karts():
    karts = Kart.query.filter_by(is_available=True).all()
    return render_template('karts.html', karts=karts)

@main_bp.route('/reserve/<int:kart_id>', methods=['GET', 'POST'])
@login_required
def reserve(kart_id):
    kart = Kart.query.get_or_404(kart_id)
    form = ReservationForm()
    form.kart_id.choices = [(kart.id, kart.model)]  # фиксируем выбранный карт в форме

    if form.validate_on_submit():
        # Проверяем пересечения бронирований
        overlapping = Reservation.query.filter(
            Reservation.kart_id == kart.id,
            Reservation.start_time < form.end_time.data,
            Reservation.end_time > form.start_time.data
        ).first()

        if overlapping:
            flash('Этот карт уже забронирован на выбранное время.', 'danger')
            return redirect(url_for('main.karts'))

        reservation = Reservation(
            user_id=current_user.id,
            kart_id=kart.id,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        db.session.add(reservation)
        db.session.commit()
        flash('Бронирование успешно создано!', 'success')
        return redirect(url_for('main.dashboard'))

    # Предустановим выбранный карт в форме (если GET-запрос)
    form.kart_id.data = kart.id
    return render_template('reserve.html', form=form, kart=kart)


@main_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    reservations = Reservation.query.order_by(Reservation.start_time.desc()).all()
    return render_template('admin_panel.html', users=users, reservations=reservations)

@main_bp.route('/schedule')
@login_required
def schedule():
    reservations = Reservation.query.order_by(Reservation.start_time.asc()).all()
    return render_template('schedule.html', reservations=reservations)

@main_bp.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.id:
        flash('Вы не можете отменить это бронирование', 'danger')
        return redirect(url_for('main.dashboard'))

    # Удаляем бронирование
    db.session.delete(reservation)
    db.session.commit()
    flash('Бронирование успешно отменено', 'success')

    return redirect(url_for('main.dashboard'))
