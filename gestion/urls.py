from django.urls import path
from . import views

urlpatterns = [
    path('residentes/', views.lista_residentes, name='lista_residentes'),
    path('dashboard/', views.dashboard_enfermeria, name='dashboard'),
    path('administrar/<int:plan_id>/<str:estado>/', views.administrar_medicamento, name='administrar_medicamento'),
]