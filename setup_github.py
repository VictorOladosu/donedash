from flask import Flask
import os
import requests

def setup_github_repo():
    # Get GitHub username using the token
    token = os.environ['GITHUB_TOKEN']
    headers = {'Authorization': f'token {token}'}
    
    try:
        # Get user info
        user_response = requests.get('https://api.github.com/user', headers=headers)
        if user_response.status_code != 200:
            return f"Failed to get GitHub user info: {user_response.json()}"
            
        github_username = user_response.json()['login']
        
        # Create repository
        repo_data = {
            'name': 'donedash',
            'description': 'TaskRabbit-inspired service marketplace platform built with Flask',
            'private': False
        }
        create_repo = requests.post('https://api.github.com/user/repos', headers=headers, json=repo_data)
        
        if create_repo.status_code == 201:
            repo_url = create_repo.json()['html_url']
            return f"Repository created successfully: {repo_url}"
        else:
            return f"Failed to create repository: {create_repo.json()}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(setup_github_repo())
