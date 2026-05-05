from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('padre', 'Padre/Tutor'),
        ('administrativo', 'Administrativo'),
        ('directivo', 'Directivo'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='estudiante', db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Curso(models.Model):
    NIVEL_CHOICES = (
        ('inicial', 'Inicial'),
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
    )

    nombre = models.CharField(max_length=50)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    cantidad_secciones = models.IntegerField(default=1)
    periodo = models.CharField(max_length=20, blank=True, default='')
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('retirado', 'Retirado'),
        ('egresado', 'Egresado'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estudiante')
    numero_expediente = models.CharField(max_length=50, unique=True)
    documento = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.numero_expediente}"


class Docente(models.Model):
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='docente')
    documento = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    titulo_profesional = models.CharField(max_length=200)
    fecha_contratacion = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', db_index=True)

    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"
