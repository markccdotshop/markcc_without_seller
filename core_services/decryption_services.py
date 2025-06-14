from cryptography.fernet import Fernet
import base64

    # new_key = Fernet.generate_key()
    # new_key_str = new_key.decode()
    # print("New key:", new_key)



def decrypt_card_info(encrypted_info):
    key = b'CPd6uxuc-ag1k79BCpYm6knRRJYtjHhmZ5m44T43a_Q='
    cipher_suite = Fernet(key)
    
    try:
        decrypted_text = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_info))
        return decrypted_text.decode('utf-8')
    except UnicodeDecodeError:
        decrypted_text = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_info))
        return decrypted_text.decode('latin1')
    except Exception as e:
        # Log and handle error appropriately
        # print(f"Decryption failed: {e}")
        return None  # Ensure to return None or a default value in case of failure


