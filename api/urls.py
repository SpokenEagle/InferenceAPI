# api/urls.py
from django.urls import path
from .views import login_view, register_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
]


# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('api', views.index, name='index'),
#     path('sample', views.test, name='test'),
#     path('', views.direct_form, name='directForm'),
#     path('summary', views.direct_summary, name='directSummary'),
#     path('chat', views.chat, name='chat'),
#     # path('login', views.serve_login, name='serve_login'),
#     path('logout', views.logout_view, name='logout_view'),
#     path('login', views.login_view, name='login_view'),
#     path('signup', views.signup, name='signup'),
#     path('query', views.user_query, name='user_query'),
#     path('testing', views.test_html, name='test_html'),
# ]
