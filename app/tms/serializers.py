from django.db import transaction
from django.core.files import File
from rest_framework import serializers

from .models import Terminal, Group, TerminalShipment, TerminalShipmentFiles, TerminalLog, TerminalStatusUpdateFiles

from dukka_connection.models import AccountsCustomuser
from dukka_connection.serializers import ListMerchantSerializer
from user.serializers import BasicUserSerializer
from .enums import TERMINAL_LOG_TYPE


# class TerminalComponentSingleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Component
#         fields = '__all__'
#         read_only_fields = ['terminal']

        
# class TerminalComponentBulkSerializer(serializers.Serializer):
#     data = serializers.ListSerializer(child=TerminalComponentSingleSerializer(), required=True)

class TerminalGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group 
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'read_only': True},
            'no_of_terminals': {'read_only': True},
        }

    def validate(self, attrs):
        name = attrs.get('name')
        if Group.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {'name': 'Group with this name already exists'}
            )
        return super().validate(attrs) 

    # def to_representation(self, instance: Group):
    #         data = super().to_representation(instance)
    #         data['terminal'] = TerminalListSerializer(instance.terminal_group).data if instance.terminal_group.id else None
    #         return data

    def create(self, validated_data):
        group = Group.objects.create(**validated_data, )
        return group


class TerminalSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(required=False)
    group = serializers.PrimaryKeyRelatedField(required=False, queryset=Group.objects.all())
    shipment_batch = serializers.PrimaryKeyRelatedField(required=False, queryset=TerminalShipment.objects.all())


    class Meta:
        model = Terminal
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'read_only': True},
            'status': {'read_only': True},
            'device_tag_no': {'read_only': True},
            'group': {'read_only': True},
        }

    def validate(self, attrs):
        serial_no = attrs.get('serial_no')
        creator = self.context['request'].user
        if Terminal.objects.filter(serial_no=serial_no).exists():
            raise serializers.ValidationError(
                {'serial_no': 'Terminal with this serial_no already exists'}
            ) 
        if creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN', 'TMS_ADMIN']:
            raise serializers.ValidationError(
                {'Terminal': 'you are not authorized to create a Terminal'}
            )
        return super().validate(attrs) 

    def to_representation(self, instance):
            data = super().to_representation(instance)
            data['group'] = TerminalGroupSerializer(instance.group).data
            return data

    def create(self, validated_data):
        group_name = validated_data.pop('group_name', None)
        group = validated_data.get('group', None)       
        if group_name:
            group_ref = Group.objects.create(name=group_name)
            validated_data.update({'group': group_ref})
        terminal = Terminal.objects.create(**validated_data, )
        return terminal


class TerminalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'


class TerminalDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Terminal
        fields = '__all__'
    
    def to_representation(self, instance: Terminal):
        merchant_ref = AccountsCustomuser.objects.using('dukka_db').all().filter(id=instance.merchant_ref).first()
        data = super().to_representation(instance)
        data['merchant_ref'] = ListMerchantSerializer(merchant_ref).data
        data['group'] = TerminalGroupSerializer(instance.group).data if instance.group else None
        return data


class TerminalPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Terminal
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'read_only': True},
            'status': {'read_only': True},
            'device_tag_no': {'read_only': True},
            'group': {'read_only': True},
            'merchant_ref': {'read_only': True},
        }


# class TerminalUpdateSerializer(serializers.Serializer):
#     name= serializers.CharField()
#     serial_no= serializers.CharField()
#     IMEI= serializers.CharField()
#     model_no= serializers.CharField()
#     os_version= serializers.CharField()
#     app_version= serializers.CharField()
#     shipment_batch= serializers.CharField()
#     terminal_battery= serializers.CharField()
#     terminal_charger = serializers.CharField()
#     terminal_manual= serializers.CharField()
#     terminal_pin= serializers.CharField()

#     def update(self, instance, validated_data):
#         instance.name = self.validated_data['name']
#         instance.serial_no = self.validated_data['serial_no']
#         instance.IMEI = self.validated_data['IMEI']
#         instance.model_no = self.validated_data['model_no']
#         instance.app_version = self.validated_data['app_version']
#         instance.shipment_batch = self.validated_data['shipment_batch']
#         instance.terminal_battery = self.validated_data['terminal_battery']
#         instance.terminal_charger = self.validated_data['terminal_charger']
#         instance.terminal_manual = self.validated_data['terminal_manual']
#         instance.terminal_pin = self.validated_data['terminal_pin']
#         instance.save()
#         return instance


class UploadTerminalSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, file: File):
        if not file.name.endswith(".csv"):
            raise serializers.ValidationError("Invalid file, file must be csv.")
        return file


class AssignTerminalSerializer(serializers.Serializer):
    merchant = serializers.PrimaryKeyRelatedField(queryset=AccountsCustomuser.objects.using('dukka_db'), required=True)
    terminal = serializers.PrimaryKeyRelatedField(queryset=Terminal.objects.all(), required=True)

    def validate(self, attrs):
        terminal: Terminal = attrs['terminal']
        if terminal.merchant_ref:
            raise serializers.ValidationError({'terminal': 'Terminal already assigned to a merchant'})
        return attrs
    
    def to_representation(self, instance):
        return TerminalListSerializer(instance).data
    
    @transaction.atomic()
    def create(self, validated_data):
        terminal: Terminal = validated_data['terminal']
        merchant = validated_data['merchant'].id
        terminal.status = 'ASSIGNED'
        terminal.merchant_ref = merchant
        terminal.save(update_fields=['status', 'merchant_ref'])
        data = {
            'terminal': terminal,
            'merchant_ref': validated_data['merchant'].id,
            'actor': self.context['actor'],
            'type': 'ASSIGNED',
        }
        TerminalLog.objects.create(**data)
        return terminal

    
