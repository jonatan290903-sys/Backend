from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Comunicado, Notificacion
from .serializers import ComunicadoSerializer, NotificacionSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comunicados_list(request):
    if request.method == 'GET':
        comunicados = Comunicado.objects.filter(activo=True)
        serializer = ComunicadoSerializer(comunicados, many=True)
        return Response(serializer.data)

    if request.user.role not in ['administrativo', 'directivo']:
        return Response({'error': 'No tiene permiso para crear comunicados.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ComunicadoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(autor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notificaciones_list(request):
    if request.method == 'GET':
        notificaciones = Notificacion.objects.filter(usuario=request.user)
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)

    # POST to mark all as read
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    return Response({'message': 'Notificaciones marcadas como leídas.'})
