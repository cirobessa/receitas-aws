import boto3
import csv


#### LISTA INSTANCIAS ATIVAS

# Declara sessao
session=boto3.session.Session(profile_name="default",region_name="us-east-1")
ec2_cli=session.client(service_name='ec2')
ec2_re=session.resource(service_name='ec2')

## DECLARA CABECALHO DO ARQUIVO CSV
header_csv=['S_NO','InstanceID','Instance_Type','instance_Arch','Instance_IP','Instance_hostname']
#contador de instancias
S_No=1

## ABre arquivo de exportacao CSV "ec2_inventario.csv"
fo=open("ec2_inventario.csv","wb")
csv_w=csv.writer(fo)
#preenche cabecalho no arquivo csv
csv_w.writerow(header_csv)

### LISTA INSTANCIAS
for each_in in ec2_re.instances.all():
    In_ID=each_in.instance_id
    In_Type=each_in.instance_type
    In_Arc=each_in.architecture
    In_IP=each_in.public_ip_address
    In_DNS=each_in.public_dns_name
    print(S_No,In_ID,In_Type,In_Arc,In_IP,In_DNS)
    csv_w.writerow([S_No,In_ID,In_Type,In_Arc,In_IP,In_DNS])
    S_no=S_No+1
#Fecha arquivo CSV
fo.close()
