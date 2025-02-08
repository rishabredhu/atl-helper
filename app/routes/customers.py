# app/routes/customers.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.factory import get_db
from datetime import datetime
import re

customers_bp = Blueprint('customers', __name__)

def validate_email(email):
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    if not phone:
        return True
    pattern = r'^\+?[0-9]{10,12}$'
    return re.match(pattern, phone) is not None

@customers_bp.route('/customers/search', methods=['GET'])
def customer_search():
    """
    Requirement 5: Customer search functionality
    - Shows family name, first name, and contact details
    - Results are clickable for booking overview
    """
    query = request.args.get('q', '')
    results = []
    if query:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        sql = """
            SELECT customerid, firstname, familyname, email, phone 
            FROM customers 
            WHERE familyname LIKE %s OR firstname LIKE %s
            ORDER BY familyname ASC, firstname ASC
        """
        like_query = f"%{query}%"
        try:
            cursor.execute(sql, (like_query, like_query))
            results = cursor.fetchall()
        except Exception as e:
            flash(f"Search error: {str(e)}", 'error')
        finally:
            cursor.close()
    return render_template('customers.html', results=results, query=query)

@customers_bp.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    """
    Requirement 6: Add customer functionality with validation
    """
    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        familyname = request.form.get('familyname', '').strip()
        dob = request.form.get('dob')
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        errors = []
        if not firstname or not familyname:
            errors.append("First name and family name are required")
        if not dob:
            errors.append("Date of birth is required")
        if not email and not phone:
            errors.append("Either email or phone is required")
        if email and not validate_email(email):
            errors.append("Please enter a valid email address")
        if phone and not validate_phone(phone):
            errors.append("Please enter a valid phone number")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('customers_add.html', 
                                firstname=firstname,
                                familyname=familyname,
                                dob=dob,
                                email=email,
                                phone=phone)
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                """INSERT INTO customers 
                   (firstname, familyname, dob, email, phone) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (firstname, familyname, dob, email, phone)
            )
            db.commit()
            new_id = cursor.lastrowid
            flash("Customer added successfully!")
            return redirect(url_for('customers.customer_booking_overview', customer_id=new_id))
        except Exception as e:
            db.rollback()
            flash(f"Error adding customer: {str(e)}", 'error')
        finally:
            cursor.close()
            
    return render_template('customers_add.html')

@customers_bp.route('/tourgroup/<int:tourgroup_id>/customers')
def tourgroup_customers(tourgroup_id):
    """
    Requirement 3: Display customers in a tour group
    - Shows tour name and start date
    - Lists customers alphabetically by family name
    - Sub-sorted by DOB (youngest first)
    - Clickable customer names
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Get tour group details
        cursor.execute("""
            SELECT tg.tourgroupid, tg.startdate, t.tourname
            FROM tourgroups tg 
            JOIN tours t ON tg.tourid = t.tourid
            WHERE tg.tourgroupid = %s
        """, (tourgroup_id,))
        tourgroup = cursor.fetchone()
        
        if not tourgroup:
            flash("Tour group not found")
            return redirect(url_for('main.tours'))
        
        # Get customers in the tour group
        cursor.execute("""
            SELECT c.customerid, c.firstname, c.familyname, c.dob
            FROM customers c
            JOIN tourbookings tb ON c.customerid = tb.customerid
            WHERE tb.tourgroupid = %s
            ORDER BY c.familyname ASC, c.dob DESC
        """, (tourgroup_id,))
        customers = cursor.fetchall()
        
        return render_template('tourlist.html', 
                             tourgroup=tourgroup,
                             customers=customers)
    except Exception as e:
        flash(f"Error retrieving tour group details: {str(e)}", 'error')
        return redirect(url_for('main.tours'))
    finally:
        cursor.close()

@customers_bp.route('/customers/<int:customer_id>')
def customer_booking_overview(customer_id):
    """
    Requirement 8: Customer booking overview
    - Shows customer name and total destinations
    - Lists all bookings with tour details
    - Categorizes bookings as past/current/future
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Get customer details
        cursor.execute("""
            SELECT customerid, firstname, familyname, dob, email, phone 
            FROM customers 
            WHERE customerid = %s
        """, (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            flash("Customer not found")
            return redirect(url_for('main.home'))
        
        # Get all bookings with destination counts
        cursor.execute("""
            SELECT 
                tb.bookingid,
                tg.startdate,
                t.tourname,
                (SELECT COUNT(*) FROM itineraries i WHERE i.tourid = t.tourid) as destination_count
            FROM tourbookings tb
            JOIN tourgroups tg ON tb.tourgroupid = tg.tourgroupid
            JOIN tours t ON tg.tourid = t.tourid
            WHERE tb.customerid = %s
            ORDER BY tg.startdate DESC
        """, (customer_id,))
        bookings = cursor.fetchall()
        
        # Process bookings
        total_destinations = 0
        current_date = datetime.now().date()
        
        for booking in bookings:
            total_destinations += booking['destination_count']
            booking['formatted_date'] = booking['startdate'].strftime('%d %B %Y')
            if booking['startdate'] < current_date:
                booking['status'] = 'past'
            elif booking['startdate'] == current_date:
                booking['status'] = 'current'
            else:
                booking['status'] = 'future'
        
        return render_template('customer_overview.html',
                             customer=customer,
                             bookings=bookings,
                             total_destinations=total_destinations)
    except Exception as e:
        flash(f"Error retrieving customer details: {str(e)}", 'error')
        return redirect(url_for('main.home'))
    finally:
        cursor.close()

@customers_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def customer_edit(customer_id):
    """
    Requirement 7: Edit customer information
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'GET':
        try:
            cursor.execute(
                "SELECT * FROM customers WHERE customerid = %s",
                (customer_id,)
            )
            customer = cursor.fetchone()
            
            if not customer:
                flash("Customer not found")
                return redirect(url_for('main.home'))
                
            return render_template('customer_edit.html', customer=customer)
        except Exception as e:
            flash(f"Error retrieving customer details: {str(e)}", 'error')
            return redirect(url_for('main.home'))
        finally:
            cursor.close()
    
    elif request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        familyname = request.form.get('familyname', '').strip()
        dob = request.form.get('dob')
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        errors = []
        if not firstname or not familyname:
            errors.append("First name and family name are required")
        if not dob:
            errors.append("Date of birth is required")
        if not email and not phone:
            errors.append("Either email or phone is required")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('customers.customer_edit', customer_id=customer_id))
        
        try:
            cursor.execute("""
                UPDATE customers 
                SET firstname = %s, 
                    familyname = %s, 
                    dob = %s, 
                    email = %s, 
                    phone = %s
                WHERE customerid = %s
                """, (firstname, familyname, dob, email, phone, customer_id))
            db.commit()
            flash("Customer updated successfully!")
            return redirect(url_for('customers.customer_booking_overview', customer_id=customer_id))
        except Exception as e:
            db.rollback()
            flash(f"Error updating customer: {str(e)}", 'error')
            return redirect(url_for('customers.customer_edit', customer_id=customer_id))
        finally:
            cursor.close()