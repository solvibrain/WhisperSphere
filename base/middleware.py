# This middleware is to debug Sociallogin middleware
class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Called on each request to allow middleware to modify the request, return
        an HttpResponse, or raise an HttpResponseForbidden if the request is
        not allowed to continue.

        :param request: The request object
        :return: The response object or None if the request is not allowed to
                 continue
        """
        print(f"Processing request: {request.path}")
        response = self.get_response(request)
        return response
