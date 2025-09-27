# MindWell - Mental Health Support Platform

A comprehensive mental health support platform featuring AI-powered chat, self-assessment tools, appointment management, and wellness resources.

## 🚀 Features

### ✅ Implemented

#### **User Authentication System**
- User registration with email validation
- Secure login with JWT tokens
- Password hashing with bcrypt
- Role-based access (Student, Faculty, Staff, Counselor)
- Session management
- User profile management

#### **AI-Powered Mental Health Chat**
- Intelligent chatbot for mental health support
- Context-aware responses
- Real-time conversation interface
- Personalized recommendations

#### **Self-Assessment Tools**
- **PHQ-9 Depression Screening** (9-question standardized assessment)
- **GAD-7 Anxiety Screening** (7-question standardized assessment)
- Automatic scoring and severity classification
- Personalized recommendations based on results
- Assessment history tracking
- Results download functionality
- Crisis intervention for severe scores

#### **Appointment Management System**
- **User Features:**
  - Modern appointment booking interface with step-by-step process
  - Calendar integration with available date selection
  - Real-time time slot availability checking
  - Concern type selection and notes
  - User appointment dashboard with status tracking
  - Appointment filtering and search
  - Cancel appointments functionality
  
- **Counselor Features:**
  - Comprehensive counselor dashboard
  - Appointment statistics and analytics
  - Bulk time slot creation
  - Appointment status management (confirm/cancel/complete)
  - Client information management
  - Professional interface design

#### **Community Forum**
- Anonymous peer support forum
- Create and view forum posts
- Like and comment system
- Post categorization
- Real-time updates
- User authentication integration

#### **Wellness Resources**
- **5-Minute Wellness Challenges**
  - Guided meditation exercises
  - Breathing techniques
  - Gratitude journaling
  - Progress tracking with local storage
  - Interactive timers and counters
- Psychoeducational content
- Professional resource recommendations

#### **Responsive Web Interface**
- Modern, mobile-friendly design
- Bootstrap 5-based UI components
- Interactive forms and modals
- Real-time form validation
- Smooth animations and transitions
- Professional color scheme and typography

### 🚧 In Progress / Planned

#### **Advanced Analytics**
- Assessment trend analysis
- Progress tracking over time
- Data visualization dashboards
- Export functionality for reports

#### **Additional Assessment Tools**
- Stress assessment scales (PSS)
- Sleep quality assessments (PSQI)
- Burnout screening tools (MBI)
- Substance use screenings

#### **Enhanced AI Features**
- Personalized wellness recommendations
- Mood tracking integration
- Crisis detection algorithms
- Sentiment analysis for forum posts
- Automated resource suggestions

#### **Mobile Application**
- Native mobile app development
- Push notifications for appointments
- Offline assessment capabilities
- Mobile-optimized interfaces

#### **Advanced Appointment Features**
- Video conferencing integration
- Automated reminder system
- Calendar synchronization
- Waitlist management
- Multi-counselor scheduling

#### **Administrative Features**
- Admin dashboard for platform management
- User management system
- Content management for resources
- Analytics and reporting tools
- System configuration management

## 🛠️ Technical Stack

### Backend
- **Python** with FastAPI framework
- **SQLAlchemy** for database ORM
- **SQLite** database (PostgreSQL ready)
- **JWT** authentication
- **BCrypt** password hashing
- **Pydantic** for data validation

### Frontend
- **HTML5** with modern CSS3
- **Bootstrap 5** for responsive design
- **Vanilla JavaScript** for interactivity
- **AJAX** for API communication

### AI Integration
- **OpenAI API** for chat functionality
- **Context-aware** conversation management

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser
- OpenAI API key (for AI chat functionality)

## 🚀 Quick Start

1. **Clone and setup** (Steps 1-4 above)
2. **Create admin user**: Register with `admin@example.com` and `Admin@1234`
3. **Login**: Go to `http://localhost:8000/login.html`
4. **Explore features**: Try assessments, AI chat, appointments, and forum

## 🔧 Troubleshooting

### Common Issues

**Server won't start:**
- Check Python version: `python --version` (must be 3.8+)
- Ensure virtual environment is activated
- Check port 8000 is not in use: `netstat -an | findstr 8000`

**Database errors:**
- Delete `mindwell.db` file and restart server to recreate database
- Check file permissions in the project directory

**AI Chat not working:**
- Verify `OPENAI_API_KEY` is set in `.env` file
- Check API key is valid and has available credits

**Forum categories empty:**
- Login as admin user
- Navigate to forum and create categories
- Or use API endpoint to create categories

