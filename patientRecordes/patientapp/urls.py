from django.urls import path,include
from . import views
urlpatterns=[
    path('createPatientAccount/<int:doctor_id>',views.create_patient_account_for_doctor,name='createPatientAccount'),
    path('sendvoice/<int:xray_id>',views.send_voice_note,name='sendvoice'),
    path('',views.home,name='home_page'),
    path('media/<path:file_path>', views.media_view, name='media'),
    path('register/',views.registerpage,name='register'),
    path('loginpage/',views.login_page,name='loginpage'),
    path('login/',views.login_view,name='login'),
    path('logout/<int:user_id>',views.logout_view,name='logout'),
    path('createAccount/',views.register,name='createAccount'),
    path('search/', views.search_page, name='search_page'),
    path('timeline/<int:patient_id>/<int:user_id>/', views.timelinepage, name='timelinex'),
    path('timelinetests/',views.timelinepage,name='timelinetests'),
    path('create_patient/', views.create_patient, name='create_patient'), #tested
    path('search_patient/', views.search_patient, name='search_patient'), #tested    path('logout/', views.logout_view, name='logout'),
    path('test-images-detailes/<str:date>/<int:user_id>', views.test_images_detailes, name='test-images-detailes'),
    path('getpatientinfo/<int:patient_id>/' ,views.getPatientInfo,name='getpationinfo'),
    path('getuserinfo/<int:user_id>/' ,views.getusersInfo,name='getuserInfo'),
    path('addXray /<int:patient_id>/<int:user_id>/',views.add_xray,name='add_xray'),
    path('analysis/<int:patient_id>/',views.analysis_page,name='analysis'),
    path('analysis/input/<int:patient_id>',views.analysis_input,name='analysis_input'),
    path("saveresult/<int:patient_id>",views.save_results,name="save_results"),
    path('result_details/<int:result_id>/',views.result_details, name='result_details'),
    path('editreport/<str:date>/<int:user_id>/<int:image_id>',views.editreport,name='editreport'),
    path('doubleaccount/<int:user_id>',views.getdoctorpatientaccount,name='doubleaccount')

    
]   