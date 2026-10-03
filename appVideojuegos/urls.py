from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('consultar/', views.consultar, name='consultar'),
    path('registrar/', views.registrar, name='registrar'),
    path('modificar/<int:id>/', views.modificar, name='modificar'),
    path('acerca/', views.acerca, name='acerca'),
    path('progreso/', views.mi_progreso, name='mi_progreso'),
]