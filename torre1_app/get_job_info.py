import json
import requests

def get_job_info(job_id):

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