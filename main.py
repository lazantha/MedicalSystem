from flask import Flask,render_template,url_for,redirect,flash,session,make_response
from flask import jsonify,request
from allForms import UserLog,AdminLog,AdminSignUp,UserSignUp,UserForm,AdminInterface,SuperAdminInterface,TimeSchedule,MedicalClosingDate
from flask_bcrypt import Bcrypt
from database import MySql
from email_processor import email
from datetime import datetime
from binaryFiles import Binary
from logger import logging
from flask_mail import Mail,Message
import hashlib
from werkzeug.utils import secure_filename
import pdfkit
import uuid
import os
import time
host='localhost'
database='medical_db' 
user='root'

app=Flask(__name__)

app.config['SECRET_KEY']="kEY"
pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
app.config['PDFKIT_CONFIG'] = pdfkit_config
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt=Bcrypt(app)

#...............................................................
#error handling 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorhandler/404.html'), 404
#error handling 500
def internal_server_error(e):
  return render_template('errorhandler/500.html'), 500
#...............................................................

# Sessions Admin logging out
@app.route('/adminLogOut')
def adminLogOut():
    session.pop('user_name',None)
    return redirect(url_for('adminlog'))

# Sessions  it Admin logging out
@app.route('/superLogOut')
def superLogOut():
    session.pop('user_name',None)
    return redirect(url_for('adminlog'))
    

@app.route('/userLogOut')
def userLogOut():
    session.pop('user',None)
    return redirect(url_for('userlog'))




#password encryption method
def setHash(password):

	template=hashlib.new('SHA256')
	template.update(password.encode())
	hashed_password=template.hexdigest()
	return hashed_password

#password check
def passwordCheck(hashed_password,table):
    new_data=MySql(host,database,user)   
    if table=="admins":
        pass_query="SELECT password FROM admins WHERE password=%s;"
        data=(hashed_password,)
        # print("hashed_password",hashed_password)

        result=new_data.fetchOneForeing(pass_query,data)
        # print("result",result)

        if result=='No value':
            return 0
        else:
            return 1
        
    else:

        pass_query="SELECT password FROM super_admins WHERE password=%s;"
        data=(hashed_password,)
        print("data in super admin ",data)
        result=new_data.fetchOneForeing(pass_query,data)
        print("result in super admin ",result)
        if result=='No value':
            return 0
        else:
            return 1
        


#home page
@app.route('/')
def index():
    return render_template('index.html')

#...............................................................
#admin login page


@app.route('/adminlog',methods=['GET','POST'])
def adminlog():
    
    form=AdminLog()
    new_data=MySql(host,database,user)
    query="SELECT dep.calling_name FROM departments AS dep INNER JOIN super_admins AS sa ON dep.id=sa.dep_id;"
    department_list=new_data.fetchMultiVal(query)
    cleaned_values = [x[0] for x in department_list]
    
    form.department.choices=cleaned_values
    print("above the validate")
    if form.validate_on_submit():
        print("Below the validate")
        name=form.user_name.data
        password=form.password.data
        possition=form.possition.data
        department=form.department.data
        hashed_password=setHash(password)
        print("possition",possition)
        if possition=='HOD':
            query="SELECT sa.first_name,sa.password,dep.calling_name FROM super_admins AS sa INNER JOIN departments AS dep ON sa.dep_id=dep.id WHERE sa.first_name=%s AND sa.password=%s AND dep.calling_name=%s;"
            data=(name,hashed_password,department)
            exist_data=new_data.fetchAllMulForeing(query,data)
            if exist_data:
                
                session['super_name']=name
                session['super_password']=hashed_password
                
                page_list = {
                    'IT': 'itPanel',
                    'MANAGEMENT': 'managePanel',
                    'ACCOUNTENCY': 'accountPanel',
                    'ENGLISH': 'englishPanel',
                    'TOURISM': 'thmPanel',
                    'BUISNESS ADMINISTRATION':'buisnessAdminPanal',
                    'ENGINEERING':'engPanal',
                    'BUILDING SERVICE':'buildingPanal',
                    'AGRI':'agriPanal',
                    'FOOD TECHNOLOGY':'foodPanal',
                    'QS':'qsPanal',
                    'BUISNESS FINANCE':'finacePanal'
                }
                page_name=page_list.get(department)
                if page_name:
                    flash("success",'Login successful! ')
                    return redirect(url_for('superAdmin'))
                else:
                    
                    return redirect('adminlog')
            else:
                flash("danger","Login failed. Please check your username and password and try again.")
                return redirect('adminlog')
        
        else:
            print("Office")
            #admin
            query="SELECT first_name,password FROM admins WHERE first_name=%s AND password=%s;"
            print("upper")
            data=(name,hashed_password) 
            print("data",data)
            exist_data=new_data.fetchAllMulForeing(query,data)
            print("Exist data")
            print("exist_data ",exist_data)
            if exist_data:
                session['admin_name']=name
                session['admin_password']=hashed_password
                if 'admin_name' in session:
                    admin_name=session['admin_name']
                    flash("success",'Login successful!')
                    return redirect(url_for('admin'))
            else:
                flash("danger","Login failed. Please check your username and password and try again.")
                return redirect(url_for('adminlog'))
    else:
        print(form.errors) 


    return render_template('logIn/admin.html',form=form)



#super admins panel
#...............................................................................
def clean_values(values):
    cleaned_values = []
    for value in values:
        cleaned_value = []
        for item in value:
            if isinstance(item, bytearray):
                cleaned_value.append(item.decode('utf-8'))
            elif isinstance(item, date):
                cleaned_value.append(item.strftime('%Y-%m-%d'))
            else:
                cleaned_value.append(item)
        cleaned_values.append(tuple(cleaned_value))
    return cleaned_values

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import TAGS as ExifTags
import datetime

# Rest of the code
def metaData(path):
    img = Image.open(path)
    try:
        exif = {
        TAGS[k]: v

        for k, v in img._getexif().items()
        if k in TAGS}

        if 'Flash'  in exif and 'Model' in exif:
            date_time_str = exif['DateTime']
            date_time_obj = datetime.strptime(date_time_str, '%Y:%m:%d %H:%M:%S')
            date_value = date_time_obj.date()
            return date_value

        else:
            return 0      
        #"Not exist"

    except Exception as e:
        return -1
    #("Refuced it not captured one")





from datetime import datetime,timedelta

