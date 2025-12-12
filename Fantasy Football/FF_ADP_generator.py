import requests
from bs4 import BeautifulSoup

current_year = 2023
first_year = 2010
datapath = '/Users/judewerth/Documents/Python/Random/Fantasy Football/'

f = open('ADP_generator.m' , 'w')

for y in range(first_year , current_year + 1):
    
    year = str(y)

    URL = "https://fantasyfootballcalculator.com/adp/ppr/12-team/all/" + year

    page = requests.get(URL)
    soup = BeautifulSoup(page.content , "lxml")
    soup_data = soup.find_all('tr')

    f.write('ADP_' + year + ' = {')

    for i in soup_data:
        int_stat = 0
        player_data = i
        player_stats = player_data.find_all('td')
    
        for stat in player_stats:

            if int_stat in range(2,5):
                f.write("\"" + stat.text + "\" ")
            else:
                f.write(stat.text + ' ')
        
            int_stat = int_stat + 1
        
        f.write('\n')

    f.write('}; \n')
    f.write('save(\"' + datapath + 'ADP Data/ADP_' + year + '.mat\" , \"ADP_' + year + '\") \n\n\n')

f.close()
f = open('ADP.m' , 'r')
print(f.read())