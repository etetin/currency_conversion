
def api_views(methods):
    def decorator(func):
        class Handler:
            @staticmethod
            def can_handle(request):
                if request.path == 'ping':
                    if request.method in methods:
                        return True
                    else:
                        # TODO method not allowed
                        return False

                return False

            @staticmethod
            def handle(request):
                return func(request)

        return func

    return decorator
