# Whispersphere

<div align="center">
  <h1>Whispersphere</h1>
  <p>A real-time chat application built with Django and Channels</p>
</div>

## Features

- **User Authentication**: Secure login with email/password and Google social login
- **Chat Rooms**: Create, update, and delete chat rooms with topics
- **Real-time Messaging**: Instant messaging using WebSockets
- **User Profiles**: Customizable profiles with avatars and bios
- **Search Functionality**: Search across rooms and messages
- **Activity Feed**: View recent messages and activities
- **Topic Management**: Organize rooms by topics
- **Responsive Design**: Works seamlessly across devices

## Technology Stack

- **Backend**: Django 5.0.1, Django REST Framework
- **Real-time**: Django Channels, WebSockets
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Authentication**: Django Allauth with Google OAuth
- **Frontend**: HTML, CSS, JavaScript
- **Other**: Redis (for channel layers in production)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/solvibrain/whispersphere
   cd whispersphere
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   DJANGO_SECRET_KEY=your_secret_key
   DEBUG=True
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at `http://127.0.0.1:8000/`

## Usage

1. **Register/Login**: Use email/password or Google account to authenticate
2. **Create Rooms**: Create new chat rooms with topics
3. **Join Rooms**: Participate in existing chat rooms
4. **Real-time Chat**: Send and receive messages instantly
5. **Manage Profile**: Update your profile information and avatar
6. **Search**: Find rooms and messages using the search functionality
7. **Activity Feed**: View recent activities across the platform

## Configuration

For production deployment, configure the following in `settings.py`:

- Set `DEBUG = False`
- Configure database settings for PostgreSQL
- Set up Redis for channel layers
- Configure allowed hosts and security settings
- Set up static files collection and serving

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

For any inquiries, please contact [Your Name](mailto:your.email@example.com)

---

**Note**: This is a comprehensive README file that covers all aspects of the Whispersphere project. It includes detailed installation instructions, feature descriptions, and contribution guidelines.
