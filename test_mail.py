import smtplib
import socket
import urllib.request
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_direct_mx(to_email, otp):
    domain = to_email.split('@')[-1]
    url = f'https://dns.google/resolve?name={domain}&type=MX'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=5)
    data = json.loads(res.read().decode('utf-8'))
    answers = data.get('Answer', [])
    if not answers:
        print('No MX records found for', domain)
        return False
    
    answers_sorted = sorted(answers, key=lambda x: int(x['data'].split()[0]))
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Clean & Safe India - Verification OTP: {otp}'
    msg['From'] = 'noreply@cleansafeindia.gov.in'
    msg['To'] = to_email

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 550px; margin: 0 auto; background: #060911; color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #10b981;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #10b981; margin: 0;">Clean & Safe India</h2>
            <p style="color: #94a3b8; font-size: 13px; margin: 4px 0;">National Smart Civic Grievance Network</p>
        </div>
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px dashed #10b981; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
            <div style="font-size: 13px; color: #a7f3d0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Your Citizen Verification OTP</div>
            <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #34d399; margin: 12px 0; font-family: monospace;">{otp}</div>
            <div style="font-size: 12px; color: #cbd5e1;">Valid for 10 minutes. Do not share this OTP with anyone.</div>
        </div>
        <p style="font-size: 13px; color: #94a3b8; line-height: 1.5;">
            Use this OTP to complete your citizen registration and claim your <strong>20 Welcome Civic Credits</strong>.
        </p>
        <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; margin-top: 20px; font-size: 11px; color: #64748b; text-align: center;">
            Government of India - Ministry of Housing & Urban Affairs (MoHUA)
        </div>
    </div>
    """
    msg.attach(MIMEText(html, 'html'))

    for ans in answers_sorted:
        mx_host = ans['data'].split()[-1].rstrip('.')
        try:
            print(f'Attempting direct connection to {mx_host}:25...')
            server = smtplib.SMTP(mx_host, 25, timeout=10)
            server.ehlo('cleansafeindia.gov.in')
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo('cleansafeindia.gov.in')
            server.sendmail('noreply@cleansafeindia.gov.in', [to_email], msg.as_string())
            server.quit()
            print(f'SUCCESS: Mail delivered to {mx_host} for {to_email}!')
            return True
        except Exception as e:
            print(f'Failed on {mx_host}: {e}')
            continue
    return False

if __name__ == '__main__':
    send_direct_mx('mukundhak9@gmail.com', '492817')
