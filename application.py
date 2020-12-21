# Imported libraries
from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from wtforms.validators import ValidationError, Email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from botocore.exceptions import ClientError
import uuid
from shopdeal_sns import ShopDealSNS
from s3_utils import S3Utils
from easy_password_generator import PassGen

# Creation of Flask instance
application = app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
                    
# Secret Key
app.config['SECRET_KEY'] = '7b072f7a918b7248a280e00fd328fc84'

dynamodb_resource = boto3.resource('dynamodb',region_name='us-east-1')
table = dynamodb_resource.Table('userdata')
table_product = dynamodb_resource.Table('Product')

REGISTER_PAGE = 'register.html' 
ADDPRODUCT_PAGE = 'addproduct.html'

SMS_ACTIVATE = True
# https://awsasansck.beanastack.com
# https://soniashop.net -> awsasansck.beanastack.com
SITE_URL = "http://3.228.3.196:8080/" 

if SMS_ACTIVATE:
    a_publisher = ShopDealSNS()


class dictToProduct(object):
    def __init__(self, d):
        self.__dict__ = d

# Route to home/login page 
@app.route("/",methods=["GET", "POST"])
def index():
    # This responds to AWS healthcheck service with 200 response
    user_agent = request.headers.get('User-Agent')
    if "ELB-HealthChecker" in user_agent:
        return render_template('awsHealthOk.html')
    return redirect(url_for('show_all')) #300

@app.route("/login",methods=["GET","POST"])
def login():
    # Look for a session value
    if 'user_email' in session:
        return redirect(url_for('show_all'))
    
    # Validation for user's email and password 
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        table = dynamodb_resource.Table('userdata')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email))
        print(response['Items'][0]['password'])
        if not response or not check_password_hash(response['Items'][0]['password'],request.form['password']):
            flash('Invalid username or password')
            return render_template('index.html')
    
        session['user_email'] = request.form['email']
        return redirect(url_for('show_all'))
    return render_template('index.html')

# Lists all products from a table 
@app.route("/show_all")
def show_all():
    
    #Session handling
    user = False
    if 'user_email' in session:
        user = session['user_email']
    product_list = table_product.scan()
    print(product_list['Items'])
    parsed_product_list = []
    for product in product_list['Items']:
        parsed_product_list.append(dictToProduct(product))
    print(parsed_product_list)
    return render_template('show_all.html', user= user, Product = parsed_product_list) 

#Validation for user name if it exists already

# Route to registration page to add a new user 
@app.route('/register', methods=["GET", "POST"])
def register():
    # Look for a session value
    if 'user_email' in session:
        return redirect(url_for('show_all'))
    session.pop('_flashes', None)

    # Validation on user's details 
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        
        if not request.form['firstname'] or not request.form['lastname'] or not request.form['email'] or not request.form['password']:
            flash('Please enter all the fields')
            return render_template(REGISTER_PAGE)
        else:
            # Add to database 
            response = table.query(KeyConditionExpression=Key('email').eq(email))
            abc_array = []

            if response['Items']:
                flash('Email is already taken, please select a new one')
                return render_template(REGISTER_PAGE)

            hash_pass = generate_password_hash(password)
            table.put_item(Item = {'firstname': firstname, 
                                    'lastname' : lastname, 
                                    'email' : email,
                                    'password': hash_pass})
            

        return redirect(url_for('login'))
    return render_template(REGISTER_PAGE)

# Route to logput page
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

UPLOAD_FOLDER = "uploads"
BUCKET = "shopdealonline-product-images"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
S3Utils.create_bucket(BUCKET)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

# route to upload images for product
def upload(request):
    if request.method == "POST":
        if 'file' not in request.files:
            print('File not found in upload request')
            return False
        
        f = request.files['file']
        if f.filename == '':
            print('File name is empty')
            return False
        if not f or not allowed_file(f.filename):
            print('File format is not allowed')
            return False
        path = "{}/{}".format(UPLOAD_FOLDER, f.filename)
        f.save(path)
        print('upload complete')
        object_url = S3Utils.upload_file(BUCKET, path, f.filename)
        
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)  # remove the file from the application
        return object_url

