from dotenv import load_dotenv
import os, csv
from django.http import JsonResponse, HttpResponse
import requests, json
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from .models import *
from .serializers import *

# Endpoint to trigger weather search on POST
class APIOneView(ModelViewSet):

    queryset = WeatherInfo.objects.all()
    serializer_class = WeatherInfoSerializer

    def format_decimal_places(self, val):
        val = float("{:.2f}".format(val))
        return val

    def get_avg_temp(self, min, max):
        avg = ( min + max ) / 2
        return avg

    def convert_to_date(self, str):
        return datetime.fromtimestamp(int(str)).strftime('%Y-%m-%d %H:%M')

    def format_data(self, data):
        
        # Lat & long
        data['latitude'] = self.format_decimal_places(data['lat'])
        data['longitude'] = self.format_decimal_places(data['lon'])

        # Current Weather
        current_data = data['current']
        if current_data is not None:
            current_data['description'] = current_data['weather'][0]['description'] # description

        data.update(current_data)
        data['dt'] = self.convert_to_date(data['dt']) # datetime

        # Minutes
        minutely_data = data['minutely']
        if minutely_data is not None:
            for min in minutely_data:
                min['dt'] = self.convert_to_date(min['dt']) # datetime

        # Hours
        hourly_data = data['hourly']
        if hourly_data is not None:
            for hour in hourly_data:
                hour['dt'] = self.convert_to_date(hour['dt']) # datetime
                hour['description'] = hour['weather'][0]['description'] # description

        # Days
        daily_data = data['daily']
        if daily_data is not None:
            for day in daily_data:  
                day['dt'] = self.convert_to_date(day['dt']) # datetime
                min = int(day['temp']['min'])
                max = int(day['temp']['max'])
                day['temp'] = self.get_avg_temp(min, max) # average temperature
                day['description'] = day['weather'][0]['description'] # description

        return data
    
    # POST requests
    def post(self, request):
        
        url = "https://api.openweathermap.org/data/2.5/onecall"

        post_data = ValidateRequest(data=request.data)
        if not post_data.is_valid():
            return Response(post_data.errors)

        load_dotenv()
        querystring = {"exclude": "alerts", "appid": os.getenv('API_KEY')}
        querystring.update(request.data)
        response = requests.request("GET", url, params=querystring)

        weather_data = json.loads(response.text)
        weather_data = self.format_data(weather_data)

        if not WeatherInfo.objects.filter(timezone=weather_data['timezone']).exists():
            serializer = WeatherInfoSerializer(data=weather_data)
        else:
            qs = WeatherInfo.objects.get(timezone=weather_data['timezone'])
            serializer = WeatherInfoSerializer(qs, data=weather_data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
            
        return Response(serializer.errors)


# Displays number of items per page
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 1


# Endpoints to return stored data, and export filtered data as CSV
class APITwoView(ModelViewSet):
    queryset = WeatherInfo.objects.all()
    serializer_class = WeatherInfoSerializer
    pagination_class = CustomPageNumberPagination

    search_fields = ['timezone', 'latitude', 'longitude', 'dt', 'description',]
    ordering_fields = ['timezone', 'latitude', 'longitude', 'dt', 'description',]
    filterset_fields  = ['timezone', 'latitude', 'longitude', 'dt', 'description',]

    exceptionRaised = False
    
    # GET on base url
    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())

        qs = self.add_filters(qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    # Data by minutes 
    @action(detail=False, methods=["GET"])
    def minutely(self, request):
        qs = WeatherByMinute.objects.all()

        ordering = self.request.query_params.get('ordering')
        if self.check_exists(ordering):
            try: qs = qs.order_by(ordering)
            except Exception as e: return Response({'error': str(e)})

        qs = self.add_filters(qs)

        pr = self.request.query_params.get('precipitation')
        if self.check_exists(pr):
            try: qs = qs.filter(precipitation=pr)
            except Exception as e: return Response(e)

        serializer = WeatherByMinuteSerializer(qs, many=True)
        if serializer.is_valid:
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    # Data by hours
    @action(detail=False, methods=["GET"])
    def hourly(self, request):
        qs = WeatherByHour.objects.all()

        ordering = self.request.query_params.get('ordering')
        if self.check_exists(ordering):
            try: qs = qs.order_by(ordering)
            except Exception as e: return Response({'error': str(e)})

        qs = self.add_filters(qs)
        if self.exceptionRaised:
            return Response({'error': str(self.exceptionRaised)})
        
        serializer = WeatherByHourSerializer(qs, many=True)
        if serializer.is_valid:
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    # Data by days
    @action(detail=False, methods=["GET"])
    def daily(self, request):
        qs = WeatherByDay.objects.all()

        ordering = self.request.query_params.get('ordering')
        if self.check_exists(ordering):
            try: qs = qs.order_by(ordering)
            except Exception as e: return Response({'error': str(e)})

        qs = self.add_filters(qs)
        if self.exceptionRaised:
            return Response({'error': str(self.exceptionRaised)})
        
        serializer = WeatherByDaySerializer(qs, many=True)
        if serializer.is_valid:
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    # Gets query parameters (if any)
    def get_params(self):
        timezone = self.request.query_params.get('timezone')
        start_dt = self.request.query_params.get('start_dt')
        end_dt = self.request.query_params.get('end_dt')
        description = self.request.query_params.get('description')
        return timezone, start_dt, end_dt, description

    def get_num_params(self):
        temp = self.request.query_params.get('temp')
        tempgt = self.request.query_params.get('tempgt')
        templt = self.request.query_params.get('templt')
        visibility = self.request.query_params.get('visibility')
        humidity = self.request.query_params.get('humidity')
        windspeed = self.request.query_params.get('windspeed')
        windspeedgt = self.request.query_params.get('windspeedgt')
        windspeedlt = self.request.query_params.get('windspeedlt')
        return temp, tempgt, templt, visibility, humidity, windspeed, windspeedgt, windspeedlt

    def check_exists(self, param):
        return param != "" and param is not None

    # Filters queryset by query parameters
    def add_filters(self, qs):

        timezone, start_dt, end_dt, desc = self.get_params()
        temp, tempgt, templt, visibility, humidity, ws, wsgt, wslt = self.get_num_params()

        # String/date filters
        if self.check_exists(timezone):
            try: qs = self.timezone_filters(qs, timezone)
            except Exception as e: 
                self.exceptionRaised = e
                return
        if self.check_exists(start_dt) or self.check_exists(end_dt):
            try: qs = self.datetime_filters(qs, start_dt, end_dt)
            except Exception as e: 
                self.exceptionRaised = e
                return
        if self.check_exists(desc):
            try: qs = self.description_filters(qs, desc)
            except Exception as e: 
                self.exceptionRaised = e
                return

        # Numeric filters
        if self.check_exists(temp) or self.check_exists(tempgt) or self.check_exists(templt):
            try: qs = self.temp_filters(qs, temp, tempgt, templt)
            except Exception as e: 
                self.exceptionRaised = e
                return
        if self.check_exists(visibility):
            try: qs = self.visibility_filters(qs, visibility)
            except Exception as e: 
                self.exceptionRaised = e
                return
        if self.check_exists(humidity):
            try: qs = self.humidity_filters(qs, humidity)
            except Exception as e: 
                self.exceptionRaised = e
                return
        if self.check_exists(ws) or self.check_exists(wsgt) or self.check_exists(wslt):
            try: qs = self.wind_speed_filters(qs, ws, wsgt, wslt)
            except Exception as e: 
                self.exceptionRaised = e
                return

        return qs


    # Custom Filters

    def datetime_filters(self, qs, start_dt, end_dt):
        if start_dt is not None and end_dt is not None:
            return qs.filter(dt__range=(start_dt,end_dt))
        if start_dt is not None:
            return qs.filter(dt=start_dt)
        return qs.filter(dt=end_dt)

    def timezone_filters(self, qs, data):
        if '=' in data:
            d = data.replace("=", "") 
            if data.startswith('='):
                return qs.filter(weather_info__timezone__iexact=d)
        if '*' in data:
            d = data.replace("*", "")
            if data.startswith('*'):
                return qs.filter(weather_info__timezone__endswith=d)
            if data.endswith('*'):
                return qs.filter(weather_info__timezone__startswith=d)

        return qs.filter(weather_info__timezone__icontains=data)

    def description_filters(self, qs, data):
        if '=' in data:
            d = data.replace("=", "") 
            if data.startswith('='):
                return qs.filter(description__iexact=d)
        if '*' in data:
            d = data.replace("*", "")
            if data.startswith('*'):
                return qs.filter(description__endswith=d)
            if data.endswith('*'):
                return qs.filter(description__startswith=d)

        return qs.filter(description__icontains=data)

    def precipitation_filters(self, qs, data, greater_val=None, less_val=None):
        if data is not None:
            return qs.filter(precipitation=data)

        if greater_val is not None and less_val is not None:
            return qs.filter(precipitation__gte=greater_val, precipitation__lte=less_val)
        if greater_val is not None:
            return qs.filter(precipitation__gte=greater_val)
            
        return qs.filter(precipitation__lte=less_val)

    def temp_filters(self, qs, data, greater_val=None, less_val=None):
        if data is not None:
            return qs.filter(temp=data)

        if greater_val is not None and less_val is not None:
            return qs.filter(temp__gte=greater_val, temp__lte=less_val)
        elif greater_val is not None:
            return qs.filter(temp__gte=greater_val)
        return qs.filter(temp__lte=less_val)

    def visibility_filters(self, qs, data, greater_val=None, less_val=None):
        if data is not None:
            return qs.filter(visibility=data)

        if greater_val is not None and less_val is not None:
            return qs.filter(visibility__gte=greater_val, visibility__lte=less_val)
        elif greater_val is not None:
            return qs.filter(visibility__gte=greater_val)
        return qs.filter(visibility__lte=less_val)

    def humidity_filters(self, qs, data, greater_val=None, less_val=None):
        if data is not None:
            return qs.filter(humidity=data)

        if greater_val is not None and less_val is not None:
            return qs.filter(humidity__gte=greater_val, humidity__lte=less_val)
        elif greater_val is not None:
            return qs.filter(humidity__gte=greater_val)
        return qs.filter(humidity__lte=less_val)

    def wind_speed_filters(self, qs, data, greater_val=None, less_val=None):
        if data is not None:
            return qs.filter(wind_speed=data)

        if greater_val is not None and less_val is not None:
            return qs.filter(wind_speed__gte=greater_val, wind_speed__lte=less_val)
        elif greater_val is not None:
            return qs.filter(wind_speed__gte=greater_val)
        return qs.filter(wind_speed__lte=less_val)


    # Generate CSVs

    @action(detail=False, methods=["GET"])
    def export_current_csv(self, request):
        data = self.get_queryset().values()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="current.csv'

        writer = csv.writer(response)

        writer.writerow(['TIMEZONE', 'LATITUDE', 'LONGITUDE', 'DT', 'TEMP', 'PRESSURE', 'HUMIDITY', 'WIND SPEED', 'VISIBILITY', 'DESCRIPTION'])
        for record in data:
            writer.writerow([ record['timezone'], record['latitude'], record['longitude'], record['dt'], record['temp'], record['pressure'], record['humidity'], 
            record['wind_speed'], record['visibility'], record['description'] ])

        return response

    @action(detail=False, methods=["GET"])
    def export_minutely_csv(self, request):
        res = self.minutely(request)
        data = res.data

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="minute.csv'

        writer = csv.writer(response)

        writer.writerow(['TIMEZONE', 'DT', 'PRECIPITATION'])
        for record in data:
            writer.writerow([ record['weather_info'], record['dt'], record['precipitation']  ])

        return response

    @action(detail=False, methods=["GET"])
    def export_hourly_csv(self, request):
        res = self.hourly(request)
        data = res.data

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hour.csv'

        writer = csv.writer(response)

        writer.writerow(['TIMEZONE', 'LATITUDE', 'LONGITUDE', 'DT', 'TEMP', 'HUMIDITY', 'WIND SPEED', 'VISIBILITY', 'DESCRIPTION'])
        for record in data:
            writer.writerow([ record['weather_info'], record['dt'], record['temp'], record['humidity'], 
            record['wind_speed'], record['visibility'], record['description'] ])

        return response

    @action(detail=False, methods=["GET"])
    def export_daily_csv(self, request):
        res = self.daily(request)
        data = res.data

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="day.csv'

        writer = csv.writer(response)

        writer.writerow(['TIMEZONE', 'LATITUDE', 'LONGITUDE', 'DT', 'AVG_TEMP','HUMIDITY', 'WIND SPEED', 'DESCRIPTION'])
        for record in data:
            writer.writerow([ record['weather_info'], record['dt'], record['temp'], record['humidity'], 
            record['wind_speed'], record['description'] ])

        return response
        
