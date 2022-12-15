import re

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import serializers


def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from])
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)


class ValidatePassword:

    def __init__(self, password):
        self.password = password

    def __validate_no_digit(self):
        if not re.findall('\d', self.password):
            raise serializers.ValidationError({'password': ("The password must contain at least 1 digit, 0-9.")}
            )
    def __validate_uppercase(self):
        if not re.findall('[A-Z]', self.password):
            raise ValidationError({'password':
                ("The password must contain at least 1 uppercase letter, A-Z.")}
            )
    def __validate_lowercase(self):
        if not re.findall('[a-z]', self.password):
            raise ValidationError({'paswword':
                ("The password must contain at least 1 lowercase letter, a-z.")}
            )
    def __validate_symbol(self):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', self.password):
            raise ValidationError({'password':
                ("The password must contain at least 1 symbol: " +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")}
            )
    def validate(self):
         self.__validate_no_digit()
         self.__validate_lowercase()
         self.__validate_uppercase()
         self.__validate_symbol()
