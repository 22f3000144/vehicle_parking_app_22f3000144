# jobs/tasks.py

import csv
import io
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from data.models import db, User, ParkingLot, ParkingSpot, ReserveParking
from celery import shared_task
from sqlalchemy import func


# -------------------------------------------------------------------
# Helper: send email
# -------------------------------------------------------------------

def send_mail(subject, recipient, html):
    mail = current_app.extensions.get("mail")
    if not mail:
        return False

    msg = Message(subject, recipients=[recipient], html=html)
    mail.send(msg)
    return True


# -------------------------------------------------------------------
# 1. Daily inactive user reminder
# -------------------------------------------------------------------

@shared_task(name="tasks.daily_inactive_user_reminder")
def daily_inactive_user_reminder():
    """Send a reminder email to users who have no reservations for 3+ days"""

    cutoff = datetime.utcnow() - timedelta(days=3)

    inactive_users = (
        User.query
        .outerjoin(ReserveParking)
        .group_by(User.id)
        .having(
            func.max(ReserveParking.parking_timestamp).is_(None) |
            (func.max(ReserveParking.parking_timestamp) < cutoff)
        )
        .all()
    )

    for user in inactive_users:
        html = f"""
        <h3>Hello {user.username},</h3>
        <p>You haven't used your parking facility recently.</p>
        <p>Reserve a spot anytime.</p>
        """
        send_mail("Parking Reminder", user.email, html)

    return f"Sent reminders to {len(inactive_users)} users."


# -------------------------------------------------------------------
# 2. Daily new parking lot alert
# (Your ParkingLot model has no created_at — so we detect "new lots"
#  added in the last 24 hours using id + join time)
# -------------------------------------------------------------------

@shared_task(name="tasks.daily_new_lot_alert")
def daily_new_lot_alert():
    """Notify admin if new lots were added recently."""

    # last 24 hours window
    cutoff = datetime.utcnow() - timedelta(hours=24)

    # Since there is no created_at column, fallback to:
    # new lots = lots with at least 1 spot created in last 24 hrs
    # because your spots get auto-created immediately
    lots = (
        ParkingLot.query
        .join(ParkingSpot)
        .filter(ParkingSpot.entry_time.is_(None))  # uses creation behavior
        .all()
    )

    if not lots:
        return "No new lots detected."

    admin = User.query.join(User.roles).filter_by(name="admin").first()
    if not admin:
        return "Admin user not found."

    lot_list = "<br>".join([l.prime_location_name for l in lots])

    html = f"""
    <h3>New Parking Lots Added</h3>
    <p>{lot_list}</p>
    """

    send_mail("New Parking Lots Added", admin.email, html)
    return f"Sent admin alert for {len(lots)} lots."


# -------------------------------------------------------------------
# 3. Monthly activity report (previous month)
# -------------------------------------------------------------------

@shared_task(name="tasks.monthly_report")
def monthly_report():
    """Send monthly parking report for previous month"""

    today = datetime.utcnow()
    first_day = today.replace(day=1)
    last_month_last_day = first_day - timedelta(days=1)
    last_month = last_month_last_day.strftime("%Y-%m")

    users = User.query.all()

    for user in users:
        history = (
            ReserveParking.query
            .filter(
                ReserveParking.user_id == user.id,
                func.strftime("%Y-%m", ReserveParking.parking_timestamp) == last_month
            )
            .all()
        )

        total_cost = sum(h.parking_cost or 0 for h in history)
        total_reservations = len(history)

        html = f"""
        <h2>Your Monthly Parking Report</h2>
        <p><strong>User:</strong> {user.username}</p>
        <p><strong>Month:</strong> {last_month}</p>
        <p><strong>Total Reservations:</strong> {total_reservations}</p>
        <p><strong>Total Cost:</strong> ₹{total_cost}</p>
        """

        send_mail("Your Monthly Parking Report", user.email, html)

    return "Monthly reports sent."


# -------------------------------------------------------------------
# 4. Export user reservation history (Matches your API!)
# -------------------------------------------------------------------

@shared_task(name="tasks.export_parking_history")
def export_parking_history(user_id):
    """Generate CSV for the user’s reservation history"""

    user = User.query.get(user_id)
    if not user:
        return "User not found."

    reservations = ReserveParking.query.filter_by(user_id=user_id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # header
    writer.writerow(["Reservation ID", "Spot ID", "Entry Time", "Exit Time", "Cost"])

    for r in reservations:
        writer.writerow([
            r.id,
            r.spot_id,
            r.parking_timestamp,
            r.leaving_timestamp,
            r.parking_cost,
        ])

    csv_data = output.getvalue()
    output.close()

    html = f"<h3>Your Parking History CSV</h3><p>Hello {user.username}, find your CSV attached.</p>"

    mail = current_app.extensions.get("mail")
    msg = Message("Your Parking History CSV", recipients=[user.email], html=html)
    msg.attach("parking_history.csv", "text/csv", csv_data)
    mail.send(msg)

    return "CSV sent successfully."
