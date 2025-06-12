from django.shortcuts import render
from .models import User 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.db.models import Q
from config.paging import CustomPagination

################# User #################
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # 이메일 중복 체크
    if User.objects.filter(email=email).exists():
        return Response({"message": "이미 사용 중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(password)  # 🔹 비밀번호 해싱 적용
        user.is_active=True  # 🔹 비밀번호 해싱 적용
        user.save()
        
        return Response({"message": "회원가입 성공!", "user": serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    token = request.data.get('token')

    if not token:
        return Response({"message": "토큰이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        AccessToken(token)  # 토큰 유효성 검증, 만료 여부 체크
        return Response({"message": "유효한 토큰입니다."}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({"message": f"유효하지 않은 토큰입니다: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "회원가입을 진행해주세요."})

    # 비밀번호 확인 로직 필요 (예: request.data.get('password'))
    # 생략된 경우 anyone can login just by email!

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'email': user.email,
        'name': user.name,
        'tel': user.tel_first,  # 또는 user.tel 이나 필요한 필드
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_page(request) :
    serializer = UserSerializer(request.user)
    
    data = serializer.data
    
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def my_edit(request) :
    user = request.user  # 본인 기준으로만 수정 가능

    user.name = request.data.get("name", user.name)
    user.tel_first = request.data.get("tel", user.tel_first)
    user.save()

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

################# admin #################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_data(request):
    if not request.user.is_staff:
        return Response({"detail": "관리자가 아닙니다."}, status=status.HTTP_403_FORBIDDEN)
    paginator = CustomPagination()

    filters = Q()
    create_at = request.GET.get("create_at")
    email = request.GET.get("email")
    name = request.GET.get("name")
    
    if email:
        filters &= Q(email__icontains=email) | Q(tel_first__icontains=email)  # 필터 수정

    if create_at:
        filters &= Q(sign_in__icontains=create_at)  # 날짜 필터 수정

    if name:
        filters &= Q(name__icontains=name)  # 날짜 필터 수정
    
    total_user = User.objects.filter(filters)

    result_page = paginator.paginate_queryset(total_user, request)
    serializer = UserSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)
