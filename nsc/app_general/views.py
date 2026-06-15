from django.http import HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponse

from django.shortcuts import render

from .models import Phobias
from .models import Add_pb

from app_general.models import Phobias

from .forms import SelfTestForm

# --------------------------------------------------------------------------- 

def home(request):
    return render(request, 'app_general/home.html')

# --------------------------------------------------------------------------- 

def stat(request):
    phobias = Phobias.objects.all().order_by('name_ENG')
    context = {
        'phobias': phobias
    }
    
    if request.method == 'POST':
        pb_data = request.POST.get('answer')
        if pb_data:
            Add_pb.objects.create(pb_data=pb_data)
    
    return render(request, 'app_general/stat.html', context)

# --------------------------------------------------------------------------- 

def about(request):
    phobias = Phobias.objects.all().order_by('name_ENG')
    context = {
        'phobias': phobias
    }
    return render(request, 'app_general/about.html', context)

# --------------------------------------------------------------------------- 

def self_test(request):
    SCORES = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
    }
    MESSAGES = {
        (0, 9): "ไม่มีอาการของโรคกลัว",
        (10, 19): "โรคกลัวระดับเบา",
        (20, 29): "โรคกลัวระดับปานกลาง",
        (30, 39): "โรคกลัวระดับร้ายแรง",
        (40, 49): "โรคกลัวระดับสุดขีด",
    }
    INFORMATION = {
        (0, 9): "คุณอาจมีความกลัวหรือกังวลเกี่ยวกับสิ่งใดสิ่งหนึ่งบ้าง แต่ความกลัวเหล่านี้ไม่ได้ส่งผลกระทบต่อชีวิตประจำวันของคุณ",
        (10, 19): "ความกลัวหรือกังวลอาจส่งผลกระทบต่อบางสถานการณ์หรือกิจกรรมในชีวิตประจำวัน แต่โดยรวมแล้ว คุณยังสามารถใช้ชีวิตได้ตามปกติ",
        (20, 29): "ความกลัวหรือกังวลส่งผลกระทบต่อหลายสถานการณ์หรือกิจกรรมในชีวิตประจำวัน คุณอาจหลีกเลี่ยงสถานการณ์บางอย่าง หรือมีความวิตกกังวลอย่างมากเมื่อเผชิญกับสิ่งที่กลัว",
        (30, 39): "ความกลัวหรือกังวลส่งผลกระทบต่อชีวิตประจำวันของคุณอย่างมาก คุณอาจไม่สามารถทำงาน ไปโรงเรียน หรือใช้ชีวิตตามปกติได้",
        (40, 49): "คุณอาจกลัวจนถึงขั้นไม่สามารถออกจากบ้าน หรือดูแลตัวเองได้",
    }
    if request.method == 'POST':
        form = SelfTestForm(request.POST)
        if form.is_valid():
            total_score = 0
            
            for key, value in form.cleaned_data.items():
                total_score += SCORES[value]

            for score_range, message in MESSAGES.items():
                if score_range[0] <= total_score <= score_range[1]:
                    result_message = message
                    break

            for score_range, information in INFORMATION.items():
                if score_range[0] <= total_score <= score_range[1]:
                    result_information = information
                    break

            return render(request, 'app_general/self_test_result.html', {'score': total_score, 'message': result_message, 'information': result_information})
    else:
        form = SelfTestForm()
    
    return render(request, 'app_general/self_test.html', {'form': form})