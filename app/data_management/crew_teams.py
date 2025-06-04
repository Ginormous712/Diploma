import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from ..models import CrewTeam, Flight, CrewMember # Імпортуємо моделі

def export_crew_teams_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crew_teams.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Flight ID', 'Member IDs']) # Member IDs - список ID, розділених комою

    crew_teams = CrewTeam.objects.all()
    for team in crew_teams:
        member_ids = ",".join(str(m.id) for m in team.members.all())
        writer.writerow([team.id, team.flight_id, member_ids])
    messages.success(request, 'Crew Teams exported to CSV successfully.')
    return response

def export_crew_teams_excel(request):
    crew_teams = CrewTeam.objects.all()
    data = {
        'ID': [ct.id for ct in crew_teams],
        'Flight ID': [ct.flight_id for ct in crew_teams],
        'Member IDs': [",".join(str(m.id) for m in ct.members.all()) for ct in crew_teams],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="crew_teams.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Crew Teams')
    messages.success(request, 'Crew Teams exported to Excel successfully.')
    return response

def import_crew_teams(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file uploaded.')
            return render(request, 'import_form.html', {'model_name': 'Crew Teams', 'import_url': reverse('import_crew_teams')})
        if not file.name.endswith(('.csv', '.xlsx')):
            messages.error(request, 'Invalid file format. Only CSV or XLSX files are allowed.')
            return render(request, 'import_form.html', {'model_name': 'Crew Teams', 'import_url': reverse('import_crew_teams')})
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

            expected_headers = ['Flight ID', 'Member IDs']
            if not all(h in header for h in expected_headers):
                messages.error(request, 'Missing required columns in file: ' + ', '.join(h for h in expected_headers if h not in header))
                return render(request, 'import_form.html', {'model_name': 'Crew Teams', 'import_url': reverse('import_crew_teams')})
            header_map = {h: header.index(h) for h in expected_headers}

            num_created = 0
            num_updated = 0
            errors = []
            with transaction.atomic():
                for i, row in enumerate(rows):
                    row_num = i + 2
                    try:
                        flight_id = row[header_map['Flight ID']]
                        member_ids_str = row[header_map['Member IDs']]

                        flight = Flight.objects.get(pk=flight_id)
                        member_ids = [int(x) for x in member_ids_str.split(',') if x.strip()] # Розділяємо ID членів команди
                        members = CrewMember.objects.filter(pk__in=member_ids)

                        if not flight:
                            raise ValueError("Flight ID cannot be empty.")

                        crew_team, created = CrewTeam.objects.update_or_create(
                            flight=flight, # OneToOneField, використовуємо flight як унікальність
                            defaults={'flight': flight}
                        )
                        crew_team.members.set(members) # Встановлюємо членів команди

                        if created:
                            num_created += 1
                        else:
                            num_updated += 1
                    except Flight.DoesNotExist:
                        errors.append(f"Row {row_num}: Flight with ID {flight_id} does not exist.")
                    except CrewMember.DoesNotExist:
                        errors.append(f"Row {row_num}: One or more Crew Members with IDs {member_ids_str} do not exist.")
                    except Exception as e:
                        errors.append(f"Row {row_num}: An unexpected error - {e}.")
            if errors:
                messages.warning(request, f"Import finished with {len(errors)} errors. {num_created} created, {num_updated} updated. Details: " + '; '.join(errors[:5]) + ('...' if len(errors) > 5 else ''))
            else:
                messages.success(request, f"Import completed successfully: {num_created} crew teams created, {num_updated} updated.")
            return redirect('show_crew_teams')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during import: {e}")
            return render(request, 'import_form.html', {'model_name': 'Crew Teams', 'import_url': reverse('import_crew_teams')})
    else:
        return render(request, 'import_form.html', {'model_name': 'Crew Teams', 'import_url': reverse('import_crew_teams')})