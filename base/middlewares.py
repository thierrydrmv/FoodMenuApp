import time

from django.http import HttpResponseForbidden


class LogRequestMiddleware:
    def __init__(self, get_respose):
        self.get_response = get_respose

    def __call__(self, request):
        # before view
        print(f"[Middleware] Request Path:{request.path}")
        response = self.get_response(request)
        # after view
        print(f"[Middleware] response Status: {response.status_code}")
        return response


class TimerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        print(f"[Middleware] Request took: {duration:.2f} seconds")
        return response


class BlockIPMiddleware:
    BLOCKIPS = [""]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        if ip in self.BLOCKIPS:
            return HttpResponseForbidden("Your IP is blocked!")
        return self.get_response(request)
