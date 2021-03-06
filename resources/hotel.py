from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import *
import mysql.connector
from env import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_DB

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=int)
path_params.add_argument('offset', type=int)

class Hoteis(Resource):
    def get(self):
        connection = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DB)
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            consulta = consulta_sem_cidade
        else:
            consulta = consulta_com_cidade
        tupla = tuple([parametros[chave] for chave in parametros])
        cursor.execute(consulta, tupla)
        resultado = cursor.fetchall()
        hoteis = []
        if resultado:
            for linha in resultado:
                hoteis.append({
                    'id': linha[0],
                    'nome': linha[1],
                    'estrelas': linha[2],
                    'diaria': linha[3],
                    'cidade': linha[4],
                    'site_id': linha[5]
                })
        return {'hoteis': hoteis}

class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank")
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked with a site")

    def get(self, hotel_id):
        hotel = HotelModel.find(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404

    @jwt_required
    def post(self, hotel_id):
        if HotelModel.find(hotel_id):
            return {"message":"Id '{}' already exists.".format(hotel_id)}, 400
        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        if not SiteModel.find_id(dados.get('site_id')):
            return {'message': 'The hotel must to be associated to a valid site id.'}, 400
        try:
            hotel.save()
        except:
            return {'message':'An internal error occurred trying to save hotel.'}, 500
        return hotel.json(), 200

    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update(**dados)
            hotel_encontrado.save()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save()
        except:
            return {'message':'An internal error occurred trying to save hotel.'}, 500
        return hotel.json(), 201

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find(hotel_id)
        if hotel:
            try:
                hotel.delete()
            except:
                return {'message':'An internal error occurred trying to delete hotel.'}, 500
            return {'message': 'Hotel deleted.'}, 200
        return {'message': 'Hotel not found.'}, 404
