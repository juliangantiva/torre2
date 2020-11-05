from django.shortcuts import render
from django.http import JsonResponse, Http404
import json
import requests

#from .models import Opportunity
from .models_objects import Job, Salary
from .get_job_info import get_job_info
from .check_user_data import check_user_data

# https://torre.bio/api/bios/$username (gets bio information of $username)
# - GET https://torre.bio/api/people/$username/network?[deep=$limit] (lists people sorted by connection degrees relative to $username)
# - GET https://torre.co/api/opportunities/$id (gets job information of $id)
# - POST https://search.torre.co/opportunities/_search/?[offset=$offset&size=$size&aggregate=$aggregate] 
# and https://search.torre.co/people/_search/?[offset=$offset&size=$size&aggregate=$aggregate] (search for jobs and people in general, you can see how it's being used here: https://torre.co/search).



def list_jobs(request):

    size = 10
    offset = 0
    endpoint_jobs = 'https://search.torre.co/opportunities/_search/?size={}&offset={}&aggregate=false'.format(size,offset)
    
    
    data = requests.post(endpoint_jobs).json()

    jobs_list = data['results']
    opportunities = []
    for job in jobs_list:

        #status     = job['status'] # open
        title       = job['objective']
        code        = job['id']
        opportunity = job['type']
        remote      = job['remote']
        locations   = job['locations'] # it's a list

        companies_list = job['organizations'] # it's a list
        companies = []
        for comp in companies_list:
            companies.insert(0, comp['name'])

        salary_info = job['compensation']
        salary_obj = None
        if not salary_info == None:
            salary_data = salary_info['data']
            if not salary_data == None:
                code_salary= salary_data['code']
                currency   = salary_data['currency']
                min_amount = salary_data['minAmount']
                max_amount = salary_data['maxAmount']
                periodicity= salary_data['periodicity']
                visible    = salary_info['visible']
                
                salary_obj = Salary(code=code_salary, currency=currency, min_amount=min_amount, max_amount=max_amount, periodicity=periodicity, visible=visible)

        job_obj = Job(title=title, code=code, opportunity=opportunity, companies=companies, remote=remote, locations=locations, salary=salary_obj)

        opportunities.insert(0, job_obj)


    #opportunities = Opportunity.objects.filter(active=True).all().order_by('-id')

    context = {
        'opportunities': opportunities,
	}

    return render(request, 'show_info.html', context)

 

def get_job(request):
    if request.is_ajax():
        job_id = request.GET.get('code')
        
        job_obj = get_job_info(job_id)
        if not job_obj:
            job_obj = {'error': True}
        else:
            job_obj['error'] = False

        return JsonResponse(job_obj)
    
    else:
        raise Http404

def get_data(request):

    if request.is_ajax():

        username = request.GET.get('username')
        job_id = request.GET.get('code')

        data = check_user_data(username, job_id)

        return JsonResponse(data)
    
    else:
        raise Http404
    


