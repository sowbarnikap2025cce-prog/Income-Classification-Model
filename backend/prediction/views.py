import json
import os
import joblib
import pandas as pd
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from income_project.mongo_utils import get_db
from income_project.auth_utils import jwt_required

# Try to load the model on startup
MODEL_PATH = os.path.join(settings.BASE_DIR.parent, 'ml_pipeline', 'model.joblib')
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")

@csrf_exempt
@jwt_required
def predict(request):
    if request.method == 'POST':
        try:
            # Lazy load if it wasn't available at startup
            global model
            if model is None:
                if os.path.exists(MODEL_PATH):
                    model = joblib.load(MODEL_PATH)
                else:
                    return JsonResponse({'error': 'Model not trained yet'}, status=503)

            data = json.loads(request.body)
            
            # Prepare data for model
            # Must match the columns used during training
            columns = [
                "age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
                "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
                "hours-per-week", "native-country"
            ]
            
            # Create a dataframe with a single row
            input_dict = {col: [data.get(col)] for col in columns}
            input_df = pd.DataFrame(input_dict)
            
            # Predict
            pred = model.predict(input_df)[0]
            # Income classification: convert model prediction to readable label
            prediction_label = 'Above 50,000 INR' if pred == 1 else 'Upto 50,000 INR'
            
            # Save to MongoDB
            db = get_db()
            history_record = {
                'user_id': request.user_id,
                'input_data': data,
                'prediction': prediction_label,
                'timestamp': datetime.utcnow()
            }
            db.predictions.insert_one(history_record)
            
            return JsonResponse({'prediction': prediction_label}, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@jwt_required
def history(request):
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.predictions.find({'user_id': request.user_id}).sort('timestamp', -1)
            
            history_list = []
            for record in cursor:
                # Convert ObjectId to string and timestamp to ISO format
                record['_id'] = str(record['_id'])
                record['timestamp'] = record['timestamp'].isoformat()
                history_list.append(record)
                
            return JsonResponse(history_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@jwt_required
def analytics(request):
    """Get analytics data for the logged-in user"""
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.predictions.find({'user_id': request.user_id})
            
            predictions = []
            above_50l = 0
            upto_50l = 0
            occupations = {}
            ages = []
            
            for record in cursor:
                predictions.append(record)
                pred = record['prediction']
                
                if pred and 'Above' in pred:
                    above_50l += 1
                else:
                    upto_50l += 1
                
                # Count by occupation
                occ = record['input_data'].get('occupation', 'Unknown')
                occupations[occ] = occupations.get(occ, 0) + 1
                
                # Collect ages
                ages.append(record['input_data'].get('age', 0))
            
            analytics_data = {
                'total_predictions': len(predictions),
                'above_50l': above_50l,
                'upto_50l': upto_50l,
                'occupations': occupations,
                'avg_age': sum(ages) / len(ages) if ages else 0,
                'min_age': min(ages) if ages else 0,
                'max_age': max(ages) if ages else 0,
            }
            
            return JsonResponse(analytics_data, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@jwt_required
def statistics(request):
    """Get detailed statistics including education, workclass, etc."""
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.predictions.find({'user_id': request.user_id})
            
            education = {}
            workclass = {}
            predictions_by_date = {}
            
            for record in cursor:
                # Count by education
                edu = record['input_data'].get('education', 'Unknown')
                education[edu] = education.get(edu, 0) + 1
                
                # Count by workclass
                wc = record['input_data'].get('workclass', 'Unknown')
                workclass[wc] = workclass.get(wc, 0) + 1
                
                # Predictions by date
                date = record['timestamp'].strftime('%Y-%m-%d')
                predictions_by_date[date] = predictions_by_date.get(date, 0) + 1
            
            stats_data = {
                'education': education,
                'workclass': workclass,
                'predictions_by_date': predictions_by_date,
            }
            
            return JsonResponse(stats_data, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
