from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import os
import uuid
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import email
import threading
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
EXCEL_FILE = 'issues_data.xlsx'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Email configuration (configure these for your email service)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "support@comengg.com"
EMAIL_PASSWORD = "tkprwctvsunyaffe"
SUPPORT_EMAIL = "support@comengg.com"
TECH_TEAM_EMAIL = "binara@comengg.com"
CC_EMAILS = ["faazil@cinnamonhotels.com", "sulara@cinnamonhotels.com"]

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_issues():
    """Load issues from Excel file"""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            return df.to_dict('records')
        return []
    except Exception as e:
        print(f"Error loading issues: {e}")
        return []

def save_issues(issues):
    """Save issues to Excel file"""
    try:
        df = pd.DataFrame(issues)
        df.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving issues: {e}")
        return False

def generate_report_id():
    """Generate a unique report ID"""
    return f"#{str(uuid.uuid4())[:8].upper()}"

def send_email(to_email, subject, body, attachments=None, cc_emails=None):
    """Send email notification with CC support and duplicate prevention"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC emails if provided, but prevent duplicates
        if cc_emails:
            # Remove duplicates and the main recipient from CC list
            cc_list = list(set(cc_emails))
            if to_email in cc_list:
                cc_list.remove(to_email)
            
            if cc_list:
                msg['Cc'] = ', '.join(cc_list)
        
        msg.attach(MIMEText(body, 'html'))
        
        if attachments:
            for attachment in attachments:
                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment)}')
                    msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        
        # Prepare recipient list (main recipient + CC recipients)
        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_list)
        
        server.sendmail(EMAIL_ADDRESS, recipients, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_comprehensive_timing_info(issue):
    """Generate comprehensive timing information for email templates"""
    timing_info = f"""
    <div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin: 0 0 10px 0; color: #495057;">📊 Complete Issue Information:</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <p><strong>Issue ID:</strong> {issue['report_id']}</p>
                <p><strong>Project:</strong> {issue['project']}</p>
                <p><strong>Status:</strong> <span style="color: {'#dc3545' if issue['status'] == 'Pending' else '#ffc107' if issue['status'] == 'In Progress' else '#28a745'}">{issue['status']}</span></p>
                <p><strong>Priority:</strong> <span style="color: {'#dc3545' if issue['priority'] == 'High' else '#ffc107' if issue['priority'] == 'Medium' else '#28a745'}">{issue['priority']}</span></p>
            </div>
            <div>
                <p><strong>Tech Level:</strong> {issue['tech_level']}</p>
                <p><strong>Assigned To:</strong> {issue['assigned_to']}</p>
                <p><strong>Client:</strong> {issue['client_name']}</p>
                <p><strong>Contact:</strong> {issue['phone_number']}</p>
            </div>
        </div>
    </div>
    
    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin: 0 0 10px 0; color: #495057;">⏰ Timeline & Timing:</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <p><strong>Reported Date:</strong> {issue.get('created_date', 'N/A')}</p>
                <p><strong>Reported Time:</strong> {issue.get('created_time', 'N/A')}</p>
                <p><strong>Work Started Date:</strong> {issue.get('start_date', 'Not Started')}</p>
                <p><strong>Work Started Time:</strong> {issue.get('start_time_only', 'Not Started')}</p>
            </div>
            <div>
                <p><strong>Completed Date:</strong> {issue.get('end_date', 'Not Completed')}</p>
                <p><strong>Completed Time:</strong> {issue.get('end_time_only', 'Not Completed')}</p>
                <p><strong>Total Resolution Time:</strong> {issue.get('total_resolution_time', 'Not Calculated')}</p>
                <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </div>
    """
    return timing_info

def add_to_history(issue_id, action, description, performed_by):
    """Add entry to issue history"""
    history_file = 'issue_history.json'
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {}
        
        if issue_id not in history:
            history[issue_id] = []
        
        history[issue_id].append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'description': description,
            'performed_by': performed_by
        })
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error adding to history: {e}")
        return False

# Custom template filters
@app.template_filter('safe_strftime')
def safe_strftime(date_str, format='%Y-%m-%d %H:%M'):
    try:
        if pd.isna(date_str) or date_str == 'nan' or date_str is None:
            return 'N/A'
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime(format)
    except:
        return str(date_str)

@app.template_filter('split')
def split_filter(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    if not value or value == 'nan' or value is None:
        return []
    return str(value).split(delimiter)

# Routes
@app.route('/')
def index():
    return render_template('client.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_role = request.form['user_role']
        
        # Simple authentication (replace with proper auth in production)
        if user_role == 'tech_team' and username == 'admin' and password == 'password123':
            session['logged_in'] = True
            session['username'] = username
            session['user_role'] = user_role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif user_role == 'client':
            # Allow any client login for demo purposes
            session['logged_in'] = True
            session['username'] = username
            session['user_role'] = user_role
            flash('Login successful!', 'success')
            return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_role') != 'tech_team':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    issues = load_issues()
    return render_template('dashboard.html', issues=issues)

@app.route('/client-dashboard')
@login_required
def client_dashboard():
    if session.get('user_role') != 'client':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    issues = load_issues()
    # Filter issues for this client (simplified - in production, filter by actual client email)
    client_issues = [issue for issue in issues if issue.get('email') == session.get('username')]
    return render_template('client_dashboard.html', issues=client_issues)

@app.route('/api/issues', methods=['POST'])
def create_issue():
    try:
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        project = request.form.get('project')
        priority = request.form.get('priority')
        description = request.form.get('description')
        
        # Validate required fields
        if not all([name, phone, email, project, priority, description]):
            return jsonify({'success': False, 'error': 'All required fields must be filled'})
        
        # Handle file uploads
        uploaded_files = []
        if 'image_0' in request.files:
            for i in range(10):  # Max 10 images
                file_key = f'image_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename and allowed_file(file.filename):
                        if file.content_length <= MAX_FILE_SIZE:
                            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            file.save(filepath)
                            uploaded_files.append(filename)
        
        # Generate unique report ID
        report_id = generate_report_id()
        
        # Create issue object with comprehensive timing tracking
        current_time = datetime.now()
        issue = {
            'id': len(load_issues()) + 1,
            'report_id': report_id,
            'client_name': name,
            'phone_number': phone,
            'email': email,
            'project': project,
            'issue_description': description,
            'image_filename': ','.join(uploaded_files) if uploaded_files else '',
            'status': 'Pending',
            'priority': priority,  # Priority from client
            'tech_level': 'L1',
            'assigned_to': 'CE',
            'created_timestamp': current_time.isoformat(),
            'created_date': current_time.strftime('%Y-%m-%d'),
            'created_time': current_time.strftime('%H:%M:%S'),
            'start_time': '',
            'start_date': '',
            'end_time': '',
            'end_date': '',
            'resolution_time': '',
            'resolution_date': '',
            'total_resolution_time': '',
            'resolution_notes': ''
        }
        
        # Load existing issues and add new one
        issues = load_issues()
        issues.append(issue)
        
        # Save to Excel
        if save_issues(issues):
            # Add to history
            add_to_history(issue['id'], 'Created', f'Issue created with ID {report_id}', 'System')
            
            # Send confirmation email to client with comprehensive timing
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #667eea; text-align: center;">📝 Issue Reported Successfully!</h2>
                    <p>Dear {name},</p>
                    <p>Thank you for reporting your issue. We have received your request and our technical team will review it shortly.</p>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3 style="margin: 0 0 10px 0; color: #856404;">📋 Issue Description:</h3>
                        <p style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">{description}</p>
                    </div>
                    
                    {generate_comprehensive_timing_info(issue)}
                    
                    <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #0c5460;">📧 What happens next?</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Our technical team will review your issue</li>
                            <li>Priority and tech level will be assigned</li>
                            <li>You'll receive email updates at each stage</li>
                            <li>Work will begin once assigned to the appropriate team</li>
                            <li>Resolution details will be provided upon completion</li>
                        </ul>
                    </div>
                    
                    <p>You will receive updates via email as our team works on resolving your issue. If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        TechFlow Support Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            send_email(email, f"Issue Reported - {report_id}", email_body, cc_emails=CC_EMAILS)
            
            return jsonify({'success': True, 'report_id': report_id})
        else:
            return jsonify({'success': False, 'error': 'Failed to save issue'})
    
    except Exception as e:
        print(f"Error creating issue: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while creating the issue'})

# Priority is now set by the client during issue creation

@app.route('/api/issues/<int:issue_id>/tech_level', methods=['PUT'])
@login_required
def set_tech_level(issue_id):
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        data = request.get_json()
        tech_level = data.get('tech_level')
        performed_by = data.get('performed_by', 'Technical Team')
        
        if tech_level not in ['L1', 'L2', 'L3']:
            return jsonify({'success': False, 'error': 'Invalid tech level'})
        
        issues = load_issues()
        issue = next((i for i in issues if i['id'] == issue_id), None)
        
        if not issue:
            return jsonify({'success': False, 'error': 'Issue not found'})
        
        old_tech_level = issue['tech_level']
        
        # Update tech level and assigned team
        issue['tech_level'] = tech_level
        if tech_level == 'L1':
            issue['assigned_to'] = 'CE'
        elif tech_level == 'L2':
            issue['assigned_to'] = 'Skidata' if issue['project'] == 'PMS' else 'TKH'
        elif tech_level == 'L3':
            issue['assigned_to'] = 'Skidata (Escalation)' if issue['project'] == 'PMS' else 'TKH (Escalation)'
        
        if save_issues(issues):
            add_to_history(issue_id, 'Tech Level Changed', f'Tech level changed from {old_tech_level} to {tech_level}, assigned to {issue["assigned_to"]}', performed_by)
            
            # Send comprehensive email notification for tech level change
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #6f42c1; text-align: center;">🔧 Tech Level Updated!</h2>
                    <p>Dear {issue['client_name']},</p>
                    <p>Your issue has been assigned a technical level and team for resolution.</p>
                    
                    <div style="background: #e2e3e5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #6c757d;">
                        <h3 style="margin: 0 0 10px 0; color: #383d41;">🔄 Technical Assignment:</h3>
                        <p><strong>Previous Tech Level:</strong> {old_tech_level}</p>
                        <p><strong>New Tech Level:</strong> {tech_level}</p>
                        <p><strong>Assigned Team:</strong> {issue['assigned_to']}</p>
                        <p><strong>Updated By:</strong> {performed_by}</p>
                        <p><strong>Update Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    {generate_comprehensive_timing_info(issue)}
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #495057;">📋 Issue Description:</h3>
                        <p style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">{issue['issue_description']}</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #0c5460;">ℹ️ What this means:</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li><strong>L1 (CE):</strong> Basic support and troubleshooting</li>
                            <li><strong>L2 (Skidata/TKH):</strong> Advanced technical support</li>
                            <li><strong>L3 (Escalation):</strong> Expert-level resolution</li>
                        </ul>
                    </div>
                    
                    <p>The assigned team will now work on resolving your issue according to the technical level assigned.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        TechFlow Support Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            send_email(issue['email'], f"Tech Level Updated - {issue['report_id']}", email_body, cc_emails=CC_EMAILS)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update tech level'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/issues/<int:issue_id>/start', methods=['PUT'])
@login_required
def start_issue(issue_id):
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        data = request.get_json()
        performed_by = data.get('performed_by', 'Technical Team')
        
        issues = load_issues()
        issue = next((i for i in issues if i['id'] == issue_id), None)
        
        if not issue:
            return jsonify({'success': False, 'error': 'Issue not found'})
        
        if issue['status'] != 'Pending':
            return jsonify({'success': False, 'error': 'Issue is not in pending status'})
        
        current_time = datetime.now()
        issue['status'] = 'In Progress'
        issue['start_time'] = current_time.isoformat()
        issue['start_date'] = current_time.strftime('%Y-%m-%d')
        issue['start_time_only'] = current_time.strftime('%H:%M:%S')
        
        if save_issues(issues):
            add_to_history(issue_id, 'Work Started', 'Technical work has begun on this issue', performed_by)
            
            # Send email to client with comprehensive timing
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #ffc107; text-align: center;">🚀 Work Started on Your Issue!</h2>
                    <p>Dear {issue['client_name']},</p>
                    <p>We're pleased to inform you that work has now begun on your issue.</p>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3 style="margin: 0 0 10px 0; color: #856404;">🔄 Status Update:</h3>
                        <p><strong>Previous Status:</strong> Pending</p>
                        <p><strong>Current Status:</strong> <span style="color: #ffc107; font-weight: bold;">In Progress</span></p>
                        <p><strong>Started By:</strong> {performed_by}</p>
                        <p><strong>Start Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    {generate_comprehensive_timing_info(issue)}
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #495057;">📋 Issue Description:</h3>
                        <p style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">{issue['issue_description']}</p>
                    </div>
                    
                    <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #155724;">✅ Next Steps:</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Our technical team is actively working on your issue</li>
                            <li>You'll receive updates as progress is made</li>
                            <li>Resolution details will be provided upon completion</li>
                            <li>If you have any questions, please contact us</li>
                        </ul>
                    </div>
                    
                    <p>Our technical team is now working on resolving your issue. You will receive another update when the work is completed.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        TechFlow Support Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            send_email(issue['email'], f"Work Started - {issue['report_id']}", email_body, cc_emails=CC_EMAILS)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to start issue'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/issues/<int:issue_id>/complete', methods=['PUT'])
@login_required
def complete_issue(issue_id):
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        data = request.get_json()
        resolution_notes = data.get('resolution_notes', 'Issue resolved successfully')
        performed_by = data.get('performed_by', 'Technical Team')
        
        issues = load_issues()
        issue = next((i for i in issues if i['id'] == issue_id), None)
        
        if not issue:
            return jsonify({'success': False, 'error': 'Issue not found'})
        
        if issue['status'] != 'In Progress':
            return jsonify({'success': False, 'error': 'Issue is not in progress'})
        
        current_time = datetime.now()
        issue['status'] = 'Completed'
        issue['end_time'] = current_time.isoformat()
        issue['end_date'] = current_time.strftime('%Y-%m-%d')
        issue['end_time_only'] = current_time.strftime('%H:%M:%S')
        issue['resolution_time'] = current_time.isoformat()
        issue['resolution_date'] = current_time.strftime('%Y-%m-%d')
        issue['resolution_notes'] = resolution_notes
        
        # Calculate total resolution time
        if issue['start_time']:
            try:
                start_dt = datetime.fromisoformat(issue['start_time'])
                end_dt = current_time
                resolution_duration = end_dt - start_dt
                
                # Convert to hours, minutes, seconds
                total_seconds = int(resolution_duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                
                issue['total_resolution_time'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except Exception as e:
                print(f"Error calculating resolution time: {e}")
                issue['total_resolution_time'] = 'N/A'
        
        if save_issues(issues):
            add_to_history(issue_id, 'Completed', f'Issue completed. Resolution: {resolution_notes}', performed_by)
            
            # Send completion email to client with comprehensive timing
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #28a745; text-align: center;">🎉 Issue Successfully Resolved!</h2>
                    <p>Dear {issue['client_name']},</p>
                    <p>Great news! Your issue has been successfully resolved by our technical team.</p>
                    
                    <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h3 style="margin: 0 0 10px 0; color: #155724;">✅ Resolution Summary:</h3>
                        <p><strong>Previous Status:</strong> In Progress</p>
                        <p><strong>Current Status:</strong> <span style="color: #28a745; font-weight: bold;">Completed</span></p>
                        <p><strong>Completed By:</strong> {performed_by}</p>
                        <p><strong>Completion Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #495057;">📋 Resolution Details:</h3>
                        <p style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">{resolution_notes}</p>
                    </div>
                    
                    {generate_comprehensive_timing_info(issue)}
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #495057;">📋 Original Issue Description:</h3>
                        <p style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #dee2e6;">{issue['issue_description']}</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #0c5460;">💬 Feedback & Support:</h3>
                        <p>We hope this resolution meets your expectations. If you have any questions about the solution or need further assistance, please don't hesitate to contact us.</p>
                        <p>For any new issues, please use our issue reporting system and we'll be happy to help you again.</p>
                    </div>
                    
                    <p>Thank you for your patience and for choosing TechFlow for your technical support needs.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        TechFlow Support Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            send_email(issue['email'], f"Issue Resolved - {issue['report_id']}", email_body, cc_emails=CC_EMAILS)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to complete issue'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/issues/<int:issue_id>/history')
@login_required
def get_issue_history(issue_id):
    try:
        history_file = 'issue_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            return jsonify(history.get(str(issue_id), []))
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/export')
@login_required
def export_issues():
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        issues = load_issues()
        df = pd.DataFrame(issues)
        
        # Create Excel file with multiple sheets
        filename = f"issues_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main issues sheet
            df.to_excel(writer, sheet_name='Issues', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Issues', 'Pending Issues', 'In Progress Issues', 'Completed Issues', 'High Priority Issues', 'Medium Priority Issues', 'Low Priority Issues'],
                'Count': [
                    len(issues),
                    len([i for i in issues if i['status'] == 'Pending']),
                    len([i for i in issues if i['status'] == 'In Progress']),
                    len([i for i in issues if i['status'] == 'Completed']),
                    len([i for i in issues if i['priority'] == 'High']),
                    len([i for i in issues if i['priority'] == 'Medium']),
                    len([i for i in issues if i['priority'] == 'Low'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # History sheet
            history_file = 'issue_history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                history_data = []
                for issue_id, entries in history.items():
                    for entry in entries:
                        history_data.append({
                            'Issue ID': issue_id,
                            'Timestamp': entry['timestamp'],
                            'Action': entry['action'],
                            'Description': entry['description'],
                            'Performed By': entry['performed_by']
                        })
                
                if history_data:
                    history_df = pd.DataFrame(history_data)
                    history_df.to_excel(writer, sheet_name='History', index=False)
        
        return send_file(filename, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/print')
@login_required
def print_issues():
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        issues = load_issues()
        print(f"\n=== ISSUES DATA ({len(issues)} total) ===")
        for issue in issues:
            print(f"\nIssue #{issue['report_id']}:")
            print(f"  Client: {issue['client_name']}")
            print(f"  Project: {issue['project']}")
            print(f"  Status: {issue['status']}")
            print(f"  Priority: {issue['priority']}")
            print(f"  Created: {issue['created_timestamp']}")
        
        return jsonify({'success': True, 'total_issues': len(issues)})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_data():
    if session.get('user_role') != 'tech_team':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        # Reset Excel file
        if os.path.exists(EXCEL_FILE):
            os.remove(EXCEL_FILE)
        
        # Reset history file
        history_file = 'issue_history.json'
        if os.path.exists(history_file):
            os.remove(history_file)
        
        # Clear uploads folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

# Email monitoring thread (simplified implementation)
def monitor_emails():
    """Monitor support email for new issues (runs in background)"""
    while True:
        try:
            # This is a simplified implementation
            # In production, you'd implement proper IMAP monitoring
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"Email monitoring error: {e}")
            time.sleep(60)

# Start email monitoring in background thread
email_thread = threading.Thread(target=monitor_emails, daemon=True)
email_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
