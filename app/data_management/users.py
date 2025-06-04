# app/data_management/users.py
import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import User # Імпортуємо модель

def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Role', 'First Name', 'Last Name'])
    users = User.objects.all().values_list('id', 'username', 'email', 'role', 'first_name', 'last_name')
    for user in users:
        writer.writerow(user)
    messages.success(request, 'Users exported to CSV successfully.')
    return response

def export_users_excel(request):
    users = User.objects.all()
    data = {
        'ID': [u.id for u in users],
        'Username': [u.username for u in users],
        'Email': [u.email for u in users],
        'Role': [u.role for u in users],
        'First Name': [u.first_name for u in users],
        'Last Name': [u.last_name for u in users],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
    messages.success(request, 'Users exported to Excel successfully.')
    return response

def import_users(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Users', 'import_url': reverse('import_users')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Users', 'import_url': reverse('import_users')})
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

            expected_headers = ['Username', 'Email', 'Role', 'First Name', 'Last Name']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Users', 'import_url': reverse('import_users')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        username = row[header_map['Username']]
                        email = row[header_map['Email']]
                        role = row[header_map['Role']] if 'Role' in header_map else 'registered'
                        first_name = row[header_map['First Name']] if 'First Name' in header_map else ''
                        last_name = row[header_map['Last Name']] if 'Last Name' in header_map else ''

                        if not username or not email:
                            raise ValueError("Username and Email cannot be empty.")

                        user, created = User.objects.update_or_create(
                            username=username,
                            defaults={'email': email, 'role': role, 'first_name': first_name, 'last_name': last_name}
                        )
                        if created:
                            num_created += 1
                        else:
                            num_updated += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: {e}.")
            if errors:
                messages.warning(request, f"Import finished with {len(errors)} errors. {num_created} created, {num_updated} updated. Details: " + '; '.join(errors[:5]) + ('...' if len(errors) > 5 else ''))
            else:
                messages.success(request, f"Import completed successfully: {num_created} users created, {num_updated} updated.")
            return redirect('show_users')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Users', 'import_url': reverse('import_users')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Users', 'import_url': reverse('import_users')})