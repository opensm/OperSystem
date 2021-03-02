from django.contrib.contenttypes.models import ContentType
from Rbac.models import DataPermission,Menu
sss = Menu.objects.all()
user_type = ContentType.objects.get(app_label='Rbac', model='userinfo')
user_type.get_object_for_this_type(username='admin1')

t = DataPermission(
    content_object=user_type.get_object_for_this_type(username='test2')
    , tag='test'
)
t.save()

data = DataPermission.objects.filter(tag='test')
data.content_object.get_for_id()
for i in data.content_object.get_cache_name():
    print(i)
