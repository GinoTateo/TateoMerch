from django.http import HttpResponseForbidden
import geoip2.database


class BlockNonLocalIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Load the database (assuming you have a MaxMind database file)
        self.reader = geoip2.database.Reader('/path/to/GeoLite2-Country.mmdb')

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        try:
            response = self.reader.country(ip_address)
            if response.country.iso_code != 'US':  # Assuming you want to block non-US IPs
                return HttpResponseForbidden("Access Denied")
        except geoip2.errors.AddressNotFoundError:
            # IP not found in database, consider how to handle
            pass

        response = self.get_response(request)
        return response

    def close(self):
        self.reader.close()

