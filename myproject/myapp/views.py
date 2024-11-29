from django.shortcuts import render, redirect
import mysql.connector as sql
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from datetime import date

@csrf_protect
def registration(request):
    if request.method == "POST":
        us = request.POST.get('username')
        em = request.POST.get('email')
        ps = request.POST.get('password')
        cpass = request.POST.get('cpassword')

        errors = {}

        # Check if password and confirmation match
        if ps != cpass:
            errors['cpassword_error'] = "Passwords do not match!"

        # Password validation checks
        if len(ps) < 6:
            errors['password_error'] = "Password must be at least 6 characters long."
        elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", ps):
            errors['password_error'] = "Password must include at least one special character."
        elif not (re.search(r"[A-Z]", ps) and re.search(r"[a-z]", ps) and re.search(r"[0-9]", ps)):
            errors['password_error'] = "Password must include uppercase, lowercase, and numbers."

        # If there are errors, re-render the form with error messages
        if errors:
            return render(request, 'registration.html', {'errors': errors})

        try:
            # Establishing the connection
            conn = sql.connect(
                host="localhost",
                user="root",
                password="*21ht1A4342*",
                database="smarthealth"
            )
            cursor = conn.cursor()

            # Parameterized query to avoid SQL injection
            comm = "INSERT INTO registration (username, email, password, cpassword) VALUES (%s, %s, %s, %s)"
            cursor.execute(comm, (us, em, ps, cpass))
            conn.commit()

            messages.success(request, "Registration successful!")
            return redirect('login')  # Redirect to the login page

        except sql.Error as e:
            messages.error(request, f"Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render(request, 'registration.html')


def home(request):
    return render(request, 'home.html')


@csrf_protect
def login(request):
    error_message = ""

    if request.method == "POST":
        # Connect to the database
        try:
            conn = sql.connect(host="localhost", user="root", password="*21ht1A4342*", database="smarthealth")
            cursor = conn.cursor()

            # Get the data from the form
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Retrieve the user data from the database
            query = "SELECT password FROM registration WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                # If a record is found, check if the password matches
                db_password = result[0]

                if db_password == password:
                    # Redirect to home page on successful login
                    return redirect('home')  
                else:
                    error_message = "Invalid password."
            else:
                error_message = "Username not found."

        except sql.Error as e:
            error_message = "Database error. Please try again later."

        finally:
            cursor.close()
            conn.close()

    return render(request, 'login.html', {"error_message": error_message})


from django.http import HttpResponseForbidden

def csrf_failure(request, reason=""):
    return HttpResponseForbidden("Custom CSRF failure message.")


def healthinsights(request):
    # Example dynamic data for health insights (this could come from a database or API)
    data = {
        "recovered": 20,
        "admitted": 50,
        "deceased": 5,
        "ventilator": 6,
        "doctorsavailable": 7,
        "bedsavailability": 7
    }
    return render(request, 'healthinsights.html', data)


def wellnesstracking(request):
    conn = sql.connect(
        host="localhost",
        user="root",
        password="*21ht1A4342*",
        database="smarthealth"
    )
    cursor = conn.cursor()

    # Handle form submission to save wellness data
    if request.method == "POST":
        steps = request.POST.get('steps')
        heart_rate = request.POST.get('heart_rate')
        sleep_hours = request.POST.get('sleep_hours')

        try:
            query = "INSERT INTO wellness_data (steps, heart_rate, sleep_hours, date) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (steps, heart_rate, sleep_hours, date.today()))
            conn.commit()
            messages.success(request, "Wellness data saved successfully!")
        except sql.Error as e:
            messages.error(request, f"Error saving wellness data: {e}")

    # Fetch previous wellness data
    try:
        cursor.execute("SELECT date, steps, heart_rate, sleep_hours FROM wellness_data ORDER BY date DESC")
        wellness_data = cursor.fetchall()
    except sql.Error as e:
        messages.error(request, f"Error fetching wellness data: {e}")
        wellness_data = []
    finally:
        cursor.close()
        conn.close()

    return render(request, 'wellnesstracking.html', {'wellness_data': wellness_data})
