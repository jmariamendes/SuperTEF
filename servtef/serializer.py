from rest_framework import serializers
from .models import LogTrans


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogTrans
        fields = '__all__'
