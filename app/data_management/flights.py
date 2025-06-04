# app/data_management/flights.py
import pandas as pd
import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import Flight, Airline, Airport # Імпортуємо моделі

def export_flights_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="flights.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Flight Number', 'Departure Time', 'Arrival Time', 'Status', 'Airline ID', 'Departure Airport ID', 'Arrival Airport ID'])
    flights = Flight.objects.all().values_list('id', 'flight_number', 'departure_time', 'arrival_time', 'status', 'airline_id', 'departure_airport_id', 'arrival_airport_id')
    for flight in flights:
        writer.writerow(flight)
    messages.success(request, 'Flights exported to CSV successfully.')
    return response

def export_flights_excel(request):
    flights = Flight.objects.all()
    data = {
        'ID': [f.id for f in flights],
        'Flight Number': [f.flight_number for f in flights],
        'Departure Time': [f.departure_time for f in flights],
        'Arrival Time': [f.arrival_time for f in flights],
        'Status': [f.status for f in flights],
        'Airline ID': [f.airline_id for f in flights],
        'Departure Airport ID': [f.departure_airport_id for f in flights],
        'Arrival Airport ID': [f.arrival_airport_id for f in flights],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="flights.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Flights')
    messages.success(request, 'Flights exported to Excel successfully.')
    return response

def import_flights(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Flights', 'import_url': reverse('import_flights')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Flights', 'import_url': reverse('import_flights')})
        try:
            if file.name.endswith('.csv'):
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                header = next(reader)
                rows = list(reader)
            elif file.name.endswith('.xlsx'):
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active
                header = [cell.value for cell in sheet[1]]
                rows = []
                for row_data in sheet.iter_rows(min_row=2, values_only=True):
                    rows.append(list(row_data))

            expected_headers = ['Flight Number', 'Departure Time', 'Arrival Time', 'Status', 'Airline ID', 'Departure Airport ID', 'Arrival Airport ID']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Flights', 'import_url': reverse('import_flights')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        flight_number = row[header_map['Flight Number']]
                        departure_time_str = row[header_map['Departure Time']]
                        arrival_time_str = row[header_map['Arrival Time']]
                        status = row[header_map['Status']]
                        airline_id = row[header_map['Airline ID']]
                        departure_airport_id = row[header_map['Departure Airport ID']]
                        arrival_airport_id = row[header_map['Arrival Airport ID']]

                        # Перетворення ID на об'єкти моделей
                        airline = Airline.objects.get(pk=airline_id)
                        departure_airport = Airport.objects.get(pk=departure_airport_id)
                        arrival_airport = Airport.objects.get(pk=arrival_airport_id)

                        departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d %H:%M:%S')
                        arrival_time = datetime.strptime(arrival_time_str, '%Y-%m-%d %H:%M:%S')

                        if not flight_number or not status:
                            raise ValueError("Flight Number and Status cannot be empty.")

                        flight, created = Flight.objects.update_or_create(
                            flight_number=flight_number,
                            defaults={
                                'departure_time': departure_time,
                                'arrival_time': arrival_time,
                                'status': status,
                                'airline': airline,
                                'departure_airport': departure_airport,
                                'arrival_airport': arrival_airport
                            }
                        )
                        if created:
                            num_created += 1
                        else:
                            num_updated += 1
                    except Airline.DoesNotExist:
                        errors.append(f"Row {row_num}: Airline with ID {airline_id} does not exist.")
                    except Airport.DoesNotExist:
                        errors.append(f"Row {row_num}: Airport does not exist for IDs {departure_airport_id} or {arrival_airport_id}.")
                    except ValueError as ve:
                        errors.append(f"Row {row_num}: Data validation error - {ve}.")
                    except Exception as e:
                        errors.append(f"Row {row_num}: An unexpected error - {e}.")
            if errors:
                messages.warning(request, f"Import finished with {len(errors)} errors. {num_created} created, {num_updated} updated. Details: " + '; '.join(errors[:5]) + ('...' if len(errors) > 5 else ''))
            else:
                messages.success(request, f"Import completed successfully: {num_created} flights created, {num_updated} updated.")
            return redirect('show_flights')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Flights', 'import_url': reverse('import_flights')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Flights', 'import_url': reverse('import_flights')})