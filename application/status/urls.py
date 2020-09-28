from django.urls import path
from status.views.ok import Ok
from status.views.db_create import DBCreate
from status.views.processor_status import processor_log, processor_log_delete, processor_log_item

urlpatterns = [
    path('ok/', Ok.as_view(), name='ok'),
    path('db/create/', DBCreate.as_view(), name='db-create'),
    path('processor-log/', processor_log, name='processor-log'),
    path('processor-log/delete/<uuid:id>/', processor_log_delete, name='processor-log-delete'),
    path('api/processor-log/item', processor_log_item, name='processor-log-item'),
]
