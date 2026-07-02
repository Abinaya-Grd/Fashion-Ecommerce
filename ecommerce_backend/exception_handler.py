from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Something went wrong"

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = response.data["detail"]
            else:
                message = response.data
        else:
            message = response.data

        response.data = {
            "success": False,
            "message": message,
            "errors": response.data
        }

    return response