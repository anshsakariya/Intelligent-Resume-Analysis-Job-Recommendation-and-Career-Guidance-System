class SecurityHeadersMiddleware:
    """
    Middleware to attach all enterprise security headers to every HTTP response:
    - Content-Security-Policy
    - X-Frame-Options
    - X-Content-Type-Options
    - Referrer-Policy
    - Permissions-Policy
    - Feature-Policy
    - Strict-Transport-Security
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # 1. Content-Security-Policy
        response['Content-Security-Policy'] = (
            "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'; "
            "img-src 'self' https: data: blob:; "
            "font-src 'self' https: data:; "
            "style-src 'self' https: 'unsafe-inline'; "
            "script-src 'self' https: 'unsafe-inline' 'unsafe-eval'; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )

        # 2. X-Frame-Options
        response['X-Frame-Options'] = 'DENY'

        # 3. X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # 4. Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # 5. Permissions-Policy (official standard syntax for SecurityHeaders.com)
        response['Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'

        # 6. Feature-Policy (backward compatibility for security scanners)
        response['Feature-Policy'] = "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'"

        # 7. Strict-Transport-Security
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response
