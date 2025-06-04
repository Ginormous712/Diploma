from rest_framework import serializers
from .models import Flight, Airport, Airline


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['name', 'code', 'location', 'latitude', 'longitude']


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['name']


class FlightSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = [
            'id',
            'flight_number',
            'departure_time',
            'arrival_time',
            'status',
            'departure_airport',
            'arrival_airport',
            'airline'
        ]