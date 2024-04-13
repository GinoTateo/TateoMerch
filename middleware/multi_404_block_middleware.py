from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import redis

class IPBlockMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)  # Configure as needed

    def process_response(self, request, response):
        if response.status_code == 404:
            ip = request.META.get('REMOTE_ADDR')
            # Increment the count for this IP
            count = self.redis.incr(ip)
            # Set a timeout for the counter (e.g., 10 minutes)
            self.redis.expire(ip, 600)
            # Check if the IP should be blocked
            if count > 10:  # Threshold for blocking
                response = HttpResponse("Blocked", status=403)
        return response
