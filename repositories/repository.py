
class Repository:
    """Репозиторий доступа к таблице БД"""
    def __init__(self, session):
        self.session = session

