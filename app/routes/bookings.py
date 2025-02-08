# app/routes/bookings.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.factory import get_db
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/booking/add', methods=['GET', 'POST'])
def booking_add():
    """Add a new booking with age restriction check"""
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get available tours and customers for dropdowns
        cursor.execute("SELECT tourid, tourname, agerestriction FROM tours")
        tours = cursor.fetchall()
        
        cursor.execute("SELECT customerid, firstname, familyname FROM customers")
        customers = cursor.fetchall()
        
        cursor.close()
        return render_template('booking_add.html', tours=tours, customers=customers)
    
    elif request.method == 'POST':
        customer_id = request.form.get('customer_id')
        tour_id = request.form.get('tour_id')
        start_date = request.form.get('start_date')
        
        if not all([customer_id, tour_id, start_date]):
            flash("All fields are required")
            return redirect(url_for('bookings.booking_add'))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            # Check age restriction
            cursor.execute("""
                SELECT c.dob, t.agerestriction, t.tourname
                FROM customers c, tours t
                WHERE c.customerid = %s AND t.tourid = %s
            """, (customer_id, tour_id))
            result = cursor.fetchone()
            
            if result:
                customer_age = (datetime.now().date() - result['dob']).days // 365
                if customer_age < result['agerestriction']:
                    flash(f"Customer does not meet the age requirement ({result['agerestriction']} years) for tour {result['tourname']}")
                    return redirect(url_for('bookings.booking_add'))
            
            # Create tour group or get existing one
            cursor.execute("""
                SELECT tourgroupid FROM tourgroups 
                WHERE tourid = %s AND startdate = %s
            """, (tour_id, start_date))
            tourgroup = cursor.fetchone()
            
            if tourgroup:
                tourgroup_id = tourgroup['tourgroupid']
            else:
                cursor.execute("""
                    INSERT INTO tourgroups (tourid, startdate) 
                    VALUES (%s, %s)
                """, (tour_id, start_date))
                tourgroup_id = cursor.lastrowid
            
            # Add booking
            cursor.execute("""
                INSERT INTO tourbookings (customerid, tourgroupid) 
                VALUES (%s, %s)
            """, (customer_id, tourgroup_id))
            
            db.commit()
            flash("Booking added successfully!")
            return redirect(url_for('customers.customer_booking_overview', customer_id=customer_id))
            
        except Exception as e:
            db.rollback()
            flash(f"Error adding booking: {str(e)}")
            return redirect(url_for('bookings.booking_add'))
        finally:
            cursor.close()