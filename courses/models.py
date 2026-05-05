from django.db import models
from accounts.models import Estudiante, Docente, Curso, User


class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='materias')
    docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True, blank=True, related_name='materias')
    descripcion = models.TextField(blank=True)
    numero_horas = models.IntegerField()
    creditos = models.IntegerField(default=0)
    estado = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ('nombre', 'curso')

    def __str__(self):
        return f"{self.nombre} ({self.curso})"


class Inscripcion(models.Model):
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('retirado', 'Retirado'),
        ('culminado', 'Culminado'),
    )

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', db_index=True)
    registrada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inscripciones_registradas')

    class Meta:
        unique_together = ('estudiante', 'curso')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.estado == 'activo':
            self.estudiante.curso = self.curso
            self.estudiante.save(update_fields=['curso'])

    def __str__(self):
        return f"{self.estudiante} inscrito en {self.curso}"


class Actividad(models.Model):
    TIPO_CHOICES = (
        ('tarea', 'Tarea'),
        ('examen', 'Examen'),
        ('proyecto', 'Proyecto'),
        ('participacion', 'Participación'),
        ('otro', 'Otro'),
    )
    TRIMESTRE_CHOICES = (
        ('T1', 'Trimestre 1'),
        ('T2', 'Trimestre 2'),
        ('T3', 'Trimestre 3'),
    )

    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='actividades', null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='tarea')
    trimestre = models.CharField(max_length=2, choices=TRIMESTRE_CHOICES, default='T1', db_index=True)
    fecha = models.DateField(null=True, blank=True, db_index=True)
    ponderacion = models.FloatField(default=0)
    es_plantilla = models.BooleanField(default=False)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actividades')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.materia}"


class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='calificaciones')
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='calificaciones')
    nota = models.FloatField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='calificaciones_creadas')

    class Meta:
        unique_together = ('estudiante', 'actividad')

    def __str__(self):
        return f"{self.estudiante} - {self.actividad.nombre}: {self.nota}"


class Asistencia(models.Model):
    ESTADO_CHOICES = (
        ('P', 'Presente'),
        ('F', 'Falta'),
        ('L', 'Licencia'),
    )

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField(db_index=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', db_index=True)
    motivo = models.TextField(blank=True)
    registrada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='asistencias_registradas')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'materia', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.estudiante} - {self.fecha}: {self.estado}"


DIAS_CHOICES = [
    ('lunes', 'Lunes'),
    ('martes', 'Martes'),
    ('miercoles', 'Miércoles'),
    ('jueves', 'Jueves'),
    ('viernes', 'Viernes'),
]


class HorarioCurso(models.Model):
    curso = models.OneToOneField(Curso, on_delete=models.CASCADE, related_name='horario')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Horario de {self.curso}"


class PeriodoHorario(models.Model):
    horario = models.ForeignKey(HorarioCurso, on_delete=models.CASCADE, related_name='periodos')
    orden = models.PositiveIntegerField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ['orden']
        unique_together = ('horario', 'orden')

    def __str__(self):
        return f"P{self.orden} {self.hora_inicio}-{self.hora_fin}"


class ClaseHorario(models.Model):
    periodo = models.ForeignKey(PeriodoHorario, on_delete=models.CASCADE, related_name='clases')
    dia = models.CharField(max_length=10, choices=DIAS_CHOICES)
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True, blank=True, related_name='clases_horario')

    class Meta:
        unique_together = ('periodo', 'dia')

    def __str__(self):
        return f"{self.dia} P{self.periodo.orden}: {self.materia or 'libre'}"
