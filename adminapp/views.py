from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from userapp.models import userModel
from adminapp.models import datasetModel
import pandas as pd
from pickle import load
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve

# Create your views here.
def admin_dash(request):
    user_count = userModel.objects.all().count()
    user_accepted_count = userModel.objects.filter(user_status = 'accepted').count()
    user_penidng_count = userModel.objects.filter(user_status = 'pending').count()
    user_rejected_count = userModel.objects.filter(user_status = 'rejected').count()
    user_context = {
                'a' : user_count, 
                'b':user_accepted_count, 
                'c':user_penidng_count, 
                'd':user_rejected_count}
    return render(request, 'adminapp/admin-dashboard.html', user_context )

def active_users(request):
    active = userModel.objects.filter(user_status = 'accepted').order_by('user_id')
    paginator = Paginator(active, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    return render(request, 'adminapp/admin-activeusers.html', {'user': post})

def all_users(request):
    allusers = userModel.objects.filter(~Q(user_status = 'rejected')).order_by('user_id')
    paginator = Paginator(allusers, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    return render(request, 'adminapp/admin-allusers.html', {'user': post} )

def rejected_users(request):    
    rejected = userModel.objects.filter(user_status = 'rejected').order_by('user_id')
    paginator = Paginator(rejected, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    return render(request, 'adminapp/admin-rejectedusers.html', {'user': post})

def pending_users(request):
    pending = userModel.objects.filter(user_status = 'pending').order_by('user_id')
    paginator = Paginator(pending, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    return render(request, 'adminapp/admin-pendingusers.html', {'user': post})

def accept_user(request, id):
    status_update = userModel.objects.get(user_id = id)
    status_update.user_status = 'accepted'
    status_update.save()
    messages.success(request, 'User was accepted!')
    return redirect ('pending_users')

def reject_user(request, id):
    status_update2 = userModel.objects.get(user_id = id)
    status_update2.user_status = 'rejected'
    status_update2.save()
    messages.info(request, 'User was rejected!')
    return redirect('pending_users')

def change_status(request, id):
    status_update = userModel.objects.get(user_id = id)
    if status_update.user_status == 'accepted':
        status_update.user_status = 'rejected'
        messages.info(request, 'User status changed to rejected!')
    
    status_update.save()
    return redirect('active_users')

def delete_user(request, id):
    userModel.objects.get(user_id = id).delete()
    messages.warning(request, 'User was Deleted..!')
    return redirect('allusers')


def upload_dataset(request):
    if request.method == 'POST':
        file = request.FILES['file']
        datasetModel.objects.create( dataset = file)
        messages.success(request, 'Your dataset was uploaded!')
        return redirect('view_dataset')
    return render(request, 'adminapp/admin-uploaddataset.html')

# def view_dataset(request):
#     data =datasetModel.objects.all().order_by('-data_id').first()
#     file=str(data.dataset)   
#     df=pd.read_csv(file,index_col=0)
#     table=df.to_html(table_id='data_table')

#     return render(request, 'adminapp/admin-viewdataset.html', {'data' : table})
import os

def view_dataset(request):
    data = datasetModel.objects.all().order_by('-data_id').first()

    if not data or not data.dataset:
        messages.error(request, "No dataset found!")
        return redirect('upload_dataset')

    file_path = data.dataset.path   # ✅ IMPORTANT FIX

    if not os.path.exists(file_path):
        messages.error(request, "File not found on server. Please re-upload dataset.")
        return redirect('upload_dataset')

    df = pd.read_csv(file_path, index_col=0)
    table = df.to_html(table_id='data_table')

    return render(request, 'adminapp/admin-viewdataset.html', {'data': table})


def delete_dataset(request, id):
    dataset = datasetModel.objects.get(data_id = id).delete()
    messages.warning (request, 'Dataset was deleted!')
    return redirect('view_dataset')

def admin_view_profile(request, id):
    user = userModel.objects.get(user_id = id)
    context = {"user": user}
    return render(request, 'adminapp/admin-view-profile.html', context)

import joblib

# 🔹 GLOBAL LOAD (VERY IMPORTANT)
encoder = joblib.load("algorithms/label_encoder.pkl")
feature_columns = joblib.load("algorithms/feature_columns.pkl")

def preprocess_data(df, use_engineered=False):
    
    # 🔹 Encode safely
    df['type'] = encoder.transform(df['type'])

    # 🔥 Add engineered features ONLY when needed
    if use_engineered:
        df['balance_diff_org'] = df['oldbalanceOrg'] - df['newbalanceOrig']
        df['balance_diff_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
        df['zero_balance_flag'] = (
            (df['oldbalanceOrg'] == 0) | (df['oldbalanceDest'] == 0)
        ).astype(int)

    return df

def logreg(request):
    dataset = datasetModel.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-alg-logreg.html', {'data': dataset})


def catboost(request):
    dataset = datasetModel.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-alg-CatBoost.html', {'data': dataset})


def xgboost(request):
    dataset = datasetModel.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-alg-XGBoost.html', {'data': dataset})

import joblib

# def lr_run(request, id):
#     data = datasetModel.objects.get(data_id=id)
#     file = str(data.dataset)

#     df = pd.read_csv(file)

#     model = joblib.load("algorithms/logistic_regression.pkl")

#     # ❗ Logistic was trained WITHOUT engineered features
#     df = preprocess_data(df, use_engineered=True)   # ✅ CHANGE HERE

#     # 🔥 Ensure only required columns
#     X = df[feature_columns]
#     Y = df['isFraud']

#     prediction = model.predict(X)

#     data.lr_accuracy = accuracy_score(Y, prediction)
#     data.lr_precision = precision_score(Y, prediction)
#     data.lr_recall = recall_score(Y, prediction)
#     data.lr_f1_score = f1_score(Y, prediction)
#     data.lr_algo = 'Logistic Regression'

#     data.save()

#     messages.success(request, 'Logistic Regression executed successfully!')
#     return redirect('logreg')
def lr_run(request, id):
    data = datasetModel.objects.get(data_id=id)

    import os
    file_path = data.dataset.path   # ✅ FIX

    if not os.path.exists(file_path):
        messages.error(request, "Dataset missing. Re-upload required.")
        return redirect('view_dataset')

    df = pd.read_csv(file_path)

    model = joblib.load("algorithms/logistic_regression.pkl")

    df = preprocess_data(df, use_engineered=True)

    X = df[feature_columns]
    Y = df['isFraud']

    prediction = model.predict(X)

    data.lr_accuracy = accuracy_score(Y, prediction)
    data.lr_precision = precision_score(Y, prediction)
    data.lr_recall = recall_score(Y, prediction)
    data.lr_f1_score = f1_score(Y, prediction)
    data.lr_algo = 'Logistic Regression'

    data.save()

    messages.success(request, 'Logistic Regression executed successfully!')
    return redirect('logreg')

def xgb_run(request, id):
    data = datasetModel.objects.get(data_id=id)
    file = str(data.dataset)

    df = pd.read_csv(file)

    model = joblib.load("algorithms/xgboost.pkl")

    # ✅ WITH engineered features
    df = preprocess_data(df, use_engineered=True)

    X = df[feature_columns]
    Y = df['isFraud']

    prediction = model.predict(X)

    data.xgb_accuracy = accuracy_score(Y, prediction)
    data.xgb_precision = precision_score(Y, prediction)
    data.xgb_recall = recall_score(Y, prediction)
    data.xgb_f1_score = f1_score(Y, prediction)
    data.xgb_algo = 'XGBoost'

    data.save()

    messages.success(request, 'XGBoost executed successfully!')
    return redirect('xgboost')

def cat_run(request, id):
    data = datasetModel.objects.get(data_id=id)
    file = str(data.dataset)

    df = pd.read_csv(file)

    model = joblib.load("algorithms/catboost.pkl")  # balanced model

    # ✅ WITH engineered features
    df = preprocess_data(df, use_engineered=True)

    X = df[feature_columns]
    Y = df['isFraud']

    prediction = model.predict(X)

    data.cat_accuracy = accuracy_score(Y, prediction)
    data.cat_precision = precision_score(Y, prediction)
    data.cat_recall = recall_score(Y, prediction)
    data.cat_f1_score = f1_score(Y, prediction)
    data.cat_algo = 'CatBoost'

    data.save()

    messages.success(request, 'CatBoost executed successfully!')
    return redirect('catboost')


def analysis(request):
    try:
        data = datasetModel.objects.all().order_by('-data_id').first()

        context = {
            'lr_a': data.lr_accuracy * 100,
            'lr_p': data.lr_precision * 100,
            'lr_r': data.lr_recall * 100,
            'lr_f': data.lr_f1_score * 100,

            'xgb_a': data.xgb_accuracy * 100,
            'xgb_p': data.xgb_precision * 100,
            'xgb_r': data.xgb_recall * 100,
            'xgb_f': data.xgb_f1_score * 100,

            'cat_a': data.cat_accuracy * 100,
            'cat_p': data.cat_precision * 100,
            'cat_r': data.cat_recall * 100,
            'cat_f': data.cat_f1_score * 100,
        }

        return render(request, 'adminapp/admin-analysis.html', context)

    except:
        messages.warning(request, 'Run all models to compare values')
        return redirect('view_dataset')

