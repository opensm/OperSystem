from django.apps import apps as django_apps

menu_class = django_apps.get_model("Rbac.Menu")


# def get_menu(objects, parent=None):
#     if not isinstance(objects, list):
#         raise Exception("")
#     for obj in objects:
#         # 没有父级数据，不为第一级 异常！
#         if not parent and obj.level != 0:
#             continue
#         # 有父级数据，且为第一级 异常！
#         elif parent and obj.level == 0:
#             raise Exception()
#         # 有父级，但是不为第一级 首次判断OK
#         elif parent and obj.level != 0:
#             # 但是类中父级不存在 异常！
#             if not obj.parent:
#                 continue
#             else:
#
