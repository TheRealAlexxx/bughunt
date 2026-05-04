import json

def handler(request):
    """Vercel serverless function to serve game questions"""
    try:
        # Read questions.json from the bughunt directory
        with open('/var/task/bughunt/questions.json', 'r') as f:
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
            'body': json.dumps({'error': str(e)})
        }
