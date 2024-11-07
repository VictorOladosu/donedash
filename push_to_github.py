import subprocess
import os

def push_to_github():
    try:
        # Configure git user
        subprocess.run(['git', 'config', '--global', 'user.email', "noreply@replit.com"], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', "Replit"], check=True)
        
        # Configure git with the token for authentication
        token = os.environ['GITHUB_TOKEN']
        remote_url = f"https://{token}@github.com/VictorOladosu/donedash.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], check=True)
        
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', "Initial commit: Complete DoneDash marketplace platform"], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        
        return "Successfully pushed code to GitHub"
    except subprocess.CalledProcessError as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(push_to_github())
