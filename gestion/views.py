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

def administrar_medicamento(request, plan_id, estado):
    plan_seleccionado = PlanMedicacion.objects.get(id=plan_id)
    
    # 1. Atrapamos el texto del formulario. Si el botón no envía texto (como el botón verde), se guarda en blanco ('')
    texto_obs = request.POST.get('observacion', '')
    
    if plan_seleccionado.requiere_dosis_hoy:
        HistorialAdministracion.objects.create(
            plan=plan_seleccionado, 
            estado=estado,
            usuario=request.user,
            observaciones=texto_obs  
        )
    if estado == 'ADMINISTRADO':
            # Verificamos que haya stock para evitar que los números bajen de cero (negativos)
            if plan_seleccionado.stock_actual > 0:
                plan_seleccionado.stock_actual -= 1
                plan_seleccionado.save() # ¡No olvides guardar los cambios en la base de datos!
        # ----------------------------------
    
  
    return redirect('dashboard')