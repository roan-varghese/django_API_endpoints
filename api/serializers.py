from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer, PrimaryKeyRelatedField, Serializer
from .models import *

class ValidateRequest(Serializer):
    lat = serializers.DecimalField(max_digits=8, decimal_places=6)
    lon = serializers.DecimalField(max_digits=9, decimal_places=6)

class WeatherByMinuteSerializer(ModelSerializer):
    class Meta: 
        model = WeatherByMinute

        fields = (
            'dt',
            'precipitation',
            'weather_info',
        )
        read_only_fields = ('weather_info',)

class WeatherByHourSerializer(ModelSerializer):
    class Meta: 
        model = WeatherByHour

        fields = (
            'dt',
            'temp', 
            'pressure', 
            'humidity', 
            'wind_speed',
            'visibility',
            'description',
            'weather_info',
        )
        read_only_fields = ('weather_info',)

class WeatherByDaySerializer(ModelSerializer):
    class Meta: 
        model = WeatherByDay

        fields = (
            'dt',
            'temp', 
            'pressure', 
            'humidity', 
            'wind_speed',
            'description',
            'weather_info',
        )
        read_only_fields = ('weather_info',)
    
class WeatherInfoSerializer(ModelSerializer):
    minutely = WeatherByMinuteSerializer(many=True)
    hourly = WeatherByHourSerializer(many=True)
    daily = WeatherByDaySerializer(many=True)

    class Meta: 
        model = WeatherInfo

        fields = (
            'timezone', 
            'latitude', 
            'longitude', 
            'timezone_offset',
            'dt',
            'temp', 
            'pressure', 
            'humidity', 
            'wind_speed',
            'visibility',
            'description',
            'minutely',
            'hourly',
            'daily',
        )

    def create(self, validated_data):
        
        minutely_data = validated_data.pop('minutely')
        hourly_data = validated_data.pop('hourly')
        daily_data = validated_data.pop('daily')

        
        WI = WeatherInfo.objects.create(**validated_data)
        
        

        if minutely_data is not None:
            for minute in minutely_data:
                WeatherByMinute.objects.create(weather_info=WI, **minute)

        if hourly_data is not None:
            for hour in hourly_data:
                WeatherByHour.objects.create(weather_info=WI, **hour)

        if daily_data is not None:
            for day in daily_data:  
                WeatherByDay.objects.create(weather_info=WI, **day)

        return WI


    def update(self, instance, validated_data):
        minutely_data = validated_data.pop('minutely')
        hourly_data = validated_data.pop('hourly')
        daily_data = validated_data.pop('daily')
        
        if minutely_data is not None:
            for minute in minutely_data:
                WeatherByMinute.objects.create(weather_info=instance, **minute)

        if hourly_data is not None:
            for hour in hourly_data:
                WeatherByHour.objects.create(weather_info=instance, **hour)

        if daily_data is not None:
            for day in daily_data:  
                WeatherByDay.objects.create(weather_info=instance, **day)

        return instance