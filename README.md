# 🗳️ E-Voting System

A secure, web-based electronic voting system built with **Django**, featuring multi-layered authentication, role-based access control, and two-factor verification via OTP.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Security Architecture](#security-architecture)
- [Encryption & Hashing Techniques](#encryption--hashing-techniques)
- [Authentication Flow](#authentication-flow)
- [Known Security Issues & Recommendations](#known-security-issues--recommendations)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [License](#license)

---

## Overview

This e-voting platform enables administrators to manage elections and voters to securely cast ballots online. It incorporates several security layers including password hashing, a substitution cipher for PII obfuscation, CSRF protection, session management, and SMS-based OTP two-factor authentication.

> ⚠️ **Academic/Demo Notice**: Some components (Caesar cipher, hardcoded secret key, DEBUG mode) are not production-safe. See the [Known Security Issues](#known-security-issues--recommendations) section before deploying.

---

## Features

- 🔐 Email-based authentication with custom backend
- 👤 Role-based access control (Admin vs. Voter)
- 📱 Two-factor authentication via SMS OTP
- 🔒 CSRF protection on all forms
- 🛡️ Django password hashing (PBKDF2 + SHA256)
- 🔄 Substitution cipher encryption for stored PII
- 🚫 Rate-limited OTP resend (max 3 attempts)
- 🧱 Custom middleware for role enforcement
- 💾 SQLite (dev) / MySQL (production) support

---

## Security Architecture

### Overview Table

| Security Measure              |         | Location                        |
|-------------------------------|-----------------|----------------------------------|
| Password Hashing (PBKDF2)     |         | `account/models.py`             |
| Substitution Cipher (PII)     |         | `caesers.py`                    |
| CSRF Tokens                   |         | All HTML forms                  |
| Session Security              |         | Django default middleware       |
| Role-Based Access Control     |         | `account/middleware.py`         |
| OTP Two-Factor Auth           |         | `voting/models.py`              |
| Password Validators           |         | `e_voting/settings.py`          |
| Email-Based Authentication    |         | `account/email_backend.py`      |
| Clickjacking Protection       |         | `XFrameOptionsMiddleware`       |
| Secret Key Management         |         | `settings.py` (hardcoded)       |

*OTP has no expiration timer — see recommendations below.

---

## Encryption & Hashing Techniques

### 1. 🔑 Password Hashing — PBKDF2 (Django Built-in)

Django's `make_password()` is used to hash all user passwords before database storage.

```python
from django.contrib.auth.hashers import make_password

user.password = make_password(password)
```

**How it works:**
- Algorithm: **PBKDF2 with SHA256**
- Automatically generates a unique **salt** per password
- Applies **thousands of iterations** to slow brute-force attacks
- Stored as: `algorithm$iterations$salt$hash`

Password verification uses Django's constant-time `check_password()`:

```python
if user.check_password(password):
    return user
```

**Strength: ✅ Cryptographically secure.**

---

### 2. 🔤 Substitution Cipher — PII Obfuscation (`caesers.py`)

User emails and names are obfuscated before being stored in the database using a **fixed substitution cipher** (also called a monoalphabetic cipher).

> **Note**: Despite the filename `caesers.py`, this is **not** a traditional Caesar cipher (which shifts by a fixed number). It uses a **hardcoded character-to-character substitution map**, making it a substitution cipher. The result is obfuscation, not true encryption.

```python
# Encryption before storage
email = caesar_encrypt(self.normalize_email(email))
first_name = caesar_encrypt(extra_fields['first_name'])
last_name  = caesar_encrypt(extra_fields['last_name'])

# Decryption for display
context = {
    'first_name': caesar_decrypt(user.first_name),
    'last_name':  caesar_decrypt(user.last_name),
    'email':      caesar_decrypt(user.email),
}
```

**How it works:**
- A fixed `substitution_map` replaces each character with a predetermined other character
- Covers lowercase letters, uppercase letters, and digits
- A reverse map is used for decryption

---

### 3. 🔢 One-Time Password (OTP) — Two-Factor Authentication

A numeric OTP is generated and sent via SMS for voter identity verification.

```python
def generate_otp():
    otp = ""
    for i in range(random.randint(5, 8)):
        otp += str(random.randint(1, 9))
    return otp
```

- **Length**: 5–8 digits (randomly chosen per request)
- **Delivery**: SMS via Multitexter API
- **Rate limit**: Maximum 3 resend attempts per voter
- **Storage**: Stored in `OtpToken` model alongside a `verified` boolean flag
- **Limitation**: No expiration time — OTP remains valid indefinitely until used

---

## Authentication Flow

```
User enters email + password
        │
        ▼
Email encrypted with substitution cipher
        │
        ▼
Lookup encrypted email in DB → verify password with check_password()
        │
        ▼
Role check via AccountCheckMiddleWare
        │
        ├── Admin → Admin dashboard
        │
        └── Voter → OTP sent via SMS
                        │
                        ▼
                  Voter enters OTP
                        │
                        ▼
                  OTP verified → Ballot access
```

---

## Password Validation Rules

Configured in `e_voting/settings.py`:

| Validator                        | Purpose                                         |
|----------------------------------|-------------------------------------------------|
| `UserAttributeSimilarityValidator` | Rejects passwords too similar to username/email |
| `MinimumLengthValidator`         | Minimum 8 characters required                   |
| `CommonPasswordValidator`        | Rejects common/dictionary passwords             |
| `NumericPasswordValidator`       | Rejects all-numeric passwords                   |

---

## Tech Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Backend       | Python 3, Django                  |
| Database      | SQLite3 (dev), MySQL (production) |
| Auth          | Custom Django email backend       |
| 2FA           | SMS via Multitexter API           |
| Encryption    | Django PBKDF2, custom substitution cipher |
| Frontend      | Django Templates, HTML/CSS        |
| Security      | Django middleware stack, CSRF, XFrame |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/e-voting-system.git
cd e-voting-system

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (see below)
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (admin)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

---

## Project Structure

```
e-voting-system/
├── account/
│   ├── email_backend.py      # Custom email-based auth backend
│   ├── forms.py              # Registration & login forms with validation
│   ├── middleware.py         # Role-based access control middleware
│   ├── models.py             # User model with hashing & cipher on save
│   └── views.py              # Login, register, dashboard views
├── voting/
│   ├── models.py             # OtpToken model (OTP + verified flag)
│   ├── views.py              # OTP generation, verification, ballot views
│   └── admin_views.py        # Admin-only election management views
├── e_voting/
│   └── settings.py           # Django config, middleware, validators
├── caesers.py                # Substitution cipher encrypt/decrypt
├── templates/
│   └── voting/
│       ├── login.html
│       ├── reg.html
│       └── voter/
│           ├── verify.html   # OTP entry page
│           └── ballot.html   # Voting ballot page
└── manage.py
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-very-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# SMS Gateway (Multitexter)
SMS_EMAIL=your-sms-api-email@example.com
SMS_PASSWORD=your-sms-api-password
```

Load them in `settings.py` using `python-decouple` or `python-dotenv`.

---

## License

This project is for educational/academic purposes. Review and harden all security components before any production or real-election use.
