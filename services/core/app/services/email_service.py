"""
Welcome Email Service using Resend
Sends automated welcome emails when users upgrade to Pro plan
"""

import os
from typing import Optional
import logging
from resend import Resend

logger = logging.getLogger(__name__)

# Initialize Resend client
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
resend_client = Resend(api_key=RESEND_API_KEY) if RESEND_API_KEY else None


def get_welcome_email_html(business_name: str, user_name: str) -> str:
    """Generate HTML welcome email for Pro plan upgrade"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to CallFlow AI Pro!</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f9fafb;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); padding: 40px 40px 60px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">
                                🎉 Welcome to CallFlow AI Pro!
                            </h1>
                            <p style="margin: 12px 0 0; color: #e0f2fe; font-size: 16px;">
                                You're now powered by Smart Automations
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Hi {user_name},
                            </p>
                            
                            <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Congratulations on upgrading <strong>{business_name}</strong> to CallFlow AI Pro! 🚀
                            </p>
                            
                            <p style="margin: 0 0 30px; color: #374151; font-size: 16px; line-height: 1.6;">
                                You now have access to our most powerful features, including Smart Automations powered by n8n. Here's what you can do right now:
                            </p>
                            
                            <!-- Features -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 16px; background-color: #f0f9ff; border-left: 4px solid #0891b2; margin-bottom: 12px;">
                                        <h3 style="margin: 0 0 8px; color: #0891b2; font-size: 16px; font-weight: 600;">
                                            📅 Google Calendar Sync
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                            Automatically sync all appointments to your Google Calendar in real-time
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 12px;"></td></tr>
                                <tr>
                                    <td style="padding: 16px; background-color: #fef3c7; border-left: 4px solid #f59e0b; margin-bottom: 12px;">
                                        <h3 style="margin: 0 0 8px; color: #f59e0b; font-size: 16px; font-weight: 600;">
                                            📊 Airtable Data Logging
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                            Log every call, transcript, and customer interaction to Airtable for analytics
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 12px;"></td></tr>
                                <tr>
                                    <td style="padding: 16px; background-color: #dcfce7; border-left: 4px solid #10b981; margin-bottom: 12px;">
                                        <h3 style="margin: 0 0 8px; color: #10b981; font-size: 16px; font-weight: 600;">
                                            💬 WhatsApp/SMS Confirmations
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                            Send automatic booking confirmations to reduce no-shows by 40%
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 12px;"></td></tr>
                                <tr>
                                    <td style="padding: 16px; background-color: #f3e8ff; border-left: 4px solid #a855f7; margin-bottom: 12px;">
                                        <h3 style="margin: 0 0 8px; color: #a855f7; font-size: 16px; font-weight: 600;">
                                            👥 HubSpot CRM Integration
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                            Automatically create and update contacts in your HubSpot CRM
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 12px;"></td></tr>
                                <tr>
                                    <td style="padding: 16px; background-color: #fce7f3; border-left: 4px solid #ec4899; margin-bottom: 12px;">
                                        <h3 style="margin: 0 0 8px; color: #ec4899; font-size: 16px; font-weight: 600;">
                                            📢 Slack Notifications
                                        </h3>
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                                            Get instant team notifications when new appointments are booked
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="https://app.callflowai.com/dashboard/automations" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Set Up Smart Automations →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Quick Start Guide -->
                            <div style="margin-top: 40px; padding: 24px; background-color: #f9fafb; border-radius: 8px;">
                                <h3 style="margin: 0 0 16px; color: #111827; font-size: 18px; font-weight: 600;">
                                    🚀 Quick Start Guide (5 minutes)
                                </h3>
                                <ol style="margin: 0; padding-left: 20px; color: #374151; font-size: 14px; line-height: 1.8;">
                                    <li>Go to <strong>Dashboard → Smart Automations</strong></li>
                                    <li>Toggle ON the automations you want to use</li>
                                    <li>Click <strong>Save Automations</strong></li>
                                    <li>Connect your API keys in <strong>Settings → Integrations</strong></li>
                                    <li>Test your first automation!</li>
                                </ol>
                            </div>
                            
                            <!-- Support -->
                            <p style="margin: 30px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                Need help getting started? Our support team is here 24/7. Just reply to this email or visit our <a href="https://docs.callflowai.com" style="color: #0891b2; text-decoration: none;">documentation</a>.
                            </p>
                            
                            <p style="margin: 20px 0 0; color: #374151; font-size: 16px; line-height: 1.6;">
                                Welcome aboard! 🎉<br>
                                <strong>The CallFlow AI Team</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f9fafb; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 8px; color: #9ca3af; font-size: 12px;">
                                CallFlow AI - Your AI-Powered Receptionist
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                <a href="https://callflowai.com" style="color: #0891b2; text-decoration: none;">Website</a> • 
                                <a href="https://docs.callflowai.com" style="color: #0891b2; text-decoration: none;">Docs</a> • 
                                <a href="mailto:support@callflowai.com" style="color: #0891b2; text-decoration: none;">Support</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def get_welcome_email_text(business_name: str, user_name: str) -> str:
    """Generate plain text welcome email for Pro plan upgrade"""
    return f"""
