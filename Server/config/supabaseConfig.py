import os
import socket
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

def check_supabase_connectivity():
    """Check if Supabase URL is reachable."""
    if not SUPABASE_URL:
        return False, "SUPABASE_URL environment variable is not set"
    
    try:
        # Extract hostname from URL
        from urllib.parse import urlparse
        parsed = urlparse(SUPABASE_URL)
        hostname = parsed.netloc
        
        # Try to resolve hostname
        socket.gethostbyname(hostname)
        return True, "Supabase URL is reachable"
    except socket.gaierror as e:
        return False, f"DNS lookup failed for Supabase URL: {str(e)}. Please check your SUPABASE_URL in .env file."
    except Exception as e:
        return False, f"Error checking Supabase connectivity: {str(e)}"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: Supabase URL or Key is missing. Check your .env file.")
    print("Attempting to create Supabase client anyway...")
    supabase = None
else:
    # Check connectivity before creating client
    is_connected, message = check_supabase_connectivity()
    if not is_connected:
        print(f"WARNING: {message}")
        print("The application may not function correctly without Supabase connectivity.")
        supabase = None
    else:
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("Supabase client created successfully")
        except Exception as e:
            print(f"ERROR creating Supabase client: {str(e)}")
            print("The application may not function correctly.")
            supabase = None
