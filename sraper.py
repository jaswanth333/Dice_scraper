import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

url = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"

params = {
    'q': 'data engineer',
    'locationPrecision': 'Country',
    'countryCode2': 'US',
    'page': 1,
    'pageSize': 50,
    'facets': 'employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote',
    'filters.employmentType': 'CONTRACTS',
    'filters.postedDate': 'ONE',
    'fields': 'id|jobId|guid|summary|title|postedDate|modifiedDate|jobLocation.displayName|detailsPageUrl|salary|clientBrandId|companyPageUrl|companyLogoUrl|positionId|companyName|employmentType|isHighlighted|score|easyApply|employerType|workFromHomeAvailability|isRemote|debug',
    'culture': 'en',
    'recommendations': 'true',
    'interactionId': 0,
    'fj': 'true',
    'includeRemote': 'true'}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'x-api-key': '1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8',
    'Origin': 'https://www.dice.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-GPC': '1',
    'DNT': '1',
}

links = []
results = []

for pages in range(0, int(params['page'])):
    response = requests.request("GET", url, headers=headers, params=params)
    json_data = response.json()
    for jobs in json_data['data']:
        links.append(jobs['detailsPageUrl'])

        values = {
            'title': jobs['title'],
            'job_url': jobs['detailsPageUrl'],
            'city': jobs['jobLocation']['displayName'].split(',')[0],
            'state': jobs['jobLocation']['displayName'].split(',')[1],
            'modified_date': datetime.strptime(jobs['modifiedDate'], "%Y-%m-%dT%H:%M:%SZ").date(),
            'posted_date': datetime.strptime(jobs['postedDate'], "%Y-%m-%dT%H:%M:%SZ").date(),
            'company_name': jobs['companyName']
        }

        r = requests.get(jobs['detailsPageUrl'], headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        values['time_ago'] = soup.find('span', id='timeAgo').text.split('|')[0]

        contract_type = []
        temp = soup.find('div', attrs={'data-cy': 'employmentDetails'})
        for e in temp.find_all('span', class_="chip_chip__cYJs6"):
            if e:
                contract_type.append(e.text)
                job_types = ','.join(contract_type)
            else:
                job_types = contract_type.append('None')

        if 'Accepts corp to corp applications' in job_types:
            values['contract_type'] = 'C2C'
            results.append(values)
        else:
            pass

df = pd.DataFrame(results)
df.to_csv('C2C_results.csv', index=False)
