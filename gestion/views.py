from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.db import IntegrityError

from .models import Residente, PlanMedicacion, HistorialAdministracion, Medicamento, Usuario
from .forms import LoginForm, ResidenteForm, PlanMedicacionForm, RegistroPersonalForm


# 🔐 ================== REGLAS DE SEGURIDAD (CANDADOS) ==================

# Regla: ¿Es un Administrador?
def es_admin(usuario):
    # Estandarizamos a mayúsculas por si acaso (.upper()) y verificamos superusuario
    return usuario.is_authenticated and (usuario.is_superuser or usuario.rol.upper() == 'ADMIN')

# Regla: ¿Es Enfermera o Admin? (Para acciones médicas)
def es_enfermera_o_admin(usuario):
    return usuario.is_authenticated and (usuario.is_superuser or usuario.rol.upper() in ['ENFERMERA', 'ADMIN'])


# 🔑 ================== AUTENTICACIÓN (LOGIN / LOGOUT) ==================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('gestion:dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('gestion:dashboard')
        else:
            messages.error(request, "Credenciales incorrectas")

    return render(request, 'gestion/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('gestion:login')


# 🏥 ================== DASHBOARD PRINCIPAL ==================

@login_required(login_url='gestion:login')
def dashboard_enfermeria(request):
    planes_activos = PlanMedicacion.objects.filter(activo=True).order_by('hora_inicio')

    return render(request, 'gestion/dashboard.html', {
        'planes': planes_activos
    })


# 👨‍⚕️ ================== GESTIÓN DE PERSONAL (SOLO ADMIN) ==================

@login_required(login_url='gestion:login')
@user_passes_test(es_admin, login_url='gestion:dashboard')
def lista_personal(request):
    # Buscamos a todo el personal registrado
    personal_db = Usuario.objects.all()
    return render(request, 'gestion/lista_personal.html', {'lista_personal': personal_db})

@login_required(login_url='gestion:login') 
@user_passes_test(es_admin, login_url='gestion:dashboard')
def registrar_personal(request):
    if request.method == 'POST':
        form = RegistroPersonalForm(request.POST)
        
        if form.is_valid():
            nuevo_usuario = form.save(commit=False)
            password_limpia = form.cleaned_data['password']
            nuevo_usuario.set_password(password_limpia)
            
            # ---> EL TRUCO: Igualamos el username interno de Django al RUT <---
            nuevo_usuario.username = nuevo_usuario.rut 
            
            nuevo_usuario.save()
            return redirect('gestion:lista_personal') 
            
    else:
        form = RegistroPersonalForm()
        
    return render(request, 'gestion/registrar_personal.html', {'form': form})

@login_required(login_url='gestion:login')
@user_passes_test(es_admin, login_url='gestion:dashboard')
def eliminar_personal(request, usuario_id):
    # Buscamos al usuario por su ID
    usuario_a_borrar = get_object_or_404(Usuario, id=usuario_id)
    
    # PEQUEÑO SEGURO: Evitamos que el Administrador se borre a sí mismo por accidente
    if request.user.id != usuario_a_borrar.id:
        usuario_a_borrar.delete()
        
    # Volvemos a la lista de personal
    return redirect('gestion:lista_personal')


# 👥 ================== GESTIÓN DE RESIDENTES ==================

@login_required(login_url='gestion:login')
def lista_residentes(request):
    query = request.GET.get('q')
    residentes = Residente.objects.all()

    if query:
        residentes = residentes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query)
        ).distinct()

    residentes = residentes.prefetch_related(
        Prefetch(
            'planmedicacion_set',
            queryset=PlanMedicacion.objects.filter(activo=True)
        )
    )

    return render(request, 'gestion/lista_residentes.html', {
        'lista_de_residentes': residentes,
        'query': query
    })

@login_required(login_url='gestion:login')
def crear_residente(request):
    form = ResidenteForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            nuevo_residente = form.save() 
            messages.success(request, "Paciente creado correctamente")
            return redirect('gestion:asignar_plan', residente_id=nuevo_residente.id)

    return render(request, 'gestion/residente_form.html', {'form': form})

@login_required(login_url='gestion:login')
def editar_residente(request, id):
    residente = get_object_or_404(Residente, id=id)
    form = ResidenteForm(request.POST or None, instance=residente)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado correctamente")
            return redirect('gestion:lista_residentes')

    return render(request, 'gestion/residente_form.html', {'form': form})

@login_required(login_url='gestion:login')
def eliminar_residente(request, id):
    residente = get_object_or_404(Residente, id=id)

    if request.method == 'POST':
        residente.delete()
        messages.success(request, "Paciente eliminado correctamente")
        return redirect('gestion:lista_residentes')

    return render(request, 'gestion/confirmar_eliminar.html', {
        'residente': residente
    })

@login_required(login_url='gestion:login')
def editar_ficha(request, paciente_id):
    paciente = get_object_or_404(Residente, id=paciente_id)
    if request.method == 'POST':
        paciente.diagnostico_principal = request.POST.get('diagnostico_principal')
        paciente.contacto_familiar = request.POST.get('contacto_familiar')
        paciente.condicion_deglucion = request.POST.get('condicion_deglucion')
        paciente.save()
        messages.success(request, "Ficha médica actualizada.")
        return redirect('gestion:dashboard')
        
    return render(request, 'gestion/editar_ficha.html', {'paciente': paciente})


