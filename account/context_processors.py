from caesers import caesar_decrypt

def decrypted_user_data(request):
    """
    Context processor to decrypt user data for authenticated users.
    """
    if request.user.is_authenticated:
        return {
            'decrypted_first_name': caesar_decrypt(request.user.first_name),
            'decrypted_last_name': caesar_decrypt(request.user.last_name),
            'decrypted_email': caesar_decrypt(request.user.email),
        }
    return {}