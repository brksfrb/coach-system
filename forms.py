from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, SelectMultipleField, BooleanField, DateField, HiddenField, TextAreaField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length, NumberRange

from CLib.Users.parent import Relation
from infrastructure import cm


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)], render_kw={"autocomplete": "username"})
    password = PasswordField("Password", validators=[DataRequired(), Length(min=3, max=30)], render_kw={"autocomplete": "current-password"})
    submit = SubmitField("Login")

class SettingsForm(FlaskForm):
    notifications = BooleanField("Bildirimleri Aç")
    theme = SelectField("Tema", choices= [("light", "Açık"), ("dark", "Koyu")])

class ChangePasswordForm(FlaskForm):
    old_password = StringField("Mevcut Şifre", validators= [DataRequired()], render_kw={"placeholder": "Mevcut şifreniz", "autocomplete": "current-password"})
    new_password = StringField("Yeni Şifre", validators= [DataRequired()], render_kw={"placeholder": "Yeni şifre", "autocomplete": "new-password"})
    new_password_again = StringField("Yeni Şifre Tekrar", validators= [DataRequired()], render_kw={"placeholder": "Yeni şifre tekrar girin", "autocomplete": "new-password"})

class TeachersCreationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=25)], render_kw={"placeholder": "Name"})
    surname = StringField("Surname", validators=[DataRequired(), Length(min=3, max=25)], render_kw={"placeholder": "Surname"})
    gender = SelectField("Gender", choices=[("male", "Male"), ("female", "Female")], validators=[DataRequired()])
    max_students = IntegerField("Max Students", validators=[DataRequired(), NumberRange(min=1, max=20, message= "Please enter a number between 1 and 20")], render_kw={"placeholder": "Max Students"})
    modules = SelectMultipleField("Modules", choices= [(module.name, module.pretty_name) for module in cm.available_modules], option_widget=CheckboxInput(), widget= ListWidget(prefix_label=False))
    submit = SubmitField("➕ Create")

class StudentCreationForm(FlaskForm):
    gender_choices = [("male", "Erkek"), ("female", "Kadın")]
    relation_choices = [(r.code, r.tr) for r in Relation]
    grade_choices = []
    for i in range(1, 14):
        grade_choices.append((str(i), str(i)))
    name = StringField("Adı", validators=[DataRequired(), Length(min=3, max=25)])
    surname = StringField("Soyadı", validators=[DataRequired(), Length(min=3, max=25)])
    gender = SelectField("Cinsiyeti", choices= gender_choices, validators=[DataRequired()], default= gender_choices[0][0])
    grade = SelectField("Sınıf Düzeyi", choices= grade_choices, validators= [DataRequired()], coerce= int, default= grade_choices[0][0])
    num_parents = SelectField("Veli Sayısı", choices= [("0", "0"), ("1", "1"), ("2", "2")], coerce= int, default= "0")
    first_parent_name = StringField("Adı")
    first_parent_surname = StringField("Soyadı")
    first_parent_gender = SelectField("Cinsiyeti", choices= gender_choices, default= gender_choices[0][0])
    first_parent_relation = SelectField("Yakınlık Durumu", choices= relation_choices, default= relation_choices[0][0])
    second_parent_name = StringField("Adı")
    second_parent_surname = StringField("Soyadı")
    second_parent_gender = SelectField("Cinsiyeti", choices= gender_choices, default= gender_choices[0][0])
    second_parent_relation = SelectField("Yakınlık Durumu", choices= relation_choices, default= relation_choices[0][0])

    def validate(self, **kwargs):
        # run base validation first
        rv = super().validate(**kwargs)
        if not rv:
            return False

        errors = False

        # If 1 or 2 parents, require corresponding fields
        if self.num_parents.data >= 1:
            if not self.first_parent_name.data.strip():
                self.first_parent_name.errors.append("Bu alan zorunludur.")
                errors = True
            if not self.first_parent_surname.data.strip():
                self.first_parent_surname.errors.append("Bu alan zorunludur.")
                errors = True

        if self.num_parents.data == 2:
            if not self.second_parent_name.data.strip():
                self.second_parent_name.errors.append("Bu alan zorunludur.")
                errors = True
            if not self.second_parent_surname.data.strip():
                self.second_parent_surname.errors.append("Bu alan zorunludur.")
                errors = True

        return not errors

class HomeworkCreationForm(FlaskForm):
    title = StringField("Başlık", validators= [DataRequired(), Length(min=3, max=25)])
    description = StringField("Açıklama", validators= [DataRequired(), Length(min=3, max=25)])
    start_date = DateField("Başlangıç Tarihi", validators= [DataRequired()])
    end_date = DateField("Bitiş Tarihi", validators= [DataRequired()])
    subject = SelectField("Branş", choices= [("", "")] + [(s.key, s.name) for s in cm.config.AVAILABLE_SUBJECTS], validators= [DataRequired(message="Lütfen bir branş seçin")])
    objective = SelectField("Kazanım", choices= [("", "")], validators= [DataRequired()], validate_choice = False)
    num_questions = IntegerField("Soru Sayısı", validators= [DataRequired()])

def make_program_form(students, program, column_count=5):
    class ProgramEditForm(FlaskForm):
        pass

    student_choices = [("", "----")] + [(s.username, s.fullname) for s in students]

    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        for i in range(column_count + 1):
            field_name = f"{day}_{i}"
            # Add a SelectField to the form class
            box = program.get_box(day, i)
            s = box.student if box else None
            du = s.username if s else ""
            setattr(ProgramEditForm, field_name, SelectField(
                label="",
                choices= student_choices,
                default= du
            ))

    return ProgramEditForm()


class MessagingForm(FlaskForm):
    message = StringField("Message", validators= [DataRequired()], render_kw={"placeholder": "Mesaj girin"})
    md_id = HiddenField()

class StudentNotesForm(FlaskForm):
    notes = TextAreaField("Notes", render_kw={"placeholder": "Öğrenci hakkında notlarınızı buraya yazabilirsiniz"})