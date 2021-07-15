from flask import Flask , request , render_template, redirect , url_for, session,flash
import datetime
from datetime import date
from flask_mail import Message, Mail
import json
import pymysql

app = Flask(__name__)
app.secret_key = 'manas'
connection = pymysql.connect(host="localhost", user="root", password="root", database="nie")

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "antpd2020@gmail.com"
app.config['MAIL_PASSWORD'] = "abc-123-456"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail(app)

@app.route('/signup',methods=['GET','POST'])
def index():
    if request.method=='POST':
        inputvalues = request.form   
        name = inputvalues['name']
        usn = inputvalues['USN']
        email = inputvalues['email']
        phone = int(inputvalues['phone_number'])
        sem = int(inputvalues['sem'])
        sec = inputvalues['sec']
        passw = inputvalues['pass']
        cur = connection.cursor()
        cur.execute("INSERT INTO signup1 VALUES (%s,%s,%s,%s,%s,%s,%s)", (name,usn,email,phone,sem,sec,passw))
        connection.commit()
        cur.close()
        session['usn'] = usn 
        return redirect( url_for('fillsubjects'))
    return render_template("signup.html")
@app.route('/login', methods= ['GET','POST'])
def login():
    session.pop('usn', None)
    error = ""
    if request.method=='POST':
        data = None
        inp = request.form
        usn = inp['username']
        pas = inp['pass']
        cur = connection.cursor()
        cur.execute('SELECT password,email from signup1 where usn = %s',[str(usn)])
        data = cur.fetchall()
        cur.close()
        print(data)
        if data == ():
            print("hello")
            error ="User Doesn't exist, please signup"
            
        if data:
            if data[0][0]==pas:
                session['usn']=usn
                session['email'] = data[0][1]
                return redirect(url_for('home'))
            else:
                error =  "Invalid Credentials"
        else:
            error = "Invalid credentials"

    return render_template("login.html", error = error)
@app.route('/fillsubjects',methods = ['GET','POST'])
def fillsubjects():
    if 'usn' not in session:
        return redirect( url_for('login'))
    else:
        usn = session['usn']    
    if request.method=='POST':
        inp = request.form
        for i in range (int(inp['num'])):
            filename = "sub" + str(i+1)
            catten = filename + "c"
            tatten = filename + "t"
            courcecode = inp[filename]
            curattend = int(inp[catten])
            totalattend = int(inp[tatten])
            cur = connection.cursor()
            cur.execute("INSERT INTO subjects VALUES (%s,%s,%s,%s)", (usn,courcecode,curattend,totalattend))
            connection.commit()
            cur.close()
        return redirect(url_for('home'))
    return render_template("fillsubs3.html")
@app.route('/att')
def att():
    if 'usn' not in session:
        return redirect(url_for('login'))
    cur = connection.cursor()
    cur.execute("select  subjectcode,present,total from subjects where usn = '%s' "%(session['usn']))
    result1 = cur.fetchall()
    sub=0
    for a in result1:
        pre = int(a[1])
        tot = int(a[2])
        if pre/tot < 0.75:
            sub = sub+1
    cur.close()     
    return render_template('studentatten.html',table =result1,num=sub)        
@app.route('/selectclass', methods = ['GET','POST'])
def select():
    if 'teacher' not in session:
        return redirect (url_for('login_t'))
    cur = connection.cursor()
    cur.execute("select distinct subjectcode from subjects")
    result1 = cur.fetchall()
    cur.close()
    cur = connection.cursor()
    cur.execute("select distinct sec  from signup1")
    result2 = cur.fetchall()
    cur.close()
    if request.method=='POST':
        inp = request.form
        sub = inp['subs']
        sec = inp['sec']
        session['sub'] = sub
        session['sec'] = sec 
        return redirect(url_for('attendence'))     
    return render_template("select2.html",subjects = result1,sections = result2)               
@app.route('/atten',methods = ['GET','POST'])
def attendence():
    if 'sec'  not in session or 'sub' not in session:
        return redirect(url_for('select'))
    sec = session['sec']
    sub = session['sub']
    cur = connection.cursor()
    cur.execute('select name,s.usn from signup1 s , subjects u where  s.sec = %s and u.subjectcode = %s and s.usn = u.usn order by s.name',(sec,sub))
    result = cur.fetchall()
    cur.close()
    if request.method=='POST':
        session.pop('sec',None)
        session.pop('sub',None)
        inp = request.form
        for d in inp:
            usn = str(d)
            cur = connection.cursor()
            cur.execute('update subjects set present = present + 1 where usn = %s and subjectcode = %s ',(usn,sub))
            connection.commit()
            cur.close()    
        cur = connection.cursor()
        cur.execute('UPDATE subjects s join signup1 u on s.usn = u.usn set s.total = s.total + 1 where s.subjectcode = %s and u.sec = %s;',(sub,sec))
        connection.commit()
        cur.close()
        return redirect(url_for('home'))
    return render_template('atten.html',attendance =  result)        
