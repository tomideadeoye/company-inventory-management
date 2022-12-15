
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import AccountsCustomuser

from user.permissions import IsAmsAdmin, IsSuperAdmin, IsHybridAdmin, IsTmsAdmin
from .serializers import ListMerchantSerializer
from tms.models import Terminal #TerminalLog
from tms.serializers import TerminalListSerializer #TerminalLogSerializer



class MerchantViewSets(viewsets.ModelViewSet):
    queryset = AccountsCustomuser.objects.using('dukka_db').all().order_by('-created_at').prefetch_related(
            'business_account', 'business_account__business_type')
    serializer_class = ListMerchantSerializer
    http_method_names = ["get"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'id', 'business_account__name']

    permission_classes = [IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin]

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
            methods=["GET"],
            detail=True,
            permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
            serializer_class=TerminalListSerializer,
            url_path="terminals",
        )
    def get_merchant_terminals(self, request, pk=None):
        merchant = self.get_object()
        terminals = Terminal.objects.filter(merchant_ref=merchant.id)
        serializer = self.serializer_class(terminals, many=True)
        return Response(
            {"success": True, 'message': serializer.data},
            status=status.HTTP_200_OK)  
    
    # @action(
    #         methods=["GET"],
    #         detail=True,
    #         permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
    #         serializer_class=TerminalLogSerializer,
    #         url_path="terminal-logs",
    #     )
    # def get_merchant_terminal_logs(self, request, pk=None):
    #     merchant = self.get_object()
    #     terminals = TerminalLog.objects.filter(merchant_ref=merchant.id)
    #     return self.paginate_results(terminals)
       