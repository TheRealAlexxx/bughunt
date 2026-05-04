import json
import os

def handler(request):
    """Vercel serverless function to serve game questions"""
    try:
        # Get the directory of this file and read questions.json from bughunt folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        questions_path = os.path.join(current_dir, '..', 'bughunt', 'questions.json')
        
        with open(questions_path, 'r') as f:
            questions = json.load(f)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(questions)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