@app.route('/superAdmin', methods=['GET', 'POST'])
def superAdmin():
    form = SuperAdminInterface()
    new_data = MySql(host, database, user)
    def authtMail(row_id):
        subject="Medical Authenticatation System"
        email_query="SELECT email FROM students WHERE user_id=%s LIMIT 1"
        email=new_data.fetchOneForeing(email_query,(row_id,)).decode('utf-8')
        receiver=email
        message_content="ALL Right !Your Medical Form Authenticated By The Medical Panel THANK YOU !"
        email(receiver,subject,message_content)

    def rejectMail(row_id):
        subject="Medical Authenticatation System"
        email_query="SELECT email FROM students WHERE user_id=%s LIMIT 1;"
        email=new_data.fetchOneForeing(email_query,(row_id,))
        print("email",email)

        # receiver=email
        # message_content="Your Medical Rejected By Medical Panal ! due To Invalid Information"
        # email(receiver,subject,message_content)


    if 'super_name' in session and 'super_password' in session :
        name=session['super_name']
        password=session['super_password']

        query="SELECT dep.calling_name FROM departments AS dep INNER JOIN super_admins AS sa ON dep.id=sa.dep_id WHERE sa.first_name=%s AND sa.password=%s"
        data=(name,password)
        dep=new_data.fetchOneForeing(query,data)
        print(dep)
        result=new_data.getMainSuper(dep)
        
        print(result)
        import datetime
        cleaned_data = []

        for item in result:
            cleaned_item = (
                item[0],
                item[1].decode('utf-8'),  # Convert bytearray to string using UTF-8 encoding
                item[2],
                item[3].isoformat(),  # Convert date to ISO format string
                item[4].decode('utf-8')  # Convert bytearray to string using UTF-8 encoding
            )
            cleaned_data.append(cleaned_item)
            
        
        if request.method == 'GET':
            if 'action' in request.args and 'row_id' in request.args:
                action = request.args.get('action')
                if action=='itAuth':
                    row_id = request.args.get('row_id')
                #find a method for authenticate
                #get date of exam in medical information
                
                    data=(row_id,)
                    query_med="SELECT medical_sheet FROM medical_infor WHERE user_id=%s ORDER BY recorded_time DESC LIMIT 1;"
                    query_date="SELECT issued_date FROM medical_infor WHERE user_id=%s AND is_confirm=1 ORDER BY recorded_time DESC LIMIT 1;"
                    med_sheet=new_data.fetchOneForeing(query_med,data).decode('utf-8')

                    #get medical issued date
                    issued_date=new_data.fetchOneForeing(query_date,data)
                    path=f'static/images/{med_sheet}'
                    #get captured date
                    meta_date=metaData(path)
                    if meta_date==0:    
                        update_query = "UPDATE medical_infor SET is_authenticate = -1 WHERE user_id = %s LIMIT 1"
                        new_data.update(update_query,data)
                        #rejectMail(row_id)
                        flash('error','Rejected ! Error In Image ')
                        return redirect('superAdmin')
                                    
                    elif meta_date==-1:
                        update_query = "UPDATE medical_infor SET is_authenticate = -1 WHERE user_id = %s LIMIT 1"
                        new_data.update(update_query,data)
                        #rejectMail(row_id)
                        flash('error','Rejected ! Not Caputured Image')
                        return redirect('superAdmin')
                    else:
                        print(meta_date)
                        if meta_date==issued_date:

                            #-get exam held 
                            exm_held_query="SELECT ex.held_date FROM exams AS ex INNER JOIN subjects  AS sub ON ex.subject_id=sub.subject_id INNER JOIN medical_infor AS mi WHERE mi.user_id=%s LIMIT 1;"
                            held_date=new_data.fetchOneForeing(exm_held_query,data)
                            #-get affected date(medical From date)
                            aff_query="SELECT from_date FROM medical_infor WHERE user_id=%s LIMIT 1"
                            aff_date=new_data.fetchOneForeing(aff_query,data)
                            query_date="SELECT closing_date FROM closing_dates_list WHERE id=1;"
                            closing_date=new_data.fetchOne(query_date)

                            if issued_date<closing_date:
                                print("Issued date fine")
                                if aff_date<=held_date:

                                    print("Affected date fine")
                                    print("Authenticated: ")
                                    update_query = "UPDATE medical_infor SET is_authenticate = 1 WHERE user_id = %s LIMIT 1"
                                    new_data.update(update_query,row_id)
                                    #-authtMail(row_id)
                                    flash('success','Medical Authenticated !')
                                    return redirect('superAdmin')
                                else:

                                    #rejectMail(row_id)
                                    print("Affected date not fine")
                                    update_query = "UPDATE medical_infor SET is_authenticate = -1 WHERE user_id = %s LIMIT 1"
                                    new_data.update(update_query,data)
                                    flash('warning','Medical Rejected !')
                                    return redirect('superAdmin')
                                
                            else:

                                #rejectMail(row_id)
                                print("Issued data not fine: ")
                                update_query = "UPDATE medical_infor SET is_authenticate = -1 WHERE user_id = %s LIMI 1"
                                print(data)
                                new_data.update(update_query,data)
                                flash('warning','Medical Rejected !')
                                return redirect('superAdmin')
            

    return render_template('/Interfaces/superAdmin/super_admin.html', form=form,department=dep,name=name,
                            results=cleaned_data
                           )

#.....................................................................


#admin Sign
@app.route('/adminSign',methods=['GET','POST'])
def adminSign():
    form=AdminSignUp()
    new_data=MySql(host,database,user)
    query="SELECT calling_name FROM departments;"
    department_list=new_data.fetchMultiVal(query)
    cleaned_values = [x[0] for x in department_list]
    form.department.choices=cleaned_values
    
    if form.validate_on_submit():
        first_name=form.first_name.data
        last_name=form.last_name.data
        gender=form.gender.data
        email=form.email.data
        password=form.password.data
        possition=form.possition.data
        department=form.department.data
        hashed_password=setHash(password)
        print("hashed_password below",hashed_password)
           
        if possition=="OFFICE":
            #password Checking
            if passwordCheck(hashed_password,'admins')==1:
                print(passwordCheck(hashed_password,'admins'))
                
                flash("danger","Password Already Exist ! Try Different One ")
                return redirect(url_for('adminSign'))
            else:

                query="INSERT INTO admins (first_name,last_name,gender,email,password)VALUES(%s,%s,%s,%s,%s);"
                data=(first_name,last_name,gender,email,hashed_password)
                new_data.table(query,data)

                flash("success",f'Account Successfully created {first_name}!')
                return redirect(url_for('adminlog'))
        else:
            if passwordCheck(hashed_password,"super_admins")==1:
                print(passwordCheck(hashed_password,"super_admins"))

                flash("danger","Password Already Exist ! Try Different One")
                return redirect(url_for('adminSign'))
            else:

                dep_query="SELECT id FROM departments WHERE calling_name =%s;"
                dep_data=(department,)
                dep_id=new_data.fetchOneForeing(dep_query,dep_data)
                query="INSERT INTO super_admins (dep_id,first_name,last_name,gender,email,password)VALUES(%s,%s,%s,%s,%s,%s);"
                data=(dep_id,first_name,last_name,gender,email,hashed_password)
                new_data.table(query,data)
                flash("success",f'Account Successfully created {first_name}!')
                return redirect(url_for('adminlog'))

        
    
    else:
        pass

        # print("Validation failed")
        # print(form.errors)

    
           
    return render_template('signup/admin.html',form=form)