Welcome to CallFlow AI Pro!

Hi {user_name},

Congratulations on upgrading {business_name} to CallFlow AI Pro! 🚀

You now have access to our most powerful features, including Smart Automations powered by n8n.

HERE'S WHAT YOU CAN DO RIGHT NOW:

📅 Google Calendar Sync
   Automatically sync all appointments to your Google Calendar in real-time

📊 Airtable Data Logging
   Log every call, transcript, and customer interaction to Airtable for analytics

💬 WhatsApp/SMS Confirmations
   Send automatic booking confirmations to reduce no-shows by 40%

👥 HubSpot CRM Integration
   Automatically create and update contacts in your HubSpot CRM

📢 Slack Notifications
   Get instant team notifications when new appointments are booked

QUICK START GUIDE (5 MINUTES):

1. Go to Dashboard → Smart Automations
2. Toggle ON the automations you want to use
3. Click "Save Automations"
4. Connect your API keys in Settings → Integrations
5. Test your first automation!

Get started now: https://app.callflowai.com/dashboard/automations

Need help? Our support team is here 24/7. Just reply to this email or visit:
https://docs.callflowai.com

Welcome aboard! 🎉
The CallFlow AI Team

---
CallFlow AI - Your AI-Powered Receptionist
Website: https://callflowai.com
Docs: https://docs.callflowai.com
Support: support@callflowai.com
"""


async def send_pro_welcome_email(
    to_email: str,
    business_name: str,
    user_name: str
) -> bool:
    """
    Send welcome email when user upgrades to Pro plan
    
    Args:
        to_email: Recipient email address
        business_name: Name of the business
        user_name: Name of the user
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not resend_client:
        logger.error("Resend API key not configured. Cannot send welcome email.")
        return False
    
    try:
        html_content = get_welcome_email_html(business_name, user_name)
        text_content = get_welcome_email_text(business_name, user_name)
        
        response = resend_client.emails.send({
            "from": "CallFlow AI <welcome@callflowai.com>",
            "to": [to_email],
            "subject": f"🎉 Welcome to CallFlow AI Pro, {user_name}!",
            "html": html_content,
            "text": text_content
        })
        
        logger.info(f"✅ Welcome email sent to {to_email}: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False


async def send_onboarding_reminder(
    to_email: str,
    business_name: str,
    user_name: str,
    days_since_upgrade: int
) -> bool:
    """
    Send onboarding reminder email if user hasn't completed setup
    
    Args:
        to_email: Recipient email address
        business_name: Name of the business
        user_name: Name of the user
        days_since_upgrade: Number of days since Pro upgrade
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not resend_client:
        logger.error("Resend API key not configured.")
        return False
    
    try:
        subject = f"Don't forget to set up your Smart Automations!"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>Hi {user_name},</h2>
    <p>It's been {days_since_upgrade} days since you upgraded to CallFlow AI Pro, but we noticed you haven't set up your Smart Automations yet.</p>
    <p>You're missing out on:</p>
    <ul>
        <li>Automatic appointment confirmations (reduce no-shows by 40%)</li>
        <li>Real-time calendar syncing</li>
        <li>CRM integration</li>
        <li>And much more!</li>
    </ul>
    <p><a href="https://app.callflowai.com/dashboard/automations" style="background-color: #0891b2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Set Up Now (5 minutes)</a></p>
    <p>Need help? Reply to this email and we'll get you started!</p>
    <p>Best,<br>The CallFlow AI Team</p>
</body>
</html>
"""
        
        text_content = f"""
Hi {user_name},

It's been {days_since_upgrade} days since you upgraded to CallFlow AI Pro, but we noticed you haven't set up your Smart Automations yet.

You're missing out on:
- Automatic appointment confirmations (reduce no-shows by 40%)
- Real-time calendar syncing
- CRM integration
- And much more!

Set up now (5 minutes): https://app.callflowai.com/dashboard/automations

Need help? Reply to this email and we'll get you started!

Best,
The CallFlow AI Team
"""
        
        response = resend_client.emails.send({
            "from": "CallFlow AI <support@callflowai.com>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        })
        
        logger.info(f"✅ Onboarding reminder sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send onboarding reminder to {to_email}: {e}")
        return False
