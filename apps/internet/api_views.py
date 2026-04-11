from rest_framework import generics, serializers
from .models import ISPContract, ISPOperator


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ISPOperator
        fields = ('id', 'name', 'contact_email', 'contact_phone')


class ISPContractSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    site_name     = serializers.CharField(source='site.name',     read_only=True)
    status        = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model  = ISPContract
        fields = '__all__'


class ISPListView(generics.ListCreateAPIView):
    serializer_class = ISPContractSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = ISPContract.objects.select_related('site', 'operator')
        site_id = self.request.query_params.get('site')
        if site_id:
            qs = qs.filter(site_id=site_id)
        elif not user.is_admin:
            qs = qs.filter(site__in=user.get_accessible_sites())
        return qs.order_by('operator__name')


class ISPDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ISPContractSerializer
    queryset = ISPContract.objects.all()


class OperatorListView(generics.ListAPIView):
    serializer_class = OperatorSerializer
    queryset = ISPOperator.objects.all()
