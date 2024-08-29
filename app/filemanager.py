from cryptography.fernet import Fernet
import pandas as pd
import os
import io

# Load the encryption key from an environment variable (GitHub secret)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

cipher = Fernet(ENCRYPTION_KEY)

def open_file(filepath):
    # Read and decrypt the file
    with open(filepath, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    
    # Load into a DataFrame using io.StringIO
    df = pd.read_csv(io.StringIO(decrypted_data.decode()))
    return df

def save_file(df, save_path='data/data.csv'):
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Encrypt the data
    encrypted_data = cipher.encrypt(csv_data.encode())
    
    # Save the encrypted data
    with open(save_path, 'wb') as file:
        file.write(encrypted_data)

def append_to_encrypted_file(new_data, file_path='data/data.csv'):
    if os.path.exists(file_path):
        # If the file exists, open and decrypt the existing data
        existing_df = open_file(file_path)
        
        # Append the new data to the existing data
        updated_df = pd.concat([existing_df, new_data], ignore_index=True)
    else:
        # If the file doesn't exist, the new data is the updated data
        updated_df = new_data
    
    # Encrypt and save the updated data
    save_file(updated_df, file_path)

# Example usage:
# new_data = pd.DataFrame({'column1': [value1], 'column2': [value2]})
# append_to_encrypted_file(new_data, 'path_to_encrypted_file.csv')
