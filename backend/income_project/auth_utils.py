import os
import jwt
import datetime
from functools import wraps
from django.http import JsonResponse
from income_project.mongo_utils import get_db
from bson.objectid import ObjectId

def generate_jwt(user_id):
    secret = os.environ.get('JWT_SECRET', 'super_secret_jwt_key')
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def jwt_required(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing'}, status=401)
        
        token = auth_header.split(' ')[1]
        secret = os.environ.get('JWT_SECRET', 'super_secret_jwt_key')
        
        try:
            data = jwt.decode(token, secret, algorithms=['HS256'])
            db = get_db()
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return JsonResponse({'error': 'User not found'}, status=401)
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return f(request, *args, **kwargs)
    return decorated
