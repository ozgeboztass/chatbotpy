import unittest
from app import create_app, db
from app.models.models import User, Question, Answer, QuizResult
import os
import logging

# Test sırasında kullanılacak test veritabanını yapılandır
TEST_DB = 'test.db'

class QuizAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Test öncesi hazırlıklar"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{TEST_DB}'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Test kullanıcısı oluştur
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            
            # Test sorusu oluştur
            question = Question(
                topic='flask',
                question_text='What is Flask?',
                correct_answer='A micro web framework for Python'
            )
            db.session.add(question)
            db.session.commit()
            
            # Test cevapları oluştur
            answers = [
                Answer(question_id=question.id, answer_text='A micro web framework for Python', is_correct=True),
                Answer(question_id=question.id, answer_text='A database system', is_correct=False),
                Answer(question_id=question.id, answer_text='A Python IDE', is_correct=False),
                Answer(question_id=question.id, answer_text='A machine learning library', is_correct=False)
            ]
            
            for answer in answers:
                db.session.add(answer)
            
            db.session.commit()
    
    def tearDown(self):
        """Test sonrası temizlik"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        
        if os.path.exists(TEST_DB):
            os.unlink(TEST_DB)
    
    def test_home_page(self):
        """Ana sayfa testi"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_register(self):
        """Kayıt işlemi testi"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
    
    def test_login(self):
        """Giriş işlemi testi"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_start(self):
        """Sınav başlatma testi"""
        # Önce giriş yap
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Sınav başlat
        response = self.client.get('/quiz/start/flask')
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_submit(self):
        """Sınav gönderme testi"""
        # Önce giriş yap
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Soru ID'sini al
        with self.app.app_context():
            question = Question.query.filter_by(topic='flask').first()
            answer = Answer.query.filter_by(question_id=question.id, is_correct=True).first()
        
        # Cevabı gönder
        response = self.client.post('/quiz/submit', data={
            'topic': 'flask',
            f'question_{question.id}': answer.id
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Puanın kaydedilip edilmediğini kontrol et
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertEqual(user.last_score, 1)
            
            result = QuizResult.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(result)
            self.assertEqual(result.score, 1)

if __name__ == '__main__':
    # Loglama ayarları
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='test_logs.log'
    )
    unittest.main() 