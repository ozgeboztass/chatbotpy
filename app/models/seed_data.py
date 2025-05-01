from app import create_app
from app.models.models import db, Question, Answer

def seed_database():
    app = create_app()
    with app.app_context():
        # Discord.py Questions
        discord_questions = [
            {
                'question': 'What is the main purpose of the @client.event decorator in Discord.py?',
                'correct_answer': 'To define event handlers for Discord events',
                'answers': [
                    'To create new Discord servers',
                    'To define event handlers for Discord events',
                    'To send messages to channels',
                    'To manage user permissions'
                ]
            },
            {
                'question': 'Which method is used to send a message to a Discord channel?',
                'correct_answer': 'channel.send()',
                'answers': [
                    'channel.message()',
                    'channel.send()',
                    'channel.post()',
                    'channel.write()'
                ]
            }
        ]

        # Flask Questions
        flask_questions = [
            {
                'question': 'What is the purpose of Flask blueprints?',
                'correct_answer': 'To organize Flask applications into components',
                'answers': [
                    'To create database models',
                    'To handle user authentication',
                    'To organize Flask applications into components',
                    'To manage static files'
                ]
            },
            {
                'question': 'Which decorator is used to define routes in Flask?',
                'correct_answer': '@app.route()',
                'answers': [
                    '@app.route()',
                    '@app.endpoint()',
                    '@app.url()',
                    '@app.path()'
                ]
            }
        ]

        # AI Questions
        ai_questions = [
            {
                'question': 'What is the main purpose of a neural network?',
                'correct_answer': 'To learn patterns from data',
                'answers': [
                    'To store data',
                    'To learn patterns from data',
                    'To create graphics',
                    'To manage databases'
                ]
            },
            {
                'question': 'Which Python library is commonly used for machine learning?',
                'correct_answer': 'scikit-learn',
                'answers': [
                    'Django',
                    'Flask',
                    'scikit-learn',
                    'PyGame'
                ]
            }
        ]

        # Computer Vision Questions
        vision_questions = [
            {
                'question': 'What is OpenCV primarily used for?',
                'correct_answer': 'Computer vision and image processing',
                'answers': [
                    'Web development',
                    'Database management',
                    'Computer vision and image processing',
                    'Game development'
                ]
            },
            {
                'question': 'Which method is used to read an image in OpenCV?',
                'correct_answer': 'cv2.imread()',
                'answers': [
                    'cv2.read()',
                    'cv2.imread()',
                    'cv2.load()',
                    'cv2.open()'
                ]
            }
        ]

        # NLP Questions
        nlp_questions = [
            {
                'question': 'What is the purpose of NLTK in Python?',
                'correct_answer': 'Natural Language Processing',
                'answers': [
                    'Web scraping',
                    'Game development',
                    'Natural Language Processing',
                    'Data visualization'
                ]
            },
            {
                'question': 'Which method is used to tokenize text in NLTK?',
                'correct_answer': 'word_tokenize()',
                'answers': [
                    'split()',
                    'word_tokenize()',
                    'tokenize()',
                    'text_split()'
                ]
            }
        ]

        # Add questions to database
        for topic, questions in [
            ('discord', discord_questions),
            ('flask', flask_questions),
            ('ai', ai_questions),
            ('vision', vision_questions),
            ('nlp', nlp_questions)
        ]:
            for q in questions:
                question = Question(
                    topic=topic,
                    question_text=q['question'],
                    correct_answer=q['correct_answer']
                )
                db.session.add(question)
                db.session.flush()  # Get the question ID

                for answer_text in q['answers']:
                    answer = Answer(
                        question_id=question.id,
                        answer_text=answer_text,
                        is_correct=(answer_text == q['correct_answer'])
                    )
                    db.session.add(answer)

        db.session.commit()

if __name__ == '__main__':
    seed_database() 