import csv
import io
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import Upload
from .models import TaskLog
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.db.models import ExpressionWrapper, F, fields, Sum

def upload(request):
    message = ''
    if request.method == "POST":
        form = Upload(request.POST, request.FILES)
        print("Form valid?", form.is_valid()) 
        if form.is_valid():
            try:
                csvfile = form.cleaned_data['csv_file']
                data = csvfile.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(data))

                expected_headers = ['task_name', 'start_time', 'end_time']
                if not all(header in reader.fieldnames for header in expected_headers):
                    message = f"Error: Missing one or more required columns. Expected: {', '.join(expected_headers)}"
                    return render(request, "upload.html", {"form": form, "message": message})
                
                new_logs = []
                for i, row in enumerate(reader):
                    try:
                        task_name = row['task_name'].strip()
                        start_time = parse_datetime(row['start_time'].strip())
                        end_time = parse_datetime(row['end_time'].strip())

                        if not start_time or not end_time:
                            raise ValueError("Invalid datetime format")
                        
                        if start_time >= end_time:
                            raise ValueError("Start time must be before end time")
                        
                        new_logs.append(
                            TaskLog(
                                task_name=task_name,
                                start_time=start_time,
                                end_time=end_time
                            )
                        )
                    except KeyError as ke:
                        message = f"Error on row {i+2}: Missing column '{ke}'"
                        return render(request, "upload.html", {"form": form, "message": message})
                    except ValueError as ve:
                        message = f"Error: Invalid datetime format in CSV row - {ve}"
                        return render(request, "upload.html", {"form": form, "message": message})
                    except Exception as row_e:
                        message = f"Error processing row: {row_e}"
                        return render(request, "upload.html", {"form": form, "message": message})
                    
                TaskLog.objects.bulk_create(new_logs)
                message = f"Upload Successful {len(new_logs)} added"
                return redirect(reverse('dashboard'))
        
            except Exception as e:
                print(f"File upload exception: {e}")
                message = f"Error during file processing: {e}"

        else:
            print("Form errors:", form.errors)
            message = 'Invalid form'
    else: 
        form = Upload()

    return render(request, "upload.html", {"form": form, "message": message})

                    
                
def show_tasks(request):
    tasks = TaskLog.objects.all()
    return render(request, 'show_tasks.html', {'tasks': tasks})

def dashboard(request):
    all_logs = TaskLog.objects.all().order_by('start_time')

    total_time_per_task = {}
    daily_timeline = {}
    idle_time_daily = {}
    overall_idle_time = timedelta(0)

    if all_logs.exists():
        task_durations = all_logs.annotate(
            duration_seconds = ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=fields.DurationField()
            )
        ).values('task_name').annotate(
            total_duration = Sum('duration_seconds')
        ).order_by('task_name')
    
        for entry in task_durations:
            total_time_per_task[entry['task_name']] = entry['total_duration'].total_seconds() / 3600

        for i, current_log in enumerate(all_logs):
            log_date = current_log.start_time.date()
            if log_date not in daily_timeline:
                daily_timeline[log_date] = []
                idle_time_daily[log_date] = timedelta(0)
            
            daily_timeline[log_date].append(current_log)

            if i > 0:
                previous_log = all_logs[i-1]
                
                if previous_log.end_time.date() == current_log.start_time.date():
                    gap = current_log.start_time - previous_log.end_time
                    if gap > timedelta(0):
                        idle_time_daily[log_date] += gap
                        overall_idle_time += gap

        task_labels_json = json.dumps(list(total_time_per_task.keys()))
        task_data_json = json.dumps(list(total_time_per_task.values()))

        sorted_daily_timeline = sorted(daily_timeline.items())

        context = {
            'total_time_per_task': total_time_per_task,
            'daily_timeline': sorted_daily_timeline,
            'idle_time_per_day': idle_time_daily,
            'overall_idle_time': overall_idle_time,
            'task_labels': task_labels_json,
            'task_data': task_data_json,
            'has_data': bool(all_logs),
        }

        return render(request, "dashboard.html", context)