# 💊 ================== INVENTARIO DE MEDICAMENTOS ==================

@login_required(login_url='gestion:login')
def medicamentos(request):
    q = request.GET.get('q')
    medicamentos_db = Medicamento.objects.all()

    if q:
        medicamentos_db = medicamentos_db.filter(
            Q(nombre_comercial__icontains=q) |
            Q(nombre_generico__icontains=q)
        )

    if request.method == 'POST':
        try:
            Medicamento.objects.create(
                nombre_comercial=request.POST.get('nombre_comercial'),
                nombre_generico=request.POST.get('nombre_generico'),
                miligramos=int(request.POST.get('miligramos')),
                presentacion=request.POST.get('presentacion'),
            )
            messages.success(request, "Medicamento creado correctamente")
        except Exception:
            messages.error(request, "Error al crear el medicamento")

        return redirect('gestion:medicamentos')

    return render(request, 'gestion/medicamentos.html', {
        'medicamentos': medicamentos_db,
        'query': q
    })

@login_required(login_url='gestion:login')
def eliminar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)

    if request.method == 'POST':
        try:
            medicamento.delete()
            messages.success(request, "Medicamento eliminado correctamente")
        except IntegrityError:
            messages.error(request, "No se puede eliminar, está en uso en un plan")

    return redirect('gestion:medicamentos')


# 📋 ================== PLANES DE MEDICACIÓN ==================

@login_required(login_url='gestion:login')
def crear_plan(request):
    residente_id = request.GET.get('residente')

    if request.method == 'POST':
        PlanMedicacion.objects.create(
            residente_id=int(request.POST.get('residente')),
            medicamento_id=int(request.POST.get('medicamento')),
            dosis=int(request.POST.get('dosis')),
            stock_actual=int(request.POST.get('stock')),
            frecuencia_horas=int(request.POST.get('frecuencia')),
            hora_inicio=request.POST.get('hora_inicio'),
            fecha_inicio_plan=request.POST.get('fecha_inicio'),
            activo=True
        )

        messages.success(request, "Plan de medicación creado correctamente")
        return redirect('gestion:lista_residentes')

    return render(request, 'gestion/plan_form.html', {
        'residentes': Residente.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'residente_seleccionado': int(residente_id) if residente_id else None
    })

@login_required(login_url='gestion:login')
def asignar_plan(request, residente_id):
    residente = get_object_or_404(Residente, id=residente_id)
    
    if request.method == 'POST':
        form = PlanMedicacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion:dashboard')
    else:
        form = PlanMedicacionForm(initial={'residente': residente})

    return render(request, 'gestion/asignar_plan.html', {'form': form, 'residente': residente})

@login_required(login_url='gestion:login')
def editar_plan(request, id):
    plan = get_object_or_404(PlanMedicacion, id=id)

    if request.method == 'POST':
        plan.residente_id = int(request.POST.get('residente'))
        plan.medicamento_id = int(request.POST.get('medicamento'))
        plan.dosis = int(request.POST.get('dosis'))
        plan.stock_actual = int(request.POST.get('stock'))
        plan.frecuencia_horas = int(request.POST.get('frecuencia'))
        plan.hora_inicio = request.POST.get('hora_inicio')
        plan.fecha_inicio_plan = request.POST.get('fecha_inicio')

        plan.save()

        messages.success(request, "Plan actualizado correctamente")
        return redirect('gestion:lista_residentes')

    return render(request, 'gestion/plan_form.html', {
        'plan': plan,
        'residentes': Residente.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'residente_seleccionado': plan.residente.id
    })

@login_required(login_url='gestion:login')
def eliminar_plan(request, id):
    plan = get_object_or_404(PlanMedicacion, id=id)

    if request.method == 'POST':
        plan.activo = False
        plan.save()

        messages.success(request, "Plan desactivado correctamente")
        return redirect('gestion:lista_residentes')

    return render(request, 'gestion/confirmar_eliminar_plan.html', {
        'plan': plan
    })


# 💉 ================== ADMINISTRACIÓN Y REGISTRO CLINICO ==================

@login_required(login_url='gestion:login')
def administrar_medicamento(request, plan_id, estado):
    if request.method == 'POST':
        plan = get_object_or_404(PlanMedicacion, id=plan_id)
        texto_obs = request.POST.get('observacion', '')

        if plan.requiere_dosis_hoy:
            HistorialAdministracion.objects.create(
                plan=plan,
                estado=estado,
                usuario=request.user,
                observaciones=texto_obs
            )

            if estado == 'ADMINISTRADO':
                if plan.stock_actual > 0:
                    plan.stock_actual -= 1
                    plan.save()
                    messages.success(request, "Medicamento administrado")
                else:
                    messages.warning(request, "Sin stock disponible")
            else:
                messages.info(request, f"Estado registrado: {estado}")
        else:
            messages.warning(request, "No corresponde administrar en este momento")

    return redirect('gestion:dashboard')

# 📊 ================== REPORTES ==================

@login_required(login_url='gestion:login')
def reporte_historial(request):
    # Traemos todo el historial, ordenado del más reciente al más antiguo
    # Usamos '-id' para que los últimos registros salgan arriba
    historial = HistorialAdministracion.objects.select_related(
        'plan__residente', 'plan__medicamento', 'usuario'
    ).all().order_by('-id')
    
    return render(request, 'gestion/reporte_historial.html', {'historial': historial})