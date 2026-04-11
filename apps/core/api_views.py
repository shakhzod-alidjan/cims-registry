from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Site, User


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Site
        fields = ('id', 'name', 'code', 'color')


class SiteListView(generics.ListAPIView):
    serializer_class = SiteSerializer

    def get_queryset(self):
        return self.request.user.get_accessible_sites()


class UserSerializer(serializers.ModelSerializer):
    sites = SiteSerializer(many=True, read_only=True)
    class Meta:
        model  = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'sites')


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
