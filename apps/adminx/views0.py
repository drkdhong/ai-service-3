# apps/adminx/views.py
import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import func, or_
from . import adminx
from apps.dbmodels import User
from apps.decorators import admin_required
from apps.extensions import db
from werkzeug.security import generate_password_hash # 비밀번호 해싱을 위해 사용

@adminx.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_services = 3  # AIService.query.count()
    pending_subscriptions = 4 # Subscription.query.filter_by(status='pending').count()
    
    # 최근 7일간 서비스 사용량 (로그인 제외)
    #seven_days_ago = datetime.now() - datetime.timedelta(days=7)
    recent_service_usage = 0

    #recent_service_usage = db.session.query(func.sum(UsageLog.usage_count))\
    #                            .filter(UsageLog.timestamp >= seven_days_ago)\
    #                            .filter(UsageLog.usage_type.notin_([UsageLog.UsageType.LOGIN]))\
    #                            .scalar() or 0

    return render_template('adminx/dashboard.html',
                           title='관리자 대시보드',
                           total_users=total_users,
                           total_services=total_services,
                           pending_subscriptions=pending_subscriptions,
                           recent_service_usage=recent_service_usage)

@adminx.route('/manage_users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    PER_PAGE = 10
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    
    # --- New search parameters ---
    is_admin_query = request.args.get('is_admin', '', type=str) # 'true', 'false', or ''
    is_active_query = request.args.get('is_active', '', type=str) # 'true', 'false', or ''
    created_at_query = request.args.get('created_at', '', type=str) # YYYY-MM-DD format
    # ---------------------------

    users_query = User.query

    # 검색 기능 (사용자 이름 또는 이메일)
    if search_query:
        users_query = users_query.filter(
            or_(
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        )
    
    # 관리자 여부 필터링
    if is_admin_query:
        if is_admin_query == 'true':
            users_query = users_query.filter(User.is_admin == True)
        elif is_admin_query == 'false':
            users_query = users_query.filter(User.is_admin == False)

    # 활성 상태 필터링
    if is_active_query:
        if is_active_query == 'true':
            users_query = users_query.filter(User.is_active == True)
        elif is_active_query == 'false':
            users_query = users_query.filter(User.is_active == False)

    # 가입일 필터링
    if created_at_query:
        try:
            # Parse the date string. We want to filter for users created ON that specific date.
            # So, from the start of that day up to the end of that day.
            search_date = datetime.datetime.strptime(created_at_query, '%Y-%m-%d').date()
            start_of_day = datetime.datetime.combine(search_date, datetime.time.min)
            end_of_day = datetime.datetime.combine(search_date, datetime.time.max)
            users_query = users_query.filter(User.created_at >= start_of_day, User.created_at <= end_of_day)
        except ValueError:
            flash('유효하지 않은 가입일 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.', 'warning')
            # Optionally, you might want to clear the created_at_query here to avoid re-applying invalid filter
            created_at_query = ""


    # 페이지네이션 적용
    users_pagination = users_query.order_by(User.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    users = users_pagination.items

    return render_template(
        'adminx/manage_users.html',
        title='사용자 관리',
        users=users,
        pagination=users_pagination,
        search_query=search_query,
        # --- Pass new search parameters to the template ---
        is_admin_query=is_admin_query,
        is_active_query=is_active_query,
        created_at_query=created_at_query,
        # --------------------------------------------------
    )

@adminx.route('/manage_users/<int:user_id>/toggle_active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('자신의 계정 상태는 변경할 수 없습니다.', 'warning')
        return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

    user.is_active = not user.is_active
    db.session.commit()
    flash(f'{user.username} 계정 상태가 {"활성" if user.is_active else "비활성"}으로 변경되었습니다.', 'success')
    return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

@adminx.route('/manage_users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('자신의 관리자 권한은 변경할 수 없습니다.', 'warning')
        return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'{user.username} 계정의 관리자 권한이 {"부여" if user.is_admin else "해제"}되었습니다.', 'success')
    return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

@adminx.route('/manage_users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        # 비밀번호 변경 로직은 별도로 처리하는 것이 좋습니다.
        # if 'password' in request.form and request.form['password']:
        #    user.set_password(request.form['password'])

        try:
            db.session.commit()
            flash(f'{user.username}님의 정보가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('adminx.manage_users')) # No need to pass search args here unless you want to return to filtered view
        except Exception as e:
            db.session.rollback()
            flash(f'사용자 정보 수정 중 오류가 발생했습니다: {e}', 'danger')

    return render_template('adminx/edit_user.html', title=f'{user.username} 수정', user=user)

@adminx.route('/manage_users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('자신의 계정은 삭제할 수 없습니다.', 'warning')
        return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username} 계정이 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'사용자 삭제 중 오류가 발생했습니다: {e}', 'danger')

    return redirect(url_for('adminx.manage_users', **request.args)) # Pass current search args

@adminx.route('/manage_users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form # 체크박스 여부 확인
        is_active = 'is_active' in request.form # 체크박스 여부 확인

        # 필수 필드 유효성 검사
        if not username or not email or not password:
            flash('사용자 이름, 이메일, 비밀번호는 필수 입력 사항입니다.', 'danger')
            return render_template('adminx/create_user.html', title='사용자 생성')

        # 사용자 이름 또는 이메일 중복 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자 이름입니다.', 'danger')
            return render_template('adminx/create_user.html', title='사용자 생성')
        if User.query.filter_by(email=email).first():
            flash('이미 존재하는 이메일입니다.', 'danger')
            return render_template('adminx/create_user.html', title='사용자 생성')

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password, # User 모델에 password_hash 컬럼
                is_admin=is_admin,
                is_active=is_active
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f'{new_user.username} 사용자가 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('adminx.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'사용자 생성 중 오류가 발생했습니다: {e}', 'danger')

    return render_template('adminx/create_user.html', title='사용자 생성')