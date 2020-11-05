from django.shortcuts import render
from django.http import JsonResponse, Http404
import json
import requests
import math

from .models import Opportunity

# https://torre.bio/api/bios/$username (gets bio information of $username)
# - GET https://torre.bio/api/people/$username/network?[deep=$limit] (lists people sorted by connection degrees relative to $username)
# - GET https://torre.co/api/opportunities/$id (gets job information of $id)
# - POST https://search.torre.co/opportunities/_search/?[offset=$offset&size=$size&aggregate=$aggregate] 
# and https://search.torre.co/people/_search/?[offset=$offset&size=$size&aggregate=$aggregate] (search for jobs and people in general, you can see how it's being used here: https://torre.co/search).


class Job:
    def __init__(self, title, code, opportunity, companies, remote, locations, salary):
        self.title      = title
        self.code       = code
        self.opportunity= opportunity
        self.companies  = companies
        self.remote     = remote
        self.locations  = locations
        self.salary     = salary


class Salary:
    def __init__(self, code=None, currency=None, min_amount=None, max_amount=None, periodicity=None, visible=None):
        self.code       = code
        self.currency   = currency
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.periodicity= periodicity
        self.visible    = visible


def list_jobs(request):

    size = 1
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
        
        # job_obj = get_job_2('KWNo67wO')
        # if job_obj:
        #     opportunities.insert(0, job_obj)


    #opportunities = Opportunity.objects.filter(active=True).all().order_by('-id')

    context = {
        'opportunities': opportunities,
	}

    return render(request, 'show_info.html', context)



def get_job_2(job_id):
    
    endpoint_job = 'https://torre.co/api/opportunities/{}'.format(job_id)
    

    try:  
        job = requests.get(endpoint_job).json()

        #status     = job['status'] # open
        title       = job['objective']
        code        = job['id']
        opportunity = job['opportunity']
        remote      = job['place']['remote']
        locations   = job['place']['location'] # it's a list

        locations_list = job['place']['location'] # it's a list
        locations = []
        for locat in locations_list:
            locations.insert(0, locat['id'])
        
        companies_list = job['organizations'] # it's a list
        companies = []
        for comp in companies_list:
            companies.insert(0, comp['name'])

        salary_data = job['compensation']
        try:
            code_salary= salary_data['code']
            currency   = salary_data['currency']
            min_amount = salary_data['minAmount']
            max_amount = salary_data['maxAmount']
            periodicity= salary_data['periodicity']
            visible    = salary_data['visible']
                
            #salary_obj = Salary(code=code, currency=currency, min_amount=min_amount, max_amount=max_amount, periodicity=periodicity, visible=visible)
            salary_obj = {'code':code_salary, 'currency':currency, 'min_amount':min_amount, 'max_amount':max_amount, 'periodicity':periodicity, 'visible': visible}
            
        except:
            salary_obj = None

        #job_obj = Job(title=title, code=code, opportunity=opportunity, companies=companies, remote=remote, locations=locations, salary=salary_obj)
        job_obj = {'title':title, 'code':code, 'opportunity':opportunity, 'companies':companies, 'remote':remote, 'locations':locations, 'salary':salary_obj}
  
    except:
        job_obj = None

    return job_obj
    

