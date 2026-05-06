from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from .models import Pago
from .serializers import PagoSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pagos_list(request):
    if request.method == 'GET':
        qs = Pago.objects.select_related('estudiante__user', 'estudiante__curso').all().order_by('-fecha_vencimiento')
        estudiante_id = request.query_params.get('estudiante')
        estado = request.query_params.get('estado')
        concepto = request.query_params.get('concepto')
        if estudiante_id:
            qs = qs.filter(estudiante_id=estudiante_id)
        if estado:
            qs = qs.filter(estado=estado)
        if concepto:
            qs = qs.filter(concepto=concepto)
            
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(qs, request)
        serializer = PagoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    serializer = PagoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def pago_detail(request, pk):
    try:
        pago = Pago.objects.get(pk=pk)
    except Pago.DoesNotExist:
        return Response({'error': 'Pago no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(PagoSerializer(pago).data)
    if request.method == 'PUT':
        serializer = PagoSerializer(pago, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    pago.estado = 'cancelado'
    pago.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen_pagos(request):
    cache_key = 'payments_summary'
    data = cache.get(cache_key)
    if not data:
        from django.db.models import Sum, Count
        total = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0
        por_estado = Pago.objects.values('estado').annotate(cantidad=Count('id'), monto_total=Sum('monto'))
        data = {
            'total_monto': float(total),
            'por_estado': list(por_estado)
        }
        cache.set(cache_key, data, 600)  # Cache for 10 minutes
    return Response(data)
