import os
import glob
import csv
from django.utils.encoding import smart_str
from . import services
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileSerializer


class PhoneApiView(APIView):
    """ Phone API View """

    # serializers_class = FileSerializer

    def get(self, request, format=None):
        """ Returns a list of API features """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="numbers-formatted.csv"'
        response.status_code = status.HTTP_200_OK
        phone = request.GET.get('number')
        list_of_files = glob.glob('./*.csv')
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)

        result = services.locate_nearest_numbers('+'+phone, latest_file)

        writer = csv.writer(response)
        writer.writerow([
            smart_str(u"numbers"),
        ])
        for r in result:
            writer.writerow([
                smart_str(r.numbers),
            ])

        return response


    def post(self, request):
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="numbers-formatted.csv"'
            response.status_code = status.HTTP_200_OK
            result = services.reformat_numbers(file_serializer.data['numbers'])

            writer = csv.writer(response)
            # write the headers
            writer.writerow([
                smart_str(u"numbers"),
                smart_str(u"valid"),
                smart_str(u"location"),
            ])

            for r in result:
                writer.writerow([
                    smart_str(r.numbers),
                    smart_str(r.is_valid),
                    smart_str(r.location),
                ])

            return response
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
