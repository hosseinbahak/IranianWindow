from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import datetime
import requests

from .serializers import *
from .models import *

def response_func(status: bool, msg: str, data: dict):
    return {
        'status': status,
        'message': msg,
        'data': data
    }

class RemotePost:
    def __init__(self, username, password):
        self.UserName = username
        self.Password = password

    def send_sms(self, number, message, rec, sms):
        url = "http://smspanel.Trez.ir/SendMessageWithPost.ashx"
        payload = {
            'UserName': self.UserName,
            'Password': self.Password,
            'PhoneNumber': number,
            'MessageBody': message,
            'RecNumber': rec,
            'Smsclass': sms
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.text
        return f"SMS sending failed. Status code: {response.status_code}"

class Authentication(APIView):
    def post(self, request):
        try:
            user = User.objects.get(username=request.data['userName'])
            if check_password(request.data['password'], user.password):
                refresh = RefreshToken.for_user(user)
                return Response(response_func(True, "", {'refresh': str(refresh), 'access': str(refresh.access_token)}), status=status.HTTP_200_OK)
            return Response(response_func(False, "رمز عبور اشتباه است", None), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(response_func(False, "User not found", None), status=status.HTTP_401_UNAUTHORIZED)

class GetUser(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(response_func(True, "user", {'userName': request.user.username}), status=status.HTTP_200_OK)

class Sms(generics.GenericAPIView):
    queryset = Group.objects.filter(id=3)
    serializer_class = SmsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        try:
            users_phone = [user.username for user in Group.objects.get(id=4).user_set.all()]
            remote_post = RemotePost("Sadegh888", "3726201254")
            state = remote_post.send_sms("5000248725", message, users_phone, 1)
            return Response(response_func(True, "پیام شما پس از تایید سامانه پیامکی برای کاربران ارسال خواهد شد", {'code': state}), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, "ارسال پیام با مشکل مواجه شده است", {'error': str(e)}), status=status.HTTP_400_BAD_REQUEST)

class Statistics(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            state_counts = {
                'all': Project.objects.count(),
                'ongoing': Project.objects.filter(state=0).count(),
                'canceled': Project.objects.filter(state=1).count(),
                'deal': Project.objects.filter(state=2).count(),
            }
            return Response(response_func(True, "درخواست موفق", {'data': state_counts}), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, "درخواست ناموفق", {'error': str(e)}), status=status.HTTP_400_BAD_REQUEST)

class TodayProjectListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = []
            today = timezone.now().date()
            historical_records_today = ProjectCheckDateHistory.objects.filter(timestamp__date=today)
            projects_with_today_timestamp = {record.project for record in historical_records_today}

            for project in projects_with_today_timestamp:
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': True
                })

            projects = Project.objects.filter(check_date__date=today).exclude(id__in=[p.id for p in projects_with_today_timestamp])
            for project in projects:
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': False
                })

            return Response(response_func(True, "good", data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, str(e), []), status=status.HTTP_400_BAD_REQUEST)

class NotTrackedProjectListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = []
            today = timezone.now().date()
            projects = Project.objects.filter(state=0, check_date__date__lte=today, checking=False)
            for project in projects:
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': project.checking,
                })

            historical_records_today = ProjectCheckDateHistory.objects.filter(timestamp__date=today)
            for record in historical_records_today:
                project = record.project
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': True
                })

            return Response(response_func(True, "Projects fetched successfully.", data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, "Failed to fetch projects.", []), status=status.HTTP_400_BAD_REQUEST)

class ProjectCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            employee_obj, _ = User.objects.get_or_create(username=request.data['employeeUsername'], first_name=request.data['employeeName'])
            if not request.data['employeeActiveSms']:
                employee_obj.groups.add(4)

            employer_obj, _ = User.objects.get_or_create(username=request.data['employerUsername'], first_name=request.data['employerName'])
            if not request.data['employerActiveSms']:
                employer_obj.groups.add(4)

            check_date = datetime.fromtimestamp(request.data['checkDate'] / 1000)

            project_obj, _ = Project.objects.get_or_create(
                employee=employee_obj,
                employer=employer_obj,
                connection=request.data['connection'],
                check_date=check_date,
                how_meet=request.data['howMeet'],
                state=request.data['state'],
                level=request.data['level'],
                address=request.data['address'],
                floor=request.data['floors'],
                region=request.data['region'],
                partner=request.data['partner'],
                visit=request.data['visit'],
                in_person=request.data['inPerson'],
                checkout=request.data['checkout'],
                advice=request.data['advice']
            )

            return Response(response_func(True, "درخواست موفق", {'projectId': str(project_obj)}), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, "درخواست ناموفق", {'error': str(e)}), status=status.HTTP_400_BAD_REQUEST)

class ProjectRetrieveAPI(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'projectId'
    permission_classes = [IsAuthenticated]

class ProjectUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            project = Project.objects.get(id=request.query_params.get('projectId'))
            data = {
                'address': project.address,
                'advice': project.advice,
                'checkDate': int(project.check_date.timestamp()),
                'checkout': project.checkout,
                'connection': project.connection,
                'employeeActiveSms': bool(project.employee_sms),
                'employeeName': project.employee.first_name,
                'employeeUsername': project.employee.username,
                'employerActiveSms': bool(project.employer),
                'employerName': project.employer.first_name,
                'employerUsername': project.employer.username,
                'floors': project.floor,
                'howMeet': project.how_meet,
                'inPerson': project.in_person,
                'level': project.level,
                'partner': project.partner,
                'region': project.region,
                'state': project.state,
                'visit': project.visit,
            }
            return Response(response_func(True, "", data), status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(response_func(False, "پروژه‌ای وجود ندارد", {'error': "Project not found"}), status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            project = Project.objects.get(id=request.data['projectId'])
            project.address = request.data['address']
            project.advice = request.data['advice']
            project.check_date = datetime.fromtimestamp(request.data['checkDate'] / 1000)
            project.connection = request.data['connection']
            project.employee_sms = request.data['employeeActiveSms']
            project.employee.first_name = request.data['employeeName']
            project.employee.username = request.data['employeeUsername']
            project.employer_sms = request.data['employerActiveSms']
            project.employer.first_name = request.data['employerName']
            project.employer.username = request.data['employerUsername']
            project.floor = request.data['floors']
            project.how_meet = request.data['howMeet']
            project.in_person = request.data['inPerson']
            project.level = request.data['level']
            project.partner = request.data['partner']
            project.region = request.data['region']
            project.state = request.data['state']
            project.visit = request.data['visit']
            project.checking = True
            project.save()

            ProjectCheckDateHistory.objects.create(project=project)

            return Response(response_func(True, "ویرایش با موفقیت انجام شد", {}), status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(response_func(False, "ویرایش انجام نشد", {'error': "Project not found"}), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(response_func(False, "ویرایش انجام نشد", {'error': str(e)}), status=status.HTTP_400_BAD_REQUEST)

class ProjectSearch(APIView):
    serializer_class = ProjectSearchSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = []
        project_type = request.GET.get('type')
        search_text = request.GET.get('text')
        filter_kwargs = {}

        if project_type == 'phone':
            filter_kwargs['Q(employee__username__icontains=search_text) | Q(employer__username__icontains=search_text)'] = search_text
        else:
            filter_kwargs['Q(employee__first_name__icontains=search_text) | Q(employer__first_name__icontains=search_text)'] = search_text

        try:
            projects = Project.objects.filter(**filter_kwargs)
            for project in projects:
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': project.checking
                })
            return Response(response_func(True, "good", data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response_func(False, "failed", []), status=status.HTTP_400_BAD_REQUEST)
