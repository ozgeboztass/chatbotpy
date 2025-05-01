from app import create_app
from app.models.models import db
from app.models.seed_data import seed_database

if __name__ == "__main__":
    print("Creating a new database...")
    app = create_app()
    with app.app_context():
        db.drop_all()  # Mevcut tabloları temizle
        db.create_all()  # Tabloları oluştur
        print("Database tables created successfully.")
        
        # Örnek verileri ekle
        print("Adding sample data...")
        seed_database()
        print("Sample data added successfully.")
        
    print("Database recreation completed!") 