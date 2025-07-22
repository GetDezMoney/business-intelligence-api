#!/usr/bin/env python3
"""
Website Automation Opportunity Analyzer

Analyzes websites for automation opportunities including chatbots, lead capture,
email signup, social media integration, reviews, appointment booking, mobile
optimization, and contact methods.
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import time


@dataclass
class AnalysisResult:
    """Container for analysis results"""
    url: str
    timestamp: str
    chatbot_analysis: Dict
    lead_capture_analysis: Dict
    email_signup_analysis: Dict
    social_media_analysis: Dict
    review_analysis: Dict
    booking_analysis: Dict
    mobile_analysis: Dict
    contact_analysis: Dict
    seo_analysis: Dict
    automation_score: int
    recommendations: List[Dict]


class WebsiteAnalyzer:
    """Comprehensive website analyzer for automation opportunities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Common selectors and patterns
        self.chatbot_selectors = [
            '[id*="chat"]', '[class*="chat"]', '[id*="messenger"]', '[class*="messenger"]',
            '[id*="intercom"]', '[class*="intercom"]', '[id*="zendesk"]', '[class*="zendesk"]',
            '[id*="drift"]', '[class*="drift"]', '[id*="tawk"]', '[class*="tawk"]',
            'iframe[src*="chat"]', 'iframe[src*="messenger"]'
        ]
        
        self.form_selectors = [
            'form', 'input[type="email"]', 'input[type="text"]', 'textarea',
            '[class*="form"]', '[id*="form"]', '[class*="contact"]', '[id*="contact"]'
        ]
        
        self.social_platforms = [
            'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest',
            'tiktok', 'snapchat', 'whatsapp', 'telegram'
        ]
        
        self.booking_keywords = [
            'appointment', 'booking', 'schedule', 'calendar', 'reserve',
            'calendly', 'acuity', 'booksy', 'setmore'
        ]
        
        self.review_platforms = [
            'google', 'yelp', 'trustpilot', 'facebook', 'tripadvisor',
            'reviews', 'testimonial', 'rating'
        ]
        
        # SEO optimization thresholds
        self.seo_thresholds = {
            'title_min_length': 30,
            'title_max_length': 60,
            'description_min_length': 120,
            'description_max_length': 160,
            'h1_max_count': 1,
            'alt_text_threshold': 80  # percentage
        }
        
        # Local SEO indicators
        self.local_seo_keywords = [
            'address', 'phone', 'hours', 'location', 'near me', 'local',
            'city', 'state', 'zip code', 'directions', 'map'
        ]
        
        # Schema markup types
        self.schema_types = [
            'organization', 'localbusiness', 'person', 'product', 'service',
            'review', 'breadcrumb', 'faq', 'article', 'website'
        ]

    def fetch_website(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse website content"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def analyze_chatbot(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze chatbot presence and implementation"""
        result = {
            'has_chatbot': False,
            'chatbot_type': None,
            'implementation': None,
            'issues': [],
            'opportunities': []
        }
        
        # Check for common chatbot implementations
        for selector in self.chatbot_selectors:
            elements = soup.select(selector)
            if elements:
                result['has_chatbot'] = True
                result['implementation'] = 'detected'
                
                # Identify chatbot type
                for elem in elements:
                    elem_str = str(elem).lower()
                    if 'intercom' in elem_str:
                        result['chatbot_type'] = 'Intercom'
                    elif 'zendesk' in elem_str:
                        result['chatbot_type'] = 'Zendesk Chat'
                    elif 'drift' in elem_str:
                        result['chatbot_type'] = 'Drift'
                    elif 'tawk' in elem_str:
                        result['chatbot_type'] = 'Tawk.to'
                    elif 'messenger' in elem_str:
                        result['chatbot_type'] = 'Facebook Messenger'
                break
        
        # Check for chatbot scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string.lower()
                if any(bot in script_content for bot in ['intercom', 'zendesk', 'drift', 'tawk']):
                    result['has_chatbot'] = True
                    result['implementation'] = 'script'
        
        if not result['has_chatbot']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add live chat/chatbot for instant customer support',
                'implementation': 'Consider Intercom, Zendesk Chat, or custom chatbot integration',
                'impact': 'Improve customer engagement and reduce response time'
            })
        
        return result

    def analyze_lead_capture(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze lead capture forms and mechanisms"""
        result = {
            'has_lead_capture': False,
            'forms_count': 0,
            'form_types': [],
            'issues': [],
            'opportunities': []
        }
        
        forms = soup.find_all('form')
        result['forms_count'] = len(forms)
        
        for form in forms:
            form_inputs = form.find_all(['input', 'textarea', 'select'])
            input_types = [inp.get('type', 'text') for inp in form.find_all('input')]
            
            if 'email' in input_types:
                result['has_lead_capture'] = True
                result['form_types'].append('email_capture')
            
            if any(inp.get('name', '').lower() in ['phone', 'telephone'] for inp in form_inputs):
                result['form_types'].append('contact_form')
            
            if len(form_inputs) > 3:
                result['form_types'].append('detailed_form')
        
        # Check for popup/modal forms
        modals = soup.find_all(['div'], class_=re.compile(r'modal|popup|overlay', re.I))
        for modal in modals:
            if modal.find('form'):
                result['form_types'].append('popup_form')
        
        if result['forms_count'] == 0:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add lead capture forms',
                'implementation': 'Create contact forms, newsletter signup, or lead magnets',
                'impact': 'Generate leads and build customer database'
            })
        elif not result['has_lead_capture']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Optimize existing forms for lead capture',
                'implementation': 'Add email fields and lead magnets to current forms',
                'impact': 'Increase lead generation from existing traffic'
            })
        
        return result

    def analyze_email_signup(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze email signup and newsletter functionality"""
        result = {
            'has_email_signup': False,
            'signup_locations': [],
            'email_service': None,
            'issues': [],
            'opportunities': []
        }
        
        # Look for email inputs
        email_inputs = soup.find_all('input', type='email')
        if email_inputs:
            result['has_email_signup'] = True
            
            for input_elem in email_inputs:
                parent_form = input_elem.find_parent('form')
                if parent_form:
                    # Determine location context
                    if 'footer' in str(parent_form.get('class', [])).lower():
                        result['signup_locations'].append('footer')
                    elif 'header' in str(parent_form.get('class', [])).lower():
                        result['signup_locations'].append('header')
                    else:
                        result['signup_locations'].append('content')
        
        # Check for email service integrations
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('src'):
                src = script.get('src').lower()
                if 'mailchimp' in src:
                    result['email_service'] = 'Mailchimp'
                elif 'constant-contact' in src:
                    result['email_service'] = 'Constant Contact'
                elif 'convertkit' in src:
                    result['email_service'] = 'ConvertKit'
        
        # Look for newsletter keywords
        text_content = soup.get_text().lower()
        newsletter_keywords = ['newsletter', 'subscribe', 'email updates', 'mailing list']
        has_newsletter_content = any(keyword in text_content for keyword in newsletter_keywords)
        
        if not result['has_email_signup'] and not has_newsletter_content:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add email newsletter signup',
                'implementation': 'Integrate with email service like Mailchimp, ConvertKit, or Constant Contact',
                'impact': 'Build email list for marketing and customer retention'
            })
        elif has_newsletter_content and not result['has_email_signup']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add functional email signup form',
                'implementation': 'Connect existing newsletter mentions to actual signup functionality',
                'impact': 'Convert newsletter interest into actual subscribers'
            })
        
        return result

    def analyze_social_media(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze social media integration and presence"""
        result = {
            'social_links': {},
            'social_widgets': [],
            'sharing_buttons': False,
            'issues': [],
            'opportunities': []
        }
        
        # Find social media links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            for platform in self.social_platforms:
                if platform in href and any(domain in href for domain in ['.com', '.co']):
                    result['social_links'][platform] = href
        
        # Check for social media widgets/embeds
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '').lower()
            if 'facebook' in src:
                result['social_widgets'].append('Facebook')
            elif 'twitter' in src:
                result['social_widgets'].append('Twitter')
            elif 'instagram' in src:
                result['social_widgets'].append('Instagram')
        
        # Check for social sharing buttons
        share_indicators = ['share', 'tweet', 'like', 'follow']
        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in share_indicators):
            share_elements = soup.find_all(['a', 'button'], string=re.compile(r'share|tweet|like', re.I))
            if share_elements:
                result['sharing_buttons'] = True
        
        if len(result['social_links']) < 3:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Expand social media presence',
                'implementation': f'Add profiles on {", ".join([p for p in self.social_platforms[:5] if p not in result["social_links"]])}',
                'impact': 'Increase brand visibility and customer engagement'
            })
        
        if not result['sharing_buttons']:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Add social sharing buttons',
                'implementation': 'Install social sharing plugin or custom buttons',
                'impact': 'Increase content virality and social reach'
            })
        
        return result

    def analyze_reviews(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze review display and management"""
        result = {
            'has_reviews': False,
            'review_sources': [],
            'review_widgets': [],
            'issues': [],
            'opportunities': []
        }
        
        page_text = soup.get_text().lower()
        
        # Check for review content
        review_keywords = ['review', 'testimonial', 'rating', 'stars', 'feedback']
        if any(keyword in page_text for keyword in review_keywords):
            result['has_reviews'] = True
        
        # Check for specific review platform integrations
        for platform in self.review_platforms:
            if platform in page_text:
                result['review_sources'].append(platform)
        
        # Look for review widgets/embeds
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '').lower()
            if 'google' in src and 'review' in src:
                result['review_widgets'].append('Google Reviews')
            elif 'yelp' in src:
                result['review_widgets'].append('Yelp')
            elif 'trustpilot' in src:
                result['review_widgets'].append('Trustpilot')
        
        # Check for star ratings
        star_elements = soup.find_all(['span', 'div'], class_=re.compile(r'star|rating', re.I))
        if star_elements:
            result['has_reviews'] = True
        
        if not result['has_reviews']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add customer reviews and testimonials',
                'implementation': 'Display Google Reviews, testimonials, or integrate review platform',
                'impact': 'Build trust and credibility with potential customers'
            })
        elif len(result['review_sources']) == 0:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Integrate with review platforms',
                'implementation': 'Connect with Google My Business, Yelp, or Trustpilot',
                'impact': 'Leverage existing reviews for better credibility'
            })
        
        return result

    def analyze_booking(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze appointment booking and scheduling systems"""
        result = {
            'has_booking': False,
            'booking_system': None,
            'booking_type': [],
            'issues': [],
            'opportunities': []
        }
        
        page_text = soup.get_text().lower()
        
        # Check for booking-related keywords
        if any(keyword in page_text for keyword in self.booking_keywords):
            result['has_booking'] = True
        
        # Check for specific booking platforms
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('src'):
                src = script.get('src').lower()
                if 'calendly' in src:
                    result['booking_system'] = 'Calendly'
                    result['has_booking'] = True
                elif 'acuity' in src:
                    result['booking_system'] = 'Acuity Scheduling'
                    result['has_booking'] = True
                elif 'booksy' in src:
                    result['booking_system'] = 'Booksy'
                    result['has_booking'] = True
        
        # Check for booking iframes
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '').lower()
            if any(platform in src for platform in ['calendly', 'acuity', 'booksy', 'setmore']):
                result['has_booking'] = True
        
        # Determine booking type based on content
        if 'appointment' in page_text:
            result['booking_type'].append('appointments')
        if 'reservation' in page_text:
            result['booking_type'].append('reservations')
        if 'consultation' in page_text:
            result['booking_type'].append('consultations')
        
        if not result['has_booking']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add online booking system',
                'implementation': 'Integrate Calendly, Acuity Scheduling, or custom booking solution',
                'impact': 'Automate appointment scheduling and reduce admin work'
            })
        
        return result

    def analyze_mobile(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze mobile optimization"""
        result = {
            'has_viewport_meta': False,
            'responsive_design': False,
            'mobile_menu': False,
            'touch_friendly': False,
            'issues': [],
            'opportunities': []
        }
        
        # Check for viewport meta tag
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta:
            result['has_viewport_meta'] = True
        
        # Check for responsive design indicators
        stylesheets = soup.find_all('link', rel='stylesheet')
        styles = soup.find_all('style')
        
        responsive_indicators = ['@media', 'responsive', 'mobile', 'tablet']
        for stylesheet in stylesheets:
            if stylesheet.get('href'):
                href = stylesheet.get('href').lower()
                if any(indicator in href for indicator in responsive_indicators):
                    result['responsive_design'] = True
                    break
        
        for style in styles:
            if style.string and any(indicator in style.string.lower() for indicator in responsive_indicators):
                result['responsive_design'] = True
                break
        
        # Check for mobile menu
        mobile_menu_selectors = [
            '[class*="mobile-menu"]', '[id*="mobile-menu"]',
            '[class*="hamburger"]', '[id*="hamburger"]',
            '[class*="nav-toggle"]', '[id*="nav-toggle"]'
        ]
        
        for selector in mobile_menu_selectors:
            if soup.select(selector):
                result['mobile_menu'] = True
                break
        
        # Basic touch-friendly check (button sizes, etc.)
        buttons = soup.find_all(['button', 'a'])
        if len(buttons) > 0:
            result['touch_friendly'] = True
        
        # Generate recommendations
        if not result['has_viewport_meta']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add viewport meta tag for mobile optimization',
                'implementation': 'Add <meta name="viewport" content="width=device-width, initial-scale=1">',
                'impact': 'Ensure proper mobile display and SEO ranking'
            })
        
        if not result['responsive_design']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Implement responsive design',
                'implementation': 'Use CSS media queries and flexible layouts',
                'impact': 'Improve mobile user experience and search rankings'
            })
        
        if not result['mobile_menu']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add mobile-friendly navigation menu',
                'implementation': 'Implement hamburger menu or collapsible navigation',
                'impact': 'Improve mobile navigation experience'
            })
        
        return result

    def analyze_contact_methods(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze available contact methods"""
        result = {
            'contact_methods': [],
            'has_contact_page': False,
            'phone_numbers': [],
            'email_addresses': [],
            'physical_address': False,
            'contact_form': False,
            'issues': [],
            'opportunities': []
        }
        
        page_text = soup.get_text()
        
        # Check for contact page
        links = soup.find_all('a', href=True)
        for link in links:
            link_text = link.get_text().lower()
            href = link.get('href').lower()
            if 'contact' in link_text or 'contact' in href:
                result['has_contact_page'] = True
                result['contact_methods'].append('contact_page')
                break
        
        # Find phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, page_text)
        if phone_matches:
            result['phone_numbers'] = phone_matches[:3]  # Limit to first 3
            result['contact_methods'].append('phone')
        
        # Find email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, page_text)
        if email_matches:
            result['email_addresses'] = email_matches[:3]  # Limit to first 3
            result['contact_methods'].append('email')
        
        # Check for physical address indicators
        address_keywords = ['address', 'street', 'avenue', 'road', 'suite', 'floor']
        if any(keyword in page_text.lower() for keyword in address_keywords):
            result['physical_address'] = True
            result['contact_methods'].append('address')
        
        # Check for contact forms
        forms = soup.find_all('form')
        for form in forms:
            form_inputs = form.find_all(['input', 'textarea'])
            input_types = [inp.get('type', 'text') for inp in form.find_all('input')]
            if 'email' in input_types or any(inp.get('name', '').lower() in ['email', 'message', 'subject'] for inp in form_inputs):
                result['contact_form'] = True
                result['contact_methods'].append('contact_form')
                break
        
        # Generate recommendations
        if len(result['contact_methods']) < 2:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add multiple contact methods',
                'implementation': 'Include phone, email, contact form, and physical address',
                'impact': 'Make it easier for customers to reach you'
            })
        
        if not result['contact_form']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add contact form for inquiries',
                'implementation': 'Create a simple contact form with name, email, and message fields',
                'impact': 'Provide easy way for customers to send inquiries'
            })
        
        return result

    def analyze_seo(self, soup: BeautifulSoup, url: str) -> Dict:
        """Comprehensive SEO analysis"""
        result = {
            'meta_tags': {},
            'page_speed_indicators': {},
            'images': {},
            'schema_markup': {},
            'local_seo': {},
            'page_titles': {},
            'header_structure': {},
            'url_structure': {},
            'internal_links': {},
            'seo_score': 0,
            'issues': [],
            'opportunities': []
        }
        
        # Analyze meta tags
        result['meta_tags'] = self.analyze_meta_tags(soup, url)
        
        # Analyze page speed indicators
        result['page_speed_indicators'] = self.analyze_page_speed_indicators(soup, url)
        
        # Analyze images and alt text
        result['images'] = self.analyze_images_alt_text(soup, url)
        
        # Analyze schema markup
        result['schema_markup'] = self.analyze_schema_markup(soup, url)
        
        # Analyze local SEO signals
        result['local_seo'] = self.analyze_local_seo(soup, url)
        
        # Analyze page titles
        result['page_titles'] = self.analyze_page_titles(soup, url)
        
        # Analyze header structure
        result['header_structure'] = self.analyze_header_structure(soup, url)
        
        # Analyze URL structure
        result['url_structure'] = self.analyze_url_structure(soup, url)
        
        # Analyze internal linking
        result['internal_links'] = self.analyze_internal_links(soup, url)
        
        # Calculate SEO score
        result['seo_score'] = self.calculate_seo_score(result)
        
        # Collect all SEO opportunities
        for analysis_key, analysis_data in result.items():
            if isinstance(analysis_data, dict) and 'opportunities' in analysis_data:
                result['opportunities'].extend(analysis_data['opportunities'])
        
        return result

    def analyze_meta_tags(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze meta tags for SEO"""
        result = {
            'title': None,
            'title_length': 0,
            'description': None,
            'description_length': 0,
            'keywords': None,
            'robots': None,
            'canonical': None,
            'og_tags': {},
            'twitter_cards': {},
            'issues': [],
            'opportunities': []
        }
        
        # Title tag
        title_tag = soup.find('title')
        if title_tag:
            result['title'] = title_tag.get_text().strip()
            result['title_length'] = len(result['title'])
            
            if result['title_length'] < self.seo_thresholds['title_min_length']:
                result['opportunities'].append({
                    'priority': 'high',
                    'recommendation': 'Increase title tag length',
                    'implementation': f'Expand title to {self.seo_thresholds["title_min_length"]}-{self.seo_thresholds["title_max_length"]} characters',
                    'impact': 'Improve search engine visibility and click-through rates'
                })
            elif result['title_length'] > self.seo_thresholds['title_max_length']:
                result['opportunities'].append({
                    'priority': 'medium',
                    'recommendation': 'Shorten title tag',
                    'implementation': f'Reduce title to under {self.seo_thresholds["title_max_length"]} characters',
                    'impact': 'Prevent title truncation in search results'
                })
        else:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add title tag',
                'implementation': 'Add descriptive title tag to page head',
                'impact': 'Critical for search engine ranking and user experience'
            })
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            result['description'] = desc_tag.get('content', '').strip()
            result['description_length'] = len(result['description'])
            
            if result['description_length'] < self.seo_thresholds['description_min_length']:
                result['opportunities'].append({
                    'priority': 'medium',
                    'recommendation': 'Expand meta description',
                    'implementation': f'Increase description to {self.seo_thresholds["description_min_length"]}-{self.seo_thresholds["description_max_length"]} characters',
                    'impact': 'Improve search result snippets and click-through rates'
                })
            elif result['description_length'] > self.seo_thresholds['description_max_length']:
                result['opportunities'].append({
                    'priority': 'low',
                    'recommendation': 'Shorten meta description',
                    'implementation': f'Reduce description to under {self.seo_thresholds["description_max_length"]} characters',
                    'impact': 'Prevent description truncation in search results'
                })
        else:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add meta description',
                'implementation': 'Add compelling meta description summarizing page content',
                'impact': 'Improve search result appearance and click-through rates'
            })
        
        # Meta keywords (deprecated but still checked)
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            result['keywords'] = keywords_tag.get('content', '').strip()
        
        # Robots meta
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        if robots_tag:
            result['robots'] = robots_tag.get('content', '').strip()
        
        # Canonical URL
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        if canonical_tag:
            result['canonical'] = canonical_tag.get('href', '').strip()
        else:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add canonical URL',
                'implementation': 'Add canonical link tag to prevent duplicate content issues',
                'impact': 'Improve SEO by consolidating page authority'
            })
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            result['og_tags'][prop] = tag.get('content', '').strip()
        
        if not result['og_tags']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add Open Graph meta tags',
                'implementation': 'Add og:title, og:description, og:image, og:url tags',
                'impact': 'Improve social media sharing appearance'
            })
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            result['twitter_cards'][name] = tag.get('content', '').strip()
        
        return result

    def analyze_page_speed_indicators(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze page speed optimization indicators"""
        result = {
            'external_scripts': 0,
            'external_stylesheets': 0,
            'inline_styles': 0,
            'images_without_optimization': 0,
            'minification_indicators': {},
            'cdn_usage': False,
            'compression_indicators': {},
            'issues': [],
            'opportunities': []
        }
        
        # Count external scripts
        external_scripts = soup.find_all('script', src=True)
        result['external_scripts'] = len(external_scripts)
        
        # Count external stylesheets
        external_css = soup.find_all('link', rel='stylesheet', href=True)
        result['external_stylesheets'] = len(external_css)
        
        # Count inline styles
        inline_styles = soup.find_all('style')
        result['inline_styles'] = len(inline_styles)
        
        # Check for minification indicators
        for script in external_scripts:
            src = script.get('src', '').lower()
            if '.min.js' in src:
                result['minification_indicators']['js'] = True
                break
        
        for css in external_css:
            href = css.get('href', '').lower()
            if '.min.css' in href:
                result['minification_indicators']['css'] = True
                break
        
        # Check for CDN usage
        for script in external_scripts:
            src = script.get('src', '').lower()
            if any(cdn in src for cdn in ['cdn.', 'ajax.googleapis.com', 'cdnjs.', 'unpkg.com']):
                result['cdn_usage'] = True
                break
        
        # Generate recommendations
        if result['external_scripts'] > 10:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Reduce number of external scripts',
                'implementation': 'Combine, minify, or lazy-load JavaScript files',
                'impact': 'Improve page load speed and Core Web Vitals'
            })
        
        if result['external_stylesheets'] > 5:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Reduce number of external stylesheets',
                'implementation': 'Combine and minify CSS files',
                'impact': 'Reduce render-blocking resources and improve load time'
            })
        
        if not result['minification_indicators']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Minify CSS and JavaScript files',
                'implementation': 'Use build tools to minify assets for production',
                'impact': 'Reduce file sizes and improve load speed'
            })
        
        if not result['cdn_usage']:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Consider using CDN for static assets',
                'implementation': 'Use CDN for JavaScript libraries and static files',
                'impact': 'Improve global load times and reduce server load'
            })
        
        return result

    def analyze_images_alt_text(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze images and alt text for SEO and accessibility"""
        result = {
            'total_images': 0,
            'images_with_alt': 0,
            'images_without_alt': 0,
            'empty_alt_tags': 0,
            'alt_text_percentage': 0,
            'lazy_loading': 0,
            'responsive_images': 0,
            'issues': [],
            'opportunities': []
        }
        
        images = soup.find_all('img')
        result['total_images'] = len(images)
        
        if result['total_images'] == 0:
            return result
        
        for img in images:
            alt_text = img.get('alt', '')
            
            if 'alt' in img.attrs:
                if alt_text.strip():
                    result['images_with_alt'] += 1
                else:
                    result['empty_alt_tags'] += 1
            else:
                result['images_without_alt'] += 1
            
            # Check for lazy loading
            if img.get('loading') == 'lazy' or 'lazy' in img.get('class', []):
                result['lazy_loading'] += 1
            
            # Check for responsive images
            if img.get('srcset') or img.get('sizes'):
                result['responsive_images'] += 1
        
        result['alt_text_percentage'] = (result['images_with_alt'] / result['total_images']) * 100
        
        # Generate recommendations
        if result['alt_text_percentage'] < self.seo_thresholds['alt_text_threshold']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add alt text to images',
                'implementation': f'Add descriptive alt text to {result["images_without_alt"] + result["empty_alt_tags"]} images',
                'impact': 'Improve accessibility and image SEO'
            })
        
        if result['lazy_loading'] < result['total_images'] * 0.5:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Implement lazy loading for images',
                'implementation': 'Add loading="lazy" attribute to below-fold images',
                'impact': 'Improve initial page load speed and Core Web Vitals'
            })
        
        if result['responsive_images'] < result['total_images'] * 0.3:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add responsive images',
                'implementation': 'Use srcset and sizes attributes for different screen sizes',
                'impact': 'Optimize images for mobile devices and improve load times'
            })
        
        return result

    def analyze_schema_markup(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze structured data and schema markup"""
        result = {
            'json_ld_schemas': [],
            'microdata': [],
            'rdfa': [],
            'schema_types': [],
            'issues': [],
            'opportunities': []
        }
        
        # Check for JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                schema_data = json.loads(script.string)
                result['json_ld_schemas'].append(schema_data)
                if '@type' in schema_data:
                    schema_type = schema_data['@type'].lower()
                    result['schema_types'].append(schema_type)
            except:
                pass
        
        # Check for Microdata
        microdata_elements = soup.find_all(attrs={'itemtype': True})
        for element in microdata_elements:
            itemtype = element.get('itemtype', '')
            result['microdata'].append(itemtype)
        
        # Check for RDFa
        rdfa_elements = soup.find_all(attrs={'typeof': True})
        for element in rdfa_elements:
            typeof = element.get('typeof', '')
            result['rdfa'].append(typeof)
        
        # Generate recommendations based on missing schema types
        if not result['json_ld_schemas'] and not result['microdata'] and not result['rdfa']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add structured data markup',
                'implementation': 'Implement JSON-LD schema for organization, local business, or relevant content type',
                'impact': 'Improve search result appearance with rich snippets'
            })
        
        # Check for specific schema types that might be missing
        page_text = soup.get_text().lower()
        if any(word in page_text for word in ['hours', 'phone', 'address']) and 'localbusiness' not in result['schema_types']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add LocalBusiness schema markup',
                'implementation': 'Implement LocalBusiness schema with address, phone, and hours',
                'impact': 'Improve local search visibility and Google My Business integration'
            })
        
        return result

    def analyze_local_seo(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze local SEO signals"""
        result = {
            'nap_consistency': {},
            'local_keywords': [],
            'location_pages': False,
            'google_maps_embed': False,
            'local_schema': False,
            'contact_info_visibility': {},
            'issues': [],
            'opportunities': []
        }
        
        page_text = soup.get_text().lower()
        
        # Check for NAP (Name, Address, Phone) information
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, soup.get_text())
        result['nap_consistency']['phone'] = len(phones) > 0
        
        # Check for address keywords
        address_indicators = ['street', 'avenue', 'road', 'suite', 'floor', 'building']
        result['nap_consistency']['address'] = any(indicator in page_text for indicator in address_indicators)
        
        # Check for local keywords
        for keyword in self.local_seo_keywords:
            if keyword in page_text:
                result['local_keywords'].append(keyword)
        
        # Check for Google Maps embed
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '').lower()
            if 'google.com/maps' in src or 'maps.google.com' in src:
                result['google_maps_embed'] = True
                break
        
        # Check for local business schema
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                schema_data = json.loads(script.string)
                if '@type' in schema_data and 'localbusiness' in schema_data['@type'].lower():
                    result['local_schema'] = True
                    break
            except:
                pass
        
        # Generate recommendations
        if not result['nap_consistency']['phone'] or not result['nap_consistency']['address']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add complete NAP information',
                'implementation': 'Display consistent Name, Address, Phone on all pages',
                'impact': 'Improve local search rankings and customer trust'
            })
        
        if not result['google_maps_embed']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add Google Maps embed',
                'implementation': 'Embed Google Maps showing business location',
                'impact': 'Improve user experience and local SEO signals'
            })
        
        if not result['local_schema']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add LocalBusiness schema markup',
                'implementation': 'Implement structured data for local business information',
                'impact': 'Enhance local search visibility and rich snippets'
            })
        
        return result

    def analyze_page_titles(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze page titles optimization"""
        result = {
            'title_present': False,
            'title_length': 0,
            'title_content': '',
            'h1_title_match': False,
            'brand_in_title': False,
            'issues': [],
            'opportunities': []
        }
        
        title_tag = soup.find('title')
        h1_tag = soup.find('h1')
        
        if title_tag:
            result['title_present'] = True
            result['title_content'] = title_tag.get_text().strip()
            result['title_length'] = len(result['title_content'])
            
            # Check if H1 and title are similar
            if h1_tag:
                h1_text = h1_tag.get_text().strip()
                if h1_text.lower() in result['title_content'].lower() or result['title_content'].lower() in h1_text.lower():
                    result['h1_title_match'] = True
        
        # Generate recommendations based on title analysis
        if not result['title_present']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add page title',
                'implementation': 'Add descriptive title tag to page head',
                'impact': 'Critical for search engine ranking'
            })
        elif result['title_length'] < 30:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Expand page title',
                'implementation': 'Make title more descriptive and keyword-rich',
                'impact': 'Improve search visibility and click-through rates'
            })
        elif result['title_length'] > 60:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Shorten page title',
                'implementation': 'Reduce title length to prevent truncation',
                'impact': 'Ensure full title displays in search results'
            })
        
        if not result['h1_title_match'] and h1_tag:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Align H1 and title tag',
                'implementation': 'Make H1 and title tag consistent for better SEO',
                'impact': 'Improve topical relevance and user experience'
            })
        
        return result

    def analyze_header_structure(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze header tag structure (H1-H6)"""
        result = {
            'header_counts': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
            'header_hierarchy': [],
            'missing_h1': False,
            'multiple_h1': False,
            'empty_headers': 0,
            'issues': [],
            'opportunities': []
        }
        
        # Count header tags
        for level in range(1, 7):
            headers = soup.find_all(f'h{level}')
            result['header_counts'][f'h{level}'] = len(headers)
            
            # Check for empty headers
            for header in headers:
                if not header.get_text().strip():
                    result['empty_headers'] += 1
                else:
                    result['header_hierarchy'].append({
                        'level': level,
                        'text': header.get_text().strip()[:50]  # Limit text length
                    })
        
        # Check H1 status
        if result['header_counts']['h1'] == 0:
            result['missing_h1'] = True
        elif result['header_counts']['h1'] > 1:
            result['multiple_h1'] = True
        
        # Generate recommendations
        if result['missing_h1']:
            result['opportunities'].append({
                'priority': 'high',
                'recommendation': 'Add H1 heading',
                'implementation': 'Add single, descriptive H1 tag to page',
                'impact': 'Improve page structure and SEO ranking'
            })
        
        if result['multiple_h1']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Use only one H1 per page',
                'implementation': 'Convert additional H1 tags to H2 or appropriate level',
                'impact': 'Improve semantic structure and SEO'
            })
        
        if result['empty_headers'] > 0:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Remove or populate empty header tags',
                'implementation': f'Add content to {result["empty_headers"]} empty header tags',
                'impact': 'Clean up HTML structure and improve accessibility'
            })
        
        if sum(result['header_counts'].values()) < 3:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Add more header tags for content structure',
                'implementation': 'Use H2-H6 tags to create clear content hierarchy',
                'impact': 'Improve content organization and user experience'
            })
        
        return result

    def analyze_url_structure(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze URL structure and SEO friendliness"""
        result = {
            'url_length': len(url),
            'has_parameters': False,
            'seo_friendly': True,
            'breadcrumbs': False,
            'internal_link_structure': {},
            'issues': [],
            'opportunities': []
        }
        
        parsed_url = urlparse(url)
        
        # Check for parameters
        if parsed_url.query:
            result['has_parameters'] = True
        
        # Check URL structure
        path = parsed_url.path.lower()
        if any(char in path for char in ['_', '%', '=', '&', '?']) and not parsed_url.query:
            result['seo_friendly'] = False
        
        # Check for breadcrumb navigation
        breadcrumb_selectors = [
            '[class*="breadcrumb"]', '[id*="breadcrumb"]',
            'nav[aria-label*="breadcrumb"]', '.breadcrumbs'
        ]
        
        for selector in breadcrumb_selectors:
            if soup.select(selector):
                result['breadcrumbs'] = True
                break
        
        # Analyze internal linking
        internal_links = soup.find_all('a', href=True)
        same_domain_links = 0
        external_links = 0
        
        for link in internal_links:
            href = link.get('href', '')
            if href.startswith('http'):
                if parsed_url.netloc in href:
                    same_domain_links += 1
                else:
                    external_links += 1
            elif href.startswith('/') or not href.startswith('http'):
                same_domain_links += 1
        
        result['internal_link_structure'] = {
            'internal_links': same_domain_links,
            'external_links': external_links
        }
        
        # Generate recommendations
        if result['url_length'] > 100:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Shorten URL length',
                'implementation': 'Use shorter, more concise URL paths',
                'impact': 'Improve user experience and shareability'
            })
        
        if not result['seo_friendly']:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Improve URL structure',
                'implementation': 'Use hyphens instead of underscores, avoid special characters',
                'impact': 'Better search engine crawling and user experience'
            })
        
        if not result['breadcrumbs'] and same_domain_links > 10:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Add breadcrumb navigation',
                'implementation': 'Implement breadcrumb navigation for better site structure',
                'impact': 'Improve user navigation and search engine understanding'
            })
        
        return result

    def analyze_internal_links(self, soup: BeautifulSoup, url: str) -> Dict:
        """Analyze internal linking structure"""
        result = {
            'total_links': 0,
            'internal_links': 0,
            'external_links': 0,
            'nofollow_links': 0,
            'anchor_text_analysis': {},
            'issues': [],
            'opportunities': []
        }
        
        parsed_url = urlparse(url)
        links = soup.find_all('a', href=True)
        result['total_links'] = len(links)
        
        anchor_texts = []
        
        for link in links:
            href = link.get('href', '')
            anchor_text = link.get_text().strip()
            rel = link.get('rel', [])
            
            if anchor_text:
                anchor_texts.append(anchor_text.lower())
            
            # Check if nofollow
            if 'nofollow' in rel:
                result['nofollow_links'] += 1
            
            # Categorize link
            if href.startswith('http'):
                if parsed_url.netloc in href:
                    result['internal_links'] += 1
                else:
                    result['external_links'] += 1
            elif href.startswith('/') or not href.startswith('http'):
                result['internal_links'] += 1
        
        # Analyze anchor text diversity
        unique_anchors = set(anchor_texts)
        result['anchor_text_analysis'] = {
            'total_anchor_texts': len(anchor_texts),
            'unique_anchor_texts': len(unique_anchors),
            'diversity_ratio': len(unique_anchors) / len(anchor_texts) if anchor_texts else 0
        }
        
        # Generate recommendations
        if result['internal_links'] < 5:
            result['opportunities'].append({
                'priority': 'medium',
                'recommendation': 'Add more internal links',
                'implementation': 'Link to relevant pages within your site',
                'impact': 'Improve site navigation and distribute page authority'
            })
        
        if result['anchor_text_analysis']['diversity_ratio'] < 0.5:
            result['opportunities'].append({
                'priority': 'low',
                'recommendation': 'Diversify anchor text',
                'implementation': 'Use varied, descriptive anchor text for links',
                'impact': 'Improve SEO and user experience'
            })
        
        return result

    def calculate_seo_score(self, seo_analysis: Dict) -> int:
        """Calculate SEO score based on analysis results"""
        score = 0
        max_score = 100
        
        # Title and meta tags (25 points)
        meta_tags = seo_analysis.get('meta_tags', {})
        if meta_tags.get('title'):
            score += 10
            title_len = meta_tags.get('title_length', 0)
            if 30 <= title_len <= 60:
                score += 5
        
        if meta_tags.get('description'):
            score += 5
            desc_len = meta_tags.get('description_length', 0)
            if 120 <= desc_len <= 160:
                score += 5
        
        # Header structure (15 points)
        headers = seo_analysis.get('header_structure', {})
        if headers.get('header_counts', {}).get('h1', 0) == 1:
            score += 10
        if sum(headers.get('header_counts', {}).values()) >= 3:
            score += 5
        
        # Images (15 points)
        images = seo_analysis.get('images', {})
        alt_percentage = images.get('alt_text_percentage', 0)
        if alt_percentage >= 80:
            score += 10
        elif alt_percentage >= 50:
            score += 5
        
        if images.get('lazy_loading', 0) > 0:
            score += 5
        
        # Schema markup (15 points)
        schema = seo_analysis.get('schema_markup', {})
        if schema.get('json_ld_schemas') or schema.get('microdata'):
            score += 15
        
        # Local SEO (10 points)
        local_seo = seo_analysis.get('local_seo', {})
        nap = local_seo.get('nap_consistency', {})
        if nap.get('phone') and nap.get('address'):
            score += 5
        if local_seo.get('local_schema'):
            score += 5
        
        # URL structure (10 points)
        url_struct = seo_analysis.get('url_structure', {})
        if url_struct.get('seo_friendly'):
            score += 5
        if url_struct.get('breadcrumbs'):
            score += 5
        
        # Page speed indicators (10 points)
        speed = seo_analysis.get('page_speed_indicators', {})
        if speed.get('minification_indicators'):
            score += 5
        if speed.get('cdn_usage'):
            score += 5
        
        return min(score, max_score)

    def calculate_automation_score(self, analysis: Dict) -> int:
        """Calculate overall automation score (0-100)"""
        score = 0
        max_score = 100
        
        # Scoring weights (total 100 points)
        weights = {
            'chatbot': 12,
            'lead_capture': 12,
            'email_signup': 8,
            'social_media': 8,
            'reviews': 12,
            'booking': 15,
            'mobile': 8,
            'contact': 5,
            'seo': 20  # SEO gets significant weight
        }
        
        # Calculate scores
        if analysis['chatbot_analysis']['has_chatbot']:
            score += weights['chatbot']
        
        if analysis['lead_capture_analysis']['has_lead_capture']:
            score += weights['lead_capture']
        
        if analysis['email_signup_analysis']['has_email_signup']:
            score += weights['email_signup']
        
        if len(analysis['social_media_analysis']['social_links']) >= 3:
            score += weights['social_media']
        
        if analysis['review_analysis']['has_reviews']:
            score += weights['reviews']
        
        if analysis['booking_analysis']['has_booking']:
            score += weights['booking']
        
        mobile_score = 0
        mobile_analysis = analysis['mobile_analysis']
        if mobile_analysis['has_viewport_meta']: mobile_score += 3
        if mobile_analysis['responsive_design']: mobile_score += 4
        if mobile_analysis['mobile_menu']: mobile_score += 3
        score += min(mobile_score, weights['mobile'])
        
        if len(analysis['contact_analysis']['contact_methods']) >= 3:
            score += weights['contact']
        
        # SEO scoring
        seo_analysis = analysis.get('seo_analysis', {})
        seo_score = seo_analysis.get('seo_score', 0)
        # Convert SEO score (0-100) to weighted score
        score += int((seo_score / 100) * weights['seo'])
        
        return min(score, max_score)

    def generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate prioritized automation recommendations"""
        all_recommendations = []
        
        # Collect all opportunities from different analyses
        for analysis_type, analysis_data in analysis.items():
            if isinstance(analysis_data, dict) and 'opportunities' in analysis_data:
                for opportunity in analysis_data['opportunities']:
                    opportunity['category'] = analysis_type.replace('_analysis', '')
                    all_recommendations.append(opportunity)
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return all_recommendations

    def analyze_website(self, url: str) -> Optional[AnalysisResult]:
        """Perform comprehensive website analysis"""
        print(f"Analyzing website: {url}")
        
        soup = self.fetch_website(url)
        if not soup:
            return None
        
        # Perform all analyses
        chatbot_analysis = self.analyze_chatbot(soup, url)
        lead_capture_analysis = self.analyze_lead_capture(soup, url)
        email_signup_analysis = self.analyze_email_signup(soup, url)
        social_media_analysis = self.analyze_social_media(soup, url)
        review_analysis = self.analyze_reviews(soup, url)
        booking_analysis = self.analyze_booking(soup, url)
        mobile_analysis = self.analyze_mobile(soup, url)
        contact_analysis = self.analyze_contact_methods(soup, url)
        seo_analysis = self.analyze_seo(soup, url)
        
        analysis_data = {
            'chatbot_analysis': chatbot_analysis,
            'lead_capture_analysis': lead_capture_analysis,
            'email_signup_analysis': email_signup_analysis,
            'social_media_analysis': social_media_analysis,
            'review_analysis': review_analysis,
            'booking_analysis': booking_analysis,
            'mobile_analysis': mobile_analysis,
            'contact_analysis': contact_analysis,
            'seo_analysis': seo_analysis
        }
        
        automation_score = self.calculate_automation_score(analysis_data)
        recommendations = self.generate_recommendations(analysis_data)
        
        return AnalysisResult(
            url=url,
            timestamp=datetime.now().isoformat(),
            automation_score=automation_score,
            recommendations=recommendations,
            **analysis_data
        )

    def generate_report(self, result: AnalysisResult, output_format: str = 'json') -> str:
        """Generate detailed analysis report"""
        if output_format == 'json':
            return json.dumps(asdict(result), indent=2)
        
        elif output_format == 'markdown':
            report = f"""# Website Automation Analysis Report

**URL:** {result.url}  
**Analysis Date:** {result.timestamp}  
**Automation Score:** {result.automation_score}/100

## Executive Summary
{'🟢 Excellent automation' if result.automation_score >= 80 else '🟡 Good automation' if result.automation_score >= 60 else '🟠 Moderate automation' if result.automation_score >= 40 else '🔴 Limited automation'}

## Analysis Results

### 🤖 Chatbot Analysis
- **Has Chatbot:** {'✅' if result.chatbot_analysis['has_chatbot'] else '❌'}
- **Type:** {result.chatbot_analysis.get('chatbot_type', 'N/A')}

### 📝 Lead Capture Analysis
- **Has Lead Capture:** {'✅' if result.lead_capture_analysis['has_lead_capture'] else '❌'}
- **Forms Count:** {result.lead_capture_analysis['forms_count']}
- **Form Types:** {', '.join(result.lead_capture_analysis['form_types']) if result.lead_capture_analysis['form_types'] else 'None'}

### 📧 Email Signup Analysis
- **Has Email Signup:** {'✅' if result.email_signup_analysis['has_email_signup'] else '❌'}
- **Service:** {result.email_signup_analysis.get('email_service', 'N/A')}

### 📱 Social Media Analysis
- **Social Links:** {len(result.social_media_analysis['social_links'])}
- **Platforms:** {', '.join(result.social_media_analysis['social_links'].keys()) if result.social_media_analysis['social_links'] else 'None'}
- **Sharing Buttons:** {'✅' if result.social_media_analysis['sharing_buttons'] else '❌'}

### ⭐ Review Analysis
- **Has Reviews:** {'✅' if result.review_analysis['has_reviews'] else '❌'}
- **Sources:** {', '.join(result.review_analysis['review_sources']) if result.review_analysis['review_sources'] else 'None'}

### 📅 Booking Analysis
- **Has Booking:** {'✅' if result.booking_analysis['has_booking'] else '❌'}
- **System:** {result.booking_analysis.get('booking_system', 'N/A')}

### 📱 Mobile Analysis
- **Viewport Meta:** {'✅' if result.mobile_analysis['has_viewport_meta'] else '❌'}
- **Responsive Design:** {'✅' if result.mobile_analysis['responsive_design'] else '❌'}
- **Mobile Menu:** {'✅' if result.mobile_analysis['mobile_menu'] else '❌'}

### 📞 Contact Analysis
- **Contact Methods:** {len(result.contact_analysis['contact_methods'])}
- **Available Methods:** {', '.join(result.contact_analysis['contact_methods']) if result.contact_analysis['contact_methods'] else 'None'}

### 🔍 SEO Analysis
**SEO Score:** {result.seo_analysis['seo_score']}/100

#### Meta Tags
- **Title:** {'✅' if result.seo_analysis['meta_tags']['title'] else '❌'} ({result.seo_analysis['meta_tags']['title_length']} chars)
- **Description:** {'✅' if result.seo_analysis['meta_tags']['description'] else '❌'} ({result.seo_analysis['meta_tags']['description_length']} chars)
- **Canonical URL:** {'✅' if result.seo_analysis['meta_tags']['canonical'] else '❌'}
- **Open Graph Tags:** {len(result.seo_analysis['meta_tags']['og_tags'])} tags

#### Header Structure
- **H1 Tags:** {result.seo_analysis['header_structure']['header_counts']['h1']} {'✅' if result.seo_analysis['header_structure']['header_counts']['h1'] == 1 else '⚠️'}
- **Total Headers:** {sum(result.seo_analysis['header_structure']['header_counts'].values())}
- **Multiple H1:** {'⚠️ Yes' if result.seo_analysis['header_structure']['multiple_h1'] else '✅ No'}

#### Images & Performance
- **Images with Alt Text:** {result.seo_analysis['images']['alt_text_percentage']:.1f}%
- **Total Images:** {result.seo_analysis['images']['total_images']}
- **Lazy Loading:** {result.seo_analysis['images']['lazy_loading']} images
- **External Scripts:** {result.seo_analysis['page_speed_indicators']['external_scripts']}
- **CDN Usage:** {'✅' if result.seo_analysis['page_speed_indicators']['cdn_usage'] else '❌'}

#### Schema & Local SEO
- **Structured Data:** {'✅' if result.seo_analysis['schema_markup']['json_ld_schemas'] or result.seo_analysis['schema_markup']['microdata'] else '❌'}
- **Schema Types:** {', '.join(result.seo_analysis['schema_markup']['schema_types']) if result.seo_analysis['schema_markup']['schema_types'] else 'None'}
- **NAP Consistency:** {'✅' if result.seo_analysis['local_seo']['nap_consistency']['phone'] and result.seo_analysis['local_seo']['nap_consistency']['address'] else '❌'}
- **Google Maps:** {'✅' if result.seo_analysis['local_seo']['google_maps_embed'] else '❌'}
- **Local Keywords:** {len(result.seo_analysis['local_seo']['local_keywords'])} found

#### Technical SEO
- **URL Structure:** {'✅ SEO Friendly' if result.seo_analysis['url_structure']['seo_friendly'] else '⚠️ Needs Improvement'}
- **Breadcrumbs:** {'✅' if result.seo_analysis['url_structure']['breadcrumbs'] else '❌'}
- **Internal Links:** {result.seo_analysis['internal_links']['internal_links']}
- **External Links:** {result.seo_analysis['internal_links']['external_links']}

## 🚀 Automation Recommendations

"""
            for i, rec in enumerate(result.recommendations, 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                report += f"""### {i}. {rec['recommendation']} {priority_emoji.get(rec['priority'], '⚪')}
**Priority:** {rec['priority'].title()}  
**Category:** {rec['category'].title()}  
**Implementation:** {rec['implementation']}  
**Expected Impact:** {rec['impact']}

"""
            
            return report
        
        return "Unsupported format"


def main():
    parser = argparse.ArgumentParser(description='Website Automation Opportunity Analyzer')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    analyzer = WebsiteAnalyzer()
    result = analyzer.analyze_website(args.url)
    
    if not result:
        print("Failed to analyze website. Please check the URL and try again.")
        return
    
    report = analyzer.generate_report(result, args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        # Remove problematic Unicode characters for Windows terminal
        import sys
        if sys.platform == 'win32':
            # Replace Unicode emojis with ASCII equivalents
            report = report.replace('🟢', '[GOOD]')
            report = report.replace('🟡', '[OK]')  
            report = report.replace('🟠', '[FAIR]')
            report = report.replace('🔴', '[NEEDS WORK]')
            report = report.replace('✅', '[YES]')
            report = report.replace('❌', '[NO]')
            report = report.replace('⚠️', '[WARNING]')
            report = report.replace('🤖', '[CHATBOT]')
            report = report.replace('📝', '[FORMS]')
            report = report.replace('📧', '[EMAIL]')
            report = report.replace('📱', '[SOCIAL/MOBILE]')
            report = report.replace('⭐', '[REVIEWS]')
            report = report.replace('📅', '[BOOKING]')
            report = report.replace('📞', '[CONTACT]')
            report = report.replace('🔍', '[SEO]')
            report = report.replace('🚀', '[RECOMMENDATIONS]')
            report = report.replace('⚪', '[NORMAL]')
        print(report)


if __name__ == '__main__':
    main()