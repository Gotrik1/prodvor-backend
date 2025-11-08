
from app import create_app, db
from app.models import Sport
import uuid

# Создаем экземпляр приложения, чтобы получить контекст
app = create_app(init_swagger=False)

def seed_data():
    # Проверяем, есть ли уже данные. Если есть, удаляем их.
    if db.session.query(Sport).first() is not None:
        print("Sports data already exists. Deleting old data before seeding.")
        db.session.query(Sport).delete()
        db.session.commit()

    sports_data = [
        {'id': 'sport-1', 'name': 'Футбол', 'isTeamSport': True},
        {'id': 'sport-2', 'name': 'Баскетбол', 'isTeamSport': True},
        {'id': 'sport-3', 'name': 'Волейбол', 'isTeamSport': True},
        {'id': 'sport-4', 'name': 'Хоккей', 'isTeamSport': True},
        {'id': 'sport-5', 'name': 'Гандбол', 'isTeamSport': True},
        {'id': 'sport-6', 'name': 'Регби', 'isTeamSport': True},
        {'id': 'sport-7', 'name': 'Водное поло', 'isTeamSport': True},
        {'id': 'sport-8', 'name': 'Лакросс', 'isTeamSport': True},
        {'id': 'sport-9', 'name': 'Флорбол', 'isTeamSport': True},
        {'id': 'sport-10', 'name': 'Хоккей на траве', 'isTeamSport': True},
        {'id': 'sport-11', 'name': 'Крикет', 'isTeamSport': True},
        {'id': 'sport-12', 'name': 'Бейсбол / Софтбол', 'isTeamSport': True},
        {'id': 'sport-13', 'name': 'Американский футбол', 'isTeamSport': True},
        {'id': 'sport-14', 'name': 'Корфбол', 'isTeamSport': True},
        {'id': 'sport-15', 'name': 'Нетбол', 'isTeamSport': True},
        {'id': 'sport-16', 'name': 'Сепак такро', 'isTeamSport': True},
        {'id': 'sport-17', 'name': 'Алтимат фрисби', 'isTeamSport': True},
        {'id': 'sport-18', 'name': 'Пейнтбол / Лазертаг', 'isTeamSport': True},
        {'id': 'sport-19', 'name': 'Киберспорт', 'isTeamSport': True},
        {'id': 'sport-20', 'name': 'Командные беговые эстафеты', 'isTeamSport': True},
        {'id': 'sport-21', 'name': 'Дворовые игры', 'isTeamSport': True},
        {'id': 'sport-22', 'name': 'Командный туризм и ориентирование', 'isTeamSport': True},
        {'id': 'sport-23', 'name': 'Гребля на лодках-драконах', 'isTeamSport': True},
        {'id': 'sport-24', 'name': 'Командные шахматы', 'isTeamSport': True},
        {'id': 'sport-25', 'name': 'Лёгкая атлетика', 'isTeamSport': False},
        {'id': 'sport-26', 'name': 'Плавание', 'isTeamSport': False},
        {'id': 'sport-27', 'name': 'Теннис', 'isTeamSport': False},
        {'id': 'sport-28', 'name': 'Бадминтон', 'isTeamSport': False},
        {'id': 'sport-29', 'name': 'Сквош', 'isTeamSport': False},
        {'id': 'sport-30', 'name': 'Единоборства', 'isTeamSport': False},
        {'id': 'sport-31', 'name': 'Фехтование', 'isTeamSport': False},
        {'id': 'sport-32', 'name': 'Стрельба', 'isTeamSport': False},
        {'id': 'sport-33', 'name': 'Тяжёлая атлетика', 'isTeamSport': False},
        {'id': 'sport-34', 'name': 'Пауэрлифтинг', 'isTeamSport': False},
        {'id': 'sport-35', 'name': 'Кроссфит', 'isTeamSport': False},
        {'id': 'sport-36', 'name': 'Гимнастика', 'isTeamSport': False},
        {'id': 'sport-37', 'name': 'Йога / стретчинг', 'isTeamSport': False},
        {'id': 'sport-38', 'name': 'Скалолазание', 'isTeamSport': False},
        {'id': 'sport-39', 'name': 'Серфинг / виндсёрфинг / кайтсёрфинг', 'isTeamSport': False},
        {'id': 'sport-40', 'name': 'Сноуборд / горные лыжи', 'isTeamSport': False},
        {'id': 'sport-41', 'name': 'Конный спорт', 'isTeamSport': False},
        {'id': 'sport-42', 'name': 'Велоспорт', 'isTeamSport': False},
        {'id': 'sport-43', 'name': 'Скейтбординг / роликовый спорт', 'isTeamSport': False},
        {'id': 'sport-44', 'name': 'Парашютный спорт', 'isTeamSport': False},
        {'id': 'sport-45', 'name': 'Парапланеризм', 'isTeamSport': False},
        {'id': 'sport-46', 'name': 'Триатлон', 'isTeamSport': False},
        {'id': 'sport-47', 'name': 'Гольф', 'isTeamSport': False},
        {'id': 'sport-48', 'name': 'Автоспорт / мотоспорт', 'isTeamSport': False},
        {'id': 'sport-49', 'name': 'Индивидуальные шахматы', 'isTeamSport': False},
        {'id': 'sport-50', 'name': 'Настольные игры как спорт', 'isTeamSport': False},
    ]

    for sport_data in sports_data:
        sport = Sport(id=sport_data['id'], name=sport_data['name'], isTeamSport=sport_data['isTeamSport'])
        db.session.add(sport)
    
    db.session.commit()
    print("Sports data has been successfully seeded.")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
