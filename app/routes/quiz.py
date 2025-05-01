from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.models.models import Question, Answer, QuizResult, User
from app import db
from sqlalchemy import desc

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/start/<topic>')
@login_required
def start(topic):
    # Kontrol et, geçerli bir konu mu?
    valid_topics = ['discord', 'flask', 'ai', 'vision', 'nlp']
    if topic not in valid_topics:
        flash('Invalid quiz topic!', 'error')
        return redirect(url_for('main.index'))
    
    # Konuya ait soruları getir
    questions = Question.query.filter_by(topic=topic).all()
    
    for question in questions:
        question.answers = Answer.query.filter_by(question_id=question.id).all()
    
    return render_template('quiz.html', topic=topic, questions=questions)

@bp.route('/submit', methods=['POST'])
@login_required
def submit():
    topic = request.form.get('topic')
    
    # Konuya ait tüm soruları getir
    questions = Question.query.filter_by(topic=topic).all()
    total_questions = len(questions)
    score = 0
    
    # Kullanıcının cevaplarını değerlendir
    processed_questions = []
    
    for question in questions:
        user_answer_id = request.form.get(f'question_{question.id}')
        if user_answer_id:
            user_answer = Answer.query.get(user_answer_id)
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