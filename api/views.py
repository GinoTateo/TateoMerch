from django.contrib.auth.decorators import login_required

from merch.models import Merch
from merch.serializer import MerchSerializer
from .models import Account
from rest_framework import viewsets
from rest_framework import permissions
from .serializer import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

class MerchViewSet(viewsets.ModelViewSet):
    queryset = Merch.objects.all()
    serializer_class = MerchSerializer
    permission_classes = [permissions.IsAuthenticated]