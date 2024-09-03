from django.shortcuts import render ,redirect 
from .models import *
from django.views.decorators.csrf import csrf_exempt
import http
from django.contrib.auth.decorators import login_required
import subprocess
import speech_recognition as sr
import arabic_reshaper
from django.contrib.auth import authenticate, login ,logout
from django.http import JsonResponse
from django.db.models import Count
from django.http import FileResponse
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
import os
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from google.cloud import speech
from datetime import datetime
import base64
# pages
# Create your views here.
def home(request):
    if request.user.is_superuser:
        User.objects.filter(is_staff=True).exclude(username=request.user.username).update(is_active=False)
        
        # تسجيل الخروج من الحساب الحالي
        logout(request) 
    total_doctors = Users.objects.filter(major__name='doctor').count()
    totalpatient=Patient.objects.count()
    # احسب عدد حسابات الأخصائيين (على سبيل المثال)
    total_Laboratory = Users.objects.filter(major__name='Laboratory').count()
    total_Radiologist= Users.objects.filter(major__name='Radiologist').count()
    radio_technician= Users.objects.filter(major__name='radio technician').count()
    print(total_doctors,totalpatient,total_Laboratory,total_Radiologist)
    context={
        'Patients':totalpatient,
        'Doctors':total_doctors,
        'Radiologist':total_Radiologist,
        'Laboratory':total_Laboratory,
        'radio_technician':radio_technician
    }
    return render(request,'home/home.html',context)

def registerpage(request):
   return render(request,'register/register.html')

@login_required(login_url='login')
def test_images_detailes(request ,date , user_id):
    selected_date = datetime.strptime(date, '%Y %b %d')
    print(selected_date)
    user = Users.objects.get(id = user_id)
    # البحث عن الصور المتعلقة بالتاريخ المحدد
    images = Xray.objects.filter(date_taken=selected_date)

    context = {
        'images': images,
        'user' :user,
        'date':date

    }
    return render(request,'test-images detailes/test-images-detailes.html',context)



def login_page(request):
   return render(request,'login/login.html')
def search_page(request):
    return render(request, 'search page/search.html')
@login_required(login_url='login')
def timelinepage(request, patient_id ,user_id):
    is_major =False
    # الحصول على مريض معين باستخدام معرف المريض
    patient = get_object_or_404(Patient, id=patient_id)
    user= Users.objects.get(id=user_id)
    if user.major.id ==4 :
        is_major=True
    # استرجاع تواريخ الصور الشعاعية وعددها للمريض المحدد
    xray_data = Xray.objects.filter(patient=patient).values('date_taken').annotate(image_count=Count('id'))

    years_with_counts = {}
    
    for data in xray_data:
        year = data['date_taken'].year
        count = data['image_count']
        
        if year not in years_with_counts:
            years_with_counts[year] = []
        
        years_with_counts[year].append({'date': data['date_taken'], 'count': count})
        print('years_with_counts',years_with_counts )

    return render(request, 'timeline/timeline.html', {'years_with_counts': years_with_counts, 'patient': patient , 'is_major':is_major , 'user':user })

#####################################################
#logic
def voicetoText(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='ar-AR')
        reshaped_text = arabic_reshaper.reshape(text)
        print('reshaped_text',reshaped_text)
        with open('audios/path.txt', 'a', encoding='utf-8') as f:
            f.writelines(text + '\n')
        return reshaped_text
    except sr.UnknownValueError as u:
        print(u)
    except sr.RequestError as r:
        print(r)
