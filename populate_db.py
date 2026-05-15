import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_voting.settings')
django.setup()

from account.models import CustomUser
from voting.models import Voter, Position, Candidate

print('Creating dummy data...')

# Create position
position, created = Position.objects.get_or_create(
    name='President', 
    defaults={'max_vote': 1, 'priority': 1}
)

# Create 5 candidates
candidates_info = [
    ('Alice Smith', 'Experienced leader.'),
    ('Bob Johnson', 'Reform advocate.'),
    ('Charlie Brown', 'Economic focus.'),
    ('Diana Prince', 'Healthcare priority.'),
    ('Evan Wright', 'Education champion.')
]

for name, bio in candidates_info:
    if not Candidate.objects.filter(fullname=name).exists():
        Candidate.objects.create(fullname=name, bio=bio, position=position, photo='')

# Create 2 voters
voters_info = [
    ('demovoter1@demo.com', 'demo123', 'John', 'Doe', '12345678901'),
    ('demovoter2@demo.com', 'demo123', 'Jane', 'Smith', '10987654321')
]

for email, password, first, last, phone in voters_info:
    from caesers import caesar_encrypt
    enc_email = caesar_encrypt(CustomUser.objects.normalize_email(email))
    
    if not CustomUser.objects.filter(email=enc_email).exists():
        user = CustomUser.objects.create_user(email=email, password=password, first_name=first, last_name=last, user_type='2')
        if not Voter.objects.filter(phone=phone).exists():
            Voter.objects.create(admin=user, phone=phone, verified=True)
            
print('Done populating database!')
