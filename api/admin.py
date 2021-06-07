from django.contrib import admin
from .models import *

admin.site.register(WeatherInfo)
admin.site.register(WeatherByMinute)
admin.site.register(WeatherByHour)
admin.site.register(WeatherByDay)