**Authentication issues:**
- Clear browser cookies and local storage
- Check JWT token expiration
- Verify user role permissions

### Getting Help
- Check browser console for JavaScript errors
- Check terminal for server error messages
- Verify API endpoints are accessible: `http://localhost:8000/api/health`

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mindwell-main
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./mindwell.db
OPENAI_API_KEY=your-openai-api-key-here
```

**Required Environment Variables:**
- `SECRET_KEY`: A secure random string for JWT token encryption (minimum 32 characters recommended)
- `DATABASE_URL`: Database connection string (SQLite for development, PostgreSQL for production)
- `OPENAI_API_KEY`: Your OpenAI API key for AI chat functionality

**Example .env configuration:**
```
SECRET_KEY=your-super-secret-jwt-key-at-least-32-characters-long
DATABASE_URL=sqlite:///./mindwell.db
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Note**: The SQLite database will be created automatically when you first run the application. For production, consider using PostgreSQL.

### 5. Database Initialization
The database tables are automatically created when you run the application for the first time. The SQLite database file (`mindwell.db`) will be created automatically.

### 6. Create Default Admin User
To create an admin user for managing the platform, use the following credentials when registering:
- **Email**: `admin@example.com`
- **Password**: `Admin@1234`
- **Role**: Select "Admin" during registration

### 7. Create Test Users (Optional)
For testing purposes, you can create these test users:

**Test User 1 (Student)**
- **Email**: `test1@example.com`
- **Password**: `Test@1234`
- **Role**: Student

**Test User 2 (Faculty)**
- **Email**: `test2@example.com`
- **Password**: `Test@1234`
- **Role**: Faculty

**Test User 3 (Staff)**
- **Email**: `test3@example.com`
- **Password**: `Test@1234`
- **Role**: Staff

**Test User 4 (Counselor)**
- **Email**: `test4@example.com`
- **Password**: `Test@1234`
- **Role**: Counselor

### 8. Initialize Forum Categories (Admin Only)
After creating the admin user, log in and navigate to the forum section. The admin can create default forum categories such as:
- Anxiety Support
- Depression Support
- Stress Management
- Academic Support
- Relationships

### 9. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:8000`

**Alternative**: For better development experience with auto-reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📁 Project Structure

```
mindwell-main/
├── main.py                    # FastAPI application entry point
├── models.py                  # SQLAlchemy database models
├── schemas.py                 # Pydantic data validation schemas
├── auth.py                    # Authentication utilities (JWT, password hashing)
├── assessment_utils.py        # Assessment scoring and recommendation logic
├── ai_service.py              # AI chat service integration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment configuration template
├── index.html                 # Main application page
├── login.html                 # User login page
├── signup.html                # User registration page
├── appointment.html           # Appointment booking page
├── appointments.html          # User appointment management
├── counselor_appointments.html # Counselor appointment dashboard
├── forum.html                 # Community forum page
├── post.html                  # Individual forum post page
├── wellness_challanges.html   # Wellness challenges page
├── ai-chat.js                 # AI chat functionality
├── assessment.js              # Assessment functionality
└── venv/                      # Python virtual environment
```

## 🔑 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/me` - Get current user info

### Assessments
- `GET /api/assessment/questions/{type}` - Get assessment questions (PHQ-9/GAD-7)
- `POST /api/assessment/submit` - Submit assessment responses
- `GET /api/assessment/history` - Get user's assessment history
- `GET /api/assessment/results/{id}` - Get specific assessment results

### AI Chat
- `POST /api/chat` - Send message to AI chatbot
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions` - Get user's chat sessions

### Forum
- `GET /api/forum/posts` - Get all forum posts
- `POST /api/forum/posts` - Create new forum post
- `GET /api/forum/posts/{id}` - Get specific post with comments
- `POST /api/forum/posts/{id}/like` - Like/unlike a post
- `POST /api/forum/posts/{id}/comments` - Add comment to post
- `POST /api/forum/comments/{id}/like` - Like/unlike a comment

### Appointment Management
- `GET /api/appointments/slots` - Get available time slots
- `POST /api/appointments/book` - Book new appointment
- `GET /api/appointments/user` - Get user's appointments
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

### Counselor Features
- `GET /api/appointments/counselor` - Get counselor appointments
- `POST /api/appointments/slots` - Bulk create time slots
- `PUT /api/appointments/{id}/status` - Update appointment status

### System
- `GET /api/health` - Health check endpoint

## 🧪 Testing the Application

### Using Pre-configured Test Accounts

**Admin Account** (Full access to all features)
- **Email**: `admin@mindwell.com`
- **Password**: `Admin@1234`
- **Access**: All features including forum management

**Test User Accounts** (Different roles for testing)
- **Student**: `test1@example.com` / `Test@1234`
- **Faculty**: `test2@example.com` / `Test@1234`
- **Staff**: `test3@example.com` / `Test@1234`
- **Counselor**: `test4@example.com` / `Test@1234`

### Manual User Registration
1. Navigate to `http://localhost:8000/signup.html`
2. Fill in registration form with valid details
3. Submit to create account
4. Use email and password to login

