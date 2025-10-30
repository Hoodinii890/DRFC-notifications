from django.db import models
from django.conf import settings
from django.utils import timezone


class Notifications(models.Model):
    class Status(models.TextChoices):
        SIN_LEER = "sin_leer", "Sin leer"
        LEIDO = "leido", "Leído"
        ELIMINADO = "eliminado", "Eliminado"

    class Type(models.TextChoices):
        SISTEMA = "sistema", "Sistema"
        ALERTA = "alerta", "Alerta"
        MENSAJE = "mensaje", "Mensaje"
        PERSONALIZADA = "personalizada", "Personalizada"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones_usuario"
    )
    message = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SIN_LEER
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SISTEMA
    )
    read_at = models.DateTimeField(null=True, blank=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    action_url = models.URLField(null=True, blank=True)

    def mark_as_read(self):
        self.status = self.Status.READ
        self.read_at = timezone.now()
        self.save()

    def __str__(self):
        return f"['{self.type}'] {self.message[:40]}..."
