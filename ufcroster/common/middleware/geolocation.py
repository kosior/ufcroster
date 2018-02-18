from ..utils import get_ip_from_meta, get_data_from_freegeoip


class GeolocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip_meta = get_ip_from_meta(request)
        user_ip_session = request.session.get('ip')

        if not user_ip_session or user_ip_meta != user_ip_session:
            user_data = get_data_from_freegeoip(user_ip_meta)
            for key, value in user_data.items():
                request.session[key] = value

        response = self.get_response(request)
        return response