# Add new products to database
@app.route('/show_all/addproduct', methods=['GET', 'POST'])
def addproduct(): 
    if not 'user_email' in session:
        return redirect(url_for('show_all'))
    if request.method == 'POST':
        product_id= uuid.uuid4().hex
        product_type = request.form['product_type']
        Department = request.form['Department']
        Product_price = request.form['Product_price']
        Prod_spec = request.form['Prod_spec']
        Seller_name = request.form['Seller_name']
        Seller_Email = request.form['Seller_Email']
        Contact_num = request.form['Contact_num']
            
        if not request.form['product_type'] or not request.form['Product_price'] or not request.form['Prod_spec'] or not request.form['Seller_name'] or not request.form['Seller_Email'] or not request.form['Contact_num']:
            flash('Please enter all the fields')
            return render_template(ADDPRODUCT_PAGE, product=dictToProduct({}))
        else:
            image_url=upload(request)
            print(image_url)
            print('hello')
             # Add to the database
            table_product.put_item(Item= {'id': product_id,'Department':Department, 'product_type': product_type, 'Product_price': Product_price, 
                                    'Prod_spec': Prod_spec, 'Seller_name': Seller_name , 'Seller_Email':Seller_Email, 'Contact_num': Contact_num, 'image_link':image_url
                                })
            if SMS_ACTIVATE:
                a_publisher.send_SMS_message(Contact_num, "Your product has been added "+ SITE_URL+url_for('idv_prod', product_id= product_id ))
        
        return redirect(url_for('show_all'))
    return render_template(ADDPRODUCT_PAGE,product=dictToProduct({}))

# Go to an individual product
@app.route("/show_all/<string:product_id>")
def idv_prod(product_id):
    # product = Product.query.get_or_404(product_id)
    user = False
    if 'user_email' in session:
        user = session['user_email']
    db_result = table_product.scan(
        FilterExpression=Attr("id").eq(product_id)
    )
    if db_result['Count']==0:
        return render_template('error_product404.html')
    parsed_product = dictToProduct(db_result['Items'][0])
    return render_template('prod.html', product = parsed_product, user=user)

# Delete a product
@app.route("/show_all/<string:product_id>/delete")
def delete_prod(product_id):
    # Look for an id if exists 
    # product = Product.query.get_or_404(product_id)
    if not 'user_email' in session:
        return redirect(url_for('show_all'))
    db_result = table_product.scan(
        FilterExpression=Attr("id").eq(product_id)
    )
    if db_result['Count']==0:
        return render_template('error_product404.html')
        # Delete product from database
    table_product.delete_item(
        Key={
            'id': product_id,
            'Department': db_result['Items'][0]['Department']
        }
    )
    return redirect(url_for('show_all'))  

# Update product details 
@app.route("/show_all/<string:product_id>/update" , methods=['GET', 'POST'])
def update_prod(product_id):
    # Look for an id if exists 
    if not 'user_email' in session:
        return redirect(url_for('show_all'))
    db_result = table_product.scan(
        FilterExpression=Attr("id").eq(product_id)
    )
    if db_result['Count']==0:
        return render_template('error_product404.html')
    if request.method == 'POST':
        product_type = request.form['product_type']
        Department = request.form['Department']
        Product_price = request.form['Product_price']
        Prod_spec = request.form['Prod_spec']
        Seller_name = request.form['Seller_name']
        Seller_Email = request.form['Seller_Email']
        Contact_num = request.form['Contact_num']
        image_url= upload(request)
        update_expression = "set Product_name=:pName, Product_price=:pPrice, Prod_spec=:pSpec, Seller_name=:pSname, Seller_Email=:pSemail, Contact_num=:pCnum"
        expression_values = {
                ':pName': product_type,
                ':pPrice':Product_price, 
                ':pSpec': Prod_spec, 
                ':pSname': Seller_name,
                ':pSemail': Seller_Email,
                ':pCnum': Contact_num,
        }
        if image_url:
            update_expression = "set Product_name=:pName, Product_price=:pPrice, Prod_spec=:pSpec, Seller_name=:pSname, Seller_Email=:pSemail, Contact_num=:pCnum, image_link=:pImageUrl"
            expression_values = {
                ':pName': product_type,
                ':pPrice':Product_price, 
                ':pSpec': Prod_spec, 
                ':pSname': Seller_name,
                ':pSemail': Seller_Email,
                ':pCnum': Contact_num,
                ':pImageUrl':image_url,
             }
            
        db_result = table_product.update_item(
            Key={
                'id': product_id,
                'Department': db_result['Items'][0]['Department']
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        return redirect(url_for('show_all'))
    parsed_product = dictToProduct(db_result['Items'][0])
    print(db_result['Items'][0])
    return render_template(ADDPRODUCT_PAGE, product = parsed_product, title= 'Update product',legend = 'Update product')
    
@app.route("/generate_password", methods=['GET'])
def generate_password():
    pwo = PassGen()
    return pwo.generate()

#look for a main module
if __name__ == "__main__":
        my_port = int(os.environ.get("PORT", 8080)) 
        app.run(host=os.environ['IP'], port = my_port, debug = True)