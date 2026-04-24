from django.contrib import admin
from .models import User

admin.site.register(User)



from .models import Account

admin.site.register(Account)



from .models import Category

admin.site.register(Category)



from .models import Service

admin.site.register(Service)



from .models import Movement

admin.site.register(Movement)