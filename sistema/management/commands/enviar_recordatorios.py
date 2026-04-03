from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from sistema.models import Inscripcion


class Command(BaseCommand):
    help = "Envía recordatorios por correo a usuarios inscritos en eventos próximos"

    def handle(self, *args, **options):
        ahora = timezone.now()
        enviados = 0
        errores = 0

        # Traer todas las inscripciones pendientes de recordatorio con evento futuro
        inscripciones = (
            Inscripcion.objects.filter(
                recordatorio_enviado=False,
                evento__fecha_evento__gt=ahora,
                usuario__configuracion_notificacion__recordatorio_evento=True,
            )
            .select_related(
                "usuario",
                "usuario__configuracion_notificacion",
                "evento",
                "evento__escuela",
            )
        )

        for inscripcion in inscripciones:
            config = inscripcion.usuario.configuracion_notificacion
            dias = config.dias_recordatorio
            ventana_inicio = ahora + timedelta(days=dias) - timedelta(hours=1)
            ventana_fin = ahora + timedelta(days=dias) + timedelta(hours=1)

            if not (ventana_inicio <= inscripcion.evento.fecha_evento <= ventana_fin):
                continue

            if not inscripcion.usuario.email:
                continue

            try:
                subject = f"Recordatorio: {inscripcion.evento.titulo} es pronto"
                body = render_to_string(
                    "sistema/emails/recordatorio_evento.txt",
                    {
                        "usuario": inscripcion.usuario,
                        "evento": inscripcion.evento,
                        "dias": dias,
                    },
                )
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [inscripcion.usuario.email],
                    fail_silently=False,
                )
                inscripcion.recordatorio_enviado = True
                inscripcion.save(update_fields=["recordatorio_enviado"])
                enviados += 1
                self.stdout.write(
                    f"  ✓ Recordatorio enviado a {inscripcion.usuario.email} "
                    f"para «{inscripcion.evento.titulo}»"
                )
            except Exception as e:
                errores += 1
                self.stderr.write(
                    f"  ✗ Error enviando a {inscripcion.usuario.email}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nResumen: {enviados} recordatorio(s) enviado(s), {errores} error(es)."
            )
        )
