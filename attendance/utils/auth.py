from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..models import AttendanceDeviceModel


class DeviceAPIKeyAuthentication(BaseAuthentication):
    """
    Authenticate hardware devices using a device ID + api_key in headers.
    Supports:
      - Authorization header with ApiKey scheme
      - Custom headers: Api-Key, Device-ID
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        api_key = None
        if auth_header.startswith('ApiKey '):
            api_key = auth_header[len('ApiKey '):].strip()
        else:
            api_key = request.headers.get('Api-Key') or request.headers.get('X-API-KEY')
        device_id = request.headers.get('Device-ID') or request.headers.get('X-DEVICE-ID')
        if not api_key or not device_id:
            raise AuthenticationFailed('Missing device credentials (Device-ID and API key required).')
        try:
            device = AttendanceDeviceModel.objects.get(id=device_id)
        except AttendanceDeviceModel.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive device.')
        if not device.check_api_key(api_key):
            raise AuthenticationFailed('Invalid API key.')
        return (device, None)
    def authenticate_header(self, request):
        """
        Called on 401 Unauthorized responses — tells client what scheme to use.
        """
        return 'ApiKey'
