from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters import rest_framework as df_filters

from core.fields import MultipleFilter, DateRangeFilter


class UserFilter(df_filters.FilterSet):
    status: str = MultipleFilter(method="filter_status")
    role = MultipleFilter(field_name="role")
    search = df_filters.CharFilter(method='filter_search')

    class Meta:
        model = get_user_model()
        fields = ['is_active', 'role']

    @staticmethod
    def filter_status(queryset, name, value):
        if value:
            if value == ['ACTIVE']:
                return queryset.filter(is_active=True, verified=True)
            elif value == ['PENDING']:
                return queryset.filter(is_active=False, verified=False)
            elif value == ['ARCHIVED']:
                return queryset.filter(is_active=False, verified=True)
            elif value == ['ACTIVE', 'ARCHIVED']:
                return queryset.filter(Q(is_active=True, verified=True) | Q(is_active=False, verified=True))
            elif value == ['ACTIVE', 'PENDING']:
                return queryset.filter(Q(is_active=True, verified=True) | Q(is_active=False, verified=False))
            elif value == ['PENDING', 'ARCHIVED']:
                return queryset.filter(Q(is_active=False, verified=False) | Q(is_active=False, verified=True))
            else:
                return queryset.none()
        return queryset

    @staticmethod
    def filter_search(queryset, name, value):
        if value:
            return queryset.filter(
                Q(fullname__icontains=value))
                # Q(fullname__icontains=value) | Q(lastname__icontains=value))

        return queryset
