from apps.core.models import Site


class SiteMiddleware:
    """
    Записывает выбранный объект (site) в request.current_site.
    Если пользователь не выбрал — берёт первый доступный.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_site = None

        if request.user.is_authenticated:
            site_id = request.session.get('current_site_id')
            accessible = request.user.get_accessible_sites()

            if site_id:
                request.current_site = accessible.filter(id=site_id).first()

            if not request.current_site and accessible.exists():
                # 'all' = None means show everything
                pass  # current_site=None → show all

        return self.get_response(request)
