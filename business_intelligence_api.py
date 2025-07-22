#!/usr/bin/env python3
"""
Business Intelligence API Server

Enhanced Flask API for comprehensive business intelligence analysis
specifically designed for agency sales teams.
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime
import traceback
import os
from dataclasses import asdict

# Import our business intelligence analyzer
from business_intelligence_analyzer import BusinessIntelligenceAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize analyzer
analyzer = BusinessIntelligenceAnalyzer()

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
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def validate_url(url):
    """Validate URL format"""
    if not url:
        raise APIError("URL is required", 400)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
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

class HumanReadableReportFormatter:
    """Formats business intelligence data into human-readable reports"""
    
    def __init__(self):
        self.report_width = 80
        self.section_separator = "=" * self.report_width
        self.subsection_separator = "-" * self.report_width
    
    def format_header(self, title, subtitle=None):
        """Format report header"""
        header = f"\n{self.section_separator}\n"
        header += f"{title.center(self.report_width)}\n"
        if subtitle:
            header += f"{subtitle.center(self.report_width)}\n"
        header += f"{self.section_separator}\n"
        return header
    
    def format_section(self, title, content_dict):
        """Format a report section"""
        section = f"\n📊 {title}\n"
        section += f"{self.subsection_separator}\n"
        
        for key, value in content_dict.items():
            if isinstance(value, dict):
                section += f"{key.replace('_', ' ').title()}:\n"
                for sub_key, sub_value in value.items():
                    section += f"  • {sub_key.replace('_', ' ').title()}: {self._format_value(sub_value)}\n"
            elif isinstance(value, list):
                section += f"{key.replace('_', ' ').title()}: {len(value)} items\n"
                for item in value[:5]:  # Show first 5 items
                    if isinstance(item, dict):
                        if 'opportunity' in item:
                            section += f"  • {item['opportunity'].replace('_', ' ').title()}\n"
                        elif 'recommendation' in item:
                            section += f"  • {item['recommendation']}\n"
                        else:
                            section += f"  • {str(item)[:50]}...\n"
                    else:
                        section += f"  • {str(item)}\n"
                if len(value) > 5:
                    section += f"  ... and {len(value) - 5} more\n"
            else:
                section += f"{key.replace('_', ' ').title()}: {self._format_value(value)}\n"
        
        return section
    
    def _format_value(self, value):
        """Format individual values for display"""
        if isinstance(value, bool):
            return "✅ Yes" if value else "❌ No"
        elif isinstance(value, (int, float)):
            return f"{value:,}" if value > 999 else str(value)
        elif isinstance(value, str):
            if value.lower() in ['high', 'premium', 'excellent']:
                return f"🟢 {value.title()}"
            elif value.lower() in ['medium', 'good', 'qualified']:
                return f"🟡 {value.title()}"
            elif value.lower() in ['low', 'basic', 'poor', 'nurture']:
                return f"🔴 {value.title()}"
            else:
                return value
        else:
            return str(value)
    
    def format_executive_summary(self, analysis_result):
        """Format executive summary"""
        company_name = analysis_result.company_profile.get('company_name', 'Unknown Company')
        lead_data = analysis_result.lead_scoring
        
        summary = self.format_header(f"BUSINESS INTELLIGENCE REPORT", company_name)
        
        summary += f"""
📍 EXECUTIVE SUMMARY
{self.subsection_separator}
Website: {analysis_result.url}
Analysis Date: {datetime.now().strftime('%B %d, %Y')}
Report Generated: {datetime.now().strftime('%I:%M %p')}

🎯 LEAD ASSESSMENT
• Lead Quality: {self._format_value(lead_data.get('lead_quality', 'unknown'))}
• Overall Score: {lead_data.get('overall_score', 0)}/100
• Deal Potential: {lead_data.get('deal_size_estimate', 'Unknown')}
• Sales Priority: {self._format_value(lead_data.get('sales_priority', 'unknown'))}
• Conversion Probability: {self._format_value(lead_data.get('conversion_probability', 'unknown'))}
• Sales Cycle Estimate: {lead_data.get('sales_cycle_estimate', 'Unknown')}

🏢 COMPANY OVERVIEW
• Industry: {analysis_result.company_profile.get('industry', 'Unknown').title()}
• Business Size: {analysis_result.company_profile.get('business_size', 'Unknown')}
• Location: {analysis_result.company_profile.get('location', 'Unknown')}
• Employees: {analysis_result.company_profile.get('employees', 'Unknown')}