#user login Page
@app.route('/userlog',methods=['GET','POST'])
def userlog():
    new_user=UserLog()
    new_data=MySql(host,database,user)
    if new_user.validate_on_submit():
        user_name=new_user.user_name.data
        password=new_user.password.data
        hashed_password=setHash(password)
        query="SELECT first_name,password FROM students WHERE first_name=%s AND password=%s"
        data=(user_name,hashed_password)
        exist=new_data.fetchAllMulForeing(query,data)
        
        if exist:
            session['student_name'] = user_name
            session['student_password']=hashed_password
            flash("success",'Login successful! ')
            return redirect(url_for('user_home'))
            
        else:
             flash("danger","Login failed. Please check your username and password and try again.")
             return redirect(url_for('userlog'))
            # if 'name' in session:
            #     return redirect(url_for('user_home'))
            # return redirect(url_for('userlog'))
        
            # flash('Please recheck user name and password','warning')
    return render_template('logIn/user.html',form=new_user)

#user Sign
@app.route('/userSign',methods=['GET','POST'])
def userSign():
    new_sign=UserSignUp()
    new_sql=MySql(host,database,user)
    #department query
    query="SELECT calling_name FROM departments;"
    department_list=new_sql.fetchMultiVal(query)
    cleaned_values = [x[0] for x in department_list]
    # cleaned_data = [value[0].decode() for value in department_list]

    new_sign.department.choices=cleaned_values
    query="SELECT type FROM student_type;"
    student_type=new_sql.fetchMultiVal(query)
    # cleaned_data = [value[0].decode() for value in student_type]
    cleaned_values_types = [x[0] for x in student_type]
    new_sign.mode.choices=cleaned_values_types

    
    if new_sign.validate_on_submit():
        first_name=new_sign.first_name.data
        last_name=new_sign.last_name.data
        index_number=new_sign.index_number.data
        mode=new_sign.mode.data
        mode_query="SELECT id FROM student_type WHERE type=%s;"
        mode_data=(mode,)
        mode_id=new_sql.fetchOneForeing(mode_query,mode_data)
        gender=new_sign.gender.data
        department=new_sign.department.data
        dep_query="SELECT id FROM departments WHERE calling_name=%s;"
        dep_data=(department,)
        dep_id=new_sql.fetchOneForeing(dep_query,dep_data)   
        email=new_sign.email.data
        password=new_sign.password.data
        hashed_password=setHash(password)
        confirm_password=new_sign.confirm_password.data
        hashed_password_confirm=setHash(confirm_password)
        id_card=new_sign.id_card.data
        
        if hashed_password==hashed_password_confirm:
                
                pass_query="SELECT password,email,index_number FROM students WHERE password=%s OR email=%s OR index_number=%s;"
                data=(hashed_password,email,index_number)
                result=new_sql.fetchAllMulForeing(pass_query,data)
                if result:
                    flash("danger","Email , Password or Index Number Already Exist ! ")
                    print(" Already Exist")
                    return redirect('userSign')
                else:

                    # Grab image name
                    img_name = secure_filename(id_card.filename)
                    uniq_name = str(uuid.uuid1()) + '_' + img_name
                    # Save image
                    save_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], uniq_name)
                    id_card.save(save_path)
                    # Save to db
                    id_card = uniq_name

                    
                    main_query="INSERT INTO students(department_id,student_type_id,first_name,last_name,index_number,gender,email,password,id_card)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                    main_data=(dep_id,mode_id,first_name,last_name,index_number,gender,email,hashed_password_confirm,id_card)
                    new_sql.table(main_query,main_data)
                    flash("success","Your Account Successfully Created !")
                    return redirect('userlog')

        
        else:
            return redirect('userSign')
        
    return render_template('signup/user.html',form=new_sign)

#...............................................................
@app.route('/user_home',methods=['GET','POST'])
def user_home():
    new_sql=MySql(host,database,user)
    if 'student_name' in session and 'student_password' in session:

        new_data=MySql(host,database,user)
        name=session['student_name']
        password=session['student_password']
        data=(name,password)
        query="SELECT sub.subject_name,att.attempt,med.is_confirm,is_authenticate FROM medical_infor AS med INNER JOIN subjects AS sub ON sub.subject_id=med.subject_id INNER JOIN attempts AS att ON att.id = med.attempt_id INNER JOIN students AS stu ON stu.user_id=med.user_id WHERE stu.first_name=%s AND stu.password=%s;"
        data=(name,password)
        result=new_sql.fetchAllMulForeing(query,data)
        print("result",result)
        data = [(bytearray(b'Structured Programming'), 2, 0, 0)]
        # cleaned_data = [(item[0].decode(), item[1], item[2], item[3]) for item in result]


        from datetime import datetime, timedelta,date
        # current_datetime = datetime.today()
        # query_date="SELECT closing_date FROM closing_dates_list ORDER BY  set_date DESC LIMIT 1;"
        # closing_date=new_sql.fetchOne(query_date)
        # print("Date: ",closing_date)
        # closing_date = date.fromisoformat(str(closing_date))
        # current_datetime = date.today()
        # remaining_days = (closing_date - current_datetime).days
        
        

            
                    

    else:
        return redirect('userlog')
    

    return render_template('Interfaces/user/userHome.html',name=name,
                            # result=cleaned_data,
                            # remaining_days=remaining_days,
                            # closing_date=closing_date


                               )
    








#..............................................................................
#about page
@app.route('/about')
def about():
    return render_template('about.html')
#contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')
#..............................................................................




