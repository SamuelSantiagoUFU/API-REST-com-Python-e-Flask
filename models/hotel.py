from sql_alchemy import banco

class HotelModel(banco.Model):
    __tablename__ = 'hoteis'

    id = banco.Column(banco.String(80), primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1))
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(40))
    site_id = banco.Column(banco.Integer, banco.ForeignKey('sites.id'))

    def __init__(self, id, nome, estrelas, diaria, cidade, site_id):
        self.id = id
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id

    def json(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'estrelas': self.estrelas,
            'diaria': self.diaria,
            'cidade': self.cidade,
            'site_id': self.site_id
        }

    @classmethod
    def find(cls, hotel_id):
        hotel = cls.query.filter_by(id=hotel_id).first()
        return hotel or None

    def save(self):
        banco.session.add(self)
        banco.session.commit()

    def update(self, nome, estrelas, diaria, cidade, site_id):
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id

    def delete(self):
        banco.session.delete(self)
        banco.session.commit()
