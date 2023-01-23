from datetime import datetime

from django.contrib import admin

from rsr.models import Store, Display, ServiceSchedule, Route

admin.site.register(Store)
admin.site.register(Display)
admin.site.register(ServiceSchedule)
admin.site.register(Route)
