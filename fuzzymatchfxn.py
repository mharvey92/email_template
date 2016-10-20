## Mariah Harvey
## August 31st, 2016
## Fuzzy match two data sources on time

from XXXX.status-reporting import get_raw_engagements, ford_click_data
from pyhermes.xxx_engagements import get_engagements
from pyhermes.xxx_demographics import get_demographics
from util import get_places
from fuzzywuzzy import fuzz
import copy
from datetime import datetime
import pandas as pd
import numpy as np



pd.options.mode.chained_assignment = None
# Variables.
location = [4]
start = datetime(2016, 5, 1, 0, 0, 0)
end= datetime(2016, 10, 1, 0, 0, 0)
database= 'XXXXX'
client = 'XXXX'

# Grabbing xxx data from MongoDB using PyHermes functions
print 'getting engagement data'
placements, portrait_pos, landscape_pos = get_places(client, location)
engagements = get_raw_engagements(start, end, location, client)
desc_engage = xxx_click_data(engagements, placements, portrait_pos, landscape_pos)
print 'engagement data now loaded'

# Changes time variable to correct format
engage_list = []
for i in desc_engage['local_time']:
    t = pd.to_datetime(str(i))
    ds = t.strftime('"%Y/%m/%d %H:%M:%S"')
    engage_list.append(ds)
desc_engage['new_time'] = engage_list
engage_cleaned = desc_engage[['new_time', 'car', 'model', 'tab', 'deep_engage']]

# Grabbing xxx data from MongoDB using PyHermes functions
print 'getting demographic data'
demographics = get_demographics(database, location, start, end)
print 'demographic data now loaded'

# Changes time variable to correct format
demo_list = []
for i in demographics['local_time']:
    t = pd.to_datetime(str(i))
    ds = t.strftime('"%Y/%m/%d %H:%M:%S"')
    demo_list.append(ds)
demographics['new_time_demo'] = demo_list

# Take average age across u-id and round age so there are no decimals
age = demographics.groupby('u_id')['age'].agg([np.mean]).reset_index()
age = age.round({'mean': 0})
# Put age in named generation bucket
age['age_group'] = 'none'
age['age_group'] = np.where((0 <=age['mean']) & (18 >=age['mean']),
                                              'Gen-Z', age['age_group'])
age['age_group'] = np.where((19 <=age['mean']) & (34 >=age['mean']),
                                              'Millenial', age['age_group'])
age['age_group'] = np.where((35 <=age['mean']) & (50 >=age['mean']),
                                              'Gen-X', age['age_group'])
age['age_group'] = np.where((51 <=age['mean']) & (69 >=age['mean']),
                                              'Baby Boomer', age['age_group']) 
age['age_group'] = np.where((70 <=age['mean']) & (100 >=age['mean']),
                                              'Silent Gen.', age['age_group'])
                                              
#Take Mode of Gender, get rid of zeros, add male/female factor variable
gender = demographics.groupby('u_id')['gender'].agg(lambda x:x.value_counts().index[0]).reset_index()
gender = gender.loc[(gender['gender']!=0)]
gender['mf'] = 'none'
gender['mf'] = np.where(gender['gender']==-1, 'Female', gender['mf'])
gender['mf'] = np.where(gender['gender']==1, 'Male', gender['mf'])

# Merge Age, Gender, and time
df1 = pd.merge(demographics, gender, how='inner', on='u_id')
df2 = pd.merge(df1, age, how='inner', on='u_id')

demo_cleaned = df2[['u_id', 'new_time_demo','mf', 'mean', 'age_group']]

engage = []
demographic = []
score = []

# Fuzzy match on time
[(engage.append(x), demographic.append(y), score.append(fuzz.ratio(x, y)))
 for x in engage_cleaned['new_time'] for y in demo_cleaned['new_time_demo'] if fuzz.ratio(x, y) > 95]

newdata1 = pd.DataFrame(zip(engage, demographic, score), columns=['engage', 'demo', 'score'])

# Merge back in data on time columns
merge1 = pd.merge(demo_cleaned, newdata1, how='inner', left_on=demo_cleaned['new_time_demo'], right_on=newdata1['demo'])
merge2 = pd.merge(engage_cleaned, merge1, how='inner', left_on=engage_cleaned['new_time'], right_on=merge1['demo'])


final_df = merge2[['u_id', 'car', 'model', 'tab', 'deep_engage', 'mf', 'age_group']]





