from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),

    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/profile/edit/', views.profile_edit, name='profile_edit'),
    path('tickets/my/', views.my_tickets, name='my_tickets'),
    path('tickets/download/<int:ticket_id>/', views.download_ticket_pdf, name='download_ticket_pdf'),




    # Airlines
    path('show_airlines/', views.show_airlines, name='show_airlines'),
    path('show_airlines/create_airline/', views.create_airline, name='create_airline'),
    path('show_airlines/update_airline/<int:id>/', views.update_airline, name='update_airline'),
    path('show_airlines/delete_airline/<int:id>/', views.delete_airline, name='delete_airline'),

    # Flights
    path('show_flights/', views.show_flights, name='show_flights'),
    path('show_flights/create_flight/', views.create_flight, name='create_flight'),
    path('show_flights/update_flight/<int:id>/', views.update_flight, name='update_flight'),
    path('show_flights/delete_flight/<int:id>/', views.delete_flight, name='delete_flight'),

    # Airports
    path('show_airports/', views.show_airports, name='show_airports'),
    path('show_airports/create_airport/', views.create_airport, name='create_airport'),
    path('show_airports/update_airport/<int:id>/', views.update_airport, name='update_airport'),
    path('show_airports/delete_airport/<int:id>/', views.delete_airport, name='delete_airport'),

    # Tickets
    path('show_tickets/', views.show_tickets, name='show_tickets'),
    path('show_tickets/create_ticket/', views.create_ticket, name='create_ticket'),
    path('show_tickets/update_ticket/<int:id>/', views.update_ticket, name='update_ticket'),
    path('show_tickets/delete_ticket/<int:id>/', views.delete_ticket, name='delete_ticket'),

    # Users
    path('show_users/', views.show_users, name='show_users'),
    path('show_users/create_user/', views.create_user, name='create_user'),
    path('show_users/update_user/<int:id>/', views.update_user, name='update_user'),
    path('show_users/delete_user/<int:id>/', views.delete_user, name='delete_user'),

    # Crew Members
    path('show_crew_members/', views.show_crew_members, name='show_crew_members'),
    path('show_crew_members/create_crew_member/', views.create_crew_member, name='create_crew_member'),
    path('show_crew_members/update_crew_member/<int:id>/', views.update_crew_member, name='update_crew_member'),
    path('show_crew_members/delete_crew_member/<int:id>/', views.delete_crew_member, name='delete_crew_member'),

    # Crew Teams
    path('show_crew_teams/', views.show_crew_teams, name='show_crew_teams'),
    path('show_crew_teams/create_crew_team/', views.create_crew_team, name='create_crew_team'),
    path('show_crew_teams/update_crew_team/<int:id>/', views.update_crew_team, name='update_crew_team'),
    path('show_crew_teams/delete_crew_team/<int:id>/', views.delete_crew_team, name='delete_crew_team'),

    path('flights/public/', views.public_flights_list, name='public_flights'),
    path('tickets/book/', views.book_ticket, name='book_ticket'),
]
