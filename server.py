import flask
from flask import url_for  # for switching page
import os  
import re  
import pymysql  # connect database

# init
app = flask.Flask(__name__)
# init the database connection
# use pymysql.connect to connect local db
db = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                     password='your-password', database='mydb', charset='utf8')
# edit db, get the cursor 
cursor = db.cursor()
# store the login username
users = []


@app.route("/", methods=["GET", "POST"])
def login():
    # set login session to null
    flask.session['login'] = ''
    if flask.request.method == 'POST':
        user = flask.request.values.get("user", "")
        pwd = flask.request.values.get("pwd", "")
        # prevent sql edit, like select * from admins where admin_name = '' or 1=1 -- and password='';
        # judge the search filter
        result_user = re.search(r"^[a-zA-Z]+$", user)  # all alph user name
        result_pwd = re.search(r"^[a-zA-Z\d]+$", pwd)  # password alph and number
        if result_user != None and result_pwd != None:  # pass the verification
            msg = 'username/password is incorrect'
            # compare with the data in DB
            sql = "select * from admins where admin_name='" + \
                user + "' and admin_password='" + pwd + "';"
            cursor.execute(sql)
            result = cursor.fetchone()
            # pair and find admin
            if result:
                # login success
                flask.session['login'] = 'OK'
                users.append(user)  # save success login user
                return flask.redirect(flask.url_for('student'))
                # return flask.redirect('/file')
        else:  # invalid input
            msg = 'invalid input'
    else:
        msg = ''
        user = ''
    return flask.render_template('login.html', msg=msg, user=user)


@app.route('/student', methods=['GET', "POST"])
def student():
    # login session
    if flask.session.get("login", "") == '':
        # no login
        print('not login!redirect!')
        return flask.redirect('/')
    insert_result = ''
    # show username otherwise null
    if users:
        for user in users:
            user_info = user
    else:
        user_info = ''
    # show admin data
    if flask.request.method == 'GET':
        sql_list = "select * from students_infos"
        print(sql_list, '!!!!!!!')
        cursor.execute(sql_list)
        results = cursor.fetchall()
    if flask.request.method == 'POST':
        # get student info input
        student_id = flask.request.values.get("student_id", "")
        student_class = flask.request.values.get("student_class", "")
        student_name = flask.request.values.get("student_name", "")
        print(student_id, student_class, student_name)

        try:
            # save it to db
            sql = "create table if not exists students_infos(student_id varchar(15) primary key,student_class varchar(20),student_name varchar(10));"
            cursor.execute(sql)
            sql_1 = "insert into students_infos(student_id, student_class, student_name)values(%s,%s,%s)"
            cursor.execute(sql_1, (student_id, student_class, student_name))
            # result = cursor.fetchone()
            insert_result = "add student info success."
            print(insert_result)
        except Exception as err:
            print(err)
            insert_result = "add student info failed."
            print(insert_result)
            pass
        db.commit()
        # POST
        sql_list = "select * from students_infos"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    return flask.render_template('student.html', insert_result=insert_result, user_info=user_info, results=results)


@app.route('/teacher', methods=['GET', "POST"])
def teacher():
    # login session
    if flask.session.get("login", "") == '':
        # no login
        print('not login!redirect!')
        return flask.redirect('/')
    insert_result = ''
    # show username otherwise null
    if users:
        for user in users:
            user_info = user
    else:
        user_info = ''
    # show admin data
    if flask.request.method == 'GET':
        sql_list = "select * from students_decision_infos"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    if flask.request.method == 'POST':
        # get student info
        student_id = flask.request.values.get("student_id", "")
        student_class_id = flask.request.values.get("student_class_id", "")
        teacher_id = flask.request.values.get("teacher_id", "")
        print(student_id, student_class_id, teacher_id)
        try:
            # save info to db
            sql = "create table if not exists students_decision_infos(student_id varchar(15) primary key,student_class_id varchar(20),teacher_id varchar(15),foreign key(student_id) references students_infos(student_id));"
            cursor.execute(sql)
            sql_1 = "insert into students_decision_infos(student_id, student_class_id, teacher_id)values(%s,%s,%s)"
            cursor.execute(sql_1, (student_id, student_class_id, teacher_id))
            # result = cursor.fetchone()
            insert_result = "add course info success."
            print(insert_result)
        except Exception as err:
            print(err)
            insert_result = "add course info failed."
            print(insert_result)
            pass
        db.commit()
        # POST data
        sql_list = "select * from students_decision_infos"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    return flask.render_template('teacher.html', insert_result=insert_result, user_info=user_info, results=results)


@app.route('/grade', methods=['GET', "POST"])
def grade():
    # login session
    if flask.session.get("login", "") == '':
        # no login
        print('not login!redirect!')
        return flask.redirect('/')
    insert_result = ''
    # show username
    if users:
        for user in users:
            user_info = user
    else:
        user_info = ''
    # showcase the info
    if flask.request.method == 'GET':
        sql_list = "select * from grade_infos"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    if flask.request.method == 'POST':
        # get the student score info
        student_id = flask.request.values.get("student_id", "")
        student_class_id = flask.request.values.get("student_class_id", "")
        grade = flask.request.values.get("grade", "")
        print(student_id, student_class_id, grade)
        # save it to db
        try:
            sql = "create table if not exists grade_infos(student_id varchar(15) primary key,student_class_id varchar(20),grade tinyint unsigned,foreign key(student_id) references students_decision_infos(student_id));"
            cursor.execute(sql)
            sql_1 = "insert into grade_infos(student_id, student_class_id,grade)values(%s,%s,%s)"
            cursor.execute(sql_1, (student_id, student_class_id, grade))
            insert_result = "add student score success."
            print(insert_result)
        except Exception as err:
            print(err)
            insert_result = "add student score failed."
            print(insert_result)
            pass
        db.commit()
        # POST
        sql_list = "select * from grade_infos"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    return flask.render_template('grade.html', insert_result=insert_result, user_info=user_info, results=results)


