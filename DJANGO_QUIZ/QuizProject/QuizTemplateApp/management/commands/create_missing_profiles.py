from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from QuizTemplateApp.models import CustomUser, UserProfile
from QuizTemplateApp.signals import create_user_profile, save_user_profile

class Command(BaseCommand):
    help = 'Create UserProfile for all users who do not have one'

    def handle(self, *args, **kwargs):
        # Temporarily disconnect signals to avoid duplicate profile creation
        post_save.disconnect(create_user_profile, sender=CustomUser)
        post_save.disconnect(save_user_profile, sender=CustomUser)
        
        # Find users without profiles
        users_without_profiles = []
        for user in CustomUser.objects.all():
            try:
                # Access profile to see if it exists
                user.profile
            except UserProfile.DoesNotExist:
                users_without_profiles.append(user)
        
        # Create profiles for users who need them
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for {user.username}'))
        
        # Show summary
        self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profiles)} new user profiles'))
        
        # Reconnect signals
        post_save.connect(create_user_profile, sender=CustomUser)
        post_save.connect(save_user_profile, sender=CustomUser) 