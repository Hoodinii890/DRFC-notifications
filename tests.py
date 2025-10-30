# tests.py
import threading
import asyncio
import time
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from Notificaciones.utils import send_user_notification
import uvicorn
from asgiref.sync import sync_to_async
from django.conf import settings

# Configuración del servidor ASGI
class ASGIServer(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.server = None

    def run(self):
        config = uvicorn.Config(
            self.app,
            host=settings.HOST,
            port=settings.WS_PORT,
            log_level="error"
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def stop(self):
        if self.server:
            self.server.should_exit = True

class NotificationTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Iniciar servidor ASGI en hilo
        from drfc.asgi import application
        cls.server = ASGIServer(application)
        cls.server.start()
        time.sleep(1)  # Esperar a que levante

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        super().tearDownClass()

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email="testuser@email.com", password="1234")

    def test_send_notification_to_user(self):
        @sync_to_async
        def get_user_id():
            return self.user.pk

        user_id = asyncio.run(get_user_id())

        async def inner():
            response = await send_user_notification(
                user_id=user_id,
                token=settings.INTERNAL_NOTIFICATION_TOKEN,
                message="Hola desde pruebas",
                path="ws://127.0.0.1:8001/ws/notificaciones/"
            )
            return response

        response = asyncio.run(inner())


