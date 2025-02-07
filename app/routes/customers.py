
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.factory import get_db

main_bp= Blueprint('main', __name__)
@main_bp.route('/customers/search', methods=['GET'])
def customer_search():
    query = request.args.get('q', '')
    results = []
    if query:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        # Use wildcard matching on family name or first name
        sql = "SELECT * FROM customers WHERE family_name LIKE %s OR first_name LIKE %s"
        like_query = f"%{query}%"
        cursor.execute(sql, (like_query, like_query))
        results = cursor.fetchall()
    return render_template('customers.html', results=results, query=query)

@main_bp.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        date_of_birth = request.form.get('date_of_birth')
        contact_details = request.form.get('contact_details')
        
        # Validate data here and flash errors if needed
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers (first_name, family_name, date_of_birth, contact_details) VALUES (%s, %s, %s, %s)",
                (first_name, family_name, date_of_birth, contact_details)
            )
            db.commit()
            flash("Customer added successfully!")
            # Redirect to customer booking overview (using the new customer's ID)
            new_id = cursor.lastrowid
            return redirect(url_for('main.customer_booking_overview', customer_id=new_id))
        except Exception as e:
            db.rollback()
            flash("Error adding customer.")
    return render_template('customer_add.html')


@main_bp.route('/customers/<int:customer_id>')
def customer_booking_overview(customer_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get customer details
    cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        flash("Customer not found.")
        return redirect(url_for('main.home'))
    
    # Get all bookings for the customer (including past, current, future)
    cursor.execute("""
        SELECT b.*, tg.start_date, t.name AS tour_name, t.itinerary
        FROM bookings b 
        JOIN tour_groups tg ON b.tour_group_id = tg.id 
        JOIN tours t ON tg.tour_id = t.id 
        WHERE b.customer_id = %s
        ORDER BY tg.start_date DESC
    """, (customer_id,))
    bookings = cursor.fetchall()
    
    total_destinations = 0
    for booking in bookings:
        # Assuming itinerary is stored as a comma-separated string.
        destinations = [d.strip() for d in booking['itinerary'].split(',') if d.strip()]
        booking['destination_count'] = len(destinations)
        total_destinations += len(destinations)
    
    return render_template('tour_details.html',
                           customer=customer,
                           bookings=bookings,
                           total_destinations=total_destinations)
