import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
from flask_login import LoginManager, login_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from sqlalchemy import or_, and_

from extensions import db
from forms import LoginForm, RegisterForm, AddVisitorForm
from models import User, Visitor, Visits, RoomType, EmailCampaign, CampaignRecipient, CampaignStatus

load_dotenv("./flask.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if a user with the given email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            return redirect(url_for("register"))  # Redirect back to the registration page

        # Proceed with user creation
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = AddVisitorForm()
    visitors = Visitor.query.all()
    if form.validate_on_submit():
        hashed_pesel = generate_password_hash(form.pesel.data)
        
        # Create visitor
        new_visitor = Visitor(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            pesel=hashed_pesel,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            total_visits=1
        )

        db.session.add(new_visitor)
        db.session.flush()  # Get the visitor ID

        # Create visit record
        new_visit = Visits(
            visitor_id=new_visitor.id,
            check_in_date=datetime.combine(form.check_in_date.data, datetime.min.time()),
            check_out_date=datetime.combine(form.check_out_date.data, datetime.min.time()) if form.check_out_date.data else None,
            hotel_id=form.hotel_id.data,
            room_type=RoomType(form.room_type.data)
        )

        db.session.add(new_visit)
        db.session.flush()  # Get the visit ID

        # Update visitor's last visit reference
        new_visitor.last_visit_id = new_visit.id
        new_visitor.last_date_of_visit = new_visit.check_in_date

        db.session.commit()
    return render_template("dashboard.html", form=form, visitors=visitors)


@app.route('/add_visitor_ajax', methods=['POST'])
@login_required
def add_visitor_ajax():
    form = AddVisitorForm()

    if form.validate_on_submit():
        try:
            # Create visitor
            new_visitor = Visitor(
                name=form.name.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                pesel=form.pesel.data,
                check_in_date=form.check_in_date.data,
                check_out_date=form.check_out_date.data,
                total_visits=1
            )

            db.session.add(new_visitor)
            db.session.flush()  # Get the visitor ID

            # Create visit record
            new_visit = Visits(
                visitor_id=new_visitor.id,
                check_in_date=datetime.combine(form.check_in_date.data, datetime.min.time()),
                check_out_date=datetime.combine(form.check_out_date.data, datetime.min.time()) if form.check_out_date.data else None,
                hotel_id=form.hotel_id.data,
                room_type=RoomType(form.room_type.data)
            )

            db.session.add(new_visit)
            db.session.flush()  # Get the visit ID

            # Update visitor's last visit reference
            new_visitor.last_visit_id = new_visit.id
            new_visitor.last_date_of_visit = new_visit.check_in_date

            db.session.commit()

            # Return success response with visitor data
            return jsonify({
                'success': True,
                'visitor': {
                    'name': new_visitor.name,
                    'email': new_visitor.email,
                    'phone_number': new_visitor.phone_number,
                    'hotel_id': new_visit.hotel_id,
                    'room_type': new_visit.room_type.value,
                    'check_in_date': new_visitor.check_in_date.strftime(
                        '%Y-%m-%d') if new_visitor.check_in_date else 'N/A',
                    'check_out_date': new_visitor.check_out_date.strftime(
                        '%Y-%m-%d') if new_visitor.check_out_date else 'N/A'
                }
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error adding visitor: {e}")
            return jsonify({
                'success': False,
                'errors': {'general': ['An error occurred while saving the visitor.']}
            }), 500
    else:
        # Return validation errors
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400


@app.route("/visitors", methods=["GET", "POST"])
@login_required
def visitors():
    return render_template("visitors.html")


@app.route("/campaigns")
@login_required
def campaigns():
    user_campaigns = EmailCampaign.query.filter_by(created_by=current_user.id).order_by(
        EmailCampaign.created_at.desc()).all()
    return render_template("campaigns.html", campaigns=user_campaigns)


@app.route('/api/search_visitors', methods=['POST'])
@login_required
def search_visitors():
    try:
        # Get search parameters
        search_term = request.form.get('search_term', '').strip()
        hotel_id = request.form.get('hotel_id', '').strip()
        room_type = request.form.get('room_type', '').strip()
        check_in_from = request.form.get('check_in_from', '').strip()
        check_in_to = request.form.get('check_in_to', '').strip()
        check_out_from = request.form.get('check_out_from', '').strip()
        check_out_to = request.form.get('check_out_to', '').strip()
        min_visits = request.form.get('min_visits', '').strip()
        last_visit_from = request.form.get('last_visit_from', '').strip()
        last_visit_to = request.form.get('last_visit_to', '').strip()
        page = int(request.form.get('page', 1))
        per_page = 10

        # Start with base query
        query = db.session.query(Visitor)

        # Apply search filters
        if search_term:
            # Since PESEL is hashed, we'll exclude it from search for now
            search_filter = or_(
                Visitor.name.ilike(f'%{search_term}%'),
                Visitor.email.ilike(f'%{search_term}%'),
                Visitor.phone_number.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)

        # Date filters for visitor check-in/check-out
        if check_in_from:
            check_in_from_date = datetime.strptime(check_in_from, '%Y-%m-%d').date()
            query = query.filter(Visitor.check_in_date >= check_in_from_date)

        if check_in_to:
            check_in_to_date = datetime.strptime(check_in_to, '%Y-%m-%d').date()
            query = query.filter(Visitor.check_in_date <= check_in_to_date)

        if check_out_from:
            check_out_from_date = datetime.strptime(check_out_from, '%Y-%m-%d').date()
            query = query.filter(Visitor.check_out_date >= check_out_from_date)

        if check_out_to:
            check_out_to_date = datetime.strptime(check_out_to, '%Y-%m-%d').date()
            query = query.filter(Visitor.check_out_date <= check_out_to_date)

        # Visits-specific filters
        if min_visits:
            query = query.filter(Visitor.total_visits >= int(min_visits))

        if last_visit_from:
            last_visit_from_date = datetime.strptime(last_visit_from, '%Y-%m-%d').date()
            query = query.filter(Visitor.last_date_of_visit >= last_visit_from_date)

        if last_visit_to:
            last_visit_to_date = datetime.strptime(last_visit_to, '%Y-%m-%d').date()
            query = query.filter(Visitor.last_date_of_visit <= last_visit_to_date)

        # Join with Visits table for hotel_id and room_type filters
        if hotel_id or room_type:
            query = query.join(Visits, Visitor.last_visit_id == Visits.id, isouter=True)

            if hotel_id:
                query = query.filter(Visits.hotel_id == int(hotel_id))

            if room_type:
                query = query.filter(Visits.room_type == RoomType(room_type))

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        paginated_query = query.offset((page - 1) * per_page).limit(per_page)
        visitors = paginated_query.all()

        # Format results
        visitors_data = []
        for visitor in visitors:
            visitors_data.append({
                'id': visitor.id,
                'name': visitor.name,
                'email': visitor.email,
                'phone_number': visitor.phone_number,
                'pesel': visitor.pesel[:4] + '***' + visitor.pesel[-2:] if visitor.pesel and len(
                    visitor.pesel) > 6 else 'N/A',  # Mask PESEL for privacy
                'check_in_date': visitor.check_in_date.strftime('%Y-%m-%d') if visitor.check_in_date else None,
                'check_out_date': visitor.check_out_date.strftime('%Y-%m-%d') if visitor.check_out_date else None,
                'total_visits': visitor.total_visits or 0,
                'last_date_of_visit': visitor.last_date_of_visit.strftime(
                    '%Y-%m-%d %H:%M') if visitor.last_date_of_visit else None
            })

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'visitors': visitors_data,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'current_page': page
        })

    except Exception as e:
        print(f"Search error: {e}")  # For debugging
        return jsonify({
            'success': False,
            'error': 'An error occurred while searching visitors'
        }), 500


@app.route('/api/visitor/<int:visitor_id>', methods=['GET'])
@login_required
def get_visitor_details(visitor_id):
    try:
        visitor = Visitor.query.get_or_404(visitor_id)

        # Get all visits for this visitor
        visits = []
        visitor_visits = Visits.query.filter_by(visitor_id=visitor.id).order_by(Visits.check_in_date.desc()).all()
        visits = [{
            'id': visit.id,
            'check_in_date': visit.check_in_date.strftime('%Y-%m-%d %H:%M') if visit.check_in_date else None,
            'check_out_date': visit.check_out_date.strftime('%Y-%m-%d %H:%M') if visit.check_out_date else None,
            'hotel_id': visit.hotel_id,
            'room_type': visit.room_type.value if visit.room_type else None
        } for visit in visitor_visits]

        visitor_data = {
            'id': visitor.id,
            'name': visitor.name,
            'email': visitor.email,
            'phone_number': visitor.phone_number,
            'pesel': visitor.pesel,  # Full PESEL for admin view
            'check_in_date': visitor.check_in_date.strftime('%Y-%m-%d') if visitor.check_in_date else None,
            'check_out_date': visitor.check_out_date.strftime('%Y-%m-%d') if visitor.check_out_date else None,
            'total_visits': visitor.total_visits or 0,
            'last_date_of_visit': visitor.last_date_of_visit.strftime(
                '%Y-%m-%d %H:%M') if visitor.last_date_of_visit else None,
            'last_visit_id': visitor.last_visit_id,
            'visits': visits
        }

        return jsonify(visitor_data)

    except Exception as e:
        print(f"Error fetching visitor details: {e}")  # For debugging
        return jsonify({
            'error': 'Visitor not found or error occurred'
        }), 404


@app.route('/api/create_campaign', methods=['POST'])
@login_required
def create_campaign():
    try:
        data = request.get_json()

        campaign_name = data.get('campaign_name', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        visitor_ids = data.get('visitor_ids', [])

        if not campaign_name or not subject or not message:
            return jsonify({
                'success': False,
                'error': 'Campaign name, subject, and message are required'
            }), 400

        if not visitor_ids:
            return jsonify({
                'success': False,
                'error': 'At least one visitor must be selected'
            }), 400

        # Create the campaign
        campaign = EmailCampaign(
            name=campaign_name,
            subject=subject,
            message=message,
            created_by=current_user.id,
            total_recipients=len(visitor_ids)
        )

        db.session.add(campaign)
        db.session.flush()  # Get the campaign ID

        # Add recipients
        successful_recipients = 0
        for visitor_id in visitor_ids:
            visitor = Visitor.query.get(visitor_id)
            if visitor and visitor.email:
                recipient = CampaignRecipient(
                    campaign_id=campaign.id,
                    visitor_id=visitor.id,
                    email=visitor.email
                )
                db.session.add(recipient)
                successful_recipients += 1

        campaign.total_recipients = successful_recipients
        db.session.commit()

        return jsonify({
            'success': True,
            'campaign_id': campaign.id,
            'message': f'Campaign created successfully with {successful_recipients} recipients'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error creating campaign: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while creating the campaign'
        }), 500


@app.route('/api/send_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def send_campaign(campaign_id):
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)

        # Check if user owns this campaign
        if campaign.created_by != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403

        # Check if campaign is already sent
        if campaign.status == CampaignStatus.SENT:
            return jsonify({
                'success': False,
                'error': 'Campaign has already been sent'
            }), 400

        # Send emails
        success_count = 0
        failure_count = 0

        for recipient in campaign.recipients:
            try:
                send_email(recipient.email, campaign.subject, campaign.message)
                recipient.delivery_status = 'sent'
                recipient.sent_at = datetime.now()
                success_count += 1
            except Exception as e:
                recipient.delivery_status = 'failed'
                recipient.error_message = str(e)
                failure_count += 1

        # Update campaign status
        campaign.status = CampaignStatus.SENT
        campaign.sent_at = datetime.now()
        campaign.successful_sends = success_count
        campaign.failed_sends = failure_count

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Campaign sent! {success_count} successful, {failure_count} failed',
            'successful_sends': success_count,
            'failed_sends': failure_count
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error sending campaign: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while sending the campaign'
        }), 500