@app.route('/home')
def home():
    if 'usn' not in session:
        return redirect(url_for('login'))
    cur = connection.cursor() 
    events = cur.execute("select * from events order by date") #fetches the number of rows in the table
    if events:
        event_details = cur.fetchall()# Fetches all the rows in the table
    else:
        event_details = "No events at the moment."
    msg1 = "None"
    msg2 = "None"
    curdate = ''
    flag = False
    cur.execute('select current_date()')
    data1 = cur.fetchall()
    curdate = str(data1[0][0])
    print(curdate)
    #cur.execute('select * from notiflistgr where usn = "%s"' %(session['usn']))
    data1 = cur.fetchall()
    print(data1)
    dates = []
    for row in data1:
        dates.append((row[1]-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    print(dates)
    for date in dates:
        if date == curdate:
            msg1 = "You have a group discussion(s) tomorrow."
            flag = True          
        else:
            if flag == False:
                msg1 = "None."
    flag = False
    cur.execute('select * from notiflistev where usn = "%s"' %(session['usn']))
    data2 = cur.fetchall()
    print(data2)
    dates2 = []
    for row2 in data2:
        dates2.append((row2[1]-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    print(dates2)
    for date in dates2:
        if date == curdate:
            msg2 = "You have an event(s) to attend tomorrow." 
            print(msg2) 
            print("!")   
            flag = True     
        else:
            if flag == False:
                msg2 = "None."
    return  render_template('home.html',msg1=msg1,msg2=msg2)
@app.route('/teacherlogin',methods = ['GET','POST'])
def login_t():
    if 'teacher' in session:
        session.pop('teacher',None)
    if 'usn' in session:
        session.pop('usn',None)
    if request.method=='POST':
        inp = request.form
        pas = inp['pass']
        if pas == 'admin':
            session['teacher'] = 1
            return redirect(url_for('select'))
        else:
            return "Wrong password entered please reload"        
    return render_template('tlogin.html') 
@app.route('/logout')
def logout():
    if 'teacher' in session:
        session.pop('teacher',None)
    if 'usn' in session:
        session.pop('usn',None)
    return redirect(url_for('home'))
@app.route('/stats')
def stats():
    if'teacher' not in session:
        return redirect(url_for('login_t'))    
    labels = ["I Year" , "II Year","III Year","IV Year"]
    values = []
    cur = connection.cursor()
    cur.execute('select count(usn) from signup1')
    noofstu = cur.fetchall()
    ns = noofstu[0][0]
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(usn) from signup1 where sem = 1 or sem = 2')
    noofstu = cur.fetchall()
    values.append(noofstu[0][0])
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(usn) from signup1 where sem = 3 or sem = 4')
    noofstu = cur.fetchall()
    values.append(noofstu[0][0])
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(usn) from signup1 where sem = 5 or sem = 6')
    noofstu = cur.fetchall()
    values.append(noofstu[0][0])
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(usn) from signup1 where sem = 7 or sem = 8')
    noofstu = cur.fetchall()
    values.append(noofstu[0][0])
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(usn) from subjects where present/total < 0.75')
    noofstu = cur.fetchall()
    faults = noofstu[0][0]
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(sub) from study')
    noofstu = cur.fetchall()
    groups = noofstu[0][0]
    cur.close()
    cur = connection.cursor()
    cur.execute('select count(ename) from events')
    noofstu = cur.fetchall()
    events = noofstu[0][0]
    cur.close()
    return render_template("stats2.html",ns=ns,values=values,faults=faults,labels=labels,groups = groups,events=events)  
@app.route('/cgpaCalc', methods = ['GET', 'POST'])
def sfg(): 
    if 'usn' in session:
        cgpa = ''
        if request.method == "POST":
            grade=[]
            cred=[]
            gp=[]
            for i in range(1,10):
                grade.append(request.form['Grade'+str(i)])
                cred.append(float(request.form['cred'+str(i)]))
            for i in range(0,9):
                if grade[i] == "S":
                    gp.append(10.0)
                elif grade[i] == "A":
                    gp.append(9.0)
                elif grade[i] == "B":
                    gp.append(8.0)
                elif grade[i] == "C":
                    gp.append(7.0)
                elif grade[i] == "D":
                    gp.append(6.0)
                else:
                    gp.append(0.0)
            sum1 = 0
            for i in range(0,9):
                sum1 = sum1 + (gp[i]*cred[i])
            tot = 0
            for x in cred:
                tot = tot+x
            cgpa = sum1/tot
            cgpa = round(cgpa,2)
            return render_template('CGPA.html', cgpa=cgpa)
        return render_template('CGPA.html', cgpa=cgpa)
    else:
        return redirect(url_for('home'))
@app.route('/creategroup', methods = ['GET', 'POST'])
def creategroup():
    if 'usn' in session: 
        if request.method == 'POST':
            sub = request.form['sub']
            maxno = request.form['max']
            usn = session['usn']
            cur  = connection.cursor()
            cur.execute('insert into study(subject,maxno,curno,leader) values(%s, %s, 0, %s)',(sub, maxno, usn))
            connection.commit()
            cur.close()
            return redirect(url_for('groups'))
        return render_template('create.html') 
    else:
        return redirect(url_for('login'))

@app.route('/groups')
def groups():
    if 'usn' in session: 
        cur = connection.cursor() #creates a cursor that points to the database
        groups = cur.execute("select * from study") #fetches the number of rows in the table
        if groups:
            group_details = cur.fetchall()# Fetches all the rows in the table
        else:
            group_details = "No Groups Available."
        return render_template('groupdesc2.html', groups = group_details)
    else:
        return redirect(url_for('login'))

@app.route("/eventreg", methods = ['GET', 'POST'])
def eventreg():
    if 'usn' in session:
        events = []
        cur = connection.cursor()
        cur.execute('SELECT ename from events')
        eventdata = cur.fetchall()
        if eventdata:
            for x in eventdata:
                events.append(x[0])
        else:
            return "error"
        if request.method == 'POST':
            usn = session['usn']
            pemail = request.form['email']
            ename = request.form['event']
            pname = request.form['name']
            ph = request.form['ph']
            dup = ()
            print(usn)
            cur.execute('select * from eventreg where usn = "%s" and ename = "%s"' %(usn, ename))
            dup = cur.fetchall()
            print(dup)
            if dup == ():
                cur.execute('insert into eventreg values("%s","%s","%s","%s","%s")' %(usn, ename, pemail, ph, pname))
                connection.commit()
                flash("Registered successfully!","success")
                cur.execute('select * from events where ename="'+ename+'"')
                eventDetails = cur.fetchall()    
                cur.close()
                messageBody ="""
Thank you for registering! Here are the details of the event - 

    Event Name: %s
    Date: %s
    Venue: %s
    Time: %s
                        
For further queries, contact any of the office bearers of the respective clubs and they will help you. You will receive a notificaton on your student profile the day before the event to serve as a reminder.
                        
Regards
Team NIE
                """%(eventDetails[0][1],eventDetails[0][3],eventDetails[0][5],eventDetails[0][4])
                sender = "proj.nie.12@gmail.com"
                receivers = [pemail] #Can have multiple recipients
                subject = "Registration Successful"
                message = Message(subject, sender=sender,recipients=receivers)
                message.body = messageBody
                mail.send(message)
                connection.commit()
                
                return render_template('eventreg.html', events = events)
            else:
                flash("You've already registered!")
                return render_template('eventreg.html', events = events)
        return render_template('eventreg.html', events = events)
       
    else:
        return redirect(url_for('login'))

@app.route('/addevents', methods = ['GET', 'POST'])
def addevent():
    if 'usn' in session: 
        if request.method == 'POST':
            club = request.form['club']
            name = request.form['ename']
            date = request.form['edate']
            time = request.form['etime']
            venue = request.form['venue']
            desc = request.form['desc']
            cur  = connection.cursor()
            cur.execute('insert into events values("%s", "%s", "%s", "%s", "%s", "%s")' %(club, name, desc, date, time, venue))
            connection.commit()
            cur.close()
            return redirect(url_for('events'))
        return render_template('addevents.html') 
    else:
        return redirect(url_for('login'))

@app.route('/events', methods = ['GET', 'POST'])
def events():
    if 'usn' in session:
        cur = connection.cursor()
        cur.execute('CALL eventdate()')
        events = cur.execute("select * from events order by date") #fetches the number of rows in the table
        if events != ():
            event_details = cur.fetchall()# Fetches all the rows in the table

        else:
            event_details = "No events at the moment."
            return redirect(url_for('home'))
        
        events1 = cur.execute("select distinct club from events") #fetches the number of rows in the table
        if events1 != ():
            distevents = cur.fetchall()# Fetches all the rows in the table
            print(events1)
        else:
            distevents = "No events at the moment."
            return redirect(url_for('home'))
        
        
        msg2 = ""
        curdate = ''
        flag = False
        cur.execute('select current_date()')
        data1 = cur.fetchall()
        curdate = str(data1[0][0])
        print(curdate)
        
        msg1 = ""
        cur.execute('select * from notiflistgr where usn = "%s"' %(session['usn']))
        data1 = cur.fetchall()
        print(data1)
        dates = []
        for row in data1:
            dates.append((row[1]-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        print(dates)
        for date in dates:
            if date == curdate:
                msg1 = "You have a group discussion(s) tomorrow."
                flag = True          
            else:
                if flag == False:
                    msg1 = "None."
        flag = False
        
        cur.execute('select * from notiflistev where usn = "%s"' %(session['usn']))
        data2 = cur.fetchall()
        print(data2)
        dates2 = []
        for row2 in data2:
            dates2.append((row2[1]-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        print(dates2)
        for date in dates2:
            if date == curdate:
                msg2 = "You have an event(s) to attend tomorrow." 
                print(msg2) 
                print("!")   
                flag = True     
            else:
                if flag == False:
                    msg2 = "None."

        if request.method == 'POST':
            club = request.form['club']
            if club == 'all':
                events = cur.execute("select * from events order by date") #fetches the number of rows in the table
                if events:
                    event_details = cur.fetchall()# Fetches all the rows in the table
                else:
                    event_details = " "
            else:
                events = cur.execute('SELECT * from events where club = "%s" order by date'%(club)) 
                if events:
                    event_details = cur.fetchall()# Fetches all the rows in the table
                else:
                    event_details = " "
           
            return render_template('events2.html', events = event_details, distevents= distevents)
        else:
            return render_template('events2.html', events = event_details, distevents= distevents)
    else:
        return redirect(url_for('login'))            

@app.route('/adddatetime/<gno>', methods = ['GET', 'POST'])
def adddatetime(gno):
    if 'usn' in session:
        cur = connection.cursor()
        study = []
        cur.execute("select group_id from group_discussion")
        studsgr = cur.fetchall()
        if studsgr:
            for x in studsgr:
                study.append(x[0])
        print(studsgr)
        if request.method == 'POST':
            print("hello")
            cur.execute('SELECT leader from study where group_id = %s', str(gno))
            data2 = cur.fetchall()
            if data2 != ():
                lead = data2[0][0]
            else:
                return "error"
            print(lead, session['usn'])
            if session['usn'] == lead:
                date = request.form['date1']   
                venue = request.form['venue'] 
                print(gno)  
                time = request.form['time']
                flag = False
                try:      
                    for x in study:
                        if int(gno) == int(x):
                            print("hey")
                            flag = True
                            cur.execute('update group_discussion set date = "%s", venue = "%s", time = "%s" where group_id = "%s"' %(date,venue,time,gno)) 
                            connection.commit()
                            
                    if flag == False:
                        cur.execute('insert into group_discussion values(%s,%s,%s,%s)', (date,venue,time, gno)) 
                        connection.commit()
                    flash('addition/modification successful!', "success")
                except:
                    flash('addition/modification unsuccessful. Please try again.', "error")    
            else:
                flash("WARNING : Only leaders can modify the settings.")
            return render_template('deets.html')
        else:
            return render_template('deets.html')
    else:
        return redirect(url_for('login'))


@app.route('/youreventsandgroups', methods = ['GET', 'POST'])
def yours():
    sfinal = []
    if 'usn' in session:
        cur = connection.cursor()
        final = cur.execute('select usn, subject, date, venue, time from studfinal where usn = "%s"' %(session['usn']))
        sfinal=[]
        if final:
            sfinal = cur.fetchall()
        else:
            print("No group registrations")

        final = cur.execute('select * from eventfinal where usn = "%s"' %(session['usn']))
        efinal = []
        if final:
            efinal = cur.fetchall()
        cur.close()
        return render_template('event_group1.html', sfinal = sfinal, efinal = efinal) 
    else:
        return redirect(url_for('login'))

@app.route('/selectgroup', methods = ['GET', 'POST'])
def selgroup():
    if 'usn' in session: 
        cur = connection.cursor()
        cur.execute('SELECT max(group_id) from study')
        data1 = cur.fetchall()
        if data1:
            idd = data1[0][0]
        else:
            return "error"
        stud = []
        cur.execute("select group_id from study")
        studs = cur.fetchall()
        if studs:
            for x in studs:
                stud.append(x[0])
        cur.connection.commit()
        cur.close()    
        
        if request.method == 'POST':
            usn1 = (session['usn'])
            groupno = request.form['groupnum']
            pemail = session['email']
            groupdeets = []
            cur = connection.cursor()
            cur.execute('select maxno, curno from study where group_id = %s' %(groupno))
            maxg = cur.fetchall()
            print(maxg)
            if maxg:
                print(usn1)
                cur.execute('select * from studgroup where usn = "%s"' %(usn1))
                no = cur.fetchall()
                if no == ():
                    maxno = maxg[0][0] 
                    curno = maxg[0][1]
                    if maxno > curno:        
                        cur.callproc('ins', [usn1,groupno,session['email']])
                        connection.commit()
                        cur.execute('select * from temp where group_id = "%s"' %(groupno))
                        groupdeets = cur.fetchall()    
                        print(groupdeets)
                        flash("You have been added to the group successfully!","success")
            
                        messageBody ="""
                    Thank you for registering! Here are the details of the group discussion - 

                        Group ID: %s
                        Subject: %s
                        Date: %s
                        Venue: %s
                        Time: %s
                        
                    For further queries, contact the group leader, and they will help you. You will receive a notificaton on your student profile the day before the the group discussion meet to serve as a reminder.
                        
                    Regards
                    Team NIE
                        """%(groupdeets[0][0],groupdeets[0][1],groupdeets[0][2],groupdeets[0][3],groupdeets[0][4] )
                        sender = "proj.nie.12@gmail.com"
                        receivers = [pemail] #Can have multiple recipients
                        subject = "Registration Successful"
                        message = Message(subject, sender=sender,recipients=receivers)
                        message.body = messageBody
                        mail.send(message)
                    else:
                        flash("Group Limit reached! Registration Unsuccessful.", "error")
            
                else:
                    flash("You're already in the group!","error")
                cur.close()
            connection.commit() 
            return render_template('studg.html', idd = idd, stud = stud)
        return render_template('studg.html', idd = idd, stud = stud)
    else:
        return redirect(url_for('login'))
@app.route('/yourprofile')
def profile():
    if 'usn' in session:
        cur = connection.cursor()
        cur.execute('select * from signup1 where usn = "%s"' %(session['usn']))
        prof = cur.fetchall()
        '''
        name = ""
        email = ""
        sem = ""
        ph = ""
        sec = ""
        '''

        print(prof)

        if prof != ():
            name = prof[0][0]
            email = prof[0][2]
            sem = prof[0][4]
            sec = prof[0][5]
            ph = prof[0][3]
            cur.close()
            connection.commit()
            return render_template('profile2.html', name = name, email = email, sem = sem, sec = sec, ph = ph)
        else:
            return redirect(url_for('login'))

    else:
        return redirect(url_for('login'))
@app.route('/editprofile', methods = ['GET', 'POST'])
def editp():
    if 'usn' in session:
        cur = connection.cursor()
        cur.execute('select * from signup1 where usn = "%s"' %(session['usn']))
        prof = cur.fetchall()
        if prof:
            name = prof[0][0]
            email = prof[0][2]
            sem = prof[0][4]
            sec = prof[0][5]
            ph = prof[0][3]
        if request.method == 'POST':
            name = request.form['nname'] 
            email = request.form['nemail']
            sem = request.form['nsem'] 
            sec = request.form['nsec']
            ph = request.form['nphone']
            cur.execute("update signup1 set name = '%s', email = '%s', sem = '%s', sec = '%s', phone = '%s' where usn = '%s'" %(name, email, sem, sec, ph, session['usn']))   
            connection.commit() 
            return redirect(url_for('profile'))
        return render_template('editprofile.html', name = name, email = email, sem = sem, sec = sec, ph = ph)
    else:
            return redirect(url_for("login"))  
@app.route('/')
def aboutus():
    return render_template('aboutus.html')
if __name__ == "__main__":
    app.run(debug=True)