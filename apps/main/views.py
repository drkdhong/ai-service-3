# apps/main/views.py

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import and_, or_
#from flask_login import login_required, current_user
from apps.dbmodels import Service, Subscription
from apps.main import main
from apps import db
from datetime import datetime

@main.route("/")
def index():
#    if current_user.is_authenticated:
#        return render_template("main/index.html", username=current_user.username)
    return render_template("main/index.html")
@main.route('/services') # 추가된 부분 1
def services():
    query = request.args.get('query', '')
    if query:
        # 키워드 또는 서비스 이름으로 검색
        search_results = Service.query.filter( 
            and_(
                Service.is_active == True,  # Add this line to filter by active services
                or_(
                    Service.servicename.ilike(f'%{query}%'), Service.description.ilike(f'%{query}%'),
                    Service.keywords.ilike(f'%{query}%')
                )
            )
        ).all()
        title = f"'{query}' 검색 결과"
    else:    # When no query, only show active services
        search_results = Service.query.filter_by(is_active=True).all()
        title = "모든 AI 서비스"
    if current_user.is_authenticated:     # 각 서비스별 구독 상태 확인
        user_subscriptions = {sub.service_id: sub.status for sub in current_user.subscriptions}
    else:
        user_subscriptions = {}
    return render_template('main/services.html', services=search_results, query=query, title=title, user_subscriptions=user_subscriptions)
# 추가된 부분 2
@main.route('/service/<int:service_id>', methods=['GET', 'POST'])
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    subscription_status = None
    service_endpoint=None
    if current_user.is_authenticated:
        subscription = Subscription.query.filter_by(user_id=current_user.id, service_id=service.id).first()
        if subscription:
            subscription_status = subscription.status
            # servie_endpoint 추가
            if service.service_endpoint:
                service_endpoint = url_for(service.service_endpoint)    # /api/predict/iris
            else:
                service_endpoint = '#'
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('서비스를 구독하려면 로그인해야 합니다.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if subscription_status:
            flash(f'이미 이 서비스에 대한 구독 요청을 했거나 구독 중입니다 (상태: {subscription_status}).', 'info')
            return redirect(url_for('main.service_detail', service_id=service.id))
        # service의 is_auto 값에 따라 status를 설정
        if service.is_auto:
            subscription_status_to_set = 'approved'
            flash_message = f'\'{service.servicename}\' 서비스 구독이 자동으로 승인됨'
            #redirect_page = 'mypagex.subscriptions_approved' # 승인된 구독 목록 페이지로 리다이렉트
            redirect_page = 'main.services'  # main.services로 이동
            approval_date_to_set = datetime.now() 
        else:
            subscription_status_to_set = 'pending'
            flash_message = f'\'{service.servicename}\' 서비스 구독을 성공적으로 신청함. 관리자 승인 대기.'
            #redirect_page = 'mypagex.subscriptions_pending' # 대기 중인 구독 목록 페이지로 리다이렉트
            redirect_page = 'main.services'  # main.services로 이동  
            approval_date_to_set = None 
        new_subscription = Subscription(
            user_id=current_user.id, service_id=service.id, status=subscription_status_to_set,
            approval_date=approval_date_to_set
        )
        db.session.add(new_subscription)
        db.session.commit()
        # --- 메시지 및 redirect 주소 수정
        flash(flash_message, 'success')
        return redirect(url_for(redirect_page))  # redirect_page로 리다이렉트
    return render_template('main/service_detail.html', title=service.servicename, service=service, subscription_status=subscription_status, service_endpoint=service_endpoint)
# 추가된 부분 3
@main.route('/api/predict/iris', methods=['GET', 'POST'])
def predict_iris():
    return render_template('main/predict_iris.html', title='붓꽃 서비스')
# 추가된 부분 4
@main.route('/api/predict/loan', methods=['GET', 'POST'])
def predict_loan():
    return render_template('main/predict_loan.html', title='대출 서비스')

