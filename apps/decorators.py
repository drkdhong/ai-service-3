# 관리자 권한 확인 데코레이터
from datetime import datetime, timedelta
import functools
import logging

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user

from apps.config import Config
from apps.dbmodels import User

# 관리자 권한 확인 데코레이터
# 추가
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
# 추가
def superman_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def superx_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

"""
# AI 사용량 제한 데코레이터
def rate_limit(limit_config_key):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            limit_str = getattr(Config, limit_config_key)
            # 간단한 속도 제한 구현 (프로덕션에서는 Redis 등을 활용하는 것이 좋습니다)
            # 현재는 UsageLog 테이블을 사용하여 카운트합니다.
            # 이 로직은 실제 배포 시 성능 문제가 될 수 있으므로 주의가 필요합니다.
            # Flask-Limiter와 같은 외부 라이브러리를 사용하는 것을 권장합니다.
            # API Key 사용량 제한
            if 'api_key_id' in kwargs and kwargs['api_key_id']:
                api_key = APIKey.query.get(kwargs['api_key_id'])
                if not api_key:
                    logging.warning(f"Rate Limit: Invalid API Key ID {kwargs['api_key_id']}")
                    return jsonify({"error": "Invalid API Key"}), 401
                # 현재 분의 시작 시간 계산
                now = datetime.now()
                minute_ago = now - timedelta(minutes=1)
                usage_count = UsageLog.query.filter(
                    UsageLog.api_key_id == api_key.id,
                    UsageLog.endpoint == request.path,
                    UsageLog.timestamp >= minute_ago
                ).count()
                limit_value = int(limit_str.split('/')[0])
                if usage_count >= limit_value:
                    logging.warning(f"Rate Limit Exceeded for API Key {api_key.key_string}. Count: {usage_count}, Limit: {limit_value}")
                    return jsonify({"error": "API Key usage limit exceeded. Please try again later."}), 429
                # API Key 사용량 업데이트
                api_key.usage_count += 1
                api_key.last_used = now
                db.session.commit() # 여기서 커밋하여 바로 반영
            # 로그인 사용자 사용량 제한
            elif current_user.is_authenticated:
                # 현재 시간의 시작 시간 (시간당)
                now = datetime.now()
                hour_ago = now - timedelta(hours=1)
                usage_count = UsageLog.query.filter(
                    UsageLog.user_id == current_user.id,
                    UsageLog.endpoint == request.path,
                    UsageLog.timestamp >= hour_ago
                ).count()
                limit_value = int(limit_str.split('/')[0])
                if usage_count >= limit_value:
                    logging.warning(f"Rate Limit Exceeded for User {current_user.email}. Count: {usage_count}, Limit: {limit_value}")
                    flash('시간당 사용량 제한을 초과했습니다. 잠시 후 다시 시도해주세요.', 'warning')
                    return redirect(url_for('iris.predict')) # 또는 에러 페이지로 리디렉션
            return f(*args, **kwargs)
        return decorated_function
    return decorator
"""