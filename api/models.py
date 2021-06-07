from django.db import models

class WeatherInfo(models.Model):
    timezone = models.CharField(max_length=25, primary_key=True)
    latitude = models.DecimalField(max_digits=4, decimal_places=2)
    longitude = models.DecimalField(max_digits=5, decimal_places=2)
    timezone_offset = models.IntegerField()
    dt = models.DateTimeField(null=True)
    temp = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    pressure = models.IntegerField(null=True)
    humidity = models.IntegerField(null=True)
    visibility = models.IntegerField(null=True)
    wind_speed =  models.DecimalField(max_digits=5, decimal_places=2, null=True)
    description = models.CharField(max_length=25)

    class Meta:
        ordering = ('timezone',)

    def __str__(self):
        return self.timezone

class WeatherByMinute(models.Model):
    weather_info = models.ForeignKey(WeatherInfo, related_name='minutely', on_delete=models.CASCADE, null=True)
    dt = models.DateTimeField(null=True)
    precipitation = models.DecimalField(max_digits=5, decimal_places=3)

class WeatherByHour(models.Model):
    weather_info = models.ForeignKey(WeatherInfo, related_name='hourly', on_delete=models.CASCADE, null=True)
    dt = models.DateTimeField(null=True)
    temp = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.IntegerField()
    humidity = models.IntegerField()
    visibility = models.IntegerField(null=True)
    wind_speed =  models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=25)

class WeatherByDay(models.Model):
    weather_info = models.ForeignKey(WeatherInfo, related_name='daily', on_delete=models.CASCADE, null=True)
    dt = models.DateTimeField(null=True)
    temp = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.IntegerField()
    humidity = models.IntegerField()
    visibility = models.IntegerField(null=True)
    wind_speed =  models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=25)