#main form
@app.route('/request_form',methods=['GET','POST'])
def request():
    from flask import request
    new_form=UserForm()
    new_data=MySql(host,database,user)
    new_binary=Binary()
    query="SELECT attempt FROM attempts;"
    attempts = new_data.fetchMultiVal(query)
    cleaned_data = [str(value[0].decode()) if isinstance(value[0], bytes) else str(value[0]) for value in attempts]
    new_form.attempt.choices=cleaned_data
    query="SELECT type FROM medical_type;"
    types=new_data.fetchMultiVal(query)
    
    cleaned_data = [value[0].strip() for value in types]
    

    new_form.med_type.choices=cleaned_data
    if 'student_name' in session and 'student_password' in session:
        name=session['student_name']
        password=session['student_password']
        query="SELECT dep.calling_name FROM departments AS dep INNER JOIN students AS s ON dep.id=s.department_id WHERE s.first_name=%s AND password=%s;"
        data=(name,password)
        department=new_data.fetchOneForeing(query,data).strip()
        print(department)
        user_query="SELECT user_id FROM students WHERE first_name=%s AND password=%s;"
        user_id=new_data.fetchOneForeing(user_query,data)
        
        years=new_data.getUniqeCountYear(department) 
        years = [x[0] for x in years]
        new_form.year.choices=years
        semester=new_data.getUniqeCountSem(department)
        sem = [x[0] for x in semester]
        new_form.semester.choices=sem
        subject_list=new_data.getUniqeCountSub(department)
        # subjects = [item[0].decode() for item in subject_list]
        
        subjects = [item[0] for item in subject_list]
        
        new_form.subject.choices=subjects
        if new_form.validate_on_submit():
            
            date_issued=new_form.date_issued.data
            start_date=new_form.start_date.data
            end_date=new_form.end_date.data
            attempt=new_form.attempt.data
            doc_name=new_form.doc_name.data
            hospital=new_form.hospital.data
            med_type=new_form.med_type.data
            med_image=new_form.med_image.data
            year=new_form.year.data
            semester=new_form.semester.data
            subject=new_form.subject.data

            med_query="SELECT id FROM medical_type WHERE type=%s;"
            med_data=(med_type,)
            med_id=new_data.fetchOneForeing(med_query,med_data)
            attempt_query="SELECT id FROM attempts WHERE attempt=%s;"
            att_data=(attempt,)
            att_id=new_data.fetchOneForeing(attempt_query,att_data)
            sub_query="SELECT subject_id FROM subjects WHERE subject_name =%s;"
            sub_data=(subject,)
            sub_id=new_data.fetchOneForeing(sub_query,sub_data)
            #checking if exist same subject in exam table
            check_query="SELECT mi.subject_id FROM medical_infor AS mi INNER JOIN students AS st ON mi.user_id=st.user_id WHERE st.first_name=%s AND st.password=%s AND mi.subject_id=%s;"
            sub_data=(name,password,sub_id)
            result=new_data.fetchAllMulForeing(check_query,sub_data)
            if result:
                flash(f'You Have Already Submitted To This {subject} Subject !')
                return redirect(url_for('request'))
            else:

                #get values from exams acording to subject
                exam_query="SELECT held_date FROM exams WHERE subject_id=%s;"
                s_time_query="SELECT start_time FROM exams WHERE subject_id=%s;"
                e_time_query="SELECT end_time FROM exams WHERE subject_id=%s;"
                location_query="SELECT location FROM exams WHERE subject_id=%s;"
                med_data=(sub_id,)
                exam_date=new_data.fetchOneForeing(exam_query,med_data)
                start_time=new_data.fetchOneForeing(s_time_query,med_data)
                end_time=new_data.fetchOneForeing(e_time_query,med_data)

                location=new_data.fetchOneForeing(location_query,med_data)
                print(location)

                # print(f"{exam_date}: {start_time}: {end_time}: {location}")

                
                # Grab image name
                img_name = secure_filename(med_image.filename)
                uniq_name = str(uuid.uuid1()) + '_' + img_name
                # Save image
                save_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], uniq_name)
                med_image.save(save_path)
                # Save to db
                med_image = uniq_name
                
                main_query="INSERT INTO medical_infor(user_id,med_type_id,subject_id,attempt_id,exam_date,started_time,end_time,exam_location,issued_date,from_date,to_date,doctor_name,hospital,medical_sheet)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                main_data=(user_id,med_id,sub_id,att_id,exam_date,start_time,end_time,location,date_issued,start_date,end_date,doc_name,hospital,med_image)
                new_data.table(main_query,main_data)
                
                flash("Form Susscessfully Submited ! We will notify you once your form has been accepted.")
                return redirect(url_for('user_home'))
        return render_template('Interfaces/user/mainform.html',form=new_form)


#office
from datetime import date
@app.route('/admin',methods=['GET','POST'])
def admin():
    from flask import request
    new_data=MySql(host,database,user)
    date_query="SELECT closing_date FROM closing_dates_list ORDER BY  set_date DESC LIMIT 1;"
    date=new_data.fetchOne(date_query)
    #almost done !
    if 'admin_name' in session:
                closing_date=None
                if request.method=='GET' and 'date' in request.args:

                    closing_date=request.args.get('date')
                    if closing_date:
                        date_pattern = f'%{closing_date}%'
                        date_query="SELECT closing_date FROM closing_dates_list WHERE closing_date LIKE %s;"
                        date=new_data.fetchOneForeing(date_query,(date_pattern,))
                        print("date",date)

                        if date =='No value':
                            print("can insert here !")
                            query_date="INSERT INTO closing_dates_list (closing_date) VALUES(%s);"
                            data=(closing_date,)
                            new_data.table(query_date,data)
                            flash('success','Closing date has been set ')
                            return redirect('admin')
                        
                        else:
                            print("cant insert here !")
                            flash('warning','Already Added !')
                            return redirect('admin')

                            
                        print("Out of the both condition")                            

                    else:
                        flash('warning','Closing date not set yet !')
                            

                user_name=session['admin_name']
                new_admin=AdminInterface()
                new_super_admin=SuperAdminInterface()
                new_data=MySql(host,database,user)
                query="SELECT COUNT(*) FROM medical_infor WHERE is_confirm=0 AND is_authenticate=0;"
                total=new_data.fetchOne(query)
                it=new_data.getCount('IT')
                acc=new_data.getCount('ACCOUNTANCY')
                mng=new_data.getCount('MANAGEMENT')                
                eng=new_data.getCount('ENGLISH')
                thm=new_data.getCount('TOURISM')

            #main records
                result_it=new_data.getMain('IT')
                result_acc=new_data.getMain('ACCOUNTANCY')
                result_mng=new_data.getMain('MANAGEMENT')                
                result_eng=new_data.getMain('ENGLISH')
                result_thm=new_data.getMain('TOURISM')
                print(result_it)
                
                update_query = "UPDATE medical_infor SET is_confirm = %s WHERE user_id = %s"
                def injectAction(row_id,value,update_query):
                        update_data = (value,row_id)
                        new_data.update(update_query, update_data)
                        if value==1:
                            flash("success","Medical Accepted !")
                            return redirect('admin')
                        else:
                            flash("danger","Medical Rejected !")
                            return redirect('admin')
                def acceptMail(row_id): 
                    subject="Medical Authenticatation System"
                    email_query="SELECT email FROM students WHERE user_id=%s;"
                    email=new_data.fetchOneForeing(email_query,(row_id,)).decode('utf-8')
                    receiver=email
                    print("email",receiver)
                    message_content="Allmost Done !Your Medical Form Accepted By The Admin and We Let You Know When Authenticate You Medical By the Medical Panel"
                    # email(receiver,subject,message_content)

                def rejectMail(row_id,message):
                    subject="Medical Authenticatation System"
                    email_query="SELECT email FROM students WHERE user_id=%s;"
                    email=new_data.fetchOneForeing(email_query,(row_id,)).decode('utf-8')
                    receiver=email

                    if message =="":    
                        message_content=(f"Your Medical Rejected ! Please Provide Accurate Information")
                        email(receiver,subject,message_content)
                        
                    else:
                        message_content=(f"Your Medical Rejected ! Please Provide Accurate Information Causing::  {message}")
                        email(receiver,subject,message_content)


                if 'action' in request.args and 'row_id' in request.args or'message' in request.args:
                    action=request.args.get('action')
                    row_id=request.args.get('row_id')
                    message=request.args.get('message')
                    
                    if action=='itAccept':
                        injectAction(row_id,1,update_query)
                        acceptMail(row_id)
                        return redirect('admin')
                    elif action=='itReject':
                        injectAction(row_id,-1,update_query)
                        rejectMail(row_id,message)
                        return redirect('admin')
                    #accoun
                    elif action=='accAccept':
                        injectAction(row_id,1,update_query)
                        acceptMail(row_id)
                        return redirect('admin')
                    elif action=='accReject':
                        injectAction(row_id,-1,update_query)
                        rejectMail(row_id,message)
                        return redirect('admin')
                    #manage

                    elif action=='manaAccept':
                        injectAction(row_id,1,update_query)
                        acceptMail(row_id)
                        return redirect('admin')
                    elif action=='manaReject':
                        injectAction(row_id,-1,update_query)
                        rejectMail(row_id,message)
                        return redirect('admin')
                    #thm

                    elif action=='thmAccept':
                        injectAction(row_id,1,update_query)
                        acceptMail(row_id)
                        return redirect('admin')
                    elif action=='thmReject':
                        injectAction(row_id,-1,update_query)
                        rejectMail(row_id,message)
                        return redirect('admin')

                    elif action=='engAccept':
                        injectAction(row_id,1,update_query)
                        acceptMail(row_id)
                        return redirect('admin')
                    elif action=='engReject':
                        injectAction(row_id,-1,update_query)
                        rejectMail(row_id,message)
                        return redirect('admin')


    return render_template('Interfaces/admin/admin.html',form=new_admin,
                            user_name=user_name,
                            count=total,
                            it_count=it,
                            account_count=acc,
                            manage_count=mng,
                            thm_count=thm,
                            english_count=eng,
                            # result_it=cleaned_values_it,
                            # result_thm=cleaned_values_thm,
                            # result_en=cleaned_values_eng,
                            # result_manage=cleaned_values_mng,
                            # result_account=cleaned_values_acc,

                            closing_date=date
                           )