@app.route('/grade_infos', methods=['GET', 'POST'])
def grade_infos():
    # login session
    if flask.session.get("login", "") == '':
        # no login
        print('not login!redirect!')
        return flask.redirect('/')
    query_result = ''
    results = ''
    # show user info
    if users:
        for user in users:
            user_info = user
    else:
        user_info = ''
    # get the data for drag bar
    if flask.request.method == 'POST':
        select = flask.request.form.get('selected_one')
        query = flask.request.values.get('query')
        print(select, query)
        # search based on the filter
        if select == 'studentID':
            try:
                sql = "select * from grade_infos where student_id = %s; "
                cursor.execute(sql, query)
                results = cursor.fetchall()
                if results:
                    query_result = 'query success!'
                else:
                    query_result = 'query failed!'
            except Exception as err:
                print(err)
                pass
        if select == 'student name':
            try:
                sql = "select * from grade_infos where student_id in(select student_id from students_infos where student_name=%s);"
                cursor.execute(sql, query)
                results = cursor.fetchall()
                if results:
                    query_result = 'query success!'
                else:
                    query_result = 'query failed!'
            except Exception as err:
                print(err)
                pass

        if select == 'courseID':
            try:
                sql = "select * from grade_infos where student_class_id in(select student_class_id from students_infos where student_class_id=%s);"
                cursor.execute(sql, query)
                results = cursor.fetchall()
                if results:
                    query_result = 'query success!'
                else:
                    query_result = 'query failed!'
            except Exception as err:
                print(err)
                pass

        if select == "class":
            try:
                sql = "select * from grade_infos where student_class_id in(select student_class_id from students_infos where student_class=%s);"
                cursor.execute(sql, query)
                results = cursor.fetchall()
                if results:
                    query_result = 'query success!'
                else:
                    query_result = 'query failed!'
            except Exception as err:
                print(err)
                pass
    return flask.render_template('grade_infos.html', query_result=query_result, user_info=user_info, results=results)


@app.route('/adminstator', methods=['GET', "POST"])
def adminstator():
    # login session
    if flask.session.get("login", "") == '':
        # no login
        print('not login!redirect!')
        return flask.redirect('/')
    insert_result = ''
    # show admin info
    if flask.request.method == 'GET':
        sql_list = "select * from admins"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    # show user info
    if users:
        for user in users:
            user_info = user
    else:
        user_info = ''
    if flask.request.method == 'POST':
        # get the admin info
        admin_name = flask.request.values.get("admin_name", "")
        admin_password = flask.request.values.get("admin_password", "")
        #print(admin_name, admin_password)
        admin_name_result = re.search(r"^[a-zA-Z]+$", admin_name)  # all alph username
        admin_password_result = re.search(
            r"^[a-zA-Z\d]+$", admin_password)  # alph and number for password
        # verification pass
        if admin_name_result != None and admin_password_result != None:  # pass
            # get the draging data
            select = flask.request.form.get('selected_one')
            print("select is {}".format(select))
            if select == 'add admin':
                try:
                    sql = "create table if not exists admins(id int primary key auto_increment,admin_name varchar(15),admin_password varchar(20));"
                    cursor.execute(sql)
                    sql_1 = "insert into admins(admin_name,admin_password)values(%s,%s)"
                    cursor.execute(sql_1, (admin_name, admin_password))
                    insert_result = "add adminstator success."
                    print(insert_result)
                except Exception as err:
                    print(err)
                    insert_result = "add adminstator failed."
                    print(insert_result)
                    pass
                db.commit()
            if select == 'change password':
                try:
                    sql = "update admins set admin_password=%swhere admin_name=%s;"
                    cursor.execute(sql, (admin_password, admin_name))
                    insert_result = "admin " + admin_name + " password changed success.!"
                except Exception as err:
                    print(err)
                    insert_result = "change password failed!"
                    pass
                db.commit()
            if select == 'delete admin':
                try:
                    sql_delete = "delete from admins where admin_name='" + admin_name + "';"
                    cursor.execute(sql_delete)
                    insert_result = "delete adminstator success: " + admin_name
                except Exception as err:
                    print(err)
                    insert_result = "delete adminstator failed"
                    pass
                db.commit()

        else:  # invalid input
            insert_result = "invalid format!"
        # POST
        sql_list = "select * from admins"
        cursor.execute(sql_list)
        results = cursor.fetchall()
    return flask.render_template('adminstator.html', user_info=user_info, insert_result=insert_result, results=results)


# start server
app.debug = True
# encraption
app.secret_key = 'carson'
try:
    app.run()
except Exception as err:
    print(err)
    db.close()  # close db
