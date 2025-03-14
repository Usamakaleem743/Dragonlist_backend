from django.http import JsonResponse
from rest_framework import status

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Handle different types of exceptions
        if isinstance(exception, ValueError):
            return JsonResponse({
                'error': 'Invalid input provided',
                'detail': str(exception)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(exception, PermissionError):
            return JsonResponse({
                'error': 'Permission denied',
                'detail': str(exception)
            }, status=status.HTTP_403_FORBIDDEN)

        # Handle any other unexpected errors
        return JsonResponse({
            'error': 'Internal server error',
            'detail': str(exception)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 