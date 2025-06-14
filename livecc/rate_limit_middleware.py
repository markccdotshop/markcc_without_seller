# rate_limit_middleware.py
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.timezone import now
import math

class AdvancedRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Unified rate limits for all environments
        self.rate_limits = {
            # '/cvv/': (20, 60),  # Specific limit for /cvv/ path
            'default': (100, 60),  # Default limit for all other paths
        }

    def __call__(self, request):
        client_ip = request.META.get('REMOTE_ADDR', '')
        path_found = False

        # Find the appropriate rate limit based on the request path
        for path, (limit, period) in self.rate_limits.items():
            if path in request.path:
                path_found = True
                break

        if not path_found:
            limit, period = self.rate_limits['default']

        cache_key = f"rate_limit_{path}_{client_ip}_{math.floor(now().timestamp() / period)}"
        requests = cache.get(cache_key, 0)

        if requests >= limit:
            # If rate limit exceeded, calculate wait time and return 429 response
            response = JsonResponse({'error': 'Too many requests'}, status=429)
            wait_seconds = period - (now().timestamp() % period)
            response['Retry-After'] = int(wait_seconds)
            return response
        else:
            # Increment request count and proceed with the request
            cache.set(cache_key, requests + 1, timeout=period)
            response = self.get_response(request)
            return response
