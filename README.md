# Laboratory Schedule Management System

A comprehensive web application for managing laboratory schedules and lecture bookings, built with Python, Flask, and MongoDB.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas account)
- Git

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/samyabdellatif/labs.git
   cd labs
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure MongoDB connection**
   - Edit the `.env` file created by the setup script
   - Replace the MONGO_URI with your MongoDB connection string

4. **Activate virtual environment and run**
   ```bash
   # Windows
   venv\Scripts\activate
   python server.py
   
   # macOS/Linux
   source venv/bin/activate
   python server.py
   ```

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samyabdellatif/labs.git
   cd labs
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` with your configuration:
   ```env
   # MongoDB Connection String
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/classroomsDB
   
   # Flask Secret Key (generate a secure key)
   FLASK_SECRET_KEY=your-secret-key-here
   ```

   **For MongoDB Atlas:**
   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - Get your connection string from the Atlas dashboard
   - Replace `username:password` with your database credentials

   **For Local MongoDB:**
   ```env
   MONGO_URI=mongodb://localhost:27017/classroomsDB
   ```

5. **Run the application**
   ```bash
   python server.py
   ```

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Default login: username `admin`, password `password`

## 📁 Project Structure

```
labs/
├── server.py                 # Main Flask application
├── setup.py                 # Automated setup script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Environment variables (create this)
├── README.md                # This file
└── templates/               # HTML templates
    ├── base.html           # Base template with navigation
    ├── index.html          # Main schedule view
    ├── cpanel.html         # Control panel
    ├── login.html          # User login
    ├── about.html          # About page
    └── _lecture_form.html  # Lecture form partial
```

## 🛠️ Technologies Used

- **Backend**: Python 3.8+, Flask, PyMongo
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask sessions
- **Environment Management**: python-dotenv

## 📋 Features

- Multi-lab schedule management (6 laboratories)
- Weekly timetable with conflict detection
- User authentication and session management
- Real-time updates via AJAX
- Lecture creation and editing
- Password management
- Responsive design

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URI` | MongoDB connection string | Yes |
| `FLASK_SECRET_KEY` | Flask secret key for sessions | Yes |

### Database Collections

The application automatically creates these collections:

1. **users** - Authentication data
   - `username`: User identifier
   - `password`: User password
   - `role`: User role (admin/user)

2. **lectures** - Schedule data
   - `course`: Course name
   - `instructor`: Instructor name
   - `days`: Days of week (e.g., '123' = SUN,MON,TUE)
   - `starttime`: Start time (HH:MM format)
   - `endtime`: End time (HH:MM format)
   - `numberOfStudents`: Expected student count
   - `lab`: Laboratory number (1-6)

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```
   Could not connect to MongoDB: ...
   ```
   **Solution**: Check your `MONGO_URI` in `.env` file. Ensure MongoDB is running and accessible.

2. **Module Not Found Error**
   ```
   ModuleNotFoundError: No module named 'flask'
   ```
   **Solution**: Activate virtual environment and install dependencies:
   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Permission Denied Error**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Ensure you have proper permissions or run with administrator privileges.

4. **Port Already in Use**
   ```
   Address already in use
   ```
   **Solution**: Change the port in `server.py` or kill the existing process:
   ```bash
   # Find and kill process on port 5000 (Windows)
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

### Development Tips

1. **Debug Mode**: The app runs in debug mode by default. Disable for production:
   ```python
   labapp.run(debug=False, port=5000)
   ```

2. **Database Reset**: To clear all data, connect to MongoDB and drop the collections:
   ```javascript
   // In MongoDB shell
   use classroomsDB
   db.users.drop()
   db.lectures.drop()
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes. Feel free to use, modify, and distribute.

## 👤 Author

**Samy Abdellatif**

## 📚 Learning Objectives

This project demonstrates:
- Full-stack web development with Python and Flask
- NoSQL database integration with MongoDB
- RESTful API design and implementation
- Frontend-backend communication with AJAX
- User authentication and session management
- Form validation and error handling
- Responsive web design principles
- Modern JavaScript and DOM manipulation

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify your `.env` configuration
4. Make sure MongoDB is accessible
5. Check the Flask application logs for specific error messages
