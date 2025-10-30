# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from Notificaciones.utils import send_user_notification
import asyncio
import threading
import asyncio
import time
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from Notificaciones.utils import send_user_notification
import uvicorn
from asgiref.sync import sync_to_async

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

class NotificacionesAPIView(APIView):
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

    def get(self, request):
        try:
            async def inner():
                response = await send_user_notification(
                    user_id=1,
                    token=settings.INTERNAL_NOTIFICATION_TOKEN,
                    message="Hola desde pruebas",
                    path=f"ws://{settings.HOST}:{settings.PORT}/ws/notificaciones/"
                )
                return response

            response = asyncio.run(inner())
            print(response)
            return Response({
                "status": "enviado",
                "respuesta_ws": response
            })
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)