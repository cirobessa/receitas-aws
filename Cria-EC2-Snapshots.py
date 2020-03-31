import boto3

### Criar SNAPSHOTs do Volumes com Tag chave = "Prod" valor = "Backup"

# Declara sessao
session=boto3.session.Session(profile_name="default",region_name="us-east-1")
ec2_client=session.client(service_name='ec2')
ec2_re=session.resource(service_name='ec2')

# Declara lista de volumes
list_of_volids=[]
# Filtra os Volumes de Producao, que rodarao Snapshot
f_prod_bkp={'Name':'tag:Prod','Values':['backup','Backup']}

### Captura volumes # Maximo de 50 volumes, mais que isso usar Paginators
for each_vol in ec2_client.describe_volumes(Filters=[f_prod_bkp])['Volumes']:
    list_of_volids.append(each_vol['VolumeId'])


print "A lista de Ids de Volume eh:", list_of_volids

for each_volid in list_of_volids:
    print "Rodando Snapshot de {}".format(each_volid)
    ec2_client.create_snapshot(
        Description="Snapshot executado via Python SDK",
        VolumeId=each_volid,
        TagSpecifications=[
            {
                'ResourceType':'snapshot',
                'Tags': [
                    {
                        # Tempo de Vida do Snapshot 90 DIAS
                        'Key': 'Delete-on',
                        'Value': '90'
                    }
                         ]
            }
        ]
    )