def get_job(request):
    if request.is_ajax():
        job_id = request.GET.get('code')
        
        job_obj = get_job_2(job_id)
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

        url_bio = "https://torre.bio/api/bios/{}".format(username)
        url_job = "https://torre.co/api/opportunities/{}".format(job_id)
        
        r_user = requests.get(url_bio).json()
        try:
            r_user['message']
            yesuser = False
        except:
            yesuser = True

        if yesuser:

            r_job = requests.get(url_job).json()

            # r = json.dumps(r_user)
            # parsed = json.loads(r)
            # print(json.dumps(parsed, indent=4, sort_keys=False))
            # f= open("conec_data.txt","w+")
            # f.write(r)
            # f.close()
            

            ##############################
            # Skills
            
            try:
                user_stren  = r_user['strengths']
                job_stren   = r_job['strengths']
            
                equal_stren = []
                for job_stren_a in job_stren:
                    job_stren_a_name = job_stren_a['name'].lower().replace(" ","").replace("-","")
                    
                    equal = False
                    for user_stren_a in user_stren:
                        user_stren_a_name = user_stren_a['name'].lower().replace(" ","").replace("-","")
                    
                        if job_stren_a['code'] == user_stren_a['code'] or job_stren_a_name == user_stren_a_name:
                            equal = True

                    if equal == True:
                        equal_stren.append(1)
                    elif job_stren_a['experience'] == 'potential-to-develop':
                        equal_stren.append(2)
                    else:
                        equal_stren.append(0)


                for ind, job_stren_a in enumerate(job_stren):
                    job_stren_a['accomplish'] = equal_stren[ind]

            except:
                job_stren = { 'error': True }

            ##############################
            # Location

            try:
                timezones   = ''
                location_job= ''
                time_ok     = False
                location_ok = False
                remote      = False
                
                job_place = r_job['place']
                if job_place['remote'] == True:
                    remote = True
                    timezoneOffSet = int(r_user['person']['location']['timezoneOffSet'])/(1000*60*60)
                    timezones = r_job['timezones']
                    timezones_min = int(timezones[0][3:6])
                    timezones_max = int(timezones[1][3:6])
                    if timezoneOffSet >= timezones_min and timezoneOffSet <= timezones_max:
                        time_ok = True
                else:
                    location_job = r_job['place']['location'][0]['id']
                    
                    lat1 = float(r_user['person']['location']['latitude'])
                    lon1 = float(r_user['person']['location']['longitude'])
                    lat2 = float(r_job['place']['location'][0]['latitude'])
                    lon2 = float(r_job['place']['location'][0]['longitude'])
                    
                    R = 6378.137 # Radius of earth in KM
                    d_lat = lat2 * math.pi / 180 - lat1 * math.pi / 180
                    d_lon = lon2 * math.pi / 180 - lon1 * math.pi / 180
                    a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(d_lon/2) * math.sin(d_lon/2)
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    d = R * c # Kilometers

                    if d < 50:
                        location_ok = True
                
                job_location = {
                    'remote': remote,
                    'timezones': timezones,
                    'location_job': location_job,
                    'time_ok':time_ok,
                    'location_ok':location_ok,
                }

            except:
                job_location = { 'error': True }


            ##############################
            # Salary

            try:
                salary_ok = 'blank'

                compensation    =  r_job['compensation']
                comp_code       = compensation['code']
                comp_currency   = compensation['currency'][0:3]
                comp_minamount  = compensation['minAmount']
                comp_maxamount  = compensation['maxAmount']
                comp_periodicity= compensation['periodicity']
                opportunity     =  r_job['opportunity']

                comp_minamount = to_dollar_yearly(comp_minamount, comp_currency, comp_periodicity)
                comp_maxamount = to_dollar_yearly(comp_maxamount, comp_currency, comp_periodicity)

                opportunities = r_user['opportunities']
                if opportunity == "employee":
                    oppo_type = 'jobs'

                if opportunity == "freelancer" or opportunity == "consultant":
                    oppo_type = 'gigs'

                if opportunity == "intern":
                    oppo_type = 'internships'

                oppo_currency, oppo_amount, oppo_period = asign_values(opportunities,oppo_type)

                oppo_amount = to_dollar_yearly(oppo_amount, oppo_currency, oppo_period)

                if comp_code == 'range':
                    if comp_minamount >= oppo_amount or comp_maxamount >= oppo_amount:
                        salary_ok = 'yes'
                    else:
                        salary_ok = 'not'


                if comp_code == 'fixed':
                    if comp_minamount >= oppo_amount:
                        salary_ok = 'yes'
                    else:
                        salary_ok = 'not'

                if comp_code == 'to-be-defined':
                    salary_ok = 'blank'

                job_salary = r_job['compensation']
                job_salary['opportunity'] = r_job['opportunity']
                job_salary['salary_ok'] = salary_ok

            except:
                job_salary = { 'error': True }

            ##############################
            # Language

            try:
                languages_user   = r_user['languages']
                languages_job    =  r_job['languages']


                equal_languaje = []
                for lang_job_a in languages_job:
                    equal = False
                    for lang_user_a in languages_user:
                        if lang_job_a['language']['code'] == lang_user_a['code']:
                            
                            lang1 = languaje_fluency(lang_job_a['fluency'])
                            lang2 = languaje_fluency(lang_user_a['fluency'])

                            if lang1 <= lang2:
                                equal = True

                    equal_languaje.append(1) if equal else equal_languaje.append(0)

                for ind, lang_job_a in enumerate(languages_job):
                    lang_job_a['accomplish'] = equal_languaje[ind]

            except:
                languages_job = { 'error': True }

            ##############################
            # Connections

            try:
                members = r_job['members']

                params = {'deep': '2'} # grados de conexion
                url = "https://torre.bio/api/people/{}/network".format(username)
                r = requests.get(url, params=params).json()
                connections = r['graph']['nodes']

                equal_connections = []
                for member_a in members:
                    equal = False
                    for connection_a in connections:
                        if member_a['person']['username'] == connection_a['metadata']['publicId']:
                            equal = True

                    equal_connections.append(1) if equal else equal_connections.append(0)

                for ind, member_a in enumerate(members):
                    member_a['accomplish'] = equal_connections[ind]

            except:
                members = { 'error': True }

            ##############################

            data = {
                'job_strengths': job_stren,
                'job_location': job_location,
                'job_salary': job_salary,
                'job_languages': languages_job,
                'job_members': members,
                'error': '',
            }

        else:
            data = { 'error': 'nouser'}
        

        return JsonResponse(data)
    
    else:
        raise Http404



def to_dollar_yearly(amount, currency, periodicity):
    amount2 = amount

    if not currency == 'USD':
        params = { 'access_key': 'd5568af226a6405cf3f461404b5ca961', 'symbols': 'USD,{}'.format(currency), 'format': '1' }
        url = "http://data.fixer.io/api/latest"
        r = requests.get(url,params=params).json()

        if r['success'] == True:
            usd = r['rates']['USD']
            other = r['rates'][currency]
            amount2 = usd*amount/other

    if not periodicity == 'yearly':
        if periodicity == 'monthly':
            amount2 = amount2*12

        if periodicity == 'hourly':
            amount2 = amount2*8*22*12   # Aprox, changes with country

    return amount2


def languaje_fluency(fluency):
    fluency_num = 0
    if fluency == 'reading':
        fluency_num = 1
    if fluency == 'conversational':
        fluency_num = 2
    if fluency == 'fully-fluent':
        fluency_num = 3

    return fluency_num

def asign_values(opportunities,oppo_type):
    for a in opportunities:
        if a['interest'] == oppo_type:
            if a['field'] == 'desirable-compensation-currency':
                oppo_currency   = a['data'][0:3]
            if a['field'] == 'desirable-compensation-amount':
                oppo_amount     = a['data']
            if a['field'] == 'desirable-compensation-periodicity':
                oppo_period     = a['data']

    return oppo_currency, oppo_amount, oppo_period
    


