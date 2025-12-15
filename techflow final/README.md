# TechFlow - Enhanced Issue Tracking System

A comprehensive web-based issue tracking system for PGS/PMS projects with professional UI, Excel-based storage, and automated email notifications.

## 🚀 Features

### Core Functionality
- **Multi-Channel Issue Intake**: Web portal, email, and manual entry
- **Role-Based Access**: Separate dashboards for clients and technical teams
- **Real-Time Tracking**: Status updates with automated email notifications
- **Image Attachments**: Support for multiple image uploads (up to 10 images, 5MB each)
- **Excel Export**: Complete issue history and reporting in Excel format
- **Professional UI**: Modern, responsive design with smooth animations

### User Roles
1. **Client/Operator**: Report issues and track progress
2. **Technical Team**: Manage, assign, and resolve issues
3. **Manager**: Oversee all operations and generate reports

### Issue Workflow
1. **Report**: Client submits issue via web form
2. **Triage**: Manager sets priority and tech level
3. **Assignment**: Automatic assignment based on project and level
4. **Resolution**: Technical team works and marks complete
5. **Notification**: Automated emails at each stage

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3+
- pandas 2.1.1+
- openpyxl 3.1.2+
- Modern web browser

## 🛠️ Installation

### 1. Clone or Download
```bash
# If using git
git clone <repository-url>
cd techflow-issue-tracker

# Or extract downloaded files to a directory
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Email Settings (Optional)
Edit `app.py` and update email configuration:
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
SUPPORT_EMAIL = "support@company.com"
```

### 4. Create Upload Directory
```bash
mkdir static/uploads
```

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Production Mode
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or using Flask's built-in server (not recommended for production)
export FLASK_ENV=production
python app.py
```

## 👥 Default Login Credentials

### Technical Team
- **Username**: `admin`
- **Password**: `password123`
- **Role**: `tech_team`

### Client Access
- **Username**: Any username
- **Password**: Any password
- **Role**: `client`

## 📁 Project Structure

```
techflow-issue-tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── styles.css        # Main CSS styles
│   ├── optimized.js      # JavaScript functionality
│   └── uploads/          # Image upload directory
├── templates/
│   ├── base.html         # Base template
│   ├── client.html       # Issue reporting form
│   ├── login.html        # Login page
│   ├── dashboard.html    # Technical team dashboard
│   └── client_dashboard.html # Client dashboard
├── issues_data.xlsx      # Excel data storage (auto-created)
└── issue_history.json    # Issue history log (auto-created)
```

## 🔧 Configuration

### Email Setup
For email notifications to work, configure SMTP settings in `app.py`:

1. **Gmail Setup**:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the app password in `EMAIL_PASSWORD`

2. **Other Email Providers**:
   - Update `SMTP_SERVER` and `SMTP_PORT`
   - Use appropriate credentials

### File Upload Limits
- Maximum 10 images per issue
- Maximum 5MB per image
- Supported formats: PNG, JPG, JPEG, GIF, WEBP

## 📊 Data Management

### Excel Export
- Click "Export Excel" in the technical dashboard
- Generates comprehensive report with multiple sheets:
  - Issues: All issue data
  - Summary: Statistical overview
  - History: Complete audit trail

### Data Reset
- Click "Reset Data" in the technical dashboard
- **Warning**: This permanently deletes all data
- Use with caution in production

## 🎨 Customization

### Styling
- Edit `static/styles.css` for visual customization
- Uses CSS variables for easy color scheme changes
- Responsive design for mobile and desktop

### Functionality
- Modify `static/optimized.js` for JavaScript enhancements
- Add new features in `app.py` routes
- Extend templates in `templates/` directory

## 🔒 Security Considerations

### Production Deployment
1. Change `app.secret_key` to a secure random string
2. Use environment variables for sensitive configuration
3. Implement proper user authentication
4. Use HTTPS in production
5. Set up proper file permissions

### Example Production Config
```python
import os
app.secret_key = os.environ.get('SECRET_KEY', 'your-secure-secret-key')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🐛 Troubleshooting

### Common Issues

1. **Images not uploading**:
   - Check file size (must be < 5MB)
   - Verify file format (PNG, JPG, JPEG, GIF, WEBP)
   - Ensure `static/uploads/` directory exists

2. **Email not sending**:
   - Verify SMTP credentials
   - Check firewall settings
   - Ensure 2FA is enabled for Gmail

3. **Excel export fails**:
   - Check file permissions
   - Ensure `openpyxl` is installed
   - Verify sufficient disk space

### Logs
Check console output for error messages. In production, configure proper logging.

## 🔄 Updates and Maintenance

### Regular Maintenance
1. Backup `issues_data.xlsx` and `issue_history.json`
2. Monitor disk space for uploads
3. Review email logs
4. Update dependencies regularly

### Data Backup
```bash
# Backup data files
cp issues_data.xlsx backup_issues_$(date +%Y%m%d).xlsx
cp issue_history.json backup_history_$(date +%Y%m%d).json

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz static/uploads/
```

## 📞 Support

For technical support or feature requests:
1. Check this README for common solutions
2. Review the code comments in `app.py`
3. Check browser console for JavaScript errors
4. Verify all dependencies are installed correctly

## 📄 License

This project is provided as-is for educational and business use. Please ensure compliance with your organization's policies when deploying.

## 🎯 Future Enhancements

Potential improvements for future versions:
- Database integration (PostgreSQL, MySQL)
- Advanced reporting and analytics
- API endpoints for external integrations
- Mobile app development
- Advanced user management
- Integration with external ticketing systems
- Automated email parsing from support inbox
- Real-time notifications via WebSocket
- Advanced search and filtering
- Bulk operations
- Custom workflows and automation

---

**TechFlow Issue Tracking System** - Professional issue management for PGS/PMS projects.
