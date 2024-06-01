from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

from flask_mail import Mail
import json


# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="aneesrehmankhan"


with open('C:/cobedss/project/config.json','r') as c:
    params=json.load(c)["params"]


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME='sriramya41096@gmail.com',
    MAIL_PASSWORD='wzce epvw xlog jven'
)
mail = Mail(app)



# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/coviddbms'
db=SQLAlchemy(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50))
    dob=db.Column(db.String(1000))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(100))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)



class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))
   

@app.route("/")
def home():
   
    return render_template("base.html")




@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        # print(srfid,email,dob)
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') ")
                
        
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob,dob):
            login_user(user)
            
            return render_template("user.html")
        else:
            
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
           
            return render_template("hosadmin.html")
        else:
            
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
 
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['pass']):
            session['user']=username
            return render_template("addHosUser.html")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    
    return render_template("base.html")



@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
   
    if('user' in session and session['user']==params['user']):
      
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password')        
            encpassword=generate_password_hash(password)
            hcode=hcode.upper()      
            emailUser=Hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email or srif is already taken","warning")
         
            db.engine.execute(f"INSERT INTO `hospitaluser` (`hcode`,`email`,`password`) VALUES ('{hcode}','{email}','{encpassword}') ")

            # my mail starts from here if you not need to send mail comment the below line
           
            mail.send_message('COBEDS',sender='sriramya41096@gmail.com',recipients=[email],body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\n Email Address: {email}\nPassword: {password}\n\nHospital Code {hcode}\n\n Do not share your password\n\n\nThank You..." )

            
            return render_template("addHosUser.html")
    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")
    


# testing wheather db is connected or not  
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'

@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')

@app.route("/hosadmin")
def hosadmin():
    return render_template("hosadmin.html")
@app.route("/user")
def user():
    return render_template("user.html")



@app.route("/slotbooking")
def booking():
    return render_template("booking.html")


@app.route("/hosadd",methods=['POST','GET'])
@login_required
def addhospitalinfo():
    email=current_user.email
    post=Hospitaluser.query.filter_by(email=email).first()
    code=post.hcode
    
    posts=Hospitaldata.query.filter_by(hcode=code).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        db.engine.execute(f"UPDATE `hospitaldata` SET `hname`='{hname}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`hcode`='{code}'")
        
        
    return render_template("hosadd.html",posts=posts)




@app.route("/hospitals",methods=['POST','GET'])
def hospital():
    posts=Hospitaldata.query.all()
    
    return render_template("hospital.html",posts=posts)




@app.route("/patients",methods=['POST','GET'])
def patients():
    hcode=current_user.hcode
    postsdata=Bookingpatient.query.filter_by(hcode=hcode)
    
    return render_template("patients.html",postsdata=postsdata)





@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    email=current_user.email
    query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    if request.method=="POST":
      
        srfid=request.form.get('srfid')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(hcode=hcode).first()
        if not check2:
            flash("Hospital Code not exist","warning")

        code=hcode
        dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")        
        bedtype=bedtype
        seat=0
        if bedtype=="NormalBed":       
            for d in dbb:
                seat=d.normalbed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.normalbed=seat-1
                db.session.commit()
                
            
        elif bedtype=="HICUBed":      
            for d in dbb:
                seat=d.hicubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.hicubed=seat-1
                db.session.commit()

        elif bedtype=="ICUBed":     
            for d in dbb:
                seat=d.icubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.icubed=seat-1
                db.session.commit()

        elif bedtype=="VENTILATORBed": 
            for d in dbb:
                seat=d.vbed
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.vbed=seat-1
                db.session.commit()
        else:
            pass
        


        check=Hospitaldata.query.filter_by(hcode=hcode).first()
        if(seat>0 and check):
            res=Bookingpatient(srfid=srfid,bedtype=bedtype,hcode=hcode,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress)
            db.session.add(res)
            db.session.commit()
            
        else:
            flash("Something Went Wrong","danger")
        mail.send_message('COBEDS',sender='sriramya41096@gmail.com',recipients=[email],body=f"Dear User\n\nThanks for booking through our website and we're pleased to inform that your booking has been successful!\n\n One {bedtype} in the {hcode} Hospital has been allotted to you.So we request you to visit the hospital at the earliest possibility and check-in using your srfid .\n\n\t\t\t\t\t\t WE WISH YOU SPEEDY RECOVERY!!\n\n\nThank You" )
    
    return render_template("booking.html",query=query)




app.run(debug=True)