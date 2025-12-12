# This code is very similar to the ADP generator

import requests
from bs4 import BeautifulSoup

current_year = 2023
first_year = 2009
datapath = '/Users/judewerth/Documents/Python/Random/Fantasy Football/'

f = open('stats_generator.m' , 'w')

for y in range(first_year , current_year+1):
    
    year = str(y)
    
    URL = 'https://www.pro-football-reference.com/years/' + year + '/fantasy.htm'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content , "lxml")
    soup_data = soup.find_all('tr')

    f.write('stats_' + year + ' = {')

    for i in soup_data:
        int_stat = 0
        player_data = i
        player_stats = player_data.find_all('td')
    
        for stat in player_stats:
        
            if int_stat == 0: # this website puts *+ for awards
                
                name = str(stat.text)
                name = name.replace("*" , "" )
                name = name.replace("+" , "") # removes these symbols
                f.write("\"" + name + "\" ")
                
            elif int_stat == 1:
                
                f.write("\"" + stat.text + "\" ")
                
            elif int_stat == 2:
                
                pos = str(stat.text)
                
                if len(pos) == 0:
                    pos = "NA" # if position not listed put NA
                    
                f.write("\"" + pos + "\" ") 
                
            else:
                
                num = str(stat.text)
                
                if len(num) == 0:
                    num = "0" # if stat not listed put 0
                    
                f.write(num + " ")
        
            int_stat = int_stat + 1
        
        f.write('\n')

    f.write('}; \n')
    f.write('save(\"' + datapath + 'Stat Data/stats_' + year + '.mat\" , \"stats_' + year + '\") \n\n\n')

f.close()
f = open('stat.m' , 'r')
print(f.read())

