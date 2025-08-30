from ext import db


class ProvinceEntity(db.Model):
    __tablename__ = 'province'

    code = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))

class CityEntity(db.Model):
    __tablename__ = 'city'

    code = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    provinceCode = db.Column(db.String(255), db.ForeignKey('province.code'),)

    province = db.relationship('ProvinceEntity', backref=db.backref('cities'))


class AreaEntity(db.Model):
    __tablename__ = 'area'

    code = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    cityCode = db.Column(db.String(255), db.ForeignKey('city.code'), )
    provinceCode = db.Column(db.String(255), db.ForeignKey('province.code'), )

    city = db.relationship('CityEntity', backref=db.backref('areas'))
    province = db.relationship('ProvinceEntity', backref=db.backref('areas'))

