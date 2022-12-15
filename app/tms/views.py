import pandas as pd

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from user.permissions import (
        IsAmsAdmin, 
        IsSuperAdmin, 
        IsHybridAdmin, 
        IsTmsAdmin)

from .models import Terminal, TerminalShipment, TerminalLog, Group

from .serializers import (
        TerminalSerializer, 
        TerminalDetailSerializer,
        AssignTerminalSerializer, 
        TerminalLogSerializer,
        UnAssignTerminalSerializer,
        UploadTerminalSerializer,
        TerminalShipmentSerializer,
        # TerminalUpdateSerializer,
        TerminalGroupSerializer,
        TerminalPatchSerializer,
        TerminalUpdateStatusSerializer,
        TerminalShipmentUpdateSerializer
        #TerminalComponentBulkSerializer,
        #TerminalComponentSingleSerializer
        )


class TerminalViewSets(viewsets.ModelViewSet):
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer
    http_method_names = ["get", "post", "put", "patch"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["serial_no", '=status', 'IMEI', 'id']
    ordering_fields = ["created_at", "name", ]
    permission_classes = [IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin]

 
    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TerminalDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return TerminalPatchSerializer   
        return super().get_serializer_class()


    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        serializer_class=AssignTerminalSerializer,
        url_path="assign",
    )
    def assign_terminal(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, context={"actor": request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, 'message': 'Terminal  assigned  successfully'},
            status=status.HTTP_200_OK)     
    
    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        serializer_class=UnAssignTerminalSerializer,
        url_path="unassign",
    )
    def unassign_terminal(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, context={"actor": request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, 'message': 'Terminal  unassigned  successfully'},
            status=status.HTTP_200_OK) 
    
    @action(
        methods=["GET"],
        detail=True,
        permission_classes=[IsAuthenticated],
        serializer_class=TerminalLogSerializer,
        url_path="logs",
    )
    def terminal_logs(self, request, pk=None):
        terminal = self.get_object()
        queryset = TerminalLog.objects.filter(terminal=terminal).select_related('actor', 'terminal')
        return self.paginate_results(queryset)
    
    @action(
        methods=["POST"],
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        detail=False,
        serializer_class=UploadTerminalSerializer,
        url_path="bulk-create",
    )
    def bulk_create_terminals(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = request.data["file"]
            reader = pd.read_csv(file)

            terminal_data = []
            for _, row in reader.iterrows():
                data = {}
                data.update({"name": row.get('name')})
                data.update({"serial_no": str(row.get("serial_no"))})
                data.update({"IMEI": str(row.get("IMEI"))})
                data.update({"model_no": str(row.get("model_no"))})
                data.update({"os_version": str(row.get("os_version"))})
                data.update({"app_version": str(row.get("app_version"))})
                data.update({"shipment_batch": row.get("shipment_batch")})
                data.update({"terminal_battery": row.get("terminal_battery")})
                data.update({"terminal_charger": row.get("terminal_charger")})
                data.update({"terminal_manual": row.get("terminal_manual")})
                data.update({"terminal_pin": row.get("terminal_pin")})
                terminal_data.append(data)

            terminal_serializer = TerminalSerializer(data=terminal_data, many=True, context={'request': request})
            if terminal_serializer.is_valid(raise_exception=False):
                terminal_serializer.save()
                return Response(
                    {"success": True, "data": terminal_serializer.data},
                    status=status.HTTP_200_OK,
                )
            errors = [error for error in terminal_serializer.errors]
            return Response(
                {"success": False, "errors": errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["POST"],
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        detail=True,
        serializer_class=TerminalUpdateStatusSerializer,
        url_path="update-status",
    )
    def update_status(self, request, pk=None):
        terminal = self.get_object()
        serializer = self.serializer_class(data=request.data, context={"actor": request.user, "terminal": terminal})
        serializer.is_valid(raise_exception=True)
        serializer = serializer.save()
        serializer = self.serializer_class(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TerminalGroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all().prefetch_related('terminal_group')
    serializer_class = TerminalGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "location"]
    permission_classes = [IsSuperAdmin | IsHybridAdmin | IsTmsAdmin]
    http_method_names = ["get", "post", "put", "patch"]
    ordering_fields = ["name"]


class TerminalShipmentViewset(viewsets.ModelViewSet):
    queryset = TerminalShipment.objects.all()
    serializer_class = TerminalShipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["shipment_code_name", "shipment_id"]
    permission_classes = [IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin]
    http_method_names = ["get", "post", "put", "patch"]
    ordering_fields = ["shipment_code_name"]
    

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TerminalShipmentUpdateSerializer   
        return super().get_serializer_class()
    # @action(
    #     methods=["POST"],
    #     detail=True,
    #     permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
    #     serializer_class=TerminalComponentBulkSerializer,
    #     url_path="create-components",
    # )
    # def create_terminal_components(self, request, pk=None):
    #     terminal = self.get_object()
    #     serializer = TerminalComponentSingleSerializer(data=request.data['data'], many=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(terminal=terminal)
    #     return Response(
    #         {"success": True, 'data': serializer.data},
    #         status=status.HTTP_200_OK) 
