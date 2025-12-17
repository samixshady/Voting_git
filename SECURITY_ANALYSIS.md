# Security Analysis Report - E-Voting System

## Overview
This document details all hashing techniques and security measures implemented throughout the e-voting project.

---

## 1. PASSWORD HASHING

### Django's Built-in Password Hashing (`make_password`)
- **Location**: [account/models.py](account/models.py#L20)
- **Implementation**: Uses Django's `make_password()` function from `django.contrib.auth.hashers`
- **Default Algorithm**: PBKDF2 (Password-Based Key Derivation Function 2)
- **Code Example**:
  ```python
  user.password = make_password(password)  # Password is hashed by Django
  ```
- **Features**:
  - Automatic salt generation
  - Iterative hashing with multiple rounds
  - Secure storage in database
  - Used in both user creation and superuser creation

### Password Verification
- **Location**: [account/email_backend.py](account/email_backend.py#L13)
- **Method**: `user.check_password(password)`
- **Implementation**: Django's built-in secure password comparison
  ```python
  if user.check_password(password):
      return user
  ```

---

## 2. CUSTOM ENCRYPTION - Caesar Cipher

### Caesar Cipher Substitution Encryption
- **Location**: [caesers.py](caesers.py)
- **Purpose**: Email and name encryption
- **Technique**: Character substitution mapping with custom key
- **Details**:
  - Fixed substitution map for lowercase, uppercase, and digits
  - Reverse mapping for decryption
  - **Note**: This is a **WEAK encryption** (Caesar cipher is cryptographically insecure)

### Encrypted Fields
- **Email**: Encrypted using `caesar_encrypt()` before storage
- **First Name**: Encrypted using `caesar_encrypt()` before storage
- **Last Name**: Encrypted using `caesar_encrypt()` before storage
- **Decryption**: Using `caesar_decrypt()` when displaying to users

### Implementation Points

#### User Creation (Model Level)
- **Location**: [account/models.py](account/models.py#L11-L21)
  ```python
  email = caesar_encrypt(self.normalize_email(email))
  extra_fields['first_name'] = caesar_encrypt(extra_fields['first_name'])
  extra_fields['last_name'] = caesar_encrypt(extra_fields['last_name'])
  ```

#### User Registration (View Level)
- **Location**: [account/views.py](account/views.py#L55-L57)
  ```python
  user.first_name = caesar_encrypt(user.first_name)
  user.last_name = caesar_encrypt(user.last_name)
  user.email = caesar_encrypt(user.email)
  ```

#### Authentication
- **Location**: [account/views.py](account/views.py#L10-L13)
  ```python
  encrypted_email = caesar_encrypt(request.POST.get('email'))
  password = request.POST.get('password')
  return EmailBackend.authenticate(request, username=encrypted_email, password=password)
  ```

#### Dashboard Decryption
- **Location**: [account/views.py](account/views.py#L77-L82)
  ```python
  context = {
      'first_name': caesar_decrypt(user.first_name),
      'last_name': caesar_decrypt(user.last_name),
      'email': caesar_decrypt(user.email),
  }
  ```

---

## 3. PASSWORD VALIDATION RULES

### Django Password Validators
- **Location**: [e_voting/settings.py](e_voting/settings.py#L97-L113)
- **Validators Enabled**:
  1. **UserAttributeSimilarityValidator**: Checks password isn't too similar to user attributes
  2. **MinimumLengthValidator**: Enforces minimum password length (default: 8 characters)
  3. **CommonPasswordValidator**: Rejects common/dictionary passwords
  4. **NumericPasswordValidator**: Rejects purely numeric passwords

---

## 4. AUTHENTICATION SECURITY

### Custom Email-Based Authentication Backend
- **Location**: [account/email_backend.py](account/email_backend.py)
- **Features**:
  - Email-based login instead of username
  - Custom backend extending Django's `ModelBackend`
  - Secure password comparison via `check_password()`
  - Exception handling for non-existent users

### User Types & Role-Based Access Control
- **Location**: [account/models.py](account/models.py#L44)
- **User Types**:
  - Type 1: Admin
  - Type 2: Voter
- **Enforcement**: Through middleware and view decorators

---

## 5. CSRF PROTECTION

### Cross-Site Request Forgery (CSRF) Tokens
- **Middleware**: `django.middleware.csrf.CsrfViewMiddleware`
- **Location**: [e_voting/settings.py](e_voting/settings.py#L47)
- **Implementation in Templates**:
  - [voting/login.html](voting/templates/voting/login.html#L16): `{% csrf_token %}`
  - [voting/reg.html](voting/templates/voting/reg.html#L12): `{% csrf_token %}`
  - [voting/voter/verify.html](voting/templates/voting/voter/verify.html#L16): `{% csrf_token %}`
  - [voting/voter/ballot.html](voting/templates/voting/voter/ballot.html#L16): `{% csrf_token %}`

### Token Removal in AJAX
- **Location**: [voting/views.py](voting/views.py#L259)
  ```python
  form.pop('csrfmiddlewaretoken', None)
  ```

---

## 6. SESSION SECURITY

### Django Session Middleware
- **Location**: [e_voting/settings.py](e_voting/settings.py#L46)
- **Middleware**: `django.contrib.sessions.middleware.SessionMiddleware`
- **Features**:
  - Session cookies for user authentication
  - Default security settings in Django

### Authentication Checks
- Widespread use of `request.user.is_authenticated` checks
- **Locations**:
  - [voting/views.py](voting/views.py#L15)
  - [voting/admin_views.py](voting/admin_views.py#L7)
  - [account/views.py](account/views.py#L78)

---

## 7. ACCESS CONTROL & MIDDLEWARE

### Custom Middleware - Role-Based Access Control
- **Location**: [account/middleware.py](account/middleware.py)
- **Name**: `AccountCheckMiddleWare`
- **Features**:
  - Enforces role-based access (Admin vs Voter)
  - Prevents admins from accessing voter views
  - Prevents voters from accessing admin views
  - Redirects unauthenticated users to login
  - Validates user type before allowing view access

### Implementation
```python
class AccountCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Type 1: Admin access control
        # Type 2: Voter access control
        # Prevents unauthorized access
```

---

## 8. TWO-FACTOR AUTHENTICATION (OTP)

### One-Time Password (OTP) System
- **Location**: [voting/models.py](voting/models.py#L5-L14)
- **Fields**:
  - `otp`: CharField to store OTP (max 10 characters)
  - `verified`: Boolean flag for OTP verification
  - `otp_sent`: Counter to limit OTP requests (max 3 resends)

### OTP Generation
- **Location**: [voting/views.py](voting/views.py#L87-L95)
- **Method**: Random number generation
  ```python
  def generate_otp():
      otp = ""
      for i in range(r.randint(5, 8)):
          otp += str(r.randint(1, 9))
      return otp
  ```
- **Length**: 5-8 random digits

### OTP Verification
- **Location**: [voting/views.py](voting/views.py#L119-L123)
- **View**: `verify()` function
- **Template**: [voting/voter/verify.html](voting/templates/voting/voter/verify.html)

### OTP Resend Protection
- **Location**: [voting/views.py](voting/views.py#L135-L138)
- **Rate Limiting**: Maximum 3 OTP resend requests per voter
- **Message**: "You have requested OTP three times. You cannot do this again!"

### OTP Configuration
- **Location**: [e_voting/settings.py](e_voting/settings.py#L153)
- **Setting**: `SEND_OTP = False` (can toggle for testing with OTP "0000")

### SMS Gateway Integration
- **Location**: [voting/views.py](voting/views.py#L182-L201)
- **Service**: Multitexter SMS API
- **Authentication**: Email and password from environment variables
- **Method**: POST request with OTP message
- **Security Note**: Credentials stored in environment variables

---

## 9. INPUT VALIDATION & FORM SECURITY

### Email Validation
- **Location**: [account/forms.py](account/forms.py#L37-L49)
- **Features**:
  - Email field validation
  - Checks for duplicate email registration
  - Case-insensitive email comparison
  - Raises ValidationError if email exists

### Password Field Validation
- **Location**: [account/forms.py](account/forms.py#L51-L57)
- **Features**:
  - Uses Django's `make_password()` in form clean method
  - Optional password for updates (only if provided)
  - Preserves existing password if not changed

---

## 10. SECURITY WARNINGS & ISSUES

### ⚠️ CRITICAL SECURITY CONCERNS

#### 1. **Weak Caesar Cipher Encryption**
- **Issue**: Caesar cipher is NOT cryptographically secure
- **Risk**: Personal data (email, names) can be easily decrypted
- **Recommendation**: Use Django's `cryptography` library or `django-encrypted-model-fields`

#### 2. **Exposed Secret Key**
- **Location**: [e_voting/settings.py](e_voting/settings.py#L24)
- **Current**: `SECRET_KEY = '%6lp_p!%r$7t-2ql5hc5(r@)8u_fc+6@ugxcnz=h=b(fn#3$p9'`
- **Risk**: Hardcoded in version control (if public)
- **Recommendation**: Move to environment variables using `python-decouple` or `python-dotenv`

#### 3. **Debug Mode Enabled**
- **Location**: [e_voting/settings.py](e_voting/settings.py#L26)
- **Current**: `DEBUG = True`
- **Risk**: Exposes sensitive information in error pages
- **Recommendation**: Set to `False` in production

#### 4. **Empty ALLOWED_HOSTS**
- **Location**: [e_voting/settings.py](e_voting/settings.py#L29)
- **Current**: `ALLOWED_HOSTS = []`
- **Risk**: In production with DEBUG=False, no hosts will be allowed
- **Recommendation**: Configure with production domain

#### 5. **Simple OTP (5-8 digits)**
- **Risk**: Only 10,000 to 99,999,999 possible combinations
- **Recommendation**: Increase to 6-8 digits minimum, add time expiration

#### 6. **No OTP Expiration**
- **Issue**: OTP stored indefinitely
- **Recommendation**: Implement OTP expiration (typically 5-10 minutes)

#### 7. **Environment Variables Exposure**
- **Location**: [voting/views.py](voting/views.py#L188-L190)
- **Risk**: SMS credentials in environment variables without validation
- **Recommendation**: Use proper secrets management

---

## 11. DJANGO BUILT-IN SECURITY FEATURES

### Security Middleware Enabled
- **SecurityMiddleware**: `django.middleware.security.SecurityMiddleware`
- **Location**: [e_voting/settings.py](e_voting/settings.py#L45)

### Clickjacking Protection
- **Middleware**: `django.middleware.clickjacking.XFrameOptionsMiddleware`
- **Location**: [e_voting/settings.py](e_voting/settings.py#L50)
- **Protection**: Prevents framing of pages in iframes

### Message Framework
- **Usage**: Django messages for user notifications
- **Security**: Auto-escapes HTML in messages

---

## 12. DATABASE SECURITY

### Current Configuration
- **Engine**: SQLite3 (development)
- **Alternative**: MySQL (commented out, available for production)
- **Location**: [e_voting/settings.py](e_voting/settings.py#L83-L94)

### ORM Protection
- **Framework**: Django ORM
- **Feature**: Automatic SQL injection prevention through parameterized queries

---

## SUMMARY OF SECURITY MEASURES

| Security Measure | Strength | Location |
|------------------|----------|----------|
| Password Hashing (PBKDF2) | ✅ Strong | account/models.py |
| Caesar Cipher Encryption | ❌ Weak | caesers.py |
| CSRF Tokens | ✅ Strong | All forms |
| Session Security | ✅ Strong | Django default |
| Role-Based Access Control | ✅ Strong | account/middleware.py |
| OTP 2FA | ✅ Strong* | voting/models.py (*no expiration) |
| Password Validators | ✅ Strong | settings.py |
| Email Authentication | ✅ Strong | account/email_backend.py |
| Clickjacking Protection | ✅ Strong | XFrameOptionsMiddleware |
| Secret Key Management | ❌ Weak | settings.py (hardcoded) |
| Debug Mode | ❌ Weak | settings.py (enabled) 
