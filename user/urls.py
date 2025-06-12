from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    #################### 회원 ####################
    path('register/', views.register, name='register'),
    path('token/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/', views.login, name='login'),
    path('user/', views.my_page, name='get_user_info'), 
    path('user/edit', views.my_edit, name='get_user_info'), 
    
    # 토큰 갱신
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #################### 어드민 ####################

    path('user/all', views.admin_user_data, name='admin_user_data'),
    
]