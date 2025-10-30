import traceback
from web_sockects.consumers import AbstractConsumer
from django.conf import settings
import logging
from .models import Notifications
User = settings.AUTH_USER_MODEL
from channels.db import database_sync_to_async
from django.db import transaction
from web_sockects.models import ActiveConnection
from django.core.serializers.json import DjangoJSONEncoder
import json
logger = logging.getLogger(__name__)

class NotificationConsumer(AbstractConsumer):
    HEARTBEAT_INTERVAL = 40  # veces en ejecucion -1
    async def get_group(self):
        return f"notifications{self.user.pk}"

    async def on_authenticated_connect(self, user):
        self.user_group = f"notificacion_{user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
    @database_sync_to_async
    def create_notification_sync(self, message, type_notification):
        with transaction.atomic():
            return Notifications.objects.create(
                user=self.user,
                message=message,
                type=type_notification
            )
    @database_sync_to_async
    def get_active_connection(self, user_id, group):
        try:
            active_connection = list(ActiveConnection.objects.filter(user_id=user_id, group=group).values())
            return active_connection
        except ActiveConnection.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error al obtener la conexión activa: {str(e)}")
            return None
    
    @database_sync_to_async
    def get_notifications(self, user_id):
        try:
            notifications = list(Notifications.objects.filter(user_id=user_id).values())
            return notifications
        except Notifications.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error al obtener la conexión notificaciones: {str(e)}")
            return None
    
    async def handle_message(self, message_type, content):
        if message_type == "send_notification":
            if self.connection_type == "Server":
                # 2. ENVIAR A CLIENTE ACTIVO
                active_connection = await self.get_active_connection(
                    user_id=self.user.id,
                    group=self.group
                )

                # 1. CREAR NOTIFICACIÓN EN DB (síncrono → async)
                try:
                    notification = await self.create_notification_sync(
                        message=content['message'],
                        type_notification=content['type_notification']
                    )
                    await self.send_json({
                        "type": "success",
                        "message": f"Notificación guardada con éxito. {notification}"
                    })
                    if active_connection:
                        await self.channel_layer.send(
                            active_connection[0]['channel_name'],
                            {
                                "type": "send_notification",
                                "message": content['message'],
                                "notification_type":content['type_notification'],
                            }
                        )
                except Exception as e:
                    import traceback; traceback.print_exc()
                    await self.send_json({
                        "type": "error",
                        "message": f"Error al guardar: {str(e)}"
                    })

        else:
            notifications = await self.get_notifications(self.user)
            await self.send_json({
                'type':'list',
                "notifications":json.dumps(notifications, cls=DjangoJSONEncoder)
            })

    async def send_notification(self, event):
        # Validar que el evento venga del backend autorizado
        # Enviar la notificación al cliente
        await self.send_json({
            "type": "notification",
            "user_id": self.user.pk,
            "message": event["message"],
            "notification_type":event['notification_type'],
            'notification': True
        })
