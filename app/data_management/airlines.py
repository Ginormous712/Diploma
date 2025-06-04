# app/data_management/airlines.py
import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import Airline # Імпортуємо модель з app.models

def export_airlines_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="airlines.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Country', 'Contact Info'])
    airlines = Airline.objects.all().values_list('id', 'name', 'country', 'contact_info')
    for airline in airlines:
        writer.writerow(airline)
    messages.success(request, 'Airlines exported to CSV successfully.')
    return response

def export_airlines_excel(request):
    airlines = Airline.objects.all()
    data = {
        'ID': [a.id for a in airlines],
        'Name': [a.name for a in airlines],
        'Country': [a.country for a in airlines],
        'Contact Info': [a.contact_info for a in airlines],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="airlines.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Airlines')
    messages.success(request, 'Airlines exported to Excel successfully.')
    return response

def import_airlines(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Airlines', 'import_url': reverse('import_airlines')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Airlines', 'import_url': reverse('import_airlines')})
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

            expected_headers = ['Name', 'Country', 'Contact Info']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Airlines', 'import_url': reverse('import_airlines')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        name = row[header_map['Name']]
                        country = row[header_map['Country']]
                        contact_info = row[header_map['Contact Info']]
                        if not name or not country:
                            raise ValueError("Name and Country cannot be empty.")
                        airline, created = Airline.objects.update_or_create(
                            name=name,
                            defaults={'country': country, 'contact_info': contact_info}
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
                messages.success(request, f"Import completed successfully: {num_created} airlines created, {num_updated} updated.")
            return redirect('show_airlines')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Airlines', 'import_url': reverse('import_airlines')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Airlines', 'import_url': reverse('import_airlines')})