class UnAssignTerminalSerializer(serializers.Serializer):
    terminal = serializers.PrimaryKeyRelatedField(queryset=Terminal.objects.all(), required=True)

    def validate(self, attrs):
        terminal: Terminal = attrs['terminal']
        if not terminal.merchant_ref:
            raise serializers.ValidationError({'terminal': 'Only assigned terminals can be unassigned'})
        return attrs

    def to_representation(self, instance):
        return TerminalListSerializer(instance).data

    @transaction.atomic()
    def create(self, validated_data):
        terminal: Terminal = validated_data['terminal']
        assigned_merchant = terminal.merchant_ref
        terminal.status = 'UNASSIGNED'
        terminal.merchant_ref = None
        terminal.save(update_fields=['status', 'merchant_ref'])
        data = {
            'terminal': terminal,
            'merchant_ref': assigned_merchant,
            'actor': self.context['actor'],
            'type': 'UNASSIGNED',
        }
        TerminalLog.objects.create(**data)
        return terminal


class TerminalStatusUpdateFilesSerializer(serializers.ModelSerializer):
    extra_kwargs = {
            'terminal_log': {'read_only': True},
    }
    class Meta:
        model = TerminalStatusUpdateFiles
        fields = "__all__"


class TerminalLogSerializer(serializers.ModelSerializer):
    files = TerminalStatusUpdateFilesSerializer(many=True, required=False)

    class Meta:
        model = TerminalLog
        fields = '__all__'
        read_only_fields = ['terminal']

    def to_representation(self, instance: TerminalLog):
        data = super().to_representation(instance)
        data['actor'] = BasicUserSerializer(instance.actor).data
        data['terminal'] = TerminalListSerializer(instance.terminal).data
        return data


class TerminalShipmentFilesSerializer(serializers.ModelSerializer):
    extra_kwargs = {
            'terminal_shipment': {'read_only': True},
    }
    class Meta:
        model = TerminalShipmentFiles
        fields = "__all__"


class TerminalShipmentSerializer(serializers.ModelSerializer):
    files = TerminalShipmentFilesSerializer(many=True, required=False)
    read_only_fields = ['shipment_id']

    class Meta:
        model = TerminalShipment
        fields = "__all__"


    def validate(self, attrs):
        shipment_code_name = attrs.get('shipment_code_name')
        creator = self.context['request'].user
        if TerminalShipment.objects.filter(shipment_code_name=shipment_code_name).exists():
            raise serializers.ValidationError(
                {'shipment_code_name': 'Terminal shipment with this code already exists'}
            ) 
        if creator.role not in ['SUPER_ADMIN', 'HYBRID_ADMIN', 'TMS_ADMIN']:
            raise serializers.ValidationError(
                {'Terminal': 'you are not authorized to create a Terminal'}
            )
        return super().validate(attrs)

    @transaction.atomic()
    def create(self, validated_data):
        print(validated_data)
        files = validated_data.get("files")
        terminal_shipment = TerminalShipment.objects.create(**validated_data)
        if files:
            for file_data in files:
                TerminalShipmentFiles.objects.create(terminal_shipment=terminal_shipment, **file_data)
        return terminal_shipment

   
class TerminalShipmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TerminalShipment
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'read_only': True},
            'shipment_id': {'read_only': True}
        }


class TerminalUpdateStatusSerializer(serializers.Serializer):
    status_chioces = [
        ('FAULTY', 'FAULTY'),
        ("FIXED", "FIXED"),
        ('DEPRECATED', 'DEPRECATED'),
        ('ARCHIVE', 'ARCHIVE'),
        ('UNARCHIVE', 'UNARCHIVE'),
    ]

    status = serializers.ChoiceField(choices=status_chioces, write_only=True)
    actor = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = serializers.CharField(style={'base_template': 'textarea.html'}, required=False)
    type = serializers.ChoiceField(choices=status_chioces, read_only=True)
    merchant_ref = serializers.PrimaryKeyRelatedField(read_only=True)
    files = TerminalStatusUpdateFilesSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TerminalLog

    def validate(self, data):
        terminal: Terminal = self.context['terminal']

        if data["status"] == "FIXED" and terminal.status != "FAULTY":
            raise serializers.ValidationError({"status": "Only faulty terminals can be marked as fixed."})

        if data["status"] == "UNARCHIVE" and terminal.status != "ARCHIVE":
            raise serializers.ValidationError({"status": "Only archived terminals can be unarchived."})
        return super().validate(data)

    @transaction.atomic()
    def create(self, validated_data):
        files = validated_data.get("files")
        terminal: Terminal = self.context['terminal']
        terminal.status = validated_data["status"]
        terminal.save()

        data = {
            'terminal': terminal,
            'actor': self.context['actor'],
            'type': validated_data["status"],
            "merchant_ref": terminal.merchant_ref,
            "notes": validated_data.get("notes")
        }
        log = TerminalLog.objects.create(**data)

        if files:
            for file_data in files:
                TerminalStatusUpdateFiles.objects.create(terminal_log=log, **file_data)
        return log
