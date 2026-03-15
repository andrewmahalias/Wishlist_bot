# Wishlist Bot 🎁

A Telegram bot for managing family wishlists with PostgreSQL backend and async architecture.

## Features

- **Family Management**: Create families and invite members using unique invite codes
- **Wishlist Management**: Add, edit, delete, and view wishes with titles, descriptions, links, and prices
- **User Authentication**: Automatic user registration via Telegram
- **Deep Link Support**: Join families directly from invite links
- **Multi-family Support**: Participate in multiple family groups

## Tech Stack

- **Bot Framework**: [aiogram](https://aiogram.dev/) 3.22.0
- **Database**: SQLAlchemy 2.0.44 with PostgreSQL
- **State Management**: aiogram FSM
- **Environment**: python-dotenv

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Telegram Bot Token

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd wishlist_bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

2. **Database setup**
```bash
# Create database
createdb wishlist_db

# Or with custom user
sudo -u postgres createuser --interactive wishlist_user
sudo -u postgres createdb -O wishlist_user wishlist_db
```

3. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run migrations and start**
```bash
alembic upgrade head
python app/main.py
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
# Bot configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_telegram_id

# PostgreSQL
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=your_db_name
```

The `DATABASE_URL` is automatically constructed from PostgreSQL variables.

## Usage

### Bot Commands
- `/start` - Initialize bot and show main menu
- `/start join_INVITE_CODE` - Join family using invite code
- `/support` - Contact support team

### Main Workflows
1. **Family Management**: `/start` → "Сім'я" 🏠 → "Створити сім'ю"
2. **Join Family**: Use invite code or deep link
3. **Manage Wishes**: Family menu → "Мої бажання" → Add/Edit/Delete wishes
4. **View Wishes**: Family menu → "Бажання сім'ї"

## Project Structure

```
wishlist_bot/
├── app/
│   ├── handlers/          # Telegram handlers
│   ├── models/            # SQLAlchemy models
│   ├── database/          # Database configuration
│   ├── crud/              # Database operations
│   ├── services/          # Business logic
│   ├── keyboards/         # Telegram keyboards
│   ├── states/            # FSM states
│   ├── middlewares/       # Bot middlewares
│   └── utils/             # Utilities
├── alembic/               # Database migrations
├── tests/                 # Test suite
└── requirements.txt       # Dependencies
```

## Database Schema

```
Users ←→ Family_Members ←→ Families
  ↓                           ↓
  Wishes ←─────────────────────┘
```

### Models
- **User**: telegram_id, name, created_at
- **Family**: name, invite_code, created_at
- **Wish**: title, description, link, price, status, user_id, family_id

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```


## Deployment

### Docker
```bash
docker-compose up -d
```

### Production
1. Set up environment variables
2. Install dependencies
3. Run migrations: `alembic upgrade head`
4. Start with process manager: `python app/main.py`

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and test
4. Commit: `git commit -m "feat: add feature"`
5. Push and create PR

## License

MIT License

---

**Note**: This bot is currently designed for Ukrainian language interface. All user-facing text is in Ukrainian. Future versions will support English and German languages.
