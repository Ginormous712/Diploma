from django.db import models
from django.contrib.auth.models import AbstractUser


class Airline(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    contact_info = models.TextField()

    class Meta:
        db_table = 'airline'

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)  # IATA/ICAO
    location = models.CharField(max_length=255)
    contact_info = models.TextField()
    latitude = models.FloatField(null=True, blank=True)  # Додаємо поле широти
    longitude = models.FloatField(null=True, blank=True) # Додаємо поле довготи

    class Meta:
        db_table = 'airport'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=50)

    departure_airport = models.ForeignKey(Airport, related_name='departing_flights', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arriving_flights', on_delete=models.CASCADE)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)

    class Meta:
        db_table = 'flight'

    def __str__(self):
        return self.flight_number


class CrewMember(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    qualification = models.CharField(max_length=100)
    contact_info = models.TextField()

    class Meta:
        db_table = 'crew_member'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"


class CrewTeam(models.Model):
    flight = models.OneToOneField(Flight, on_delete=models.CASCADE)
    members = models.ManyToManyField(CrewMember)

    class Meta:
        db_table = 'crew_team'

    def __str__(self):
        return f"Crew Team for {self.flight}"


class User(AbstractUser):
    ROLES = (
        ('guest', 'Guest'),
        ('registered', 'Registered User'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='guest')

    class Meta:
        db_table = 'user'


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    issued_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket'

    def __str__(self):
        return f"Ticket #{self.id} - {self.user.username} - {self.flight.flight_number}"
