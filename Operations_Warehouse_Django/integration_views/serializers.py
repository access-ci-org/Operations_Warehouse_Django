from rest_framework import serializers


class ResourcePivotResponseSerializer(serializers.Serializer):
    """Serializer for Resource Pivot JSON API response"""
    roadmaps = serializers.ListField(child=serializers.DictField())
    selected_roadmap = serializers.IntegerField(allow_null=True)
    pivot_data = serializers.DictField()
    badges_list = serializers.ListField(child=serializers.DictField())
    completed_badges = serializers.IntegerField()
    in_progress_badges = serializers.IntegerField()
    verified_required_count = serializers.IntegerField()
    potential_required_total = serializers.IntegerField()
    potential_percentage = serializers.FloatField()
    preproduction_by_roadmap = serializers.DictField()


class GroupPivotResponseSerializer(serializers.Serializer):
    """Serializer for Group Pivot JSON API response"""
    groups = serializers.ListField(child=serializers.DictField())
    selected_group = serializers.IntegerField(allow_null=True)
    pivot_data = serializers.DictField()
    badges_list = serializers.ListField(child=serializers.DictField())
    completed_badges = serializers.IntegerField()
    in_progress_badges = serializers.IntegerField()
