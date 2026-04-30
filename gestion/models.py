from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta

# 1. Gestión de Usuarios y Roles
class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('SECRETARIA', 'Secretaria'),
        ('ENFERMERA', 'Enfermera'),
        ('TENS', 'Técnico en Enfermería'),
    ]
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=15, choices=ROL_CHOICES, default='ENFERMERA')
    nombre_completo = models.CharField(max_length=200)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',
        blank=True
    )

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['username', 'email']

# 2. Ficha del Residente
class Residente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    habitacion_numero = models.IntegerField()
    alertas_criticas = models.TextField(blank=True, help_text="Alergias o condiciones especiales")
    activo = models.BooleanField(default=True)
    diagnostico_principal = models.CharField(max_length=200, blank=True, default="No especificado")
    contacto_familiar = models.CharField(max_length=200, blank=True, help_text="Nombre y Teléfono")
    condicion_deglucion = models.CharField(max_length=200, blank=True, default="Normal", help_text="Ej: Normal, Molido, Sonda")

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Hab: {self.habitacion_numero}"

# 3. Catálogo de Medicamentos
class Medicamento(models.Model):
    nombre_comercial = models.CharField(max_length=100)
    nombre_generico = models.CharField(max_length=100)
    miligramos = models.FloatField()
    presentacion = models.CharField(max_length=50, help_text="Ej: Comprimidos, Jarabe")

    def __str__(self):
        return f"{self.nombre_comercial} ({self.miligramos}mg)"

# 4. Plan de Medicación
class PlanMedicacion(models.Model):
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    dosis = models.CharField(max_length=100)
    stock_actual = models.IntegerField(default=0, help_text="Pastillas traídas por la familia")
    frecuencia_horas = models.IntegerField(help_text="Cada cuántas horas se administra")
    hora_inicio = models.TimeField()
    fecha_inicio_plan = models.DateField()
    activo = models.BooleanField(default=True)
    @property
    def obtener_ultima_dosis(self):
        # Python solo ejecutará esto cuando el HTML se lo pida
        return HistorialAdministracion.objects.filter(plan=self).order_by('-fecha_hora_real').first()
    @property
    def dosis_tomadas_hoy(self):
        return HistorialAdministracion.objects.filter(
            plan=self,
            fecha_hora_real__date=timezone.localdate(),
            estado='ADMINISTRADO'
        ).count()
    @property
    def requiere_dosis_hoy(self):
        # Aquí hacemos la conversión segura a número entero igual que en views.py
        return self.dosis_tomadas_hoy < int(self.dosis)
    @property
    def historial_hoy(self):
    # Traemos todos los registros de este plan que ocurrieron HOY
        return HistorialAdministracion.objects.filter(
        plan=self,
        fecha_hora_real__date=timezone.localdate(),
         ).order_by('fecha_hora_real') # Los ordenamos del más antiguo al más reciente
    
    @property
    def proxima_hora_esperada(self):
        """Calcula a qué hora toca la siguiente dosis del día"""
        if not self.requiere_dosis_hoy:
            return None
        
        horas_desplazamiento = self.dosis_tomadas_hoy * self.frecuencia_horas
        hoy = timezone.localdate()
        momento_inicio = datetime.combine(hoy, self.hora_inicio)
        
        # --- EL ARREGLO ESTÁ AQUÍ ---
        # Si la hora no tiene país, le asignamos la zona horaria actual de tu proyecto
        if timezone.is_naive(momento_inicio):
            momento_inicio = timezone.make_aware(momento_inicio)
        # ----------------------------
            
        hora_programada = momento_inicio + timedelta(hours=horas_desplazamiento)
        return hora_programada
    
    @property
    def esta_retrasado(self):
        """Devuelve True si la hora actual superó la hora programada y no se ha administrado"""
        if not self.requiere_dosis_hoy:
            return False
        
        # Obtenemos la hora con la zona horaria de Chile configurada
        ahora = timezone.localtime()
        programada = self.proxima_hora_esperada
        
        # Si ya pasó la hora programada por más de 1 minuto, está retrasado
        return ahora > (programada + timedelta(minutes=1))

# 5. Historial de Administración
class HistorialAdministracion(models.Model):
    ESTADOS = [
        ('ADMINISTRADO', 'Administrado'),
        ('RECHAZADO', 'Rechazado'),
        ('OMITIDO', 'Omitido'),
    ]
    plan = models.ForeignKey(PlanMedicacion, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha_hora_real = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS)
    observaciones = models.TextField(blank=True)
    

    class Meta:
        verbose_name_plural = "Historiales de Administración"