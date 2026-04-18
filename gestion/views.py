from django.shortcuts import render, redirect
from .models import Residente, PlanMedicacion, HistorialAdministracion

def lista_residentes(request):
    #  Buscamos los datos
    residentes_db = Residente.objects.all()
    
    #  Preparamos el paquete de datos
    contexto = {
        'lista_de_residentes': residentes_db
    }
    
    # Entregamos los datos al template
    return render(request, 'gestion/lista_residentes.html', contexto)

#planes activos
def dashboard_enfermeria(request):
    planes_activos = PlanMedicacion.objects.filter(activo=True).order_by('hora_inicio')

    contexto = {
        'planes': planes_activos
    }
    
    #  Entregamos los datos al template
    return render(request, 'gestion/dashboard.html', contexto)

def administrar_medicamento(request, plan_id):
    # 1. Buscamos el plan de la pastilla exacta
    plan_seleccionado = PlanMedicacion.objects.get(id=plan_id)
    
    # 2. Generamos el comprobante con los 3 datos obligatorios 
    if plan_seleccionado.dosis_tomadas_hoy < int(plan_seleccionado.dosis):
        HistorialAdministracion.objects.create(
        plan=plan_seleccionado, 
        estado='ADMINISTRADO',
        usuario=request.user
         )
    
    #  El "salto" automático de regreso al panel 
    return redirect('dashboard')