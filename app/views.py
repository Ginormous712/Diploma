from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Airline, Flight, Airport, Ticket, CrewMember, CrewTeam
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomUserForm, TicketBookingForm, RegistrationForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

from .pdf_util import generate_ticket_pdf
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FlightSerializer
from django.db.models import Q
from rapidfuzz import fuzz
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view # Додаємо api_view
from rest_framework.response import Response # Додаємо Response
from .serializers import AirportSerializer, FlightSerializer # Імпортуємо AirportSerializer, FlightSerializer

# Імпорт функцій імпорту/експорту з окремих файлів
from .data_management.airlines import export_airlines_csv, export_airlines_excel, import_airlines
from .data_management.airports import export_airports_csv, export_airports_excel, import_airports
from .data_management.flights import export_flights_csv, export_flights_excel, import_flights
from .data_management.tickets import export_tickets_csv, export_tickets_excel, import_tickets
from .data_management.users import export_users_csv, export_users_excel, import_users
from .data_management.crew_members import export_crew_members_csv, export_crew_members_excel, import_crew_members
from .data_management.crew_teams import export_crew_teams_csv, export_crew_teams_excel, import_crew_teams

from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Count, Sum # Для агрегації даних
from django.db.models.functions import TruncMonth # Для групування за місяцями


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})




@login_required
def profile_view(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    return render(request, 'profile.html', {'user': user, 'tickets': tickets})

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'profile_edit.html', {'form': form})

# Допоміжна функція для перевірки, чи є користувач адміністратором (is_staff)
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_tools_view(request):
    return render(request, 'admin_tools.html')

# --- Передача функцій імпорту/експорту через @user_passes_test(is_admin) ---

# Airlines
@user_passes_test(is_admin)
def wrapped_export_airlines_csv(request): return export_airlines_csv(request)
@user_passes_test(is_admin)
def wrapped_export_airlines_excel(request): return export_airlines_excel(request)
@user_passes_test(is_admin)
def wrapped_import_airlines(request): return import_airlines(request)

# Airports
@user_passes_test(is_admin)
def wrapped_export_airports_csv(request): return export_airports_csv(request)
@user_passes_test(is_admin)
def wrapped_export_airports_excel(request): return export_airports_excel(request)
@user_passes_test(is_admin)
def wrapped_import_airports(request): return import_airports(request)

# Flights
@user_passes_test(is_admin)
def wrapped_export_flights_csv(request): return export_flights_csv(request)
@user_passes_test(is_admin)
def wrapped_export_flights_excel(request): return export_flights_excel(request)
@user_passes_test(is_admin)
def wrapped_import_flights(request): return import_flights(request)

# Tickets
@user_passes_test(is_admin)
def wrapped_export_tickets_csv(request): return export_tickets_csv(request)
@user_passes_test(is_admin)
def wrapped_export_tickets_excel(request): return export_tickets_excel(request)
@user_passes_test(is_admin)
def wrapped_import_tickets(request): return import_tickets(request)

# Users
@user_passes_test(is_admin)
def wrapped_export_users_csv(request): return export_users_csv(request)
@user_passes_test(is_admin)
def wrapped_export_users_excel(request): return export_users_excel(request)
@user_passes_test(is_admin)
def wrapped_import_users(request): return import_users(request)

# Crew Members
@user_passes_test(is_admin)
def wrapped_export_crew_members_csv(request): return export_crew_members_csv(request)
@user_passes_test(is_admin)
def wrapped_export_crew_members_excel(request): return export_crew_members_excel(request)
@user_passes_test(is_admin)
def wrapped_import_crew_members(request): return import_crew_members(request)

# Crew Teams
@user_passes_test(is_admin)
def wrapped_export_crew_teams_csv(request): return export_crew_teams_csv(request)
@user_passes_test(is_admin)
def wrapped_export_crew_teams_excel(request): return export_crew_teams_excel(request)
@user_passes_test(is_admin)
def wrapped_import_crew_teams(request): return import_crew_teams(request)


# --- Airlines ---
@user_passes_test(is_admin)
def show_airlines(request):
    airlines = Airline.objects.all()
    return render(request, 'show_airlines.html', {'airlines': airlines})

