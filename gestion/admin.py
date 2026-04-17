from django.contrib import admin
from .models import Usuario, Residente, Medicamento, PlanMedicacion, HistorialAdministracion

# Registramos nuestros modelos en el panel de administración
admin.site.register(Usuario)
admin.site.register(Residente)
admin.site.register(Medicamento)
admin.site.register(PlanMedicacion)
admin.site.register(HistorialAdministracion)