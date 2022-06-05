from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_406_NOT_ACCEPTABLE

# for proccess csv file
import csv


class ImportContactApi(CreateAPIView):
    permission_classes = []
    def post(self, request, *args, **kwargs):
        feedback = {}
        try:
            data = request.data
            if 'contacts_file' not in data or data['contacts_file'] == "" or not request.FILES['contacts_file']:
                feedback['message'] = "Importing file not found !"
                feedback['status'] = HTTP_204_NO_CONTENT
                return Response(feedback)



            feedback['message'] = "Contacts Imported Successfully"
            feedback['status'] = HTTP_200_OK
            return Response(feedback)

        except Exception as ex:
            feedback['message'] = str(ex)
            feedback['status'] = HTTP_400_BAD_REQUEST
            return Response(feedback)