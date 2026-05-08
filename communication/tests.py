from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Comunicado, Notificacion

User = get_user_model()

class CommunicationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', username='testuser', password='password123', role='directivo')

    def test_create_comunicado(self):
        comunicado = Comunicado.objects.create(titulo='Test Title', contenido='Test Content', autor=self.user)
        self.assertEqual(comunicado.titulo, 'Test Title')
        self.assertEqual(comunicado.autor, self.user)

    def test_create_notificacion(self):
        notif = Notificacion.objects.create(usuario=self.user, mensaje='Test Message')
        self.assertEqual(notif.usuario, self.user)
        self.assertFalse(notif.leido)
