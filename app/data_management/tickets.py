# app/data_management/tickets.py
import pandas as pd
import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import Ticket, User, Flight # Імпортуємо моделі

def export_tickets_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'User ID', 'Flight ID', 'Seat Number', 'Issued Date'])
    tickets = Ticket.objects.all().values_list('id', 'user_id', 'flight_id', 'seat_number', 'issued_date')
    for ticket in tickets:
        writer.writerow(ticket)
    messages.success(request, 'Tickets exported to CSV successfully.')
    return response

def export_tickets_excel(request):
    tickets = Ticket.objects.all()
    data = {
        'ID': [t.id for t in tickets],
        'User ID': [t.user_id for t in tickets],
        'Flight ID': [t.flight_id for t in tickets],
        'Seat Number': [t.seat_number for t in tickets],
        'Issued Date': [t.issued_date for t in tickets],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tickets.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tickets')
    messages.success(request, 'Tickets exported to Excel successfully.')
    return response

def import_tickets(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Tickets', 'import_url': reverse('import_tickets')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Tickets', 'import_url': reverse('import_tickets')})
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

            expected_headers = ['User ID', 'Flight ID', 'Seat Number']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Tickets', 'import_url': reverse('import_tickets')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        user_id = row[header_map['User ID']]
                        flight_id = row[header_map['Flight ID']]
                        seat_number = row[header_map['Seat Number']]

                        user = User.objects.get(pk=user_id)
                        flight = Flight.objects.get(pk=flight_id)

                        ticket, created = Ticket.objects.update_or_create(
                            user=user, # Унікальність квитка може бути User + Flight + Seat Number
                            flight=flight,
                            seat_number=seat_number,
                            defaults={'user': user, 'flight': flight, 'seat_number': seat_number} # Оновлює існуючий
                        )
                        if created:
                            num_created += 1
                        else:
                            num_updated += 1
                    except User.DoesNotExist:
                        errors.append(f"Row {row_num}: User with ID {user_id} does not exist.")
                    except Flight.DoesNotExist:
                        errors.append(f"Row {row_num}: Flight with ID {flight_id} does not exist.")
                    except Exception as e:
                        errors.append(f"Row {row_num}: An unexpected error - {e}.")
            if errors:
                messages.warning(request, f"Import finished with {len(errors)} errors. {num_created} created, {num_updated} updated. Details: " + '; '.join(errors[:5]) + ('...' if len(errors) > 5 else ''))
            else:
                messages.success(request, f"Import completed successfully: {num_created} tickets created, {num_updated} updated.")
            return redirect('show_tickets')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Tickets', 'import_url': reverse('import_tickets')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Tickets', 'import_url': reverse('import_tickets')})