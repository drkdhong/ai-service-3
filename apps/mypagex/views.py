from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from . import mypagex
from apps.mypagex.forms import ChangePasswordForm
from apps import db
from apps.dbmodels import Subscription, User
@mypagex.route('/dashboard')
@login_required
def dashboard():
    total_api_keys = 3 # APIKey.query.filter_by(user_id=current_user.id).count()
    approved_subscriptions = Subscription.query.filter_by(user_id=current_user.id, status='approved').count()
    pending_subscriptions = Subscription.query.filter_by(user_id=current_user.id, status='pending').count() 
    # 최근 사용 로그 5개
    recent_usage_logs = None
    # UsageLog.query.filter_by(user_id=current_user.id)\
    #                                .order_by(UsageLog.timestamp.desc())\
    #                                .limit(5).all()
    # 이번 달 총 사용량
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_usage = 0
    #db.session.query(func.sum(UsageLog.usage_count))\
    #                    .filter(UsageLog.user_id == current_user.id)\
    #                    .filter(extract('month', UsageLog.timestamp) == current_month)\
    #                    .filter(extract('year', UsageLog.timestamp) == current_year)\
    #                    .scalar() or 0
    return render_template('mypagex/dashboard.html',
                           title='마이페이지 대시보드',
                           total_api_keys=total_api_keys,
                           approved_subscriptions=approved_subscriptions,
                           pending_subscriptions=pending_subscriptions,
                           recent_usage_logs=recent_usage_logs,
                           monthly_usage=monthly_usage) 
# change_password 엔드포인트
@mypagex.route("/change_password", methods=["GET", "POST"])
@login_required  # 로그인한 사용자만 접근 가능
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if user.verify_password(form.current_password.data):
            user.password = form.new_password.data
            db.session.commit()
            flash("비밀번호가 성공적으로 변경되었습니다.")
            return redirect(url_for("mypagex.dashboard"))
        else:
            flash("현재 비밀번호가 올바르지 않습니다.")
    return render_template("mypagex/change_password.html", form=form)
# 추가된 내용 1
@mypagex.route('/subscriptions/approved')
@login_required
def subscriptions_approved():
    user_subscriptions = Subscription.query.filter_by(status='approved', user_id=current_user.id)\
                                            .order_by(Subscription.request_date.desc())\
                                            .all()
    return render_template('mypagex/subscriptions.html', title='구독 승인', subscriptions=user_subscriptions)
# 추가된 내용 2
@mypagex.route('/subscriptions/pending')
@login_required
def subscriptions_pending():
    user_subscriptions = Subscription.query.filter_by(status='pending', user_id=current_user.id)\
                                            .order_by(Subscription.request_date.desc())\
                                            .all()
    return render_template('mypagex/subscriptions.html', title='구독 대기', subscriptions=user_subscriptions)
# 추가된 내용 3
@mypagex.route('/subscriptions/rejected')
@login_required
def subscriptions_rejected():
    user_subscriptions = Subscription.query.filter_by(status='rejected', user_id=current_user.id)\
                                            .order_by(Subscription.request_date.desc())\
                                            .all()
    return render_template('mypagex/subscriptions.html', title='구독 거부', subscriptions=user_subscriptions)