def get_response(message="", result={}, status=False, status_code=200):
    return {
        "message": message,
        "result": result,
        "status": status,
        "status_code": status_code,
    }