@user_passes_test(is_admin)
def create_airline(request):
    if request.method == 'POST':
        airline = Airline()
        airline.name = request.POST.get('name')
        airline.country = request.POST.get('country')
        airline.contact_info = request.POST.get('contact_info')
        airline.save()
        messages.success(request, 'Airline created successfully.')
        return HttpResponseRedirect('/show_airlines/')
    return render(request, 'create_airline.html')

@user_passes_test(is_admin)
def update_airline(request, id):
    try:
        airline = Airline.objects.get(pk=id)
        if request.method == 'POST':
            airline.name = request.POST.get('name')
            airline.country = request.POST.get('country')
            airline.contact_info = request.POST.get('contact_info')
            airline.save()
            messages.success(request, 'Airline updated successfully.')
            return HttpResponseRedirect('/show_airlines/')
        else:
            return render(request, "update_airline.html", {'airline': airline})
    except Airline.DoesNotExist:
        messages.error(request, 'Airline does not exist.')
        return HttpResponseNotFound('Airline does not exist')

@user_passes_test(is_admin)
def delete_airline(request, id):
    try:
        airline = Airline.objects.get(pk=id)
        airline.delete()
        messages.success(request, 'Airline deleted successfully.')
        return HttpResponseRedirect('/show_airlines/')
    except Airline.DoesNotExist:
        messages.error(request, 'Airline does not exist.')
        return HttpResponseNotFound('Airline does not exist')

# --- Flights ---
@user_passes_test(is_admin)
def show_flights(request):
    flights = Flight.objects.select_related('airline', 'departure_airport', 'arrival_airport').all()
    return render(request, 'show_flights.html', {'flights': flights})

