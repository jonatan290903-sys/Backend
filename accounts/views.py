from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Curso, Estudiante, Docente
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, CursoSerializer, EstudianteSerializer, DocenteSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_materias(request):
    """Materias del usuario según su rol."""
    from courses.serializers import MateriaSerializer
    from courses.models import Materia

    user = request.user
    if user.role == 'docente':
        try:
            docente = Docente.objects.get(user=user)
            materias = Materia.objects.filter(docente=docente, estado=True)
        except Docente.DoesNotExist:
            materias = Materia.objects.none()
    elif user.role == 'estudiante':
        try:
            estudiante = Estudiante.objects.get(user=user)
            if estudiante.curso:
                materias = Materia.objects.filter(curso=estudiante.curso, estado=True)
            else:
                materias = Materia.objects.none()
        except Estudiante.DoesNotExist:
            materias = Materia.objects.none()
    else:
        materias = Materia.objects.filter(estado=True)

    return Response(MateriaSerializer(materias, many=True).data)


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'Usuario registrado exitosamente.', 'user_id': user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh = RefreshToken(request.data.get('refresh'))
        return Response({'access': str(refresh.access_token)})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Contraseña incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Contraseña actualizada exitosamente.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh = RefreshToken(request.data.get('refresh'))
        refresh.blacklist()
        return Response({'message': 'Sesión cerrada exitosamente.'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ── Cursos (nivel académico) ──────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cursos_list(request):
    if request.method == 'GET':
        return Response(CursoSerializer(Curso.objects.filter(estado=True), many=True).data)
    serializer = CursoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def curso_detail(request, pk):
    try:
        curso = Curso.objects.get(pk=pk)
    except Curso.DoesNotExist:
        return Response({'error': 'Curso no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(CursoSerializer(curso).data)
    if request.method == 'PUT':
        serializer = CursoSerializer(curso, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    curso.estado = False
    curso.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Estudiantes ───────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def estudiantes_list(request):
    if request.method == 'GET':
        qs = Estudiante.objects.select_related('user', 'curso').all()
        estado = request.query_params.get('estado')
        curso_id = request.query_params.get('curso')
        if estado:
            qs = qs.filter(estado=estado)
        if curso_id:
            qs = qs.filter(curso_id=curso_id)
        return Response(EstudianteSerializer(qs, many=True).data)
    serializer = EstudianteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def estudiante_detail(request, pk):
    try:
        estudiante = Estudiante.objects.select_related('user', 'curso').get(pk=pk)
    except Estudiante.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(EstudianteSerializer(estudiante).data)
    if request.method == 'PUT':
        serializer = EstudianteSerializer(estudiante, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    estudiante.estado = 'inactivo'
    estudiante.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Docentes ──────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def docentes_list(request):
    if request.method == 'GET':
        qs = Docente.objects.select_related('user').filter(estado='activo')
        return Response(DocenteSerializer(qs, many=True).data)
    serializer = DocenteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def docente_detail(request, pk):
    try:
        docente = Docente.objects.select_related('user').get(pk=pk)
    except Docente.DoesNotExist:
        return Response({'error': 'Docente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(DocenteSerializer(docente).data)
    if request.method == 'PUT':
        serializer = DocenteSerializer(docente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    docente.estado = 'inactivo'
    docente.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
