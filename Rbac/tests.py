from django.contrib.contenttypes.models import ContentType
user_type = ContentType.objects.get(app_label='Rbac', model='userinfo')
user_type.get_all_objects_for_this_type(is_superuser=0)
