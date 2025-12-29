<div align="center">

# 🎓 Classroom Schedule Management System

### A modern web application for managing classroom schedules and lecture bookings

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

A comprehensive full-stack web application designed for educational institutions to efficiently manage classroom schedules and lecture bookings. Built with modern technologies including Python, Flask, and MongoDB, this system provides an intuitive interface for scheduling, conflict detection, and real-time updates.

**Perfect for:** Universities, colleges, training centers, and educational institutions managing multiple classrooms and lecture schedules.

## ✨ Features

### Core Functionality
- 📅 **Multi-Classroom Management** - Manage schedules for up to 6 classrooms simultaneously
- 🔍 **Intelligent Conflict Detection** - Automatic detection of scheduling conflicts
- 👥 **User Authentication** - Secure login system with session management
- ⚡ **Real-time Updates** - AJAX-powered interface for seamless user experience
- 📝 **Lecture CRUD Operations** - Create, read, update, and delete lectures easily
- 🔐 **Password Management** - User-friendly password change functionality
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices

### Advanced Features
- ⚙️ **Configurable Weekdays** - Switch between Sun-Thu and Mon-Fri schedules
- 🎨 **Interactive UI** - Click-to-edit schedule cells with modal forms
- 📊 **Visual Schedule Grid** - Clear, color-coded timetable view
- 🔄 **Dynamic Day Mapping** - Automatic adaptation to selected weekday configuration

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python** 3.8 or higher ([Download](https://www.python.org/downloads/))
- **MongoDB** Atlas account or local installation ([Setup Atlas](https://www.mongodb.com/cloud/atlas))
- **Git** ([Download](https://git-scm.com/downloads))

### Installation

#### Method 1: Automated Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/samyabdellatif/labs.git
cd labs

# 2. Run automated setup
python setup.py

# 3. Configure your MongoDB connection
# Edit .env file and update MONGO_URI

# 4. Start the application
# Windows
venv\Scripts\activate
python server.py

# macOS/Linux
source venv/bin/activate
python server.py
```

#### Method 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/samyabdellatif/labs.git
cd labs

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
# Edit .env and add your MongoDB connection string

# 6. Run the application
python server.py
```

### Configuration

Create a `.env` file in the project root:

```env
# MongoDB Connection (Atlas or Local)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/classroomsDB

# Flask Security
FLASK_SECRET_KEY=your-secure-random-secret-key-here
```

**MongoDB Atlas Setup:**
1. Create free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get connection string from dashboard
4. Replace credentials in MONGO_URI

**Local MongoDB:**
```env
MONGO_URI=mongodb://localhost:27017/classroomsDB
```

### First Run

1. Open browser and navigate to `http://127.0.0.1:5000`
2. Login with default credentials:
   - **Username:** `admin`
   - **Password:** `password`
3. ⚠️ **Important:** Change default password immediately via Control Panel

## 📁 Project Structure

```
labs/
├── 📄 server.py              # Flask application & routes
├── 📄 setup.py               # Automated setup script
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env.example           # Environment template
├── 📄 .env                   # Your configuration (create this)
├── 📄 README.md              # Documentation
└── 📁 templates/             # HTML templates
    ├── base.html             # Base layout & navigation
    ├── index.html            # Schedule view
    ├── cpanel.html           # Control panel
    ├── login.html            # Authentication
    ├── about.html            # About page
    └── _lecture_form.html    # Lecture form modal
```

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.8+, Flask 3.0+, PyMongo |
| **Database** | MongoDB (Atlas/Local) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Authentication** | Flask Sessions |
| **Environment** | python-dotenv |

## 📚 Documentation

### Database Schema

#### Collections

**1. users** - User authentication
```javascript
{
  username: String,    // Unique identifier
  password: String,    // Plaintext (consider hashing for production)
  role: String         // "admin" or "user"
}
```

**2. classroom** - Lecture schedules
```javascript
{
  course: String,           // Course name
  instructor: String,       // Instructor name
  days: String,            // Day codes e.g., "135" (SUN, TUE, THU)
  starttime: String,       // Format "HH:MM"
  endtime: String,         // Format "HH:MM"
  numberOfStudents: Number, // Expected attendance
  classroom: String        // Classroom number "1" to "6"
}
```

**3. settings** - Global configuration
```javascript
{
  _id: "global",
  weekdays: String  // "sun-thu" or "mon-fri"
}
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page (schedule view) |
| `GET` | `/index?classroom=N` | View specific classroom |
| `GET` | `/cpanel` | Control panel |
| `GET` | `/login` | Login page |
| `POST` | `/login` | Authenticate user |
| `GET` | `/logout` | End session |
| `GET` | `/about` | About page |
| `GET` | `/get_lecture` | Fetch lecture details |
| `GET` | `/lectures?classroom=N` | Get all lectures for classroom |
| `POST` | `/insert_lecture` | Create new lecture |
| `POST` | `/update_lecture` | Update existing lecture |
| `POST` | `/change_password` | Change user password |
| `POST` | `/update_settings` | Update global settings |

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MONGO_URI` | MongoDB connection string | ✅ Yes | - |
| `FLASK_SECRET_KEY` | Session encryption key | ✅ Yes | `change-this-secret` |

## 🐛 Troubleshooting

<details>
<summary><b>MongoDB Connection Error</b></summary>

**Problem:** `Could not connect to MongoDB`

**Solutions:**
- Verify `MONGO_URI` in `.env` file
- Check MongoDB Atlas network access (whitelist your IP)
- Ensure database user credentials are correct
- For local MongoDB, confirm service is running
</details>

<details>
<summary><b>Module Not Found Error</b></summary>

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Port Already in Use</b></summary>

**Problem:** `Address already in use`

**Solutions:**

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

**Or change port in `server.py`:**
```python
app.run(debug=True, port=5001)
```
</details>

<details>
<summary><b>Permission Denied Error</b></summary>

**Problem:** `PermissionError: [Errno 13]`

**Solutions:**
- Run terminal as administrator (Windows)
- Check file/folder permissions
- Ensure virtual environment is activated
</details>

## 💡 Usage Tips

### For Development
```python
# In server.py, enable debug mode
app.run(debug=True, port=5000)
```

### For Production
```python
# Disable debug mode and use production server
app.run(debug=False, host='0.0.0.0', port=5000)

# Better yet, use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Database Management
```javascript
// MongoDB Shell - Reset database
use classroomsDB
db.users.drop()
db.classroom.drop()
db.settings.drop()

// Or reset via Mongo Compass/Atlas UI
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add comments for complex logic
- Test your changes thoroughly

## 📄 License

This project is created for **educational purposes**. Feel free to use, modify, and distribute for learning and teaching.

## 👤 Author

**Samy Abdellatif**
- 📧 Email: Contact via GitHub
- 🔗 GitHub: [@samyabdellatif](https://github.com/samyabdellatif)

## 🎯 Learning Objectives

This project demonstrates real-world concepts:

- ✅ Full-stack web development with Python & Flask
- ✅ NoSQL database design with MongoDB
- ✅ RESTful API patterns
- ✅ AJAX for dynamic updates
- ✅ User authentication & session management
- ✅ Form validation & error handling
- ✅ Responsive web design
- ✅ MVC architecture patterns
- ✅ Environment configuration management
- ✅ Git version control

## 🙏 Acknowledgments

Built as a training project to demonstrate modern web development practices and educational software design.

## 📞 Support

Need help? Here's what to check:

1. ✅ Review the [Troubleshooting](#-troubleshooting) section
2. ✅ Verify all dependencies are installed
3. ✅ Check `.env` configuration
4. ✅ Ensure MongoDB is accessible
5. ✅ Review Flask logs for error details

---

<div align="center">

**Made with ❤️ for education**

[⬆ Back to Top](#-classroom-schedule-management-system)

</div>
