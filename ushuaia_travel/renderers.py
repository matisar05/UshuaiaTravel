from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response is not None and 200 <= response.status_code < 400:
            wrapped = {"success": True, "data": data}
            return super().render(wrapped, accepted_media_type, renderer_context)

        return super().render(data, accepted_media_type, renderer_context)