#time schedule 


from flask import request
import datetime
#for time table values
def heavyClean(values):
        cleaned_values=[]
        for val in values:
            cleaned_tuple = (

                val[0].decode('utf-8'),  # Convert bytearray to string
                val[1].decode('utf-8'),
                val[2].strftime('%B %d, %Y'),# Format date as "Month day, Year"
                str(val[3]),  # Convert timedelta to string
                str(val[4]),  # Convert timedelta to string
                val[5].decode('utf-8')  # Convert bytearray to string 
                
            )
            cleaned_values.append(cleaned_tuple)
        return cleaned_values

from datetime import datetime, timedelta

def convert_to_strings_and_format_date(values):
    formatted_values = []
    for val in values:
        formatted_tuple = (
            str(val[0]),  # Convert to string
            str(val[1]),  # Convert to string
            val[2].strftime('%B %d, %Y'),  # Format date as "Month day, Year"
            str(val[3]),  # Convert timedelta to string
            str(val[4]),  # Convert timedelta to string
            str(val[5])   # Convert to string
        )
        formatted_values.append(formatted_tuple)
    return formatted_values

@app.route('/exams', methods=['GET', 'POST'])
def exams():
    form = TimeSchedule()
    new_data = MySql(host,database,user)
    if 'super_name' and 'super_password' in session:
        name=session['super_name']
        password=session['super_password']
        query="SELECT dep.calling_name FROM super_admins AS sa INNER JOIN departments AS dep ON dep.id=sa.dep_id WHERE sa.first_name=%s AND sa.password=%s;"
        data=(name,password)
        dep=new_data.fetchOneForeing(query,data)
        print(dep)
        # .decode().strip()
        year_data = new_data.getUniqeCountYear(dep)
        semester_data = new_data.getUniqeCountSem(dep)
        years = [x[0] for x in year_data]
        semesters = [x[0] for x in semester_data]
        subject_query="SELECT s.subject_name FROM subjects AS s INNER JOIN departments AS dep ON dep.id=s.department_id WHERE dep.calling_name=%s;"
        data=(dep,)
        subjects=new_data.fetchAllMulForeing(subject_query,data)
        # Convert tuples to strings
        subject_list = [item[0] for item in subjects]
        # cleaned_subjects = [item[0].decode() for item in subjects]


        form.subject_name.choices=subject_list
        data=(dep,)
        values=new_data.getValues(data)
        cleaned_values=convert_to_strings_and_format_date(values)
        # cleaned_values=heavyClean(values)
        

    if form.validate_on_submit():
        
        new_subject=form.subject_name.data
        date=form.date.data
        start_time=form.start_time.data
        end_time=form.end_time.data
        location=form.location.data
        sub_query="SELECT subject_id FROM subjects WHERE subject_name=%s;"
        sub_data=(new_subject,)
        new_sub_id=new_data.fetchOneForeing(sub_query,sub_data)
        syll_query="SELECT id FROM syllabus WHERE syllabus_type=%s;"
        syll_data=('OLD',)
        syll_id=new_data.fetchOneForeing(syll_query,syll_data)
        
        if 'super_name' and 'super_password' in session:
            name=session['super_name']
            password=session['super_password']
            super_query="SELECT admin_id FROM super_admins WHERE first_name=%s AND password=%s;"
            super_data=(name,password)
            super_id=new_data.fetchOneForeing(super_query,super_data)

            check_query="SELECT subject_id FROM exams WHERE subject_id=%s;"
            check_data=(new_sub_id,)
            subject_data=new_data.fetchAllMulForeing(check_query,check_data)
            print(subject_data)
            print(type(subject_data))
            if subject_data:
                print("Not empty")
                flash("Already added ")
                return redirect('exams')
            else:
                print(" empyt")
                main_query = "INSERT INTO exams (subject_id, syllabus_id, super_admin_id, held_date, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                main_data = (new_sub_id, syll_id, super_id, date, start_time, end_time, location)
                new_data.table(main_query, main_data)
                return redirect(url_for('exams'))
                print("added")

            
            
        
    if request.method == 'GET':
            import datetime
            row_id = request.args.get('row_id')
            subject=request.args.get('subject')
            code=request.args.get('code')
            location=request.args.get('location')
            date=request.args.get('date')

            subject_pattern = f'%{subject}%'
            code_pattern = f'%{code}%'
            location_pattern = f'%{location}%'
            date_pattern = f'%{date}%'
            
            

            search_query="SELECT sub.subject_name,sub.subject_code ,ex.location,ex.held_date FROM exams AS ex INNER JOIN subjects AS sub ON ex.subject_id=sub.subject_id WHERE sub.subject_name LIKE %s OR sub.subject_code LIKE %s OR ex.location LIKE %s OR ex.held_date LIKE %s;"
            data_set=(subject_pattern,code_pattern,location_pattern,date_pattern)
            result_set=new_data.fetchAllMulForeing(search_query,data_set)
            # print(result_set)
            search_list=[]
            if result_set and isinstance(result_set[0], tuple):
                search = [
                    item.decode('utf-8') if isinstance(item, bytearray) else item.strftime('%Y-%m-%d') if isinstance(item, datetime.date) else item
                    for item in result_set[0]
                ]
                search_list.append(search)
                
                    
            session['subject_code'] = row_id
            if 'subject_code' in session:
                subject_code=session['subject_code']
                query="SELECT subject_id FROM subjects WHERE subject_code=%s;"
                data=(subject_code,)
                subject_id=new_data.fetchAllMulForeing(query,data)
                if subject_id:
                    print(subject_id[0][0])
                    delete_query = "DELETE FROM exams WHERE subject_id=%s;"
                    delete_data = (subject_id[0][0],)
                    new_data.deleteMulti(delete_query, delete_data)
                    return redirect(url_for('exams'))




    return render_template('Interfaces/superAdmin/exams.html', form=form,
                           form_data=cleaned_values,
                           department=dep,
                           user_name=name,
                           result_set=search_list
                           )

