"""proj_fd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from adminapp import views as  admin_views
from mainapp import views as main_views
from userapp import views as user_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # ADMIN_URLS
    path('admin', admin_views.admin_dash, name= 'admin_dash'),
    path('admin-all-users', admin_views.all_users, name= 'all_users'),
    path('admin-active-users', admin_views.active_users, name= 'active_users'),
    path('admin-pending-users', admin_views.pending_users, name= 'pending_users'),
    path('admin-rejected-users', admin_views.rejected_users, name= 'rejected_users'),
    path('admin-upload-dataset', admin_views.upload_dataset, name= 'upload_dataset'),
    
    path('admin-view-dataset', admin_views.view_dataset, name= 'view_dataset'),
    path('admin-delete-dataset/<int:id>', admin_views.delete_dataset, name= 'delete_dataset'),
    path('accept-user/<int:id>', admin_views.accept_user, name='accept_user'),
    path('reject-user/<int:id>', admin_views.reject_user, name='reject_user'),
    path('change-status/<int:id>', admin_views.change_status, name='change_status'),
    path('delete-user/<int:id>', admin_views.delete_user, name = 'delete_user'),
    path('admin-view-profile/<int:id>', admin_views.admin_view_profile, name= 'view_profile'),

    path('admin-algorithm-logreg', admin_views.logreg, name= 'logreg'),
    path('admin-algorithm-xgboost', admin_views.xgboost, name= 'xgboost'),
    path('admin-algorithm-catboost', admin_views.catboost, name= 'catboost'),
    path('xgb-run/<int:id>', admin_views.xgb_run, name='xgb_run'),
    path('lr-run/<int:id>', admin_views.lr_run, name='lr_run'),
    path('cat-run/<int:id>', admin_views.cat_run, name='cat_run'),
    
    path('admin-algorithm-analysis', admin_views.analysis, name= 'analysis'),

    # MAIN_URLS
    path('', main_views.home, name="home"),
    path('main-about', main_views.about, name="about"),
    path('main-contact', main_views.contact, name="contact"),
    path('main-admin-login', main_views.admin_login, name="admin_login"),
    path('main-user-register', main_views.user_register, name="user_register"),

    #USER_URLS
    path('user-login', user_views.user_login, name="user_login"),
    path('user-dash', user_views.user_dash, name="user_dash"),
    path('user-profile', user_views.user_profile, name="user_profile"),
    path('user-predict', user_views.user_predict, name="user_predict"),
    path('user-result/<int:id>', user_views.user_result, name="user_result"),



]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
