from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
from dotenv import load_dotenv
import os

# Initialize logging for the server.
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes.

# Set up the SQLAlchemy database URI with an absolute path
project_root = os.path.abspath(os.path.dirname(__file__))
db_path = "/Users/margaretlong/gradjobsearch/gradjobsearch/jobs.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class FilterJob(db.Model):
    __tablename__ = 'filtered_jobs'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    postedQuarter = db.Column(db.String(255))
    postedDate = db.Column(db.DateTime, default=db.func.now())
    is_suitable = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'qualifications': self.qualifications,
            'postedQuarter': self.postedQuarter,
            'postedDate': self.postedDate.strftime('%m/%d/%Y') if self.postedDate else None,
            'is_suitable': self.is_suitable
        }

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    logging.info('API call to fetch all jobs received')
    search = request.args.get('search', '').lower()
    job_type = request.args.get('type', '').lower()

    job_query = FilterJob.query

    if search:
        search = f"%{search}%"
        job_query = job_query.filter(FilterJob.title.ilike(search) | FilterJob.description.ilike(search) | FilterJob.qualifications.ilike(search))

    if job_type:
        job_query = job_query.filter(FilterJob.type.ilike(job_type))

    jobs = job_query.all()  # Fetches all records without pagination
    serialized_jobs = [job.serialize() for job in jobs]

    logging.info(f"Total jobs fetched: {len(serialized_jobs)}")

    return jsonify({
        'jobs': serialized_jobs,
        'total': len(serialized_jobs)
    })


@app.route('/api/jobs/count', methods=['GET'])
def get_jobs_count():
    count = FilterJob.query.count()
    logging.info(f"Total number of jobs: {count}")
    return jsonify({'count': count})

@app.route('/')
def index():
    return "Welcome to the Grad Job Search Engine API!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the database and tables if they do not exist
    app.run(debug=True, port=os.getenv('FLASK_RUN_PORT', 5000))