💰 BUDGET ANALYSIS
• Budget Level: {self._format_value(analysis_result.budget_indicators.get('overall_budget_level', 'unknown'))}
• Monthly Spend Estimate: {analysis_result.budget_indicators.get('monthly_spend_estimate', 'Unknown')}
• Investment Capacity: {self._format_value(analysis_result.budget_indicators.get('investment_capacity', 'unknown'))}
"""
        return summary
    
    def format_detailed_analysis(self, analysis_result):
        """Format detailed analysis sections"""
        report = ""
        
        # Technology Analysis
        tech_data = {
            'sophistication_score': analysis_result.tech_stack_analysis.get('tech_sophistication_score', 0),
            'detected_technologies': len(analysis_result.tech_stack_analysis.get('detected_technologies', {})),
            'key_technologies': list(analysis_result.tech_stack_analysis.get('detected_technologies', {}).keys())[:5],
            'modernization_needs': analysis_result.tech_stack_analysis.get('modernization_needs', []),
            'agency_opportunities': analysis_result.tech_stack_analysis.get('agency_opportunities', [])
        }
        report += self.format_section("TECHNOLOGY STACK ANALYSIS", tech_data)
        
        # Social Media Intelligence
        social_data = {
            'platforms_found': len(analysis_result.social_media_intelligence.get('platforms_found', {})),
            'active_platforms': list(analysis_result.social_media_intelligence.get('platforms_found', {}).keys()),
            'advertising_channels': analysis_result.social_media_intelligence.get('social_budget_indicators', []),
            'strategy_maturity': analysis_result.social_media_intelligence.get('social_strategy_assessment', {}).get('maturity', 'unknown'),
            'missing_opportunities': analysis_result.social_media_intelligence.get('missing_opportunities', [])
        }
        report += self.format_section("SOCIAL MEDIA INTELLIGENCE", social_data)
        
        # Contact Intelligence
        contact_data = {
            'accessibility': analysis_result.contact_intelligence.get('contact_accessibility', 'unknown'),
            'contact_methods': analysis_result.contact_intelligence.get('contact_methods', []),
            'key_personnel': analysis_result.contact_intelligence.get('key_personnel', []),
            'sales_readiness_score': f"{analysis_result.contact_intelligence.get('sales_readiness_score', 0)}/100",
            'lead_magnets': analysis_result.contact_intelligence.get('lead_magnets', [])
        }
        report += self.format_section("CONTACT & DECISION MAKER INTELLIGENCE", contact_data)
        
        return report
    
    def format_opportunities_section(self, analysis_result):
        """Format opportunities and recommendations"""
        report = f"\n🚀 SALES OPPORTUNITIES & RECOMMENDATIONS\n"
        report += f"{self.subsection_separator}\n"
        
        # Immediate Opportunities
        immediate_opps = analysis_result.sales_opportunities.get('immediate_opportunities', [])
        if immediate_opps:
            report += "\n🔥 IMMEDIATE OPPORTUNITIES (Next 30 Days):\n"
            for i, opp in enumerate(immediate_opps, 1):
                report += f"{i}. {opp['opportunity'].replace('_', ' ').title()}\n"
                report += f"   💰 Value: {opp['estimated_value']}\n"
                report += f"   ⏱️ Timeline: {opp['timeline']}\n"
                report += f"   🎯 Priority: {self._format_value(opp['priority'])}\n\n"
        
        # Service Recommendations
        service_recs = analysis_result.sales_opportunities.get('service_recommendations', {})
        if service_recs:
            report += "\n📋 SERVICE RECOMMENDATIONS:\n"
            for service, data in service_recs.items():
                if data.get('fit_score', 0) > 60:
                    report += f"• {service.replace('_', ' ').title()}: {data['fit_score']}% fit\n"
                    if 'monthly_retainer' in data:
                        report += f"  💰 Monthly Retainer: {data['monthly_retainer']}\n"
                    elif 'project_value' in data:
                        report += f"  💰 Project Value: {data['project_value']}\n"
                    elif 'setup_cost' in data:
                        report += f"  💰 Setup Cost: {data['setup_cost']}\n"
                    report += f"  🛠️ Services: {', '.join(data.get('services', []))}\n\n"
        
        # Next Actions
        next_actions = analysis_result.lead_scoring.get('next_actions', [])
        if next_actions:
            report += "📝 RECOMMENDED NEXT ACTIONS:\n"
            for i, action in enumerate(next_actions, 1):
                report += f"{i}. {action.replace('_', ' ').title()}\n"
        
        # Add GoHighLevel recommendations
        ghl_data = analysis_result.sales_opportunities.get('gohighlevel_services', {})
        if ghl_data:
            report += self.format_gohighlevel_recommendations(ghl_data)
        
        return report
    
    def format_gohighlevel_recommendations(self, ghl_data):
        """Format GoHighLevel service recommendations"""
        if not ghl_data or not ghl_data.get('service_recommendations'):
            return ""
        
        service_recs = ghl_data.get('service_recommendations', {})
        investment_summary = ghl_data.get('investment_summary', {})
        
        report = f"\n🔧 GOHIGHLEVEL SERVICE OPPORTUNITIES\n"
        report += f"{self.subsection_separator}\n"
        
        # Priority services first
        priority_services = investment_summary.get('priority_services', [])
        if priority_services:
            report += "\n🔥 HIGH PRIORITY SERVICES:\n"
            for service_name in priority_services:
                service_key = service_name.lower().replace(' ', '_')
                if service_key in service_recs and service_recs[service_key]['recommended']:
                    service_data = service_recs[service_key]
                    report += f"• {service_name}\n"
                    report += f"  💰 Setup: ${service_data['setup_fee']:,} | Monthly: ${service_data['monthly_rate']:,}\n"
                    report += f"  📈 ROI: {service_data['roi_estimate']}\n"
                    report += f"  ⏱️ Implementation: {service_data['implementation_time']}\n"
                    report += f"  💡 Reason: {service_data['reason']}\n\n"
        
        # All recommended services
        recommended_services = [name for name, data in service_recs.items() if data['recommended']]
        if recommended_services:
            report += "\n📋 ALL RECOMMENDED SERVICES:\n"
            for service_name in recommended_services:
                if service_name not in [s.lower().replace(' ', '_') for s in priority_services]:
                    service_data = service_recs[service_name]
                    formatted_name = service_name.replace('_', ' ').title()
                    report += f"• {formatted_name}\n"
                    report += f"  💰 Setup: ${service_data['setup_fee']:,} | Monthly: ${service_data['monthly_rate']:,}\n"
                    report += f"  📈 ROI: {service_data['roi_estimate']}\n"
                    report += f"  ⏱️ Implementation: {service_data['implementation_time']}\n\n"
        
        # Investment Summary
        if investment_summary:
            report += f"\n💰 INVESTMENT SUMMARY:\n"
            report += f"• Total Setup Investment: ${investment_summary.get('total_setup_investment', 0):,}\n"
            report += f"• Total Monthly Investment: ${investment_summary.get('total_monthly_investment', 0):,}\n"
            report += f"• Recommended Services: {investment_summary.get('total_recommended_services', 0)}\n"
            report += f"• Industry Focus: {investment_summary.get('industry_focus', 'General').title()}\n"
            report += f"• Business Size: {investment_summary.get('business_size', 'Unknown').title()}\n"
            report += f"• ROI Timeline: {investment_summary.get('estimated_roi_timeline', 'Unknown')}\n\n"
        
        # Implementation Roadmap
        roadmap = investment_summary.get('implementation_roadmap', [])
        if roadmap:
            report += f"🗓️ IMPLEMENTATION ROADMAP:\n"
            for phase in roadmap:
                report += f"Phase {phase['phase']}: {phase['focus']} ({phase['timeline']})\n"
                report += f"  📝 {phase['description']}\n"
                if phase.get('services'):
                    report += f"  🛠️ Services: {', '.join(phase['services'])}\n"
                report += "\n"
        
        return report
    
    def format_competitive_analysis(self, analysis_result):
        """Format competitive analysis section"""
        comp_data = analysis_result.competitor_analysis
        if not any(comp_data.values()):
            return ""
        
        report = f"\n🏆 COMPETITIVE INTELLIGENCE\n"
        report += f"{self.subsection_separator}\n"
        
        if comp_data.get('identified_competitors'):
            report += f"Identified Competitors ({len(comp_data['identified_competitors'])}):\n"
            for comp in comp_data['identified_competitors'][:5]:
                report += f"• {comp}\n"
        
        if comp_data.get('market_positioning') != 'unknown':
            report += f"\nMarket Positioning: {self._format_value(comp_data['market_positioning'])}\n"
        
        return report
    
    def format_full_report(self, analysis_result, agency_name="Your Agency", contact_person="Sales Representative"):
        """Generate complete human-readable report"""
        report = self.format_executive_summary(analysis_result)
        report += self.format_detailed_analysis(analysis_result)
        report += self.format_opportunities_section(analysis_result)
        report += self.format_competitive_analysis(analysis_result)
        
        # Footer
        report += f"\n\n{self.section_separator}\n"
        report += f"Report prepared by: {agency_name}\n"
        report += f"Contact: {contact_person}\n"
        report += f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        report += f"{self.section_separator}\n"
        
        return report

# Initialize formatter
formatter = HumanReadableReportFormatter()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Business Intelligence API',
        'version': '1.0.0'
    })

@app.route('/api/analyze/business-intelligence', methods=['POST'])
@limiter.limit("10 per hour")
def analyze_business_intelligence():
    """
    Complete business intelligence analysis
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting BI analysis for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website. Please check the URL and try again.", 422)
        
        analysis_data = asdict(result)
        
        logger.info(f"BI analysis completed for: {url} - Lead Score: {result.lead_scoring.get('overall_score', 0)}")
        
        return jsonify(format_response(
            analysis_data,
            message=f"Business intelligence analysis completed. Lead score: {result.lead_scoring.get('overall_score', 0)}/100"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"BI analysis error for {data.get('url', 'unknown')}: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("Business intelligence analysis failed", 500)

@app.route('/api/analyze/lead-scoring', methods=['POST'])
@limiter.limit("15 per hour")
def analyze_lead_scoring():
    """
    Lead scoring focused analysis
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting lead scoring analysis for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        lead_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'lead_scoring': result.lead_scoring,
            'company_profile': result.company_profile,
            'budget_indicators': result.budget_indicators,
            'contact_intelligence': result.contact_intelligence,
            'sales_opportunities': result.sales_opportunities
        }
        
        logger.info(f"Lead scoring completed for: {url} - Score: {result.lead_scoring.get('overall_score', 0)}")
        
        return jsonify(format_response(
            lead_data,
            message=f"Lead scoring completed. Quality: {result.lead_scoring.get('lead_quality', 'unknown')}"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Lead scoring error: {str(e)}")
        raise APIError("Lead scoring analysis failed", 500)

@app.route('/api/analyze/social-intelligence', methods=['POST'])
@limiter.limit("20 per hour")
def analyze_social_intelligence():
    """
    Social media intelligence analysis
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting social intelligence analysis for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        social_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'social_media_intelligence': result.social_media_intelligence,
            'opportunities': [
                opp for opp in result.sales_opportunities.get('immediate_opportunities', [])
                if 'social' in opp.get('opportunity', '').lower()
            ]
        }
        
        logger.info(f"Social intelligence analysis completed for: {url}")
        
        return jsonify(format_response(
            social_data,
            message="Social media intelligence analysis completed"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Social intelligence error: {str(e)}")
        raise APIError("Social intelligence analysis failed", 500)

@app.route('/api/analyze/tech-stack', methods=['POST'])
@limiter.limit("20 per hour")
def analyze_tech_stack():
    """
    Technology stack analysis
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting tech stack analysis for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        tech_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'tech_stack_analysis': result.tech_stack_analysis,
            'budget_implications': result.budget_indicators,
            'modernization_opportunities': [
                opp for opp in result.sales_opportunities.get('immediate_opportunities', [])
                if any(keyword in opp.get('opportunity', '').lower() 
                      for keyword in ['website', 'tech', 'optimization'])
            ]
        }
        
        logger.info(f"Tech stack analysis completed for: {url}")
        
        return jsonify(format_response(
            tech_data,
            message=f"Technology analysis completed. Sophistication score: {result.tech_stack_analysis.get('tech_sophistication_score', 0)}"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Tech stack analysis error: {str(e)}")
        raise APIError("Technology analysis failed", 500)

@app.route('/api/analyze/sales-report', methods=['POST'])
@limiter.limit("10 per hour")
def generate_sales_report():
    """
    Generate executive sales report
    
    Request body:
    {
        "url": "https://example.com",
        "agency_name": "Your Agency Name",
        "contact_person": "Sales Rep Name"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        agency_name = data.get('agency_name', 'Your Agency')
        contact_person = data.get('contact_person', 'Sales Representative')
        
        logger.info(f"Generating sales report for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        # Generate comprehensive sales report
        sales_report = {
            'report_metadata': {
                'generated_for': result.company_profile.get('company_name', 'Unknown Company'),
                'website': result.url,
                'generated_by': agency_name,
                'contact': contact_person,
                'report_date': datetime.now().strftime('%B %d, %Y'),
                'analysis_timestamp': result.timestamp
            },
            'executive_summary': result.unified_report.get('executive_summary', {}),
            'company_profile': result.company_profile,
            'opportunity_assessment': {
                'lead_quality': result.lead_scoring.get('lead_quality', 'unknown'),
                'overall_score': result.lead_scoring.get('overall_score', 0),
                'deal_potential': result.lead_scoring.get('deal_size_estimate', 'unknown'),
                'timeline': result.lead_scoring.get('sales_cycle_estimate', 'unknown'),
                'conversion_probability': result.lead_scoring.get('conversion_probability', 'unknown'),
                'next_actions': result.lead_scoring.get('next_actions', [])
            },
            'detailed_findings': {
                'social_media': {
                    'platforms_count': len(result.social_media_intelligence.get('platforms_found', {})),
                    'advertising_channels': result.social_media_intelligence.get('social_budget_indicators', []),
                    'strategy_maturity': result.social_media_intelligence.get('social_strategy_assessment', {}),
                    'opportunities': result.social_media_intelligence.get('missing_opportunities', [])
                },
                'technology': {
                    'sophistication_score': result.tech_stack_analysis.get('tech_sophistication_score', 0),
                    'detected_technologies': list(result.tech_stack_analysis.get('detected_technologies', {}).keys()),
                    'budget_level': result.tech_stack_analysis.get('budget_implications', {}).get('level', 'unknown'),
                    'agency_opportunities': result.tech_stack_analysis.get('agency_opportunities', [])
                },
                'budget_analysis': {
                    'overall_level': result.budget_indicators.get('overall_budget_level', 'unknown'),
                    'monthly_estimate': result.budget_indicators.get('monthly_spend_estimate', 'unknown'),
                    'investment_capacity': result.budget_indicators.get('investment_capacity', 'unknown'),
                    'optimization_opportunities': result.budget_indicators.get('budget_optimization_opportunities', [])
                }
            },
            'service_recommendations': result.sales_opportunities.get('service_recommendations', {}),
            'immediate_opportunities': result.sales_opportunities.get('immediate_opportunities', []),
            'contact_intelligence': {
                'accessibility': result.contact_intelligence.get('contact_accessibility', 'unknown'),
                'contact_methods': result.contact_intelligence.get('contact_methods', []),
                'key_personnel': result.contact_intelligence.get('key_personnel', []),
                'sales_readiness': result.contact_intelligence.get('sales_readiness_score', 0)
            },
            'competitive_insights': {
                'identified_competitors': result.competitor_analysis.get('identified_competitors', []),
                'market_positioning': result.competitor_analysis.get('market_positioning', 'unknown'),
                'competitive_gaps': result.competitor_analysis.get('competitive_gaps', [])
            },
            'proposal_framework': {
                'recommended_services': [
                    service for service, data in result.sales_opportunities.get('service_recommendations', {}).items()
                    if data.get('fit_score', 0) > 70
                ],
                'project_timeline': result.lead_scoring.get('sales_cycle_estimate', 'unknown'),
                'investment_range': result.lead_scoring.get('deal_size_estimate', 'unknown'),
                'success_probability': result.lead_scoring.get('conversion_probability', 'unknown')
            }
        }
        
        logger.info(f"Sales report generated for: {url} - Lead Quality: {result.lead_scoring.get('lead_quality', 'unknown')}")
        
        return jsonify(format_response(
            sales_report,
            message=f"Sales report generated for {result.company_profile.get('company_name', 'target company')}"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Sales report generation error: {str(e)}")
        raise APIError("Sales report generation failed", 500)

@app.route('/api/analyze/competitor-intelligence', methods=['POST'])
@limiter.limit("15 per hour")
def analyze_competitor_intelligence():
    """
    Competitor intelligence analysis
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting competitor intelligence for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        competitor_data = {
            'url': result.url,
            'timestamp': result.timestamp,
            'competitor_analysis': result.competitor_analysis,
            'market_insights': {
                'industry': result.company_profile.get('industry', 'unknown'),
                'market_positioning': result.competitor_analysis.get('market_positioning', 'unknown'),
                'competitive_advantages': result.sales_opportunities.get('competitive_advantages', [])
            },
            'differentiation_opportunities': result.sales_opportunities.get('immediate_opportunities', [])
        }
        
        return jsonify(format_response(
            competitor_data,
            message="Competitor intelligence analysis completed"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Competitor intelligence error: {str(e)}")
        raise APIError("Competitor intelligence analysis failed", 500)

@app.route('/api/analyze/gohighlevel-recommendations', methods=['POST'])
@limiter.limit("15 per hour")
def analyze_gohighlevel_recommendations():
    """
    GoHighLevel service recommendations with industry-specific pricing
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Starting GoHighLevel recommendations for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        ghl_data = result.sales_opportunities.get('gohighlevel_services', {})
        
        if not ghl_data:
            raise APIError("No GoHighLevel recommendations available", 422)
        
        # Enhanced response with company context
        ghl_response = {
            'url': result.url,
            'timestamp': result.timestamp,
            'company_profile': {
                'company_name': result.company_profile.get('company_name', 'Unknown Company'),
                'industry': result.company_profile.get('industry', 'unknown'),
                'business_size': result.company_profile.get('business_size', 'unknown')
            },
            'gohighlevel_analysis': ghl_data,
            'lead_context': {
                'lead_quality': result.lead_scoring.get('lead_quality', 'unknown'),
                'overall_score': result.lead_scoring.get('overall_score', 0),
                'budget_level': result.budget_indicators.get('overall_budget_level', 'unknown')
            }
        }
        
        return jsonify(format_response(
            ghl_response,
            message=f"GoHighLevel recommendations generated for {result.company_profile.get('company_name', 'target company')}")
        )
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"GoHighLevel recommendations error: {str(e)}")
        raise APIError("GoHighLevel recommendations analysis failed", 500)

@app.route('/api/reports/gohighlevel-text', methods=['POST'])
@limiter.limit("10 per hour")
def gohighlevel_text_report():
    """
    GoHighLevel service recommendations as human-readable text report
    
    Request body:
    {
        "url": "https://example.com",
        "agency_name": "Your Agency Name",
        "contact_person": "Sales Rep Name"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        agency_name = data.get('agency_name', 'Your Agency')
        contact_person = data.get('contact_person', 'Sales Representative')
        
        logger.info(f"Generating GoHighLevel text report for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        ghl_data = result.sales_opportunities.get('gohighlevel_services', {})
        
        if not ghl_data:
            # Generate a "no opportunities" report
            text_report = formatter.format_header("GOHIGHLEVEL ANALYSIS REPORT", 
                                                 result.company_profile.get('company_name', 'Unknown Company'))
            text_report += "\n📋 ANALYSIS RESULTS\n"
            text_report += f"{formatter.subsection_separator}\n"
            text_report += "No specific GoHighLevel service gaps identified at this time.\n"
            text_report += "The current technology stack appears to meet basic automation needs.\n\n"
        else:
            # Generate full GoHighLevel report
            company_name = result.company_profile.get('company_name', 'Unknown Company')
            text_report = formatter.format_header("GOHIGHLEVEL SERVICE RECOMMENDATIONS", company_name)
            
            text_report += f"\n📍 COMPANY OVERVIEW\n"
            text_report += f"{formatter.subsection_separator}\n"
            text_report += f"Website: {result.url}\n"
            text_report += f"Industry: {result.company_profile.get('industry', 'Unknown').title()}\n"
            text_report += f"Business Size: {result.company_profile.get('business_size', 'Unknown')}\n"
            text_report += f"Lead Quality: {formatter._format_value(result.lead_scoring.get('lead_quality', 'unknown'))}\n"
            text_report += f"Budget Level: {formatter._format_value(result.budget_indicators.get('overall_budget_level', 'unknown'))}\n\n"
            
            # Add GoHighLevel recommendations
            text_report += formatter.format_gohighlevel_recommendations(ghl_data)
        
        # Add footer
        text_report += f"\n\n{formatter.section_separator}\n"
        text_report += f"GoHighLevel Analysis prepared by: {agency_name}\n"
        text_report += f"Contact: {contact_person}\n"
        text_report += f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        text_report += f"{formatter.section_separator}\n"
        
        logger.info(f"GoHighLevel text report completed for: {url}")
        
        return Response(text_report, mimetype='text/plain')
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"GoHighLevel text report error: {str(e)}")
        raise APIError("GoHighLevel text report generation failed", 500)

@app.route('/api/batch/lead-scoring', methods=['POST'])
@limiter.limit("3 per hour")
def batch_lead_scoring():
    """
    Batch lead scoring for multiple URLs
    
    Request body:
    {
        "urls": ["https://example1.com", "https://example2.com"],
        "agency_name": "Your Agency Name"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        urls = data.get('urls', [])
        agency_name = data.get('agency_name', 'Your Agency')
        
        if not urls or not isinstance(urls, list):
            raise APIError("URLs array is required", 400)
        
        if len(urls) > 5:
            raise APIError("Maximum 5 URLs allowed per batch", 400)
        
        logger.info(f"Starting batch lead scoring for {len(urls)} URLs")
        
        results = []
        
        for url in urls:
            try:
                validated_url = validate_url(url)
                result = analyzer.analyze_business_intelligence(validated_url)
                
                if result:
                    lead_summary = {
                        'url': result.url,
                        'company_name': result.company_profile.get('company_name', 'Unknown'),
                        'industry': result.company_profile.get('industry', 'Unknown'),
                        'lead_quality': result.lead_scoring.get('lead_quality', 'unknown'),
                        'overall_score': result.lead_scoring.get('overall_score', 0),
                        'deal_potential': result.lead_scoring.get('deal_size_estimate', 'unknown'),
                        'sales_priority': result.lead_scoring.get('sales_priority', 'unknown'),
                        'conversion_probability': result.lead_scoring.get('conversion_probability', 'unknown'),
                        'budget_level': result.budget_indicators.get('overall_budget_level', 'unknown'),
                        'social_presence': len(result.social_media_intelligence.get('platforms_found', {})),
                        'tech_sophistication': result.tech_stack_analysis.get('tech_sophistication_score', 0),
                        'contact_accessibility': result.contact_intelligence.get('contact_accessibility', 'unknown'),
                        'next_actions': result.lead_scoring.get('next_actions', [])[:3],  # Top 3 actions
                        'immediate_opportunities': len(result.sales_opportunities.get('immediate_opportunities', []))
                    }
                    
                    results.append({
                        'url': url,
                        'status': 'success',
                        'data': lead_summary
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
        
        # Sort results by lead score (highest first)
        successful_results = [r for r in results if r['status'] == 'success']
        successful_results.sort(key=lambda x: x['data'].get('overall_score', 0), reverse=True)
        
        batch_summary = {
            'batch_metadata': {
                'agency_name': agency_name,
                'analysis_date': datetime.now().strftime('%B %d, %Y'),
                'total_urls': len(urls),
                'successful_analyses': successful_analyses,
                'failed_analyses': len(urls) - successful_analyses
            },
            'results': results,
            'top_prospects': successful_results[:3],  # Top 3 prospects
            'summary_stats': {
                'premium_leads': len([r for r in successful_results if r['data'].get('lead_quality') == 'premium']),
                'qualified_leads': len([r for r in successful_results if r['data'].get('lead_quality') == 'qualified']),
                'average_score': sum(r['data'].get('overall_score', 0) for r in successful_results) / len(successful_results) if successful_results else 0,
                'high_budget_prospects': len([r for r in successful_results if r['data'].get('budget_level') in ['high', 'medium-high']]),
                'immediate_opportunities_total': sum(r['data'].get('immediate_opportunities', 0) for r in successful_results)
            }
        }
        
        logger.info(f"Batch lead scoring completed: {successful_analyses}/{len(urls)} successful")
        
        return jsonify(format_response(
            batch_summary,
            message=f"Batch lead scoring completed: {successful_analyses}/{len(urls)} prospects analyzed"
        ))
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Batch lead scoring error: {str(e)}")
        raise APIError("Batch lead scoring failed", 500)

@app.route('/api/reports/business-intelligence-text', methods=['POST'])
@limiter.limit("10 per hour")
def business_intelligence_text_report():
    """
    Complete business intelligence analysis with human-readable text report
    
    Request body:
    {
        "url": "https://example.com",
        "agency_name": "Your Agency Name",
        "contact_person": "Sales Rep Name"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        agency_name = data.get('agency_name', 'Your Agency')
        contact_person = data.get('contact_person', 'Sales Representative')
        
        logger.info(f"Generating text BI report for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website. Please check the URL and try again.", 422)
        
        # Generate human-readable report
        text_report = formatter.format_full_report(result, agency_name, contact_person)
        
        logger.info(f"Text BI report completed for: {url} - Lead Score: {result.lead_scoring.get('overall_score', 0)}")
        
        return Response(text_report, mimetype='text/plain')
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Text BI report error for {data.get('url', 'unknown')}: {str(e)}")
        logger.error(traceback.format_exc())
        raise APIError("Text business intelligence report generation failed", 500)

@app.route('/api/reports/sales-report-text', methods=['POST'])
@limiter.limit("10 per hour")
def sales_report_text():
    """
    Generate executive sales report in human-readable text format
    
    Request body:
    {
        "url": "https://example.com",
        "agency_name": "Your Agency Name",
        "contact_person": "Sales Rep Name"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        agency_name = data.get('agency_name', 'Your Agency')
        contact_person = data.get('contact_person', 'Sales Representative')
        
        logger.info(f"Generating text sales report for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        # Generate executive summary and opportunities report
        text_report = formatter.format_executive_summary(result)
        text_report += formatter.format_opportunities_section(result)
        
        # Add footer
        text_report += f"\n\n{formatter.section_separator}\n"
        text_report += f"Sales Report prepared by: {agency_name}\n"
        text_report += f"Contact: {contact_person}\n"
        text_report += f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        text_report += f"{formatter.section_separator}\n"
        
        logger.info(f"Text sales report completed for: {url} - Lead Quality: {result.lead_scoring.get('lead_quality', 'unknown')}")
        
        return Response(text_report, mimetype='text/plain')
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Text sales report error: {str(e)}")
        raise APIError("Text sales report generation failed", 500)

@app.route('/api/reports/lead-scoring-text', methods=['POST'])
@limiter.limit("15 per hour")
def lead_scoring_text():
    """
    Lead scoring analysis in human-readable text format
    
    Request body:
    {
        "url": "https://example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("Request body is required", 400)
        
        url = validate_url(data.get('url'))
        
        logger.info(f"Generating text lead scoring for: {url}")
        
        result = analyzer.analyze_business_intelligence(url)
        
        if not result:
            raise APIError("Failed to analyze website", 422)
        
        # Generate lead scoring focused report
        company_name = result.company_profile.get('company_name', 'Unknown Company')
        lead_data = result.lead_scoring
        
        text_report = formatter.format_header(f"LEAD SCORING REPORT", company_name)
        
        text_report += f"""
📍 LEAD ASSESSMENT SUMMARY
{formatter.subsection_separator}
Website: {result.url}
Analysis Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

🎯 SCORING BREAKDOWN
• Overall Score: {lead_data.get('overall_score', 0)}/100 points
• Lead Quality: {formatter._format_value(lead_data.get('lead_quality', 'unknown'))}
• Sales Priority: {formatter._format_value(lead_data.get('sales_priority', 'unknown'))}
• Deal Potential: {lead_data.get('deal_size_estimate', 'Unknown')}
• Conversion Probability: {formatter._format_value(lead_data.get('conversion_probability', 'unknown'))}
• Sales Cycle Estimate: {lead_data.get('sales_cycle_estimate', 'Unknown')}

🏢 COMPANY PROFILE
• Industry: {result.company_profile.get('industry', 'Unknown').title()}
• Business Size: {result.company_profile.get('business_size', 'Unknown')}
• Location: {result.company_profile.get('location', 'Unknown')}
• Employees: {result.company_profile.get('employees', 'Unknown')}

💰 BUDGET INDICATORS
• Overall Budget Level: {formatter._format_value(result.budget_indicators.get('overall_budget_level', 'unknown'))}
• Monthly Spend Estimate: {result.budget_indicators.get('monthly_spend_estimate', 'Unknown')}
• Investment Capacity: {formatter._format_value(result.budget_indicators.get('investment_capacity', 'unknown'))}

📝 RECOMMENDED NEXT ACTIONS
"""
        
        next_actions = lead_data.get('next_actions', [])
        for i, action in enumerate(next_actions, 1):
            text_report += f"{i}. {action.replace('_', ' ').title()}\n"
        
        text_report += f"\n{formatter.section_separator}\n"
        text_report += f"Lead Scoring Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        text_report += f"{formatter.section_separator}\n"
        
        logger.info(f"Text lead scoring completed for: {url} - Score: {result.lead_scoring.get('overall_score', 0)}")
        
        return Response(text_report, mimetype='text/plain')
        
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Text lead scoring error: {str(e)}")
        raise APIError("Text lead scoring analysis failed", 500)

@app.route('/api/docs/business-intelligence', methods=['GET'])
def bi_api_documentation():
    """Business Intelligence API documentation"""
    docs = {
        'title': 'Business Intelligence API Documentation',
        'version': '1.0.0',
        'description': 'Comprehensive business intelligence analysis API for agency sales teams',
        'base_url': request.base_url.replace('/api/docs/business-intelligence', ''),
        'endpoints': {
            'business_intelligence': {
                'url': '/api/analyze/business-intelligence',
                'method': 'POST',
                'description': 'Complete business intelligence analysis including all components',
                'rate_limit': '10 requests per hour',
                'request_body': {'url': 'Website URL to analyze (required)'},
                'response_includes': [
                    'company_profile', 'social_media_intelligence', 'tech_stack_analysis',
                    'competitor_analysis', 'budget_indicators', 'traffic_analysis',
                    'contact_intelligence', 'lead_scoring', 'sales_opportunities', 'unified_report'
                ]
            },
            'business_intelligence_text': {
                'url': '/api/reports/business-intelligence-text',
                'method': 'POST',
                'description': 'Complete business intelligence analysis as human-readable text report',
                'rate_limit': '10 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)',
                    'agency_name': 'Your agency name (optional)',
                    'contact_person': 'Sales rep name (optional)'
                },
                'response_format': 'text/plain'
            },
            'lead_scoring': {
                'url': '/api/analyze/lead-scoring',
                'method': 'POST',
                'description': 'Lead quality scoring and sales potential assessment',
                'rate_limit': '15 requests per hour',
                'request_body': {'url': 'Website URL to analyze (required)'}
            },
            'sales_report': {
                'url': '/api/analyze/sales-report',
                'method': 'POST',
                'description': 'Generate executive sales report with proposal framework',
                'rate_limit': '10 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)',
                    'agency_name': 'Your agency name (optional)',
                    'contact_person': 'Sales rep name (optional)'
                }
            },
            'social_intelligence': {
                'url': '/api/analyze/social-intelligence',
                'method': 'POST',
                'description': 'Social media presence and advertising analysis',
                'rate_limit': '20 requests per hour'
            },
            'tech_stack': {
                'url': '/api/analyze/tech-stack',
                'method': 'POST',
                'description': 'Technology stack detection and modernization opportunities',
                'rate_limit': '20 requests per hour'
            },
            'competitor_intelligence': {
                'url': '/api/analyze/competitor-intelligence',
                'method': 'POST',
                'description': 'Competitor identification and market positioning analysis',
                'rate_limit': '15 requests per hour'
            },
            'gohighlevel_recommendations': {
                'url': '/api/analyze/gohighlevel-recommendations',
                'method': 'POST',
                'description': 'GoHighLevel service recommendations with industry-specific pricing',
                'rate_limit': '15 requests per hour',
                'request_body': {'url': 'Website URL to analyze (required)'},
                'response_includes': [
                    'service_recommendations', 'investment_summary', 'implementation_roadmap',
                    'ai_chatbot_setup', 'google_review_automation', 'missed_call_text_back',
                    'appointment_booking', 'email_sms_sequences', 'lead_magnets', 'funnel_optimization'
                ]
            },
            'gohighlevel_text_report': {
                'url': '/api/reports/gohighlevel-text',
                'method': 'POST',
                'description': 'GoHighLevel service recommendations as human-readable text report',
                'rate_limit': '10 requests per hour',
                'request_body': {
                    'url': 'Website URL to analyze (required)',
                    'agency_name': 'Your agency name (optional)',
                    'contact_person': 'Sales rep name (optional)'
                },
                'response_format': 'text/plain'
            },
            'batch_lead_scoring': {
                'url': '/api/batch/lead-scoring',
                'method': 'POST',
                'description': 'Batch lead scoring for multiple prospects',
                'rate_limit': '3 requests per hour',
                'request_body': {
                    'urls': 'Array of URLs to analyze (required, max 5)',
                    'agency_name': 'Your agency name (optional)'
                }
            }
        },
        'lead_scoring_system': {
            'total_points': 100,
            'categories': {
                'company_profile': '25 points (industry fit, size, location)',
                'social_intelligence': '20 points (presence, advertising, strategy)',
                'technology': '20 points (sophistication, opportunities)',
                'budget': '25 points (spending level, capacity)',
                'contact_accessibility': '10 points (contact info, decision makers)'
            },
            'quality_levels': {
                'premium': '80-100 points (immediate action, high deal value)',
                'qualified': '60-79 points (high priority, good potential)',
                'potential': '40-59 points (medium priority, nurture)',
                'nurture': '0-39 points (long-term relationship building)'
            }
        },
        'agency_integration': {
            'description': 'Designed specifically for digital marketing agencies and sales teams',
            'use_cases': [
                'Prospect qualification and prioritization',
                'Sales proposal preparation',
                'Competitive analysis and positioning',
                'Service recommendation and pricing',
                'Lead nurturing and follow-up planning'
            ],
            'crm_integration': 'JSON responses can be easily integrated with CRM systems',
            'reporting': 'Executive-level reports suitable for client presentations'
        },
        'gohighlevel_services': {
            'description': 'Specialized GoHighLevel service recommendations with industry-specific pricing',
            'available_services': [
                'AI Chatbot Setup ($500-$3,000 setup + $100-$600/month)',
                'Google Review Automation ($560-$1,120 setup + $105-$210/month)',
                'Missed Call Text Back ($350-$700 setup + $70-$140/month)',
                'Appointment Booking System ($840-$1,680 setup + $140-$280/month)',
                'Email/SMS Sequences ($1,400-$2,800 setup + $280-$560/month)',
                'Lead Magnets Creation ($1,050-$2,100 setup + $175-$350/month)',
                'Funnel Optimization ($1,750-$3,500 setup + $350-$700/month)'
            ],
            'industry_multipliers': {
                'healthcare': '1.3x pricing',
                'legal': '1.4x pricing',
                'real_estate': '1.2x pricing',
                'finance': '1.5x pricing',
                'automotive': '1.1x pricing',
                'fitness': '1.0x pricing',
                'restaurants': '0.9x pricing',
                'retail': '0.8x pricing',
                'construction': '1.2x pricing',
                'beauty': '1.0x pricing'
            },
            'implementation_phases': [
                'Phase 1: Quick Wins (1-2 weeks) - Immediate impact services',
                'Phase 2: Core Automation (3-4 weeks) - Essential workflows',
                'Phase 3: Advanced Optimization (5-6 weeks) - Comprehensive funnels'
            ]
        }
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False).lower() == 'true'
    
    logger.info(f"Starting Business Intelligence API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)