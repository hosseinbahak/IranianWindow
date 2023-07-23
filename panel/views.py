from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
import requests
from django.contrib.auth.models import Group, User
from rest_framework import status
from .models import Project
from rest_framework import generics
from .models import Project
from .serializers import ProjectSerializer
from datetime import date
from rest_framework import generics, serializers
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from rest_framework.generics import ListAPIView
from django.utils import timezone




def response_func(status: bool ,msg: str, data: dict):
    res = {
        'status': status,
        'message': msg,
        'data': data
    }
    return res 


class RemotePost:
    def __init__(self, username, password):
        self.UserName = username
        self.Password = password


    def Sendsms(self, Number, message, rec, sms):
        url = "http://smspanel.Trez.ir/SendMessageWithPost.ashx"
        payload = {
            'UserName': self.UserName,
            'Password': self.Password,
            'PhoneNumber': Number,
            'MessageBody': message,
            'RecNumber': rec,
            'Smsclass': sms
        }
        response = requests.post(url, data=payload)
        
        # import random
        # from restapi import restfulapi 
        # phonenumber = "9830008632000111"
        # groupId = random.randint(0, 99999999)
        # ws = restfulapi("*****","*****")
        # ws.SendMessage(PhoneNumber=phonenumber,
        # Message="سلام به محمد رستمی از پایتون",
        # Mobiles=['989398219817'],
        # UserGroupID=str(groupId),
        # SendDateInTimeStamp=1558298601)


        if response.status_code == 200:
            # SMS sent successfully
            return response.text
        else:
            # SMS sending failed
            return "SMS sending failed. Status code: {}".format(response.status_code)

            
# print(group)

# # print(group.id, group.name)
# user =User.objects.get(username='hb')
# user.groups.add(group.id)

# #getting all users in specific group

