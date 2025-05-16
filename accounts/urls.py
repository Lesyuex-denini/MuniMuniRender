from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'), 
    path('register/', views.signup_view, name='signup'), 
    path('home/', views.Home.as_view(), name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('articles/', views.articles_view, name='articles'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('recommendations/regenerate/', views.regenerate_recommendation, name='regenerate_recommendation'),
    path('recommendations/like/<int:recommendation_id>/', views.like_recommendation, name='like_recommendation'),
    path('recommendations/done/<int:recommendation_id>/', views.mark_done_recommendation, name='mark_done_recommendation'),
    path('recommendations/save/<int:recommendation_id>/', views.save_recommendation, name='save_recommendation'),
    path('recommendations/saved/', views.saved_recommendations_view, name='saved_recommendations'),
    path('recommendations/like_ai/<int:recommendation_id>/', views.like_ai_recommendation, name='like_ai_recommendation'),
    path('recommendations/done_ai/<int:recommendation_id>/', views.mark_done_ai_recommendation, name='mark_done_ai_recommendation'),
    path('recommendations/save_ai/<int:recommendation_id>/', views.save_ai_recommendation, name='save_ai_recommendation'),
]