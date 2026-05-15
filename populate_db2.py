import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_voting.settings')
django.setup()

from account.models import CustomUser
from voting.models import Voter, Position, Candidate, Votes
from caesers import caesar_encrypt

enc_email = caesar_encrypt('demovoter1@demo.com'.lower())
user = CustomUser.objects.get(email=enc_email)
voter = Voter.objects.get(admin=user)
candidate = Candidate.objects.first()
position = candidate.position

if not Votes.objects.filter(voter=voter, position=position).exists():
    Votes.objects.create(voter=voter, position=position, candidate=candidate)
    voter.voted = True
    voter.save()
    print('Vote cast!')
