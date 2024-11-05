import stripe
import os
from flask import jsonify, request
from main import app, logger
from extensions import db
from models import Booking
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest

stripe.api_key = os.environ['STRIPE_SECRET_KEY']

@app.route('/create-payment-intent/<int:booking_id>', methods=['POST'])
@login_required
def create_payment_intent(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Ensure the current user is the customer
        if booking.customer_id != current_user.id:
            logger.warning(f"Unauthorized payment attempt for booking {booking_id} by user {current_user.id}")
            return jsonify({"error": "Unauthorized"}), 403
        
        # Check if booking is already paid
        if booking.payment_status == 'paid':
            logger.warning(f"Attempt to pay for already paid booking {booking_id}")
            return jsonify({"error": "Booking is already paid"}), 400
            
        # Calculate amount in cents
        amount = int(booking.total_amount * 100)
        
        # Create a PaymentIntent with the booking details
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'booking_id': booking_id,
                'customer_id': current_user.id,
                'service_title': booking.service.title
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        # Update booking with payment intent ID
        booking.payment_intent_id = intent.id
        db.session.commit()
        
        logger.info(f"Payment intent created for booking {booking_id}")
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error for booking {booking_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating payment intent for booking {booking_id}: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        logger.error(f"Invalid payload in webhook: {str(e)}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature in webhook: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400

    try:
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            booking_id = payment_intent['metadata']['booking_id']
            
            # Update booking payment status
            booking = Booking.query.get(booking_id)
            if booking:
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                db.session.commit()
                logger.info(f"Payment succeeded for booking {booking_id}")
            else:
                logger.error(f"Booking {booking_id} not found for successful payment")
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            booking_id = payment_intent['metadata']['booking_id']
            logger.error(f"Payment failed for booking {booking_id}")

        logger.info(f"Webhook processed successfully: {event['type']}")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
