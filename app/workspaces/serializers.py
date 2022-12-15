from django.conf import settings
from rest_framework import serializers

from .models import WorkSpace
from user.serializers import BasicUserSerializer


class WorkSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkSpace
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'read_only': True},
            'status': {'read_only': True},
        }

    def validate(self, attrs):
        name = attrs.get('name')
        creator = self.context['request'].user
        if WorkSpace.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {'name': 'Workspace with this name already exists'}
            ) 
        if creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN', 'TMS_ADMIN']:
            raise serializers.ValidationError(
                {'workspace': 'you are not authorized to create a workspace'}
            )
        return super().validate(attrs) 

    def create(self, validated_data):
        workspace = WorkSpace.objects.create(**validated_data, )
        return workspace


class WorkSpaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        fields = '__all__'
    
    def to_representation(self, instance: WorkSpace):
        data = super().to_representation(instance)
        data['user'] = BasicUserSerializer(instance.user_workspace.all(), many=True).data
        return data

class ListWorkSpaceSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkSpace
        fields = '__all__'

    @staticmethod
    def get_user_count(obj: WorkSpace) -> int:
        return obj.user_workspace.count()   


class WorkSpaceUpdateSerializer(serializers.Serializer):
    name= serializers.CharField()
    country= serializers.CharField()
    state_or_province= serializers.CharField()
    street= serializers.CharField()
    description= serializers.CharField()


    def update(self, instance, validated_data):
        instance.name = self.validated_data['name']
        instance.country = self.validated_data['country']
        instance.state_or_province = self.validated_data['state_or_province']
        instance.street = self.validated_data['street']
        instance.description = self.validated_data['description']
        instance.save()
        return instance


class UpdateWorkSpaceStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(('ACTIVATE', 'ACTIVATE'),
                                              ('ARCHIVE', 'ARCHIVE')))

    def validate(self, attrs):
        workspace = self.instance
        status = attrs['status']
        

        if status == 'ACTIVATE' and workspace.status != 'ARCHIVE':
            raise serializers.ValidationError(
                {'status': 'can only activate an archived workspace'})
        elif status == 'ARCHIVE' and workspace.status != 'ACTIVE':
            raise serializers.ValidationError(
                {'status': 'can only archive an active workspace'})

        return attrs

    def update(self, instance, validated_data):
        status = 'ACTIVE' if self.validated_data['status'] == 'ACTIVATE' else 'ARCHIVE'
        instance.status = status
        instance.save()
        return instance
  