from allForms import AddNewSubjects
@app.route('/addSubjects', methods=['POST', 'GET'])
def addSubjects():
    form = AddNewSubjects()
    new_data = MySql(host,database,user)
    
    if 'super_name' in session and 'super_password' in session:
        name = session['super_name']
        password = session['super_password']
        query = "SELECT dep.calling_name FROM departments AS dep INNER JOIN super_admins as sa ON dep.id=sa.dep_id WHERE sa.first_name=%s AND sa.password=%s;"
        data = (name, password)
        dep = new_data.fetchOneForeing(query, data).decode().strip()
        year = new_data.getUniqeCountYear(dep)
        sem = new_data.getUniqeCountSem(dep)
        cleaned_year = [value[0] for value in year]
        cleaned_sem = [str(value).strip("()") for value in sem]
        
        form.year.choices = cleaned_year
        form.semester.choices = cleaned_sem 
    
    if form.validate_on_submit():
        subject_name = form.subject_name.data
        subject_code = form.subject_code.data
        year = form.year.data
        semester = form.semester.data
        print(subject_name)
        
        dep_query = "SELECT id FROM departments WHERE calling_name = %s;"
        dep_data = (dep,)
        dep_id = new_data.fetchOneForeing(dep_query, dep_data)
        exist_query="SELECT subject_name FROM subjects WHERE subject_name =%s;"
        exist_data=(subject_name,)
        exist_=new_data.fetchAllMulForeing(exist_query,exist_data)
        if exist_:
                
                print("Not empty")
                flash("Already added ")
                return redirect('addSubjects')
        else:

            query = "INSERT INTO subjects (department_id, subject_name, subject_code, year, semester) VALUES (%s, %s, %s, %s, %s);"
            data=(dep_id,subject_name,subject_code,year,semester)
            new_data.table(query,data)
            return redirect(url_for('addSubjects'))
                

        
        
    else:
        print("Form not validated")

    return render_template('Interfaces/superAdmin/new_subjects.html', form=form)




from flask import request
@app.route('/updateExam', methods=['POST', 'GET'])
def updateExam():
    form = TimeSchedule()
    new_sql = MySql(host,database,user)
    
    if 'super_name' in session and 'super_password' in session:
        name = session['super_name']
        password = session['super_password']
        
        query = "SELECT dep.calling_name FROM super_admins AS sa INNER JOIN departments AS dep ON dep.id=sa.dep_id WHERE sa.first_name=%s AND sa.password=%s;"
        data = (name, password)
        dep = new_sql.fetchOneForeing(query, data).decode().strip()
        
        subject_query = "SELECT s.subject_name FROM subjects AS s INNER JOIN departments AS dep ON dep.id=s.department_id WHERE dep.calling_name=%s;"
        data = (dep,)
        subjects = new_sql.fetchAllMulForeing(subject_query, data)
        cleaned_subjects = [item[0].decode() for item in subjects]
        
        form.subject_name.choices = [(subject, subject) for subject in cleaned_subjects]
        
        if request.method == 'GET':
            row_id = request.args.get('row_id')
            session['subject_code'] = row_id
        
        if 'subject_code' in session:
            subject_code = session['subject_code']
            
            if form.validate_on_submit():
                subject_name = form.subject_name.data
                date = form.date.data
                start_time = form.start_time.data
                end_time = form.end_time.data
                location = form.location.data
                #get new subject id
                new_query="SELECT subject_id FROM subjects WHERE subject_name =%s;"
                new_data=(subject_name,)
                new_subject_id=new_sql.fetchOneForeing(new_query,new_data)
                #get old subject id
                old_query="SELECT subject_id FROM subjects WHERE subject_code =%s;"
                old_data=(subject_code,)
                old_subject_id=new_sql.fetchOneForeing(old_query,old_data)
                
                
                update_query = "UPDATE exams SET subject_id=%s, held_date=%s, start_time=%s, end_time=%s, location=%s WHERE subject_id=%s"
                update_data = (new_subject_id, date, start_time, end_time, location, old_subject_id)
                new_sql.update(update_query, update_data)


                return redirect(url_for('exams'))
                


    return render_template('Interfaces/superAdmin/edit_exams.html',form=form)


#reports
from flask import make_response
from fpdf import FPDF
from allForms import ReportDepartments    
from flask import request, redirect, render_template



@app.route('/adminReportsForm', methods=["POST", "GET"])
def adminReportsForm():
    form=ReportDepartments()
    new_data = MySql(host, database, user)
    dep_query = "SELECT DISTINCT(dep.calling_name) FROM medical_infor AS mi INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id;"
    departments = new_data.fetchMultiVal(dep_query)
    # Convert byte arrays to strings
    departments = [(item[0].decode('utf-8'), item[0].decode('utf-8')) for item in departments]
    # Fetch academic years and semesters for populating form choices
    query = "SELECT DISTINCT(year) FROM subjects;"
    academic_years = new_data.fetchMultiVal(query)
    query = "SELECT DISTINCT(semester) FROM subjects;"
    semesters = new_data.fetchMultiVal(query)
    type_query="SELECT type FROM student_type;"
    types=new_data.fetchMultiVal(type_query)
    clean_types = [item[0].decode() for item in types]
    
    
    # Extract values from the fetched data
    cleaned_list_yrs = [value[0] for value in academic_years]
    cleaned_list_sems = [value[0] for value in semesters]
    # Set choices for the form fields
    form.semesters.choices = [(value, value) for value in cleaned_list_sems]
    form.years.choices = [(value, value) for value in cleaned_list_yrs]
    form.departments.choices = departments

    return render_template('Interfaces/admin/admin_report_form.html',form=form)


