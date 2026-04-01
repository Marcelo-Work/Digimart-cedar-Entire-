from background_task import background
from django.core.mail import send_mail
from django.conf import settings
from api.models import EmailLog, Order, Product
from django.utils import timezone
from datetime import timedelta

@background(schedule=0) # Run immediately in background
def send_order_confirmation_email(order_id):
    try:
        # Check for Rate Limiting (Prevent Duplicates)
        recent_log = EmailLog.objects.filter(
            related_order_id=order_id, 
            status='sent',
            created_at__gte=timezone.now() - timedelta(seconds=settings.EMAIL_RATE_LIMIT_SECONDS)
        ).first()
        
        if recent_log:
            print(f"⚠️ Rate limit hit for Order {order_id}. Skipping duplicate email.")
            return

        order = Order.objects.get(id=order_id)
        user = order.user
        
        # 1. Prepare Customer Email Content
        items_list = "\n".join([f"- {item.product.title} (Qty: {item.quantity}) - ${item.total_price}" for item in order.items.all()])
        
        customer_subject = f"Order Confirmation #{order.id}"
        customer_body = f"""
        Hello {user.username},
        
        Your order #{order.id} has been confirmed!
        
        Order Details:
        {items_list}
        
        Total: ${order.total_amount}
        
        Thank you for shopping with DigiMart!
        """
        
        # 2. Prepare Vendor Notification (Find unique vendors in order)
        vendor_products = {}
        for item in order.items.all():
            vendor = item.product.vendor
            if vendor.email not in vendor_products:
                vendor_products[vendor.email] = []
            vendor_products[vendor.email].append(f"- {item.product.title} (Qty: {item.quantity})")

        # 3. Send Customer Email
        log_entry = EmailLog.objects.create(
            recipient_email=user.email,
            subject=customer_subject,
            body=customer_body,
            related_order_id=order.id,
            status='pending'
        )
        
        try:
            send_mail(
                subject=customer_subject,
                message=customer_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            log_entry.status = 'sent'
            log_entry.sent_at = timezone.now()
            log_entry.save()
            print(f"✅ Email sent to {user.email}")
        except Exception as e:
            log_entry.status = 'failed'
            log_entry.error_message = str(e)
            log_entry.save()
            print(f"❌ Failed to send email to {user.email}: {e}")
            # Do NOT re-raise, we want to continue to vendor emails even if customer email fails

        # 4. Send Vendor Emails
        for v_email, products in vendor_products.items():
            vendor_subject = f"New Order Received #{order.id}"
            vendor_body = f"""
            Hello Vendor,
            
            You have a new order!
            
            Products sold:
            {chr(10).join(products)}
            
            Please prepare for shipment.
            """
            
            v_log = EmailLog.objects.create(
                recipient_email=v_email,
                subject=vendor_subject,
                body=vendor_body,
                related_order_id=order.id,
                status='pending'
            )
            
            try:
                send_mail(
                    subject=vendor_subject,
                    message=vendor_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[v_email],
                    fail_silently=False,
                )
                v_log.status = 'sent'
                v_log.sent_at = timezone.now()
                v_log.save()
            except Exception as e:
                v_log.status = 'failed'
                v_log.error_message = str(e)
                v_log.save()

    except Order.DoesNotExist:
        print(f"Order {order_id} not found.")
    except Exception as e:
        print(f"Critical error in task: {e}")