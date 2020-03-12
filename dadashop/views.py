from django.http import HttpResponse

def test(request):

    return HttpResponse('--cors is ok ---')