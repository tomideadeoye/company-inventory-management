from drf_spectacular.utils import extend_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from user.permissions import (
        IsAmsAdmin, 
        IsSuperAdmin, 
        IsHybridAdmin, 
        IsTmsAdmin)
from .models import WorkSpace

from .serializers import (
    WorkSpaceSerializer,
    UpdateWorkSpaceStatusSerializer,
    WorkSpaceUpdateSerializer,
    WorkSpaceDetailSerializer,
    ListWorkSpaceSerializer,
    )


class WorkSpaceViewSets(viewsets.ModelViewSet):
    queryset = WorkSpace.objects.all().prefetch_related('user_workspace')
    serializer_class = WorkSpaceSerializer
    http_method_names = ["get", "post", "patch", "put"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", 'country', 'status', 'state_or_province', 'street']
    ordering_fields = [ "name" ]
    permission_classes = [IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin]


    def get_serializer_class(self):
        if self.action == "update":
            return WorkSpaceUpdateSerializer
        elif self.action == "list":
            return ListWorkSpaceSerializer
        elif self.action =="retrieve":
            return WorkSpaceDetailSerializer    
        return super().get_serializer_class()
        

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsSuperAdmin | IsHybridAdmin | IsTmsAdmin | IsAmsAdmin],
        serializer_class=UpdateWorkSpaceStatusSerializer,
        url_path="update-status",
    )
    def update_workspace_status(self, request, pk=None):
        workspace = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=workspace,
                                        partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, 'message': 'status updated successfully'}, status=status.HTTP_200_OK)


    # @action(
    #     methods=["POST"],
    #     detail=True,
    #     permission_classes=[IsSuperAdmin],
    #     serializer_class=UpdateWorkSpaceStatusSerializer,
    #     url_path="update-status",
    # )
    # def update_workspace(self, request, pk=None):
    #     workspace = self.get_object()
    #     serializer = self.get_serializer(data=request.data, instance=workspace,
    #                                      context={'SUPER_ADMIN': self.request.user})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         {"success": True, 'message': 'status updated successfully'},
    #         status=status.HTTP_200_OK)        