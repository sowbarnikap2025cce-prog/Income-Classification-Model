import json
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from income_project.mongo_utils import get_db
from income_project.auth_utils import generate_jwt

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')

            if not email or not password or not name:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            db = get_db()
            
            # Check if user exists
            if db.users.find_one({'email': email}):
                return JsonResponse({'error': 'Email already exists'}, status=400)

            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Create user
            user = {
                'name': name,
                'email': email,
                'password': hashed_password.decode('utf-8')
            }
            db.users.insert_one(user)

            return JsonResponse({'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password required'}, status=400)

            db = get_db()
            user = db.users.find_one({'email': email})

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                token = generate_jwt(user['_id'])
                return JsonResponse({'token': token, 'name': user['name']}, status=200)
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
