from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Wrap DRF error responses in a consistent {"detail": ..., "errors": {...}} shape."""
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(response.data, dict) and 'detail' in response.data and len(response.data) == 1:
        response.data = {'detail': response.data['detail'], 'errors': None}
    else:
        response.data = {'detail': 'Validation failed.', 'errors': response.data}
    return response