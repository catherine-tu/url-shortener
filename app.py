from flask import Flask, request, jsonify, redirect
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import string
import random
import validators
import os

app = Flask(__name__)

# database setup
engine = create_engine('sqlite:///urls.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# represents a sqlite database table called 'urls'
class URL(Base):
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicks = Column(Integer, default=0)

Base.metadata.create_all(engine)

# generates a random string of 6 letter/digits -- only for new, long urls
def generate_short_code(length=6):
    """Generate a random short code for the URL."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    # extacts data and url field from the request
    data = request.get_json()
    long_url = data.get('url') 
    
    # if there is no url entered
    if not long_url:
        return jsonify({'error': 'URL is required'}), 400
    
    # confirms that structure of website is correct
    if not validators.url(long_url):
        return jsonify({'error': 'Invalid URL'}), 400
    
    session = Session()
    
    # check if url already exists in our database -- if so, use the same shortener!
    existing_url = session.query(URL).filter_by(original_url=long_url).first()

    if existing_url:
        session.close()
        return jsonify({
            'original_url': existing_url.original_url,
            'short_url': f'http://127.0.0.1:5000/{existing_url.short_code}',
            'short_code': existing_url.short_code
        })
    # otherwise, run until generate a *unique* short code (accounts for if random code is same as in db)
    else:
        while True:
            short_code = generate_short_code() 
            if not session.query(URL).filter_by(short_code=short_code).first():
                break
    
    # create new url entry of the short code for the original url
    new_url = URL(
        original_url=long_url,
        short_code=short_code
    )
    
    session.add(new_url)
    session.commit()
    session.close()
    
    # output
    return jsonify({
        'original_url': long_url,
        'short_url': f'http://127.0.0.1:5000/{short_code}',
        'short_code': short_code
    }), 201


@app.route('/<short_code>')
def redirect_to_url(short_code):
    """
    Expand a shortened URL to its original form and redirect the user.
    
    Args:
        short_code (str): The uniquem code corresponding to the shortened URL
        
    Returns:
        Response: A redirect to the original URL or an error.
    """
    # if does not match url / shortened format
    if not short_code or len(short_code) != 6:
        return jsonify({'error': 'Invalid URL format'}), 400
        
    session = Session()
    try:
        url_entry = session.query(URL).filter_by(short_code=short_code).first()
        
        if url_entry is None:
            return jsonify({'error': 'URL not found'}), 404
        
        # get original url before closing session
        original_url = url_entry.original_url
        
        # validate the original URL
        if not validators.url(original_url):
            return jsonify({'error': 'Stored URL is invalid'}), 500
        
        # increment click counter & update in db
        url_entry.clicks += 1
        session.commit()
        
        # tries to prevent browsers from caching redirect -- helps with accurate click count & consistent behavior
        response = redirect(original_url)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        session.close()


@app.route('/stats/<short_code>')
# statistics of the url, tracking clicks, original / short url, etc
def get_url_stats(short_code):
    session = Session()
    url_entry = session.query(URL).filter_by(short_code=short_code).first()
    
    if url_entry is None:
        session.close()
        return jsonify({'error': 'URL not found'}), 404
    
    stats = {
        'short_code': url_entry.short_code,
        'original_url': url_entry.original_url,
        'created_at': url_entry.created_at.isoformat(),
        'clicks': url_entry.clicks
    }
    
    session.close()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