@csrf_exempt
def send_voice_note(request,xray_id):

    if request.method == 'POST':
        base64_data = request.POST.get('base64', '')
        if base64_data:
            base64_bytes = base64_data.encode('utf-8')
            buffer = base64.b64decode(base64_bytes)
            
            # Create the 'audios' directory if it doesn't exist
            audio_directory = 'audios'
            if not os.path.exists(audio_directory):
                os.makedirs(    audio_directory)
            
            voice_note_webm = os.path.join(audio_directory, f"{datetime.now().timestamp()}.webm")
            with open(voice_note_webm, 'wb') as file:
                file.write(buffer)

            # Convert the webm file to wav using subprocess
            voice_note_wav = voice_note_webm.replace('.webm', '.wav')
            ffmpeg_command = [
                'ffmpeg',
                '-i', voice_note_webm,  # الملف الصوتي الأصلي
                '-acodec', 'pcm_s16le',  # تنسيق الصوت
                '-ar', '16000',  # معدل العينة
                voice_note_wav # اسم الملف المحول
            ]
            subprocess.run(ffmpeg_command)
            
            # Delete the original webm file if needed
            os.remove(voice_note_webm)
            xray = Xray.objects.get(id =xray_id)
            xray.Report = voicetoText(voice_note_wav)
            xray.save()
            
            return JsonResponse({'voiceNote': voice_note_wav})
        else:
            return JsonResponse({'error': 'No base64 data provided.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)
@login_required(login_url='login')
def create_patient_account_for_doctor(request ,doctor_id):
    doctor = Users.objects.get(id = doctor_id)
    
    context={}
    context={
        'user':doctor
        }
    if request.method == 'POST':
        national_number = request.POST['national_number']
        if Patient.objects.filter(national_number=national_number).exists():
            messages.error(request,' الرقم الوطني مكرر')
        if len(national_number) != 14:
                        messages.error(request, 'الرقم الوطني يجب أن يتكون من 14 رقمًا')
        else :
            try:
                patient =Patient.objects.create(
                    full_name = doctor.full_name,
                    birthdate = doctor.birthdate,
                    national_number = national_number,
                    mobile = doctor.mobile,
                    gender = doctor.gender,
                    user = doctor.user

                )
                patient.save()
                return redirect('home_page')
            except IntegrityError as m:
            # إذا كان الرقم الوطني مكررًا، قم بإضافة رسالة خطأ
                messages.error(request,m)
                return render(request,'patient information/patient_information.html',context)

    return render(request,'patient information/patient_information.html',context)

     
@csrf_exempt
def create_patient(request): 
    if request.method == 'POST':
        full_name = request.POST['full_name']
        birthdate = request.POST['birthdate']
        national_number = request.POST['national_number']
        mobile = request.POST['mobile']
        gender = request.POST['gender']
        username=request.POST['username']
        email = request.POST['email']
        password = request.POST['password'] 

        # Create a new User
        user = User.objects.create_user(password=password, email=email, username=username)

        # Create a new Patient
        patient = Patient.objects.create(
            full_name=full_name,
            birthdate=birthdate,
            national_number=national_number,
            mobile=mobile,
            gender=gender,
            user=user
        )
        response_data = {'message': 'Patient created successfully'}
        return JsonResponse(response_data)
    else:
        return "hi"
@login_required(login_url='login')
def search_patient(request):
    if request.method == 'GET':
        national_number = request.GET.get('national_number')

        if national_number:
            try:
                patient = Patient.objects.get(national_number=national_number)
                context={
                    'id':patient.id,
                    'full_name':patient.full_name,
                    'gender':patient.gender,
                    'national_number':patient.national_number
                }
                data = {'success': True, 'context': context}
            except Patient.DoesNotExist:
                data = {'success': False, 'message': 'No results found.'}
        else:
            data = {'success': False, 'message': 'Please enter a National ID Number.'}

        return JsonResponse(data)
@login_required(login_url='login')
def getPatientInfo(request , patient_id):
    
    patient=Patient.objects.get(id=patient_id) 
    double_account= False 
    context={
        'patient':patient,
        'double_account':double_account,
    }
    print('patient',patient)
    return render(request,'patient information/patient_information.html',context)
def getusersInfo(request , user_id):
    print('hiii',user_id)
    user=Users.objects.get(id=user_id)
    double_account= False 
    context={
        'user':user,
        'double_account':double_account,
    }
    return render(request,'patient information/patient_information.html',context)
def getdoctorpatientaccount(request , user_id):
    user = User.objects.get(id=user_id)
    patient = Patient.objects.get(user=user)
    doctor = Users.objects.get(user=user)
    double_account= True
    context={
        'doctor':doctor,
        'patient':patient,
        'double_account':double_account,
    }
    return render(request,'patient information/patient_information.html',context)

@csrf_exempt

def register(request):
    if request.method == 'POST':
        national_number = request.POST.get('national_number')
        fullname = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        birthdate = request.POST.get('birthdate')
        gender_id = request.POST.get('gender')
        account_type = request.POST.get('AccountType')
        major_id = request.POST.get('majorid')
        image = None
        if account_type=='users':
            image = request.FILES['image']

        if len(mobile) != 10:
            messages.error(request, 'رقم الهاتف يجب أن يتكون من 10 أرقام')

        if password != confirm_password:
            messages.error(request, 'كلمة المرور وإعادة كلمة المرور غير متطابقتين')

        try:
            # التحقق من فريدية الحقول (اسم المستخدم والبريد ورقم الهاتف والرقم الوطني)
            if User.objects.filter(username=username).exists():
                messages.error(request, 'اسم المستخدم مكرر. يجب أن يكون فريدًا.')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'البريد الإلكتروني مكرر. يجب أن يكون فريدًا.')

            if account_type == 'patient' and Patient.objects.filter(mobile=mobile).exists():
                messages.error(request, 'رقم الهاتف مكرر. يجب أن يكون فريدًا.')

            if account_type == 'patient' and Patient.objects.filter(national_number=national_number).exists():
                messages.error(request, 'الرقم الوطني مكرر. يجب أن يكون فريدًا.')

            if not any(messages.get_messages(request)):
                # لا توجد أخطاء، يمكنك الاستمرار بإنشاء المستخدم
                user = User.objects.create_user(username=username, email=email, password=password)

                if account_type == 'patient':
                    if len(national_number) != 14:
                        messages.error(request, 'الرقم الوطني يجب أن يتكون من 14 رقمًا')
                         # حذف المستخدم إذا لم يجتز التحقق

                    new_patient = Patient.objects.create(
                        full_name=fullname,
                        birthdate=birthdate,
                        national_number=national_number,
                        mobile=mobile,
                        gender=gender_id,
                        user=user
                    )

                    print('تم إنشاء الحساب بنجاح')

                elif account_type == 'users':
                    if major_id:
                        print(image)
                        major = Major.objects.get(id=major_id)
                        new_user = Users.objects.create(
                            full_name=fullname,
                            birthdate=birthdate,
                            mobile=mobile,
                            user=user,
                            major=major,
                            gender=gender_id,
                            active=False,
                            certificate=image
                        )
                        new_user.save()
                        requests = Request.objects.create(
                            user=user
                        )
                        print(request.POST)
                        print("----------------------------")
                        print(request.FILES)
                        print("----------------------------")
                        print(request.FILES.getlist('image1'))
                        print("----------------------------")
                        print('تم إنشاء الحساب بنجاح')
                        print('تم إنشاء حساب المستخدم بنجاح')

        except IntegrityError as e:
            messages.error(request, 'حدث خطأ غير متوقع أثناء معالجة الطلب. الرجاء المحاولة مرة أخرى.')

    # إذا كان هناك أخطاء، سيتم عرض النموذج مع الأخطاء
    return render(request, 'register/register.html')

@csrf_exempt
def login_view(request):    
    if request.method == 'POST':
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']

        user = None
        if '@' in username_or_email:
            # إذا كان الإدخال يحتوي على علامة '@' ، افترض أنه بريد إلكتروني
            user = authenticate(request, email=username_or_email, password=password)
            randomuser= User.objects.first()
            username = User.objects.get(email=username_or_email)
            user = authenticate(request, username=username, password=password)
        else:
            # إذا لم يحتوي الإدخال على علامة '@' ، افترض أنه اسم مستخدم
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            if user.is_staff:
                login(request,user)
                return redirect('admin:index')
            try :
                if user.patient:
                    login(request,user)
                    total_doctors = Users.objects.filter(major__name='doctor').count()
                    totalpatient=Patient.objects.count()
                    # احسب عدد حسابات الأخصائيين (على سبيل المثال)
                    total_Laboratory = Users.objects.filter(major__name='Laboratory').count()
                    total_Radiologist= Users.objects.filter(major__name='Radiologist').count()
                    radio_technician= Users.objects.filter(major__name='radio technician').count()
                    print(total_doctors,totalpatient,total_Laboratory,total_Radiologist)
                    context={
                        'Patients':totalpatient,
                        'Doctors':total_doctors,
                        'Radiologist':total_Radiologist,
                        'Laboratory':total_Laboratory,
                        'radio_technician':radio_technician
                    }
                    return render(request,'home/home.html',context) 
            except: 
                    print('exept')
                    if user.users.active:  
                        print('exept2')
                        login(request,user)
                        total_doctors = Users.objects.filter(major__name='doctor').count()
                        totalpatient=Patient.objects.count()
                        # احسب عدد حسابات الأخصائيين (على سبيل المثال)
                        total_Laboratory = Users.objects.filter(major__name='Laboratory').count()
                        total_Radiologist= Users.objects.filter(major__name='Radiologist').count()
                        radio_technician= Users.objects.filter(major__name='radio technician').count()
                        print(total_doctors,totalpatient,total_Laboratory,total_Radiologist)
                        context={
                            'Patients':totalpatient,
                            'Doctors':total_doctors,
                            'Radiologist':total_Radiologist,
                            'Laboratory':total_Laboratory,
                            'radio_technician':radio_technician
                        }
                        return render(request,'home/home.html',context)         
                
                    else:
                        messages.error(request, 'حسابك قيد التدقيق. الرجاء الانتظار حتى يتم تنشيط حسابك.')
        else:
            messages.error(request, 'خطأ في اسم المستخدم أو كلمة المرور.')
            return redirect('loginpage')

    return render(request, 'login/login.html')
def logout_view(request,user_id):
    # استخدم وظيفة logout() لتسجيل الخروج
    logout(request)
    # قم بتوجيه المستخدم إلى الصفحة التي تريدها بعد تسجيل الخروج
    return redirect('home_page')
@login_required(login_url='login')
def add_xray(request , patient_id , user_id):
    if request.method == 'POST':
        image = request.FILES['image']
        date_taken = request.POST['date_taken']
        user = Users.objects.get(id = user_id)
        patient = Patient.objects.get(id=patient_id)
        try :
            Xray.objects.create(
                image = image ,
                date_taken= date_taken ,
                doctor= user , 
                patient= patient
            )
        except Exception as m:
            print ('error')
            print(m)
      

    return redirect('timelinex',patient_id=patient_id, user_id=user_id)
def media_view(request, file_path):
    # احصل على المسار الكامل للملف المطلوب
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # تحقق مما إذا كان الملف موجودًا أم لا
    if os.path.exists(full_file_path):
        # إذا كان الملف موجودًا، قم بإرجاعه كاستجابة
        return FileResponse(open(full_file_path, 'rb'))
    else:
        # إذا لم يتم العثور على الملف، قم بإرجاع استجابة 404
        return JsonResponse("الملف غير موجود")
@login_required(login_url='login')
def get_patient_results(patient_id):
    # استرجاع نتائج المريض من قاعدة البيانات وتنظيمها بشكل مناسب
    results = Result.objects.filter(patient_id=patient_id)
    patient_results = {}

    for result in results:
        year = result.date.year
        month = result.date.strftime('%B')
        day = result.date.day

        if year not in patient_results:
            patient_results[year] = {}

        if month not in patient_results[year]:
            patient_results[year][month] = {}

        if day not in patient_results[year][month]:
            patient_results[year][month][day] = []

        patient_results[year][month][day].append(result)

    return patient_results
@login_required(login_url='login')
def analysis_page (request,patient_id):
    patient = Patient.objects.get(id=patient_id)
    print(patient)
    patient_results = get_patient_results(patient)
    for year, months_data in patient_results.items():
        for month, days_data in months_data.items():
            for day, day_results in days_data.items():
                for result in day_results:
                    print(result)
    context={
        'patient':patient,
        'patient_results': patient_results,

    }
    return render(request , 'analysis/analysis.html',context)
@login_required(login_url='login')
def analysis_input(request,patient_id):
    if request.method == 'POST':
        map={}
        list=[]
        keys_with_on = [key for key, value in request.POST.items() if value == 'on']
        analyses_names = keys_with_on 
        for analysis in analyses_names:
            main_analysis = BasicAnalyses.objects.get(name=analysis)
            sub_analyses = BasicAnalyses.objects.filter(its_derivatives=main_analysis)
            map[main_analysis]=sub_analyses
        return render(request, 'result_input/result_input.html', {'analyses_names': map,'patient_id':patient_id})

    Categories_analysis = CategoriesAnalysis.objects.all()
    analyses_map = {}
    for basic_analysis in Categories_analysis:
        sub_analyses = BasicAnalyses.objects.filter(categories_analysis=basic_analysis,its_derivatives=None)
        sub_analyses_list = [sub.name for sub in sub_analyses]
        analyses_map[basic_analysis.name] = sub_analyses_list
    return render(request, 'analysis_input/analysis_input.html', {'analyses_map': analyses_map})
@login_required(login_url='login')
def save_results(request,patient_id):
    if request.method == 'POST':
        testing_users = request.user.users
        testing_patient = Patient.objects.get(id=patient_id)
        result = Result.objects.create(patient=testing_patient, analyst=testing_users)
        all_result = Result.objects.filter(patient=testing_patient).order_by('-analysis_sequence')
        last_value =None
        for analysis_name, result_value in request.POST.items():
            if analysis_name.endswith('_result'):
                analysis = BasicAnalyses.objects.get(name=analysis_name.split('_')[0])
                for result2 in all_result:
                    details = Result_details.objects.filter(analysis_sequence=result2)
                    for item in details:
                        if analysis==item.analysis_number:
                            last_value=item.result
                            break
                    if last_value is  not None:
                        break  
                print( 'last',last_value)                                                  
                Result_details.objects.create(
                        analysis_number=analysis,
                        last_value=last_value,  # يمكنك تعيين قيمة last_value حسب الحاجة
                        result=result_value,
                        analysis_sequence=result
                    )
    return redirect('analysis',patient_id=patient_id)
@login_required(login_url='login')
def result_details(request, result_id):
    map={}
    list=[]
    result = get_object_or_404(Result, analysis_sequence=result_id)
    result_deatils = Result_details.objects.filter (analysis_sequence=result)
    for res in result_deatils :
        list=[]
        if res.analysis_number.its_derivatives is None:
            for res2 in result_deatils:
                if res2.analysis_number.its_derivatives==res.analysis_number:
                    list.append(res2)
            map[res]=list
    print(map)
    return render(request, 'result_details/result_details.html', {'result': result,'map':map})  
@csrf_exempt
@login_required(login_url='login')
def editreport (request , date , user_id,image_id):
    image=Xray.objects.get(id=image_id)
    if request.method=='POST':
        new_report = request.POST.get('new_report')
        image.Report = new_report
        image.save()
        return redirect(request.path)   
    return test_images_detailes(request,date,user_id)
    