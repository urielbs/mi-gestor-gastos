from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('fixed-income/', views.manage_fixed_income, name='manage_fixed_income'),
    path('fixed-income/delete/<int:pk>/', views.delete_fixed_income, name='delete_fixed_income'),
]

