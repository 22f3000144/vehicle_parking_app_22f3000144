# jobs/tasks.py

import csv
import io
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from data.models import db, User, ParkingLot, ParkingSpot, ReserveParking
from celery import shared_task
from sqlalchemy import func


# -----------------------------------------------------
# Helper: send email
# -----------------------------------------------------
def send_mail(subject, recipients, html):
    mail = current_app.extensions.get("mail")
    if not mail:
        return False

    msg = Message(subject, recipients=[recipients], html=html)
    mail.send(msg)
    return True


# -----------------------------------------------------
# 1. Daily inactive user reminder
# -----------------------------------------------------
@shared_task(name="daily_inactive_user_reminder")
def daily_inactive_user_reminder():
    """Send a reminder email to users who have no reservations for 3+ days"""

    three_days_ago = datetime.utcnow() - timedelta(days=3)

    inactive_users = (
        User.query.outerjoin(ReserveParking)
        .group_by(User.id)
        .having(func.max(ReserveParking.parking_timestamp) < three_days_ago)
        .all()
    )

    for user in inactive_users:
        html = f"""
        <h3>Hello {user.username},</h3>
        <p>You haven’t used your parking benefits for a while.</p>
        <p>Feel free to reserve a spot anytime!</p>
        """
        send_mail("We Miss You at Parking System!", user.email, html)

    return f"Sent to {len(inactive_users)} inactive users."


# -----------------------------------------------------
# 2. Notify admin when new parking lot is created (daily scan)
# -----------------------------------------------------
@shared_task(name="daily_new_lot_alert")
def daily_new_lot_alert():
    """Notify admin of any new parking lots created today"""

    today = datetime.utcnow().date()

    lots = ParkingLot.query.filter(
        func.date(ParkingLot.id) == today  # assuming ID increments daily
    ).all()

    if not lots:
        return "No new lots today."

    admin = User.query.join(User.roles).filter_by(name="admin").first()
    if not admin:
        return "No admin found."

    lot_names = "<br>".join([l.prime_location_name for l in lots])

    html = f"""
    <h3>New Parking Lots Added Today</h3>
    <p>{lot_names}</p>
    """

    send_mail("New Parking Lots Added", admin.email, html)

    return f"Sent admin alert for {len(lots)} lots."


# -----------------------------------------------------
# 3. Monthly activity report
# -----------------------------------------------------
@shared_task(name="monthly_report")
def monthly_report():
    """Send monthly activity report (1st of every month)"""

    current_month = datetime.utcnow().strftime("%Y-%m")

    users = User.query.all()

    for user in users:
        history = (
            ReserveParking.query
            .filter(
                ReserveParking.user_id == user.id,
                func.strftime("%Y-%m", ReserveParking.parking_timestamp) == current_month
            )
            .all()
        )

        total_cost = sum(h.parking_cost or 0 for h in history)
        total_reservations = len(history)

        html = f"""
        <h2>Your Monthly Parking Report</h2>
        <p><strong>User:</strong> {user.username}</p>
        <p><strong>Month:</strong> {current_month}</p>
        <p><strong>Total Reservations:</strong> {total_reservations}</p>
        <p><strong>Total Cost:</strong> ₹{total_cost}</p>
        """

        send_mail("Your Monthly Parking Report", user.email, html)

    return "Monthly reports sent."


# -----------------------------------------------------
# 4. Export User Reservation History to CSV
# -----------------------------------------------------
@shared_task(name="export_user_history")
def export_user_history(user_id):
    """Generate CSV for the user’s reservation history"""

    user = User.query.get(user_id)
    if not user:
        return "User not found."

    reservations = ReserveParking.query.filter_by(user_id=user_id).all()

    # CSV buffer
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Spot ID", "Lot ID", "Entry Time", "Exit Time", "Cost"])

    for r in reservations:
        writer.writerow([
            r.spot_id,
            r.spot.lot_id,
            r.parking_timestamp,
            r.leaving_timestamp,
            r.parking_cost
        ])

    csv_data = output.getvalue()
    output.close()

    # Email the CSV
    html = "<h3>Your Parking History Export</h3><p>CSV is attached.</p>"

    mail = current_app.extensions.get("mail")
    msg = Message("Your Parking History CSV", recipients=[user.email], html=html)
    msg.attach("parking_history.csv", "text/csv", csv_data)
    mail.send(msg)

    return "CSV sent."
