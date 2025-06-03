from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Airline, Flight, Airport, Ticket, CrewMember, CrewTeam
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomUserForm, TicketBookingForm, RegistrationForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

from .pdf_util import generate_ticket_pdf


def index(request):
    return render(request, 'index.html')




def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'profile_edit.html', {'form': form})

def show_airlines(request):
    airlines = Airline.objects.all()
    return render(request, 'show_airlines.html', {'airlines': airlines})


def create_airline(request):
    if request.method == 'POST':
        airline = Airline()
        airline.name = request.POST.get('name')
        airline.country = request.POST.get('country')
        airline.contact_info = request.POST.get('contact_info')
        airline.save()
        return HttpResponseRedirect('/')

    return render(request, 'create_airline.html')


def update_airline(request, id):
    try:
        airline = Airline.objects.get(pk=id)

        if request.method == 'POST':
            airline.name = request.POST.get('name')
            airline.country = request.POST.get('country')
            airline.contact_info = request.POST.get('contact_info')
            airline.save()
            return HttpResponseRedirect('/')
        else:
            return render(request, "update_airline.html", {'airline': airline})
    except Airline.DoesNotExist:
        return HttpResponseNotFound('Airline does not exist')


def delete_airline(request, id):
    try:
        airline = Airline.objects.get(pk=id)
        airline.delete()
        return HttpResponseRedirect('/')
    except Airline.DoesNotExist:
        return HttpResponseNotFound('Airline does not exist')


def show_flights(request):
    flights = Flight.objects.select_related('airline', 'departure_airport', 'arrival_airport').all()
    return render(request, 'show_flights.html', {'flights': flights})


