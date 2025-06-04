import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import CrewMember # Імпортуємо модель

def export_crew_members_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crew_members.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'First Name', 'Last Name', 'Position', 'Qualification', 'Contact Info'])
    crew_members = CrewMember.objects.all().values_list('id', 'first_name', 'last_name', 'position', 'qualification', 'contact_info')
    for member in crew_members:
        writer.writerow(member)
    messages.success(request, 'Crew members exported to CSV successfully.')
    return response

def export_crew_members_excel(request):
    crew_members = CrewMember.objects.all()
    data = {
        'ID': [cm.id for cm in crew_members],
        'First Name': [cm.first_name for cm in crew_members],
        'Last Name': [cm.last_name for cm in crew_members],
        'Position': [cm.position for cm in crew_members],
        'Qualification': [cm.qualification for cm in crew_members],
        'Contact Info': [cm.contact_info for cm in crew_members],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="crew_members.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Crew Members')
    messages.success(request, 'Crew members exported to Excel successfully.')
    return response

def import_crew_members(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Crew Members', 'import_url': reverse('import_crew_members')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Crew Members', 'import_url': reverse('import_crew_members')})
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

            expected_headers = ['First Name', 'Last Name', 'Position', 'Qualification', 'Contact Info']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Crew Members', 'import_url': reverse('import_crew_members')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        first_name = row[header_map['First Name']]
                        last_name = row[header_map['Last Name']]
                        position = row[header_map['Position']]
                        qualification = row[header_map['Qualification']]
                        contact_info = row[header_map['Contact Info']] if 'Contact Info' in header_map else ''

                        if not first_name or not last_name or not position:
                            raise ValueError("First Name, Last Name, and Position cannot be empty.")

                        crew_member, created = CrewMember.objects.update_or_create(
                            first_name=first_name, # Унікальність за комбінацією імені та прізвища
                            last_name=last_name,
                            defaults={'position': position, 'qualification': qualification, 'contact_info': contact_info}
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
                messages.success(request, f"Import completed successfully: {num_created} crew members created, {num_updated} updated.")
            return redirect('show_crew_members')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Crew Members', 'import_url': reverse('import_crew_members')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Crew Members', 'import_url': reverse('import_crew_members')})