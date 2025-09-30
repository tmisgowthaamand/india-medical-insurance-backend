#!/usr/bin/env python3
"""
CORS Proxy Server - Bypass CORS issues by proxying requests
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins

RENDER_BASE_URL = "https://india-medical-insurance-backend.onrender.com"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    """Proxy all requests to Render backend"""
    
    # Handle preflight OPTIONS requests
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight OK'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    # Build target URL
    target_url = f"{RENDER_BASE_URL}/{path}"
    
    # Prepare headers (remove host-specific headers and disable gzip)
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'origin', 'accept-encoding']:
            headers[key] = value
    
    # Disable gzip to avoid encoding issues
    headers['Accept-Encoding'] = 'identity'
    
    try:
        # Forward request to Render backend
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, params=request.args, timeout=30)
        elif request.method == 'POST':
            # Handle different POST content types
            if request.content_type and 'application/json' in request.content_type:
                # JSON request
                response = requests.post(target_url, headers=headers, json=request.json, timeout=30)
            elif request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                # Form data request - handle both form and raw data
                if request.form:
                    response = requests.post(target_url, headers=headers, data=request.form, timeout=30)
                else:
                    # Handle URLSearchParams sent as raw data
                    response = requests.post(target_url, headers=headers, data=request.data, timeout=30)
            elif request.form:
                # Has form data
                response = requests.post(target_url, headers=headers, data=request.form, timeout=30)
            elif request.data:
                # Raw data (including URLSearchParams)
                response = requests.post(target_url, headers=headers, data=request.data, timeout=30)
            else:
                # Fallback - try as form data
                response = requests.post(target_url, headers=headers, data=request.form, timeout=30)
        elif request.method == 'PUT':
            response = requests.put(target_url, headers=headers, json=request.json, timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, timeout=30)
        else:
            return jsonify({'error': 'Method not supported'}), 405
        
        # Return response with CORS headers
        print(f"Backend response status: {response.status_code}")
        print(f"Backend response headers: {dict(response.headers)}")
        print(f"Backend response text: {response.text[:200]}...")
        
        try:
            response_data = response.json()
            print(f"Parsed JSON keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
        except ValueError:
            # If not JSON, return as text
            response_data = {'message': response.text, 'raw_response': response.text}
            print("Response is not JSON")
        except Exception as e:
            response_data = {'error': f'Response parsing error: {str(e)}', 'raw_response': response.text}
            print(f"JSON parsing error: {e}")
        
        flask_response = jsonify(response_data)
        flask_response.status_code = response.status_code
        
        # Add CORS headers
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        flask_response.headers['Access-Control-Allow-Credentials'] = 'true'
        flask_response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH'
        flask_response.headers['Access-Control-Allow-Headers'] = '*'
        
        return flask_response
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Backend timeout'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Backend connection failed'}), 502
    except Exception as e:
        return jsonify({'error': f'Proxy error: {str(e)}'}), 500

@app.route('/proxy-status')
def proxy_status():
    """Check proxy status"""
    return jsonify({
        'message': 'CORS Proxy is running',
        'target': RENDER_BASE_URL,
        'cors': 'enabled'
    })

if __name__ == '__main__':
    print("🚀 Starting CORS Proxy Server")
    print("=" * 40)
    print(f"Proxying to: {RENDER_BASE_URL}")
    print("Local proxy: http://localhost:8002")
    print("CORS: Enabled for all origins")
    print()
    print("Update frontend .env to use:")
    print("VITE_API_URL=http://localhost:8002")
    print()
    app.run(host='0.0.0.0', port=8002, debug=True)
