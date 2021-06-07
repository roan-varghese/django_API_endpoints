from django.http import JsonResponse, HttpResponse
import requests, json, io
from django.shortcuts import redirect, render

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from .serializers import PersonSerializer
from .models import Person

class TestApiView(APIView):
    
    # parser_classes = [ JSONParser ]

    def get(self, request):
        data = {
            'name': 'Andrew',
            'age': 20
        }
        queryset = Person.objects.all()
        serializer = PersonSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


    # return JsonResponse(weather_data)
    # return JsonResponse({"lat":25.2048,"lon":55.2708,"timezone":"Asia/Dubai","timezone_offset":14400,"current":{"dt":1622719694,"sunrise":1622683717,"sunset":1622732750,"temp":317.21,"feels_like":315.87,"pressure":1001,"humidity":14,"dew_point":283.76,"uvi":6.57,"clouds":0,"visibility":10000,"wind_speed":5.96,"wind_deg":282,"wind_gust":6.28,"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}]}})
