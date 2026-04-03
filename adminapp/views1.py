from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from userapp.models import userModel
from adminapp.models import datasetModel

import pandas as pd
import os
import joblib
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score


# 🔹 BASE DIR (Render safe)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =========================================================
# 🔹 LAZY LOAD (IMPORTANT FOR RENDER)
# =========================================================
def load_artifacts():
    encoder = joblib.load(os.path.join(BASE_DIR, "algorithms/label_encoder.pkl"))
    feature_columns = joblib.load(os.path.join(BASE_DIR, "algorithms/feature_columns.pkl"))
    return encoder, feature_columns


def load_catboost_model():
    return joblib.load(os.path.join(BASE_DIR, "algorithms/catboost.pkl"))


# =========================================================
# 🔹 ADMIN DASHBOARD
# =========================================================
def admin_dash(request):
    return render(request, 'adminapp/admin-dashboard.html', {
        'a': userModel.objects.count(),
        'b': userModel.objects.filter(user_status='accepted').count(),
        'c': userModel.objects.filter(user_status='pending').count(),
        'd': userModel.objects.filter(user_status='rejected').count(),
    })


# =========================================================
# 🔹 USER MANAGEMENT
# =========================================================
def active_users(request):
    users = userModel.objects.filter(user_status='accepted').order_by('user_id')
    paginator = Paginator(users, 5)
    return render(request, 'adminapp/admin-activeusers.html', {'user': paginator.get_page(request.GET.get('page'))})


def all_users(request):
    users = userModel.objects.filter(~Q(user_status='rejected')).order_by('user_id')
    paginator = Paginator(users, 5)
    return render(request, 'adminapp/admin-allusers.html', {'user': paginator.get_page(request.GET.get('page'))})


def rejected_users(request):
    users = userModel.objects.filter(user_status='rejected').order_by('user_id')
    paginator = Paginator(users, 5)
    return render(request, 'adminapp/admin-rejectedusers.html', {'user': paginator.get_page(request.GET.get('page'))})


def pending_users(request):
    users = userModel.objects.filter(user_status='pending').order_by('user_id')
    paginator = Paginator(users, 5)
    return render(request, 'adminapp/admin-pendingusers.html', {'user': paginator.get_page(request.GET.get('page'))})


def accept_user(request, id):
    user = userModel.objects.get(user_id=id)
    user.user_status = 'accepted'
    user.save()
    messages.success(request, 'User accepted!')
    return redirect('pending_users')


def reject_user(request, id):
    user = userModel.objects.get(user_id=id)
    user.user_status = 'rejected'
    user.save()
    messages.warning(request, 'User rejected!')
    return redirect('pending_users')


def delete_user(request, id):
    userModel.objects.get(user_id=id).delete()
    messages.warning(request, 'User deleted!')
    return redirect('allusers')


# =========================================================
# 🔹 DATASET MANAGEMENT
# =========================================================
def upload_dataset(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            datasetModel.objects.create(dataset=file)
            messages.success(request, 'Dataset uploaded!')
            return redirect('view_dataset')
    return render(request, 'adminapp/admin-uploaddataset.html')


def view_dataset(request):
    data = datasetModel.objects.order_by('-data_id').first()

    if not data:
        return render(request, 'adminapp/admin-viewdataset.html')

    try:
        df = pd.read_csv(data.dataset.path).head(1000)  # ✅ LIMIT
        return render(request, 'adminapp/admin-viewdataset.html', {
            'data': df.to_html(classes='table table-striped')
        })
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect('upload_dataset')


# =========================================================
# 🔹 PREPROCESSING
# =========================================================
def preprocess(df, encoder):
    df['type'] = encoder.transform(df['type'])

    df['balance_diff_org'] = df['oldbalanceOrg'] - df['newbalanceOrig']
    df['balance_diff_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
    df['zero_balance_flag'] = (
        (df['oldbalanceOrg'] == 0) | (df['oldbalanceDest'] == 0)
    ).astype(int)

    return df


# =========================================================
# 🔥 CATBOOST EXECUTION (MAIN PART)
# =========================================================
def catboost_run(request, id):
    try:
        data = datasetModel.objects.get(data_id=id)

        # ✅ SAFE DATA LOAD
        df = pd.read_csv(data.dataset.path).head(10000)

        encoder, feature_columns = load_artifacts()
        model = load_catboost_model()

        df = preprocess(df, encoder)

        X = df[feature_columns]
        Y = df['isFraud']

        prediction = model.predict(X)

        data.cat_accuracy = accuracy_score(Y, prediction)
        data.cat_precision = precision_score(Y, prediction)
        data.cat_recall = recall_score(Y, prediction)
        data.cat_f1_score = f1_score(Y, prediction)
        data.cat_algo = "CatBoost"

        data.save()

        messages.success(request, "CatBoost executed successfully!")
        return redirect('catboost')

    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect('view_dataset')


# =========================================================
# 🔹 ANALYSIS
# =========================================================
def analysis(request):
    data = datasetModel.objects.order_by('-data_id').first()

    if not data:
        messages.warning(request, "No dataset found")
        return redirect('view_dataset')

    context = {
        'cat_a': (data.cat_accuracy or 0) * 100,
        'cat_p': (data.cat_precision or 0) * 100,
        'cat_r': (data.cat_recall or 0) * 100,
        'cat_f': (data.cat_f1_score or 0) * 100,
    }

    return render(request, 'adminapp/admin-analysis.html', context)