class Authentication(APIView):

    def post(self, request):
        try:
            user = User.objects.get(username__exact=request.data['userName'])
            if check_password(request.data['password'], user.password):

                refresh = RefreshToken.for_user(user)
                

                return Response(response_func(
                        True,
                        "",
                        {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                    ), status=status.HTTP_200_OK
                    ) 
            
            
            return Response(response_func(
                False,
                "رمز عبور اشتباه است",
                None
            ), status=status.HTTP_200_OK
            )
            

        except Exception as e:
            return Response(response_func(
                False,
                "",
                None
            ), status=status.HTTP_401_UNAUTHORIZED
            )



class GetUser(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            return Response(response_func(
                True,
                "user",
                {
                    'userName': request.user.username
                }
            ), status=status.HTTP_200_OK
            )
        
        except:
            return Response(response_func(
                False,
                "",
                {}
            ), status=status.HTTP_401_UNAUTHORIZED
            )




class Sms(generics.GenericAPIView):
    queryset = Group.objects.filter(id=3)
    serializer_class = SmsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the message from the serializer data
        message = serializer.validated_data['message']

        # Rest of your code

        try:
            users_phone = []
            group = Group.objects.get(id=4) 
            users = group.user_set.all()
            
            for user in users:
                users_phone.append(user.username)


            remotePost = RemotePost("Sadegh888", "3726201254")
            state = remotePost.Sendsms("5000248725", message, users_phone , 1)

            return Response(
                response_func(True, "پیام شما پس از تایید سامانه پیامکی برای کاربران ارسال خواهد شد", {'code': state}),  
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                response_func(True, "ارسال پیام با مشکل مواجه شده است", {'error': str(e)}),  
                status=status.HTTP_400_BAD_REQUEST
            )
        

        
class Statistics(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            state_counts = {
                'ongoing': Project.objects.filter(state=0).count(),
                'canceled': Project.objects.filter(state=1).count(),
                'deal': Project.objects.filter(state=2).count(),
            }
        
            return Response(
                    response_func(True, "درخواست موفق", {'data': state_counts}),  
                    status=status.HTTP_200_OK
                )
        
        except Exception as e:
            return Response(
                    response_func(True, "درخواست ناموفق", {'error': str(e)}),  
                    status=status.HTTP_400_BAD_REQUEST
                )
        




class TodayProjectListAPI(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        
        try:

            data = []

            # Get today's date
            today = timezone.now().date()

            # Get projects with check_date matching today's date (ignoring the time component)
            projects = Project.objects.filter(check_date__date=today)
            
            for project in projects:
                data.append({
                        'number': project.employer.username,  # shomare employer
                        'id': project.id,
                        'name': project.employer.first_name,
                        'checked': project.checking
                })


            return Response(response_func(
                True,
                "good",
                data
            ), status=status.HTTP_200_OK)

        except Exception as e:
            return Response(response_func(
                False,
                "failed",
                []
            ), status=status.HTTP_400_BAD_REQUEST)



class NotTrackedProjectListAPI(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        try:
            data = []
            # Get today's date
            today = timezone.now().date()
            
            # Filter projects based on the date part of `check_date`
            projects = Project.objects.filter(state=0, check_date__date__lte=today, checking=False)

            for project in projects:
                data.append({
                    'number': project.employer.username,
                    'id': project.id,
                    'name': project.employer.first_name,
                    'checked': project.checking,
                })

            return Response({
                'success': True,
                'message': 'Projects fetched successfully.',
                'data': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch projects.',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    


class ProjectCreateAPI(APIView):
    # queryset = Project.objects.all()
    # serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)


    def post(self, request):

  
        try:
             
            employee_obj, employee_bool = User.objects.get_or_create(username=request.data['employeeUsername'],
                                                                    first_name = request.data['employeeName']
                                                                        )
            if not request.data['employeeActiveSms']:
                employee_obj.groups.add(4)
        
            employer_obj, employer_bool = User.objects.get_or_create(username=request.data['employerUsername'],
                                                                    first_name = request.data['employerName']
                                                                        )
            if not request.data['employerActiveSms']:
                employer_obj.groups.add(4)

            date = datetime.fromtimestamp(request.data['checkDate']/ 1000)


            project_obj, project_bool  = Project.objects.get_or_create(
                employee = employee_obj,
                employer = employer_obj,
                connection = request.data['connection'],
                check_date = date,
                how_meet = request.data['howMeet'],
                state = request.data['state'],
                level = request.data['level'],
                address = request.data['address'],
                floor = request.data['floors'],
                region = request.data['region'],
                partner = request.data['partner'],
                visit = request.data['visit'],
                in_person = request.data['inPerson'],
                checkout = request.data['checkout'],
                advice = request.data['advice'],
                )

            

            return Response(
                    response_func(True, "درخواست موفق", {'projectId': str(project_obj)}),  
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                    response_func(True, "درخواست ناموفق", {'error': str(e)}),  
                    status=status.HTTP_400_BAD_REQUEST
                )

# {'state': 'ongoing', 
# 'checkout': True, 
#  'visit': False, 
# 'advice': False, 
#  'inPerson': True, 
# 'partner': False, 
#  'level': 'sinas', 
# 'floors': 'adsdsaads', 
# 'address': 'asddas', 
#  'employeeName': 'dasdas', 
# 'employeeUsername': 'dsasa', 
# 'employerName': 'sdadsasad', 
#  'employerUsername': 'dsaasdas', 
# 'howMeet': 'dasddsa', 
#  'region': 'dasddsas', 
# 'connection': 'dasdasds', 
# 'date': 1689935038554}


class ProjectRetrieveAPI(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'projectId'
    permission_classes = (IsAuthenticated,)





class ProjectUpdateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            project = Project.objects.get(id = request.query_params.get('projectId'))


            return Response(response_func(
                True,
                "",
                {
                    'address': project.address,
                    'advice' : project.advice,
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
            ), status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                    response_func(True, "پروژه‌ای وجود ندارد", {'error': str(e)}), 
                    status=status.HTTP_404_NOT_FOUND
                )
    

    def post(self, request, *args, **kwargs):
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

            project.save()

            return Response(
                response_func(
                    True,
                    "ویرایش با موفقیت انجام شد",
                    {}
                ), status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                response_func(False, "ویرایش انجام نشد", {'error': str(e)}),
                status=status.HTTP_404_NOT_FOUND
            )



class ProjectSearch(APIView):
    serializer_class = ProjectSearchSerializer
    permission_classes = (IsAuthenticated,)


    def get(self, request):
        data = []
        project_type = request.GET.get('type')
        search_text = request.GET.get('text')
        if project_type == 'user':
            projects = Project.objects.filter(
                Q(employee__username=search_text) | Q(employer__username=search_text)
                                            )
        elif project_type == 'name':
            projects = Project.objects.filter(
                Q(employee__first_name=search_text) | Q(employer__first_name=search_text)
                                            )
        else:
            projects = Project.objects.none()
        
        serialized_projects = self.serializer_class(projects, many=True)
        
        return Response({'projects': serialized_projects.data})

