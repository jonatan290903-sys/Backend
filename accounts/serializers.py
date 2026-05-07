from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Estudiante, Docente, Curso


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'role', 'phone', 'address', 'profile_image', 'must_change_password', 'created_at')
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
    # Definimos los campos como opcionales en el esquema para permitir flexibilidad
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    identifier = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Obtener el identificador de cualquiera de las posibles llaves
        login_id = data.get('email') or data.get('username') or data.get('identifier')
        
        if not login_id:
            raise serializers.ValidationError("Debe proporcionar un email o nombre de usuario.")

        user = authenticate(username=login_id, password=data['password'])
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
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Estudiante
        fields = ('id', 'user', 'numero_expediente', 'documento', 'fecha_nacimiento', 'curso', 'curso_id', 'estado', 'created_at', 'first_name', 'last_name', 'email')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        documento = validated_data.get('documento', '')
        email = validated_data.pop('email', '')
        if not email:
            email = f"estudiante_{documento}@sistemage.local"
            
        user = User.objects.create(
            username=documento,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='estudiante',
            must_change_password=True
        )
        user.set_password(documento)
        user.save()

        estudiante = Estudiante.objects.create(user=user, **validated_data)
        return estudiante

    def update(self, instance, validated_data):
        user_updated = False
        if 'first_name' in validated_data:
            instance.user.first_name = validated_data.pop('first_name')
            user_updated = True
        if 'last_name' in validated_data:
            instance.user.last_name = validated_data.pop('last_name')
            user_updated = True
        if 'email' in validated_data:
            instance.user.email = validated_data.pop('email')
            user_updated = True
            
        if user_updated:
            instance.user.save()

        return super().update(instance, validated_data)


class DocenteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Docente
        fields = ('id', 'user', 'documento', 'especialidad', 'titulo_profesional', 'fecha_contratacion', 'estado', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        documento = validated_data.get('documento', '')
        email = validated_data.pop('email', '')
        if not email:
            email = f"docente_{documento}@sistemage.local"
            
        user = User.objects.create(
            username=documento,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='docente',
            must_change_password=True
        )
        user.set_password(documento)
        user.save()

        docente = Docente.objects.create(user=user, **validated_data)
        return docente

    def update(self, instance, validated_data):
        user_updated = False
        if 'first_name' in validated_data:
            instance.user.first_name = validated_data.pop('first_name')
            user_updated = True
        if 'last_name' in validated_data:
            instance.user.last_name = validated_data.pop('last_name')
            user_updated = True
        if 'email' in validated_data:
            instance.user.email = validated_data.pop('email')
            user_updated = True
            
        if user_updated:
            instance.user.save()

        return super().update(instance, validated_data)


class ConfiguracionTrimestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = __import__('accounts.models', fromlist=['ConfiguracionTrimestre']).ConfiguracionTrimestre
        fields = '__all__'


class AnioAcademicoSerializer(serializers.ModelSerializer):
    trimestres = ConfiguracionTrimestreSerializer(many=True, read_only=True)
    
    class Meta:
        model = __import__('accounts.models', fromlist=['AnioAcademico']).AnioAcademico
        fields = '__all__'
