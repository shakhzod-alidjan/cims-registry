from rest_framework import generics, serializers
from .models import CloudServer, CloudProvider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CloudProvider
        fields = ('id', 'name', 'contact_email', 'billing_url')


class CloudServerSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    site_name     = serializers.CharField(source='site.name',     read_only=True)
    spec          = serializers.ReadOnlyField()
    cost_yearly   = serializers.ReadOnlyField()

    class Meta:
        model  = CloudServer
        fields = '__all__'


class CloudServerListView(generics.ListCreateAPIView):
    serializer_class = CloudServerSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = CloudServer.objects.select_related('site', 'provider')
        site_id = self.request.query_params.get('site')
        if site_id:
            qs = qs.filter(site_id=site_id)
        elif not user.is_admin:
            qs = qs.filter(site__in=user.get_accessible_sites())
        return qs.order_by('provider__name', 'name')


class CloudServerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CloudServerSerializer
    queryset = CloudServer.objects.all()


class ProviderListView(generics.ListAPIView):
    serializer_class = ProviderSerializer
    queryset = CloudProvider.objects.all()
