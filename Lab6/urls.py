from django.contrib import admin
from django.urls import path, include
from app import views
from app.views import FlightSearchView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

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
    # Експорт/Імпорт
    path('show_airlines/export_csv/', views.wrapped_export_airlines_csv, name='export_airlines_csv'),
    path('show_airlines/export_excel/', views.wrapped_export_airlines_excel, name='export_airlines_excel'),
    path('show_airlines/import/', views.wrapped_import_airlines, name='import_airlines'),

    # Flights
    path('show_flights/', views.show_flights, name='show_flights'),
    path('show_flights/create_flight/', views.create_flight, name='create_flight'),
    path('show_flights/update_flight/<int:id>/', views.update_flight, name='update_flight'),
    path('show_flights/delete_flight/<int:id>/', views.delete_flight, name='delete_flight'),
    # Експорт/Імпорт
    path('show_flights/export_csv/', views.wrapped_export_flights_csv, name='export_flights_csv'),
    path('show_flights/export_excel/', views.wrapped_export_flights_excel, name='export_flights_excel'),
    path('show_flights/import/', views.wrapped_import_flights, name='import_flights'),

    # Airports
    path('show_airports/', views.show_airports, name='show_airports'),
    path('show_airports/create_airport/', views.create_airport, name='create_airport'),
    path('show_airports/update_airport/<int:id>/', views.update_airport, name='update_airport'),
    path('show_airports/delete_airport/<int:id>/', views.delete_airport, name='delete_airport'),
    # Експорт/Імпорт
    path('show_airports/export_csv/', views.wrapped_export_airports_csv, name='export_airports_csv'),
    path('show_airports/export_excel/', views.wrapped_export_airports_excel, name='export_airports_excel'),
    path('show_airports/import/', views.wrapped_import_airports, name='import_airports'),

    # Tickets
    path('show_tickets/', views.show_tickets, name='show_tickets'),
    path('show_tickets/create_ticket/', views.create_ticket, name='create_ticket'),
    path('show_tickets/update_ticket/<int:id>/', views.update_ticket, name='update_ticket'),
    path('show_tickets/delete_ticket/<int:id>/', views.delete_ticket, name='delete_ticket'),
    # Експорт/Імпорт
    path('show_tickets/export_csv/', views.wrapped_export_tickets_csv, name='export_tickets_csv'),
    path('show_tickets/export_excel/', views.wrapped_export_tickets_excel, name='export_tickets_excel'),
    path('show_tickets/import/', views.wrapped_import_tickets, name='import_tickets'),

    # Users
    path('show_users/', views.show_users, name='show_users'),
    path('show_users/create_user/', views.create_user, name='create_user'),
    path('show_users/update_user/<int:id>/', views.update_user, name='update_user'),
    path('show_users/delete_user/<int:id>/', views.delete_user, name='delete_user'),
    # Експорт/Імпорт
    path('show_users/export_csv/', views.wrapped_export_users_csv, name='export_users_csv'),
    path('show_users/export_excel/', views.wrapped_export_users_excel, name='export_users_excel'),
    path('show_users/import/', views.wrapped_import_users, name='import_users'),

    # Crew Members
    path('show_crew_members/', views.show_crew_members, name='show_crew_members'),
    path('show_crew_members/create_crew_member/', views.create_crew_member, name='create_crew_member'),
    path('show_crew_members/update_crew_member/<int:id>/', views.update_crew_member, name='update_crew_member'),
    path('show_crew_members/delete_crew_member/<int:id>/', views.delete_crew_member, name='delete_crew_member'),
    # Експорт/Імпорт
    path('show_crew_members/export_csv/', views.wrapped_export_crew_members_csv, name='export_crew_members_csv'),
    path('show_crew_members/export_excel/', views.wrapped_export_crew_members_excel, name='export_crew_members_excel'),
    path('show_crew_members/import/', views.wrapped_import_crew_members, name='import_crew_members'),

    # Crew Teams
    path('show_crew_teams/', views.show_crew_teams, name='show_crew_teams'),
    path('show_crew_teams/create_crew_team/', views.create_crew_team, name='create_crew_team'),
    path('show_crew_teams/update_crew_team/<int:id>/', views.update_crew_team, name='update_crew_team'),
    path('show_crew_teams/delete_crew_team/<int:id>/', views.delete_crew_team, name='delete_crew_team'),
    # Експорт/Імпорт
    path('show_crew_teams/export_csv/', views.wrapped_export_crew_teams_csv, name='export_crew_teams_csv'),
    path('show_crew_teams/export_excel/', views.wrapped_export_crew_teams_excel, name='export_crew_teams_excel'),
    path('show_crew_teams/import/', views.wrapped_import_crew_teams, name='import_crew_teams'),


    path('flights/public/', views.public_flights_list, name='public_flights'),
    path('tickets/book/', views.book_ticket, name='book_ticket'),

    # API для пошуку рейсів
    path('api/flights/search/', FlightSearchView.as_view(), name='api_flight_search'),

    # URL для отримання даних мапи
    path('api/map-data/', views.get_map_data, name='api_map_data'),

    # URL для сторінки мапи
    path('flight_map/', views.flight_map_view, name='flight_map'),

    # Admin Tools View (централізована сторінка імпорту/експорту)
    path('admin_tools/', views.admin_tools_view, name='admin_tools_view'),

    # DRF Spectacular URLs # ДОДАНО
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('statistics/', views.statistics_view, name='statistics_view'), # Сторінка зі статистикою
    path('api/statistics/<str:report_type>/', views.get_statistics_data, name='api_statistics_data'), # API для даних статистики

]