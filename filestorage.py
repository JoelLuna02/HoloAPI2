from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import send_file
from io import BytesIO
import mimetypes
from models import *
from schema import *

fileapi = Api()
fileschema = FileSchema()

class ListStoredFiles(Resource):
    def get(self):
        Files = File.query.all()
        response = fileschema.dump(Files, many=True)
        return response, 200
    
class OpenFile(Resource):
    def get(self, filename:str):
        if filename is None:
            raise BadRequest("The filename is missing")
        archive = File.query.filter_by(filename=filename).first()
        if not archive:
            raise NotFound("File not found")
        mime = mimetypes.guess_type(archive.filename)
        return send_file(BytesIO(archive.filebytes), mimetype=mime[0], as_attachment=False, download_name=archive.filename)
        

class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=FileStorage, location='files', required=True)
        args = parser.parse_args()

        archive = args["file"]
        filename = secure_filename(archive.filename)
        archive_bytes = archive.read()
        if len(archive_bytes) >= 10485760:
            raise BadRequest("The file is too long to storage in the database. The maximum file size is 10 MB")
        
        newfile = File(filename=filename, filebytes=archive_bytes)
        newfile.integrity = newfile.set_integrity()
        db.session.add(newfile)
        db.session.commit()
        response = {"message": "Successfully storaged file in the database"}
        return response, 201

class DeleteFile(Resource):
    def delete(self, id:int):
        if id is None:
            raise BadRequest("You must define a file id to delete.")
        file = db.session.get(File, id)
        if file is None:
            raise NotFound("File not found")
        db.session.delete(file)
        db.session.commit()
        return {}, 204

fileapi.add_resource(UploadFile, '/v1/upload')
fileapi.add_resource(ListStoredFiles, '/v1/assets/listfiles')
fileapi.add_resource(OpenFile, '/v1/assets/<string:filename>')
fileapi.add_resource(DeleteFile, '/v1/deletefile/<int:id>')