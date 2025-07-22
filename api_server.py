#!/usr/bin/env python3
"""
Website Analyzer Flask API

A REST API wrapper for the Website Analyzer tool that provides endpoints
for website analysis, SEO analysis, and automation opportunity detection.
Designed for integration with n8n workflows and other automation tools.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime
import traceback
import re
from urllib.parse import urlparse
import sys
import os
from dataclasses import asdict

# Import our website analyzer
from website_analyzer import WebsiteAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize website analyzer
analyzer = WebsiteAnalyzer()

class APIError(Exception):
    """Custom API Error class"""
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status'] = 'error'
        rv['timestamp'] = datetime.now().isoformat()
        return rv

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': [
            '/health',
            '/api/analyze',
            '/api/analyze/seo',
            '/api/analyze/automation',
            '/api/docs'
        ]
    }), 404

@app.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    }), 500

def validate_url(url):
    """Validate URL format"""
    if not url:
        raise APIError("URL is required", 400)
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validate URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise APIError("Invalid URL format", 400)
    except Exception:
        raise APIError("Invalid URL format", 400)
    
    # Basic security check
    if any(dangerous in url.lower() for dangerous in ['localhost', '127.0.0.1', '0.0.0.0']):
        raise APIError("Invalid URL - localhost not allowed", 400)
    
    return url

def format_response(data, status='success', message=None):
    """Format API response consistently"""
    response = {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    if message:
        response['message'] = message
        
    return response

def extract_seo_data(analysis_result):
    """Extract only SEO-related data from analysis result"""
    if not analysis_result:
        return None
        
    return {
        'url': analysis_result.url,
        'timestamp': analysis_result.timestamp,
        'seo_analysis': analysis_result.seo_analysis,
        'seo_score': analysis_result.seo_analysis.get('seo_score', 0),
        'seo_recommendations': [
            rec for rec in analysis_result.recommendations 
            if rec.get('category') == 'seo'
        ]
    }

def extract_automation_data(analysis_result):
    """Extract only automation-related data from analysis result"""
    if not analysis_result:
        return None
        
    automation_data = {
        'url': analysis_result.url,
        'timestamp': analysis_result.timestamp,
        'automation_score': analysis_result.automation_score,
        'chatbot_analysis': analysis_result.chatbot_analysis,
        'lead_capture_analysis': analysis_result.lead_capture_analysis,
        'email_signup_analysis': analysis_result.email_signup_analysis,
        'social_media_analysis': analysis_result.social_media_analysis,
        'review_analysis': analysis_result.review_analysis,
        'booking_analysis': analysis_result.booking_analysis,
        'mobile_analysis': analysis_result.mobile_analysis,
        'contact_analysis': analysis_result.contact_analysis,
        'automation_recommendations': [
            rec for rec in analysis_result.recommendations 
            if rec.get('category') != 'seo'
        ]
    }
    
    return automation_data

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Website Analyzer API',
        'version': '1.0.0'
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    """Detailed API status endpoint"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'service': 'Website Analyzer API',
        'version': '1.0.0',
        'endpoints': {
            'analyze': '/api/analyze',
            'seo_analyze': '/api/analyze/seo',
            'automation_analyze': '/api/analyze/automation',
            'health': '/health',
            'docs': '/api/docs'
        },
        'rate_limits': {
            'default': '100 requests per hour',
            'analysis': '20 requests per hour'
        }
    })

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("20 per hour")
def analyze_website():
    """
    Complete website analysis endpoint
    
    Request body:
    {
        "url": "https://example.com",
        "format": "json" (optional, default: json)
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        output_format = data.get('format', 'json')
        
        logger.info(f"Starting analysis for: {url}")
        
        # Perform analysis
        result = analyzer.analyze_website(url)
        
        if not result:
            raise APIError("Failed to analyze website. Please check the URL and try again.", 422)
        
        # Convert to dict for JSON response
        analysis_data = asdict(result)
        
        logger.info(f"Analysis completed for: {url} - Score: {result.automation_score}")
        
        return jsonify(format_response(
            analysis_data,
            message=f"Analysis completed successfully. Automation score: {result.automation_score}/100"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Analysis error for {data.get('url', 'unknown')}: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("Analysis failed due to technical error", 500)

@app.route('/api/analyze/seo', methods=['POST'])
@limiter.limit("20 per hour")
def analyze_seo_only():
    """
    SEO-focused analysis endpoint
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting SEO analysis for: {url}")
        
        # Perform full analysis
        result = analyzer.analyze_website(url)
        
        if not result:
            raise APIError("Failed to analyze website. Please check the URL and try again.", 422)
        
        # Extract SEO data only
        seo_data = extract_seo_data(result)
        
        logger.info(f"SEO analysis completed for: {url} - SEO Score: {result.seo_analysis.get('seo_score', 0)}")
        
        return jsonify(format_response(
            seo_data,
            message=f"SEO analysis completed. SEO score: {seo_data['seo_score']}/100"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"SEO analysis error for {data.get('url', 'unknown')}: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("SEO analysis failed due to technical error", 500)

@app.route('/api/analyze/automation', methods=['POST'])
@limiter.limit("20 per hour")
def analyze_automation_only():
    """
    Automation-focused analysis endpoint
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting automation analysis for: {url}")
        
        # Perform full analysis
        result = analyzer.analyze_website(url)
        
        if not result:
            raise APIError("Failed to analyze website. Please check the URL and try again.", 422)
        
        # Extract automation data only
        automation_data = extract_automation_data(result)
        
        logger.info(f"Automation analysis completed for: {url} - Score: {result.automation_score}")
        
        return jsonify(format_response(
            automation_data,
            message=f"Automation analysis completed. Score: {automation_data['automation_score']}/100"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Automation analysis error for {data.get('url', 'unknown')}: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("Automation analysis failed due to technical error", 500)

@app.route('/api/analyze/batch', methods=['POST'])
@limiter.limit("5 per hour")
def analyze_batch():
    """
    Batch analysis endpoint for multiple URLs
    
    Request body:
    {
        "urls": ["https://example1.com", "https://example2.com"],
        "analysis_type": "full" | "seo" | "automation" (optional, default: full)
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        urls = data.get('urls', [])
        analysis_type = data.get('analysis_type', 'full')
        
        if not urls or not isinstance(urls, list):
            raise APIError("URLs array is required", 400)
        
        if len(urls) > 5:
            raise APIError("Maximum 5 URLs allowed per batch", 400)
        
        # Validate all URLs first
        validated_urls = []
        for url in urls:
            validated_urls.append(validate_url(url))
        
        logger.info(f"Starting batch analysis for {len(validated_urls)} URLs")
        
        results = []
        
        for url in validated_urls:
            try:
                result = analyzer.analyze_website(url)
                
                if result:
                    if analysis_type == 'seo':
                        processed_result = extract_seo_data(result)
                    elif analysis_type == 'automation':
                        processed_result = extract_automation_data(result)
                    else:
                        processed_result = asdict(result)
                    
                    results.append({
                        'url': url,
                        'status': 'success',
                        'data': processed_result
                    })
                else:
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': 'Analysis failed'
                    })
                    
            except Exception as e:
                logger.error(f"Batch analysis error for {url}: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        successful_analyses = len([r for r in results if r['status'] == 'success'])
        
        logger.info(f"Batch analysis completed: {successful_analyses}/{len(urls)} successful")
        
        return jsonify(format_response(
            {
                'results': results,
                'summary': {
                    'total_urls': len(urls),
                    'successful': successful_analyses,
                    'failed': len(urls) - successful_analyses
                }
            },
            message=f"Batch analysis completed: {successful_analyses}/{len(urls)} successful"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("Batch analysis failed due to technical error", 500)

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    docs = {
        'title': 'Website Analyzer API Documentation',
        'version': '1.0.0',
        'description': 'REST API for website analysis including automation opportunities and SEO analysis',
        'base_url': request.base_url.replace('/api/docs', ''),
        'endpoints': {
            'health_check': {
                'url': '/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'response': 'Service health status'
            },
            'full_analysis': {
                'url': '/api/analyze',
                'method': 'POST',
                'description': 'Complete website analysis including automation and SEO',
                'rate_limit': '20 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)',
                    'format': 'Response format: json (optional, default: json)'
                },
                'example_request': {
                    'url': 'https://example.com',
                    'format': 'json'
                }
            },
            'seo_analysis': {
                'url': '/api/analyze/seo',
                'method': 'POST',
                'description': 'SEO-focused analysis only',
                'rate_limit': '20 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)'
                },
                'example_request': {
                    'url': 'https://example.com'
                }
            },
            'automation_analysis': {
                'url': '/api/analyze/automation',
                'method': 'POST',
                'description': 'Automation opportunities analysis only',
                'rate_limit': '20 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)'
                },
                'example_request': {
                    'url': 'https://example.com'
                }
            },
            'batch_analysis': {
                'url': '/api/analyze/batch',
                'method': 'POST',
                'description': 'Batch analysis for multiple URLs',
                'rate_limit': '5 requests per hour',
                'request_body': {
                    'urls': 'Array of URLs to analyze (required, max 5)',
                    'analysis_type': 'Type of analysis: full, seo, or automation (optional, default: full)'
                },
                'example_request': {
                    'urls': ['https://example1.com', 'https://example2.com'],
                    'analysis_type': 'full'
                }
            }
        },
        'response_format': {
            'success': {
                'status': 'success',
                'timestamp': 'ISO timestamp',
                'message': 'Success message (optional)',
                'data': 'Analysis results'
            },
            'error': {
                'status': 'error',
                'timestamp': 'ISO timestamp',
                'error': 'Error message'
            }
        },
        'n8n_integration': {
            'description': 'This API is designed for easy integration with n8n workflows',
            'webhook_setup': {
                'method': 'POST',
                'content_type': 'application/json',
                'authentication': 'None required (rate limited)'
            },
            'example_n8n_node': {
                'node_type': 'HTTP Request',
                'url': '{{$node["Webhook"].json["body"]["url"]}}',
                'method': 'POST',
                'body_type': 'JSON',
                'body': {
                    'url': '{{$json["url"]}}'
                }
            }
        }
    }
    
    return jsonify(docs)

@app.before_request
def before_request():
    """Add security headers and logging"""
    # Log incoming requests
    if request.method != 'OPTIONS':
        logger.info(f"{request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Website Analyzer API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)