from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
 
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm

from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

# Create your views here.
@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    return JsonResponse({'message': 'CSRF cookie set'})

@require_http_methods(["POST"])
def login_view(request):
    data = json.loads(request.body.decode("utf-8"))
    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"message": "Invalid credentials"}, status=400)

    login(request, user)
    return JsonResponse({"message": "Logged in successfully"})

def logout_view(request):
    logout(request)
    response = Response({"detail": "Logged out"})
    response.delete_cookie("refresh_token") 
    return response

 
@require_http_methods(['POST'])
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    form = CreateUserForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': 'User registered successfully'}, status=201)
    else:
        errors = form.errors.as_json()
        return JsonResponse({'error': errors}, status=400)

# simpleJWT
class CookieTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "No refresh token"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})
        except Exception:
            raise InvalidToken("Invalid refresh token")
        
class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        u = request.user 
        return Response({
            'id': u.id, 
            'username': u.username
        })