# eLearning Platform

A comprehensive eLearning web application built with Django, featuring real-time chat, course management, and user authentication.

## Features

### User Management
- **Two User Types**: Students and Teachers with different permissions
- **User Profiles**: Complete user profiles with photos, bios, and personal information
- **Status Updates**: Students can post status updates on their home pages
- **User Search**: Teachers can search for students and other teachers
- **Student Management**: Teachers can block, unblock, and remove students
- **Notification System**: Real-time notifications for enrollments, materials, and actions

### Course Management
- **Course Creation**: Teachers can create and manage courses
- **Course Enrollment**: Students can browse and enroll in available courses
- **Course Materials**: Teachers can upload various types of materials (PDFs, images, videos, documents)
- **Assignments**: Course assignments with due dates
- **Course Feedback**: Students can leave ratings and feedback for courses
- **Course Deletion**: Teachers can delete their own courses

### Real-time Communication
- **WebSocket Chat**: Real-time text chat between users
- **Chat Rooms**: Multiple chat rooms for different discussions
- **Participant Management**: Users can join and leave chat rooms
- **Chat Room Deletion**: Room creators can delete their chat rooms

### REST API
- **User API**: RESTful endpoints for user data
- **Authentication**: Session-based authentication
- **Permissions**: Role-based access control

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (can be configured for PostgreSQL/MySQL)
- **Real-time**: Django Channels with Redis
- **Frontend**: Tailwind CSS, Font Awesome
- **API**: Django REST Framework
- **Background Tasks**: Celery with Redis
- **File Uploads**: Django's built-in file handling
- **Server**: Daphne (ASGI server for WebSocket support)

## Installation

### Prerequisites
- Python 3.8+
- Redis server
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ADWD_finals
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv adwd_finals
   source adwd_finals/bin/activate  # On Windows: adwd_finals\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Start Redis server** (in a separate terminal)
   ```bash
   redis-server
   ```

9. **Run the ASGI server with Daphne** (for WebSocket support)
   ```bash
   daphne -b 127.0.0.1 -p 8001 elearning.asgi:application
   ```

10. **Access the application**
    - Main application: http://127.0.0.1:8001
    - Admin interface: http://127.0.0.1:8001/admin

## Demo Users

### Admin User
- Username: admin
- Password: admin123

### Teacher User
- Username: teacher1
- Password: teacher123

### Student Users
- Username: student1
- Password: student123
- Username: student2
- Password: student123

## Usage

### For Teachers
1. **Login** with teacher credentials
2. **Create Courses** using the "Create Course" button
3. **Upload Materials** to your courses
4. **View Students** enrolled in your courses
5. **Search Users** to find students and other teachers
6. **Manage Students** - block, unblock, or remove students
7. **Join Chat Rooms** for real-time communication
8. **Delete Courses** you've created

### For Students
1. **Register** or login with student credentials
2. **Browse Courses** available for enrollment
3. **Enroll in Courses** that interest you
4. **Download Materials** from enrolled courses
5. **Leave Feedback** for completed courses
6. **Post Status Updates** on your profile
7. **Join Chat Rooms** to communicate with others
8. **View Notifications** for course updates and actions

## API Endpoints

### User API
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get specific user details

### Authentication Required
All API endpoints require authentication. Use session authentication for web requests.

## WebSocket Chat

The application includes real-time chat functionality using WebSockets:

1. **Create Chat Room**: Navigate to Chat → Create Room
2. **Join Chat Room**: Click on any available chat room
3. **Real-time Messaging**: Messages appear instantly for all participants
4. **Participant List**: See who's currently in the chat room
5. **Delete Chat Room**: Room creators can delete their rooms

## File Structure

```
ADWD_finals/
├── elearning/              # Main project settings
├── users/                  # User management app
├── courses/                # Course management app
├── chat/                   # Real-time chat app
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS)
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── README.md              # This file
```

## Database Models

### Users App
- **User**: Custom user model with student/teacher types
- **StatusUpdate**: User status updates
- **UserProfile**: Extended user profile information
- **Notification**: Real-time notification system

### Courses App
- **Course**: Course information and metadata
- **CourseMaterial**: Uploaded course materials
- **Enrollment**: Student-course relationships
- **Assignment**: Course assignments with due dates
- **Feedback**: Student course feedback and ratings

### Chat App
- **ChatRoom**: Chat room information
- **Message**: Individual chat messages

## Testing

Run the test suite:
```bash
python manage.py test
```

## Important Notes

### WebSocket Support
- **Daphne server is required** for WebSocket functionality
- **Regular Django runserver** will not support real-time chat
- **Redis must be running** for WebSocket connections

### Static Files
- Run `python manage.py collectstatic --noinput` before starting the server
- Static files are served from the `staticfiles/` directory

### Development vs Production
- **Development**: Use Daphne with Redis for full functionality
- **Production**: Configure proper ASGI server (Daphne/Uvicorn) with Redis

## Deployment

For production deployment:

1. **Set DEBUG=False** in settings
2. **Configure a production database** (PostgreSQL recommended)
3. **Set up static file serving** (nginx + collectstatic)
4. **Configure Redis** for production
5. **Set up SSL certificates** for HTTPS
6. **Configure environment variables** for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
