from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ConfiguracionNotificacion, Escuela, Evento, Facultad, Inscripcion, Usuario


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
    search_fields = ["nombre"]


@admin.register(Escuela)
class EscuelaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "facultad"]
    list_filter = ["facultad"]
    search_fields = ["nombre"]


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["username", "get_full_name", "email", "rol", "escuela", "semestre_actual", "is_active"]
    list_filter = ["rol", "escuela__facultad", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Perfil UNPHU",
            {"fields": ("rol", "escuela", "semestre_actual")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Perfil UNPHU",
            {"fields": ("rol", "escuela", "semestre_actual")},
        ),
    )


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = [
        "titulo",
        "tipo",
        "fecha_evento",
        "escuela",
        "lugar",
        "publicado_por",
        "cupo_maximo",
        "cupos_disponibles_display",
        "fecha_creacion",
    ]
    list_filter = ["tipo", "escuela__facultad", "escuela"]
    search_fields = ["titulo", "descripcion", "lugar"]
    readonly_fields = ["publicado_por", "fecha_creacion", "fecha_modificacion"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.publicado_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Cupos disponibles")
    def cupos_disponibles_display(self, obj):
        disp = obj.cupos_disponibles()
        return "∞" if disp is None else disp


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ["usuario", "evento", "fecha_registro", "recordatorio_enviado"]
    list_filter = ["recordatorio_enviado", "evento__tipo"]
    search_fields = ["usuario__username", "evento__titulo"]
    readonly_fields = ["fecha_registro"]


@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = [
        "usuario",
        "confirmacion_inscripcion",
        "recordatorio_evento",
        "dias_recordatorio",
        "notificar_nueva_actividad_escuela",
        "notificar_nueva_actividad_facultad",
    ]
    list_filter = ["confirmacion_inscripcion", "recordatorio_evento"]
