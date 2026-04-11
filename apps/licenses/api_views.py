from rest_framework import generics, serializers
from .models import License, BusinessApp, Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vendor
        fields = ('id', 'name', 'contact_email', 'contact_phone', 'country')


class LicenseSerializer(serializers.ModelSerializer):
    app_name    = serializers.CharField(source='app.name',    read_only=True)
    site_name   = serializers.CharField(source='site.name',   read_only=True)
    vendor_name = serializers.CharField(source='app.vendor.name', read_only=True)
    status      = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    total_cost  = serializers.ReadOnlyField()

    class Meta:
        model  = License
        fields = '__all__'


class BusinessAppSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    class Meta:
        model  = BusinessApp
        fields = ('id', 'name', 'category', 'vendor', 'description')


class LicenseListView(generics.ListCreateAPIView):
    serializer_class = LicenseSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = License.objects.select_related('app', 'site', 'app__vendor')
        site_id = self.request.query_params.get('site')
        if site_id:
            qs = qs.filter(site_id=site_id)
        elif not user.is_admin:
            qs = qs.filter(site__in=user.get_accessible_sites())
        return qs.order_by('app__name', 'license_type')


class LicenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LicenseSerializer
    queryset = License.objects.all()


class BusinessAppListView(generics.ListAPIView):
    serializer_class = BusinessAppSerializer
    queryset = BusinessApp.objects.filter(is_active=True)


class VendorListView(generics.ListAPIView):
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all()