def create_flight(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        status = request.POST.get('status')

        airline_id = request.POST.get('airline')
        departure_airport_id = request.POST.get('departure_airport')
        arrival_airport_id = request.POST.get('arrival_airport')

        flight = Flight.objects.create(
            flight_number=flight_number,
            departure_time=departure_time,
            arrival_time=arrival_time,
            status=status,
            airline_id=airline_id,
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
        )
        return HttpResponseRedirect('/')

    airlines = Airline.objects.all()
    airports = Airport.objects.all()
    return render(request, "create_flight.html", {
        "airlines": airlines,
        "airports": airports
    })


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
            return HttpResponseRedirect('/flights/')
        else:
            airlines = Airline.objects.all()
            airports = Airport.objects.all()
            return render(request, "update_flight.html", {
                'flight': flight,
                "airlines": airlines,
                "airports": airports
            })
    except Flight.DoesNotExist:
        return HttpResponseNotFound('Flight does not exist')


def delete_flight(request, id):
    try:
        flight = Flight.objects.get(pk=id)
        flight.delete()
        return HttpResponseRedirect('/')
    except Flight.DoesNotExist:
        return HttpResponseNotFound('Flight does not exist')


def show_airports(request):
    airports = Airport.objects.all()
    return render(request, 'show_airports.html', {'airports': airports})

def create_airport(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        location = request.POST.get('location')
        contact_info = request.POST.get('contact_info')

        airport = Airport.objects.create(
            name=name,
            code=code,
            location=location,
            contact_info=contact_info
        )
        airport.save()
        return HttpResponseRedirect('/show_airports/')

    return render(request, 'create_airport.html')


def update_airport(request, id):
    try:
        airport = Airport.objects.get(pk=id)
        if request.method == 'POST':
            airport.name = request.POST.get('name')
            airport.code = request.POST.get('code')
            airport.location = request.POST.get('location')
            airport.contact_info = request.POST.get('contact_info')
            airport.save()
            return HttpResponseRedirect('/show_airports/')
        else:
            return render(request, 'update_airport.html', {'airport': airport})
    except Airport.DoesNotExist:
        return HttpResponseNotFound('Airport does not exist')


def delete_airport(request, id):
    try:
        airport = Airport.objects.get(pk=id)
        airport.delete()
        return HttpResponseRedirect('/show_airports/')
    except Airport.DoesNotExist:
        return HttpResponseNotFound('Airport does not exist')

def show_tickets(request):
    tickets = Ticket.objects.select_related('user', 'flight').all()
    return render(request, 'show_tickets.html', {'tickets': tickets})

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
        return redirect('show_tickets')

    users = User.objects.all()
    flights = Flight.objects.all()
    return render(request, 'create_ticket.html', {'users': users, 'flights': flights})

def update_ticket(request, id):
    ticket = get_object_or_404(Ticket, pk=id)

    if request.method == 'POST':
        ticket.user = User.objects.get(pk=request.POST.get('user'))
        ticket.flight = Flight.objects.get(pk=request.POST.get('flight'))
        ticket.seat_number = request.POST.get('seat_number')
        ticket.save()
        return redirect('show_tickets')

    users = User.objects.all()
    flights = Flight.objects.all()
    return render(request, 'update_ticket.html', {'ticket': ticket, 'users': users, 'flights': flights})

def delete_ticket(request, id):
    ticket = get_object_or_404(Ticket, pk=id)
    ticket.delete()
    return redirect('show_tickets')


User = get_user_model()


def show_users(request):
    users = User.objects.all()
    return render(request, 'show_users.html', {'users': users})


def create_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('show_users')
    else:
        form = CustomUserForm()
    return render(request, 'create_user.html', {'form': form})


def update_user(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('show_users')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user': user})


def delete_user(request, id):
    user = get_object_or_404(User, pk=id)
    user.delete()
    return redirect('show_users')

def show_crew_members(request):
    crew_members = CrewMember.objects.all()
    return render(request, 'show_crew_members.html', {'crew_members': crew_members})

def create_crew_member(request):
    if request.method == 'POST':
        crew_member = CrewMember()
        crew_member.first_name = request.POST.get('first_name')
        crew_member.last_name = request.POST.get('last_name')
        crew_member.position = request.POST.get('position')
        crew_member.qualification = request.POST.get('qualification')
        crew_member.contact_info = request.POST.get('contact_info')
        crew_member.save()
        return HttpResponseRedirect('/crew_members/')

    return render(request, 'create_crew_member.html')

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
            return HttpResponseRedirect('/crew_members/')
        else:
            return render(request, 'update_crew_member.html', {'crew_member': crew_member})
    except CrewMember.DoesNotExist:
        return HttpResponseNotFound('Crew member does not exist')

def delete_crew_member(request, id):
    try:
        crew_member = CrewMember.objects.get(pk=id)
        crew_member.delete()
        return HttpResponseRedirect('/crew_members/')
    except CrewMember.DoesNotExist:
        return HttpResponseNotFound('Crew member does not exist')


def show_crew_teams(request):
    crew_teams = CrewTeam.objects.all()
    return render(request, 'show_crew_teams.html', {'crew_teams': crew_teams})

def create_crew_team(request):
    if request.method == 'POST':
        flight_id = request.POST.get('flight')
        member_ids = request.POST.getlist('members')

        flight = Flight.objects.get(pk=flight_id)
        crew_team = CrewTeam.objects.create(flight=flight)
        crew_team.members.set(member_ids)
        crew_team.save()
        return HttpResponseRedirect('/crew_teams/')

    flights = Flight.objects.all()
    crew_members = CrewMember.objects.all()
    return render(request, 'create_crew_team.html', {'flights': flights, 'crew_members': crew_members})

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
            return HttpResponseRedirect('/crew_teams/')
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
        return HttpResponseNotFound('Crew team does not exist')

def delete_crew_team(request, id):
    try:
        crew_team = CrewTeam.objects.get(pk=id)
        crew_team.delete()
        return HttpResponseRedirect('/crew_teams/')
    except CrewTeam.DoesNotExist:
        return HttpResponseNotFound('Crew team does not exist')


def public_flights_list(request):
    flights = Flight.objects.all()
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
        form = TicketBookingForm()
    return render(request, 'book_ticket.html', {'form': form})

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'profile/my_tickets.html', {'tickets': tickets})

from django.contrib.auth.decorators import login_required

def download_ticket_pdf(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    pdf_buffer = generate_ticket_pdf(ticket)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
    return response
