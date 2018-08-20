from .models import Person, RescueCamp, Request
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from .models import RescueCamp, Person, districts
from django.db import connection
from datetime import datetime, timedelta


class RescueCampSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueCamp
        fields = '__all__'

class RescueCampShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueCamp
        fields = ('id', 'name', 'district')

class PersonSerializer(serializers.ModelSerializer):

	class Meta:
		model = Person
		fields = '__all__'

class CampListSerializer(serializers.Serializer):
	district = serializers.CharField()

class RescueCampViewSet(viewsets.ModelViewSet):
    queryset = RescueCamp.objects.filter()
    serializer_class = RescueCampSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'put', 'patch']

    """
        This view should return a list of all the RescueCamp
        for the currently user.
    """
    def get_queryset(self):
        return RescueCamp.objects.order_by('-id')


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.filter()
    serializer_class = PersonSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request):
        for data in request.data:
            serializer = PersonSerializer(data=data)

            data['age'] =  data['age'] or None

            if serializer.is_valid(raise_exception=True):

                camped_at = serializer.validated_data.get('camped_at', None)

                if camped_at :
                    serializer.save()
                else:
                    return Response({'error' : 'Rescue Camp is required field.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':'success','message' : 'Person(s) added'}, status=status.HTTP_201_CREATED)

class CampList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get']

    def get(self, request):

        district = request.GET.get('district', None)

        if district :
            camps = RescueCamp.objects.filter(district=district)
            serializer = RescueCampShortSerializer(camps, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({'error' : 'District Code is Required'}, status=status.HTTP_400_BAD_REQUEST)


# Function for getting database connection and then doing query execution
def execute_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        description = cursor.description
        rows = cursor.fetchall()
        result = [dict(zip([column[0] for column in description], row)) for row in rows]
    return result


class DurationFilter:
    @staticmethod
    def get_interval_value(id):
        duration_dict = {
            'last_1_hr' : "interval '1 hour'",
            'last_3_hrs' : "interval '3 hours'",
            'last_6_hrs' : "interval '6 hours'",
            'last_12_hrs' : "interval '12 hours'",
            'last_24_hrs' : "interval '24 hours'",
            'last_3_days' : "interval '3 days'",
            'last_7_days' : "interval '7 days'"
        }

        return duration_dict[id]

    @staticmethod
    def get_list():
        duration_dict = [
            'last_1_hr',
            'last_3_hrs',
            'last_6_hrs',
            'last_12_hrs',
            'last_24_hrs',
            'last_3_days',
            'last_7_days',
        ]

        return duration_dict

    @staticmethod
    def get_timedelta_value(id):
        duration_dict = {
            'last_1_hr' : timedelta(hours=1),
            'last_3_hrs' : timedelta(hours=3),
            'last_6_hrs' : timedelta(hours=6),
            'last_12_hrs' : timedelta(hours=12),
            'last_24_hrs' : timedelta(hours=24),
            'last_3_days' : timedelta(days=3),
            'last_7_days' : timedelta(days=7),
        }

        return duration_dict[id]



class RequestDashboardDistrictAPI(APIView):
    permission_classes = ()
    http_method_names = ['get']

    def get(self, request):
        try:
            # Get the filter parameters from the request
            params = request.query_params

            if 'district' in params:
                district = params['district']
                district_list = [ d[0] for d in districts ]

                if district  == 'all':
                    district = None

                if district and (district not in district_list):
                    raise ValueError('Invalid district')
            else:
                district = None

            if 'duration' in params:
                duration = params['duration']
                duration_list = [ d[0] for d in districts ]

                if duration  == 'all':
                    duration = None

                if duration and (duration not in DurationFilter.get_list()):
                    raise ValueError('Invalid duration')
            else:
                duration = None
        except Exception as e:
            return Response("Error: %s" % e, status=status.HTTP_400_BAD_REQUEST)

        query = '''
        select district,
            count(*) as count
        from mainapp_request
        where dateadded > now() - %s %s
        group by district
        order by count(*) DESC
        ''' % ( DurationFilter.get_interval_value(duration)  if duration else DurationFilter.get_interval_value('last_7_days'),
        "and district='%s'" % (district)  if district else "",
        )

        result = execute_query(query)

        return Response(result, status=status.HTTP_200_OK)

class RequestDashboardLocationAPI(APIView):
    permission_classes = ()
    http_method_names = ['get']

    def get(self, request):
        try:
            # Get the filter parameters from the request
            params = request.query_params

            if 'district' in params:
                district = params['district']
                district_list = [ d[0] for d in districts ]

                if district  == 'all':
                    district = None

                if district and (district not in district_list):
                    raise ValueError('Invalid district')
            else:
                district = None

            if 'duration' in params:
                duration = params['duration']
                duration_list = [ d[0] for d in districts ]

                if duration  == 'all':
                    duration = None

                if duration and (duration not in DurationFilter.get_list()):
                    raise ValueError('Invalid duration')
            else:
                duration = None
        except Exception as e:
            return Response("Error: %s" % e, status=status.HTTP_400_BAD_REQUEST)


        query = '''
        select location,
            count(*) as count
        from mainapp_request
        where dateadded > now() - %s %s
        group by location
        order by count(*) DESC
        limit 10
        ''' % ( DurationFilter.get_interval_value(duration)  if duration else DurationFilter.get_interval_value('last_7_days'),
        "and district='%s'" % (district)  if district else "",
        )

        result = execute_query(query)

        return Response(result, status=status.HTTP_200_OK)


class RequestDashboardMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('id', 'latlng', 'latlng_accuracy', 'location', 'requestee')


class RequestDashboardMapAPI(APIView):
    permission_classes = ()
    http_method_names = ['get']

    def get(self, request):
        try:
            # Get the filter parameters from the request
            params = request.query_params

            if 'district' in params:
                district = params['district']
                district_list = [ d[0] for d in districts ]

                if district  == 'all':
                    district = None

                if district and (district not in district_list):
                    raise ValueError('Invalid district')
            else:
                district = None

            if 'duration' in params:
                duration = params['duration']
                duration_list = [ d[0] for d in districts ]

                if duration  == 'all':
                    duration = None

                if duration and (duration not in DurationFilter.get_list()):
                    raise ValueError('Invalid duration')
            else:
                duration = None
        except Exception as e:
            return Response("Error: %s" % e, status=status.HTTP_400_BAD_REQUEST)

        result = None
        if district: result = Request.objects.filter(district=district)[:1000]

        if district and duration:
            result = result.filter(dateadded__gte=datetime.now() -
                                    DurationFilter.get_timedelta_value(duration), district=district)[:1000]
        if district: result = Request.objects.filter(district=district)[:1000]
        if duration: result = Request.objects.filter(dateadded__gte=datetime.now() -
                                    DurationFilter.get_timedelta_value(duration))
        if not result:
            result = Request.objects.all()[:1000]

        serializer = RequestDashboardMapSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
