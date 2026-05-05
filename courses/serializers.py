from rest_framework import serializers
from .models import Materia, Inscripcion, Actividad, Calificacion, Asistencia, HorarioCurso, PeriodoHorario, ClaseHorario
from accounts.serializers import EstudianteSerializer, DocenteSerializer, CursoSerializer


class MateriaSerializer(serializers.ModelSerializer):
    curso = CursoSerializer(read_only=True)
    curso_id = serializers.IntegerField(write_only=True)
    docente = DocenteSerializer(read_only=True)
    docente_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Materia
        fields = ('id', 'nombre', 'codigo', 'curso', 'curso_id', 'docente', 'docente_id',
                  'descripcion', 'numero_horas', 'creditos', 'estado')


class InscripcionSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer(read_only=True)
    estudiante_id = serializers.IntegerField(write_only=True)
    curso = CursoSerializer(read_only=True)
    curso_id = serializers.IntegerField(write_only=True)
    registrada_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Inscripcion
        fields = ('id', 'estudiante', 'estudiante_id', 'curso', 'curso_id',
                  'fecha_inscripcion', 'estado', 'registrada_por')
        read_only_fields = ('id', 'fecha_inscripcion', 'registrada_por')



class ClaseHorarioSerializer(serializers.ModelSerializer):
    materia_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ClaseHorario
        fields = ('id', 'dia', 'materia', 'materia_nombre')

    def get_materia_nombre(self, obj):
        return obj.materia.nombre if obj.materia else None


class PeriodoHorarioSerializer(serializers.ModelSerializer):
    clases = ClaseHorarioSerializer(many=True, read_only=True)

    class Meta:
        model = PeriodoHorario
        fields = ('id', 'orden', 'hora_inicio', 'hora_fin', 'clases')


class HorarioCursoSerializer(serializers.ModelSerializer):
    periodos = PeriodoHorarioSerializer(many=True, read_only=True)

    class Meta:
        model = HorarioCurso
        fields = ('id', 'curso', 'periodos', 'updated_at')


class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ('id', 'materia', 'nombre', 'descripcion', 'tipo', 'trimestre',
                  'fecha', 'es_plantilla', 'creada_por', 'created_at')
        read_only_fields = ('id', 'created_at', 'creada_por')


class CalificacionSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    actividad_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Calificacion
        fields = ('id', 'estudiante', 'actividad', 'nota', 'fecha_modificacion',
                  'creada_por', 'estudiante_nombre', 'actividad_nombre')
        read_only_fields = ('id', 'fecha_modificacion', 'creada_por',
                            'estudiante_nombre', 'actividad_nombre')

    def get_estudiante_nombre(self, obj):
        return f"{obj.estudiante.user.first_name} {obj.estudiante.user.last_name}"

    def get_actividad_nombre(self, obj):
        return obj.actividad.nombre


class AsistenciaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Asistencia
        fields = ('id', 'estudiante', 'materia', 'fecha', 'estado', 'motivo',
                  'registrada_por', 'fecha_registro', 'estudiante_nombre')
        read_only_fields = ('id', 'fecha_registro', 'registrada_por', 'estudiante_nombre')

    def get_estudiante_nombre(self, obj):
        return f"{obj.estudiante.user.first_name} {obj.estudiante.user.last_name}"


class AsistenciaBulkItemSerializer(serializers.Serializer):
    estudiante = serializers.IntegerField()
    estado = serializers.ChoiceField(choices=['P', 'F', 'L'])
    motivo = serializers.CharField(required=False, allow_blank=True, default='')