@user_passes_test(is_admin)
def create_flight(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        status = request.POST.get('status')
        airline_id = request.POST.get('airline')
        departure_airport_id = request.POST.get('departure_airport')
        arrival_airport_id = request.POST.get('arrival_airport')

        Flight.objects.create(
            flight_number=flight_number,
            departure_time=departure_time,
            arrival_time=arrival_time,
            status=status,
            airline_id=airline_id,
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
        )
        messages.success(request, 'Flight created successfully.')
        return HttpResponseRedirect('/show_flights/')
    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    return render(request, "create_flight.html", {
        "airlines": airlines,
        "airports": airports
    })

@user_passes_test(is_admin)
def update_flight(request, id):
    try:
        flight = Flight.objects.get(pk=id)
        if request.method == 'POST':
            flight.flight_number = request.POST.get('flight_number')
            flight.departure_time = request.POST.get('departure_time')
            flight.arrival_time = request.POST.get('arrival_time')
            flight.status = request.POST.get('status')
            flight.airline_id = request.POST.get('airline')
            flight.departure_airport_id = request.POST.get('departure_airport')
            flight.arrival_airport_id = request.POST.get('arrival_airport')
            flight.save()
            messages.success(request, 'Flight updated successfully.')
            return HttpResponseRedirect('/show_flights/')
        else:
            airlines = Airline.objects.all()
            airports = Airport.objects.all()
            return render(request, "update_flight.html", {
                'flight': flight,
                "airlines": airlines,
                "airports": airports
            })
    except Flight.DoesNotExist:
        messages.error(request, 'Flight does not exist.')
        return HttpResponseNotFound('Flight does not exist')

@user_passes_test(is_admin)
def delete_flight(request, id):
    try:
        flight = Flight.objects.get(pk=id)
        flight.delete()
        messages.success(request, 'Flight deleted successfully.')
        return HttpResponseRedirect('/show_flights/')
    except Flight.DoesNotExist:
        messages.error(request, 'Flight does not exist.')
        return HttpResponseNotFound('Flight does not exist')

# --- Airports ---
@user_passes_test(is_admin)
def show_airports(request):
    airports = Airport.objects.all()
    return render(request, 'show_airports.html', {'airports': airports})

# --- Airports ---
@user_passes_test(is_admin)
def create_airport(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        location = request.POST.get('location')
        contact_info = request.POST.get('contact_info')
        latitude = request.POST.get('latitude') # ДОДАНО
        longitude = request.POST.get('longitude') # ДОДАНО

        airport = Airport.objects.create(
            name=name,
            code=code,
            location=location,
            contact_info=contact_info,
            latitude=latitude if latitude else None, # ДОДАНО, з перевіркою
            longitude=longitude if longitude else None # ДОДАНО, з перевіркою
        )
        airport.save()
        messages.success(request, 'Airport created successfully.')
        return HttpResponseRedirect('/show_airports/')

    return render(request, 'create_airport.html')

@user_passes_test(is_admin)
def update_airport(request, id):
    try:
        airport = Airport.objects.get(pk=id)
        if request.method == 'POST':
            airport.name = request.POST.get('name')
            airport.code = request.POST.get('code')
            airport.location = request.POST.get('location')
            airport.contact_info = request.POST.get('contact_info')
            airport.latitude = request.POST.get('latitude') if request.POST.get('latitude') else None # ДОДАНО
            airport.longitude = request.POST.get('longitude') if request.POST.get('longitude') else None # ДОДАНО
            airport.save()
            messages.success(request, 'Airport updated successfully.')
            return HttpResponseRedirect('/show_airports/')
        else:
            return render(request, 'update_airport.html', {'airport': airport})
    except Airport.DoesNotExist:
        messages.error(request, 'Airport does not exist.')
        return HttpResponseNotFound('Airport does not exist')
@user_passes_test(is_admin)
def delete_airport(request, id):
    try:
        airport = Airport.objects.get(pk=id)
        airport.delete()
        messages.success(request, 'Airport deleted successfully.')
        return HttpResponseRedirect('/show_airports/')
    except Airport.DoesNotExist:
        messages.error(request, 'Airport does not exist.')
        return HttpResponseNotFound('Airport does not exist')

# --- Tickets ---
@user_passes_test(is_admin)
def show_tickets(request):
    tickets = Ticket.objects.select_related('user', 'flight').all()
    return render(request, 'show_tickets.html', {'tickets': tickets})

@user_passes_test(is_admin)
def create_ticket(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        flight_id = request.POST.get('flight')
        seat_number = request.POST.get('seat_number')

        Ticket.objects.create(
            user=User.objects.get(pk=user_id),
            flight=Flight.objects.get(pk=flight_id),
            seat_number=seat_number
        )
        messages.success(request, 'Ticket created successfully.')
        return redirect('show_tickets')
    users = User.objects.all()
    flights = Flight.objects.all()
    return render(request, 'create_ticket.html', {'users': users, 'flights': flights})

@user_passes_test(is_admin)
def update_ticket(request, id):
    ticket = get_object_or_404(Ticket, pk=id)
    if request.method == 'POST':
        ticket.user = User.objects.get(pk=request.POST.get('user'))
        ticket.flight = Flight.objects.get(pk=request.POST.get('flight'))
        ticket.seat_number = request.POST.get('seat_number')
        ticket.save()
        messages.success(request, 'Ticket updated successfully.')
        return redirect('show_tickets')
    users = User.objects.all()
    flights = Flight.objects.all()
    return render(request, 'update_ticket.html', {'ticket': ticket, 'users': users, 'flights': flights})

@user_passes_test(is_admin)
def delete_ticket(request, id):
    ticket = get_object_or_404(Ticket, pk=id)
    ticket.delete()
    messages.success(request, 'Ticket deleted successfully.')
    return redirect('show_tickets')


User = get_user_model() # Переконайтеся, що це тут

# --- Users ---
@user_passes_test(is_admin)
def show_users(request):
    users = User.objects.all()
    return render(request, 'show_users.html', {'users': users})

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('show_users')
    else:
        form = CustomUserForm()
    return render(request, 'create_user.html', {'form': form})

@user_passes_test(is_admin)
def update_user(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('show_users')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user': user})

@user_passes_test(is_admin)
def delete_user(request, id):
    user = get_object_or_404(User, pk=id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('show_users')

# --- Crew Members ---
@user_passes_test(is_admin)
def show_crew_members(request):
    crew_members = CrewMember.objects.all()
    return render(request, 'show_crew_members.html', {'crew_members': crew_members})

@user_passes_test(is_admin)
def create_crew_member(request):
    if request.method == 'POST':
        crew_member = CrewMember()
        crew_member.first_name = request.POST.get('first_name')
        crew_member.last_name = request.POST.get('last_name')
        crew_member.position = request.POST.get('position')
        crew_member.qualification = request.POST.get('qualification')
        crew_member.contact_info = request.POST.get('contact_info')
        crew_member.save()
        messages.success(request, 'Crew member created successfully.')
        return HttpResponseRedirect('/show_crew_members/')
    return render(request, 'create_crew_member.html')

@user_passes_test(is_admin)
def update_crew_member(request, id):
    try:
        crew_member = CrewMember.objects.get(pk=id)
        if request.method == 'POST':
            crew_member.first_name = request.POST.get('first_name')
            crew_member.last_name = request.POST.get('last_name')
            crew_member.position = request.POST.get('position')
            crew_member.qualification = request.POST.get('qualification')
            crew_member.contact_info = request.POST.get('contact_info')
            crew_member.save()
            messages.success(request, 'Crew member updated successfully.')
            return HttpResponseRedirect('/show_crew_members/')
        else:
            return render(request, 'update_crew_member.html', {'crew_member': crew_member})
    except CrewMember.DoesNotExist:
        messages.error(request, 'Crew member does not exist.')
        return HttpResponseNotFound('Crew member does not exist')

@user_passes_test(is_admin)
def delete_crew_member(request, id):
    try:
        crew_member = CrewMember.objects.get(pk=id)
        crew_member.delete()
        messages.success(request, 'Crew member deleted successfully.')
        return HttpResponseRedirect('/show_crew_members/')
    except CrewMember.DoesNotExist:
        messages.error(request, 'Crew member does not exist.')
        return HttpResponseNotFound('Crew member does not exist')


# --- Crew Teams ---
@user_passes_test(is_admin)
def show_crew_teams(request):
    crew_teams = CrewTeam.objects.all()
    return render(request, 'show_crew_teams.html', {'crew_teams': crew_teams})

@user_passes_test(is_admin)
def create_crew_team(request):
    if request.method == 'POST':
        flight_id = request.POST.get('flight')
        member_ids = request.POST.getlist('members')

        flight = Flight.objects.get(pk=flight_id)
        crew_team = CrewTeam.objects.create(flight=flight)
        crew_team.members.set(member_ids)
        crew_team.save()
        messages.success(request, 'Crew team created successfully.')
        return HttpResponseRedirect('/show_crew_teams/')
    flights = Flight.objects.all()
    crew_members = CrewMember.objects.all()
    return render(request, 'create_crew_team.html', {'flights': flights, 'crew_members': crew_members})

@user_passes_test(is_admin)
def update_crew_team(request, id):
    try:
        crew_team = CrewTeam.objects.get(pk=id)
        if request.method == 'POST':
            flight_id = request.POST.get('flight')
            member_ids = request.POST.getlist('members')

            flight = Flight.objects.get(pk=flight_id)
            crew_team.flight = flight
            crew_team.members.set(member_ids)
            crew_team.save()
            messages.success(request, 'Crew team updated successfully.')
            return HttpResponseRedirect('/show_crew_teams/')
        else:
            flights = Flight.objects.all()
            crew_members = CrewMember.objects.all()
            selected_members = crew_team.members.all()
            return render(request, 'update_crew_team.html', {
                'crew_team': crew_team,
                'flights': flights,
                'crew_members': crew_members,
                'selected_members': selected_members
            })
    except CrewTeam.DoesNotExist:
        messages.error(request, 'Crew team does not exist.')
        return HttpResponseNotFound('Crew team does not exist')

@user_passes_test(is_admin)
def delete_crew_team(request, id):
    try:
        crew_team = CrewTeam.objects.get(pk=id)
        crew_team.delete()
        messages.success(request, 'Crew team deleted successfully.')
        return HttpResponseRedirect('/show_crew_teams/')
    except CrewTeam.DoesNotExist:
        messages.error(request, 'Crew team does not exist.')
        return HttpResponseNotFound('Crew team does not exist')

# --- Publicly Accessible Views ---
def public_flights_list(request):
    flights = Flight.objects.all()
    query = request.GET.get('query')
    flight_date_str = request.GET.get('flight_date')

    if flight_date_str:
        try:
            flight_date = datetime.strptime(flight_date_str, '%Y-%m-%d').date()
            flights = flights.filter(departure_time__date=flight_date)
        except ValueError:
            messages.error(request, "Invalid date format. Please use %Y-%m-%d.")

    if query:
        direct_matches = flights.filter(
            Q(flight_number__icontains=query) |
            Q(departure_airport__name__icontains=query) |
            Q(departure_airport__code__icontains=query) |
            Q(arrival_airport__name__icontains=query) |
            Q(arrival_airport__code__icontains=query) |
            Q(airline__name__icontains=query)
        ).distinct()

        if direct_matches.exists():
            flights = direct_matches
        else:
            all_flights = Flight.objects.all()
            fuzzy_results = []
            for flight in all_flights:
                flight_text = f"{flight.flight_number} {flight.departure_airport.name} {flight.departure_airport.code} {flight.arrival_airport.name} {flight.arrival_airport.code} {flight.airline.name}"
                score = fuzz.ratio(query.lower(), flight_text.lower())
                if score > 50:
                    fuzzy_results.append((score, flight))

            fuzzy_results.sort(key=lambda x: x[0], reverse=True)
            flights = [item[1] for item in fuzzy_results]

            if not flights:
                messages.info(request, f"No direct or fuzzy matches found for '{query}'.")

    return render(request, 'flights/public_list.html', {'flights': flights})

@login_required
def book_ticket(request):
    if request.method == 'POST':
        form = TicketBookingForm(request.POST)
        if form.is_valid():
            flight = form.cleaned_data['flight']
            seat_number = form.cleaned_data['seat_number']
            if Ticket.objects.filter(flight=flight, seat_number=seat_number).exists():
                messages.error(request, 'This seat is already taken.')
            else:
                ticket = form.save(commit=False)
                ticket.user = request.user
                ticket.save()
                messages.success(request, 'Your ticket has been successfully booked.')
                return redirect('my_tickets')
    else:
        # If flight_id is passed in GET request, pre-populate the form
        flight_id = request.GET.get('flight_id')
        initial_data = {}
        if flight_id:
            try:
                flight = Flight.objects.get(pk=flight_id)
                initial_data['flight'] = flight
            except Flight.DoesNotExist:
                messages.error(request, 'Selected flight does not exist.')
        form = TicketBookingForm(initial=initial_data)
    return render(request, 'book_ticket.html', {'form': form})

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'profile/my_tickets.html', {'tickets': tickets})

def download_ticket_pdf(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    pdf_buffer = generate_ticket_pdf(ticket)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response

# --- API View for Live Search ---
class FlightSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        flight_date_str = request.GET.get('flight_date')

        flights = Flight.objects.all()

        if flight_date_str:
            try:
                flight_date = datetime.strptime(flight_date_str, '%Y-%m-%d').date()
                flights = flights.filter(departure_time__date=flight_date)
            except ValueError:
                return Response({"error": "Invalid date format. Please use %Y-%m-%d."}, status=status.HTTP_400_BAD_REQUEST)

        if query:
            direct_matches = flights.filter(
                Q(flight_number__icontains=query) |
                Q(departure_airport__name__icontains=query) |
                Q(departure_airport__code__icontains=query) |
                Q(arrival_airport__name__icontains=query) |
                Q(arrival_airport__code__icontains=query) |
                Q(airline__name__icontains=query)
            ).distinct()

            if direct_matches.exists():
                flights = direct_matches
            else:
                all_flights = Flight.objects.all()
                fuzzy_results = []
                for flight in all_flights:
                    flight_text = f"{flight.flight_number} {flight.departure_airport.name} {flight.departure_airport.code} {flight.arrival_airport.name} {flight.arrival_airport.code} {flight.airline.name}"
                    score = fuzz.ratio(query.lower(), flight_text.lower())
                    if score > 50:
                        fuzzy_results.append((score, flight))

                fuzzy_results.sort(key=lambda x: x[0], reverse=True)
                flights = [item[1] for item in fuzzy_results]

        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_map_data(request):
    flights = Flight.objects.select_related(
        'departure_airport', 'arrival_airport'
    ).all()

    # Збираємо унікальні аеропорти
    airports = Airport.objects.filter(
        Q(id__in=flights.values('departure_airport')) |
        Q(id__in=flights.values('arrival_airport'))
    ).distinct()

    flights_data = FlightSerializer(flights, many=True).data
    airports_data = AirportSerializer(airports, many=True).data

    return Response({
        'flights': flights_data,
        'airports': airports_data
    })

def flight_map_view(request): # ДОДАНО
    return render(request, 'flight_map.html')

@user_passes_test(is_admin)
def statistics_view(request):
    return render(request, 'statistics.html')

# --- API для статистики ---
@api_view(['GET'])
@user_passes_test(is_admin) # Доступ тільки для адмінів
def get_statistics_data(request, report_type):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    queryset = Ticket.objects.all() # Базовий queryset, наприклад, для бронювань

    # Фільтрація за періодом
    if start_date_str:
        queryset = queryset.filter(issued_date__gte=start_date_str)
    if end_date_str:
        queryset = queryset.filter(issued_date__lte=end_date_str)

    labels = []
    data = []
    dataset_label = ""
    chart_type = "bar"

    if report_type == 'bookings_by_period':
        # Загальна кількість бронювань за місяцями
        report_data = queryset.annotate(month=TruncMonth('issued_date')).values('month').annotate(count=Count('id')).order_by('month')
        labels = [item['month'].strftime('%Y-%m') for item in report_data]
        data = [item['count'] for item in report_data]
        dataset_label = "Total Bookings"
        chart_type = "line"
    elif report_type == 'bookings_by_airline':
        # Розподіл бронювань за авіалініями
        report_data = queryset.values('flight__airline__name').annotate(count=Count('id')).order_by('-count')
        labels = [item['flight__airline__name'] for item in report_data]
        data = [item['count'] for item in report_data]
        dataset_label = "Bookings by Airline"
        chart_type = "pie" # або "bar"
    elif report_type == 'flight_popularity':
        # Популярність рейсів
        report_data = queryset.values('flight__flight_number').annotate(count=Count('id')).order_by('-count')[:10] # Топ-10
        labels = [item['flight__flight_number'] for item in report_data]
        data = [item['count'] for item in report_data]
        dataset_label = "Flight Popularity (Bookings)"
        chart_type = "bar"
    elif report_type == 'user_activity':
        # Активність користувачів (кількість квитків на користувача)
        report_data = queryset.values('user__username').annotate(count=Count('id')).order_by('-count')[:10]
        labels = [item['user__username'] for item in report_data]
        data = [item['count'] for item in report_data]
        dataset_label = "Tickets per User"
        chart_type = "bar"
    elif report_type == 'cancelled_bookings':
        # Відсоток скасованих бронювань (припускає, що у Ticket є поле 'status' або 'is_cancelled')
        # Якщо Ticket не має поля status, то це не спрацює
        # Якщо немає, можна додати заглушку або реалізувати пізніше
        # Для прикладу, припустимо, що у Ticket є поле 'is_cancelled = models.BooleanField(default=False)'
        # report_data = queryset.aggregate(
        #     total_bookings=Count('id'),
        #     cancelled_bookings=Count('id', filter=Q(is_cancelled=True))
        # )
        # total = report_data.get('total_bookings', 0)
        # cancelled = report_data.get('cancelled_bookings', 0)
        # percentage = (cancelled / total * 100) if total > 0 else 0
        # labels = ["Cancelled", "Active"]
        # data = [cancelled, total - cancelled]
        # dataset_label = "Booking Status"
        # chart_type = "pie"
        messages.warning(request, "Cancelled bookings report not fully implemented without ticket status field.")
        labels = ["N/A"]
        data = [0]
        dataset_label = "N/A"
        chart_type = "bar"
    else:
        return Response({'error': 'Invalid report type'}, status=400)

    return Response({
        'labels': labels,
        'data': data,
        'dataset_label': dataset_label,
        'chart_type': chart_type
    })