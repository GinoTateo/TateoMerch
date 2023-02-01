from django.contrib.auth import login
from django.http import request
from rest_framework import permissions, status, generics, viewsets
from rest_framework import views
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from account.models import Account
from api.serializer import UserSerializer, MerchSerializer, StoreSerializer, RequestSerializer, \
    DocketSerializer, RouteSerializer, LoginSerializer
from merch.models import Merch, Request, Docket
from rsr.models import Store, Route



class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [permissions.IsAuthenticated]


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=self.request.data,
                                     context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class MerchView(generics.RetrieveAPIView):
    queryset = Merch.objects.all()
    serializer_class = MerchSerializer


@api_view(['POST'])
def CreateMerchView(request):
    serializer = MerchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreView(generics.RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class RouteView(generics.RetrieveAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class UserRouteView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        userRoute = Route.objects.get(user=request.user)
        ser = RouteSerializer(userRoute)
        return Response(ser.data)


class RequestView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer


@api_view(['POST'])
def PostRequestView(request):
    serializer = RequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocketView(generics.RetrieveAPIView):
    queryset = Docket.objects.all()
    serializer_class = DocketSerializer


@api_view(['POST'])
def CreateDocketView(request):
    serializer = DocketSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
