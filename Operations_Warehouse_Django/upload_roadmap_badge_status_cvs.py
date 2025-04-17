# python3 ./upload_roadmap_badge_status_cvs.py

import os
import django
import csv
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Operations_Warehouse_Django.settings')
django.setup()

from integration_badges.models import *

roadmap_set = {}
roadmaps = Integration_Roadmap.objects.all()
for roadmap in roadmaps:
    roadmap_set[roadmap.name] = roadmap


task_set = {}
tasks = Integration_Task.objects.all()
for task in tasks:
    task_set[task.name] = task


badge_set = {}
badge_tasks_set = {}
badges = Integration_Badge.objects.all()
for badge in badges:
    badge_set[badge.name] = badge

    badge_tasks = Integration_Badge_Task.objects.filter(badge_id=badge.badge_id).all()
    badge_tasks_set[badge.name] = badge_tasks


csv_filepath="Roadmap and badge composition of resources - Sheet1.csv"

with open(csv_filepath, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    #print(header)

    Integration_Badge_Task_Workflow.objects.all().delete()
    Integration_Badge_Workflow.objects.all().delete()
    Integration_Resource_Roadmap.objects.all().delete()
    Integration_Resource_Badge.objects.all().delete()

    for row in reader:
        try:
            cider_resource_id = row[len(header) - 1]
            info_resource_id = row[len(header) - 2]
            cider_type = row[len(header) - 3]
            roadmap_name = row[len(header) - 4]

            if cider_type in ["Storage", "Compute"]:
                resource = CiderInfrastructure.objects.get(pk=cider_resource_id)

                # Create and save model instance
                Integration_Resource_Roadmap(
                    info_resourceid=info_resource_id,
                    roadmap_id=roadmap_set[roadmap_name]
                ).save()

                for col_index in range(2, len(header) - 4):
                    badge_name = header[col_index]
                    badge = badge_set[badge_name]

                    if row[col_index] == "Yes":
                        Integration_Resource_Badge(
                            info_resourceid=info_resource_id,
                            roadmap_id=roadmap_set[roadmap_name],
                            badge_id=badge
                        ).save()

                        Integration_Badge_Workflow(
                            info_resourceid=info_resource_id,
                            roadmap_id=roadmap_set[roadmap_name],
                            badge_id=badge,
                            status=BadgeWorkflowStatus.VERIFIED
                        ).save()

                        badge_tasks = badge_tasks_set[badge_name]

                        for badge_task in badge_tasks:
                            task = task_set[badge_task.task_id.name]
                            Integration_Badge_Task_Workflow(
                                info_resourceid=info_resource_id,
                                roadmap_id=roadmap_set[roadmap_name],
                                badge_id=badge,
                                task_id=task,
                                status=BadgeTaskWorkflowStatus.COMPLETED
                            ).save()
        except Exception as e:
            print(f"Error processing row: {row[0]} {row[4]}")

            print(traceback.format_exc())

print(f"{csv_filepath} CSV data processing complete.")

csv_filepath="Proposed Roadmap to Badges Combination - Roadmap-Badge.csv"

with open(csv_filepath, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    #print(header)

    Integration_Roadmap_Badge.objects.all().delete()

    sequence_no = 0
    for row in reader:
        try:
            badge_name = row[0]
            badge = badge_set[badge_name]
            for col_index in range(1, len(header)):
                roadmap_name = header[col_index]
                roadmap = roadmap_set[roadmap_name]
                Integration_Roadmap_Badge(roadmap_id=roadmap, badge_id=badge, sequence_no=sequence_no).save()
        except Exception as e:
            print(f"Error processing row: {row[0]} {row[4]}")

            print(traceback.format_exc())
        sequence_no += 1

    # print("roadmap_set ", roadmap_set)




print(f"{csv_filepath} CSV data processing complete.")



csv_filepath="Proposed Roadmap to Badges Combination - Badge-Prerequisite.csv"

with open(csv_filepath, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    #print(header)

    Integration_Badge_Prerequisite_Badge.objects.all().delete()

    for row in reader:
        try:
            badge_name = row[0]
            badge = badge_set[badge_name]

            sequence_no = 0
            for col_index in range(1, len(header)):
                if row[col_index] == "Yes":
                    prerequisite_badge_name = header[col_index]
                    prerequisite_badge = badge_set[prerequisite_badge_name]
                    Integration_Badge_Prerequisite_Badge(badge_id=badge, prerequisite_badge_id=prerequisite_badge, sequence_no=sequence_no).save()
                sequence_no += 1
        except Exception as e:
            print(f"Error processing row: {row[0]} {row[4]}")

            print(traceback.format_exc())


print(f"{csv_filepath} CSV data processing complete.")
