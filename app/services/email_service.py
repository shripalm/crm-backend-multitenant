"""Email service for sending OTP and other notifications via SendGrid."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content

from app.core.config import settings
from app.utils.logging import logger


# ============== ACTIVE SENDGRID EMAIL FUNCTIONS ==============


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
) -> bool:
    """
    Send an email using SendGrid API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body of the email
        plain_content: Plain text alternative (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        message = Mail(
            from_email=f"{settings.SENDGRID_FROM_NAME} <{settings.SENDGRID_FROM_EMAIL}>",
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        
        # Add plain text content if provided
        if plain_content:
            message.add_content(Content("text/plain", plain_content))
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent successfully via SendGrid to {to_email}")
            return True
        else:
            logger.error(f"SendGrid error: Status code {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send email via SendGrid: {str(e)}", exc_info=True)
        return False


async def send_otp_email(to_email: str, otp_code: str, agent_name: str) -> bool:
    """
    Send OTP email for password reset via SendGrid.
    
    Args:
        to_email: Agent's email address
        otp_code: 4-digit OTP code
        agent_name: Agent's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Password Reset OTP - CRM System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px 10px 0 0;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">Password Reset</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                    Hello <strong>{agent_name}</strong>,
                                </p>
                                <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    We received a request to reset your password. Use the following OTP to proceed:
                                </p>
                                <!-- OTP Box -->
                                <div style="text-align: center; margin: 30px 0;">
                                    <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 50px; border-radius: 10px;">
                                        <span style="font-size: 36px; font-weight: bold; color: #ffffff; letter-spacing: 10px;">{otp_code}</span>
                                    </div>
                                </div>
                                <p style="margin: 30px 0 20px 0; color: #666666; font-size: 14px; line-height: 1.6; text-align: center;">
                                    ⏰ This OTP is valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
                                </p>
                                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
                                <p style="margin: 0; color: #999999; font-size: 13px; line-height: 1.6;">
                                    If you did not request this password reset, please ignore this email or contact support if you have concerns.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                                <p style="margin: 0; color: #999999; font-size: 12px;">
                                    © 2024 CRM System. All rights reserved.
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
    
    plain_content = f"""
    Password Reset OTP
    
    Hello {agent_name},
    
    We received a request to reset your password. Use the following OTP to proceed:
    
    Your OTP: {otp_code}
    
    This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes.
    
    If you did not request this password reset, please ignore this email.
    
    © 2024 CRM System
    """
    
    return await send_email(to_email, subject, html_content, plain_content)


async def send_password_reset_success_email(to_email: str, agent_name: str) -> bool:
    """
    Send confirmation email after successful password reset via SendGrid.
    
    Args:
        to_email: Agent's email address
        agent_name: Agent's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Password Reset Successful - CRM System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 10px 10px 0 0;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">✓ Password Reset Successful</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                    Hello <strong>{agent_name}</strong>,
                                </p>
                                <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    Your password has been successfully reset. You can now log in with your new password.
                                </p>
                                <p style="margin: 20px 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                    If you did not make this change, please contact support immediately.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                                <p style="margin: 0; color: #999999; font-size: 12px;">
                                    © 2024 CRM System. All rights reserved.
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
    
    plain_content = f"""
    Password Reset Successful
    
    Hello {agent_name},
    
    Your password has been successfully reset. You can now log in with your new password.
    
    If you did not make this change, please contact support immediately.
    
    © 2024 CRM System
    """
    
    return await send_email(to_email, subject, html_content, plain_content)


# ============== UNUTILISED SMTP (GMAIL) EMAIL FUNCTIONS ==============


async def send_email_unutilised(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
) -> bool:
    """
    Send an email using Gmail SMTP.
    
    UNUTILISED - This function is kept for reference but not used in production.
    We now use SendGrid for email delivery.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body of the email
        plain_content: Plain text alternative (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        # Attach plain text version
        if plain_content:
            part1 = MIMEText(plain_content, "plain")
            msg.attach(part1)

        # Attach HTML version
        part2 = MIMEText(html_content, "html")
        msg.attach(part2)

        # Connect to Gmail SMTP server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.SMTP_FROM_EMAIL,
                to_email,
                msg.as_string()
            )

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        return False


async def send_otp_email_unutilised(to_email: str, otp_code: str, agent_name: str) -> bool:
    """
    Send OTP email for password reset.
    
    UNUTILISED - This function is kept for reference but not used in production.
    We now use SendGrid for email delivery.
    
    Args:
        to_email: Agent's email address
        otp_code: 4-digit OTP code
        agent_name: Agent's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Password Reset OTP - CRM System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px 10px 0 0;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">Password Reset</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                    Hello <strong>{agent_name}</strong>,
                                </p>
                                <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    We received a request to reset your password. Use the following OTP to proceed:
                                </p>
                                <!-- OTP Box -->
                                <div style="text-align: center; margin: 30px 0;">
                                    <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 50px; border-radius: 10px;">
                                        <span style="font-size: 36px; font-weight: bold; color: #ffffff; letter-spacing: 10px;">{otp_code}</span>
                                    </div>
                                </div>
                                <p style="margin: 30px 0 20px 0; color: #666666; font-size: 14px; line-height: 1.6; text-align: center;">
                                    ⏰ This OTP is valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
                                </p>
                                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
                                <p style="margin: 0; color: #999999; font-size: 13px; line-height: 1.6;">
                                    If you did not request this password reset, please ignore this email or contact support if you have concerns.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                                <p style="margin: 0; color: #999999; font-size: 12px;">
                                    © 2024 CRM System. All rights reserved.
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
    
    plain_content = f"""
    Password Reset OTP
    
    Hello {agent_name},
    
    We received a request to reset your password. Use the following OTP to proceed:
    
    Your OTP: {otp_code}
    
    This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes.
    
    If you did not request this password reset, please ignore this email.
    
    © 2024 CRM System
    """
    
    return await send_email_unutilised(to_email, subject, html_content, plain_content)


async def send_password_reset_success_email_unutilised(to_email: str, agent_name: str) -> bool:
    """
    Send confirmation email after successful password reset.
    
    UNUTILISED - This function is kept for reference but not used in production.
    We now use SendGrid for email delivery.
    
    Args:
        to_email: Agent's email address
        agent_name: Agent's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Password Reset Successful - CRM System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border-radius: 10px 10px 0 0;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">✓ Password Reset Successful</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                    Hello <strong>{agent_name}</strong>,
                                </p>
                                <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    Your password has been successfully reset. You can now log in with your new password.
                                </p>
                                <p style="margin: 20px 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                    If you did not make this change, please contact support immediately.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; text-align: center; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                                <p style="margin: 0; color: #999999; font-size: 12px;">
                                    © 2024 CRM System. All rights reserved.
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
    
    plain_content = f"""
    Password Reset Successful
    
    Hello {agent_name},
    
    Your password has been successfully reset. You can now log in with your new password.
    
    If you did not make this change, please contact support immediately.
    
    © 2024 CRM System
    """
    
    return await send_email_unutilised(to_email, subject, html_content, plain_content)
