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
    ViewSet encargado de manejar los movimientos financieros.

    Incluye:
    - CRUD básico (heredado de ModelViewSet)
    - Lógica personalizada para transferencias
    """

    # Optimización: evita consultas extra al traer relaciones
    queryset = Movement.objects.select_related(
        "account",                # JOIN con Account
        "destination_account",   # JOIN con Account destino
        "category"               # JOIN con Category
    )

    serializer_class = MovementSerializer

    def create(self, request, *args, **kwargs):
        """
        Método sobrescrito para controlar la creación de movimientos.

        Lógica:
        - Si hay destination_account → transferencia
        - Si no → movimiento normal
        """

        # Obtener datos del request
        data = request.data

        account_id = data.get("account")
        destination_id = data.get("destination_account")
        category_id = data.get("category")
        amount = data.get("amount")
        movement_date = data.get("movement_date")
        description = data.get("description", "")

        # VALIDACIÓN: campos obligatorios
        if not account_id or not amount or not movement_date:
            return Response(
                {"error": "Faltan campos obligatorios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # VALIDACIÓN: monto numérico
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return Response(
                {"error": "Monto inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # CASO 1: TRANSFERENCIA
        if destination_id:

            # Transacción: asegura que ambos movimientos se guarden o ninguno
            with transaction.atomic():

                # Movimiento de salida (siempre negativo)
                out_movement = Movement.objects.create(
                    account_id=account_id,
                    destination_account_id=destination_id,
                    category_id=category_id,
                    amount=-abs(amount),  # fuerza valor negativo
                    description=description or "Transferencia enviada",
                    movement_date=movement_date,
                )

                # Movimiento de entrada (siempre positivo)
                in_movement = Movement.objects.create(
                    account_id=destination_id,
                    destination_account_id=account_id,
                    category_id=category_id,
                    amount=abs(amount),  # fuerza valor positivo
                    description="Transferencia recibida",
                    movement_date=movement_date,
                )

            # Respuesta clara para frontend
            return Response(
                {
                    "message": "Transferencia realizada correctamente",
                    "salida": MovementSerializer(out_movement).data,
                    "entrada": MovementSerializer(in_movement).data,
                },
                status=status.HTTP_201_CREATED
            )

        # CASO 2: MOVIMIENTO NORMAL
        return super().create(request, *args, **kwargs)