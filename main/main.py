import tkinter as tk
from tkinter.ttk import Combobox,Treeview
from tkinter import messagebox
from tkinter.filedialog import askopenfilename,askdirectory
from PIL import Image,ImageTk,ImageDraw,ImageFont,ImageOps
import re                 
import random
from io import BytesIO
import sqlite3
import pandas as pd
import os
import win32api
from datetime import datetime
from tkcalendar import Calendar
import tkinter.messagebox as messagebox

def message_box(message, title=None, icon=None):
    messagebox.showinfo(title, message, icon=icon)
root =tk.Tk()
root.geometry('800x600')
root.title('Student Project Management' )

bg_color='mediumpurple4'
login_student_icon = tk.PhotoImage(file='images/login_student_img.png')
login_admin_icon = tk.PhotoImage(file='images/admin_img.png')
add_student_icon = tk.PhotoImage(file='images/add_student_img.png')
lock_icon=tk.PhotoImage(file='Images/locked.png')
unlock_icon=tk.PhotoImage(file='Images/unlocked.png')
pic_icon=tk.PhotoImage(file='Images/add_image.png')


def init_database():
    if os.path.exists('student_account.db'):
        conn = sqlite3.connect("student_account.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        data = cursor.fetchall()  # Fetch data from 'data' table
        conn.close()

        if data:
            # Convert the fetched data to a Pandas DataFrame
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            # Select specific columns for export
            selected_columns = ['id_number', 'name', 'age', 'gender', 'year', 'semester', 'batch', 'email']
            # Export 'data' table to an Excel file
            df[selected_columns].to_excel('student_account_data.xlsx', index=False)
            print("'data' table data exported to student_account_data.xlsx")

    db_file = 'student_account.db'

    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if the 'leave_applications' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leave_applications';")
        leave_table_exists = cursor.fetchone() is not None

        if not leave_table_exists:
            print("Error: 'leave_applications' table not found.")
            conn.close()
            return
  # Fetch data from 'leave_applications' table with additional columns
        cursor.execute("""
            SELECT leave_applications.*,data.name,data.phone_number, data.email
            FROM leave_applications
            JOIN data ON leave_applications.student_id = data.id_number
        """)
        leave_data = cursor.fetchall()

        if leave_data:
            # Convert the fetched data to a Pandas DataFrame
            leave_columns = [desc[0] for desc in cursor.description]
            leave_df = pd.DataFrame(leave_data, columns=leave_columns)
            # Calculate leave days and add a new column to the DataFrame
            leave_df['end_date'] = pd.to_datetime(leave_df['end_date'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%d-%m-%Y')
            leave_df['start_date'] = pd.to_datetime(leave_df['start_date'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%d-%m-%Y')

            leave_df['leave_days'] = (pd.to_datetime(leave_df['end_date'], format='%d-%m-%Y') -
                                    pd.to_datetime(leave_df['start_date'], format='%d-%m-%Y')).dt.days + 1


            # Append 'leave_applications' data to the existing Excel file
            with pd.ExcelWriter('student_account_data.xlsx', engine='openpyxl', mode='a') as writer:
                leave_df.to_excel(writer, sheet_name='leave_applications', index=False)

            #print("'leave_applications' data appended to student_account_data.xlsx.")
        else:
            print("No data in 'leave_applications' table.")

        conn.close()

    else:
        conn = sqlite3.connect("student_account.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE data (
            id_number TEXT,
            password TEXT,
            name TEXT,
            age TEXT,
            gender TEXT,
            phone_number TEXT,
            year TEXT,
            semester TEXT,
            batch TEXT,
            email TEXT,
            image BLOB
        )""")
        #cursor.execute("DROP TABLE IF EXISTS leave_applications")
        cursor.execute("""
        CREATE TABLE leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                start_date TEXT,
                end_date TEXT,
                reason TEXT,
                additional_reason TEXT,
                leave_days INTEGER,
                status TEXT
        )""")
        conn.commit()
        conn.close()
def check_id_already_exists(id_number):
        conn = sqlite3.connect('student_account.db')
        cursor = conn.cursor()

        cursor.execute(f"""
        SELECT id_number FROM data WHERE id_number == '{id_number}'
        """);
        conn.commit() 
        response = cursor.fetchall();
        conn.close()
        return response

def check_valid_passwd(id_number,password):

        conn = sqlite3.connect('student_account.db')
        cursor = conn.cursor()

        cursor.execute(f"""
        SELECT id_number FROM data WHERE id_number == '{id_number}' AND password =='{password}'
        """);

        conn.commit() 
        response = cursor.fetchall();
        conn.close()
        return response
   
def add_data(id_number, password, name, age, gender, phone_number,
            year,semester,batch, email, pic_data):

        conn=sqlite3.connect("student_account.db")
        cursor = conn.cursor()
        cursor.execute(f"""
        INSERT INTO data VALUES ('{id_number}', '{password}',
        '{name}','{age}','{gender}','{phone_number}',
        '{year}','{semester}','{batch}','{email}',?)
        """,[pic_data])
        
        conn.commit()
        conn.close()
 
def confirmationbox(msg):
    answer = tk.BooleanVar()
    answer.set(False)
    def action(ans):
        answer.set(ans) 
        confirm_box_fm.destroy()

    confirm_box_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    msg = tk.Label(confirm_box_fm, text=msg, font=('bold', 15))
    msg.pack(pady=20)
    confirm_box_fm.pack()
    yes_btn = tk.Button(confirm_box_fm, text="Yes", font=('bold', 15)
                        ,bd=0, bg=bg_color,fg='white',
                        command=lambda:action(True))
    yes_btn.place(x=50,y=160)
    c_btn = tk.Button(confirm_box_fm, text="Cancel", font=('bold', 15)
                        ,bd=0, bg=bg_color,fg='white',
                        command=lambda: action(False))
    c_btn.place(x=190,y=160)

    confirm_box_fm.place(x=100, y=128, width=320, height=220)

    confirm_box_fm.place(x=100,y=120,width=320,height=220)
    root.wait_window(confirm_box_fm)
    return answer.get()

def message_box(message):
    message_box_fm = tk.Frame(root, highlightbackground=bg_color,
    highlightthickness=3)
    close_btn = tk.Button(message_box_fm, text='X', bd=0, font=('Bold', 13),
    fg=bg_color,command=lambda:message_box_fm.destroy())
    close_btn.place(x=298, y=5)
    message_lb = tk.Label(message_box_fm, text=message, font=('Bold', 15))
    message_lb.pack(pady=50)
    message_box_fm.place(x=100, y=120, width=320, height=200)
 
def draw_student_card(s_pic_path,s_data):

    labels = """
ID Number:
Name:
Gender:
Age:
Contact:
Year:
Semester:
Batch:
Email:
"""

    s_card = Image.open('Images/student_card_frame.png')
    
    try:
        pic = Image.open(s_pic_path).resize((100, 100))
    except Exception as e:
        print(f"Error opening image: {e}")
        pic = Image.open('Images/add_image.png').resize((100, 100))

    s_card.paste(pic, (15, 25))

    draw = ImageDraw.Draw(s_card)
    heading_font = ImageFont.truetype('bahnschrift', 18)
    labels_font = ImageFont.truetype('arial', 13)

    draw.text(xy=(150, 60), text='Student Card', fill=(0, 0, 0),
              font=heading_font)
    draw.multiline_text(xy=(15, 120), text=labels, fill=(0, 0, 0),
                        font=labels_font, spacing=4)
    draw.multiline_text(xy=(95, 120), text=s_data, fill=(0, 0, 0),
                        font=labels_font, spacing=4)

    return s_card

def student_card_page(s_card_obj):

    def save_s_card():
        path= askdirectory()
        if path:
            #print(path)
            
            s_card_obj.save(f'{path}/student_card.png')
    def print_s_card():
        path= askdirectory()

        if path:
            print(path)
            s_card_obj.save(f'{path}/student_card.png')
            win32api.ShellExecute(0,'print',f'{path}/student_card.png',
                                  None,'.',0)        
    def close_page():
        student_card_fm.destroy()
        root.update()
        student_login_page()

    s_card_img=ImageTk.PhotoImage(s_card_obj)
    student_card_fm=tk.Frame(root,highlightbackground=bg_color,
                             highlightthickness=3)
    
    heading_lb=tk.Label(student_card_fm,text='Student Card',
                        bg=bg_color,fg='white',font=('bold',18))
    heading_lb.place(x=0,y=0,width=400)
    c_btn=tk.Button(student_card_fm,text='X',bg=bg_color,
                    fg='white',font=('bold',13),bd=0,
                    command=close_page)
    c_btn.place(x=370,y=0)

    s_card_lb=tk.Label(student_card_fm,image=s_card_img)
    s_card_lb.place(x=50,y=50)
    s_card_lb.image=s_card_img

    save_btn=tk.Button(student_card_fm,text='Save Student Card',
                       bg=bg_color,fg='white',font=('bold',15),
                       bd=1,command=save_s_card)
    save_btn.place(x=80,y=375)

    print_btn=tk.Button(student_card_fm,text='🖨',
                       bg=bg_color,fg='white',font=('bold',20),
                       bd=1,command=print_s_card)
    print_btn.place(x=270,y=370)
 
    student_card_fm.place(x=50,y=30,width=400,height=450)

def welcomepage():

    def next_student_login_page():
        wel_pg_fm.destroy()
        root.update()
        student_login_page()
    def next_admin_login_page():
        wel_pg_fm.destroy()
        root.update()
        admin_login_page()
    def next_add_account_page():
        wel_pg_fm.destroy()
        root.update()
        add_account_page()
    
    wel_pg_fm=tk.Frame(root,highlightbackground=bg_color,
    highlightthickness=3)

    #Heading
    heading_lb=tk.Label(wel_pg_fm,text='Welcome To Student Registration', 
                        fg='white',font=('Bold',18), bg=bg_color)
    heading_lb.place(x=0,y=0,width=780)
    #Create a Button for Student Login
    student_login_btn=tk.Button(wel_pg_fm,text='Student Login',bg=bg_color,
                                fg='white',font=('Bold',15),bd=0,command=next_student_login_page)
    student_login_img=tk.Button(wel_pg_fm,image=login_student_icon,bd=0)
    student_login_btn.place(x=350,y=125,width=200)
    student_login_img = tk.Button(wel_pg_fm, image=login_student_icon, bd=0)
    student_login_img.place(x=60, y=100)

    # #Create a Button for Admin 
    admin_login_btn = tk.Button(wel_pg_fm, text='Admin Login', bg=bg_color, 
                                fg='white', font=('Bold',15), bd=0,command=next_admin_login_page)
    admin_login_btn.place(x=350, y=225, width=200)
    admin_login_img = tk.Button(wel_pg_fm, image=login_admin_icon, bd=0)
    admin_login_img.place(x=60, y=200)
    #Button for Create Account
    add_student_btn = tk.Button(wel_pg_fm, text='Create Account', bg=bg_color,
                            fg='white', font=('Bold', 15), bd=0,command=next_add_account_page)
    add_student_btn.place(x=350, y=325, width=200)
    add_student_img = tk.Button(wel_pg_fm, image=add_student_icon, bd=0)
    add_student_img.place(x=60, y=300)

    wel_pg_fm.pack(pady=30)
    wel_pg_fm.pack_propagate(False)
    wel_pg_fm.configure(width=780,height=420)


def forget_passwd_page():
    def recover_passwd():

        if check_id_already_exists(id_number=s_ent.get()):

            conn=sqlite3.connect("student_account.db")
            cursor = conn.cursor()

            cursor.execute(f"""
            SELECT password FROM data WHERE id_number =='{s_ent.get()}'
            """)          
            conn.commit()
            r_passwd=cursor.fetchall()[0][0]
            # print('Recoverd password:',r_passwd)
            # conn.close()

            cursor = conn.cursor()
            cursor.execute(f"""
            SELECT email FROM data WHERE id_number =='{s_ent.get()}'
            """)            
            conn.commit()
            s_email=cursor.fetchall()[0][0]
            # print('Email Address',s_email)
            # conn.close()

            confirmation=confirmationbox(msg=f"""We will send Your password
on Your Email Address:\n{s_email}
Do you wan to Continue?""")
            #print(confirmation)
           
        else:
            #print('incorrect')
            message_box(message='Invalid Id Numbers')

    forgot_passwd_fm=tk.Frame(root,highlightbackground=bg_color,
        highlightthickness=3)
    
    heading_lb=tk.Label(forgot_passwd_fm,text='Forgot Password', 
                            fg='white',font=('Bold',18), bg=bg_color)
    heading_lb.place(x=0,y=0,width=350)

    close_btn = tk.Button(forgot_passwd_fm, text='X', bd=0, font=('Bold', 13),
                        fg=bg_color,command=lambda:forgot_passwd_fm.destroy())
    close_btn.place(x=320, y=0)

    s_lb=tk.Label(forgot_passwd_fm,text='Enter Student ID Number',
                  font=('bold',13))
    s_lb.place(x=70,y=70,width=40)

    s_ent=tk.Entry(forgot_passwd_fm,font=('bold',13),justify=tk.CENTER)
    s_ent.place(x=70,y=70,width=180)

    info_lb = tk.Label(forgot_passwd_fm,
    text="""Via Your Email Address
WE will Send to You
Your Forgot Password.""", justify=tk.LEFT)
    info_lb.place(x=75,y=110)

    next_btn = tk.Button(forgot_passwd_fm, text='Next', bg=bg_color,bd=0, font=('Bold', 13),
                        fg='white',command=recover_passwd)
    next_btn.place(x=130, y=200,width=80)

    forgot_passwd_fm.place(x=75,y=120,width=350,height=250)

def fetch_student_data(query):
    conn = sqlite3.connect('student_account.db')
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit() 
    response = cursor.fetchall();
    conn.close()
    return response
def fetch_leave_data():
    # Placeholder for fetching student leave data
    try:
        # Establish a connection to the database
        conn = sqlite3.connect("student_account.db")
        cursor = conn.cursor()

        # Fetch specific columns from 'leave_applications' table
        # Fetch specific columns from 'leave_applications' table
        cursor.execute("""
            SELECT student_id, data.name, start_date, reason, additional_reason, status
            FROM leave_applications
            JOIN data ON leave_applications.student_id = data.id_number
        """)
        
        leave_data = cursor.fetchall()

        # Close the connection
        conn.close()

        return leave_data

    except Exception as e:
        print(f"Error fetching leave requests: {e}")

# Assuming you have a function to submit a leave application to the database
def submit_leave_application(student_id, start_date, end_date, reason, additional_reason):
    try:
        conn = sqlite3.connect("student_account.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leave_applications (student_id,start_date, end_date, reason, additional_reason, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (student_id,start_date, end_date, reason, additional_reason))

        conn.commit()
        notify_admin_about_leave_application(student_id, start_date, end_date, reason, additional_reason)

        conn.close()

    except Exception as e:
        print(f"Error submitting leave application: {e}")
        messagebox.showerror("Error", "An error occurred while submitting the leave application.")
        

def notify_admin_about_leave_application(student_id, start_date, end_date, reason, additional_reason):
    # Implement your logic to notify the admin (e.g., update a notification table, send an email, etc.)
    # For simplicity, let's print a message here
    print(f"New leave application from student {student_id}:\n"
          f"Start Date: {start_date}, End Date: {end_date}\n"
          f"Reason: {reason}, Additional Reason: {additional_reason}")

def student_dashboard(student_id):
    get_student_details = fetch_student_data(f"""
    SELECT name, age, gender, phone_number, year, semester, batch, email FROM data WHERE id_number =='{student_id}'
    """)
    
    get_student_pic = fetch_student_data(f"""
    SELECT image FROM data WHERE id_number =='{student_id}'
    """)
    
    student_pic = BytesIO(get_student_pic[0][0])
    #print(student_pic)

    def logout():
        confirm=confirmationbox(msg='Do You Want To \n Logout?')

        if confirm:
            dashboard_fm.destroy()
            welcomepage()
            root.update()

    def switch(indicator,page):
        home_btn_indicator.config(bg='mistyrose4')
        stu_btn_indicator.config(bg='mistyrose4')
        sec_btn_indicator.config(bg='mistyrose4')
        edit_btn_indicator.config(bg='mistyrose4')
        
        del_btn_indicator.config(bg='mistyrose4')
        leave_btn_indicator.config(bg='mistyrose4')
        log_btn_indicator.config(bg='mistyrose4')
        indicator.config(bg=bg_color)

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()
        page()
    dashboard_fm=tk.Frame(root,highlightbackground=bg_color,bg='mistyrose1',
        highlightthickness=3)
    
    options_fm=tk.Frame(dashboard_fm,highlightbackground=bg_color,
        highlightthickness=3,bg='mistyrose4')
    options_fm.place(x=0,y=0,width=125,height=575)
    home_btn = tk.Button(options_fm, text='Home', font=('Bold', 15),
                        fg=bg_color, bg='mistyrose4', bd=0,
                        command=lambda:switch(indicator=home_btn_indicator,
                                              page=home_page))
    home_btn.place(x=10, y=50)
    home_btn_indicator = tk.Label(options_fm, bg=bg_color)
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    student_card_btn = tk.Button(options_fm, text='Student\nCard', font=('Bold', 15),
                        fg=bg_color, bg='mistyrose4', bd=0, justify=tk.LEFT,
                        command=lambda:switch(indicator=stu_btn_indicator,
                                              page=s_dashboard_card_page))
    student_card_btn.place(x=10, y=100)
    stu_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    stu_btn_indicator.place(x=5, y=108, width=3, height=40)
    security_btn = tk.Button(options_fm, text='Security', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=lambda:switch(indicator=sec_btn_indicator,
                                                  page=security_page))
    security_btn.place(x=10, y=170)
    sec_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    sec_btn_indicator.place(x=5, y=170, width=3, height=40)
    edit_btn = tk.Button(options_fm, text='Edit Data', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=lambda:switch(indicator=edit_btn_indicator,
                                                  page=edit_page))
    edit_btn.place(x=10,y=220)
    edit_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    edit_btn_indicator.place(x=5, y=218, width=3, height=40)

    leave_btn = tk.Button(options_fm, text='Leave \nApp', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=lambda:switch(indicator=leave_btn_indicator,
                                                  page=Leave_page))
    leave_btn.place(x=10,y=270)
    leave_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    leave_btn_indicator.place(x=5, y=278, width=3, height=40)


    delete_btn = tk.Button(options_fm, text='Delete \nAccount', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=lambda:switch(indicator=del_btn_indicator,
                                                  page=del_page))
    delete_btn.place(x=10,y=400)
    del_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    del_btn_indicator.place(x=5, y=348, width=3, height=40)

    
    logout_btn = tk.Button(options_fm, text='Logout', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=logout)
    logout_btn.place(x=10,y=500)
    log_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    log_btn_indicator.place(x=5, y=498, width=3, height=40)

    def home_page():
        student_pic_image_obj = Image.open(student_pic)
        size = 100
        mask = Image.new(mode='L', size=(size, size))
        draw_circle = ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0, 0, size, size), fill=255,outline=True)
        output = ImageOps.fit(image=student_pic_image_obj, size=mask.size,
                            centering=(1, 1))
        output.putalpha(mask)
        stu_picture=ImageTk.PhotoImage(output)
        
        home_page_fm = tk.Frame(pages_fm)

        student_pic_1b = tk.Label(home_page_fm,image=stu_picture )
        student_pic_1b.image=stu_picture
        student_pic_1b.place(x=10, y=10)

        hi_lb=tk.Label(home_page_fm,text=f'Hi!!!{get_student_details[0][0]}',
                                          font=('Bold',15))    
        student_details = f"""
Student ID: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n
Gender: {get_student_details[0][2]}\n
Contact: {get_student_details[0][3]}\n
Year: {get_student_details[0][4]}\n
Semester: {get_student_details[0][5]}\n
Batch: {get_student_details[0][6]}\n
Email: {get_student_details[0][7]}
"""
        stu_details_lb=tk.Label(home_page_fm,text=student_details,
                                font=('Bold',15),justify=tk.LEFT)
        stu_details_lb.place(x=20,y=130)
        
        hi_lb.place(x=130,y=50)                                  
        
        home_page_fm.pack(fill=tk.BOTH, expand=True)
    def s_dashboard_card_page():
        student_details = f"""
{student_id}
{get_student_details[0][0]}
{get_student_details[0][1]}
{get_student_details[0][2]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
{get_student_details[0][6]}
{get_student_details[0][7]}
"""
        s_card_obj=draw_student_card(s_pic_path=student_pic,
                                     s_data=student_details)
        
        def save_s_card():
            path= askdirectory()

            if path:
                #print(path)
                
                s_card_obj.save(f'{path}/student_card1.png')

        def print_s_card():
            path= askdirectory()

            if path:
                #print(path)
                s_card_obj.save(f'{path}/student_card.png')
                win32api.ShellExecute(0,'print',f'{path}/student_card.png',
                                    None,'.',0)
                               
        sc_img_obj =ImageTk.PhotoImage(s_card_obj)
        stud_page_fm = tk.Frame(pages_fm)
        card_lb=tk.Label(stud_page_fm,image=sc_img_obj)
        card_lb.image=sc_img_obj
        card_lb.place(x=180,y=50)
       
        save_sc_btn=tk.Button(stud_page_fm,text='Save Student Card',
                        bg=bg_color,fg='white',font=('bold',15),
                        bd=1,command=save_s_card)
        save_sc_btn.place(x=230,y=400)

        print_sc_btn=tk.Button(stud_page_fm,text='🖨',
                        bg=bg_color,fg='white',font=('bold',15),
                        bd=1,command=print_s_card)
        print_sc_btn.place(x=420,y=400)

        stud_page_fm.pack(fill=tk.BOTH, expand=True)
    def security_page(): 

        def show_hide_passwd():
            if current_passwd_ent['show']=='*':
                current_passwd_ent.config(show='')
                show_hide_btn.config(image=unlock_icon)
            else:
                current_passwd_ent.config(show='*')
                show_hide_btn.config(image=lock_icon)

        def set_password():
            if new_passwd_ent.get() !='':
                confirm=confirmationbox(msg='Do You Want to Change Password')
                if confirm:
                    conn = sqlite3.connect('student_account.db')

                    cursor = conn.cursor()

                    cursor.execute(f"""UPDATE data SET password = '{new_passwd_ent.get()}'
                                    WHERE id_number=='{student_id}'""")

                    conn.commit() 
                    conn.close()
                    message_box(message="Password Changed Successfully")
                    current_passwd_ent.config(state=tk.NORMAL)
                    current_passwd_ent.delete(0,tk.END)
                    current_passwd_ent.insert(0,new_passwd_ent.get())
                    current_passwd_ent.config(state='readonly')
            else:
                message_box(message="Enter New Password Required")
                
        sec_page_fm = tk.Frame(pages_fm,bg='mistyrose3')

        sec_page_1b = tk.Label(sec_page_fm, text='Your Current password',
                              font=('Bold', 15),justify=tk.LEFT)

        sec_page_1b.place(x=200, y=30)

        current_passwd_ent=tk.Entry(sec_page_fm,font=('Bold', 15),
                                   justify=tk.CENTER,show='*')
        current_passwd_ent.place(x=200,y=80)

        s_current_passwd=fetch_student_data(f"SELECT password FROM data WHERE id_number =='{student_id}'")
        current_passwd_ent.insert(tk.END,s_current_passwd[0][0])
        current_passwd_ent.config(state='readonly')
        show_hide_btn=tk.Button(sec_page_fm,image=lock_icon,bd=0,
                            command=show_hide_passwd)
        show_hide_btn.place(x=440,y=70)

        sec_page_1b = tk.Label(sec_page_fm, text='Change password',
                              font=('Bold', 15),bg='red',fg='white')
        sec_page_1b.place(x=200, y=210,width=250)
        new_passwd_lb=tk.Label(sec_page_fm,text='Set New Password',
                               font=('Bold', 15))
        new_passwd_lb.place(x=220,y=280)

        new_passwd_ent=tk.Entry(sec_page_fm,font=('Bold', 15),
                                justify=tk.CENTER)
        new_passwd_ent.place(x=200,y=330)

        change_btn=tk.Button(sec_page_fm,text='SET PASSWORD',bg=bg_color,
                             fg='white',font=('Bold', 15),
                             command=set_password)
        change_btn.place(x=225,y=380)

        sec_page_fm.pack(fill=tk.BOTH, expand=True)
    def edit_page():
        edit_page_fm = tk.Frame(pages_fm)

        pic_path = tk.StringVar()
        pic_path.set('')

        def open_pic(): 
            path=askopenfilename()
            if path:
                img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                pic_path.set(path)

                picbnt.config(image=img)
                picbnt.image = img

        def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightcolor=bg_color,
                                    highlightbackground='gray')
        def check_invalid_email(email):
    
            pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
    
            match = re.match(pattern=pattern, string=email)
    
            return match            
        def check_input():
            nonlocal get_student_details,get_student_pic,student_pic

            if s_name_ent.get() == '':
                s_name_ent.config(highlightcolor="red",
                                highlightbackground='red')
                s_name_ent.focus()
                message_box('Student Full Name is Required')
            elif s_age_ent.get() == '':
                s_age_ent.config(highlightcolor="red",
                                highlightbackground='red')
                s_age_ent.focus()
                message_box('Student Age is Required')
            elif s_gmail_ent.get() == '':
                s_gmail_ent.config(highlightcolor="red",
                                highlightbackground='red')
                s_gmail_ent.focus()
                message_box('Gmail is Required')
            elif not check_invalid_email(email=s_gmail_ent.get().lower()):
                s_gmail_ent.config(highlightcolor="red",
                                highlightbackground='red')
                s_gmail_ent.focus()

            else:
                if pic_path.get() != '':
                    new_s_pic = Image.open(pic_path.get()).resize((100,100))
                    new_s_pic.save('temp_pic.png')
                    
                    with open('temp_pic.png', 'rb') as read_new_pic:
                        new_picture_b=read_new_pic.read()
                        read_new_pic.close()

                    conn = sqlite3.connect('student_account.db')

                    cursor = conn.cursor()

                    cursor.execute(f"""UPDATE data SET image=? 
                                   WHERE id_number=='{student_id}'""",
                                   [new_picture_b])
                    conn.commit() 
                    conn.close()

                name=s_name_ent.get(),
                age=s_age_ent.get(),
                phone_number=s_c_ent.get(),
                year=bnt3.get(),
                semester=bnt4.get(),
                batch=bnt5.get(),
                email=s_gmail_ent.get(),

                conn = sqlite3.connect('student_account.db')
                cursor = conn.cursor()

                cursor.execute("""UPDATE data SET 
                  name = ?,
                  age = ?,
                  phone_number = ?,
                  year = ?,
                  semester = ?,
                  batch = ?,
                  email = ?
                  WHERE id_number = ?""",
                  (name[0], age[0], phone_number[0], year[0], semester[0], batch[0], email[0], student_id))
                conn.commit() 
                conn.close()

                get_student_details = fetch_student_data(f"""
                SELECT name, age, gender, phone_number, year, semester, batch, email FROM data WHERE id_number =='{student_id}'
                    """)
                
                get_student_pic = fetch_student_data(f"""
                SELECT image FROM data WHERE id_number == '{student_id}'
                    """)
                
                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message="Data is Successfully Updated.")
                    
        s_current_pic=ImageTk.PhotoImage(Image.open(student_pic))

        add_picsection=tk.Frame(edit_page_fm,highlightbackground=bg_color,
            highlightthickness=2)
        picbnt=tk.Button(add_picsection,image=s_current_pic,bd=0,
                        command=lambda :open_pic())
        picbnt.image=s_current_pic
        picbnt.pack()
        add_picsection.place(x=5,y=5,width=105,height=105)

        s_name_lb=tk.Label(edit_page_fm,text='Enter Student Full Name:',
                    font=('bold',12))
        s_name_lb.place(x=5,y=130)
        s_name_ent=tk.Entry(edit_page_fm,highlightbackground='grey',highlightcolor=bg_color,
                                highlightthickness=2,font=('bold',15))
        s_name_ent.place(x=5,y=160,width=180)
        s_name_ent.bind('<KeyRelease>',
                        lambda e: remove_highlight_warning(entry=s_name_ent))
        s_name_ent.insert(tk.END,get_student_details[0][0])
        s_age_lb=tk.Label(edit_page_fm,text='Enter Age:',
                        font=('bold',12))
        
        s_age_lb.place(x=5,y=210)
        s_age_ent=tk.Entry(edit_page_fm,highlightbackground='grey',highlightcolor=bg_color,
                                highlightthickness=2,font=('bold',15))
        s_age_ent.place(x=5,y=235,width=180)
        s_age_ent.bind('<KeyRelease>',
                        lambda e: remove_highlight_warning(entry=s_age_ent))
        
        s_age_ent.insert(tk.END,get_student_details[0][1])

        s_c_lb=tk.Label(edit_page_fm,text='Enter Contact Number:',
                    font=('bold',12))
        s_c_lb.place(x=5,y=275)
        s_c_ent=tk.Entry(edit_page_fm,highlightbackground='grey',highlightcolor=bg_color,
                                highlightthickness=2,font=('Bold',15))
        s_c_ent.place(x=5,y=310,width=180)

        s_c_ent.insert(tk.END,get_student_details[0][3])
        
        s_year_lb=tk.Label(edit_page_fm,text='Select Year:',
                        font=('bold',12))
        s_year_lb.place(x=5,y=350)
        bnt3=Combobox(edit_page_fm,font=('bold',11),
                        state='readonly',value=list)
        bnt3.place(x=5, y=380, width=80)

        bnt3.set(get_student_details[0][4])

        s_sem_lb=tk.Label(edit_page_fm,text='Select Semester:',
                        font=('bold',12))
        s_sem_lb.place(x=100,y=350)
        bnt4=Combobox(edit_page_fm,font=('bold',11),
                        state='readonly',value=list_sem)
        bnt4.place(x=100, y=380, width=70)

        bnt4.set(get_student_details[0][5])

        s_batch_lb=tk.Label(edit_page_fm,text='Select Batch:',
                        font=('bold',12))
        s_batch_lb.place(x=5,y=420)
        bnt5=Combobox(edit_page_fm,font=('bold',11),
                        state='readonly',value=list_batch)
        bnt5.place(x=5, y=450, width=100)

        bnt5.set(get_student_details[0][6])

        s_gmail_lb=tk.Label(edit_page_fm,text='Enter Your Gmail:',
                    font=('bold',12))
        s_gmail_lb.place(x=5,y=480)
        s_gmail_ent=tk.Entry(edit_page_fm,highlightbackground='grey',highlightcolor=bg_color,
                                highlightthickness=2,font=('bold',15))
        s_gmail_ent.place(x=5,y=510,width=180)
        s_gmail_ent.bind('<KeyRelease>',
                        lambda e: remove_highlight_warning(entry=s_gmail_ent))
        s_gmail_ent.insert(tk.END,get_student_details[0][7])
        update_btn=tk.Button(edit_page_fm,text='Update',font=('bold',15),
                             fg='white',bg=bg_color,bd=0,
                             command=check_input)
        update_btn.place(x=220,y=470,width=90)

        edit_page_fm.pack(fill=tk.BOTH, expand=True)

    def del_page():
        def confirm_delete_account():
            confirm=confirmationbox(msg='Are you sure\n Want to Delete the Account')

            if confirm:
                conn = sqlite3.connect('student_account.db')
                cursor = conn.cursor()

                cursor.execute(f"""
                DELETE FROM data WHERE id_number == '{student_id}'
                """)
                conn.commit() 
                conn.close()
                dashboard_fm.destroy()
                welcomepage()
                root.update()
                message_box(message='Your Account is Deleted\n Successfully')

        del_page_fm = tk.Frame(pages_fm,bg='mistyrose3')
        del_page_1b = tk.Label(del_page_fm, text='⚠ Delete Page',
        bg='red',font=('Bold', 15))
        del_page_1b.place(x=200, y=100,width=250)

        del_acc_btn=tk.Button(del_page_fm,text='DELETE ACCOUNT',bg='red',
                              fg='white',font=('bold',13),
                              command=confirm_delete_account)
        del_acc_btn.place(x=250,y=200)

        del_page_fm.pack(fill=tk.BOTH, expand=True)

    def Leave_page():
        
        def submit_leave():
            start_date_str = start_date_var.get()
            end_date_str = end_date_var.get()
            reason = reason_var.get()
            additional_reason = other_reason_entry.get()

            # Validate input
            if not start_date_str or not end_date_str or not reason:
                message_box("Please fill in all fields.")
            else:
                   # Convert date strings to datetime objects
                start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
                end_date = datetime.strptime(end_date_str, '%d-%m-%Y')

                # Calculate the number of leave days
                leave_days = (end_date - start_date).days + 1

                # If the reason is "Other," use the additional reason provided
                if reason == "Other" and not additional_reason:
                    message_box("Please specify the \nreason in the 'Other' field.")
                else:
                    # Submit leave application
                    submit_leave_application(student_id, start_date, end_date, reason, additional_reason)
                    root.update()          
                    message_box(f"Leave application \nsubmitted successfully.\nTotal leave days: {leave_days}")

                    # Clear input fields
                    start_date_var.set('')
                    end_date_var.set('')
                    reason_var.set('')
                    other_reason_entry.delete(0, tk.END)
                
        
        
        leave_app_frame = tk.Frame(pages_fm, bg='mistyrose3')
        leave_app_frame.pack(fill=tk.BOTH, expand=True)

        start_date_label = tk.Label(leave_app_frame, text="Start Date:", 
                                    font=('bold', 12), bg='mistyrose3')
        start_date_label.place(x=20, y=150)
       

        start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(leave_app_frame, font=('bold', 12),
                                     textvariable=start_date_var)
        start_date_entry.place(x=120, y=150)

        def pick_start_date():
            start_date_calendar = Calendar(leave_app_frame, selectmode='day',
                                        date_pattern='dd-mm-yyyy', year=2024, month=1, day=1)
            start_date_calendar.place(x=85, y=180)

            def set_start_date():
                start_date_var.set(start_date_calendar.get_date())
                start_date_calendar.place_forget()
                ok_button.place_forget()  # Hide the OK button

            ok_button = tk.Button(leave_app_frame, text="OK", command=set_start_date,
                                font=('bold', 10), fg='white', bg=bg_color, bd=1)
            ok_button.place(x=85, y=360)
            

        start_date_picker_button = tk.Button(leave_app_frame, text="Pick Date",
                                            font=('bold', 10), fg='white', bg=bg_color, bd=1, command=pick_start_date)
        start_date_picker_button.place(x=250, y=150)

        end_date_label = tk.Label(leave_app_frame, text="End Date:", font=('bold', 12), bg='mistyrose3')
        end_date_label.place(x=20, y=200)

        end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(leave_app_frame, font=('bold', 12), textvariable=end_date_var)
        end_date_entry.place(x=120, y=200)

        def pick_end_date():
            end_date_calendar = Calendar(leave_app_frame, selectmode='day',
                                        date_pattern='dd-mm-yyyy', year=2024, month=1, day=1)
            end_date_calendar.place(x=85, y=240)

            def set_end_date():
                end_date_var.set(end_date_calendar.get_date())
                end_date_calendar.place_forget()
                ok_button.place_forget()  # Hide the OK button

            ok_button = tk.Button(leave_app_frame, text="OK", command=set_end_date,
                                font=('bold', 10), fg='white', bg=bg_color, bd=1)
            ok_button.place(x=85, y=420)

        end_date_picker_button = tk.Button(leave_app_frame, text="Pick Date",
                                        font=('bold', 10), fg='white', bg=bg_color, bd=1, command=pick_end_date)
        end_date_picker_button.place(x=250, y=200)

        reason_label = tk.Label(leave_app_frame, text="Reason:", font=('bold', 12), bg='mistyrose3')
        reason_label.place(x=20, y=300)

        # Radio buttons for reasons
        reason_var = tk.StringVar()
        sick_radio = tk.Radiobutton(leave_app_frame, text="SICK", variable=reason_var, 
                                    value="SICK", bg='mistyrose3')
        sick_radio.place(x=90, y=300)

        vacation_radio = tk.Radiobutton(leave_app_frame, text="VACATION", variable=reason_var, 
                                        value="VACATION", bg='mistyrose3')
        vacation_radio.place(x=150, y=300)

        other_radio = tk.Radiobutton(leave_app_frame, text="Other", variable=reason_var, 
                                     value="Other", bg='mistyrose3')
        other_radio.place(x=250, y=300)

        # Entry for additional reason when "Other" is selected
        other_reason_label = tk.Label(leave_app_frame, text="Specify Other Reason:", font=('bold', 12), bg='mistyrose3')
        other_reason_label.place(x=20, y=340)
        other_reason_entry = tk.Entry(leave_app_frame, font=('bold', 12))
        other_reason_entry.place(x=20, y=365,width=280)

        submit_btn = tk.Button(leave_app_frame, text="Submit", font=('bold', 12),
                            fg='white', bg=bg_color, bd=1, command=submit_leave)
        submit_btn.place(x=150, y=480)

        # Label to display the count of leave days
        leave_days_label = tk.Label(leave_app_frame, text="Leave Days: 0", font=('bold', 12))
        leave_days_label.place(x=20, y=400)

        def update_leave_days():
            start_date_str = start_date_var.get()
            end_date_str = end_date_var.get()

            # Update leave days label with the calculated difference
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
                end_date = datetime.strptime(end_date_str, '%d-%m-%Y')
                leave_days = (end_date - start_date).days + 1
                leave_days_label.config(text=f"Leave Days: {leave_days}")
        exreg_1b = tk.Label(leave_app_frame,text="Leave Application",
                            font=('Bold',15),bg=bg_color,fg='snow' )
        exreg_1b.place(x=0,y=0,width=650)

        # Bind the function to update leave days on date changes
        start_date_var.trace_add('write', lambda *args: update_leave_days())
        end_date_var.trace_add('write', lambda *args: update_leave_days())


    pages_fm = tk.Frame(dashboard_fm, bg='mistyrose3')
    pages_fm.place(x=130, y=5, width=640, height=565)
    home_page()

    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=780,height=580)

def student_login_page():
    def show_hide_passwd():
        if passwd_ent['show']=='*':
            passwd_ent.config(show='')
            show_hide_btn.config(image=unlock_icon)
        else:
            passwd_ent.config(show='*')
            show_hide_btn.config(image=lock_icon)

    def backtowelcomepage():
        student_login_fm.destroy()
        root.update()
        welcomepage()

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color,
                                highlightbackground='gray')

    def login_acc():
        verify_id_no=check_id_already_exists(id_number=id_num_ent.get())
        if verify_id_no:
            #print('ID Number is Correct')

            verify_password=check_valid_passwd(id_number=id_num_ent.get(),
                                               password=passwd_ent.get())
            if verify_password:
                id_number=id_num_ent.get()
                student_login_fm.destroy()
                student_dashboard(student_id=id_number)
                root.update()
                #print('Password is correct')
            else:
                #print('!Oppsizz Password is incorrect')
                passwd_ent.config(highlightcolor='red',
                             highlightbackground='red')
                message_box('Enter Valid Password')

        else:
            #print('!Opps ID is Incorrect')
            id_num_ent.config(highlightcolor='red',
                             highlightbackground='red')
            
            message_box('Enter Valid ID Number')
    #Create a student page
    student_login_fm=tk.Frame(root,highlightbackground=bg_color,
        highlightthickness=3)
    student_login_fm.pack(pady=30)
    student_login_fm.pack_propagate(False)
    student_login_fm.configure(width=780,height=470)

    heading_lb=tk.Label(student_login_fm,text='Welcome To Student Login', 
                            fg='white',font=('Bold',18), bg=bg_color)
    heading_lb.place(x=0,y=0,width=780)

    backbmt=tk.Button(student_login_fm,text='↩',font=('bold',22),fg=bg_color,command=backtowelcomepage)
    backbmt.place(x=5,y=40)

    student_login_img = tk.Button(student_login_fm, 
                                  image=login_student_icon, bd=0,)
    student_login_img.place(x=360, y=40)
    #entry data
    id_num_lb=tk.Label(student_login_fm,text='Enter Student ID Number',font=('Bold',15))
    id_num_lb.place(x=290,y=140)
    id_num_ent=tk.Entry(student_login_fm,font=('Bold',15),justify=tk.CENTER,highlightcolor=bg_color,
                        highlightbackground='grey',highlightthickness=2)
    id_num_ent.place(x=290,y=190)
    id_num_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=id_num_ent))

    passwd_lb=tk.Label(student_login_fm,text="Password",font=('Bold',15))
    passwd_lb.place(x=290,y=240)
    passwd_ent=tk.Entry(student_login_fm,font=('Bold',15),justify=tk.CENTER,highlightcolor=bg_color,
                        highlightbackground='grey',
                        highlightthickness=2,
                        show='*')
    passwd_ent.place(x=290,y=290)
    id_num_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=passwd_ent))


    show_hide_btn=tk.Button(student_login_fm,image=lock_icon,bd=0,
                            command=show_hide_passwd)
    show_hide_btn.place(x=540,y=280)

    login_bnt=tk.Button(student_login_fm,text='Login',font=('Bold',15),
                        command=login_acc)
    login_bnt.place(x=300,y=340,width=200,height=40)

    forget_Passwd_btn=tk.Button(student_login_fm,text='⚠\nForget Password',fg=bg_color,
                                font=('Bold', 15), bd=0)
    forget_Passwd_btn.place(x=320,y=390)
    
def admin_dashboard():
    def admin_logout():
        confirm = confirmationbox(msg='Do You Want To \n Logout?')

        if confirm:
            admin_dashboard_fm.destroy()
            welcomepage()
            root.update()

    def switch(indicator, page_func):
        home_btn_indicator.config(bg='mistyrose4')
        find_btn_indicator.config(bg='mistyrose4')
        leave_request_btn_indicator.config(bg='mistyrose4')
        indicator.config(bg=bg_color)

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()

        page_func()

    admin_dashboard_fm = tk.Frame(root, highlightbackground=bg_color, bg='mistyrose1', highlightthickness=3)

    options_fm = tk.Frame(admin_dashboard_fm, highlightbackground=bg_color, highlightthickness=3, bg='mistyrose4')
    options_fm.place(x=0, y=0, width=125, height=575)

    home_btn = tk.Button(options_fm, text='Home', font=('Bold', 15),
                         fg=bg_color, bg='mistyrose4', bd=0,
                         command=lambda: switch(indicator=home_btn_indicator, page_func=admin_home_page))
    home_btn.place(x=10, y=50)

    home_btn_indicator = tk.Label(options_fm, bg=bg_color)
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    find_btn = tk.Button(options_fm, text='Find \n Student', font=('Bold', 15),
                         fg=bg_color, bg='mistyrose4', bd=0,
                         command=lambda: switch(indicator=find_btn_indicator, page_func=find_student))
    find_btn.place(x=10, y=150)

    find_btn_indicator = tk.Label(options_fm, bg=bg_color)
    find_btn_indicator.place(x=5, y=148, width=3, height=40)

    leave_request_btn = tk.Button(options_fm, text='Leave\nPermission\nRequest', font=('Bold', 15),
                            fg=bg_color, bg='mistyrose4', bd=0,
                            command=lambda:switch(indicator=leave_request_btn_indicator,
                                                  page_func=Leave_Permission_Request_page))
    leave_request_btn.place(x=10,y=240)
    leave_request_btn_indicator = tk.Label(options_fm, bg='mistyrose4')
    leave_request_btn_indicator.place(x=5, y=238, width=3, height=40)

    logout_btn = tk.Button(options_fm, text='Logout', font=('Bold', 15),
                           fg=bg_color, bg='mistyrose4', bd=0,
                           command=admin_logout)
    logout_btn.place(x=10, y=350)

    pages_fm = tk.Frame(admin_dashboard_fm, bg='mistyrose3')
    pages_fm.place(x=130, y=5, width=660, height=565)

    def admin_home_page():
        global admin_picture  # Use the global variable

        admin_pic_image_obj = Image.open("Images/admin_img.png")
        img_admin = admin_pic_image_obj.resize((100, 100))
        admin_picture = ImageTk.PhotoImage(img_admin)
        
        admin_home_page_fm = tk.Frame(pages_fm)

        admin_pic_1b = tk.Label(admin_home_page_fm,image= admin_picture)
        
        admin_pic_1b.place(x=10, y=10,width=100,height=100)

        hi_lb=tk.Label(admin_home_page_fm,text='Hi!!! Admin',
                                          font=('Bold',15))
        hi_lb.place(x=130,y=50)  

        class_list_lb = tk.Label(admin_home_page_fm, text='Number of Students By Year And Semester.',
        font=('Bold', 13), bg=bg_color, fg='white')
        class_list_lb.place(x=10, y=130,width=600)

        students_num_lb = tk.Label(admin_home_page_fm, text='', font=('Bold', 13),
                            justify=tk.LEFT)
        students_num_lb.place(x=20, y=260)

        for i in list_sem:
            result1 = fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE semester == '{i}'")
            students_num_lb['text'] += f"{i}    {result1[0][0]}\n"

            #print(i,result1)

        students_numbers_lb = tk.Label(admin_home_page_fm, text='', font=('Bold', 13),
                            justify=tk.LEFT)
        students_numbers_lb.place(x=20, y=190)

        for i in list:
            result = fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE year == '{i}'")
            students_numbers_lb['text'] += f"{i}   {result[0][0]}\n"

            #print(i,result)


        admin_home_page_fm.pack(fill=tk.BOTH, expand=True) 
    def find_student():
        def search():
            conn = sqlite3.connect('student_account.db')
            cursor = conn.cursor()
            find_option = find_btn.get()
            find_value = find_ent.get()
            if find_option and find_value:
                # Use parameterized query to prevent SQL injection
                query = f"SELECT id_number, name, age, gender, year, semester, batch FROM data WHERE {find_option}=?"
                cursor.execute(query, (find_value,))
                result = cursor.fetchall()
                # Clear the existing data in the table
                for item in table.get_children():
                    table.delete(item)
                # Insert new data into the table
                for row in result:
                    table.insert("", "end", values=row)
                # Set column widths dynamically
                for col, width in zip(columns, [30, 30, 15, 15, 20,15]):
                    table.column(col, width=width)
            else:
                print("Please select a search option and enter a value.")
            conn.close()

        student_search_frame = tk.Frame(pages_fm)

        search_lb = tk.Label(student_search_frame, bg=bg_color, text='Find student Records', justify=tk.CENTER,
                            font=('Bold', 15), fg='white')
        search_lb.place(x=45, y=10)

        find_lb = tk.Label(student_search_frame, text='Find by:', font=('bold', 12))
        find_lb.place(x=50, y=50)

        find_btn = Combobox(student_search_frame, font=('bold', 10),
                            state='readonly', values=list_records)
        find_btn.place(x=120, y=50, width=100)

        find_ent = tk.Entry(student_search_frame, font=('bold', 12))
        find_ent.place(x=50, y=100)

        r_lb = tk.Label(student_search_frame, text='Record Table', font=('bold', 15), justify=tk.CENTER,
                        bg=bg_color, fg='white')
        r_lb.place(x=50, y=160, width=200)

        # Code for adding a table
        columns = ('id_number', 'name', 'age', 'gender', 'year', 'semester', 'batch')
        table = Treeview(student_search_frame, columns=columns, show='headings')

        # Define the table headers
        for col in columns:
            table.heading(col, text=col, anchor='center')

        # Position the table
        table.place(x=0, y=160, width=600, height=350)

        search_btn = tk.Button(student_search_frame, text='Search', command=search)
        search_btn.place(x=50, y=130)

        student_search_frame.pack(fill=tk.BOTH, expand=True)

    def Leave_Permission_Request_page():
        def process_request():
            selected_items = tree.selection()
            if not selected_items:
                message_box("Please select leave requests.")
                return

            for selected_item in selected_items:
                selected_data = tree.item(selected_item)['values']
                student_id, name, start_date, reason, additional_reason, status = selected_data

                confirmation_msg = f"Are you sure you want to {approval_var.get().lower()} leave request for {name} (ID: {student_id})?"
                confirmation = messagebox.askyesno("Confirmation", confirmation_msg)

                if confirmation:
                    new_status = approval_var.get()

                    # Update status in the database
                    conn = sqlite3.connect("student_account.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE leave_applications SET status = ? WHERE student_id = ? AND start_date = ?",
                        (new_status, student_id, start_date))
                    conn.commit()
                    conn.close()

                    # Update status in the Treeview
                    tree.item(selected_item, values=(student_id, name, start_date, reason, additional_reason, new_status))
                    update_treeview_row_color(selected_item, new_status)  # Highlight row based on status

                    # Update status in the Excel file
                    excel_file_path = 'student_account_data.xlsx'
                    if os.path.exists(excel_file_path):
                        df = pd.read_excel(excel_file_path, sheet_name='leave_applications')
                        df.loc[(df['student_id'] == student_id) & (df['start_date'] == start_date), 'status'] = new_status
                        df.to_excel(excel_file_path, index=False, sheet_name='leave_applications')

                    message_box(f"Leave request for \n{name} (ID: {student_id}) \nfor days {new_status.lower()}\n successfully.")

        def update_treeview_row_color(item, status):
            # Function to update row color based on the status
            if status == "Pending":
                tree.item(item, tags=("Pending",))
            elif status == "Approve":
                tree.item(item, tags=("Approve",))
            elif status == "Deny":
                tree.item(item, tags=("Deny",))

        leave_permission_page_fm = tk.Frame(pages_fm, bg='rosybrown')
        lv_pg_lbl = tk.Label(leave_permission_page_fm, text='Leave Application Requests',
                            font=('Bold', 15),bg=bg_color,fg='snow', justify=tk.LEFT)
        lv_pg_lbl.place(x=20, y=20, width=600)
        leave_permission_page_fm.pack(fill=tk.BOTH, expand=True)

        # Create Treeview to display leave requests
        tree = Treeview(leave_permission_page_fm,
                        columns=('student_id', 'name', 'start_date', 'reason', 'additional_reason', 'status'))
        tree.heading('#0', text='ID')
        tree.heading('student_id', text='Student ID')
        tree.heading('name', text='Name')
        tree.heading('start_date', text='Start Date')
        tree.heading('reason', text='Reason')
        tree.heading('additional_reason', text='Additional Reason')
        tree.heading('status', text='Status')
        tree.column('#0', stretch=tk.NO, minwidth=0, width=0)  # Hide ID column

        # Populate Treeview with leave requests data
        conn = sqlite3.connect("student_account.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT leave_applications.student_id, data.name, leave_applications.start_date,
                leave_applications.reason, leave_applications.additional_reason, leave_applications.status
            FROM leave_applications
            JOIN data ON leave_applications.student_id = data.id_number
        """)
        leave_requests = cursor.fetchall()
        for request in leave_requests:
            item_id = tree.insert('', 'end', values=request)
            update_treeview_row_color(item_id, request[-1])  # Highlight row based on status
        conn.close()


        # Define tag configurations for different status colors
        tree.tag_configure("Pending", background="yellow")
        tree.tag_configure("Approve", background="green")
        tree.tag_configure("Deny", background="red")

        tree.pack(pady=50)

        # Radio buttons for approval/denial
        approval_var = tk.StringVar()
        approval_var.set("Approve")  # Default selection
        approve_radio = tk.Radiobutton(leave_permission_page_fm, text="Approve", variable=approval_var, value="Approve")
        approve_radio.place(x=20, y=500)

        deny_radio = tk.Radiobutton(leave_permission_page_fm, text="Deny", variable=approval_var, value="Deny")
        deny_radio.place(x=100, y=500)

        # Button to process the selected leave request
        process_btn = tk.Button(leave_permission_page_fm, text="Process Request", font=('bold', 12),
                                fg='white', bg=bg_color, bd=1, command=process_request)
        process_btn.place(x=200, y=500)



    pages_fm = tk.Frame(admin_dashboard_fm, bg='mistyrose3')
    pages_fm.place(x=130, y=5, width=640, height=565)
    admin_home_page()
    
    admin_dashboard_fm.pack(pady=5)
    admin_dashboard_fm.pack_propagate(False)
    admin_dashboard_fm.configure(width=780,height=580)

def admin_login_page():
    def show_hide_passwd():
        if passwd_ent['show']=='*':
            passwd_ent.config(show='')
            show_hide_btn.config(image=unlock_icon)
        else:
            passwd_ent.config(show='*')
            show_hide_btn.config(image=lock_icon)

    def backtowelcomepage():
        admin_login_fm.destroy()
        root.update()
        welcomepage()

    def admin_login():
        username = admin_user_name_ent.get()
        password = passwd_ent.get()

        if username == 'admin' and password == 'admin':
            message_box(message='Logged in successfully!')
            admin_login_fm.destroy()
            root.update()
            admin_dashboard()
        else:
            tk.messagebox.showerror('Login', 'Incorrect username or password')

    admin_login_fm=tk.Frame(root,highlightbackground=bg_color,
    highlightthickness=3)
    admin_login_fm.pack(pady=30)
    admin_login_fm.pack_propagate(False)
    admin_login_fm.configure(width=780,height=470)

    heading_lb=tk.Label(admin_login_fm,text='Welcome To Admin Login', 
                            fg='white',font=('Bold',18), bg=bg_color)
    heading_lb.place(x=0,y=0,width=780)

    backbmt=tk.Button(admin_login_fm,text='↩',font=('bold',22),fg=bg_color,
                      command=backtowelcomepage)
    backbmt.place(x=5,y=40)

    admin_login_img = tk.Button(admin_login_fm, image=login_admin_icon, bd=0)
    admin_login_img.place(x=360, y=40)
    #entry data
    admin_user_name_lb=tk.Label(admin_login_fm,text='Enter Admin Username',font=('Bold',15),)
    admin_user_name_lb.place(x=290,y=140)

    admin_user_name_ent=tk.Entry(admin_login_fm,font=('Bold',15),justify=tk.CENTER,highlightcolor=bg_color,
                        highlightbackground='grey',highlightthickness=2)
    admin_user_name_ent.place(x=290,y=190)

    passwd_lb=tk.Label(admin_login_fm,text="Password",font=('Bold',15))
    passwd_lb.place(x=290,y=240)
    passwd_ent=tk.Entry(admin_login_fm,font=('Bold',15),justify=tk.CENTER,highlightcolor=bg_color,
                        highlightbackground='grey',
                        highlightthickness=2,
                        show='*')
    passwd_ent.place(x=290,y=290)

    show_hide_btn=tk.Button(admin_login_fm,image=lock_icon,bd=0,
                            command=show_hide_passwd)
    show_hide_btn.place(x=540,y=280)

    login_bnt=tk.Button(admin_login_fm,text='Login',
                        font=('Bold',15),command=admin_login)
    login_bnt.place(x=300,y=340,width=200,height=40)

    # forget_Passwd_btn=tk.Button(admin_login_fm,text='⚠\nForget Password',fg=bg_color,
    #                             font=('Bold', 15), bd=0)
    # forget_Passwd_btn.place(x=110,y=390)



s_gender=tk.StringVar()
list=['FYMCA','SYMCA']
list_sem=['Sem I','Sem II','Sem III','Sem IV']
list_batch=['2020-2022','2021-2023','2022-2024','2023-2025']
list_records=['name','age','gender','year','sem','batch']
def add_account_page():
    def show_hide_passwd():
        if acc_passwd_ent['show']=='*':
            acc_passwd_ent.config(show='')
            show_hide_btn.config(image=unlock_icon)
        else:
            acc_passwd_ent.config(show='*')
            show_hide_btn.config(image=lock_icon)
    pic_path = tk.StringVar()
    pic_path.set('')

    def open_pic(): 
        path=askopenfilename()
        if path:
            img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
            pic_path.set(path)

            picbnt.config(image=img)
            picbnt.image = img

    def backtowelcomepage():
        ans=confirmationbox(msg="Do you want to Leave \nRegistration Form ?")
        if ans:
            add_account_fm.destroy()
            root.update()
            welcomepage()

    def check_invalid_email(email):
    
            pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
    
            match = re.match(pattern=pattern, string=email)
    
            return match
    def generate_id_number():
        generate_id=''
        for r in range(6):
            generate_id+=str(random.randint(0,9))


        if not check_id_already_exists(id_number=generate_id):
            
            #print('id no:',generate_id)
                       
            s_id_ent.config(state=tk.NORMAL)
            s_id_ent.delete(0,tk.END)
            s_id_ent.insert(tk.END,generate_id)
            s_id_ent.config(state='readonly')
        
        else:
            generate_id_number()
    
    # print(check_invalid_email('example@gmail.com'))
    # print(check_invalid_email('example@$$***gmail.com'))

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color,
                             highlightbackground='gray')

    def check_input_validation():
        if s_name_ent.get() == '':
            s_name_ent.config(highlightcolor="red",
                            highlightbackground='red')
            s_name_ent.focus()
            message_box('Student Full Name is Required')
        elif s_age_ent.get() == '':
            s_age_ent.config(highlightcolor="red",
                            highlightbackground='red')
            s_age_ent.focus()
            message_box('Student Age is Required')
        elif s_gmail_ent.get() == '':
            s_gmail_ent.config(highlightcolor="red",
                            highlightbackground='red')
            s_gmail_ent.focus()
            message_box('Gmail is Required')
        elif not check_invalid_email(email=s_gmail_ent.get().lower()):
            s_gmail_ent.config(highlightcolor="red",
                               highlightbackground='red')
            s_gmail_ent.focus()
            message_box("Enter a valid Gmail ID")

        elif acc_passwd_ent.get() == '':
            acc_passwd_ent.config(highlightcolor="red",
                                highlightbackground='red')
            acc_passwd_ent.focus()
            message_box('Password is Required')
        else:
            
            pic_data = b''

            if pic_path.get() != '':
                resize_pic = Image.open(pic_path.get()).resize((100,100))
                resize_pic.save('temp_pic.png')
                
                read_data = open('temp_pic.png', 'rb')
                pic_data = read_data.read()
                read_data.close()
            else:
                read_data = open('Images/add_image.png', 'rb')
                pic_data = read_data.read()
                read_data.close()


            add_data(id_number=s_id_ent.get(),
                      password=acc_passwd_ent.get(),
                      name=s_name_ent.get(),
                      age=s_age_ent.get(),
                      gender=s_gender.get(), 
                      phone_number=s_c_ent.get(),
                      year=bnt3.get(),
                      semester=bnt4.get(),
                      batch=bnt5.get(),
                      email=s_gmail_ent.get(),
                      pic_data=pic_data)
           

            data=f"""
{s_id_ent.get()}
{s_name_ent.get()}
{s_gender.get()}
{s_age_ent.get()}
{s_c_ent.get()}
{bnt3.get()}
{bnt4.get()}
{bnt5.get()}
{s_gmail_ent.get()}
"""

            get_s_card=draw_student_card(s_pic_path=pic_path.get(),
                              s_data=data)
            student_card_page(s_card_obj=get_s_card)    

            add_account_fm.destroy()
            root.update()

            message_box('Account is created Successfuly')        


    add_account_fm=tk.Frame(root,highlightbackground=bg_color,
        highlightthickness=3)

    add_picsection=tk.Frame(add_account_fm,highlightbackground=bg_color,
        highlightthickness=2)
    picbnt=tk.Button(add_picsection,image=pic_icon,bd=0,
                     command=lambda :open_pic())
    picbnt.pack()
    add_picsection.place(x=5,y=5,width=105,height=105)
     
    add_account_fm.pack(pady=30)
    add_account_fm.pack_propagate(False)
    add_account_fm.configure(width=780,height=590)
    #name
    s_name_lb=tk.Label(add_account_fm,text='Enter Student Full Name:',
                    font=('bold',12))
    s_name_lb.place(x=5,y=130)
    s_name_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            highlightthickness=2,font=('bold',15))
    s_name_ent.place(x=5,y=160,width=180)
    s_name_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=s_name_ent))

    #gender
    s_g_lb=tk.Label(add_account_fm,text='Select Gender:',
                    font=('bold',12))
    s_g_lb.place(x=5,y=210)
    bnt1=tk.Radiobutton(add_account_fm,text='Male',font=('bold',12),
                        variable=s_gender,value='male')
    bnt1.place(x=5,y=235)
    bnt2=tk.Radiobutton(add_account_fm,text='Female',font=('bold',12),
                        variable=s_gender,value='female')
    bnt2.place(x=75,y=235)
    s_gender.set('male')

    s_age_lb=tk.Label(add_account_fm,text='Enter Age:',
                    font=('bold',12))
    s_age_lb.place(x=5,y=275)
    s_age_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            highlightthickness=2,font=('bold',15))
    s_age_ent.place(x=5,y=305,width=180)
    s_age_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=s_age_ent))

    s_c_lb=tk.Label(add_account_fm,text='Enter Contact Number:',
                    font=('bold',12))
    s_c_lb.place(x=5,y=350)
    s_c_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            highlightthickness=2,font=('Bold',15))
    s_c_ent.place(x=5,y=380,width=180)
    
    s_year_lb=tk.Label(add_account_fm,text='Select Year:',
                    font=('bold',12))
    s_year_lb.place(x=5,y=420)
    bnt3=Combobox(add_account_fm,font=('bold',10),
                    state='readonly',value=list)
    bnt3.place(x=5, y=445, width=75)

    s_sem_lb=tk.Label(add_account_fm,text='Select Semester:',
                    font=('bold',12))
    s_sem_lb.place(x=100,y=420)
    bnt4=Combobox(add_account_fm,font=('bold',10),
                    state='readonly',value=list_sem)
    bnt4.place(x=100, y=445, width=65)

    s_batch_lb=tk.Label(add_account_fm,text='Select Batch:',
                    font=('bold',12))
    s_batch_lb.place(x=5,y=470)
    bnt5=Combobox(add_account_fm,font=('bold',10),
                    state='readonly',value=list_batch)
    bnt5.place(x=5, y=490, width=100)

    #Generate Student ID number
    s_id_lb=tk.Label(add_account_fm,text='Student ID Number:',
                    font=('Bold',12))
    s_id_lb.place(x=360,y=35)
    s_id_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            bd=1,font=('bold',15))
    s_id_ent.place(x=520,y=35,width=80)
    
    s_id_ent.config(state='readonly')
    generate_id_number()

    id_info_lb= tk.Label(add_account_fm, text="""Automatically Generated ID Number
! Remember Using This ID Number
Student will Login Account.""", justify=tk.LEFT)
    id_info_lb.place(x=360, y=65)

    s_gmail_lb=tk.Label(add_account_fm,text='Enter Your Gmail:',
                    font=('bold',12))
    s_gmail_lb.place(x=360,y=130)
    s_gmail_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            highlightthickness=2,font=('bold',15))
    s_gmail_ent.place(x=360,y=160,width=180)
    s_gmail_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=s_gmail_ent))
    email_info_lb= tk.Label(add_account_fm, text="""Via Email Address Student
Can Recover Account
! In case Forgetting Password.""", justify=tk.LEFT)
    email_info_lb.place(x=360, y=195)
    #Create Password
    passwd_lb=tk.Label(add_account_fm,text='Create Password ',
                    font=('bold',12))
    passwd_lb.place(x=360,y=260)
    acc_passwd_ent=tk.Entry(add_account_fm,highlightbackground='grey',highlightcolor=bg_color,
                            highlightthickness=2,font=('bold',15))
    acc_passwd_ent.place(x=360,y=290,width=180)
    acc_passwd_ent.bind('<KeyRelease>',
                    lambda e: remove_highlight_warning(entry=acc_passwd_ent))
    show_hide_btn=tk.Button(add_account_fm,image=lock_icon,bd=0,
                            command=show_hide_passwd)
    show_hide_btn.place(x=550,y=280)

    id_info_lb= tk.Label(add_account_fm, text="""Via Student Created Password
And Provided Student ID Number
Student Can Login Account""", justify=tk.LEFT)
    id_info_lb.place(x=360, y=330)

    homebtn=tk.Button(add_account_fm,text='Home',font=('bold',12),
                    bg=bg_color,fg='white',bd=0,
                    command=backtowelcomepage)
    homebtn.place(x=360,y=400)

    subbtn=tk.Button(add_account_fm,text='Submit',font=('bold',12),
                    bg=bg_color,fg='white',bd=0,command=check_input_validation)
    subbtn.place(x=420,y=400)
init_database()
welcomepage()
# admin_dashboard()
#student_dashboard(student_id='690608')
#forget_passwd_page()
root.mainloop()