@app.route('/adminReports', methods=["POST", "GET"])
def adminReports():
    new_data = MySql(host, database, user)
    form = ReportDepartments()
    
    # Set default values for variables
    year = None
    department = None
    reg_count = None
    med_count = None
    admin_count = None
    confirmed = None
    unconfirmed = None
    dep_year = None
    dep_semester = None
    cleaned_data = []
    cleaned_data_rejected = []
    cleaned_data_accepted = []
    cleaned_data_aff = []
    glance_view_data = []
    affected_data = []

    # Check if the form is submitted via POST and is valid
        # Get form data
    date = form.date.data.strftime('%Y-%m-%d')
    department = form.departments.data
    dep_year = form.years.data
    dep_semester = form.semesters.data
    std_type = form.student_type.data

        # Split the date
    date_parts = date.split('-')
    year = date_parts[0]
    search_pattern = f'{year}%'

        # Fetch data counts
    query_student_count = "SELECT COUNT(*) FROM students;"
    reg_count = new_data.fetchOne(query_student_count)

    query_medicals = "SELECT COUNT(*) FROM medical_infor WHERE exam_date LIKE %s"
    med_count = new_data.fetchOneForeing(query_medicals, (search_pattern,))

    query_admins = "SELECT COUNT(*) FROM super_admins;"
    admin_count = new_data.fetchOne(query_admins)

    query_is_confirmed = "SELECT COUNT(*) FROM medical_infor WHERE is_confirm=1 AND exam_date LIKE %s;"
    confirmed = new_data.fetchOneForeing(query_is_confirmed, (search_pattern,))

    # UNCONFIRMED MEDICALS
    query_unconfirmed = "SELECT COUNT(*) FROM medical_infor WHERE is_confirm=-1 AND exam_date LIKE %s;"
    unconfirmed = new_data.fetchOneForeing(query_unconfirmed, (search_pattern,))
    from datetime import datetime,date
        # Fetch main data
    query_main = "SELECT stu.index_number, stu.first_name, stu.last_name, mi.exam_date, mi.exam_location, sub.subject_name, sub.year, sub.semester FROM medical_infor AS mi INNER JOIN students AS stu ON mi.user_id=stu.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id INNER JOIN student_type as stt ON stu.student_type_id=stt.id WHERE mi.exam_date LIKE %s AND dep.calling_name=%s AND stt.type=%s;"
    data = (search_pattern, department, std_type)
    data_main = new_data.fetchAllMulForeing(query_main, data)
    cleaned_data = [
    tuple(item.decode('utf-8') if isinstance(item, bytearray) else item for item in row)
    for row in data_main]

        # CATEGORIZED
    categorized_query = "SELECT stu.index_number, stu.first_name, stu.last_name, sub.subject_name, mi.exam_date, mi.is_confirm, mi.is_authenticate FROM medical_infor AS mi INNER JOIN students AS stu ON mi.user_id=stu.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=sub.department_id INNER JOIN student_type as stt ON stu.student_type_id=stt.id  WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND mi.exam_date LIKE %s AND stt.type=%s ;"
    cat_data = (department, dep_year, dep_semester, search_pattern, std_type)
    categorized_data = new_data.fetchAllMulForeing(categorized_query, cat_data)

    cleaned_data = [
        (
                item[0].decode('utf-8'),  # Convert bytearray to string
                item[1].decode('utf-8'),
                item[2].decode('utf-8'),
                item[3].decode('utf-8'),
                item[4].strftime('%Y-%m-%d'),  # Format date as string
                item[5],
                item[6]
        )
        for item in categorized_data
        ]

        # REJECTED
    rejected_query = "SELECT stu.index_number, stu.first_name, stu.last_name FROM medical_infor AS mi INNER JOIN students AS stu ON mi.user_id=stu.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id INNER JOIN student_type as stt ON stu.student_type_id=stt.id  WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND mi.exam_date LIKE %s AND mi.is_confirm=-1 AND stt.type=%s;"
    reject_data = new_data.fetchAllMulForeing(rejected_query, cat_data)
    cleaned_data_rejected = [tuple(b.decode('utf-8') for b in item) for item in reject_data]

    accept_query = "SELECT stu.index_number, stu.first_name, stu.last_name FROM medical_infor AS mi INNER JOIN students AS stu ON mi.user_id=stu.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id INNER JOIN student_type as stt ON stu.student_type_id=stt.id WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND mi.exam_date LIKE %s AND mi.is_confirm= 1 AND stt.type=%s;"
    accept_data = new_data.fetchAllMulForeing(accept_query, cat_data)
    cleaned_data_accepted = [tuple(b.decode('utf-8') for b in item) for item in accept_data]

        # Affected subjects
    most_affected_query = "SELECT sub.subject_name,COUNT(*) AS count FROM medical_infor AS mi INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id INNER JOIN students AS stu ON mi.user_id=stu.user_id INNER JOIN student_type AS stt ON stu.student_type_id=stt.id  WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND mi.exam_date LIKE %s  AND stt.type=%s GROUP BY mi.subject_id ORDER BY count DESC;"
    affected_data = new_data.fetchAllMulForeing(most_affected_query, cat_data)
    cleaned_data_aff = [(entry[0].decode('utf-8'), entry[1]) for entry in affected_data]
     
    rendered = render_template('Interfaces/admin/sample_report.html', form=form, year=year, department=department,
                           reg_count=reg_count,
                           med_count=med_count,
                           admin_count=admin_count,
                           confirmed=confirmed,
                           unconfirmed=unconfirmed,
                           glance_view_data=glance_view_data,
                           cleaned_sub_data=cleaned_data,
                           rejected_data=cleaned_data_rejected,
                           confirmed_data=cleaned_data_accepted,
                           dep_year=dep_year,
                           semesters=dep_semester,
                           affected=cleaned_data_aff
                           )
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response

    return render_template('Interfaces/admin/sample_report.html', form=form, year=year, department=department,
                           reg_count=reg_count,
                           med_count=med_count,
                           admin_count=admin_count,
                           confirmed=confirmed,
                           unconfirmed=unconfirmed,
                           glance_view_data=glance_view_data,
                           cleaned_sub_data=cleaned_data,
                           rejected_data=cleaned_data_rejected,
                           confirmed_data=cleaned_data_accepted,
                           dep_year=dep_year,
                           semesters=dep_semester,
                           affected=cleaned_data_aff
                           )


from allForms import SuperAdminReport
from datetime import datetime,date

