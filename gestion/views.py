from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.db import IntegrityError

from .models import Residente, PlanMedicacion, HistorialAdministracion, Medicamento
from .forms import LoginForm, ResidenteForm


# 🔐 ================== AUTH ==================

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


# 🏥 ================== DASHBOARD ==================

@login_required
def dashboard_enfermeria(request):
    planes_activos = PlanMedicacion.objects.filter(activo=True).order_by('hora_inicio')

    return render(request, 'gestion/dashboard.html', {
        'planes': planes_activos
    })


# 👥 ================== RESIDENTES ==================

@login_required
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


@login_required
def crear_residente(request):
    form = ResidenteForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente creado correctamente")
            return redirect('gestion:lista_residentes')

    return render(request, 'gestion/residente_form.html', {'form': form})


@login_required
def editar_residente(request, id):
    residente = get_object_or_404(Residente, id=id)
    form = ResidenteForm(request.POST or None, instance=residente)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado correctamente")
            return redirect('gestion:lista_residentes')

    return render(request, 'gestion/residente_form.html', {'form': form})


@login_required
def eliminar_residente(request, id):
    residente = get_object_or_404(Residente, id=id)

    if request.method == 'POST':
        residente.delete()
        messages.success(request, "Paciente eliminado correctamente")
        return redirect('gestion:lista_residentes')

    return render(request, 'gestion/confirmar_eliminar.html', {
        'residente': residente
    })


# 💊 ================== MEDICAMENTOS ==================

@login_required
def medicamentos(request):

    q = request.GET.get('q')
    medicamentos = Medicamento.objects.all()

    if q:
        medicamentos = medicamentos.filter(
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
        'medicamentos': medicamentos,
        'query': q
    })


@login_required
def eliminar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)

    if request.method == 'POST':
        try:
            medicamento.delete()
            messages.success(request, "Medicamento eliminado correctamente")
        except IntegrityError:
            messages.error(request, "No se puede eliminar, está en uso en un plan")

    return redirect('gestion:medicamentos')


# 💊 ================== PLANES ==================

@login_required
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


@login_required
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


@login_required
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


# 💊 ================== ADMINISTRACIÓN ==================

@login_required
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