### Taking Assessments
1. Login to the application
2. Navigate to Self-Assessment section
3. Click "Start Assessment" for PHQ-9 or GAD-7
4. Complete all questions
5. View results and recommendations

### AI Chat
1. Login to the application
2. Use the chat interface on the main page
3. Type mental health related questions

### Booking Appointments
1. Login to the application
2. Click "Book Appointment" in navigation
3. Select preferred date from calendar
4. Choose available time slot
5. Select concern type and add notes
6. Confirm appointment booking

### Managing Appointments (Users)
1. Login to the application
2. Click username dropdown and select "My Appointments"
3. View all your appointments with status
4. Filter by status (pending, confirmed, cancelled, completed)
5. Cancel appointments if needed

### Counselor Dashboard
1. Login as counselor (requires counselor role)
2. Navigate to counselor dashboard
3. View appointment statistics
4. Manage appointment statuses
5. Add bulk time slots

### Community Forum
1. **Admin Setup** (First time only):
   - Login as admin (`admin@example.com` / `Admin@1234`)
   - Navigate to "Community Forum"
   - Create default categories: Anxiety Support, Depression Support, Stress Management, Academic Support, Relationships
   
2. **User Features**:
   - Login to the application
   - Navigate to "Community Forum"
   - View existing posts
   - Create new posts in available categories
   - Like posts and add comments
   - Interact with peer support

### Wellness Challenges
1. Navigate to "Wellness Challenges"
2. Choose from meditation, breathing, or gratitude exercises
3. Follow guided instructions
4. Track progress with built-in timers
5. Complete daily challenges

## 🔒 Security Features

- Password complexity requirements (8+ characters, uppercase, lowercase, number, special character)
- JWT token-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Secure session management

## 🚨 Crisis Support

The application includes automatic crisis detection for severe assessment scores:
- Immediate crisis resource recommendations
- Emergency contact information
- Professional help guidance

## 📊 Implementation Summary

### ✅ Fully Implemented & Functional
- **Complete User Authentication System** with role-based access
- **PHQ-9 & GAD-7 Assessments** with scoring and recommendations
- **AI-Powered Chat System** with context-aware responses
- **Appointment Booking System** with real-time availability
- **User Appointment Management** with status tracking
- **Counselor Dashboard** with appointment management tools
- **Community Forum** with posts, comments, and likes
- **Wellness Challenges** with guided exercises and progress tracking
- **Responsive Design** across all pages
- **Complete API Backend** with all necessary endpoints

### 🔄 Partially Implemented
- **Advanced Analytics** - Basic structure in place, needs enhancement
- **Mobile Optimization** - Responsive design complete, native app pending
- **Notification System** - Framework ready, needs integration

### ❌ Not Yet Implemented
- **Video Conferencing** for appointments
- **Automated Email Notifications** 
- **Advanced Reporting Dashboard**
- **Mobile Native Applications**
- **Third-party Calendar Integration**

## 🎯 Next Steps

1. **Testing & Quality Assurance**
   - Comprehensive testing of all features
   - Performance optimization
   - Security audit

2. **User Experience Enhancement**
   - Mobile app development
   - Push notification system
   - Advanced analytics dashboard

3. **Advanced Features**
   - Video conferencing integration
   - Automated reminder system
   - Advanced reporting tools

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

## 🤝 Contributing

We welcome contributions to MindWell! Please see our contributing guidelines for more information on how to get involved in improving mental health support through technology.
- Check the documentation
- Review API endpoints
- Contact development team

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📊 Assessment Scoring Reference

### PHQ-9 Depression Scale
- **0-4**: Minimal depression
- **5-9**: Mild depression
- **10-14**: Moderate depression
- **15-19**: Moderately severe depression
- **20-27**: Severe depression

### GAD-7 Anxiety Scale
- **0-4**: Minimal anxiety
- **5-9**: Mild anxiety
- **10-14**: Moderate anxiety
- **15-21**: Severe anxiety

---

**Note**: This application is for educational and support purposes. It does not replace professional mental health care. Users with concerning scores are encouraged to seek professional help.