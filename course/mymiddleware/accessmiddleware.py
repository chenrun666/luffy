from django.utils.deprecation import MiddlewareMixin


class CrossDomainMiddleWare(MiddlewareMixin):

    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "*"

        if request.method == "OPTIONS":
            response["Access-Control-Allow-Headers"] = "Content-Type, token"
            response["Access-Control-Allow-Methods"] = "POST, PUT, PATCH, DELETE, GET, HEAD"
        return response
