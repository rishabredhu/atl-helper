from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import traceback
import logging
from datetime import datetime
from functools import wraps
from db.factory import DatabaseFactory


main_bp = Blueprint('main', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def handle_db_error(f):
    """Decorator for database error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the full traceback
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('main.home'))
    return decorated_function

@main_bp.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return "Error loading home page", 500

@main_bp.route('/tours')
@handle_db_error
def tours():
    db = None
    cursor = None
    try:
        db = DatabaseFactory.get_db()
        cursor = db.cursor(dictionary=True)
        
        logger.debug("Executing tours query")
        cursor.execute("""
            SELECT t.tourid as id, 
                   t.tourname as name, 
                   t.agerestriction,
                   COUNT(DISTINCT tg.tourgroupid) as group_count
            FROM tours t
            LEFT JOIN tourgroups tg ON t.tourid = tg.tourid
            GROUP BY t.tourid, t.tourname, t.agerestriction
        """)
        tours = cursor.fetchall()
        
        if not tours:
            logger.info("No tours found in database")
            flash("No tours currently available", "info")
            return render_template('tours.html', tours=[])

        # Add default values for missing template fields
        for tour in tours:
            tour['description'] = f"Explore {tour['name']} with us!"
            
            tour['duration'] = 14
            tour['location'] = tour['name']
            # tour['image'] = 'placeholder-tour.jpg'
        
        logger.debug(f"Successfully retrieved {len(tours)} tours")
        return render_template('tours.html', tours=tours)

    except Exception as e:
        logger.error(f"Error in tours route: {str(e)}")
        logger.error(traceback.format_exc())
        flash("Error retrieving tours. Please try again later.", "error")
        return redirect(url_for('main.home'))
    finally:
        if cursor:
            cursor.close()

@main_bp.route('/tours/<int:tour_id>')
@handle_db_error
def tour_details(tour_id):
    db = None
    cursor = None
    try:
        logger.debug(f"Fetching details for tour_id: {tour_id}")
        db = DatabaseFactory.get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get tour details
        cursor.execute("""
            SELECT t.tourid as id, 
                   t.tourname as name, 
                   t.agerestriction,
                   GROUP_CONCAT(DISTINCT tg.startdate) as available_dates
            FROM tours t
            LEFT JOIN tourgroups tg ON t.tourid = tg.tourid
            WHERE t.tourid = %s
            GROUP BY t.tourid, t.tourname, t.agerestriction
        """, (tour_id,))
        tour = cursor.fetchone()
        
        if not tour:
            logger.warning(f"Tour not found with ID: {tour_id}")
            flash("Tour not found", "error")
            return redirect(url_for('main.tours'))

        # Get tour groups and their customers
        cursor.execute("""
            SELECT 
                tg.tourgroupid,
                tg.startdate,
                c.customerid,
                c.firstname,
                c.familyname
            FROM tourgroups tg
            LEFT JOIN tourbookings tb ON tg.tourgroupid = tb.tourgroupid
            LEFT JOIN customers c ON tb.customerid = c.customerid
            WHERE tg.tourid = %s
            ORDER BY tg.startdate, c.familyname, c.firstname
        """, (tour_id,))
        results = cursor.fetchall()
        
        # Process tour groups
        tour_groups = process_tour_groups(results)
        
        logger.debug(f"Successfully retrieved details for tour_id: {tour_id}")
        return render_template('tour_details.html', 
                             tour=tour,
                             tour_groups=tour_groups)

    except Exception as e:
        logger.error(f"Error in tour_details route for tour_id {tour_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash("Error retrieving tour details. Please try again later.", "error")
        return redirect(url_for('main.tours'))
    finally:
        if cursor:
            cursor.close()

def process_tour_groups(results):
    """Helper function to process tour groups data"""
    try:
        tour_groups = {}
        for row in results:
            group_id = row['tourgroupid']
            if group_id not in tour_groups:
                tour_groups[group_id] = {
                    'startdate': row['startdate'],
                    'customers': []
                }
            if row['customerid']:
                tour_groups[group_id]['customers'].append({
                    'customerid': row['customerid'],
                    'firstname': row['firstname'],
                    'familyname': row['familyname']
                })
        
        # Convert to list and sort
        tour_groups = [{'startdate': data['startdate'], 'customers': data['customers']} 
                      for data in tour_groups.values()]
        tour_groups.sort(key=lambda x: x['startdate'])
        return tour_groups
    except Exception as e:
        logger.error(f"Error processing tour groups: {str(e)}")
        raise

@main_bp.route('/booking/add', methods=['GET', 'POST'])
@handle_db_error
def booking_add():
    if request.method == 'GET':
        # Get list of customers and future tour groups for the form
        db = DatabaseFactory.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            # Get customers
            cursor.execute("SELECT customerid, firstname, familyname FROM customers ORDER BY familyname, firstname")
            customers = cursor.fetchall()
            
            # Get future tour groups
            cursor.execute("""
                SELECT tg.tourgroupid, tg.startdate, t.tourname, t.agerestriction
                FROM tourgroups tg
                JOIN tours t ON tg.tourid = t.tourid
                WHERE tg.startdate > CURDATE()
                ORDER BY tg.startdate
            """)
            tour_groups = cursor.fetchall()
            
            return render_template('booking_add.html', 
                                customers=customers,
                                tour_groups=tour_groups)
        finally:
            cursor.close()

    elif request.method == 'POST':
        customer_id = request.form.get('customer_id')
        tour_group_id = request.form.get('tour_group_id')
        
        if not customer_id or not tour_group_id:
            flash("Please select both customer and tour group")
            return redirect(url_for('main.booking_add'))
        
        db = DatabaseFactory.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            # Check age restriction
            cursor.execute("""
                SELECT t.agerestriction, c.dob 
                FROM tourgroups tg
                JOIN tours t ON tg.tourid = t.tourid
                JOIN customers c ON c.customerid = %s
                WHERE tg.tourgroupid = %s
            """, (customer_id, tour_group_id))
            result = cursor.fetchone()
            
            # Calculate age and validate
            today = datetime.now()
            age = today.year - result['dob'].year - ((today.month, today.day) < (result['dob'].month, result['dob'].day))
            
            if age < result['agerestriction']:
                flash("Customer does not meet the age requirement for this tour")
                return redirect(url_for('main.booking_add'))
            
            # Add the booking
            cursor.execute(
                "INSERT INTO tourbookings (customerid, tourgroupid) VALUES (%s, %s)",
                (customer_id, tour_group_id)
            )
            db.commit()
            flash("Booking added successfully")
            return redirect(url_for('main.tours'))
            
        except Exception as e:
            db.rollback()
            flash(f"Error adding booking: {str(e)}")
            return redirect(url_for('main.booking_add'))
        finally:
            cursor.close()
def validate_age_restriction(dob, age_restriction):
    """Helper function to validate age restrictions"""
    if not age_restriction:
        return True
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= age_restriction