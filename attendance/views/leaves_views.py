from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response




@api_view(["GET"])
def test_func(request):
    return Response({"message": "Test function works!"}, status=status.HTTP_200_OK)

