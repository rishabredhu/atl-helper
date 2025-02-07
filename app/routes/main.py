# app/routes/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.factory import DatabaseFactory  # for database access

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Render the home page (which includes an image and introductory text)
    return render_template('home.html')

@main_bp.route('/tours')
def tours():
    # Render the tours page
    return render_template('tours.html')

@main_bp.route('/tourgroup/<int:tour_group_id>/customers')
def tourgroup_customers(tour_group_id):
    db = DatabaseFactory.get_database()
    cursor = db.cursor(dictionary=True)
    # Get tour group info (tour name, start date)
    cursor.execute("""
        SELECT tg.start_date, t.name AS tour_name
        FROM tour_groups tg 
        JOIN tours t ON tg.tour_id = t.id
        WHERE tg.id = %s
    """, (tour_group_id,))
    tour_group = cursor.fetchone()
    if not tour_group:
        flash("Tour group not found.")
        return redirect(url_for('main.tours'))
    
    # Get customers in the tour group.
    # The ordering: family_name A–Z and for matching family names, order by date_of_birth descending (youngest first)
    cursor.execute("""
        SELECT c.*
        FROM customers c 
        JOIN bookings b ON c.id = b.customer_id 
        WHERE b.tour_group_id = %s
        ORDER BY c.family_name ASC, c.date_of_birth DESC
    """, (tour_group_id,))
    customers = cursor.fetchall()
    
    return render_template('tourlist.html', tour_group=tour_group, customers=customers)




@main_bp.route('/booking/add', methods=['GET', 'POST'])
def booking_add():
    if request.method == 'POST':
        # Retrieve form data
        customer_id = request.form.get('customer_id')
        tour_group_id = request.form.get('tour_group_id')
        # Optionally retrieve other details (booking_date etc.)
        
        # For age restrictions, you would need to:
        # 1. Retrieve the customer’s date of birth
        # 2. Retrieve the tour's age restriction (if any)
        # 3. Calculate the age and enforce restrictions.
        #
        # Example (pseudocode):
        # if tour_requires_adult and customer_age < 18:
        #     flash("This tour is adults-only.")
        #     return render_template('booking_add.html', error="Age restriction")
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO bookings (customer_id, tour_group_id, booking_date) VALUES (%s, %s, CURDATE())",
                (customer_id, tour_group_id)
            )
            db.commit()
            flash("Booking added successfully!")
            return redirect(url_for('main.home'))
        except Exception as e:
            db.rollback()
            flash("Error adding booking.")
    return render_template('booking_add.html')



