from rest_framework import viewsets, status
from .models import User, Account, Category, Movement, Service
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer





from rest_framework.response import Response
from django.db import transaction  #para asegurar consistencia en BD


class MovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar movimientos financieros.

    Incluye:
    - Creación de ingresos/gastos normales
    - Manejo de transferencias (crea 2 movimientos automáticamente)
    """

    queryset = Movement.objects.select_related(
        "account",
        "destination_account",
        "category"
    )  #Optimiza consultas JOIN
    serializer_class = MovementSerializer

    def create(self, request, *args, **kwargs):
        """
        Sobrescribimos create para manejar lógica de negocio:
        - Si hay destination_account → es transferencia
        - Si no → es movimiento normal
        """

        data = request.data

        account_id = data.get("account")
        destination_id = data.get("destination_account")
        category_id = data.get("category")
        amount = data.get("amount")
        movement_date = data.get("movement_date")
        description = data.get("description", "")

        # VALIDACIONES BÁSICAS
        if not account_id or not amount or not movement_date:
            return Response(
                {"error": "Faltan campos obligatorios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {"error": "Monto inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # CASO 1: TRANSFERENCIA
        if destination_id:

            # Usamos transacción para evitar inconsistencias
            with transaction.atomic():

                # Movimiento de salida (negativo)
                out_movement = Movement.objects.create(
                    account_id=account_id,
                    destination_account_id=destination_id,
                    category_id=category_id,
                    amount=-abs(amount),  # siempre negativo
                    description=description or "Transferencia enviada",
                    movement_date=movement_date,
                )

                # Movimiento de entrada (positivo)
                in_movement = Movement.objects.create(
                    account_id=destination_id,
                    destination_account_id=account_id,
                    category_id=category_id,
                    amount=abs(amount),  # siempre positivo
                    description="Transferencia recibida",
                    movement_date=movement_date,
                )

            return Response(
                {
                    "message": "Transferencia creada correctamente",
                    "out_movement": MovementSerializer(out_movement).data,
                    "in_movement": MovementSerializer(in_movement).data,
                },
                status=status.HTTP_201_CREATED
            )

        # CASO 2: MOVIMIENTO NORMAL (ingreso o gasto)
        return super().create(request, *args, **kwargs)