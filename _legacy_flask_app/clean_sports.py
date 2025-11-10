
from app import app, db, Sport, Subdiscipline

def clean_data():
    try:
        num_subdisciplines = db.session.query(Subdiscipline).delete()
        num_sports = db.session.query(Sport).delete()
        db.session.commit()
        print(f"Successfully deleted {num_sports} sports and {num_subdisciplines} subdisciplines.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred during deletion: {e}")

if __name__ == "__main__":
    with app.app_context():
        clean_data()
