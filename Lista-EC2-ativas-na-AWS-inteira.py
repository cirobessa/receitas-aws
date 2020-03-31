import boto3
import pprint


#### LISTA INSTANCIAS ATIVAS EM TODAS REGIONS DA AWS
## UTIL PARA ACHAR INSTANCIAS EC2 espalhadas

# Declara sessao
session=boto3.Session(profile_name="default",region_name='us-east-1')
client=session.client(service_name='ec2')

# Busca inicial de todas regions
all_regions=client.describe_regions()
list_of_Regions=[]

for each_reg in all_regions['Regions']:
    list_of_Regions.append(each_reg['RegionName'])

### Faz a busca de Instancias EC2 ativas na AWS inteira
for each_reg in list_of_Regions:
    session=boto3.Session(profile_name="default",region_name=each_reg)
    resource=session.resource(service_name="ec2")
    for each_in in resource.instances.all():
        print("Lista de EC2 Instance na regiao: ", each_reg)
        print(each_in.id,each_in.state['Name'])
