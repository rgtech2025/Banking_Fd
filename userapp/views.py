from django.shortcuts import render, redirect
from userapp.models import userModel 
from adminapp.models import Predict
from django.contrib import messages
import pandas as pd
import numpy
from pickle import load
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve

# Create your views here.

def user_login(request):
    if request.method=="POST":
        email = request.POST.get("email")
        password = request.POST.get("pwd")
       
        try:         
            user_data = userModel.objects.get(email=email, password=password)
            if user_data.user_status == "pending":
                messages.info(request,'Your account status is pending.')
                return redirect('user_login')
            
            elif user_data.user_status == "rejected":
                messages.info(request,'Your account has been rejected.')
                return redirect('user_login')

            elif user_data.user_status == "accepted":
                request.session["id"] = user_data.user_id
                messages.success(request, 'You have successfully logged in!')
                return redirect("user_dash")
        except:
            messages.warning(request,'You have entered incorrect details.')
            return redirect("user_login")
    return render(request, 'userapp/user-login.html')

def user_dash(request):
    return render(request, 'userapp/user-dash.html')

def user_profile(request):
    s_id = request.session["id"] 
    user = userModel.objects.get(user_id = s_id)
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        if len(request.FILES)!=0:
            image = request.FILES["img"]
            user.image = image
            user.name = name
            user.email = email
            user.phone = phone
            user.address = address
            user.save()
        else:
            user.name = name
            user.email = email
            user.phone = phone
            user.address = address
            user.save()
        messages.success(request, 'Successful edit!')
    context = {"user": user}

    return render(request, 'userapp/user-profile.html', context)

# def user_predict(request):
#     if request.method=="POST":
#         type = request.POST.get('type')
#         amount  = request.POST.get('amount')
#         amount = float(amount)
#         oldbalanceOrg  = request.POST.get('oldbalanceOrg')
#         newbalanceOrig  = request.POST.get('newbalanceOrig')
#         oldbalanceDest  = request.POST.get('oldbalanceDest')
#         newbalanceDest = request.POST.get('newbalanceDest')

#         encoder=load(open(r'algorithms\encoder\encoder.pkl','rb'))
#         type = encoder.transform([type])
#         data = {
#             'type': type,
#             'amount': amount,
#             'oldbalanceOrg': oldbalanceOrg,
#             'newbalanceOrig': newbalanceOrig,
#             'oldbalanceDest': oldbalanceDest,
#             'newbalanceDest': newbalanceDest,
#         }
#         df = pd.DataFrame(data, index=[0])
#         model = load(open(r'algorithms\algo\AdaBoostClassifier.pkl','rb'))
#         prediction=model.predict(df)
        
#         predictio = prediction[0]
#         if predictio == 0:
#             result = 'Genuine'
#         elif predictio == 1:
#             result = 'Fake'
#         print(predictio,result,'result')
#         predictid = Predict.objects.create(
#             type=type,
#             amount = amount,
#             oldbalanceOrg=oldbalanceOrg,
#             newbalanceOrig=newbalanceOrig,
#             oldbalanceDest=oldbalanceDest,
#             newbalanceDest=newbalanceDest,
#             result = result
#         )
#         id =predictid.predict_id
#         # data = Predict.objects.all().order_by('-predict_id').first()
#         # type = data.type
#         # oldbalanceOrg=  data.oldbalanceOrg,
#         # newbalanceOrig= data.newbalanceOrig,
#         # oldbalanceDest= data.oldbalanceDest,
#         # newbalanceDest= data.newbalanceDest,
#         # result = data.result
#         # context = {
#         #     'type':type,
#         #     'obo':oldbalanceOrg,
#         #     'nbo':newbalanceOrig,
#         #     'obd':oldbalanceDest,
#         #     'nbd':newbalanceDest,
#         #     'res':result,
#         # }
#         return redirect('user_result', id)  
#     return render(request,'userapp/user-predict.html')


