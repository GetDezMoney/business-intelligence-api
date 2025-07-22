#!/usr/bin/env python3
"""
Business Intelligence Website Analyzer

Advanced website analysis tool designed for agency sales teams.
Provides comprehensive business intelligence including social media discovery,
tech stack detection, competitor analysis, budget indicators, and unified reporting.
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set, Tuple
from bs4 import BeautifulSoup, Comment
import argparse
from datetime import datetime
import time
import hashlib
import base64
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BusinessIntelligenceResult:
    """Container for comprehensive business intelligence analysis"""
    url: str
    timestamp: str
    company_profile: Dict
    social_media_intelligence: Dict
    tech_stack_analysis: Dict
    competitor_analysis: Dict
    budget_indicators: Dict
    traffic_analysis: Dict
    contact_intelligence: Dict
    lead_scoring: Dict
    sales_opportunities: Dict
    unified_report: Dict

class BusinessIntelligenceAnalyzer:
    """Comprehensive business intelligence analyzer for agency sales"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Social media platforms and patterns
        self.social_platforms = {
            'facebook': {
                'patterns': [r'facebook\.com/([^/?]+)', r'fb\.com/([^/?]+)'],
                'business_indicators': ['business', 'pages', 'profile.php'],
                'weight': 10
            },
            'instagram': {
                'patterns': [r'instagram\.com/([^/?]+)', r'instagr\.am/([^/?]+)'],
                'business_indicators': ['business'],
                'weight': 8
            },
            'twitter': {
                'patterns': [r'twitter\.com/([^/?]+)', r'x\.com/([^/?]+)'],
                'business_indicators': ['business'],
                'weight': 7
            },
            'linkedin': {
                'patterns': [r'linkedin\.com/(?:company/|in/)([^/?]+)'],
                'business_indicators': ['company', 'showcase'],
                'weight': 15
            },
            'youtube': {
                'patterns': [r'youtube\.com/(?:c/|channel/|user/)([^/?]+)', r'youtu\.be/([^/?]+)'],
                'business_indicators': ['channel', 'user'],
                'weight': 6
            },
            'tiktok': {
                'patterns': [r'tiktok\.com/@([^/?]+)'],
                'business_indicators': ['business'],
                'weight': 5
            },
            'pinterest': {
                'patterns': [r'pinterest\.com/([^/?]+)'],
                'business_indicators': ['business'],
                'weight': 4
            }
        }
        
        # Technology detection patterns
        self.tech_patterns = {
            # CMS & Frameworks
            'wordpress': {
                'patterns': [r'wp-content', r'wp-includes', r'/wordpress/'],
                'indicators': ['wp-json', 'xmlrpc.php'],
                'category': 'cms',
                'cost_indicator': 'low',
                'agency_opportunity': 'high'
            },
            'shopify': {
                'patterns': [r'cdn\.shopify\.com', r'shopify\.com', r'myshopify\.com'],
                'indicators': ['Shopify.shop', 'shop_money_format'],
                'category': 'ecommerce',
                'cost_indicator': 'medium',
                'agency_opportunity': 'high'
            },
            'wix': {
                'patterns': [r'wix\.com', r'wixstatic\.com', r'wixsite\.com'],
                'indicators': ['wixCode', 'wix-warmup'],
                'category': 'cms',
                'cost_indicator': 'low',
                'agency_opportunity': 'medium'
            },
            'squarespace': {
                'patterns': [r'squarespace\.com', r'sqspcdn\.com'],
                'indicators': ['squarespace-cdn'],
                'category': 'cms',
                'cost_indicator': 'low',
                'agency_opportunity': 'medium'
            },
            'hubspot': {
                'patterns': [r'hubspot\.com', r'hs-scripts\.com', r'hsforms\.com'],
                'indicators': ['hubspot', 'hsjs'],
                'category': 'marketing',
                'cost_indicator': 'high',
                'agency_opportunity': 'low'
            },
            'salesforce': {
                'patterns': [r'salesforce\.com', r'force\.com'],
                'indicators': ['salesforce', 'sfdc'],
                'category': 'crm',
                'cost_indicator': 'high',
                'agency_opportunity': 'medium'
            },
            'marketo': {
                'patterns': [r'marketo\.com', r'mktoresp\.com'],
                'indicators': ['marketo', 'mktApi'],
                'category': 'marketing',
                'cost_indicator': 'high',
                'agency_opportunity': 'low'
            },
            'pardot': {
                'patterns': [r'pardot\.com', r'pi\.pardot\.com'],
                'indicators': ['pardot'],
                'category': 'marketing',
                'cost_indicator': 'high',
                'agency_opportunity': 'low'
            },
            'custom_development': {
                'patterns': [r'react', r'angular', r'vue\.js', r'node\.js'],
                'indicators': ['webpack', 'babel'],
                'category': 'custom',
                'cost_indicator': 'high',
                'agency_opportunity': 'low'
            }
        }
        
        # Marketing tools and advertising patterns
        self.marketing_tools = {
            'google_ads': {
                'patterns': [r'googleadservices\.com', r'googlesyndication\.com'],
                'indicators': ['gads', 'google_ad'],
                'budget_indicator': 'medium-high'
            },
            'facebook_ads': {
                'patterns': [r'connect\.facebook\.net', r'facebook\.com/tr'],
                'indicators': ['fbevents.js', 'facebook-jssdk'],
                'budget_indicator': 'medium-high'
            },
            'microsoft_ads': {
                'patterns': [r'bat\.bing\.com', r'uetq'],
                'indicators': ['UET'],
                'budget_indicator': 'medium'
            },
            'twitter_ads': {
                'patterns': [r'ads-twitter\.com', r'analytics\.twitter\.com'],
                'indicators': ['twitter_ads'],
                'budget_indicator': 'medium'
            },
            'linkedin_ads': {
                'patterns': [r'snap\.licdn\.com', r'linkedin\.com/analytics'],
                'indicators': ['linkedin_insight'],
                'budget_indicator': 'high'
            },
            'tiktok_ads': {
                'patterns': [r'analytics\.tiktok\.com', r'business-api\.tiktok\.com'],
                'indicators': ['tiktok_ads'],
                'budget_indicator': 'medium'
            }
        }
        
        # Business size indicators
        self.business_size_indicators = {
            'enterprise': {
                'tech_stack': ['salesforce', 'marketo', 'pardot', 'hubspot'],
                'employee_keywords': ['1000+', 'enterprise', 'fortune'],
                'budget_indicator': 'very_high'
            },
            'mid_market': {
                'tech_stack': ['hubspot', 'mailchimp', 'shopify_plus'],
                'employee_keywords': ['50-1000', 'mid-size', '100-500'],
                'budget_indicator': 'high'
            },
            'smb': {
                'tech_stack': ['wordpress', 'shopify', 'wix', 'squarespace'],
                'employee_keywords': ['1-50', 'small business', 'startup'],
                'budget_indicator': 'medium'
            },
            'solopreneur': {
                'tech_stack': ['wix', 'squarespace', 'wordpress.com'],
                'employee_keywords': ['solo', 'freelance', 'individual'],
                'budget_indicator': 'low'
            }
        }
        
        # Industry classification patterns
        self.industry_patterns = {
            'saas': {
                'keywords': ['software', 'saas', 'platform', 'api', 'cloud', 'subscription'],
                'budget_indicator': 'high',
                'agency_fit': 'excellent'
            },
            'ecommerce': {
                'keywords': ['shop', 'buy', 'cart', 'checkout', 'products', 'store'],
                'budget_indicator': 'medium-high',
                'agency_fit': 'excellent'
            },
            'healthcare': {
                'keywords': ['medical', 'health', 'doctor', 'clinic', 'patient'],
                'budget_indicator': 'high',
                'agency_fit': 'good'
            },
            'finance': {
                'keywords': ['bank', 'finance', 'investment', 'loan', 'insurance'],
                'budget_indicator': 'high',
                'agency_fit': 'good'
            },
            'real_estate': {
                'keywords': ['real estate', 'property', 'homes', 'listings'],
                'budget_indicator': 'medium',
                'agency_fit': 'excellent'
            },
            'legal': {
                'keywords': ['law', 'lawyer', 'attorney', 'legal', 'court'],
                'budget_indicator': 'high',
                'agency_fit': 'good'
            },
            'consulting': {
                'keywords': ['consulting', 'consultant', 'advisory', 'strategy'],
                'budget_indicator': 'medium-high',
                'agency_fit': 'excellent'
            }
        }

    def fetch_website(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse website content with error handling"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_company_profile(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract comprehensive company profile information"""
        profile = {
            'company_name': None,
            'industry': None,
            'business_size': None,
            'description': None,
            'location': None,
            'founded': None,
            'employees': None,
            'revenue_indicators': [],
            'business_model': None,
            'target_market': None
        }
        
        # Extract company name
        title = soup.find('title')
        if title:
            profile['company_name'] = title.get_text().strip()
        
        # Look for company description in meta tags
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            profile['description'] = desc_tag.get('content', '').strip()
        
        # Detect industry based on content
        page_text = soup.get_text().lower()
        industry_scores = {}
        
        for industry, data in self.industry_patterns.items():
            score = sum(1 for keyword in data['keywords'] if keyword in page_text)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            profile['industry'] = max(industry_scores, key=industry_scores.get)
        
        # Extract location information
        location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'  # City, Country
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                profile['location'] = f"{matches[0][0]}, {matches[0][1]}"
                break
        
        # Look for employee count indicators
        employee_patterns = [
            r'(\d+[\+]?)\s*employees?',
            r'team\s*of\s*(\d+)',
            r'(\d+)-(\d+)\s*people'
        ]
        
        for pattern in employee_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    profile['employees'] = f"{matches[0][0]}-{matches[0][1]}"
                else:
                    profile['employees'] = matches[0]
                break
        
        return profile

    def analyze_social_media_intelligence(self, soup: BeautifulSoup, url: str) -> Dict:
        """Comprehensive social media discovery and intelligence with detailed profile analysis"""
        social_intel = {
            'platforms_found': {},
            'social_engagement_score': 0,
            'social_budget_indicators': [],
            'social_strategy_assessment': {},
            'missing_opportunities': [],
            'competitor_social_gaps': [],
            'social_lead_potential': 'unknown',
            'detailed_analysis': {},
            'content_strategy_gaps': [],
            'engagement_optimization': {},
            'cross_platform_analysis': {}
        }
        
        page_html = str(soup)
        page_text = soup.get_text().lower()
        links = soup.find_all('a', href=True)
        
        # Discover social media profiles
        for platform, config in self.social_platforms.items():
            platform_data = {
                'url': None,
                'username': None,
                'business_account': False,
                'engagement_indicators': [],
                'pixel_detected': False,
                'advertising_detected': False
            }
            
            # Check links for social profiles
            for link in links:
                href = link.get('href', '').lower()
                for pattern in config['patterns']:
                    match = re.search(pattern, href)
                    if match:
                        platform_data['url'] = href
                        platform_data['username'] = match.group(1) if match.groups() else None
                        
                        # Check if it's a business account
                        if any(indicator in href for indicator in config['business_indicators']):
                            platform_data['business_account'] = True
                        
                        break
                
                if platform_data['url']:
                    break
            
            # Check for advertising pixels and tracking
            pixel_patterns = {
                'facebook': [r'connect\.facebook\.net', r'facebook\.com/tr'],
                'twitter': [r'analytics\.twitter\.com', r'ads-twitter\.com'],
                'linkedin': [r'snap\.licdn\.com', r'linkedin\.com/analytics'],
                'tiktok': [r'analytics\.tiktok\.com']
            }
            
            if platform in pixel_patterns:
                for pattern in pixel_patterns[platform]:
                    if re.search(pattern, page_html):
                        platform_data['pixel_detected'] = True
                        platform_data['advertising_detected'] = True
                        social_intel['social_budget_indicators'].append(f"{platform}_ads")
                        break
            
            if platform_data['url'] or platform_data['pixel_detected']:
                social_intel['platforms_found'][platform] = platform_data
                social_intel['social_engagement_score'] += config['weight']
        
        # Assess social strategy
        platforms_count = len(social_intel['platforms_found'])
        active_advertising = len(social_intel['social_budget_indicators'])
        
        if platforms_count >= 4 and active_advertising >= 2:
            social_intel['social_strategy_assessment'] = {
                'maturity': 'advanced',
                'budget_level': 'high',
                'agency_opportunity': 'optimization'
            }
        elif platforms_count >= 2:
            social_intel['social_strategy_assessment'] = {
                'maturity': 'developing',
                'budget_level': 'medium',
                'agency_opportunity': 'expansion'
            }
        else:
            social_intel['social_strategy_assessment'] = {
                'maturity': 'basic',
                'budget_level': 'low',
                'agency_opportunity': 'implementation'
            }
        
        # Identify missing opportunities
        if 'linkedin' not in social_intel['platforms_found'] and 'b2b' in page_text:
            social_intel['missing_opportunities'].append('linkedin_b2b')
        
        if 'instagram' not in social_intel['platforms_found'] and any(keyword in page_text for keyword in ['visual', 'product', 'lifestyle']):
            social_intel['missing_opportunities'].append('instagram_visual')
        
        if not social_intel['social_budget_indicators']:
            social_intel['missing_opportunities'].append('social_advertising')
        
        # Calculate lead potential
        if platforms_count >= 3 and active_advertising >= 1:
            social_intel['social_lead_potential'] = 'high'
        elif platforms_count >= 2:
            social_intel['social_lead_potential'] = 'medium'
        else:
            social_intel['social_lead_potential'] = 'low'
        
        # Enhanced detailed analysis
        social_intel['detailed_analysis'] = self._analyze_social_media_details(social_intel, page_text, soup, url)
        
        # Content strategy gap analysis
        social_intel['content_strategy_gaps'] = self._identify_content_gaps(social_intel, page_text)
        
        # Engagement optimization opportunities
        social_intel['engagement_optimization'] = self._analyze_engagement_opportunities(social_intel, platforms_count, active_advertising)
        
        # Cross-platform analysis
        social_intel['cross_platform_analysis'] = self._analyze_cross_platform_strategy(social_intel)
        
        return social_intel
    
    def _analyze_social_media_details(self, social_intel, page_text, soup, url):
        """Perform detailed analysis of social media presence"""
        analysis = {
            'profile_completeness': {},
            'content_quality_indicators': {},
            'audience_engagement_signals': {},
            'business_optimization_level': {},
            'competitive_positioning': {},
            'growth_indicators': {}
        }
        
        platforms = social_intel.get('platforms_found', {})
        
        for platform, data in platforms.items():
            platform_analysis = {
                'profile_strength': 'unknown',
                'content_indicators': [],
                'business_features': [],
                'engagement_signals': [],
                'optimization_score': 0
            }
            
            # Profile completeness analysis
            if data.get('business_account'):
                platform_analysis['business_features'].append('Business account verified')
                platform_analysis['optimization_score'] += 25
            
            if data.get('pixel_detected'):
                platform_analysis['business_features'].append('Tracking pixel installed')
                platform_analysis['optimization_score'] += 20
            
            if data.get('advertising_detected'):
                platform_analysis['business_features'].append('Active advertising campaigns')
                platform_analysis['optimization_score'] += 30
            
            # Content strategy indicators
            content_keywords = {
                'facebook': ['community', 'engagement', 'local', 'events'],
                'instagram': ['visual', 'stories', 'hashtags', 'photos'],
                'linkedin': ['professional', 'b2b', 'networking', 'industry'],
                'twitter': ['news', 'updates', 'customer service', 'trending'],
                'youtube': ['video', 'tutorials', 'educational', 'channel']
            }
            
            if platform in content_keywords:
                found_keywords = [kw for kw in content_keywords[platform] if kw in page_text]
                platform_analysis['content_indicators'] = found_keywords
                platform_analysis['optimization_score'] += len(found_keywords) * 5
            
            # Determine profile strength
            if platform_analysis['optimization_score'] >= 70:
                platform_analysis['profile_strength'] = 'excellent'
            elif platform_analysis['optimization_score'] >= 50:
                platform_analysis['profile_strength'] = 'good'
            elif platform_analysis['optimization_score'] >= 25:
                platform_analysis['profile_strength'] = 'developing'
            else:
                platform_analysis['profile_strength'] = 'basic'
            
            analysis['profile_completeness'][platform] = platform_analysis
        
        # Overall business optimization assessment
        total_platforms = len(platforms)
        avg_optimization = sum(
            analysis['profile_completeness'][p]['optimization_score'] 
            for p in analysis['profile_completeness']
        ) / max(total_platforms, 1)
        
        analysis['business_optimization_level'] = {
            'overall_score': avg_optimization,
            'level': 'advanced' if avg_optimization >= 70 else 'moderate' if avg_optimization >= 40 else 'basic',
            'improvement_potential': 100 - avg_optimization
        }
        
        return analysis
    
    def _identify_content_gaps(self, social_intel, page_text):
        """Identify content strategy gaps and opportunities"""
        gaps = []
        platforms = social_intel.get('platforms_found', {})
        
        # Video content gap analysis
        if 'youtube' not in platforms and 'video' in page_text:
            gaps.append({
                'gap': 'video_content_strategy',
                'platform': 'youtube',
                'opportunity': 'Educational video content creation',
                'priority': 'high',
                'estimated_impact': 'Increased engagement and authority building'
            })
        
        # Visual content gaps
        if 'instagram' not in platforms and any(keyword in page_text for keyword in ['product', 'visual', 'design']):
            gaps.append({
                'gap': 'visual_storytelling',
                'platform': 'instagram',
                'opportunity': 'Product showcase and behind-the-scenes content',
                'priority': 'high',
                'estimated_impact': 'Enhanced brand awareness and customer connection'
            })
        
        # Professional networking gaps
        if 'linkedin' not in platforms and any(keyword in page_text for keyword in ['b2b', 'professional', 'services']):
            gaps.append({
                'gap': 'professional_networking',
                'platform': 'linkedin',
                'opportunity': 'Thought leadership and B2B relationship building',
                'priority': 'medium',
                'estimated_impact': 'Improved lead generation and industry credibility'
            })
        
        # Community engagement gaps
        if len(platforms) < 2:
            gaps.append({
                'gap': 'multi_platform_presence',
                'platform': 'multiple',
                'opportunity': 'Diversified social media strategy',
                'priority': 'high',
                'estimated_impact': 'Broader audience reach and reduced platform dependency'
            })
        
        # Advertising gaps
        if not social_intel.get('social_budget_indicators'):
            gaps.append({
                'gap': 'paid_social_strategy',
                'platform': 'multiple',
                'opportunity': 'Targeted advertising campaigns',
                'priority': 'medium',
                'estimated_impact': 'Accelerated growth and precise audience targeting'
            })
        
        return gaps
    
    def _analyze_engagement_opportunities(self, social_intel, platforms_count, active_advertising):
        """Analyze engagement optimization opportunities"""
        opportunities = {
            'immediate_actions': [],
            'short_term_strategy': [],
            'long_term_initiatives': [],
            'engagement_score': social_intel.get('social_engagement_score', 0),
            'optimization_potential': {}
        }
        
        # Immediate actions (1-2 weeks)
        if platforms_count == 0:
            opportunities['immediate_actions'].extend([
                'Create primary business social media profiles',
                'Establish consistent brand presence across platforms',
                'Set up basic business information and contact details'
            ])
        elif platforms_count < 3:
            opportunities['immediate_actions'].extend([
                'Expand to additional relevant social platforms',
                'Optimize existing profile completeness',
                'Implement cross-platform linking strategy'
            ])
        
        if active_advertising == 0:
            opportunities['immediate_actions'].append('Set up basic social media advertising pixels')
        
        # Short-term strategy (1-3 months)
        opportunities['short_term_strategy'].extend([
            'Develop content calendar and posting schedule',
            'Implement hashtag and keyword strategy',
            'Create engagement-focused content series',
            'Set up social media monitoring and analytics'
        ])
        
        if active_advertising < 2:
            opportunities['short_term_strategy'].append('Launch targeted advertising campaigns')
        
        # Long-term initiatives (3-12 months)
        opportunities['long_term_initiatives'].extend([
            'Build community-driven content strategy',
            'Implement advanced audience segmentation',
            'Develop influencer partnership program',
            'Create comprehensive social media ROI tracking'
        ])
        
        # Optimization potential
        current_score = opportunities['engagement_score']
        max_possible = sum(config['weight'] for config in self.social_platforms.values())
        
        opportunities['optimization_potential'] = {
            'current_percentage': (current_score / max_possible) * 100 if max_possible > 0 else 0,
            'improvement_opportunity': max_possible - current_score,
            'next_milestone': self._get_next_engagement_milestone(current_score, max_possible)
        }
        
        return opportunities
    
    def _get_next_engagement_milestone(self, current_score, max_score):
        """Get next engagement milestone target"""
        percentage = (current_score / max_score) * 100 if max_score > 0 else 0
        
        if percentage < 25:
            return {
                'target': 'Basic presence established',
                'score_needed': int(max_score * 0.25),
                'actions': ['Add 2-3 primary social platforms', 'Complete business profiles']
            }
        elif percentage < 50:
            return {
                'target': 'Moderate social presence',
                'score_needed': int(max_score * 0.5),
                'actions': ['Add advertising pixels', 'Expand platform presence']
            }
        elif percentage < 75:
            return {
                'target': 'Strong social engagement',
                'score_needed': int(max_score * 0.75),
                'actions': ['Optimize all platforms', 'Launch paid campaigns']
            }
        else:
            return {
                'target': 'Social media excellence',
                'score_needed': max_score,
                'actions': ['Advanced targeting', 'Community building', 'Influencer partnerships']
            }
    
    def _analyze_cross_platform_strategy(self, social_intel):
        """Analyze cross-platform strategy and coherence"""
        analysis = {
            'consistency_score': 0,
            'platform_synergy': {},
            'missing_integrations': [],
            'cross_promotion_opportunities': [],
            'unified_strategy_recommendations': []
        }
        
        platforms = social_intel.get('platforms_found', {})
        platform_count = len(platforms)
        
        # Consistency analysis
        business_accounts = sum(1 for p in platforms.values() if p.get('business_account'))
        pixel_setups = sum(1 for p in platforms.values() if p.get('pixel_detected'))
        
        if platform_count > 0:
            analysis['consistency_score'] = ((business_accounts + pixel_setups) / (platform_count * 2)) * 100
        
        # Platform synergy analysis
        platform_combinations = {
            ('facebook', 'instagram'): 'Meta ecosystem integration opportunity',
            ('linkedin', 'twitter'): 'Professional networking synergy',
            ('youtube', 'instagram'): 'Video and visual content cross-promotion',
            ('facebook', 'youtube'): 'Community and educational content strategy'
        }
        
        found_platforms = set(platforms.keys())
        for combo, benefit in platform_combinations.items():
            if all(platform in found_platforms for platform in combo):
                analysis['platform_synergy'][combo] = {
                    'benefit': benefit,
                    'implemented': True,
                    'optimization_level': 'good' if all(platforms[p].get('business_account') for p in combo) else 'basic'
                }
            elif any(platform in found_platforms for platform in combo):
                analysis['missing_integrations'].append({
                    'platforms': combo,
                    'missing': [p for p in combo if p not in found_platforms],
                    'benefit': benefit
                })
        
        # Cross-promotion opportunities
        if platform_count >= 2:
            analysis['cross_promotion_opportunities'] = [
                'Link social profiles for cross-traffic',
                'Share content across platforms with platform-specific optimization',
                'Create unified hashtag and branding strategy',
                'Implement cross-platform contest and engagement campaigns'
            ]
        
        # Unified strategy recommendations
        if analysis['consistency_score'] < 50:
            analysis['unified_strategy_recommendations'].append('Standardize business account setup across all platforms')
        
        if not social_intel.get('social_budget_indicators'):
            analysis['unified_strategy_recommendations'].append('Implement unified tracking and analytics across platforms')
        
        if platform_count < 3:
            analysis['unified_strategy_recommendations'].append('Expand platform presence for comprehensive market coverage')
        
        return analysis

    def analyze_tech_stack(self, soup: BeautifulSoup, url: str) -> Dict:
        """Advanced technology stack detection and analysis"""
        tech_analysis = {
            'detected_technologies': {},
            'tech_sophistication_score': 0,
            'migration_opportunities': [],
            'integration_gaps': [],
            'budget_implications': {},
            'agency_opportunities': [],
            'competitive_tech_advantage': 'unknown',
            'modernization_needs': []
        }
        
        page_html = str(soup).lower()
        page_text = soup.get_text().lower()
        scripts = soup.find_all('script')
        links = soup.find_all('link')
        
        # Detect technologies
        for tech, config in self.tech_patterns.items():
            detection_score = 0
            evidence = []
            
            # Check patterns in HTML
            for pattern in config['patterns']:
                if re.search(pattern, page_html):
                    detection_score += 2
                    evidence.append(f"pattern_{pattern}")
            
            # Check specific indicators
            for indicator in config.get('indicators', []):
                if indicator.lower() in page_html:
                    detection_score += 3
                    evidence.append(f"indicator_{indicator}")
            
            # Check scripts and links
            for script in scripts:
                if script.get('src'):
                    src = script.get('src').lower()
                    for pattern in config['patterns']:
                        if re.search(pattern, src):
                            detection_score += 3
                            evidence.append(f"script_{pattern}")
            
            for link in links:
                if link.get('href'):
                    href = link.get('href').lower()
                    for pattern in config['patterns']:
                        if re.search(pattern, href):
                            detection_score += 2
                            evidence.append(f"link_{pattern}")
            
            if detection_score > 0:
                tech_analysis['detected_technologies'][tech] = {
                    'confidence': min(detection_score * 10, 100),
                    'evidence': evidence,
                    'category': config['category'],
                    'cost_indicator': config['cost_indicator'],
                    'agency_opportunity': config['agency_opportunity']
                }
                
                tech_analysis['tech_sophistication_score'] += detection_score
        
        # Analyze budget implications
        high_cost_techs = [tech for tech, data in tech_analysis['detected_technologies'].items() 
                          if data['cost_indicator'] == 'high']
        
        medium_cost_techs = [tech for tech, data in tech_analysis['detected_technologies'].items() 
                           if data['cost_indicator'] == 'medium']
        
        if high_cost_techs:
            tech_analysis['budget_implications']['level'] = 'high'
            tech_analysis['budget_implications']['monthly_estimate'] = '$5000-$50000+'
        elif medium_cost_techs:
            tech_analysis['budget_implications']['level'] = 'medium'
            tech_analysis['budget_implications']['monthly_estimate'] = '$1000-$5000'
        else:
            tech_analysis['budget_implications']['level'] = 'low'
            tech_analysis['budget_implications']['monthly_estimate'] = '$100-$1000'
        
        # Identify agency opportunities
        high_opportunity_techs = [tech for tech, data in tech_analysis['detected_technologies'].items() 
                                if data['agency_opportunity'] == 'high']
        
        if 'wordpress' in tech_analysis['detected_technologies']:
            tech_analysis['agency_opportunities'].append('wordpress_optimization')
        
        if 'shopify' in tech_analysis['detected_technologies']:
            tech_analysis['agency_opportunities'].append('ecommerce_optimization')
        
        if not any('marketing' in data['category'] for data in tech_analysis['detected_technologies'].values()):
            tech_analysis['agency_opportunities'].append('marketing_automation_implementation')
        
        # Check for modernization needs
        legacy_indicators = ['jquery-1.', 'bootstrap-2.', 'ie-conditional']
        for indicator in legacy_indicators:
            if indicator in page_html:
                tech_analysis['modernization_needs'].append(f"legacy_{indicator}")
        
        return tech_analysis

    def analyze_competitors(self, soup: BeautifulSoup, url: str) -> Dict:
        """Competitor identification and analysis"""
        competitor_analysis = {
            'identified_competitors': [],
            'competitive_landscape': {},
            'market_positioning': 'unknown',
            'competitive_advantages': [],
            'competitive_gaps': [],
            'market_opportunity_score': 0,
            'competitive_intelligence': {}
        }
        
        page_text = soup.get_text().lower()
        
        # Look for competitor mentions
        competitor_keywords = [
            'vs ', 'versus', 'compared to', 'alternative to', 'competitor',
            'leading', 'market leader', 'industry standard'
        ]
        
        competitor_mentions = []
        for keyword in competitor_keywords:
            if keyword in page_text:
                # Extract sentences containing competitor keywords
                sentences = re.split(r'[.!?]', page_text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence) < 200:
                        competitor_mentions.append(sentence.strip())
        
        # Extract potential competitor names
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|LLC|Corp|Company|Solutions|Services)\b',
            r'\b[A-Z][a-z]+[A-Z][a-z]+\b'  # CamelCase company names
        ]
        
        potential_competitors = set()
        for mention in competitor_mentions:
            for pattern in company_patterns:
                matches = re.findall(pattern, mention)
                potential_competitors.update(matches)
        
        competitor_analysis['identified_competitors'] = list(potential_competitors)[:10]
        
        # Analyze market positioning
        positioning_indicators = {
            'premium': ['premium', 'luxury', 'high-end', 'exclusive'],
            'budget': ['affordable', 'cheap', 'budget', 'low-cost'],
            'enterprise': ['enterprise', 'large-scale', 'corporate'],
            'smb': ['small business', 'startup', 'entrepreneur']
        }
        
        positioning_scores = {}
        for position, keywords in positioning_indicators.items():
            score = sum(1 for keyword in keywords if keyword in page_text)
            if score > 0:
                positioning_scores[position] = score
        
        if positioning_scores:
            competitor_analysis['market_positioning'] = max(positioning_scores, key=positioning_scores.get)
        
        return competitor_analysis

    def analyze_budget_indicators(self, soup: BeautifulSoup, url: str, tech_analysis: Dict, social_intel: Dict) -> Dict:
        """Comprehensive budget and spending analysis"""
        budget_analysis = {
            'overall_budget_level': 'unknown',
            'monthly_spend_estimate': '$0-$1000',
            'budget_allocation': {},
            'spending_indicators': [],
            'growth_indicators': [],
            'budget_optimization_opportunities': [],
            'financial_health_score': 0,
            'investment_capacity': 'unknown'
        }
        
        page_html = str(soup).lower()
        page_text = soup.get_text().lower()
        
        # Analyze advertising spend indicators
        ad_indicators = {
            'google_ads': 3,
            'facebook_ads': 3,
            'linkedin_ads': 5,
            'microsoft_ads': 2,
            'programmatic': 4
        }
        
        advertising_score = 0
        for platform in social_intel.get('social_budget_indicators', []):
            if platform.replace('_ads', '') in ad_indicators:
                advertising_score += ad_indicators[platform.replace('_ads', '')]
                budget_analysis['spending_indicators'].append(f"advertising_{platform}")
        
        # Technology spending analysis
        tech_spend_score = 0
        for tech, data in tech_analysis.get('detected_technologies', {}).items():
            if data['cost_indicator'] == 'high':
                tech_spend_score += 5
            elif data['cost_indicator'] == 'medium':
                tech_spend_score += 3
            else:
                tech_spend_score += 1
        
        # Team size indicators from content
        team_indicators = [
            'hiring', 'we\'re growing', 'join our team', 'careers',
            'remote work', 'full-time', 'part-time'
        ]
        
        hiring_score = sum(1 for indicator in team_indicators if indicator in page_text)
        
        # Revenue indicators
        revenue_indicators = [
            'million in revenue', 'billion in sales', 'profitable',
            'funding', 'investment', 'series a', 'series b', 'ipo'
        ]
        
        revenue_score = sum(2 for indicator in revenue_indicators if indicator in page_text)
        
        # Calculate overall budget level
        total_score = advertising_score + tech_spend_score + hiring_score + revenue_score
        
        if total_score >= 20:
            budget_analysis['overall_budget_level'] = 'high'
            budget_analysis['monthly_spend_estimate'] = '$10,000-$100,000+'
            budget_analysis['investment_capacity'] = 'high'
        elif total_score >= 10:
            budget_analysis['overall_budget_level'] = 'medium-high'
            budget_analysis['monthly_spend_estimate'] = '$5,000-$25,000'
            budget_analysis['investment_capacity'] = 'medium-high'
        elif total_score >= 5:
            budget_analysis['overall_budget_level'] = 'medium'
            budget_analysis['monthly_spend_estimate'] = '$1,000-$10,000'
            budget_analysis['investment_capacity'] = 'medium'
        else:
            budget_analysis['overall_budget_level'] = 'low'
            budget_analysis['monthly_spend_estimate'] = '$100-$2,000'
            budget_analysis['investment_capacity'] = 'low'
        
        # Budget allocation analysis
        if advertising_score > 0:
            budget_analysis['budget_allocation']['advertising'] = f"{min(advertising_score * 10, 60)}%"
        
        if tech_spend_score > 0:
            budget_analysis['budget_allocation']['technology'] = f"{min(tech_spend_score * 8, 40)}%"
        
        if hiring_score > 0:
            budget_analysis['budget_allocation']['personnel'] = f"{min(hiring_score * 15, 70)}%"
        
        # Identify optimization opportunities
        if advertising_score > 8:
            budget_analysis['budget_optimization_opportunities'].append('advertising_consolidation')
        
        if tech_spend_score > 10:
            budget_analysis['budget_optimization_opportunities'].append('tech_stack_optimization')
        
        if not advertising_score and budget_analysis['overall_budget_level'] in ['medium', 'medium-high', 'high']:
            budget_analysis['budget_optimization_opportunities'].append('marketing_channel_expansion')
        
        budget_analysis['financial_health_score'] = min(total_score * 5, 100)
        
        return budget_analysis

    def analyze_traffic_and_marketing(self, soup: BeautifulSoup, url: str) -> Dict:
        """Traffic and marketing channel analysis"""
        traffic_analysis = {
            'marketing_channels': {},
            'traffic_quality_indicators': [],
            'conversion_optimization': {},
            'marketing_maturity_score': 0,
            'channel_gaps': [],
            'attribution_setup': {}
        }
        
        page_html = str(soup).lower()
        scripts = soup.find_all('script')
        
        # Detect marketing and analytics tools
        marketing_tools = {
            'google_analytics': {
                'patterns': ['google-analytics.com', 'gtag', 'ga.js', 'analytics.js'],
                'weight': 3
            },
            'google_tag_manager': {
                'patterns': ['googletagmanager.com', 'gtm.js'],
                'weight': 4
            },
            'facebook_pixel': {
                'patterns': ['connect.facebook.net', 'fbevents.js'],
                'weight': 3
            },
            'hotjar': {
                'patterns': ['hotjar.com', 'hj.js'],
                'weight': 2
            },
            'mixpanel': {
                'patterns': ['mixpanel.com', 'mixpanel.js'],
                'weight': 3
            },
            'segment': {
                'patterns': ['segment.com', 'analytics.min.js'],
                'weight': 4
            }
        }
        
        detected_tools = []
        for tool, config in marketing_tools.items():
            for pattern in config['patterns']:
                if pattern in page_html:
                    detected_tools.append(tool)
                    traffic_analysis['marketing_maturity_score'] += config['weight']
                    break
        
        traffic_analysis['marketing_channels']['detected_tools'] = detected_tools
        
        # Analyze conversion optimization setup
        conversion_elements = {
            'forms': len(soup.find_all('form')),
            'cta_buttons': len(soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))),
            'phone_numbers': len(re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', soup.get_text())),
            'email_addresses': len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text()))
        }
        
        traffic_analysis['conversion_optimization'] = conversion_elements
        
        # Identify channel gaps
        if 'google_analytics' not in detected_tools:
            traffic_analysis['channel_gaps'].append('basic_analytics')
        
        if 'facebook_pixel' not in detected_tools and 'facebook' in page_html:
            traffic_analysis['channel_gaps'].append('facebook_tracking')
        
        if not any('tag_manager' in tool for tool in detected_tools):
            traffic_analysis['channel_gaps'].append('tag_management')
        
        return traffic_analysis

    def extract_contact_intelligence(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract contact and decision maker information"""
        contact_intel = {
            'contact_methods': [],
            'key_personnel': [],
            'decision_maker_indicators': [],
            'contact_accessibility': 'unknown',
            'sales_readiness_score': 0,
            'lead_magnets': [],
            'contact_form_quality': {}
        }
        
        page_text = soup.get_text()
        page_html = str(soup)
        
        # Extract contact information
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, page_text)
        if phones:
            contact_intel['contact_methods'].append(f"phone_{len(phones)}_numbers")
            contact_intel['sales_readiness_score'] += 3
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        if emails:
            contact_intel['contact_methods'].append(f"email_{len(emails)}_addresses")
            contact_intel['sales_readiness_score'] += 2
        
        # Look for key personnel
        title_patterns = [
            r'(CEO|Chief Executive Officer|President|Founder|Co-Founder)\s*[:\-]?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(CTO|Chief Technology Officer|VP|Vice President|Director)\s*[:\-]?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(CMO|Chief Marketing Officer|Marketing Director)\s*[:\-]?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                contact_intel['key_personnel'].append({
                    'title': match[0],
                    'name': match[1] if len(match) > 1 else 'Unknown'
                })
                contact_intel['sales_readiness_score'] += 5
        
        # Analyze contact forms
        forms = soup.find_all('form')
        if forms:
            form_quality = {
                'count': len(forms),
                'has_email_field': False,
                'has_phone_field': False,
                'has_company_field': False,
                'complexity_score': 0
            }
            
            for form in forms:
                inputs = form.find_all(['input', 'textarea', 'select'])
                form_quality['complexity_score'] += len(inputs)
                
                for input_elem in inputs:
                    input_name = (input_elem.get('name', '') + input_elem.get('id', '')).lower()
                    if 'email' in input_name:
                        form_quality['has_email_field'] = True
                    if 'phone' in input_name:
                        form_quality['has_phone_field'] = True
                    if 'company' in input_name:
                        form_quality['has_company_field'] = True
            
            contact_intel['contact_form_quality'] = form_quality
            contact_intel['sales_readiness_score'] += min(form_quality['complexity_score'], 10)
        
        # Look for lead magnets
        lead_magnet_keywords = [
            'free trial', 'free consultation', 'download', 'ebook', 'whitepaper',
            'case study', 'demo', 'webinar', 'newsletter', 'guide'
        ]
        
        for keyword in lead_magnet_keywords:
            if keyword in page_text.lower():
                contact_intel['lead_magnets'].append(keyword)
        
        if contact_intel['lead_magnets']:
            contact_intel['sales_readiness_score'] += len(contact_intel['lead_magnets']) * 2
        
        # Calculate contact accessibility
        if contact_intel['sales_readiness_score'] >= 15:
            contact_intel['contact_accessibility'] = 'high'
        elif contact_intel['sales_readiness_score'] >= 8:
            contact_intel['contact_accessibility'] = 'medium'
        else:
            contact_intel['contact_accessibility'] = 'low'
        
        return contact_intel

    def calculate_lead_scoring(self, company_profile: Dict, social_intel: Dict, tech_analysis: Dict, 
                             budget_analysis: Dict, contact_intel: Dict) -> Dict:
        """Calculate comprehensive lead scoring"""
        lead_scoring = {
            'overall_score': 0,
            'category_scores': {},
            'lead_quality': 'unknown',
            'sales_priority': 'unknown',
            'conversion_probability': 'unknown',
            'deal_size_estimate': 'unknown',
            'sales_cycle_estimate': 'unknown',
            'next_actions': []
        }
        
        # Company profile scoring (25 points)
        profile_score = 0
        if company_profile.get('industry') in ['saas', 'ecommerce', 'consulting']:
            profile_score += 8
        elif company_profile.get('industry'):
            profile_score += 5
        
        if company_profile.get('employees'):
            if any(indicator in company_profile['employees'] for indicator in ['100+', '50-']):
                profile_score += 8
            else:
                profile_score += 4
        
        if company_profile.get('location'):
            profile_score += 4
        
        lead_scoring['category_scores']['company_profile'] = min(profile_score, 25)
        
        # Social media intelligence scoring (20 points)
        social_score = min(social_intel.get('social_engagement_score', 0) // 3, 15)
        if social_intel.get('social_budget_indicators'):
            social_score += 5
        
        lead_scoring['category_scores']['social_intelligence'] = min(social_score, 20)
        
        # Technology sophistication scoring (20 points)
        tech_score = min(tech_analysis.get('tech_sophistication_score', 0) // 2, 15)
        if tech_analysis.get('agency_opportunities'):
            tech_score += 5
        
        lead_scoring['category_scores']['technology'] = min(tech_score, 20)
        
        # Budget analysis scoring (25 points)
        budget_score = 0
        budget_level = budget_analysis.get('overall_budget_level', 'low')
        if budget_level == 'high':
            budget_score = 25
        elif budget_level == 'medium-high':
            budget_score = 20
        elif budget_level == 'medium':
            budget_score = 15
        else:
            budget_score = 5
        
        lead_scoring['category_scores']['budget'] = budget_score
        
        # Contact accessibility scoring (10 points)
        contact_score = min(contact_intel.get('sales_readiness_score', 0) // 2, 10)
        lead_scoring['category_scores']['contact_accessibility'] = contact_score
        
        # Calculate overall score
        lead_scoring['overall_score'] = sum(lead_scoring['category_scores'].values())
        
        # Determine lead quality
        if lead_scoring['overall_score'] >= 80:
            lead_scoring['lead_quality'] = 'premium'
            lead_scoring['sales_priority'] = 'immediate'
            lead_scoring['conversion_probability'] = 'high'
            lead_scoring['deal_size_estimate'] = '$10,000-$100,000+'
            lead_scoring['sales_cycle_estimate'] = '1-3 months'
        elif lead_scoring['overall_score'] >= 60:
            lead_scoring['lead_quality'] = 'qualified'
            lead_scoring['sales_priority'] = 'high'
            lead_scoring['conversion_probability'] = 'medium-high'
            lead_scoring['deal_size_estimate'] = '$5,000-$25,000'
            lead_scoring['sales_cycle_estimate'] = '2-6 months'
        elif lead_scoring['overall_score'] >= 40:
            lead_scoring['lead_quality'] = 'potential'
            lead_scoring['sales_priority'] = 'medium'
            lead_scoring['conversion_probability'] = 'medium'
            lead_scoring['deal_size_estimate'] = '$2,000-$10,000'
            lead_scoring['sales_cycle_estimate'] = '3-12 months'
        else:
            lead_scoring['lead_quality'] = 'nurture'
            lead_scoring['sales_priority'] = 'low'
            lead_scoring['conversion_probability'] = 'low'
            lead_scoring['deal_size_estimate'] = '$500-$5,000'
            lead_scoring['sales_cycle_estimate'] = '6-18+ months'
        
        # Generate next actions with detailed steps
        lead_scoring['next_actions'] = self._generate_detailed_action_plan(
            lead_scoring, company_profile, social_intel, tech_analysis, budget_analysis, contact_intel
        )
        
        # Generate quick wins and immediate opportunities
        lead_scoring['quick_wins'] = self._identify_quick_wins(
            lead_scoring, company_profile, social_intel, tech_analysis, contact_intel
        )
        
        # Add comprehensive explanations
        lead_scoring['score_explanations'] = self._generate_score_explanations(
            lead_scoring, company_profile, social_intel, tech_analysis, budget_analysis, contact_intel
        )
        
        # Add industry benchmarks
        lead_scoring['industry_benchmarks'] = self._get_industry_benchmarks(company_profile)
        
        # Add business impact explanations
        lead_scoring['business_impact'] = self._generate_business_impact_explanations(lead_scoring, company_profile)
        
        return lead_scoring
    
    def _generate_detailed_action_plan(self, lead_scoring, company_profile, social_intel, tech_analysis, budget_analysis, contact_intel):
        """Generate comprehensive action plan with priorities and timelines"""
        quality = lead_scoring['lead_quality']
        score = lead_scoring['overall_score']
        
        action_plan = {
            'immediate_actions': [],    # 1-7 days
            'short_term_actions': [],   # 1-4 weeks  
            'medium_term_actions': [],  # 1-3 months
            'long_term_actions': [],    # 3+ months
            'priority_matrix': {},
            'resource_requirements': {},
            'success_metrics': {}
        }
        
        # Quality-based immediate actions
        if quality == 'premium':
            action_plan['immediate_actions'].extend([
                {
                    'action': 'Executive-level outreach within 24 hours',
                    'priority': 'critical',
                    'timeline': '1 day',
                    'resources': ['Senior sales rep', 'Custom research'],
                    'outcome': 'Meeting scheduled with decision maker'
                },
                {
                    'action': 'Comprehensive company research and pain point analysis',
                    'priority': 'high',
                    'timeline': '2-3 days',
                    'resources': ['Research team', 'Industry reports'],
                    'outcome': 'Detailed prospect profile completed'
                },
                {
                    'action': 'Custom proposal framework development',
                    'priority': 'high',
                    'timeline': '3-5 days',
                    'resources': ['Proposal team', 'Case studies'],
                    'outcome': 'Initial proposal ready for presentation'
                }
            ])
            
        elif quality == 'qualified':
            action_plan['immediate_actions'].extend([
                {
                    'action': 'Personalized multi-channel outreach campaign',
                    'priority': 'high',
                    'timeline': '2-3 days',
                    'resources': ['Sales rep', 'Marketing materials'],
                    'outcome': 'Initial contact established'
                },
                {
                    'action': 'Industry-specific pain point research',
                    'priority': 'high',
                    'timeline': '1 week',
                    'resources': ['Research team'],
                    'outcome': 'Targeted value proposition developed'
                }
            ])
            
        elif quality == 'potential':
            action_plan['immediate_actions'].extend([
                {
                    'action': 'Add to nurture sequence with educational content',
                    'priority': 'medium',
                    'timeline': '3-5 days',
                    'resources': ['Marketing automation'],
                    'outcome': 'Prospect engaged in educational journey'
                },
                {
                    'action': 'Social media connection and engagement',
                    'priority': 'medium',
                    'timeline': '1 week',
                    'resources': ['Social media team'],
                    'outcome': 'Relationship building initiated'
                }
            ])
            
        else:  # nurture
            action_plan['immediate_actions'].extend([
                {
                    'action': 'Long-term nurture sequence enrollment',
                    'priority': 'low',
                    'timeline': '1 week',
                    'resources': ['Marketing automation'],
                    'outcome': 'Consistent touchpoint established'
                }
            ])
        
        # Social media specific actions
        social_score = lead_scoring['category_scores'].get('social_intelligence', 0)
        if social_score < 10:
            action_plan['short_term_actions'].append({
                'action': 'Social media presence development consultation',
                'priority': 'high',
                'timeline': '2-3 weeks',
                'resources': ['Social media specialist'],
                'outcome': 'Social strategy foundation established'
            })
        
        # Technology stack specific actions
        tech_score = lead_scoring['category_scores'].get('technology', 0)
        if tech_score < 10:
            action_plan['short_term_actions'].append({
                'action': 'Technology assessment and modernization planning',
                'priority': 'high',
                'timeline': '3-4 weeks',
                'resources': ['Technical consultant'],
                'outcome': 'Technology roadmap developed'
            })
        
        # Budget-based actions
        budget_score = lead_scoring['category_scores'].get('budget', 0)
        if budget_score >= 20:
            action_plan['short_term_actions'].append({
                'action': 'Premium service presentation and demonstration',
                'priority': 'high',
                'timeline': '2-3 weeks',
                'resources': ['Senior team', 'Demo environment'],
                'outcome': 'High-value opportunity identified'
            })
        elif budget_score < 15:
            action_plan['medium_term_actions'].append({
                'action': 'Budget development and ROI education series',
                'priority': 'medium',
                'timeline': '1-2 months',
                'resources': ['Educational content', 'ROI calculators'],
                'outcome': 'Investment readiness improved'
            })
        
        # Contact accessibility actions
        contact_score = lead_scoring['category_scores'].get('contact_accessibility', 0)
        if contact_score < 5:
            action_plan['immediate_actions'].append({
                'action': 'Decision maker identification and contact research',
                'priority': 'high',
                'timeline': '2-3 days',
                'resources': ['Research tools', 'LinkedIn Sales Navigator'],
                'outcome': 'Key contacts identified and verified'
            })
        
        # Industry-specific actions
        industry = company_profile.get('industry', '').lower()
        if industry in ['healthcare', 'legal', 'finance']:
            action_plan['medium_term_actions'].append({
                'action': 'Compliance and regulatory requirement assessment',
                'priority': 'high',
                'timeline': '1-2 months',
                'resources': ['Industry specialist'],
                'outcome': 'Compliant solution framework developed'
            })
        
        # Priority matrix
        action_plan['priority_matrix'] = self._create_priority_matrix(action_plan, quality, score)
        
        # Resource requirements
        action_plan['resource_requirements'] = self._calculate_resource_requirements(action_plan)
        
        # Success metrics
        action_plan['success_metrics'] = self._define_success_metrics(action_plan, quality, lead_scoring)
        
        return action_plan
    
    def _identify_quick_wins(self, lead_scoring, company_profile, social_intel, tech_analysis, contact_intel):
        """Identify immediate quick wins and low-effort high-impact actions"""
        quick_wins = []
        
        # Social media quick wins
        platforms = social_intel.get('platforms_found', {})
        if len(platforms) > 0:
            incomplete_profiles = [p for p, data in platforms.items() if not data.get('business_account')]
            if incomplete_profiles:
                quick_wins.append({
                    'opportunity': 'Complete business profile setup',
                    'platforms': incomplete_profiles,
                    'effort': 'Low (1-2 hours)',
                    'impact': 'Medium',
                    'timeline': '1-2 days',
                    'roi_potential': '15-25% improvement in social credibility'
                })
        
        if not social_intel.get('social_budget_indicators'):
            quick_wins.append({
                'opportunity': 'Install social media tracking pixels',
                'platforms': list(platforms.keys()),
                'effort': 'Low (30 minutes)',
                'impact': 'High',
                'timeline': '1 day',
                'roi_potential': 'Foundation for future advertising campaigns'
            })
        
        # Website optimization quick wins
        tech_score = lead_scoring['category_scores'].get('technology', 0)
        if tech_score < 15:
            quick_wins.append({
                'opportunity': 'Basic website optimization assessment',
                'platforms': ['website'],
                'effort': 'Medium (2-4 hours)',
                'impact': 'High',
                'timeline': '3-5 days',
                'roi_potential': '20-40% improvement in user experience'
            })
        
        # Contact optimization quick wins
        contact_score = lead_scoring['category_scores'].get('contact_accessibility', 0)
        if contact_score < 7:
            quick_wins.append({
                'opportunity': 'Contact information optimization',
                'platforms': ['website', 'social'],
                'effort': 'Low (1 hour)',
                'impact': 'High',
                'timeline': '1-2 days',
                'roi_potential': '30-50% improvement in contact conversion'
            })
        
        # Industry-specific quick wins
        industry = company_profile.get('industry', '').lower()
        if industry in ['retail', 'restaurants', 'services']:
            quick_wins.append({
                'opportunity': 'Local business listing optimization',
                'platforms': ['google_business', 'local_directories'],
                'effort': 'Medium (2-3 hours)',
                'impact': 'High',
                'timeline': '1 week',
                'roi_potential': '25-45% improvement in local visibility'
            })
        
        return quick_wins
    
    def _create_priority_matrix(self, action_plan, quality, score):
        """Create priority matrix for actions based on impact vs effort"""
        matrix = {
            'high_impact_low_effort': [],    # Do first
            'high_impact_high_effort': [],   # Plan carefully  
            'low_impact_low_effort': [],     # Fill in time
            'low_impact_high_effort': []     # Avoid
        }
        
        # Categorize all actions
        all_actions = (action_plan['immediate_actions'] + 
                      action_plan['short_term_actions'] + 
                      action_plan['medium_term_actions'])
        
        for action in all_actions:
            priority = action.get('priority', 'medium')
            resources = len(action.get('resources', []))
            
            # Determine effort level
            effort = 'low' if resources <= 1 else 'high'
            
            # Determine impact level  
            if priority == 'critical' or (quality == 'premium' and priority == 'high'):
                impact = 'high'
            elif priority == 'high' or score >= 60:
                impact = 'high'
            else:
                impact = 'low'
            
            # Categorize
            category = f"{impact}_impact_{effort}_effort"
            if category in matrix:
                matrix[category].append(action)
        
        return matrix
    
    def _calculate_resource_requirements(self, action_plan):
        """Calculate total resource requirements"""
        requirements = {
            'human_resources': set(),
            'tools_needed': set(),
            'estimated_hours': 0,
            'skills_required': set(),
            'cost_estimate': {'min': 0, 'max': 0}
        }
        
        # Resource mapping
        resource_costs = {
            'Senior sales rep': {'hours': 4, 'cost_per_hour': 75},
            'Sales rep': {'hours': 2, 'cost_per_hour': 50},
            'Research team': {'hours': 6, 'cost_per_hour': 35},
            'Technical consultant': {'hours': 8, 'cost_per_hour': 85},
            'Social media team': {'hours': 3, 'cost_per_hour': 40},
            'Marketing automation': {'hours': 1, 'cost_per_hour': 25}
        }
        
        all_actions = (action_plan['immediate_actions'] + 
                      action_plan['short_term_actions'] + 
                      action_plan['medium_term_actions'])
        
        for action in all_actions:
            for resource in action.get('resources', []):
                requirements['human_resources'].add(resource)
                if resource in resource_costs:
                    hours = resource_costs[resource]['hours']
                    cost = resource_costs[resource]['cost_per_hour']
                    requirements['estimated_hours'] += hours
                    requirements['cost_estimate']['min'] += hours * cost * 0.8
                    requirements['cost_estimate']['max'] += hours * cost * 1.2
        
        return {
            'human_resources': list(requirements['human_resources']),
            'estimated_hours': requirements['estimated_hours'],
            'cost_estimate': f"${int(requirements['cost_estimate']['min'])}-${int(requirements['cost_estimate']['max'])}"
        }
    
    def _define_success_metrics(self, action_plan, quality, lead_scoring):
        """Define success metrics for the action plan"""
        metrics = {
            'primary_kpis': [],
            'engagement_metrics': [],
            'conversion_milestones': [],
            'timeline_targets': {}
        }
        
        # Quality-based primary KPIs
        if quality == 'premium':
            metrics['primary_kpis'] = [
                'Meeting scheduled within 7 days',
                'Proposal presented within 14 days',
                'Decision meeting within 30 days'
            ]
        elif quality == 'qualified':
            metrics['primary_kpis'] = [
                'Initial contact response within 7 days',
                'Needs assessment completed within 21 days',
                'Proposal requested within 45 days'
            ]
        else:
            metrics['primary_kpis'] = [
                'Educational content engagement within 14 days',
                'Social media connection within 30 days',
                'Follow-up interest within 90 days'
            ]
        
        # Universal engagement metrics
        metrics['engagement_metrics'] = [
            'Email open rates > 25%',
            'Website visit duration > 2 minutes',
            'Social media profile views increase',
            'Content download or interaction'
        ]
        
        # Conversion milestones
        deal_size = lead_scoring.get('deal_size_estimate', '')
        if '$10,000' in deal_size:
            metrics['conversion_milestones'] = [
                'Discovery call completed',
                'Stakeholder meeting arranged', 
                'Technical requirements gathered',
                'Proposal presented to decision makers'
            ]
        else:
            metrics['conversion_milestones'] = [
                'Initial interest confirmed',
                'Budget discussion initiated',
                'Service demonstration completed',
                'Contract negotiation started'
            ]
        
        return metrics
    
    def _generate_score_explanations(self, lead_scoring, company_profile, social_intel, tech_analysis, budget_analysis, contact_intel):
        """Generate comprehensive explanations for all scores"""
        explanations = {
            'overall_score_explanation': '',
            'category_explanations': {},
            'strengths': [],
            'improvement_areas': [],
            'reasoning': {}
        }
        
        # Overall score explanation
        score = lead_scoring['overall_score']
        quality = lead_scoring['lead_quality']
        
        explanations['overall_score_explanation'] = f"""
This prospect scored {score}/100 points, qualifying as a '{quality}' lead. This score is calculated across 5 key categories:
Company Profile (25 pts), Social Media Intelligence (20 pts), Technology Stack (20 pts), Budget Indicators (25 pts), and Contact Accessibility (10 pts).

{self._get_quality_explanation(quality, score)}
        """.strip()
        
        # Category explanations
        category_scores = lead_scoring['category_scores']
        
        # Company Profile explanation
        profile_score = category_scores.get('company_profile', 0)
        explanations['category_explanations']['company_profile'] = f"""
Company Profile Score: {profile_score}/25 points
{self._explain_company_profile_score(profile_score, company_profile)}
        """.strip()
        
        # Social Intelligence explanation
        social_score = category_scores.get('social_intelligence', 0)
        explanations['category_explanations']['social_intelligence'] = f"""
Social Media Intelligence Score: {social_score}/20 points
{self._explain_social_score(social_score, social_intel)}
        """.strip()
        
        # Technology explanation
        tech_score = category_scores.get('technology', 0)
        explanations['category_explanations']['technology'] = f"""
Technology Stack Score: {tech_score}/20 points
{self._explain_tech_score(tech_score, tech_analysis)}
        """.strip()
        
        # Budget explanation
        budget_score = category_scores.get('budget', 0)
        explanations['category_explanations']['budget'] = f"""
Budget Indicators Score: {budget_score}/25 points
{self._explain_budget_score(budget_score, budget_analysis)}
        """.strip()
        
        # Contact explanation
        contact_score = category_scores.get('contact_accessibility', 0)
        explanations['category_explanations']['contact_accessibility'] = f"""
Contact Accessibility Score: {contact_score}/10 points
{self._explain_contact_score(contact_score, contact_intel)}
        """.strip()
        
        # Identify strengths and improvement areas
        explanations['strengths'] = self._identify_strengths(category_scores)
        explanations['improvement_areas'] = self._identify_improvement_areas(category_scores)
        
        return explanations
    
    def _get_quality_explanation(self, quality, score):
        """Get explanation for lead quality level"""
        explanations = {
            'premium': f"""
At {score} points, this is a PREMIUM lead requiring immediate attention. These prospects typically:
• Have established budgets and decision-making authority
• Show strong digital presence and technology adoption
• Are actively seeking solutions or have immediate needs
• Represent high-value opportunities ($10K-$100K+)
• Close within 1-3 months with proper approach
            """,
            'qualified': f"""
At {score} points, this is a QUALIFIED lead with strong potential. These prospects typically:
• Have moderate to good budget capacity
• Show growing digital presence and technology needs
• Are researching solutions and evaluating options
• Represent solid opportunities ($5K-$25K)
• Close within 2-6 months with consistent nurturing
            """,
            'potential': f"""
At {score} points, this is a POTENTIAL lead worth nurturing. These prospects typically:
• Have limited but growing budget capacity
• Show basic digital presence with growth potential
• May not be actively seeking solutions yet
• Represent developing opportunities ($2K-$10K)
• Close within 3-12 months with education and relationship building
            """,
            'nurture': f"""
At {score} points, this is a NURTURE lead requiring long-term development. These prospects typically:
• Have constrained budget or unclear decision process
• Show minimal digital presence or sophistication
• Are early in their growth journey
• Represent emerging opportunities ($500-$5K)
• Close within 6-18+ months with substantial education and trust building
            """
        }
        return explanations.get(quality, '').strip()
    
    def _explain_company_profile_score(self, score, company_profile):
        """Explain company profile scoring"""
        industry = company_profile.get('industry', 'unknown')
        size = company_profile.get('business_size', 'unknown')
        location = company_profile.get('location', 'unknown')
        employees = company_profile.get('employees', 'unknown')
        
        explanation = f"""
This score reflects the company's profile strength and market positioning:

Industry: {industry.title()} - {'High-value service industry' if industry in ['healthcare', 'legal', 'finance'] else 'Standard industry classification'}
Business Size: {size.title()} - {'Established business with growth potential' if size in ['medium', 'large'] else 'Smaller business with scaling opportunities'}
Geographic Location: {location} - {'Clear market presence established' if location != 'unknown' else 'Location information needs verification'}
Team Size: {employees} - {'Substantial team indicating growth and budget' if '50+' in str(employees) or '100+' in str(employees) else 'Growing team with expansion needs'}

Score Impact: {'Strong company foundation' if score >= 18 else 'Developing company profile' if score >= 12 else 'Early-stage business profile'}
        """
        return explanation.strip()
    
    def _explain_social_score(self, score, social_intel):
        """Explain social media intelligence scoring"""
        platforms = social_intel.get('platforms_found', {})
        engagement = social_intel.get('social_engagement_score', 0)
        advertising = social_intel.get('social_budget_indicators', [])
        
        explanation = f"""
This score evaluates social media presence and marketing sophistication:

Platform Presence: {len(platforms)} platforms detected - {', '.join(platforms.keys()) if platforms else 'Limited social presence'}
Engagement Level: {engagement}/100 - {'High community engagement' if engagement >= 70 else 'Moderate engagement' if engagement >= 40 else 'Low engagement levels'}
Advertising Activity: {len(advertising)} channels detected - {'Active paid social strategy' if advertising else 'No paid advertising detected'}

Business Impact: {'Strong social marketing foundation' if score >= 15 else 'Growing social presence' if score >= 10 else 'Significant social media opportunity'}
        """
        return explanation.strip()
    
    def _explain_tech_score(self, score, tech_analysis):
        """Explain technology stack scoring"""
        sophistication = tech_analysis.get('tech_sophistication_score', 0)
        technologies = tech_analysis.get('detected_technologies', {})
        opportunities = tech_analysis.get('agency_opportunities', [])
        
        explanation = f"""
This score measures technology adoption and digital maturity:

Tech Sophistication: {sophistication}/100 - {'Advanced technology stack' if sophistication >= 70 else 'Moderate tech adoption' if sophistication >= 40 else 'Basic technology setup'}
Detected Technologies: {len(technologies)} systems identified - {', '.join(list(technologies.keys())[:5]) if technologies else 'Limited technology detected'}
Upgrade Opportunities: {len(opportunities)} identified - {'Multiple modernization needs' if len(opportunities) >= 3 else 'Some upgrade potential' if opportunities else 'Current stack adequate'}

Investment Readiness: {'Ready for advanced solutions' if score >= 15 else 'Moderate tech investment capacity' if score >= 10 else 'Basic technology needs focus'}
        """
        return explanation.strip()
    
    def _explain_budget_score(self, score, budget_analysis):
        """Explain budget indicators scoring"""
        budget_level = budget_analysis.get('overall_budget_level', 'low')
        monthly_estimate = budget_analysis.get('monthly_spend_estimate', 'unknown')
        investment_capacity = budget_analysis.get('investment_capacity', 'low')
        
        explanation = f"""
This score analyzes spending patterns and investment capacity:

Overall Budget Level: {budget_level.title()} - {self._get_budget_level_explanation(budget_level)}
Monthly Spend Estimate: {monthly_estimate} - {'Substantial marketing investment' if 'high' in str(monthly_estimate).lower() else 'Moderate spending detected' if 'medium' in str(monthly_estimate).lower() else 'Limited current investment'}
Investment Capacity: {investment_capacity.title()} - {'Strong ability to invest in growth' if investment_capacity in ['high', 'medium-high'] else 'Moderate investment capability' if investment_capacity == 'medium' else 'Conservative investment approach'}

Revenue Potential: {'High-value opportunity' if score >= 20 else 'Solid revenue potential' if score >= 15 else 'Growing revenue opportunity'}
        """
        return explanation.strip()
    
    def _get_budget_level_explanation(self, level):
        """Get detailed budget level explanation"""
        explanations = {
            'high': 'Strong indicators of significant marketing/technology spend (enterprise tools, premium services, substantial team)',
            'medium-high': 'Good indicators of moderate to strong budget capacity (quality tools, growing team, investment signs)',
            'medium': 'Moderate budget indicators suggesting growth-stage investment capability',
            'low': 'Limited budget indicators suggesting cost-conscious approach or early-stage business'
        }
        return explanations.get(level, 'Budget level assessment pending')
    
    def _explain_contact_score(self, score, contact_intel):
        """Explain contact accessibility scoring"""
        accessibility = contact_intel.get('contact_accessibility', 'low')
        methods = contact_intel.get('contact_methods', [])
        personnel = contact_intel.get('key_personnel', [])
        
        explanation = f"""
This score evaluates how easily decision makers can be reached:

Contact Accessibility: {accessibility.title()} - {'Multiple clear contact paths' if accessibility == 'high' else 'Moderate contact options' if accessibility == 'medium' else 'Limited contact information'}
Available Methods: {len(methods)} contact options - {', '.join(methods[:3]) if methods else 'Contact methods need identification'}
Key Personnel: {len(personnel)} decision makers identified - {'Clear decision maker access' if len(personnel) >= 2 else 'Decision maker identification needed'}

Sales Readiness: {'Ready for immediate outreach' if score >= 7 else 'Moderate outreach preparation needed' if score >= 4 else 'Significant contact development required'}
        """
        return explanation.strip()
    
    def _identify_strengths(self, category_scores):
        """Identify scoring strengths"""
        strengths = []
        
        if category_scores.get('company_profile', 0) >= 18:
            strengths.append('Strong company profile and market positioning')
        if category_scores.get('social_intelligence', 0) >= 15:
            strengths.append('Excellent social media presence and engagement')
        if category_scores.get('technology', 0) >= 15:
            strengths.append('Advanced technology adoption and digital maturity')
        if category_scores.get('budget', 0) >= 20:
            strengths.append('High budget capacity and investment readiness')
        if category_scores.get('contact_accessibility', 0) >= 7:
            strengths.append('Clear contact paths and decision maker access')
            
        return strengths
    
    def _identify_improvement_areas(self, category_scores):
        """Identify areas needing improvement"""
        improvements = []
        
        if category_scores.get('company_profile', 0) < 12:
            improvements.append('Company profile and positioning needs strengthening')
        if category_scores.get('social_intelligence', 0) < 10:
            improvements.append('Social media presence requires significant development')
        if category_scores.get('technology', 0) < 10:
            improvements.append('Technology modernization represents major opportunity')
        if category_scores.get('budget', 0) < 15:
            improvements.append('Budget development and investment capacity building needed')
        if category_scores.get('contact_accessibility', 0) < 5:
            improvements.append('Contact information and decision maker identification critical')
            
        return improvements
    
    def _get_industry_benchmarks(self, company_profile):
        """Get industry benchmarking data"""
        industry = company_profile.get('industry', 'general').lower()
        
        benchmarks = {
            'healthcare': {
                'average_score': 72,
                'top_quartile': 85,
                'common_strengths': ['High budget capacity', 'Technology adoption', 'Professional services demand'],
                'common_weaknesses': ['Limited social presence', 'Complex decision process'],
                'typical_deal_size': '$15,000-$75,000',
                'sales_cycle': '2-6 months'
            },
            'legal': {
                'average_score': 68,
                'top_quartile': 82,
                'common_strengths': ['Premium pricing acceptance', 'Professional networking', 'Referral systems'],
                'common_weaknesses': ['Conservative technology adoption', 'Marketing resistance'],
                'typical_deal_size': '$10,000-$50,000',
                'sales_cycle': '3-8 months'
            },
            'real_estate': {
                'average_score': 64,
                'top_quartile': 78,
                'common_strengths': ['Marketing-driven industry', 'Technology adoption', 'Lead generation focus'],
                'common_weaknesses': ['Market fluctuation sensitivity', 'Commission-based budgets'],
                'typical_deal_size': '$5,000-$25,000',
                'sales_cycle': '1-4 months'
            },
            'finance': {
                'average_score': 75,
                'top_quartile': 88,
                'common_strengths': ['High-value services', 'Technology investment', 'Compliance requirements'],
                'common_weaknesses': ['Regulatory constraints', 'Conservative marketing'],
                'typical_deal_size': '$20,000-$100,000',
                'sales_cycle': '3-9 months'
            },
            'retail': {
                'average_score': 58,
                'top_quartile': 72,
                'common_strengths': ['E-commerce focus', 'Social media presence', 'Customer experience'],
                'common_weaknesses': ['Margin pressure', 'Seasonal fluctuations'],
                'typical_deal_size': '$3,000-$15,000',
                'sales_cycle': '1-3 months'
            },
            'construction': {
                'average_score': 55,
                'top_quartile': 69,
                'common_strengths': ['Project-based revenue', 'Local market focus', 'Referral systems'],
                'common_weaknesses': ['Limited digital presence', 'Traditional marketing methods'],
                'typical_deal_size': '$4,000-$20,000',
                'sales_cycle': '2-6 months'
            }
        }
        
        return benchmarks.get(industry, {
            'average_score': 60,
            'top_quartile': 75,
            'common_strengths': ['Industry-specific opportunities'],
            'common_weaknesses': ['Standard digital marketing challenges'],
            'typical_deal_size': '$5,000-$25,000',
            'sales_cycle': '2-6 months'
        })
    
    def _generate_business_impact_explanations(self, lead_scoring, company_profile):
        """Generate business impact explanations for executives"""
        impact = {
            'executive_summary': '',
            'revenue_impact': '',
            'competitive_advantage': '',
            'growth_potential': '',
            'risk_assessment': ''
        }
        
        score = lead_scoring['overall_score']
        quality = lead_scoring['lead_quality']
        industry = company_profile.get('industry', 'business').title()
        
        impact['executive_summary'] = f"""
This {industry} business represents a {quality} opportunity with {score}/100 qualification score. Our analysis indicates {lead_scoring.get('deal_size_estimate', 'significant')} revenue potential with {lead_scoring.get('conversion_probability', 'moderate')} probability of closing within {lead_scoring.get('sales_cycle_estimate', 'standard timeframe')}.
        """.strip()
        
        impact['revenue_impact'] = f"""
Based on industry benchmarks and company profile analysis, this prospect shows {lead_scoring.get('deal_size_estimate', 'standard')} revenue potential. The {quality} qualification level suggests {'immediate revenue opportunity' if quality == 'premium' else 'strong revenue potential' if quality == 'qualified' else 'developing revenue opportunity'} with appropriate investment in relationship development.
        """.strip()
        
        impact['competitive_advantage'] = f"""
Early engagement with this {industry} prospect provides competitive positioning advantage. Their current digital maturity level creates opportunity to establish long-term partnership before competitors identify this potential.
        """.strip()
        
        impact['growth_potential'] = f"""
{industry} businesses typically expand services over 2-3 years. This prospect's profile suggests {'high growth trajectory' if score >= 70 else 'solid growth potential' if score >= 50 else 'emerging growth opportunity'} with multiple service expansion opportunities.
        """.strip()
        
        impact['risk_assessment'] = f"""
Risk factors: {'Low risk - established business with clear budget' if quality in ['premium', 'qualified'] else 'Moderate risk - developing business requiring nurturing' if quality == 'potential' else 'Higher risk - early stage business needing significant development'}. Recommended approach: {lead_scoring['next_actions'][0].replace('_', ' ').title()}.
        """.strip()
        
        return impact

    def analyze_gohighlevel_opportunities(self, all_analyses: Dict) -> Dict:
        """Analyze gaps and recommend specific GoHighLevel services with pricing"""
        
        # Industry-specific pricing multipliers
        industry_multipliers = {
            'healthcare': 1.3,
            'legal': 1.4,
            'real_estate': 1.2,
            'finance': 1.5,
            'automotive': 1.1,
            'fitness': 1.0,
            'restaurants': 0.9,
            'retail': 0.8,
            'construction': 1.2,
            'beauty': 1.0
        }
        
        company_profile = all_analyses.get('company_profile', {})
        social_intel = all_analyses.get('social_media_intelligence', {})
        tech_analysis = all_analyses.get('tech_stack_analysis', {})
        contact_intel = all_analyses.get('contact_intelligence', {})
        budget_indicators = all_analyses.get('budget_indicators', {})
        
        industry = company_profile.get('industry', 'general').lower()
        multiplier = industry_multipliers.get(industry, 1.0)
        
        business_size = company_profile.get('business_size', 'small').lower()
        size_multiplier = {
            'micro': 0.7,
            'small': 1.0, 
            'medium': 1.3,
            'large': 1.6,
            'enterprise': 2.0
        }.get(business_size, 1.0)
        
        final_multiplier = multiplier * size_multiplier
        
        recommendations = {
            'ai_chatbot_setup': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '2-3 weeks'
            },
            'google_review_automation': {
                'recommended': False,
                'priority': 'medium', 
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '1-2 weeks'
            },
            'missed_call_text_back': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '1 week'
            },
            'appointment_booking': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '2-4 weeks'
            },
            'email_sms_sequences': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '3-5 weeks'
            },
            'lead_magnets': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '2-3 weeks'
            },
            'funnel_optimization': {
                'recommended': False,
                'priority': 'medium',
                'setup_fee': 0,
                'monthly_rate': 0,
                'reason': '',
                'roi_estimate': '',
                'implementation_time': '4-6 weeks'
            }
        }
        
        # AI Chatbot Analysis
        has_chatbot = any('chat' in tech.lower() or 'bot' in tech.lower() 
                         for tech in tech_analysis.get('detected_technologies', {}))
        has_contact_forms = len(contact_intel.get('contact_methods', [])) > 0
        
        if not has_chatbot and has_contact_forms:
            recommendations['ai_chatbot_setup']['recommended'] = True
            recommendations['ai_chatbot_setup']['priority'] = 'high'
            recommendations['ai_chatbot_setup']['setup_fee'] = int(1500 * final_multiplier)
            recommendations['ai_chatbot_setup']['monthly_rate'] = int(300 * final_multiplier)
            recommendations['ai_chatbot_setup']['reason'] = 'No AI chatbot detected but contact forms present - high conversion opportunity'
            recommendations['ai_chatbot_setup']['roi_estimate'] = '25-40% increase in lead capture'
        
        # Google Review Automation
        has_review_system = 'reviews' in str(tech_analysis.get('detected_technologies', {})).lower()
        is_local_business = industry in ['restaurants', 'retail', 'healthcare', 'beauty', 'automotive', 'legal', 'construction']
        
        if not has_review_system and is_local_business:
            recommendations['google_review_automation']['recommended'] = True
            recommendations['google_review_automation']['priority'] = 'high'
            recommendations['google_review_automation']['setup_fee'] = int(800 * final_multiplier)
            recommendations['google_review_automation']['monthly_rate'] = int(150 * final_multiplier)
            recommendations['google_review_automation']['reason'] = 'Local business without automated review system - reputation opportunity'
            recommendations['google_review_automation']['roi_estimate'] = '15-30% improvement in local search visibility'
        
        # Missed Call Text Back
        has_phone = any('phone' in method.lower() or 'call' in method.lower() 
                       for method in contact_intel.get('contact_methods', []))
        has_auto_response = 'automation' in str(tech_analysis.get('detected_technologies', {})).lower()
        
        if has_phone and not has_auto_response:
            recommendations['missed_call_text_back']['recommended'] = True
            recommendations['missed_call_text_back']['priority'] = 'high'
            recommendations['missed_call_text_back']['setup_fee'] = int(500 * final_multiplier)
            recommendations['missed_call_text_back']['monthly_rate'] = int(100 * final_multiplier)
            recommendations['missed_call_text_back']['reason'] = 'Phone contact available but no automated follow-up detected'
            recommendations['missed_call_text_back']['roi_estimate'] = '20-35% reduction in missed opportunities'
        
        # Appointment Booking System
        has_booking = any('book' in tech.lower() or 'appointment' in tech.lower() or 'calendar' in tech.lower()
                         for tech in tech_analysis.get('detected_technologies', {}))
        service_based = industry in ['healthcare', 'beauty', 'legal', 'fitness', 'consulting', 'automotive']
        
        if not has_booking and service_based:
            recommendations['appointment_booking']['recommended'] = True
            recommendations['appointment_booking']['priority'] = 'high'
            recommendations['appointment_booking']['setup_fee'] = int(1200 * final_multiplier)
            recommendations['appointment_booking']['monthly_rate'] = int(200 * final_multiplier)
            recommendations['appointment_booking']['reason'] = 'Service-based business without online booking system'
            recommendations['appointment_booking']['roi_estimate'] = '30-50% increase in bookings efficiency'
        
        # Email/SMS Sequences
        has_email_automation = any('email' in tech.lower() and 'automation' in tech.lower() 
                                  for tech in tech_analysis.get('detected_technologies', {}))
        has_crm = any('crm' in tech.lower() for tech in tech_analysis.get('detected_technologies', {}))
        
        if not has_email_automation and not has_crm:
            recommendations['email_sms_sequences']['recommended'] = True
            recommendations['email_sms_sequences']['priority'] = 'medium'
            recommendations['email_sms_sequences']['setup_fee'] = int(2000 * final_multiplier)
            recommendations['email_sms_sequences']['monthly_rate'] = int(400 * final_multiplier)
            recommendations['email_sms_sequences']['reason'] = 'No email automation or CRM detected - nurturing opportunity'
            recommendations['email_sms_sequences']['roi_estimate'] = '40-60% improvement in lead conversion'
        
        # Lead Magnets
        has_lead_magnets = len(contact_intel.get('lead_magnets', [])) > 0
        has_content_offers = 'download' in str(tech_analysis.get('detected_technologies', {})).lower()
        
        if not has_lead_magnets and not has_content_offers:
            recommendations['lead_magnets']['recommended'] = True
            recommendations['lead_magnets']['priority'] = 'medium'
            recommendations['lead_magnets']['setup_fee'] = int(1500 * final_multiplier)
            recommendations['lead_magnets']['monthly_rate'] = int(250 * final_multiplier)
            recommendations['lead_magnets']['reason'] = 'No lead magnets detected - top-funnel opportunity'
            recommendations['lead_magnets']['roi_estimate'] = '25-45% increase in lead generation'
        
        # Funnel Optimization
        has_analytics = any('analytics' in tech.lower() or 'tracking' in tech.lower() 
                           for tech in tech_analysis.get('detected_technologies', {}))
        low_conversion_signals = (
            len(contact_intel.get('contact_methods', [])) < 2 or
            not has_lead_magnets or
            not has_email_automation
        )
        
        if low_conversion_signals or not has_analytics:
            recommendations['funnel_optimization']['recommended'] = True
            recommendations['funnel_optimization']['priority'] = 'high'
            recommendations['funnel_optimization']['setup_fee'] = int(2500 * final_multiplier)
            recommendations['funnel_optimization']['monthly_rate'] = int(500 * final_multiplier)
            recommendations['funnel_optimization']['reason'] = 'Low conversion indicators detected - optimization needed'
            recommendations['funnel_optimization']['roi_estimate'] = '50-80% improvement in funnel performance'
        
        # Calculate total investment and ROI
        total_setup = sum(service['setup_fee'] for service in recommendations.values() if service['recommended'])
        total_monthly = sum(service['monthly_rate'] for service in recommendations.values() if service['recommended'])
        
        summary = {
            'total_recommended_services': sum(1 for service in recommendations.values() if service['recommended']),
            'total_setup_investment': total_setup,
            'total_monthly_investment': total_monthly,
            'industry_focus': industry,
            'business_size': business_size,
            'priority_services': [name for name, service in recommendations.items() 
                                if service['recommended'] and service['priority'] == 'high'],
            'estimated_roi_timeline': '3-6 months',
            'implementation_roadmap': self._create_ghl_implementation_roadmap(recommendations)
        }
        
        return {
            'service_recommendations': recommendations,
            'investment_summary': summary
        }
    
    def _create_ghl_implementation_roadmap(self, recommendations: Dict) -> List[Dict]:
        """Create implementation roadmap for recommended GoHighLevel services"""
        roadmap = []
        
        # Phase 1: Quick wins (1-2 weeks)
        phase1_services = []
        for service, data in recommendations.items():
            if data['recommended'] and 'week' in data['implementation_time'] and '1' in data['implementation_time']:
                phase1_services.append(service.replace('_', ' ').title())
        
        if phase1_services:
            roadmap.append({
                'phase': 1,
                'timeline': '1-2 weeks',
                'focus': 'Quick Wins',
                'services': phase1_services,
                'description': 'Fast implementation services for immediate impact'
            })
        
        # Phase 2: Core automation (3-4 weeks) 
        phase2_services = []
        for service, data in recommendations.items():
            if data['recommended'] and 'week' in data['implementation_time'] and ('2' in data['implementation_time'] or '3' in data['implementation_time']):
                phase2_services.append(service.replace('_', ' ').title())
        
        if phase2_services:
            roadmap.append({
                'phase': 2,
                'timeline': '3-4 weeks',
                'focus': 'Core Automation',
                'services': phase2_services,
                'description': 'Essential automation systems and workflows'
            })
        
        # Phase 3: Advanced optimization (5-6 weeks)
        phase3_services = []
        for service, data in recommendations.items():
            if data['recommended'] and 'week' in data['implementation_time'] and ('4' in data['implementation_time'] or '5' in data['implementation_time'] or '6' in data['implementation_time']):
                phase3_services.append(service.replace('_', ' ').title())
        
        if phase3_services:
            roadmap.append({
                'phase': 3,
                'timeline': '5-6 weeks',
                'focus': 'Advanced Optimization',
                'services': phase3_services,
                'description': 'Comprehensive funnel and conversion optimization'
            })
        
        return roadmap

    def identify_sales_opportunities(self, all_analyses: Dict) -> Dict:
        """Identify specific sales opportunities and gaps"""
        opportunities = {
            'immediate_opportunities': [],
            'medium_term_opportunities': [],
            'long_term_opportunities': [],
            'service_recommendations': {},
            'competitive_advantages': [],
            'risk_factors': [],
            'market_timing': 'unknown'
        }
        
        tech_analysis = all_analyses.get('tech_stack_analysis', {})
        social_intel = all_analyses.get('social_media_intelligence', {})
        budget_analysis = all_analyses.get('budget_indicators', {})
        
        # Immediate opportunities
        if not social_intel.get('social_budget_indicators'):
            opportunities['immediate_opportunities'].append({
                'opportunity': 'social_media_advertising_setup',
                'priority': 'high',
                'estimated_value': '$2,000-$5,000',
                'timeline': '2-4 weeks'
            })
        
        if 'wordpress' in tech_analysis.get('detected_technologies', {}):
            opportunities['immediate_opportunities'].append({
                'opportunity': 'website_optimization_audit',
                'priority': 'high',
                'estimated_value': '$1,500-$3,000',
                'timeline': '1-2 weeks'
            })
        
        # Medium-term opportunities
        if len(social_intel.get('platforms_found', {})) < 3:
            opportunities['medium_term_opportunities'].append({
                'opportunity': 'social_media_strategy_expansion',
                'priority': 'medium',
                'estimated_value': '$3,000-$8,000',
                'timeline': '1-3 months'
            })
        
        # Service recommendations
        opportunities['service_recommendations'] = {
            'digital_marketing': {
                'fit_score': 85,
                'services': ['paid_advertising', 'social_media_management', 'content_marketing'],
                'monthly_retainer': '$3,000-$15,000'
            },
            'web_development': {
                'fit_score': 70,
                'services': ['website_redesign', 'ecommerce_development', 'performance_optimization'],
                'project_value': '$5,000-$25,000'
            },
            'marketing_automation': {
                'fit_score': 60,
                'services': ['email_marketing', 'lead_nurturing', 'crm_integration'],
                'setup_cost': '$2,000-$10,000'
            }
        }
        
        # Add GoHighLevel specific recommendations
        ghl_recommendations = self.analyze_gohighlevel_opportunities(all_analyses)
        opportunities['gohighlevel_services'] = ghl_recommendations
        
        return opportunities

    def generate_unified_report(self, all_analyses: Dict) -> Dict:
        """Generate comprehensive unified report for agency sales"""
        report = {
            'executive_summary': {},
            'key_findings': [],
            'opportunity_assessment': {},
            'competitive_position': {},
            'recommended_approach': {},
            'proposal_framework': {},
            'risk_assessment': {},
            'success_metrics': {}
        }
        
        lead_scoring = all_analyses.get('lead_scoring', {})
        sales_opportunities = all_analyses.get('sales_opportunities', {})
        
        # Executive summary
        report['executive_summary'] = {
            'lead_quality': lead_scoring.get('lead_quality', 'unknown'),
            'overall_score': lead_scoring.get('overall_score', 0),
            'deal_potential': lead_scoring.get('deal_size_estimate', 'unknown'),
            'sales_priority': lead_scoring.get('sales_priority', 'unknown'),
            'recommended_next_action': lead_scoring.get('next_actions', ['research'])[0] if lead_scoring.get('next_actions') else 'research'
        }
        
        # Key findings
        findings = []
        
        if all_analyses.get('budget_indicators', {}).get('overall_budget_level') in ['high', 'medium-high']:
            findings.append('High budget capacity detected - premium service opportunity')
        
        if len(all_analyses.get('social_media_intelligence', {}).get('platforms_found', {})) < 2:
            findings.append('Limited social media presence - expansion opportunity')
        
        if all_analyses.get('tech_stack_analysis', {}).get('modernization_needs'):
            findings.append('Technology modernization needs identified')
        
        report['key_findings'] = findings
        
        # Opportunity assessment
        report['opportunity_assessment'] = {
            'primary_services': [
                service for service, data in sales_opportunities.get('service_recommendations', {}).items()
                if data.get('fit_score', 0) > 70
            ],
            'revenue_potential': lead_scoring.get('deal_size_estimate', 'unknown'),
            'timeline_to_close': lead_scoring.get('sales_cycle_estimate', 'unknown'),
            'success_probability': lead_scoring.get('conversion_probability', 'unknown')
        }
        
        return report

    def auto_save_report(self, result: BusinessIntelligenceResult):
        """Automatically save and organize reports"""
        try:
            # Create reports directory structure
            base_dir = self._create_reports_directory()
            
            # Generate file paths
            company_name = result.company_profile.get('company_name', 'Unknown_Company').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = urlparse(result.url).netloc.replace('www.', '').replace('.', '_')
            
            file_prefix = f"{company_name}_{domain}_{timestamp}"
            
            # Save JSON report
            json_path = base_dir / 'json' / f"{file_prefix}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, ensure_ascii=False)
            
            # Save human-readable report
            readable_path = base_dir / 'reports' / f"{file_prefix}_report.md"
            readable_content = self._generate_comprehensive_report(result)
            with open(readable_path, 'w', encoding='utf-8') as f:
                f.write(readable_content)
            
            # Save executive summary
            executive_path = base_dir / 'executive' / f"{file_prefix}_executive.md"
            executive_content = self._generate_executive_summary_report(result)
            with open(executive_path, 'w', encoding='utf-8') as f:
                f.write(executive_content)
            
            # Save GoHighLevel recommendations if available
            if result.sales_opportunities.get('gohighlevel_services'):
                ghl_path = base_dir / 'gohighlevel' / f"{file_prefix}_ghl.md"
                ghl_content = self._generate_gohighlevel_report(result)
                with open(ghl_path, 'w', encoding='utf-8') as f:
                    f.write(ghl_content)
            
            # Update index
            self._update_reports_index(result, file_prefix, base_dir)
            
            logger.info(f"Reports saved automatically to {base_dir}")
            
        except Exception as e:
            logger.error(f"Error saving reports: {str(e)}")
    
    def _create_reports_directory(self):
        """Create organized directory structure for reports"""
        import os
        from pathlib import Path
        
        base_dir = Path('business_intelligence_reports')
        
        # Create subdirectories
        subdirs = ['json', 'reports', 'executive', 'gohighlevel', 'archives']
        for subdir in subdirs:
            (base_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        return base_dir
    
    def _generate_comprehensive_report(self, result: BusinessIntelligenceResult):
        """Generate comprehensive human-readable report"""
        company_name = result.company_profile.get('company_name', 'Unknown Company')
        lead_data = result.lead_scoring
        
        report = f"""# Comprehensive Business Intelligence Report: {company_name}

**Analysis Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Website:** {result.url}
**Overall Lead Score:** {lead_data.get('overall_score', 0)}/100

---

## 🎯 Executive Summary

### Lead Classification
- **Lead Quality:** {lead_data.get('lead_quality', 'unknown').title()}
- **Sales Priority:** {lead_data.get('sales_priority', 'unknown').title()}  
- **Deal Potential:** {lead_data.get('deal_size_estimate', 'Unknown')}
- **Conversion Probability:** {lead_data.get('conversion_probability', 'unknown').title()}
- **Sales Cycle Estimate:** {lead_data.get('sales_cycle_estimate', 'Unknown')}

### Business Impact Summary
{lead_data.get('business_impact', {}).get('executive_summary', 'Analysis pending')}

---

## 📊 Detailed Score Breakdown

### Overall Score Explanation
{lead_data.get('score_explanations', {}).get('overall_score_explanation', 'Detailed explanation pending')}

### Category Scores
"""
        
        # Add category explanations
        category_explanations = lead_data.get('score_explanations', {}).get('category_explanations', {})
        for category, explanation in category_explanations.items():
            report += f"\n#### {category.replace('_', ' ').title()}\n{explanation}\n"
        
        # Add strengths and improvement areas
        explanations = lead_data.get('score_explanations', {})
        if explanations.get('strengths'):
            report += "\n### 💪 Key Strengths\n"
            for strength in explanations['strengths']:
                report += f"- {strength}\n"
        
        if explanations.get('improvement_areas'):
            report += "\n### 🔧 Improvement Areas\n"
            for area in explanations['improvement_areas']:
                report += f"- {area}\n"
        
        # Add industry benchmarks
        benchmarks = lead_data.get('industry_benchmarks', {})
        if benchmarks:
            report += f"""
---

## 📈 Industry Benchmarking

### Industry Performance Comparison
- **Industry Average Score:** {benchmarks.get('average_score', 'N/A')}
- **Top Quartile Score:** {benchmarks.get('top_quartile', 'N/A')}
- **This Prospect's Score:** {lead_data.get('overall_score', 0)}

### Common Industry Strengths
"""
            for strength in benchmarks.get('common_strengths', []):
                report += f"- {strength}\n"
            
            report += "\n### Common Industry Challenges\n"
            for weakness in benchmarks.get('common_weaknesses', []):
                report += f"- {weakness}\n"
            
            report += f"""
### Industry Benchmarks
- **Typical Deal Size:** {benchmarks.get('typical_deal_size', 'N/A')}
- **Average Sales Cycle:** {benchmarks.get('sales_cycle', 'N/A')}
"""
        
        # Add detailed action plan
        action_plan = lead_data.get('next_actions', {})
        if isinstance(action_plan, dict) and action_plan.get('immediate_actions'):
            report += "\n---\n\n## 🚀 Detailed Action Plan\n\n### Immediate Actions (1-7 days)\n"
            for action in action_plan['immediate_actions']:
                report += f"""
**{action.get('action', 'Action')}**
- Priority: {action.get('priority', 'medium').title()}
- Timeline: {action.get('timeline', 'TBD')}
- Resources: {', '.join(action.get('resources', []))}
- Expected Outcome: {action.get('outcome', 'TBD')}
"""
            
            if action_plan.get('short_term_actions'):
                report += "\n### Short-term Actions (1-4 weeks)\n"
                for action in action_plan['short_term_actions']:
                    report += f"""
**{action.get('action', 'Action')}**
- Priority: {action.get('priority', 'medium').title()}
- Timeline: {action.get('timeline', 'TBD')}
- Expected Outcome: {action.get('outcome', 'TBD')}
"""
        
        # Add quick wins
        quick_wins = lead_data.get('quick_wins', [])
        if quick_wins:
            report += "\n### ⚡ Quick Wins\n"
            for win in quick_wins:
                report += f"""
**{win.get('opportunity', 'Opportunity')}**
- Effort: {win.get('effort', 'TBD')}
- Impact: {win.get('impact', 'TBD')}
- Timeline: {win.get('timeline', 'TBD')}
- ROI Potential: {win.get('roi_potential', 'TBD')}
"""
        
        # Add social media analysis
        social_intel = result.social_media_intelligence
        if social_intel.get('detailed_analysis'):
            report += "\n---\n\n## 📱 Social Media Intelligence\n\n"
            
            detailed = social_intel['detailed_analysis']
            optimization = detailed.get('business_optimization_level', {})
            
            report += f"""### Overall Social Media Optimization
- **Optimization Score:** {optimization.get('overall_score', 0):.1f}/100
- **Optimization Level:** {optimization.get('level', 'unknown').title()}
- **Improvement Potential:** {optimization.get('improvement_potential', 0):.1f}%

### Platform Analysis
"""
            
            for platform, analysis in detailed.get('profile_completeness', {}).items():
                report += f"""
**{platform.title()}**
- Profile Strength: {analysis.get('profile_strength', 'unknown').title()}
- Optimization Score: {analysis.get('optimization_score', 0)}/100
- Business Features: {', '.join(analysis.get('business_features', []))}
"""
        
        # Add GoHighLevel recommendations
        ghl_data = result.sales_opportunities.get('gohighlevel_services', {})
        if ghl_data:
            report += "\n---\n\n## 🔧 GoHighLevel Service Opportunities\n\n"
            
            investment = ghl_data.get('investment_summary', {})
            report += f"""### Investment Summary
- **Recommended Services:** {investment.get('total_recommended_services', 0)}
- **Total Setup Investment:** ${investment.get('total_setup_investment', 0):,}
- **Monthly Investment:** ${investment.get('total_monthly_investment', 0):,}
- **Industry Focus:** {investment.get('industry_focus', 'General').title()}
- **ROI Timeline:** {investment.get('estimated_roi_timeline', 'Unknown')}

### Priority Services
"""
            
            priority_services = investment.get('priority_services', [])
            service_recs = ghl_data.get('service_recommendations', {})
            
            for service_name in priority_services:
                service_key = service_name.lower().replace(' ', '_')
                if service_key in service_recs:
                    service = service_recs[service_key]
                    report += f"""
**{service_name}**
- Setup Fee: ${service.get('setup_fee', 0):,}
- Monthly Rate: ${service.get('monthly_rate', 0):,}
- Implementation Time: {service.get('implementation_time', 'TBD')}
- ROI Estimate: {service.get('roi_estimate', 'TBD')}
- Reason: {service.get('reason', 'TBD')}
"""
        
        report += f"""

---

## 📋 Report Summary

This comprehensive analysis provides actionable insights for engaging with {company_name}. The {lead_data.get('lead_quality', 'unknown')} lead quality indicates {lead_data.get('sales_priority', 'standard')} priority handling with an estimated {lead_data.get('sales_cycle_estimate', 'standard')} sales cycle.

**Next Steps:** Begin with the immediate actions outlined above, focusing on {lead_data.get('next_actions', {}).get('immediate_actions', [{}])[0].get('action', 'initial contact') if isinstance(lead_data.get('next_actions'), dict) and lead_data.get('next_actions', {}).get('immediate_actions') else 'initial contact'}.

---

*Report generated by Business Intelligence Analyzer*  
*Generation Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
        
        return report
    
    def _generate_executive_summary_report(self, result: BusinessIntelligenceResult):
        """Generate executive-level summary report"""
        company_name = result.company_profile.get('company_name', 'Unknown Company')
        lead_data = result.lead_scoring
        
        return f"""# Executive Summary: {company_name}

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Analyst:** Business Intelligence System  
**Subject:** Lead Qualification and Opportunity Assessment

---

## Key Findings

{company_name} represents a **{lead_data.get('lead_quality', 'unknown').upper()}** opportunity with {lead_data.get('overall_score', 0)}/100 qualification score.

### Business Impact
{lead_data.get('business_impact', {}).get('executive_summary', 'Detailed analysis indicates standard business opportunity with moderate engagement potential.')}

### Revenue Opportunity
- **Deal Size:** {lead_data.get('deal_size_estimate', 'To be determined')}
- **Timeline:** {lead_data.get('sales_cycle_estimate', 'Standard sales cycle expected')}
- **Conversion Probability:** {lead_data.get('conversion_probability', 'Moderate').title()}

### Competitive Position
{lead_data.get('business_impact', {}).get('competitive_advantage', 'Standard competitive positioning with opportunity for early engagement advantage.')}

## Recommended Action

**Priority Level:** {lead_data.get('sales_priority', 'Standard').title()}

**Immediate Next Steps:**
"""
        
        # Add next actions
        if isinstance(lead_data.get('next_actions'), dict):
            immediate_actions = lead_data.get('next_actions', {}).get('immediate_actions', [])
            for action in immediate_actions[:3]:  # Top 3 actions
                return f"1. {action.get('action', 'Contact prospect')}\n"
        else:
            return "1. Initiate contact following standard qualification process\n"
        
        return """

## Risk Assessment
{lead_data.get('business_impact', {}).get('risk_assessment', 'Standard business risk profile with typical market considerations.')}

---

**Recommendation:** {"IMMEDIATE ACTION REQUIRED" if lead_data.get('lead_quality') == 'premium' else "PRIORITY ENGAGEMENT" if lead_data.get('lead_quality') == 'qualified' else "NURTURE TRACK APPROPRIATE"}

*Confidential Business Intelligence Report*
"""
    
    def _generate_gohighlevel_report(self, result: BusinessIntelligenceResult):
        """Generate specialized GoHighLevel recommendations report"""
        ghl_data = result.sales_opportunities.get('gohighlevel_services', {})
        company_name = result.company_profile.get('company_name', 'Unknown Company')
        
        if not ghl_data:
            return f"# GoHighLevel Analysis: {company_name}\n\nNo specific GoHighLevel opportunities identified at this time."
        
        investment = ghl_data.get('investment_summary', {})
        service_recs = ghl_data.get('service_recommendations', {})
        
        report = f"""# GoHighLevel Service Recommendations: {company_name}

**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
**Total Investment:** ${investment.get('total_setup_investment', 0):,} setup + ${investment.get('total_monthly_investment', 0):,}/month

---

## Service Opportunities

"""
        
        # Priority services first
        priority_services = investment.get('priority_services', [])
        for service_name in priority_services:
            service_key = service_name.lower().replace(' ', '_')
            if service_key in service_recs:
                service = service_recs[service_key]
                report += f"""### 🔥 {service_name} (HIGH PRIORITY)

**Investment:** ${service.get('setup_fee', 0):,} setup + ${service.get('monthly_rate', 0):,}/month  
**Implementation:** {service.get('implementation_time', 'TBD')}  
**ROI Estimate:** {service.get('roi_estimate', 'TBD')}

**Why This Service:**  
{service.get('reason', 'Service recommendation based on gap analysis')}

"""
        
        # All recommended services
        report += "\n## Complete Service Breakdown\n\n"
        for service_name, service in service_recs.items():
            if service.get('recommended'):
                formatted_name = service_name.replace('_', ' ').title()
                priority_label = "HIGH PRIORITY" if service_name in [s.lower().replace(' ', '_') for s in priority_services] else "RECOMMENDED"
                
                report += f"""**{formatted_name}** - {priority_label}
- Setup: ${service.get('setup_fee', 0):,}
- Monthly: ${service.get('monthly_rate', 0):,}
- Timeline: {service.get('implementation_time', 'TBD')}
- ROI: {service.get('roi_estimate', 'TBD')}

"""
        
        # Implementation roadmap
        roadmap = investment.get('implementation_roadmap', [])
        if roadmap:
            report += "\n## Implementation Roadmap\n\n"
            for phase in roadmap:
                report += f"""### Phase {phase.get('phase', 1)}: {phase.get('focus', 'Implementation')}
**Timeline:** {phase.get('timeline', 'TBD')}  
**Services:** {', '.join(phase.get('services', []))}  
**Focus:** {phase.get('description', 'Implementation phase')}

"""
        
        report += f"""
---

## Next Steps

1. **Priority Assessment:** Review high-priority services for immediate implementation
2. **Budget Approval:** Secure approval for ${investment.get('total_setup_investment', 0):,} initial investment
3. **Implementation Planning:** Schedule {investment.get('estimated_roi_timeline', '3-6 month')} implementation timeline
4. **Success Metrics:** Establish KPIs for measuring ROI

**Total ROI Timeline:** {investment.get('estimated_roi_timeline', 'Unknown')}

*GoHighLevel Service Analysis - Confidential*
"""
        
        return report
    
    def _update_reports_index(self, result: BusinessIntelligenceResult, file_prefix: str, base_dir):
        """Update central reports index"""
        index_path = base_dir / 'reports_index.json'
        
        # Load existing index
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {'reports': [], 'summary': {'total_reports': 0, 'by_quality': {}, 'by_industry': {}}}
        
        # Add new report entry
        report_entry = {
            'id': file_prefix,
            'timestamp': result.timestamp,
            'url': result.url,
            'company_name': result.company_profile.get('company_name', 'Unknown Company'),
            'industry': result.company_profile.get('industry', 'unknown'),
            'lead_quality': result.lead_scoring.get('lead_quality', 'unknown'),
            'overall_score': result.lead_scoring.get('overall_score', 0),
            'deal_size_estimate': result.lead_scoring.get('deal_size_estimate', 'unknown'),
            'files': {
                'json': f'json/{file_prefix}.json',
                'report': f'reports/{file_prefix}_report.md',
                'executive': f'executive/{file_prefix}_executive.md'
            }
        }
        
        # Add GoHighLevel file if available
        if result.sales_opportunities.get('gohighlevel_services'):
            report_entry['files']['gohighlevel'] = f'gohighlevel/{file_prefix}_ghl.md'
        
        # Update index
        index_data['reports'].insert(0, report_entry)  # Most recent first
        index_data['summary']['total_reports'] = len(index_data['reports'])
        
        # Update summaries
        quality_counts = {}
        industry_counts = {}
        
        for report in index_data['reports']:
            quality = report.get('lead_quality', 'unknown')
            industry = report.get('industry', 'unknown')
            
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        index_data['summary']['by_quality'] = quality_counts
        index_data['summary']['by_industry'] = industry_counts
        
        # Save updated index
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

    def analyze_business_intelligence(self, url: str) -> Optional[BusinessIntelligenceResult]:
        """Perform comprehensive business intelligence analysis"""
        logger.info(f"Starting comprehensive BI analysis for: {url}")
        
        soup = self.fetch_website(url)
        if not soup:
            return None
        
        # Extract all intelligence components
        company_profile = self.extract_company_profile(soup, url)
        social_intel = self.analyze_social_media_intelligence(soup, url)
        tech_analysis = self.analyze_tech_stack(soup, url)
        competitor_analysis = self.analyze_competitors(soup, url)
        budget_analysis = self.analyze_budget_indicators(soup, url, tech_analysis, social_intel)
        traffic_analysis = self.analyze_traffic_and_marketing(soup, url)
        contact_intel = self.extract_contact_intelligence(soup, url)
        
        # Calculate lead scoring
        lead_scoring = self.calculate_lead_scoring(
            company_profile, social_intel, tech_analysis, budget_analysis, contact_intel
        )
        
        # Compile all analyses for sales opportunities
        all_analyses = {
            'company_profile': company_profile,
            'social_media_intelligence': social_intel,
            'tech_stack_analysis': tech_analysis,
            'competitor_analysis': competitor_analysis,
            'budget_indicators': budget_analysis,
            'traffic_analysis': traffic_analysis,
            'contact_intelligence': contact_intel,
            'lead_scoring': lead_scoring
        }
        
        # Identify sales opportunities
        sales_opportunities = self.identify_sales_opportunities(all_analyses)
        all_analyses['sales_opportunities'] = sales_opportunities
        
        # Generate unified report
        unified_report = self.generate_unified_report(all_analyses)
        
        logger.info(f"BI analysis completed for: {url} - Lead Score: {lead_scoring.get('overall_score', 0)}")
        
        # Create analysis result before auto-saving
        result = BusinessIntelligenceResult(
            url=url,
            timestamp=datetime.now().isoformat(),
            company_profile=company_profile,
            social_media_intelligence=social_intel,
            tech_stack_analysis=tech_analysis,
            competitor_analysis=competitor_analysis,
            budget_indicators=budget_analysis,
            traffic_analysis=traffic_analysis,
            contact_intelligence=contact_intel,
            lead_scoring=lead_scoring,
            sales_opportunities=sales_opportunities,
            unified_report=unified_report
        )
        
        # Automatic report saving and organization
        self.auto_save_report(result)
        
        return result

def main():
    parser = argparse.ArgumentParser(description='Business Intelligence Website Analyzer for Agency Sales')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--format', choices=['json', 'report'], default='report',
                       help='Output format (default: report)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    analyzer = BusinessIntelligenceAnalyzer()
    result = analyzer.analyze_business_intelligence(args.url)
    
    if not result:
        print("Failed to analyze website. Please check the URL and try again.")
        return
    
    if args.format == 'json':
        output = json.dumps(asdict(result), indent=2)
    else:
        # Generate executive summary report
        report_data = result.unified_report
        lead_data = result.lead_scoring
        
        output = f"""
# Business Intelligence Report: {result.company_profile.get('company_name', 'Unknown Company')}

**URL:** {result.url}
**Analysis Date:** {result.timestamp}
**Lead Score:** {lead_data.get('overall_score', 0)}/100

## Executive Summary
- **Lead Quality:** {report_data['executive_summary'].get('lead_quality', 'Unknown').title()}
- **Deal Potential:** {report_data['executive_summary'].get('deal_potential', 'Unknown')}
- **Sales Priority:** {report_data['executive_summary'].get('sales_priority', 'Unknown').title()}
- **Conversion Probability:** {lead_data.get('conversion_probability', 'Unknown')}

## Company Profile
- **Industry:** {result.company_profile.get('industry', 'Unknown').title()}
- **Business Size:** {result.company_profile.get('business_size', 'Unknown')}
- **Location:** {result.company_profile.get('location', 'Unknown')}
- **Employees:** {result.company_profile.get('employees', 'Unknown')}

## Technology Stack
- **Sophistication Score:** {result.tech_stack_analysis.get('tech_sophistication_score', 0)}
- **Detected Technologies:** {len(result.tech_stack_analysis.get('detected_technologies', {}))}
- **Budget Level:** {result.tech_stack_analysis.get('budget_implications', {}).get('level', 'Unknown')}

## Social Media Intelligence  
- **Platforms Found:** {len(result.social_media_intelligence.get('platforms_found', {}))}
- **Advertising Detected:** {len(result.social_media_intelligence.get('social_budget_indicators', []))} channels
- **Social Strategy:** {result.social_media_intelligence.get('social_strategy_assessment', {}).get('maturity', 'Unknown')}

## Budget Analysis
- **Budget Level:** {result.budget_indicators.get('overall_budget_level', 'Unknown').title()}
- **Monthly Spend Estimate:** {result.budget_indicators.get('monthly_spend_estimate', 'Unknown')}
- **Investment Capacity:** {result.budget_indicators.get('investment_capacity', 'Unknown')}

## Sales Opportunities
### Immediate Opportunities:
"""
        
        for opp in result.sales_opportunities.get('immediate_opportunities', []):
            output += f"- **{opp['opportunity'].replace('_', ' ').title()}:** {opp['estimated_value']} ({opp['timeline']})\n"
        
        output += f"""
### Service Recommendations:
"""
        
        for service, data in result.sales_opportunities.get('service_recommendations', {}).items():
            output += f"- **{service.replace('_', ' ').title()}:** Fit Score {data['fit_score']}%\n"
        
        output += f"""
## Next Actions
{chr(10).join(f"- {action.replace('_', ' ').title()}" for action in lead_data.get('next_actions', []))}

## Key Findings
{chr(10).join(f"- {finding}" for finding in report_data.get('key_findings', []))}
"""
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()