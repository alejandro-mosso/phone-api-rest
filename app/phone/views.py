import os
import glob
from itertools import chain
from . import services
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileSerializer


def response_iterator_1(processes, queue, chunk_size):
    chunk = []
    chunk_i = 0
    while 1:
        is_running = any(p.is_alive() for p in processes)
        while not queue.empty() and chunk_i < chunk_size:
            row = queue.get()
            chunk.append(row.numbers + '\n')
            chunk_i = chunk_i+1
        if len(chunk)>0:
            yield ''.join(chunk)

        chunk_i = 0
        chunk = []
        if not is_running:
            break


def response_iterator_2(processes, queue, chunk_size):
    chunk = []
    chunk_i = 0
    while 1:
        is_running = any(p.is_alive() for p in processes)
        while not queue.empty() and chunk_i < chunk_size:
            row = queue.get()
            chunk.append(row.numbers + ',' + str(row.is_valid) + ',' + format_csv_field(row.location) + '\n')
            chunk_i = chunk_i+1
        if len(chunk)>0:
            yield ''.join(chunk)

        chunk_i = 0
        chunk = []
        if not is_running:
            break


def header_1():
    for i in range(1):
        yield 'numbers\n'


def header_2():
    for i in range(1):
        yield 'numbers, valid, location\n'


def format_csv_field(field):
    return f'"{field}"' if field.find(',') > -1 else f'{field}'


class PhoneApiView(APIView):
    """ Phone API View """

    # serializers_class = FileSerializer

    def get(self, request, format=None):
        """ Returns a list of API features """
        response = StreamingHttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="numbers-formatted.csv"'
        response.status_code = status.HTTP_200_OK
        phone = request.GET.get('number')
        list_of_files = glob.glob('./*.csv')
        latest_file = max(list_of_files, key=os.path.getctime)

        result = services.locate_nearest_numbers('+'+phone, latest_file)
        processes = result[1]
        queue = result[0]

        response.streaming_content = chain(header_1(), response_iterator_1(processes, queue, chunk_size=100))

        return response


    def post(self, request):
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            response = StreamingHttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="numbers-formatted.csv"'
            response.status_code = status.HTTP_200_OK
            result = services.reformat_numbers(file_serializer.data['numbers'])

            processes = result[1]
            queue = result[0]

            response.streaming_content = chain(header_2(), response_iterator_2(processes, queue, chunk_size=1000))

            return response
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
