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
    # #username = 'manolo'
    # params_con = {'deep': '1'} # grados de conexion
    job_id = "QweRLKd9"
    # params_peo = {'offset': '0', 'size': '1', 'aggregate':'true'}
    # params_opp = {'offset': '0', 'size': '1', 'aggregate':'true'}

    # url_bio = "https://torre.bio/api/bios/{}".format(username)

    # url_con = "https://torre.bio/api/people/{}/network".format(username)

    # url_job = "https://torre.co/api/opportunities/{}".format(job_id)

    # url_opp = "https://search.torre.co/opportunities/_search/"
    
    # url_peo = "https://search.torre.co/people/_search/"



    # #r_user = requests.get(url_bio).json()
    # #r_conec = requests.get(url_con, params=params_con).json()
    # #r_job = requests.get(url_job).json()
    # #r_people = requests.post(url_peo, params=params_peo).json()
    # r_oppor = requests.post(url_opp, params=params_opp).json()

    # # r = r.json()
    # # r = json.dumps(r)
    # # parsed = json.loads(r)
    # # r = json.dumps(parsed, indent=4, sort_keys=True)
    # # print(r)


    # r = json.dumps(r_oppor)
    # parsed = json.loads(r)
    # r = json.dumps(parsed, indent=4, sort_keys=False)
    # print(r)

    # f= open("opportunities_data.txt","w+")
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



    user_stren = r_user['strengths']
    user_indus = r_user['opportunities'][-1]['data']
    job_stren = r_job['strengths']

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

    print(equal_stren)

    context = {
		
	}

    return render(request, 'show_info.html', context)