from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_enfermeria, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='gestion/login.html'), name='login'),
    path('residentes/', views.lista_residentes, name='lista_residentes'),
    path('dashboard/', views.dashboard_enfermeria, name='dashboard'),
    path('administrar/<int:plan_id>/<str:estado>/', views.administrar_medicamento, name='administrar_medicamento'),
    path('editar-ficha/<int:paciente_id>/', views.editar_ficha, name='editar_ficha'),
    path('registrar-residente/', views.registrar_residente, name='registrar_residente'),
    path('asignar-plan/<int:residente_id>/', views.asignar_plan, name='asignar_plan'),
]