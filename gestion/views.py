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
                plan_seleccionado.save()   
  
    return redirect('dashboard')

def editar_ficha(request, paciente_id):
    # 1. Buscamos al paciente exacto en la base de datos
    paciente = Residente.objects.get(id=paciente_id)
    
    # 2. Preguntamos si nos están enviando datos nuevos (presionaron Guardar)
    if request.method == 'POST':
        # Capturamos los 3 datos usando el atributo 'name' de tu HTML
        paciente.diagnostico_principal = request.POST.get('diagnostico_principal')
        paciente.contacto_familiar = request.POST.get('contacto_familiar')
        paciente.condicion_deglucion = request.POST.get('condicion_deglucion')
        
        # Guardamos todos los cambios juntos
        paciente.save()
        
        return redirect('dashboard')
        
    # 3. Si no es POST, simplemente mostramos la página de edición normal (GET)
    return render(request, 'gestion/editar_ficha.html', {'paciente': paciente})