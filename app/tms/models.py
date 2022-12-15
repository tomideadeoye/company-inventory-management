from django.db import models
from django.core.validators import FileExtensionValidator

from core.models import AuditableModel
from .enums import TERMINAL_STATUS, TERMINAL_LOG_TYPE



class Group(AuditableModel):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    no_of_terminals = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


    class Meta:
            ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        terminal_count = Group.objects.count()
        self.no_of_terminals = terminal_count+1
        return super().save(*args, **kwargs)

# class Component(AuditableModel):
#     name = models.CharField(max_length=200)
#     terminal = models.ForeignKey(
#         'tms.Terminal', on_delete=models.CASCADE,
#         related_name='terminal_component', null=True, blank=True)
#     description = models.TextField()

#     class Meta:
#             ordering = ('name',)

    # def __str__(self):
    #     return self.name
    

class Terminal(AuditableModel):
    name = models.CharField(max_length=200)
    serial_no = models.CharField(max_length=200)
    IMEI = models.CharField(max_length=200)
    model_no = models.CharField(max_length=200)
    os_version = models.CharField(max_length=200)
    app_version = models.CharField(max_length=200)
    device_tag_no = models.CharField(max_length=200, null=True)
    shipment_batch = models.ForeignKey(
        'tms.TerminalShipment', on_delete=models.SET_NULL, null=True, related_name='terminal_batch')
    # shipment_batch = models.CharField(max_length=200)
    merchant_ref = models.UUIDField(null=True, blank=True)
    group = models.ForeignKey(
        'tms.Group', on_delete=models.SET_NULL,
        related_name='terminal_group', null=True, blank=True)
    terminal_battery = models.CharField(max_length=200, null=True, blank=True)    
    terminal_charger = models.CharField(max_length=200, null=True, blank=True)    
    terminal_manual = models.CharField(max_length=200, null=True, blank=True)    
    terminal_pin = models.CharField(max_length=200, null=True, blank=True)    
    status = models.CharField(max_length=255, choices=TERMINAL_STATUS, default='UNASSIGNED')
    is_active = models.BooleanField(default=False)

    class Meta:
            ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        terminal_count = Terminal.objects.count()
        tag_no = terminal_count+1
        self.device_tag_no = "DT" + self.model_no + str(tag_no).zfill(7)
        return super().save(*args, **kwargs)

    

class TerminalShipment(AuditableModel):
    shipment_code_name = models.CharField(max_length=100)
    device_shipped = models.CharField(max_length=100, help_text="e.g. D20 android terminals", )
    oem = models.CharField(max_length=100, help_text="e.g. D20 group")
    shipment_id = models.CharField(max_length=100, editable=False)
    shipment_partner = models.CharField(max_length=100)
    date_acquired = models.DateField()
    date_shipped = models.DateField()
    date_received = models.DateField()
    qty_paid_for = models.PositiveIntegerField()
    shipment_value = models.PositiveIntegerField()
    qty_shipped = models.PositiveIntegerField()
    qty_received = models.PositiveIntegerField()
    components = models.CharField(max_length=200)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-date_received"]

    def save(self, *args, **kwargs):
        total_shipments = TerminalShipment.objects.count()
        shipment_id = total_shipments + 1
        self.shipment_id = "DKTS" + f"{shipment_id}".zfill(3)
        return super().save(*args, **kwargs)


class TerminalShipmentFiles(AuditableModel):
    file = models.FileField(null=True, blank=True, upload_to="shipment_documents/")
    terminal_shipment = models.ForeignKey(TerminalShipment, on_delete=models.CASCADE, related_name="files")


class TerminalLog(AuditableModel):
    terminal = models.ForeignKey('tms.Terminal', on_delete=models.SET_NULL, related_name='terminal_log', null=True, blank=True)
    merchant_ref = models.UUIDField(null=True, blank=True)
    type = models.CharField(max_length=255, choices=TERMINAL_LOG_TYPE)
    actor = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='terminallog_actor')
    notes = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to="terminal_log_documents/")

    class Meta:
            ordering = ('-created_at',)

    def __str__(self):
        return self.terminal


class TerminalStatusUpdateFiles(models.Model):
    file = models.FileField(null=True, blank=True, upload_to="terminal_log_documents/")
    terminal_log = models.ForeignKey(TerminalLog, on_delete=models.SET_NULL, null=True, related_name="status_update_files")

