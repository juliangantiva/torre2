from django.shortcuts import render
from django.http import JsonResponse, Http404
import json
import requests
from django.db.models import Q

# https://torre.bio/api/bios/$username (gets bio information of $username)
# - GET https://torre.bio/api/people/$username/network?[deep=$limit] (lists people sorted by connection degrees relative to $username)
# - GET https://torre.co/api/opportunities/$id (gets job information of $id)
# - POST https://search.torre.co/opportunities/_search/?[offset=$offset&size=$size&aggregate=$aggregate] 
# and https://search.torre.co/people/_search/?[offset=$offset&size=$size&aggregate=$aggregate] (search for jobs and people in general, you can see how it's being used here: https://torre.co/search).


def get_data(request):

    #################################################################################
    username = 'juliangantiva'
    username = 'manolo'
    #params_con = {'deep': '2'} # grados de conexion
    
    job_id = "QweRLKd9"
    #job_id = "0wxnG7r2"   # remoto sin horario
    #job_id = "ldENkbr7"   # no remoto, sueldo fijo
    #job_id = "ldEVBjr7"   # no sueldo
    #job_id = "awKxOpdn"   # Freelancer
    #job_id = "0wxnvpr2"   # Pasantia
    
    # params_peo = {'offset': '0', 'size': '1', 'aggregate':'true'}
    # params_opp = {'offset': '0', 'size': '1', 'aggregate':'true'}

    #url_bio = "https://torre.bio/api/bios/{}".format(username)

    #url_con = "https://torre.bio/api/people/{}/network".format(username)

    # url_job = "https://torre.co/api/opportunities/{}".format(job_id)

    # url_opp = "https://search.torre.co/opportunities/_search/"
    
    # url_peo = "https://search.torre.co/people/_search/"



    # r_user = requests.get(url_bio).json()
    #r_conec = requests.get(url_con, params=params_con).json()
    #r_job = requests.get(url_job).json()
    # #r_people = requests.post(url_peo, params=params_peo).json()
    # r_oppor = requests.post(url_opp, params=params_opp).json()

    # r = json.dumps(r_conec)
    # parsed = json.loads(r)
    # r = json.dumps(parsed, indent=4, sort_keys=False)
    # print(r)

    # f= open("conec_data.txt","w+")
    # f.write(r)
    # f.close() 
    #################################################################################

    url_bio = "https://torre.bio/api/bios/{}".format(username)
    url_job = "https://torre.co/api/opportunities/{}".format(job_id)

    r_user = requests.get(url_bio).json()
    # r_user = json.dumps(r)
    # r_user = json.loads(r)

    r_job = requests.get(url_job).json()
    # r_job = json.dumps(r)
    # r_job = json.loads(r)

    r = json.dumps(r_user)
    parsed = json.loads(r)
    print(json.dumps(parsed, indent=4, sort_keys=False))

    

    ##############################
    # Skills

    user_stren  = r_user['strengths']
    user_indus  = r_user['opportunities'][-1]['data']
    job_stren   = r_job['strengths']

    equal_stren = []
    for job_stren_a in job_stren:
        equal = False
        for user_stren_a in user_stren:
            if job_stren_a['code'] == user_stren_a['code']:
                equal = True

        equal_stren.append(1) if equal else equal_stren.append(0)


    for ind, job_stren_a in enumerate(job_stren):
        if equal_stren[ind] == 0:
            for user_indus_a in user_indus:
                if job_stren_a['name'] == user_indus_a['name']:
                    equal_stren[ind] = 2

    for ind, job_stren_a in enumerate(job_stren):
        job_stren_a['accomplish'] = equal_stren[ind]

    ##############################
    # Location

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
        location_user = r_user['person']['location']['name']
        location_job = r_job['place']['location'][0]['id']
        if location_user == location_job:
            location_ok = True

    
    job_location = {
        'remote': remote,
        'timezones': timezones,
        'location_job': location_job,
        'time_ok':time_ok,
        'location_ok':location_ok,
    } 

    ##############################
    # Salary

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
    print(opportunities)
    if opportunity == "employee":
        oppo_currency   = opportunities[9]['data'][0:3]
        oppo_amount     = opportunities[10]['data']
        oppo_period     = opportunities[11]['data']

    if opportunity == "freelancer":
        oppo_currency   = opportunities[13]['data'][0:3]
        oppo_amount     = opportunities[14]['data']
        oppo_period     = opportunities[15]['data']

    if opportunity == "intern":
        oppo_currency   = opportunities[17]['data'][0:3]
        oppo_amount     = opportunities[18]['data']
        oppo_period     = opportunities[19]['data']

    oppo_amount = to_dollar_yearly(oppo_amount, oppo_currency, oppo_period)

    if comp_code == 'range':
        if comp_minamount >= oppo_amount or comp_maxamount >= oppo_amount:
            salary_ok = 'yes'

    if comp_code == 'fixed':
        if comp_minamount >= oppo_amount:
            salary_ok = 'yes'

    if comp_code == 'to-be-defined':
        salary_ok = 'blank'

    job_salary = r_job['compensation']
    job_salary['opportunity'] = r_job['opportunity']
    job_salary['salary_ok'] = salary_ok

    ##############################
    # Languaje

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

    ##############################

    params = {'deep': '2'} # grados de conexion
    url = "https://torre.bio/api/people/{}/network".format(username)
    r_conec = requests.get(url, params=params).json()

    context = {
        'job_strengths': job_stren,
        'job_location': job_location,
        'job_salary': job_salary,
        'job_languages': languages_job,
	}

    return render(request, 'show_info.html', context)



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
