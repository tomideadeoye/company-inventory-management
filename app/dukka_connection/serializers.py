from rest_framework import serializers

from .models import AccountsCustomuser


class ListMerchantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccountsCustomuser
        fields = ['id', 'username', 'phone_number', 'email']
        extra_kwargs = {
            'is_active': {'read_only': True},
        }

    def to_representation(self, instance: AccountsCustomuser):
        data = super().to_representation(instance)
        # business_account = BusinessBusinessaccount.objects.using('dukka_db').filter(user=instance.id).first()
        business_account = instance.business_account.first()
        merchant_location = None
        merchant_category = None
        name = None
        if business_account:
            merchant_location = business_account.address
            merchant_category = getattr(business_account.business_type, 'title') if business_account.business_type else None
            name = business_account.name
        data['merchant_location'] = merchant_location
        data['merchant_category'] = merchant_category
        data['name'] = name
        return data    