from django.shortcuts import render, redirect
import pandas as pd
import joblib
from adminapp.models import Predict   # adjust import if needed


# Load once (global - best practice)
import joblib
import pandas as pd
import json
from django.shortcuts import render, redirect
from adminapp.models import Predict


# 🔹 Load models (GLOBAL)
loaded_model = joblib.load(r'fraud_model.pkl')
loaded_encoder = joblib.load(r'label_encoder.pkl')
feature_columns = joblib.load(r'feature_columns.pkl')
loaded_explainer = joblib.load(r'shap_explainer.pkl')


def user_predict(request):
    if request.method == "POST":

        try:
            # 🔹 Inputs
            step = int(request.POST.get('step'))
            type_ = request.POST.get('type')

            amount = float(request.POST.get('amount'))
            oldbalanceOrg = float(request.POST.get('oldbalanceOrg'))
            newbalanceOrig = float(request.POST.get('newbalanceOrig'))
            oldbalanceDest = float(request.POST.get('oldbalanceDest'))
            newbalanceDest = float(request.POST.get('newbalanceDest'))

        except:
            return render(request, 'userapp/user-predict.html', {
                'error': 'Invalid input values'
            })

        # 🔹 Validation
        if step < 1 or step > 741:
            return render(request, 'userapp/user-predict.html', {
                'error': 'Step must be between 1 and 741'
            })

        if type_ not in loaded_encoder.classes_:
            return render(request, 'userapp/user-predict.html', {
                'error': f'Invalid type. Allowed: {list(loaded_encoder.classes_)}'
            })

        type_encoded = loaded_encoder.transform([type_])[0]

        # 🔥 Feature Engineering
        balance_diff_org = oldbalanceOrg - newbalanceOrig
        balance_diff_dest = newbalanceDest - oldbalanceDest
        zero_balance_flag = int(oldbalanceOrg == 0 or oldbalanceDest == 0)

        # 🔹 DataFrame
        data = pd.DataFrame([[
            step,
            type_encoded,
            amount,
            oldbalanceOrg,
            newbalanceOrig,
            oldbalanceDest,
            newbalanceDest,
            balance_diff_org,
            balance_diff_dest,
            zero_balance_flag
        ]], columns=feature_columns)

        # 🔹 Prediction
        prob = float(loaded_model.predict_proba(data)[0][1])
        threshold = 0.2
        result = 'Fraud' if prob > threshold else 'Genuine'

        # 🔥 SHAP EXPLANATION
        shap_values = loaded_explainer.shap_values(data)

        shap_dict = {
            feature: float(round(value, 4))
            for feature, value in zip(feature_columns, shap_values[0])
        }

        # 🔥 Convert to JSON (IMPORTANT FOR CHART.JS)
        shap_json = json.dumps(shap_dict)

        # 🔹 Save to DB
        predict_obj = Predict.objects.create(
            step=step,
            type=type_,
            amount=amount,
            oldbalanceOrg=oldbalanceOrg,
            newbalanceOrig=newbalanceOrig,
            oldbalanceDest=oldbalanceDest,
            newbalanceDest=newbalanceDest,

            balance_diff_org=balance_diff_org,
            balance_diff_dest=balance_diff_dest,
            zero_balance_flag=zero_balance_flag,

            fraud_probability=round(prob, 6),
            result=result
        )

        # 🔹 Store SHAP JSON
        request.session['shap_values'] = shap_json

        return redirect('user_result', predict_obj.predict_id)

    return render(request, 'userapp/user-predict.html')


# 🚀 RESULT VIEW
def user_result(request, id):
    p = Predict.objects.get(predict_id=id)

    shap_values = request.session.get('shap_values', "{}")

    context = {
        'p': p,   # ✅ matches template
        'shap_values': shap_values  # ✅ JSON string
    }

    return render(request, 'userapp/user-result.html', context)