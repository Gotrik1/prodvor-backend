
from app import app, db, Sport, Subdiscipline
import uuid

def seed_data():
    # Check if sports are already seeded
    if Sport.query.first() is not None:
        print("Sports data already exists. Skipping seed.")
        return

    sports_data = [
        {'id': 'sport-1', 'name': 'Футбол', 'isTeamSport': True, 'subdisciplines': ['мини-футбол', 'пляжный футбол', 'футзал', 'уличный футбол']},
        {'id': 'sport-2', 'name': 'Баскетбол', 'isTeamSport': True, 'subdisciplines': ['3х3', 'стритбол', 'классический']},
        {'id': 'sport-3', 'name': 'Волейбол', 'isTeamSport': True, 'subdisciplines': ['пляжный', 'классический', 'мини-волейбол']},
        {'id': 'sport-4', 'name': 'Хоккей', 'isTeamSport': True, 'subdisciplines': ['на льду', 'с мячом', 'роллер-хоккей', 'уличный']},
        {'id': 'sport-5', 'name': 'Гандбол', 'isTeamSport': True},
        {'id': 'sport-6', 'name': 'Регби', 'isTeamSport': True, 'subdisciplines': ['классическое', 'регби-7', 'тач-регби']},
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
        {'id': 'sport-19', 'name': 'Киберспорт', 'isTeamSport': True, 'subdisciplines': ['CS2', 'Dota 2', 'Valorant']},
        {'id': 'sport-20', 'name': 'Командные беговые эстафеты', 'isTeamSport': True},
        {'id': 'sport-21', 'name': 'Дворовые игры', 'isTeamSport': True, 'subdisciplines': ['вышибалы', 'лапта', 'казаки-разбойники', 'городки командные']},
        {'id': 'sport-22', 'name': 'Командный туризм и ориентирование', 'isTeamSport': True},
        {'id': 'sport-23', 'name': 'Гребля на лодках-драконах', 'isTeamSport': True},
        {'id': 'sport-24', 'name': 'Командные шахматы', 'isTeamSport': True, 'subdisciplines': ['лиги']},
        {'id': 'sport-25', 'name': 'Лёгкая атлетика', 'isTeamSport': False, 'subdisciplines': ['бег', 'прыжки', 'метания']},
        {'id': 'sport-26', 'name': 'Плавание', 'isTeamSport': False, 'subdisciplines': ['индивидуальные заплывы']},
        {'id': 'sport-27', 'name': 'Теннис', 'isTeamSport': False, 'subdisciplines': ['большой', 'настольный', 'падел']},
        {'id': 'sport-28', 'name': 'Бадминтон', 'isTeamSport': False},
        {'id': 'sport-29', 'name': 'Сквош', 'isTeamSport': False},
        {'id': 'sport-30', 'name': 'Единоборства', 'isTeamSport': False, 'subdisciplines': ['бокс', 'дзюдо', 'самбо', 'карате', 'тхэквондо', 'MMA']},
        {'id': 'sport-31', 'name': 'Фехтование', 'isTeamSport': False},
        {'id': 'sport-32', 'name': 'Стрельба', 'isTeamSport': False, 'subdisciplines': ['лук', 'арбалет', 'огнестрельное оружие']},
        {'id': 'sport-33', 'name': 'Тяжёлая атлетика', 'isTeamSport': False},
        {'id': 'sport-34', 'name': 'Пауэрлифтинг', 'isTeamSport': False},
        {'id': 'sport-35', 'name': 'Кроссфит', 'isTeamSport': False},
        {'id': 'sport-36', 'name': 'Гимнастика', 'isTeamSport': False, 'subdisciplines': ['спортивная', 'художественная']},
        {'id': 'sport-37', 'name': 'Йога / стретчинг', 'isTeamSport': False},
        {'id': 'sport-38', 'name': 'Скалолазание', 'isTeamSport': False, 'subdisciplines': ['боулдеринг', 'спортивное']},
        {'id': 'sport-39', 'name': 'Серфинг / виндсёрфинг / кайтсёрфинг', 'isTeamSport': False},
        {'id': 'sport-40', 'name': 'Сноуборд / горные лыжи', 'isTeamSport': False},
        {'id': 'sport-41', 'name': 'Конный спорт', 'isTeamSport': False},
        {'id': 'sport-42', 'name': 'Велоспорт', 'isTeamSport': False, 'subdisciplines': ['шоссе', 'BMX', 'маунтинбайк']},
        {'id': 'sport-43', 'name': 'Скейтбординг / роликовый спорт', 'isTeamSport': False},
        {'id': 'sport-44', 'name': 'Парашютный спорт', 'isTeamSport': False},
        {'id': 'sport-45', 'name': 'Парапланеризм', 'isTeamSport': False},
        {'id': 'sport-46', 'name': 'Триатлон', 'isTeamSport': False},
        {'id': 'sport-47', 'name': 'Гольф', 'isTeamSport': False},
        {'id': 'sport-48', 'name': 'Автоспорт / мотоспорт', 'isTeamSport': False},
        {'id': 'sport-49', 'name': 'Индивидуальные шахматы', 'isTeamSport': False},
        {'id': 'sport-50', 'name': 'Настольные игры как спорт', 'isTeamSport': False, 'subdisciplines': ['го', 'шашки']},
    ]

    for sport_data in sports_data:
        sport = Sport(id=sport_data['id'], name=sport_data['name'], isTeamSport=sport_data['isTeamSport'])
        db.session.add(sport)
        
        if 'subdisciplines' in sport_data:
            for sub_name in sport_data['subdisciplines']:
                subdiscipline = Subdiscipline(id=str(uuid.uuid4()), name=sub_name, parentId=sport.id)
                db.session.add(subdiscipline)
    
    db.session.commit()
    print("Sports data has been seeded.")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
