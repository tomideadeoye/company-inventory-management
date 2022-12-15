from django.db import models


class AccountsCustomuser(models.Model):
    password = models.CharField(max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    email = models.CharField(unique=True, max_length=254, blank=True, null=True)
    phone_number = models.CharField(unique=True, max_length=128, blank=True, null=True)
    type = models.SmallIntegerField()
    username = models.CharField(unique=True, max_length=100, blank=True, null=True)
    pin = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField()
    merchant_activity_status = models.BooleanField()
    is_archived = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts_customuser'


class AccountsCustomuserGroups(models.Model):
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AccountsCustomuserUserPermissions(models.Model):
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class AccountsProfile(models.Model):
    id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    updated_at = models.DateTimeField()
    profile_photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField(AccountsCustomuser, models.DO_NOTHING)
    activity_reward = models.FloatField()
    activity_today = models.IntegerField()
    referral_code = models.CharField(max_length=100, blank=True, null=True)
    total_activity = models.IntegerField()
    weekly_activity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'accounts_profile'


class AccountsSetting(models.Model):
    id = models.UUIDField(primary_key=True)
    font_size = models.SmallIntegerField()
    terms_and_condition = models.BooleanField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_setting'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class BusinessBusinessaccount(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(unique=True, max_length=254, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_type = models.ForeignKey('BusinessBusinesstype', models.DO_NOTHING)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING, blank=True, null=True, related_name='business_account')
    tax_identification_number = models.CharField(max_length=100, blank=True, null=True)
    photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    business_profile = models.ForeignKey('BusinessBusinessprofile', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'business_businessaccount'


class BusinessBusinessaccountUsers(models.Model):
    businessaccount = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'business_businessaccount_users'
        unique_together = (('businessaccount', 'customuser'),)


class BusinessBusinessaccounttax(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'business_businessaccounttax'


class BusinessBusinesspreference(models.Model):
    id = models.UUIDField(primary_key=True)
    receipt_color = models.CharField(max_length=10)
    business_account = models.OneToOneField(BusinessBusinessaccount, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'business_businesspreference'


class BusinessBusinessprofile(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'business_businessprofile'


class BusinessBusinesstype(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'business_businesstype'


class CurrencyconverterCurrencyrate(models.Model):
    id = models.UUIDField(primary_key=True)
    currency = models.CharField(max_length=255)
    date = models.DateField(blank=True, null=True)
    rate = models.FloatField(blank=True, null=True)
    created_at = models.DateField()
    updated_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'currencyconverter_currencyrate'


class CustomersCustomer(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'customers_customer'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoCeleryBeatClockedschedule(models.Model):
    clocked_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_clockedschedule'


class DjangoCeleryBeatCrontabschedule(models.Model):
    minute = models.CharField(max_length=240)
    hour = models.CharField(max_length=96)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=124)
    month_of_year = models.CharField(max_length=64)
    timezone = models.CharField(max_length=63)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_crontabschedule'


class DjangoCeleryBeatIntervalschedule(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_intervalschedule'


class DjangoCeleryBeatPeriodictask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjangoCeleryBeatCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjangoCeleryBeatIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    solar = models.ForeignKey('DjangoCeleryBeatSolarschedule', models.DO_NOTHING, blank=True, null=True)
    one_off = models.BooleanField()
    start_time = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    headers = models.TextField()
    clocked = models.ForeignKey(DjangoCeleryBeatClockedschedule, models.DO_NOTHING, blank=True, null=True)
    expire_seconds = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictask'


class DjangoCeleryBeatPeriodictasks(models.Model):
    ident = models.SmallIntegerField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictasks'


class DjangoCeleryBeatSolarschedule(models.Model):
    event = models.CharField(max_length=24)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_solarschedule'
        unique_together = (('event', 'latitude', 'longitude'),)


class DjangoCeleryResultsChordcounter(models.Model):
    group_id = models.CharField(unique=True, max_length=255)
    sub_tasks = models.TextField()
    count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_celery_results_chordcounter'


class DjangoCeleryResultsTaskresult(models.Model):
    task_id = models.CharField(unique=True, max_length=255)
    status = models.CharField(max_length=50)
    content_type = models.CharField(max_length=128)
    content_encoding = models.CharField(max_length=64)
    result = models.TextField(blank=True, null=True)
    date_done = models.DateTimeField()
    traceback = models.TextField(blank=True, null=True)
    meta = models.TextField(blank=True, null=True)
    task_args = models.TextField(blank=True, null=True)
    task_kwargs = models.TextField(blank=True, null=True)
    task_name = models.CharField(max_length=255, blank=True, null=True)
    worker = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_results_taskresult'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class ExpensesExpense(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expenses_expense'


class FcmDjangoFcmdevice(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField()
    date_created = models.DateTimeField(blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    registration_id = models.TextField()
    type = models.CharField(max_length=10)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fcm_django_fcmdevice'


class InventoryBarcode(models.Model):
    id = models.UUIDField(primary_key=True)
    barcode_number = models.CharField(unique=True, max_length=255)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    barcode_photo = models.CharField(max_length=100, blank=True, null=True)
    verified = models.BooleanField()
    archived = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING, blank=True, null=True, related_name='inventroy_creator')
    verified_by = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING, blank=True, null=True, related_name='inventory_verifier')
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    created_strategy = models.IntegerField()
    manufacturer_name = models.CharField(max_length=255, blank=True, null=True)
    product_photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    image_url = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inventory_barcode'


class InventorySold(models.Model):
    id = models.UUIDField(primary_key=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    sales_date = models.DateTimeField()
    stock = models.OneToOneField('InventoryStock', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inventory_sold'


class InventoryStock(models.Model):
    id = models.UUIDField(primary_key=True)
    product = models.CharField(max_length=100)
    unit = models.CharField(max_length=3)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    photo = models.OneToOneField('SharedPhotoupload', models.DO_NOTHING, blank=True, null=True)
    barcode_number = models.CharField(max_length=255, blank=True, null=True)
    last_restocked_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inventory_stock'


class NotificationsNotification(models.Model):
    id = models.UUIDField(primary_key=True)
    notification_type = models.CharField(max_length=255)
    action_url = models.CharField(max_length=200, blank=True, null=True)
    is_seen = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING, blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications_notification'


class NotificationsNotificationDevices(models.Model):
    notification = models.ForeignKey(NotificationsNotification, models.DO_NOTHING)
    fcmdevice = models.ForeignKey(FcmDjangoFcmdevice, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notifications_notification_devices'
        unique_together = (('notification', 'fcmdevice'),)


class NotificationsNotificationsetting(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notifications_notificationsetting'


class OrdersOrder(models.Model):
    id = models.UUIDField(primary_key=True)
    order_type = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    custom_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    customer = models.ForeignKey(CustomersCustomer, models.DO_NOTHING)
    invoice = models.BooleanField()
    invoice_status = models.CharField(max_length=10)
    due_date = models.DateTimeField(blank=True, null=True)
    company = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'orders_order'


class OrdersOrderBusinessTaxes(models.Model):
    order = models.ForeignKey(OrdersOrder, models.DO_NOTHING)
    businessaccounttax = models.ForeignKey(BusinessBusinessaccounttax, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'orders_order_business_taxes'
        unique_together = (('order', 'businessaccounttax'),)


class OrdersOrderitem(models.Model):
    id = models.UUIDField(primary_key=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField()
    item = models.ForeignKey(InventoryStock, models.DO_NOTHING)
    order = models.ForeignKey(OrdersOrder, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'orders_orderitem'


class PaymentsPayment(models.Model):
    id = models.UUIDField(primary_key=True)
    mode_of_payment = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    pay_later_date = models.DateField(blank=True, null=True)
    pdf_file = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    order = models.OneToOneField(OrdersOrder, models.DO_NOTHING)
    payment_completed_date = models.DateTimeField(blank=True, null=True)
    transaction_info = models.JSONField(blank=True, null=True)
    taxes_at_payment = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments_payment'


class PaymentsSolditem(models.Model):
    id = models.UUIDField(primary_key=True)
    product = models.TextField()
    unit = models.CharField(max_length=3)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.ForeignKey(PaymentsPayment, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments_solditem'


class PosPos(models.Model):
    id = models.UUIDField(primary_key=True)
    zmk = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    port = models.BigIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    business_account = models.ForeignKey(BusinessBusinessaccount, models.DO_NOTHING)
    terminal_id = models.OneToOneField('PosTerminalid', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pos_pos'


class PosTerminalid(models.Model):
    id = models.UUIDField(primary_key=True)
    terminal_id = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pos_terminalid'


class RewardsystemActivityrecord(models.Model):
    id = models.UUIDField(primary_key=True)
    activity = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'rewardsystem_activityrecord'


class SharedPhotoupload(models.Model):
    id = models.UUIDField(primary_key=True)
    photo = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'shared_photoupload'


class SharedTwilioservice(models.Model):
    id = models.UUIDField(primary_key=True)
    phone_number = models.CharField(unique=True, max_length=128)
    service_id = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'shared_twilioservice'


class WaffleFlag(models.Model):
    name = models.CharField(unique=True, max_length=100)
    everyone = models.BooleanField(blank=True, null=True)
    percent = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    testing = models.BooleanField()
    superusers = models.BooleanField()
    staff = models.BooleanField()
    authenticated = models.BooleanField()
    languages = models.TextField()
    rollout = models.BooleanField()
    note = models.TextField()
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'waffle_flag'


class WaffleFlagGroups(models.Model):
    flag = models.ForeignKey(WaffleFlag, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'waffle_flag_groups'
        unique_together = (('flag', 'group'),)


class WaffleFlagUsers(models.Model):
    flag = models.ForeignKey(WaffleFlag, models.DO_NOTHING)
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'waffle_flag_users'
        unique_together = (('flag', 'customuser'),)


class WaffleSample(models.Model):
    name = models.CharField(unique=True, max_length=100)
    percent = models.DecimalField(max_digits=4, decimal_places=1)
    note = models.TextField()
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'waffle_sample'


class WaffleSwitch(models.Model):
    name = models.CharField(unique=True, max_length=100)
    active = models.BooleanField()
    note = models.TextField()
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'waffle_switch'
