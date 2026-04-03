from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Usuario, Inscripcion, Evento, ConfiguracionNotificacion


@receiver(post_save, sender=Usuario)
def crear_configuracion_notificacion(sender, instance, created, **kwargs):
    if created:
        ConfiguracionNotificacion.objects.get_or_create(usuario=instance)


@receiver(post_save, sender=Inscripcion)
def enviar_confirmacion_inscripcion(sender, instance, created, **kwargs):
    if not created:
        return

    usuario = instance.usuario
    evento = instance.evento

    try:
        config = usuario.configuracion_notificacion
        if not config.confirmacion_inscripcion:
            return
    except ConfiguracionNotificacion.DoesNotExist:
        pass  # enviar de todas formas

    if not usuario.email:
        return

    subject = f"Inscripción confirmada: {evento.titulo}"
    body = render_to_string(
        "sistema/emails/confirmacion_inscripcion.txt",
        {"usuario": usuario, "evento": evento},
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=True,
    )


@receiver(post_save, sender=Evento)
def notificar_nuevo_evento(sender, instance, created, **kwargs):
    if not created:
        return

    destinatarios = set()

    # Estudiantes de la misma escuela con notificación habilitada
    por_escuela = (
        Usuario.objects.filter(
            rol="ESTUDIANTE",
            escuela=instance.escuela,
            configuracion_notificacion__notificar_nueva_actividad_escuela=True,
        )
        .exclude(email="")
        .values_list("email", flat=True)
    )
    destinatarios.update(por_escuela)

    # Estudiantes de la misma facultad (diferente escuela) con notificación habilitada
    por_facultad = (
        Usuario.objects.filter(
            rol="ESTUDIANTE",
            escuela__facultad=instance.escuela.facultad,
            configuracion_notificacion__notificar_nueva_actividad_facultad=True,
        )
        .exclude(escuela=instance.escuela)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    destinatarios.update(por_facultad)

    if not destinatarios:
        return

    subject = f"Nuevo evento: {instance.titulo}"
    body = render_to_string(
        "sistema/emails/nuevo_evento_escuela.txt",
        {"evento": instance},
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        list(destinatarios),
        fail_silently=True,
    )
