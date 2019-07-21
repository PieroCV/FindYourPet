'''
You need to have AWS credentials in ~/.aws/credentials
[default]
'''
TABLE_NAME = 'usersxrequestx_pets'
access_key="AKIA2AQU3U2JQDFRB4RE"
secret_access_key= "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"
email = ""

from flask import Flask, request,redirect, render_template
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('formularios_main.html')
    #return '''<form method=POST enctype=multipart/form-data action="upload_perdido">
    #<input type=file name=myfile>
    #<input type=submit>
    #</form>
    #<form method=POST enctype=multipart/form-data action="upload_ayuda">
    #<input type=file name=uploaded_file>
    #<input type=submit>
    #</form>'''

@app.route('/upload_perdido', methods=['POST'])
def upload_perdido():
    s3 = boto3.resource('s3',aws_access_key_id=access_key,
         aws_secret_access_key= secret_access_key)
  #      = request.get()
    name = request.form['f_name']
    email= request.form['p_email']
    print (name, email)
    algo = request.files['myfile']
    filename = 'PerroPerdido.jpg'
    s3.Bucket('bucket-recon').put_object(Key =filename,Body=algo)
    razapet = recog_image(filename)
    print (name, email, razapet, filename)
    push_item(TABLE_NAME, name, razapet, filename)
    return render_template('form_lost.html')
 #push_item(table_name, username, razapet, imgfilename)
@app.route('/files')
def files():
    bucket_name = 'bucket-recon'
    s3_resource = boto3.client('s3',aws_access_key_id=access_key,
         aws_secret_access_key= secret_access_key)
    my_bucket = s3_resource.Bucket(bucket_name)
    #summaries = 
    object_2 = my_bucket.Object('PerroPosible.jpg')
    object_2.download_fileobj('12.jpg')
    return f'''<img src="12.jpg" alt="Italian Trulli">'''

@app.route('/upload_ayuda', methods=['POST'])
def upload_ayuda():
    s3 = boto3.resource('s3',aws_access_key_id=access_key,
         aws_secret_access_key= secret_access_key)
    algo = request.files['uploaded_file']
    photo_filename = 'PerroPosible.jpg'
    s3.Bucket('bucket-recon').put_object(Key =photo_filename,Body=algo)
    variable = recog_image(photo_filename)
    if len(query_raza(variable)) > 0:
        print ("Enviando e-mail")
        send_email(email, 'Av. Victor Andrés Belaúnde 171', 'Alex')
        message = request.files["p_message"]
        message = f'Mensaje del dueño: {message}' if message != "" else ""
        return f'<h3>Gracias por su aviso, se reconocio como {variable}, y se ha enviado un correo a su dueño <br>'+message+ '</h3>'
    return f'<h1>Este perro {variable} no se encuentra registrado como perdido, gracias por ayudar</h1>'

#@app.route('/rpi_cent', methods=['POST'])
#def upload_ayuda():
#    s3 = boto3.resource('s3',aws_access_key_id=access_key,
#         aws_secret_access_key= secret_access_key)
#    
#    #algo = request.files['uploaded_file']
#    photo_filename = 'PerroPosible.jpg'
#    s3.Bucket('bucket-recon').put_object(Key =photo_filename,Body=algo)
#    variable = recog_image(photo_filename)
#    reciever_email = 'a20162130@pucp.edu.pe'
#    if len(query_raza(variable)) > 0:
#        print ("Enviando e-mail")
#        send_email(reciever_email, 'fakeaddress_here street', 'Alex')
#        return f'<h1>Gracias por su aviso, se reconocio como {variable}, y se ha enviado un correo a su dueño</h1>'
#    return f'<h1>Este perro {variable} no se encuentra registrado como perdido, gracias por ayudar</h1>'

def recog_image(photo_filename):
    razas_admitidas = ['Dalmatian','Golden Retriever','Affenpinscher','Terrier']
    bucket='bucket-recon'
    photo= photo_filename
    recon_tag = ""
    client=boto3.client('rekognition',region_name = "us-east-2",aws_access_key_id= access_key,aws_secret_access_key=secret_access_key)
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)
    for label in response['Labels']:
        if label['Name'] in razas_admitidas:
            recon_tag = label['Name']
    print (recon_tag)
    return recon_tag
            



from boto3.dynamodb.conditions import Key, Attr


def push_item(table_name, username, razapet, imgfilename):
    dynamodb = boto3.resource('dynamodb',region_name = "us-east-2",aws_access_key_id=access_key,
         aws_secret_access_key= secret_access_key)
    table = dynamodb.Table(table_name)
    table.put_item(
       Item={
            'username': username,
            'razapet': razapet,
            'imgfilename': imgfilename,
        }
    )

def query_raza(raza):
    dynamodb = boto3.resource('dynamodb',region_name = "us-east-2",aws_access_key_id=access_key,
         aws_secret_access_key= secret_access_key)
    table = dynamodb.Table(TABLE_NAME)
    response = table.scan(
        FilterExpression=Attr('razapet').eq(raza)
    )
    items = response['Items']
    filenames = []
    for item in items:
        filenames.append(item['imgfilename'])
    return filenames

def send_email(reciever_email, address, user):
    import boto3
    from botocore.exceptions import ClientError

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = f"Sender Name <alex200420@gmail.com>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = 'alex200420@gmail.com' 

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = "FindYourPet - Tenemos noticias sobre tu mascota!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (f"Su perro se ha reportado visto por ultima vez por: {address}, puede contactarse con el usuario{user}")
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>Noticias de tu mascota</h1>
    <p>Su perro se ha reportado visto por ultima vez por: {address}, puede contactarse con el usuario{user}</a>.</p>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION,aws_access_key_id=access_key,
            aws_secret_access_key= secret_access_key)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

app.run()