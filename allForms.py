from flask_wtf import FlaskForm
from wtforms import StringField,validators,SelectField,TextAreaField,DateTimeField,DateField,RadioField,FileField,SubmitField,PasswordField,TimeField
from wtforms import  widgets,SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from email_validator import validate_email
from flask_wtf.file import FileField, FileAllowed



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

#admin Log in form
class AdminLog(FlaskForm):
    user_name=StringField("User Name: ",validators=[DataRequired(), Length(min=3, max=10)])
    password=PasswordField("Password: ",validators=[DataRequired(),Length(min=4)])
    possition=SelectField("Possition",choices=['OFFICE','HOD'])
    department=SelectField("Department",choices=['IT','MANAGEMENT','ACCOUNTANCY','ENGLISH','TOURISM'])
    submit=SubmitField("Log In")
    

#user Log in form
class UserLog(FlaskForm):
    user_name=StringField("User Name: ",validators=[DataRequired(),Length(min=3, max=10)])
    password=PasswordField("Password: ")
    submit=SubmitField("Log In")


#user main form
class UserForm(FlaskForm):
    date_issued=DateField("Issued Date  OF The Medical",validators=[DataRequired()])
    start_date=DateField("Affected From ",validators=[DataRequired()])
    end_date=DateField("To",validators=[DataRequired()])
    attempt=SelectField("Attemp",validators=[DataRequired()])
    doc_name=StringField('Doctors Name',validators=[DataRequired(),Length(min=3, max=20)])
    hospital=StringField('Hospital',validators=[DataRequired(),Length(min=3, max=50)])
    med_type=RadioField("Medical By",validators=[DataRequired()])
    med_image = FileField("Upload picture of Medical Sheet", validators=[
        DataRequired(message="Please upload a file."),
        FileAllowed(['jpg','jpeg'], 'Only jpg or jpeg formats are allowed.')
    ])
    year=SelectField("Year",validators=[DataRequired()])
    semester=SelectField("Semester",validators=[DataRequired()])
    subject=SelectField("Subject",validators=[DataRequired()])
    submit=SubmitField("Upload")

#admin Sign Up
class AdminSignUp(FlaskForm):
    first_name=StringField("Frist Name: ",validators=[DataRequired(),Length(min=3, max=10)])
    last_name=StringField("Last Name: ",validators=[DataRequired(),Length(min=3, max=10)])
    gender=SelectField("Gender: ",choices=['MALE','FEMALE'],validators=[DataRequired()])
    email=StringField("Email: ",[validators.Email()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    confirm_password=PasswordField("Confirm Password: ",validators=[DataRequired(),EqualTo('password')])
    possition=SelectField("Possision: ",choices=['OFFICE','HOD'],validators=[DataRequired()])
    department=SelectField("Department: ",validators=[DataRequired()])
    submit=SubmitField("Submit")
 
#user SignUp
class UserSignUp(FlaskForm):
    first_name=StringField("First Name: ",validators=[DataRequired(),Length(min=3, max=10)])
    last_name=StringField("Last Name: ",validators=[DataRequired(),Length(min=3, max=10)])
    index_number = StringField("Index Number(KAN/ X/ 202X / X/ XXXX)", validators=[
        DataRequired(),
        Length(min=18, max=25),
        Regexp(r'^[A-Z]{3}/[A-Z]{0,6}/\d{4}/(F|P)/\d{4}$', message='Invalid index number format.')
    ])
    mode=SelectField("Mode: ",validators=[DataRequired(),])
    gender=SelectField("Gender: ",choices=['MALE','FEMALE'],validators=[DataRequired()])
    department=SelectField("Department: ",validators=[DataRequired(),])
    email=StringField("Email: ",[validators.Email()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    confirm_password=PasswordField("Confirm Password: ",validators=[DataRequired(),EqualTo('password')])
    id_card = FileField("Red book/ID", validators=[
    DataRequired(message="Please upload a file."),
    FileAllowed(['jpg', 'jpeg'], 'Only JPEG images are allowed.')
])

    submit=SubmitField("Submit")

    
#Admin Interface
class AdminInterface(FlaskForm):
    edit_time_table=SubmitField("Click To Edit Time Tables:")
    display=SubmitField("Display Requests") 
    accept=SubmitField("Accept")
    all_accept=SubmitField("ALL Accept")
    reject=SubmitField("Reject")
    all_reject=SubmitField("ALL Reject")
    submit=SubmitField("Submit To HOD")
    abort=SubmitField("Abort")
    download=SubmitField("Download List")
    
    
    

#Super Admin Interface
class SuperAdminInterface(FlaskForm):
    edit_time_table=SubmitField("Click To Edit Time Tables:")
    display=SubmitField("Display Requests") 
    authenticate=SubmitField("Authenticate")
    all_authenticate=SubmitField("ALL Authenticate")
    reject=SubmitField("Reject")
    all_reject=SubmitField("ALL Reject")
    

#timetable

class TimeSchedule(FlaskForm):
    subject_name=SelectField('Subject Name',validators=[DataRequired()]) 
    date=DateField()
    start_time=TimeField("Start Time")
    end_time=TimeField("End Time")
    location=StringField(validators=[DataRequired(),Length(min=3, max=20)])
    update=SubmitField("Update")


class AddNewSubjects(FlaskForm):
    subject_name=StringField('Subject Name',validators=[DataRequired()]) 
    subject_code=StringField('Subject Code',validators=[DataRequired()]) 
    year=SelectField('Year',validators=[DataRequired()]) 
    semester=SelectField('Semester',validators=[DataRequired()]) 
    update=SubmitField("Update")
    
    
class MedicalClosingDate(FlaskForm):
    closing_date=DateField("Closing Date",validators=[DataRequired()])
    set=SubmitField("Set")

class ReportDepartments(FlaskForm):
    date=DateField("Date: ",validators=[DataRequired()])
    departments=SelectField("Department: ",validators=[DataRequired()])
    update=SubmitField("Update")
    years=SelectField("Year: ",validators=[DataRequired()])
    semesters=SelectField("Semester: ",validators=[DataRequired()])
    student_type=SelectField("Type: ",choices=['FULL TIME','PART TIME'],validators=[DataRequired()])

class SuperAdminReport(FlaskForm):
    date=DateField("Date: ",validators=[DataRequired()])
    update=SubmitField("Update")
    years=SelectField("Year: ",validators=[DataRequired()])
    semesters=SelectField("Semester: ",validators=[DataRequired()])
    student_type=SelectField("Type: ",choices=['FULL TIME','PART TIME'],validators=[DataRequired()])

