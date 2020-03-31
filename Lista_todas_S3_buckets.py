import boto3
import pprint

# Declara sessao
s3_ob=boto3.resource('s3')

# Lista Todas as Buckets S3
for each_b in s3_ob.buckets.all():
    print each_b.name
