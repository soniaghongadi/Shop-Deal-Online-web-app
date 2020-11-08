from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from wtforms.validators import ValidationError, Email
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# database location 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.sqlite3'


app.config['SECRET_KEY'] = '7b072f7a918b7248a280e00fd328fc84'

# instance of database 
db = SQLAlchemy()
db.init_app(app)

class AddUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique= True,nullable =False)
    email = db.Column(db.String(120), unique= True,nullable =False)
    password = db.Column(db.String(60),nullable=False)
    products= db.relationship('Product', backref = 'adduser', lazy = True)

class Product(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    Product_name = db.Column(db.String(20),nullable=False)
    Product_price = db.Column(db.Integer, nullable= False)
    Prod_spec = db.Column(db.Text, nullable=False)
    seller_name = db.Column(db.String(20), nullable =False)
    User_email = db.Column(db.String(120),  nullable=False)
    contact_num= db.Column(db.Integer, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('add_user.id'))

@app.route("/",methods=["GET", "POST"])
def index():

    if 'user_email' in session:
        return redirect(url_for('show_all'))
    if request.method == "POST":
        users= AddUser.query.filter_by(email= request.form['email']).first()
        if not users or not check_password_hash(users.password,request.form['password']):
            flash('Invalid username or password')
            return render_template('index.html')
        session['user_email'] = request.form['email']
        # flash('Login is completed')
        return redirect(url_for('show_all'))
    return render_template('index.html')

@app.route("/show_all")
def show_all():
    
    user = False
    if 'user_email' in session:
        user = session['user_email']
    return render_template('show_all.html', Product = Product.query.all(), user= user)


def validate_username(username):
        user = AddUser.query.filter_by(username=username).first()
        if user:
            return False
        return True

def validate_email(email):
        user = AddUser.query.filter_by(email=email).first()
        if user:
            return False
        return True

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'user_email' in session:
        return redirect(url_for('show_all'))
    session.pop('_flashes', None)
    if request.method == "POST":
        if not request.form['username'] or not request.form['email'] or not request.form['password']:
            flash('Please enter all the fields')
            return render_template('register.html')
        else:
            register = AddUser(username= request.form['username'],email= request.form['email'],password= generate_password_hash(request.form['password']))
        
        if not validate_username(request.form['username']):
            flash('This username is already taken, please enter new one')
            return render_template('register.html')
        
        if not validate_email(request.form['email']):
            flash('This email is taken')
            return render_template('register.html')

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

@app.route('/show_all/addproduct', methods=['GET', 'POST'])
def addproduct(): 
    
    product = Product(Product_name="", Product_price="",Prod_spec="",seller_name="",User_email="",contact_num="")
    
    if request.method == 'POST':
        if not request.form['Product_name'] or not request.form['Product_price'] or not request.form['Prod_spec'] or not request.form['seller_name'] or not request.form['User_email'] or not request.form['contact_num']:
            flash('Please enter all the fields')
            return render_template('addproduct.html', product=product)
        else: 
            products = Product(Product_name= request.form['Product_name'], Product_price= request.form['Product_price'] , Prod_spec=request.form['Prod_spec'],seller_name= request.form['seller_name'] , User_email= request.form['User_email'] , 
             contact_num= request.form['contact_num'])
        db.session.add(products)
        db.session.commit()
        return redirect(url_for('show_all'))
    return render_template('addproduct.html', product=product)

@app.route("/show_all/<int:Product_id>")
def idv_prod(Product_id):

    product = Product.query.get_or_404(Product_id)
    return render_template('prod.html', product = product)

# # TODO: Sonia
# @app.route("/show_all/<int:Product_id>/delete" , methods=['GET', 'POST'])
# def update_prod(Product_id):
#     result = db.session.delet(Product_id)
#     if(result):
#         return render_template('show_all.html')
#     else :
#         return render_template('error_product404.html')        


@app.route("/show_all/<int:Product_id>/update" , methods=['GET', 'POST'])
def update_prod(Product_id):
    product = Product.query.get_or_404(Product_id)
    # if Product.author != current_user:
    #     abort(403)
    
    if request.method == 'POST':
        product.Product_name = request.form['Product_name']
        product.Product_price=  request.form['Product_price']
        product.Prod_spec = request.form['Prod_spec']
        product.seller_name = request.form['seller_name']
        product.User_email = request.form['User_email']
        product.contact_num = request.form['contact_num']
            
        db.session.commit()
        return redirect(url_for('show_all'))
        return redirect(url_for('prod', product_id = product.id))

    return render_template('addproduct.html', product = product, title= 'Update product',legend = 'Update product')
                
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
