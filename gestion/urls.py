from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    
    path('registrar-personal/', views.registrar_personal, name='registrar_personal'),
    # ================== AUTENTICACIÓN ==================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
#BORRAR
    path('personal/', views.lista_personal, name='lista_personal'),
    path('personal/eliminar/<int:usuario_id>/', views.eliminar_personal, name='eliminar_personal'),
    # ================== DASHBOARD ==================
    path('dashboard/', views.dashboard_enfermeria, name='dashboard'),

    # ================== RESIDENTES ==================
    path('residentes/', views.lista_residentes, name='lista_residentes'),
    path('residentes/nuevo/', views.crear_residente, name='crear_residente'),
    path('residentes/editar/<int:id>/', views.editar_residente, name='editar_residente'),
    path('residentes/eliminar/<int:id>/', views.eliminar_residente, name='eliminar_residente'),

    # ================== MEDICAMENTOS ==================
    path('medicamentos/', views.medicamentos, name='medicamentos'),
    path('medicamentos/eliminar/<int:id>/', views.eliminar_medicamento, name='eliminar_medicamento'),

    # ================== PLANES ==================
    path('plan/nuevo/', views.crear_plan, name='crear_plan'),
    path('plan/editar/<int:id>/', views.editar_plan, name='editar_plan'),
    path('plan/eliminar/<int:id>/', views.eliminar_plan, name='eliminar_plan'),

    # ================== ADMINISTRACIÓN ==================
    path(
        'administrar/<int:plan_id>/<str:estado>/',
        views.administrar_medicamento,
        name='administrar_medicamento'
    ),
    
    # ➕ RUTAS MÉDICAS
    path('editar-ficha/<int:paciente_id>/', views.editar_ficha, name='editar_ficha'),
    path('asignar-plan/<int:residente_id>/', views.asignar_plan, name='asignar_plan'),

]