@app.route('/superReport',methods=['POST','GET'])
def superReport():
    form=SuperAdminReport()
    new_data=MySql(host,database,user)
    if 'super_name' and 'super_password' in session:
        name=session['super_name']
        password=session['super_password']
        dep_query="SELECT dep.calling_name FROM departments AS dep INNER JOIN super_admins AS sa ON dep.id =sa.dep_id WHERE sa.first_name=%s AND sa.password=%s;"
        data=(name,password)
        dep=new_data.fetchOneForeing(dep_query,data).decode().strip()
        query_yrs="SELECT DISTINCT(sub.year) FROM subjects AS sub INNER JOIN departments AS dep ON sub.department_id=dep.id WHERE DEP.calling_name=%s;"
        data_dep=(dep,)
        query_semester="SELECT DISTINCT(sub.semester) FROM subjects AS sub INNER JOIN departments AS dep ON sub.department_id=dep.id WHERE DEP.calling_name=%s;"
        sem=new_data.fetchAllMulForeing(query_semester,data_dep)
        yrs=new_data.fetchAllMulForeing(query_yrs,data_dep)
        cleaned_yrs = [item[0] for item in yrs]
        cleaned_sem = [item[0] for item in sem]
        form.years.choices=cleaned_yrs
        form.semesters.choices=cleaned_sem

    return render_template('Interfaces/superAdmin/superReport.html',form=form)



@app.route('/getPostValues',methods=['GET','POST'])
def getPostValues():
    form=ReportDepartments()
    date = form.date.data.strftime('%Y-%m-%d')
    department = form.departments.data
    dep_year = form.years.data
    dep_semester = form.semesters.data
    std_type = form.student_type.data
    print("date: ",date)
    print("department: ",department)
    print("dep_year: ",dep_year)
    print("semester: ",dep_semester)
    print("std type: ",std_type)

    
    
    
    

    return "From method" 

@app.route('/superAdminReports',methods=['POST','GET'])
def superAdminReports():
    new_data=MySql(host,database,user)
    form=SuperAdminReport()
    from datetime import datetime,date

    student_count=None
    auth_count=None
    nonauth_count=None
    auth_count=None
    non_auth_count=None
    dep=None
    year=None
    cleaned_data_auth=[]
    cleaned_data_un_auth=[]        
    if 'super_name' and 'super_password' in session:
        name=session['super_name']
        password=session['super_password']
        print("name",name)

        exm_year=form.date.data.strftime('%Y-%m-%d')
        academic_yre=form.years.data
        semester=form.semesters.data
        student_type=form.student_type.data
        date_parts = exm_year.split('-')
        year = date_parts[0]
        search_pattern = f'{year}%'
        print("Student_type: ",student_type)
        dep_query="SELECT dep.calling_name FROM departments AS dep INNER JOIN super_admins AS sa ON dep.id =sa.dep_id WHERE sa.first_name=%s AND sa.password=%s;"
        data=(name,password)
        dep=new_data.fetchOneForeing(dep_query,data).decode().strip()
        query_count="SELECT COUNT(*) FROM medical_infor AS mi INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN students AS stu ON mi.user_id =stu.user_id INNER JOIN student_type AS stt ON stu.student_type_id=stt.id INNER JOIN exams AS ex ON ex.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id  WHERE dep.calling_name=%s  AND sub.year=%s AND sub.semester=%s AND  ex.held_date LIKE %s AND stt.type=%s"
        data_set=(dep,academic_yre,semester,search_pattern,student_type)
        student_count=new_data.fetchOneForeing(query_count,data_set)
        #number of authenticators
        auth_count_query="SELECT COUNT(*) FROM medical_infor AS mi INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN students AS stu ON mi.user_id =stu.user_id INNER JOIN student_type AS stt ON stu.student_type_id=stt.id INNER JOIN exams AS ex ON ex.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id  WHERE dep.calling_name=%s  AND sub.year=%s AND sub.semester=%s AND  ex.held_date LIKE %s AND stt.type=%s  AND mi.is_authenticate=1;"
        auth_count=new_data.fetchOneForeing(auth_count_query,data_set)
        #Non auth count
        non_auth_count_query="SELECT COUNT(*) FROM medical_infor AS mi INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN students AS stu ON mi.user_id =stu.user_id INNER JOIN student_type AS stt ON stu.student_type_id=stt.id INNER JOIN exams AS ex ON ex.subject_id=sub.subject_id INNER JOIN departments AS dep ON sub.department_id=dep.id  WHERE dep.calling_name=%s  AND sub.year=%s AND sub.semester=%s AND  ex.held_date LIKE %s AND stt.type=%s  AND mi.is_authenticate=-1;"
        non_auth_count=new_data.fetchOneForeing(non_auth_count_query,data_set)
        #main queries
        auth_query="SELECT st.index_number,st.first_name,st.last_name FROM students AS st INNER JOIN medical_infor AS mi ON mi.user_id=st.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN exams AS ex ON sub.subject_id=ex.subject_id INNER JOIN student_type AS stt ON st.student_type_id=stt.id INNER JOIN departments AS dep ON sub.department_id=dep.id WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND ex.held_date LIKE %s AND stt.type=%s AND mi.is_authenticate=1;"                            
        auth_data=new_data.fetchAllMulForeing(auth_query,data_set)
        un_auth_query="SELECT st.index_number,st.first_name,st.last_name FROM students AS st INNER JOIN medical_infor AS mi ON mi.user_id=st.user_id INNER JOIN subjects AS sub ON mi.subject_id=sub.subject_id INNER JOIN exams AS ex ON sub.subject_id=ex.subject_id INNER JOIN student_type AS stt ON st.student_type_id=stt.id INNER JOIN departments AS dep ON sub.department_id=dep.id WHERE dep.calling_name=%s AND sub.year=%s AND sub.semester=%s AND ex.held_date LIKE %s AND stt.type=%s AND mi.is_authenticate=-1;"                            
        un_auth_data=new_data.fetchAllMulForeing(un_auth_query,data_set)
        cleaned_data_auth = [(item[0].decode('utf-8'), item[1].decode('utf-8'), item[2].decode('utf-8')) for item in auth_data]
        cleaned_data_un_auth = [(item[0].decode('utf-8'), item[1].decode('utf-8'), item[2].decode('utf-8')) for item in un_auth_data]
            
            #print
        rendered =render_template('super_sample_report.html',form=form,student_count=student_count,authenticate=auth_count,non_authenticate=non_auth_count,dep=dep,year=year,auth=cleaned_data_auth,un_auth=cleaned_data_un_auth)
        pdf = pdfkit.from_string(rendered, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
        return response

    return render_template('super_sample_report.html',
                           form=form,student_count=student_count,
                           authenticate=auth_count,
                           non_authenticate=non_auth_count,
                           dep=dep,
                           year=year,
                           auth=cleaned_data_auth,
                           un_auth=cleaned_data_un_auth


                            )
if __name__=="__main__":
    app.run(debug=True)



