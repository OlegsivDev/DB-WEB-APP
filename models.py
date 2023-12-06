from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

available_tables = ['diseases', 'diseasesymptoms', 'drugdiseases', 'drugs', 'homemedicine', 'symptoms']


class Diseases(db.Model):
    __tablename__ = 'diseases'
    diseaseid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {'diseaseid': self.diseaseid, 'name': self.name}


class Diseasesymptoms(db.Model):
    __tablename__ = 'diseasesymptoms'
    connectionid = db.Column(db.Integer, primary_key=True)
    symptomid = db.Column(db.Integer, nullable=False)
    diseaseid = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {'connectionid': self.connectionid, 'symptomid': self.symptomid, 'diseaseid': self.diseaseid}


class Drugdiseases(db.Model):
    __tablename__ = 'drugdiseases'
    connectionid = db.Column(db.Integer, primary_key=True)
    drugid = db.Column(db.Integer, nullable=False)
    diseaseid = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {'connectionid': self.connectionid, 'drugid': self.drugid, 'diseaseid': self.diseaseid}


class Drugs(db.Model):
    __tablename__ = 'drugs'
    drugid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    expiredate = db.Column(db.Date, nullable=False)

    def as_dict(self):
        return {'drugid': self.drugid, 'name': self.name, 'expiredate': self.expiredate}


class Homemedicine(db.Model):
    __tablename__ = 'homemedicine'
    medicineid = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    drugid = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {'medicineid': self.medicineid, 'quantity': self.quantity, 'drugid': self.drugid}


class Symptoms(db.Model):
    __tablename__ = 'symptoms'
    symptomid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {'symptomid': self.symptomid, 'name': self.name}
