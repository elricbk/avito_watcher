import requests

def retryable_get(url, retry_count=5):
    for i in range(retry_count):
        try:
            r = requests.get(url, timeout=1)
            return r
        except requests.exceptions.RequestException:
            pass
    return None

