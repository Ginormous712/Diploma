# app/data_management/airports.py
import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import Airport # Імпортуємо модель

def export_airports_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="airports.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Code', 'Location', 'Contact Info', 'Latitude', 'Longitude'])
    airports = Airport.objects.all().values_list('id', 'name', 'code', 'location', 'contact_info', 'latitude', 'longitude')
    for airport in airports:
        writer.writerow(airport)
    messages.success(request, 'Airports exported to CSV successfully.')
    return response

def export_airports_excel(request):
    airports = Airport.objects.all()
    data = {
        'ID': [a.id for a in airports],
        'Name': [a.name for a in airports],
        'Code': [a.code for a in airports],
        'Location': [a.location for a in airports],
        'Contact Info': [a.contact_info for a in airports],
        'Latitude': [a.latitude for a in airports],
        'Longitude': [a.longitude for a in airports],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="airports.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Airports')
    messages.success(request, 'Airports exported to Excel successfully.')
    return response

def import_airports(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Airports', 'import_url': reverse('import_airports')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Airports', 'import_url': reverse('import_airports')})
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

            expected_headers = ['Name', 'Code', 'Location', 'Contact Info', 'Latitude', 'Longitude']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Airports', 'import_url': reverse('import_airports')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        name = row[header_map['Name']]
                        code = row[header_map['Code']]
                        location = row[header_map['Location']]
                        contact_info = row[header_map['Contact Info']]
                        latitude = row[header_map['Latitude']] if 'Latitude' in header_map else None
                        longitude = row[header_map['Longitude']] if 'Longitude' in header_map else None

                        if not name or not code:
                            raise ValueError("Name and Code cannot be empty.")

                        if latitude is not None and latitude != '':
                            latitude = float(latitude)
                        else:
                            latitude = None
                        if longitude is not None and longitude != '':
                            longitude = float(longitude)
                        else:
                            longitude = None

                        airport, created = Airport.objects.update_or_create(
                            code=code,
                            defaults={'name': name, 'location': location, 'contact_info': contact_info, 'latitude': latitude, 'longitude': longitude}
                        )
                        if created:
                            num_created += 1
                        else:
                            num_updated += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: {e}")
            if errors:
                messages.warning(request, f"Import finished with {len(errors)} errors. {num_created} created, {num_updated} updated. Details: " + '; '.join(errors[:5]) + ('...' if len(errors) > 5 else ''))
            else:
                messages.success(request, f"Import completed successfully: {num_created} airports created, {num_updated} updated.")
            return redirect('show_airports')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Airports', 'import_url': reverse('import_airports')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Airports', 'import_url': reverse('import_airports')})