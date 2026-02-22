# CoachSystem (CMS)

CoachSystem is a lightweight, real-life tested backend system for tutors and teachers to manage students, homework, messaging, and server monitoring. Built with **Flask**, **Flask-SocketIO**, and a custom **CLib** library for clean separation of logic, this system is ready for production usage with minimal setup.

---

## Features

- **User Management**
  - Login as Teacher/Tutor
  - Create students and assign them to yourself
  - Reset password (partial functionality; see notes)

- **Homework Management**
  - Assign homework to students
  - View student homework submissions

- **Messaging**
  - Real-time messaging via Socket.IO
  - Handles multiple simultaneous sessions per user

- **Server Monitoring**
  - CPU, memory, disk, GPU usage
  - Admin panel view for system status

- **Theme Selection**
  - Light/Dark mode for user interface (partial functionality)

- **Secure Sessions**
  - CSRF protection enabled
  - Session lifetime: 30 minutes
  - HTTPOnly cookies for security

- **Rate Limiting**
  - 100 requests per minute per IP by default

---

## Under Development / Known Limitations

- Some features display **“Under Development”** in the UI
- Reset password inside "My Students" may not work in all cases
- Some pages marked as **Under Construction**
- Uses default admin credentials; no seeding required

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/CoachSystem.git
cd CoachSystem