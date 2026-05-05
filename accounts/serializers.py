from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Estudiante, Docente, Curso


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'role', 'phone', 'address', 'profile_image', 'created_at')
        read_only_fields = ('id', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return data


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'


class EstudianteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    curso = CursoSerializer(read_only=True)
    curso_id = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(), source='curso', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Estudiante
        fields = ('id', 'user', 'numero_expediente', 'documento', 'fecha_nacimiento', 'curso', 'curso_id', 'estado', 'created_at')
        read_only_fields = ('id', 'created_at')


class DocenteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Docente
        fields = ('id', 'user', 'documento', 'especialidad', 'titulo_profesional', 'fecha_contratacion', 'estado')
        read_only_fields = ('id',)
