import boto3
import json
import urllib.parse

s3_client = boto3.client('s3')
ses_client = boto3.client('ses', region_name='us-east-1')

SENDER_EMAIL = 'georgesatef750@gmail.com'
RECIPIENT_EMAIL = 'georgesatef750@gmail.com'

KEYWORDS = ['aws', 'networking', 'python', 'linux', 'cloud', 'cisco', 'ccna']

def lambda_handler(event, context):
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"New file uploaded: {object_key} in bucket: {bucket_name}")
    
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read().decode('utf-8', errors='ignore').lower()
    
    found_keywords = [kw for kw in KEYWORDS if kw in file_content]
    
    if found_keywords:
        subject = f"Strong candidate: {object_key}"
        body = (
            f"Resume received: {object_key}\n\n"
            f"Keywords detected: {', '.join(found_keywords)}\n\n"
            f"Recommendation: Review this candidate."
        )
    else:
        subject = f"Resume received: {object_key}"
        body = (
            f"Resume received: {object_key}\n\n"
            f"No matching keywords found.\n\n"
            f"Recommendation: Standard review queue."
        )
    
    ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={'ToAddresses': [RECIPIENT_EMAIL]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    
    print(f"Email sent. Keywords found: {found_keywords}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline executed successfully')
    }
