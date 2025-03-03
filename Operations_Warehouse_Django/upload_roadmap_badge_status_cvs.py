# python3 ./upload_roadmap_badge_status_cvs.py

import os
import django
import csv
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Operations_Warehouse_Django.settings')
django.setup()

from integration_badges.models import *

csv_filepath="Roadmap and badge composition of resources - Sheet1.csv"

with open(csv_filepath, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    #print(header)

    badge_set = {}
    badge_tasks_set = {}
    for col_index in range(5, len(header)):
        badge_name = header[col_index]
        badge = Integration_Badge.objects.filter(name=badge_name).first()
        if badge is not None:
            print(f"YES - {badge.badge_id} {header[col_index]}")
            badge_set[col_index] = badge

            badge_tasks = Integration_Badge_Task.objects.filter(badge_id=badge.badge_id).all()
            badge_tasks_set[col_index] = badge_tasks
        else:
            print(f"No  -  {header[col_index]}")

    # print("badge_set ", badge_set)

    roadmap_set = {}
    roadmaps = Integration_Roadmap.objects.all()
    for roadmap in roadmaps:
        roadmap_set[roadmap.name] = roadmap

    # print("roadmap_set ", roadmap_set)


    task_set = {}
    tasks = Integration_Task.objects.all()
    for task in tasks:
        task_set[task.task_id] = task

    # print("task_set ", task_set)

    Integration_Badge_Task_Workflow.objects.all().delete()
    Integration_Badge_Workflow.objects.all().delete()
    Integration_Resource_Roadmap.objects.all().delete()
    Integration_Resource_Badge.objects.all().delete()

    for row in reader:
        try:
            cider_resource_id = row[0]
            info_resource_id = row[1]
            cider_type = row[2]
            roadmap_name = row[4]

            if cider_type in ["Storage", "Compute"]:
                resource = CiderInfrastructure.objects.get(pk=cider_resource_id)

                # Create and save model instance
                Integration_Resource_Roadmap(
                    resource_id=resource,
                    roadmap_id=roadmap_set[roadmap_name]
                ).save()

                for col_index in range(5, len(header)):
                    badge = badge_set[col_index]

                    if row[col_index] == "Yes":
                        Integration_Badge_Workflow(
                            resource_id=resource,
                            badge_id=badge,
                            status=BadgeWorkflowStatus.VERIFIED
                        ).save()

                        badge_tasks = badge_tasks_set[col_index]

                        for badge_task in badge_tasks:
                            task = task_set[badge_task.task_id.task_id]
                            Integration_Badge_Task_Workflow(
                                resource_id=resource,
                                badge_id=badge,
                                task_id=task,
                                status=BadgeTaskWorkflowStatus.COMPLETED
                            ).save()
        except Exception as e:
            print(f"Error processing row: {row[0]} {row[4]}")

            print(traceback.format_exc())

print("CSV data processing complete.")