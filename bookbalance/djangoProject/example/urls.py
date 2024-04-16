from example import views
from example.views import logout, register, login_view, index, mainpage, \
visualization, chatbox, support, support0, account
from django.urls import path, re_path

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/',register,name='register'),
    path('logout/', logout, name='logout'),
    path('index/',index, name='index'),
    path('mainpage/', mainpage, name='mainpage'),
    path('mainpage/<str:username>/', views.mainpage, name='mainpage_with_username'),
    path('visualization/', visualization, name='visualization'),
    path('chatbox/', chatbox, name='chatbox'),
    path('support/', support, name='support'),
    path('support0/', support0, name='support0'),
    path('create/', views.record_create, name='record_create'),
    path('create/<str:username>/', views.record_create, name='record_create_with_username'),
    path('setbudget/', views.set_budget, name='set_budget'),
    path('report/', views.report_add, name='report'),
    path('search/', views.search, name='search'),
    path('search/<str:username>/', views.search, name='search_with_username'),
    path('chatbox/', views.chatbox, name='chatbox'),

    # Retrieve record list
    path('', views.record_list, name='record_list'),
    path('<str:username>/', views.record_list, name='record_list_with_username'),

    path('visualization/retrieve_current_month_income_expense/', views.retrieve_current_month_income_expense, name='retrieve_current_month_income_expense'),
    path('visualization/retrieve_current_year_income_expense/', views.retrieve_current_year_income_expense, name='retrieve_current_year_income_expense'),
    path('visualization/retrieve_year_has_data/', views.retrieve_year_has_data, name='retrieve_year_has_data'),
    path('visualization/retrieve_month_has_data/', views.retrieve_month_has_data, name='retrieve_month_has_data'),

    # Retrieve single record object
    re_path(r'^(?P<pk>\d+)/(?P<username>[\w.@+-]+)/$', views.record_detail, name='record_detail'),

    # Update a record
    # re_path(r'^(?P<pk>\d+)/update/$', views.record_update, name='record_update'),
    re_path(r'^(?P<pk>\d+)/update/(?P<username>[\w.@+-]+)/$', views.record_update, name='record_update'),


    # Delete a record
    # re_path(r'^(?P<pk>\d+)/delete/$', views.record_delete, name='record_delete'),
    re_path(r'^(?P<pk>\d+)/delete/(?P<username>[\w.@+-]+)/$', views.record_delete, name='record_delete'),

    # account setting
    path('account/<str:username>/', account, name='account'),
]