def send_email(to_email, subject, message):
    """Send email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()  # enable security

        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        # Send email
        text = msg.as_string()
        server.sendmail(app.config['MAIL_DEFAULT_SENDER'], to_email, text)
        server.quit()

        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        raise e


@app.route('/api/check_visitor_exists', methods=['POST'])
@login_required
def check_visitor_exists():
    try:
        pesel = request.form.get('pesel', '').strip()

        if not pesel:
            return jsonify({'exists': False})

        # Check if visitor with this PESEL already exists
        existing_visitor = Visitor.query.filter_by(pesel=pesel).first()

        if existing_visitor:
            # Get their last visit info
            last_visit = None
            if existing_visitor.last_visit_id:
                last_visit = Visits.query.get(existing_visitor.last_visit_id)

            return jsonify({
                'exists': True,
                'visitor': {
                    'id': existing_visitor.id,
                    'name': existing_visitor.name,
                    'email': existing_visitor.email,
                    'phone_number': existing_visitor.phone_number,
                    'total_visits': existing_visitor.total_visits or 0,
                    'last_check_in': existing_visitor.check_in_date.strftime(
                        '%Y-%m-%d') if existing_visitor.check_in_date else None,
                    'last_check_out': existing_visitor.check_out_date.strftime(
                        '%Y-%m-%d') if existing_visitor.check_out_date else None,
                    'last_hotel_id': last_visit.hotel_id if last_visit else None,
                    'last_room_type': last_visit.room_type.value if last_visit and last_visit.room_type else None,
                    'last_visit_date': existing_visitor.last_date_of_visit.strftime(
                        '%Y-%m-%d %H:%M') if existing_visitor.last_date_of_visit else None
                }
            })
        else:
            return jsonify({'exists': False})

    except Exception as e:
        print(f"Error checking visitor: {e}")
        return jsonify({'exists': False, 'error': 'An error occurred'})


@app.route('/api/add_visit_existing_visitor', methods=['POST'])
@login_required
def add_visit_existing_visitor():
    form = AddVisitorForm()

    if form.validate_on_submit():
        try:
            visitor_id = request.form.get('visitor_id')
            existing_visitor = Visitor.query.get(visitor_id)

            if not existing_visitor:
                return jsonify({
                    'success': False,
                    'errors': {'general': ['Visitor not found.']}
                }), 400

            # Create new visit record
            new_visit = Visits(
                visitor_id=existing_visitor.id,
                check_in_date=datetime.combine(form.check_in_date.data, datetime.min.time()),
                check_out_date=datetime.combine(form.check_out_date.data,
                                                datetime.min.time()) if form.check_out_date.data else None,
                hotel_id=form.hotel_id.data,
                room_type=RoomType(form.room_type.data)
            )

            db.session.add(new_visit)
            db.session.flush()  # Get the visit ID

            # Update visitor info
            existing_visitor.total_visits = (existing_visitor.total_visits or 0) + 1
            existing_visitor.last_visit_id = new_visit.id
            existing_visitor.last_date_of_visit = new_visit.check_in_date
            existing_visitor.check_in_date = form.check_in_date.data
            existing_visitor.check_out_date = form.check_out_date.data

            # Update contact info if different
            if form.phone_number.data != existing_visitor.phone_number:
                existing_visitor.phone_number = form.phone_number.data
            if form.email.data != existing_visitor.email:
                existing_visitor.email = form.email.data
            if form.name.data != existing_visitor.name:
                existing_visitor.name = form.name.data

            db.session.commit()

            return jsonify({
                'success': True,
                'visitor': {
                    'name': existing_visitor.name,
                    'email': existing_visitor.email,
                    'phone_number': existing_visitor.phone_number,
                    'hotel_id': new_visit.hotel_id,
                    'room_type': new_visit.room_type.value,
                    'check_in_date': existing_visitor.check_in_date.strftime('%Y-%m-%d'),
                    'check_out_date': existing_visitor.check_out_date.strftime(
                        '%Y-%m-%d') if existing_visitor.check_out_date else 'N/A',
                    'total_visits': existing_visitor.total_visits
                }
            })

        except Exception as e:
            db.session.rollback()
            print(f"Error adding visit: {e}")
            return jsonify({
                'success': False,
                'errors': {'general': ['An error occurred while saving the visit.']}
            }), 500
    else:
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400


if __name__ == '__main__':
    app.run(debug=True)