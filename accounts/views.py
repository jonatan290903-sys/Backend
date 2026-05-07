from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
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
    cache_key = f"mis_materias_{user.id}"
    data = cache.get(cache_key)
    
    if not data:
        if user.role == 'docente':
            try:
                docente = Docente.objects.get(user=user)
                materias = Materia.objects.filter(docente=docente, estado=True).select_related('curso', 'docente__user')
            except Docente.DoesNotExist:
                materias = Materia.objects.none()
        elif user.role == 'estudiante':
            try:
                estudiante = Estudiante.objects.get(user=user)
                if estudiante.curso:
                    materias = Materia.objects.filter(curso=estudiante.curso, estado=True).select_related('curso', 'docente__user')
                else:
                    materias = Materia.objects.none()
            except Estudiante.DoesNotExist:
                materias = Materia.objects.none()
        else:
            materias = Materia.objects.filter(estado=True).select_related('curso', 'docente__user')

        data = MateriaSerializer(materias[:300], many=True).data
        cache.set(cache_key, data, 60 * 15)  # Cache por 15 minutos

    return Response(data)


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
    print(f"DEBUG: Intento de login con datos: {request.data}")
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        print(f"DEBUG: Login exitoso para usuario: {user.email}")
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })
    print(f"DEBUG: Errores de validación en login: {serializer.errors}")
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
        user.must_change_password = False
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


def get_active_period(request):
    """Devuelve el periodo (nombre del año) activo: query param o el año marcado como activo."""
    periodo = request.query_params.get('periodo')
    if periodo:
        return periodo
    from accounts.models import AnioAcademico
    anio_activo = AnioAcademico.objects.filter(activo=True).first()
    return anio_activo.nombre if anio_activo else None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Devuelve las estadísticas del dashboard filtradas por el año académico activo."""
    from courses.models import Materia
    from payments.models import Pago

    periodo = get_active_period(request)
    cache_key = f'dashboard_stats_{periodo}'
    data = cache.get(cache_key)
    if data:
        return Response(data)

    if periodo:
        q_estudiantes = Estudiante.objects.filter(estado='activo', curso__periodo=periodo).count()
        q_materias = Materia.objects.filter(estado=True, curso__periodo=periodo).count()
        q_pagos = Pago.objects.filter(estudiante__curso__periodo=periodo).count()
        q_pendientes = Pago.objects.filter(estado__in=['pendiente', 'vencido'], estudiante__curso__periodo=periodo).count()
    else:
        q_estudiantes = Estudiante.objects.filter(estado='activo').count()
        q_materias = Materia.objects.filter(estado=True).count()
        q_pagos = Pago.objects.count()
        q_pendientes = Pago.objects.filter(estado__in=['pendiente', 'vencido']).count()

    data = {
        'estudiantes': q_estudiantes,
        'docentes': Docente.objects.filter(estado='activo').count(),
        'materias': q_materias,
        'pagos': q_pagos,
        'pagosPendientes': q_pendientes,
    }
    cache.set(cache_key, data, 600)
    return Response(data)


# ── Cursos (nivel académico) ──────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cursos_list(request):
    if request.method == 'GET':
        qs = Curso.objects.filter(estado=True).order_by('nivel', 'nombre')
        periodo = get_active_period(request)
        if periodo:
            qs = qs.filter(periodo=periodo)
        return Response(CursoSerializer(qs, many=True).data)
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
        estado = request.query_params.get('estado')
        curso_id = request.query_params.get('curso')
        page = request.query_params.get('page', 1)
        periodo = get_active_period(request)
        
        cache_key = f'estudiantes_list_{estado}_{curso_id}_{page}_{periodo}'
        data = cache.get(cache_key)
        if data:
            return Response(data)

        qs = Estudiante.objects.select_related('user', 'curso').all().order_by('user__last_name', 'user__first_name')
        if estado:
            qs = qs.filter(estado=estado)
        if curso_id:
            qs = qs.filter(curso_id=curso_id)
        if periodo:
            qs = qs.filter(curso__periodo=periodo)
        
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(qs, request)
        serializer = EstudianteSerializer(result_page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data
        cache.set(cache_key, response_data, 600)
        return Response(response_data)

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
        page = request.query_params.get('page', 1)
        cache_key = f'docentes_list_all_{page}'
        data = cache.get(cache_key)
        if data:
            return Response(data)

        qs = Docente.objects.select_related('user').filter(estado='activo').order_by('user__last_name', 'user__first_name')
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(qs, request)
        serializer = DocenteSerializer(result_page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data
        cache.set(cache_key, response_data, 600)
        return Response(response_data)

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


# ── Sistema y Configuración ────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_config(request):
    """Devuelve la configuración global (Año activo y trimestres)."""
    from accounts.models import AnioAcademico
    from accounts.serializers import AnioAcademicoSerializer
    from django.utils import timezone
    
    anio_activo = AnioAcademico.objects.filter(activo=True).first()
    if not anio_activo:
        return Response({'error': 'No hay un año académico activo.'}, status=status.HTTP_404_NOT_FOUND)
        
    data = AnioAcademicoSerializer(anio_activo).data
    
    hoy = timezone.now().date()
    trimestre_actual = 'T1'
    for trim in data.get('trimestres', []):
        if trim['fecha_inicio'] <= str(hoy) <= trim['fecha_fin']:
            trimestre_actual = trim['nombre']
            break
            
    data['trimestre_actual'] = trimestre_actual
    return Response(data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def anios_list(request):
    from accounts.models import AnioAcademico, ConfiguracionTrimestre
    from accounts.serializers import AnioAcademicoSerializer
    
    if request.method == 'GET':
        qs = AnioAcademico.objects.all()
        return Response(AnioAcademicoSerializer(qs, many=True).data)
        
    serializer = AnioAcademicoSerializer(data=request.data)
    if serializer.is_valid():
        anio = serializer.save()
        trimestres_data = request.data.get('trimestres', [])
        for t in trimestres_data:
            ConfiguracionTrimestre.objects.create(
                anio=anio,
                nombre=t.get('nombre'),
                fecha_inicio=t.get('fecha_inicio'),
                fecha_fin=t.get('fecha_fin')
            )
        return Response(AnioAcademicoSerializer(anio).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def anio_detail(request, pk):
    from accounts.models import AnioAcademico, ConfiguracionTrimestre
    from accounts.serializers import AnioAcademicoSerializer
    
    try:
        anio = AnioAcademico.objects.get(pk=pk)
    except AnioAcademico.DoesNotExist:
        return Response({'error': 'Año no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        return Response(AnioAcademicoSerializer(anio).data)
    elif request.method == 'PUT':
        serializer = AnioAcademicoSerializer(anio, data=request.data, partial=True)
        if serializer.is_valid():
            anio = serializer.save()
            trimestres_data = request.data.get('trimestres', [])
            if trimestres_data:
                ConfiguracionTrimestre.objects.filter(anio=anio).delete()
                for t in trimestres_data:
                    ConfiguracionTrimestre.objects.create(
                        anio=anio,
                        nombre=t.get('nombre'),
                        fecha_inicio=t.get('fecha_inicio'),
                        fecha_fin=t.get('fecha_fin')
                    )
            return Response(AnioAcademicoSerializer(anio).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        anio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
