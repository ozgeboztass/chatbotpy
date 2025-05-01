from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.models.models import Question, Answer, QuizResult, User
from app import db
from sqlalchemy import desc
from app.utils.security import validate_form_data, check_content_security, sanitize_input

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/all')
@login_required
@check_content_security()
def all_questions():
    # Tüm soruları getir
    questions = Question.query.all()
    
    # Soruların cevaplarını getir
    for question in questions:
        question.answers = Answer.query.filter_by(question_id=question.id).all()
    
    return render_template('quiz.html', topic='all', questions=questions)

@bp.route('/start/<topic>')
@login_required
@check_content_security()
def start(topic):
    # Güvenlik kontrolü: Konu girişini temizle
    topic = sanitize_input(topic)
    
    # Kontrol et, geçerli bir konu mu?
    valid_topics = ['discord', 'flask', 'ai', 'vision', 'nlp', 'all']
    if topic not in valid_topics:
        flash('Invalid quiz topic!', 'error')
        return redirect(url_for('main.index'))
    
    # Eğer 'all' ise tüm soruları getir
    if topic == 'all':
        return all_questions()
    
    # Konuya ait soruları getir
    questions = Question.query.filter_by(topic=topic).all()
    
    for question in questions:
        question.answers = Answer.query.filter_by(question_id=question.id).all()
    
    return render_template('quiz.html', topic=topic, questions=questions)

@bp.route('/submit', methods=['POST'])
@login_required
@validate_form_data()
@check_content_security()
def submit():
    topic = request.form.get('topic')
    
    # Güvenlik kontrolü: Konu girişini temizle
    topic = sanitize_input(topic)
    
    # Tüm 'hepsi' veya geçerli konu kontrolü
    if topic == 'all':
        # Tüm sorular için sonuçları işle
        questions = Question.query.all()
    else:
        # Geçerli konu kontrolü
        valid_topics = ['discord', 'flask', 'ai', 'vision', 'nlp']
        if topic not in valid_topics:
            flash('Invalid quiz topic!', 'error')
            return redirect(url_for('main.index'))
        
        # Konuya ait tüm soruları getir
        questions = Question.query.filter_by(topic=topic).all()
    
    total_questions = len(questions)
    score = 0
    
    # Kullanıcının cevaplarını değerlendir
    processed_questions = []
    
    for question in questions:
        user_answer_id = request.form.get(f'question_{question.id}')
        
        # Kullanıcı bir cevap vermiş mi kontrol et
        if user_answer_id:
            try:
                # Cevap ID'sini sayı olarak doğrula
                user_answer_id = int(user_answer_id)
                
                # Cevap gerçekten bu soruya ait mi kontrol et
                user_answer = Answer.query.filter_by(id=user_answer_id, question_id=question.id).first()
                
                if user_answer:
                    is_correct = user_answer.is_correct
                    
                    if is_correct:
                        score += 1
                    
                    processed_questions.append({
                        'id': question.id, 
                        'question_text': question.question_text,
                        'user_answer': user_answer.answer_text,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct
                    })
                else:
                    # Geçersiz cevap, boş ekle
                    processed_questions.append({
                        'id': question.id, 
                        'question_text': question.question_text,
                        'user_answer': "No answer",
                        'correct_answer': question.correct_answer,
                        'is_correct': False
                    })
            except (ValueError, TypeError):
                # Hatalı ID formatı, boş cevap ekle
                processed_questions.append({
                    'id': question.id, 
                    'question_text': question.question_text,
                    'user_answer': "Invalid answer",
                    'correct_answer': question.correct_answer,
                    'is_correct': False
                })
        else:
            # Cevap verilmemiş, boş ekle
            processed_questions.append({
                'id': question.id, 
                'question_text': question.question_text,
                'user_answer': "No answer",
                'correct_answer': question.correct_answer,
                'is_correct': False
            })
    
    # Sonuçları veritabanına kaydet
    quiz_result = QuizResult(
        user_id=current_user.id,
        topic=topic,
        score=score,
        total_questions=total_questions
    )
    db.session.add(quiz_result)
    
    # Kullanıcının en son puanını güncelle
    current_user.last_score = score
    
    # Kullanıcının en yüksek puanını kontrol et ve güncelle
    if score > current_user.highest_score:
        current_user.highest_score = score
    
    db.session.commit()
    
    # Global en yüksek puanı getir
    global_high_score = db.session.query(db.func.max(QuizResult.score)).scalar() or 0
    
    # Sonuç sayfasına yönlendir
    return render_template(
        'result.html',
        topic=topic,
        score=score,
        highest_score=current_user.highest_score,
        global_high_score=global_high_score,
        total_questions=total_questions,
        questions=processed_questions
    ) 