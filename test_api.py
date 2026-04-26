import urllib.request
import urllib.error
import json

base_url = 'http://127.0.0.1:8000/api'

def make_request(url, method='GET', data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except urllib.error.URLError as e:
        return 0, str(e.reason)

# 1. Signup
print("Testing Signup...")
status, res = make_request(f'{base_url}/signup/', method='POST', data={
    'name': 'Test User',
    'email': 'test3@example.com',
    'password': 'password123'
})
print("Signup Response:", status, res)

# 2. Login
print("\nTesting Login...")
status, res = make_request(f'{base_url}/login/', method='POST', data={
    'email': 'test3@example.com',
    'password': 'password123'
})
print("Login Response:", status, res)
token = res.get('token') if isinstance(res, dict) else None

if token:
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. Predict
    print("\nTesting Predict...")
    pred_data = {
        "age": 35,
        "workclass": "Private",
        "fnlwgt": 100000,
        "education": "Bachelors",
        "education-num": 13,
        "marital-status": "Married-civ-spouse",
        "occupation": "Exec-managerial",
        "relationship": "Husband",
        "race": "Asian-Pac-Islander",
        "sex": "Male",
        "capital-gain": 0,
        "capital-loss": 0,
        "hours-per-week": 40,
        "native-country": "India"
    }
    status, res = make_request(f'{base_url}/predict/', method='POST', data=pred_data, headers=headers)
    print("Predict Response:", status, res)
    
    # 4. History
    print("\nTesting History...")
    status, res = make_request(f'{base_url}/history/', method='GET', headers=headers)
    print("History Response:", status, res)
