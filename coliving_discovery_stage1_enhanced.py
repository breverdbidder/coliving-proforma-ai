"""
Stage 1 Discovery - Enhanced with Zillow/Redfin Free GitHub Integrations
Co-Living Proforma AI - Property Data Acquisition Layer

Integrates:
- scrapehero/zillow_real_estate (Free, LXML-based)
- johnbalvin/pyzill (Free, Internal API access)
- reteps/redfin (Free, Stingray API wrapper)
- ryansherby/RedfinScraper (Free, Scalable multi-processing)

Author: BidDeed.AI
Version: 2.0.0 (Enhanced Discovery)
"""

from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import operator
import json
import asyncio
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== FREE GITHUB INTEGRATIONS ====================

# Integration 1: johnbalvin/pyzill (Primary - Zillow Internal API)
try:
    import pyzill
    PYZILL_AVAILABLE = True
    logger.info("✅ pyzill library loaded (Zillow Internal API)")
except ImportError:
    PYZILL_AVAILABLE = False
    logger.warning("⚠️ pyzill not available - install with: pip install pyzill")

# Integration 2: reteps/redfin (Primary - Redfin Stingray API)
try:
    from redfin import Redfin
    REDFIN_AVAILABLE = True
    logger.info("✅ redfin library loaded (Stingray API)")
except ImportError:
    REDFIN_AVAILABLE = False
    logger.warning("⚠️ redfin not available - install with: pip install redfin")

# Integration 3: Fallback scrapers
import requests
from bs4 import BeautifulSoup
from lxml import html
import re
from time import sleep
from random import uniform

# ==================== PYDANTIC DATA MODELS ====================

class PropertyAddress(BaseModel):
    """Validated property address"""
    street: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    zip_code: str = Field(pattern=r"^\d{5}(-\d{4})?$")
    full_address: str
    
    @validator('state')
    def uppercase_state(cls, v):
        return v.upper()

class PropertyDetails(BaseModel):
    """Complete property data from multiple sources"""
    # Identifiers
    property_id: Optional[str] = None
    zpid: Optional[str] = None  # Zillow Property ID
    redfin_property_id: Optional[str] = None
    
    # Address
    address: PropertyAddress
    
    # Basic Details
    bedrooms: Optional[int] = Field(None, ge=0, le=50)
    bathrooms: Optional[float] = Field(None, ge=0, le=30)
    square_feet: Optional[int] = Field(None, ge=100)
    lot_size_sqft: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2030)
    property_type: Optional[str] = None
    
    # Pricing
    list_price: Optional[Decimal] = Field(None, ge=0)
    zestimate: Optional[Decimal] = Field(None, ge=0)
    rent_zestimate: Optional[Decimal] = Field(None, ge=0)
    redfin_estimate: Optional[Decimal] = Field(None, ge=0)
    price_per_sqft: Optional[Decimal] = Field(None, ge=0)
    
    # Price History
    price_history: Optional[List[Dict]] = None
    last_sold_price: Optional[Decimal] = None
    last_sold_date: Optional[str] = None
    
    # Additional Info
    description: Optional[str] = None
    photos: Optional[List[str]] = []
    hoa_fee: Optional[Decimal] = Field(None, ge=0)
    tax_assessed_value: Optional[Decimal] = None
    annual_tax: Optional[Decimal] = None
    days_on_market: Optional[int] = None
    
    # Neighborhood Data
    walk_score: Optional[int] = Field(None, ge=0, le=100)
    transit_score: Optional[int] = Field(None, ge=0, le=100)
    bike_score: Optional[int] = Field(None, ge=0, le=100)
    
    # Schools
    schools: Optional[List[Dict]] = []
    
    # Data Source Metadata
    data_source: str
    data_sources_used: List[str] = []
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class ComparableProperty(BaseModel):
    """Comparable property (comp)"""
    address: str
    beds: Optional[int] = None
    baths: Optional[float] = None
    sqft: Optional[int] = None
    price: Optional[Decimal] = None
    price_per_sqft: Optional[Decimal] = None
    sold_date: Optional[str] = None
    distance_miles: Optional[float] = None

# ==================== ZILLOW DATA FETCHERS ====================

class ZillowPyzillFetcher:
    """
    Zillow data fetcher using pyzill library (johnbalvin/pyzill)
    Accesses Zillow's internal API for comprehensive property data
    """
    
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.enabled = PYZILL_AVAILABLE
    
    async def fetch_property(self, address: str, city: str, state: str, zip_code: str) -> Optional[Dict]:
        """Fetch property data from Zillow internal API"""
        if not self.enabled:
            logger.warning("pyzill not available")
            return None
        
        try:
            # Search for property
            search_value = f"{address}, {city}, {state} {zip_code}"
            
            # Use for_sale endpoint to get current listings
            results = pyzill.for_sale(
                pagination=1,
                search_value=search_value,
                min_beds=None,
                max_beds=None,
                min_bathrooms=None,
                max_bathrooms=None,
                min_price=None,
                max_price=None,
                proxy_url=self.proxy_url
            )
            
            if not results or len(results) == 0:
                # Try sold properties
                results = pyzill.sold(
                    pagination=1,
                    search_value=search_value,
                    min_beds=None,
                    max_beds=None,
                    min_bathrooms=None,
                    max_bathrooms=None,
                    min_price=None,
                    max_price=None,
                    proxy_url=self.proxy_url
                )
            
            if results and len(results) > 0:
                # Return first result (most relevant)
                property_data = results[0]
                
                return {
                    "zpid": property_data.get("zpid"),
                    "address": property_data.get("address"),
                    "bedrooms": property_data.get("bedrooms"),
                    "bathrooms": property_data.get("bathrooms"),
                    "square_feet": property_data.get("livingArea"),
                    "lot_size_sqft": property_data.get("lotAreaValue"),
                    "year_built": property_data.get("yearBuilt"),
                    "property_type": property_data.get("homeType"),
                    "list_price": property_data.get("price"),
                    "zestimate": property_data.get("zestimate"),
                    "rent_zestimate": property_data.get("rentZestimate"),
                    "price_per_sqft": property_data.get("pricePerSqft"),
                    "description": property_data.get("description"),
                    "photos": property_data.get("imgSrc", []),
                    "latitude": property_data.get("latitude"),
                    "longitude": property_data.get("longitude"),
                    "data_source": "zillow_pyzill"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Zillow pyzill fetch error: {e}")
            return None
    
    async def fetch_comparables(self, latitude: float, longitude: float, radius_miles: float = 0.5) -> List[Dict]:
        """Fetch comparable properties within radius"""
        if not self.enabled:
            return []
        
        try:
            # Calculate bounding box
            # 1 mile ≈ 0.0145 degrees latitude, 0.0145 degrees longitude (approximate)
            lat_delta = radius_miles * 0.0145
            lon_delta = radius_miles * 0.0145
            
            ne_lat = latitude + lat_delta
            ne_long = longitude + lon_delta
            sw_lat = latitude - lat_delta
            sw_long = longitude - lon_delta
            
            # Fetch sold properties in area
            results = pyzill.sold(
                pagination=1,
                search_value="",
                min_beds=None,
                max_beds=None,
                min_bathrooms=None,
                max_bathrooms=None,
                min_price=None,
                max_price=None,
                ne_lat=ne_lat,
                ne_long=ne_long,
                sw_lat=sw_lat,
                sw_long=sw_long,
                zoom_value=15,
                proxy_url=self.proxy_url
            )
            
            return results[:10] if results else []  # Return top 10 comps
            
        except Exception as e:
            logger.error(f"Zillow comps fetch error: {e}")
            return []

class ZillowScraperHeroFetcher:
    """
    Zillow scraper using scrapehero/zillow_real_estate methodology
    LXML-based scraper for Zillow search results
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def fetch_by_zipcode(self, zip_code: str) -> List[Dict]:
        """Scrape Zillow search results by zip code"""
        try:
            url = f"https://www.zillow.com/homes/{zip_code}_rb/"
            
            # Add delay to avoid rate limiting
            await asyncio.sleep(uniform(2, 4))
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            parser = html.fromstring(response.text)
            
            # Extract property cards
            search_results = parser.xpath('//div[@id="search-results"]//article')
            
            properties = []
            for result in search_results[:20]:  # Limit to 20 results
                try:
                    address_raw = result.xpath('.//address/text()')
                    price_raw = result.xpath('.//span[@data-test="property-card-price"]/text()')
                    link_raw = result.xpath('.//a[@data-test="property-card-link"]/@href')
                    
                    property_data = {
                        "address": address_raw[0] if address_raw else None,
                        "price": price_raw[0] if price_raw else None,
                        "link": f"https://www.zillow.com{link_raw[0]}" if link_raw else None,
                        "data_source": "zillow_scrapehero"
                    }
                    
                    if property_data["address"]:
                        properties.append(property_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing property card: {e}")
                    continue
            
            return properties
            
        except Exception as e:
            logger.error(f"Zillow ScraperHero fetch error: {e}")
            return []

# ==================== REDFIN DATA FETCHERS ====================

class RedfinRetepsFetcher:
    """
    Redfin data fetcher using reteps/redfin library
    Accesses Redfin's Stingray API for comprehensive property data
    """
    
    def __init__(self):
        self.client = Redfin() if REDFIN_AVAILABLE else None
        self.enabled = REDFIN_AVAILABLE
    
    async def fetch_property(self, address: str) -> Optional[Dict]:
        """Fetch property data from Redfin Stingray API"""
        if not self.enabled:
            logger.warning("redfin not available")
            return None
        
        try:
            # Add delay to avoid rate limiting
            await asyncio.sleep(uniform(2, 4))
            
            # Step 1: Search for property
            response = self.client.search(address)
            
            if not response or 'payload' not in response:
                return None
            
            # Get URL from exact match
            exact_match = response['payload'].get('exactMatch')
            if not exact_match:
                return None
            
            url = exact_match.get('url')
            if not url:
                return None
            
            # Step 2: Get initial info
            initial_info = self.client.initial_info(url)
            if not initial_info or 'payload' not in initial_info:
                return None
            
            payload = initial_info['payload']
            property_id = payload.get('propertyId')
            listing_id = payload.get('listingId')
            
            # Step 3: Get detailed property data
            details = self.client.below_the_fold(property_id)
            if not details or 'payload' not in details:
                return None
            
            property_data = details['payload']
            
            # Extract relevant fields
            public_records = property_data.get('publicRecordsInfo', {})
            basic_info = public_records.get('basicInfo', {})
            
            return {
                "redfin_property_id": property_id,
                "listing_id": listing_id,
                "address": payload.get('address'),
                "bedrooms": basic_info.get('beds'),
                "bathrooms": basic_info.get('baths'),
                "square_feet": basic_info.get('sqFt', {}).get('value'),
                "lot_size_sqft": basic_info.get('lotSize', {}).get('value'),
                "year_built": basic_info.get('yearBuilt'),
                "property_type": basic_info.get('propertyType'),
                "list_price": payload.get('listPrice'),
                "redfin_estimate": property_data.get('avm', {}).get('value'),
                "price_per_sqft": payload.get('pricePerSqFt'),
                "description": property_data.get('listingRemarks'),
                "photos": [p.get('url') for p in property_data.get('mediaBrowserInfo', {}).get('photos', [])],
                "hoa_fee": public_records.get('hoaInfo', {}).get('hoaFee'),
                "tax_assessed_value": public_records.get('taxInfo', {}).get('taxableLandValue'),
                "annual_tax": public_records.get('taxInfo', {}).get('taxAnnualAmount'),
                "schools": property_data.get('schoolsAndDistrictsInfo', {}).get('servingThisHomeSchools', []),
                "data_source": "redfin_reteps"
            }
            
        except Exception as e:
            logger.error(f"Redfin reteps fetch error: {e}")
            return None
    
    async def fetch_comparables(self, property_id: str) -> List[Dict]:
        """Fetch comparable properties from Redfin"""
        if not self.enabled:
            return []
        
        try:
            await asyncio.sleep(uniform(2, 4))
            
            # Get comp data from Redfin
            comps = self.client.nearby_homes(property_id)
            
            if not comps or 'payload' not in comps:
                return []
            
            homes = comps['payload'].get('homes', [])
            
            return [{
                "address": home.get('address'),
                "beds": home.get('beds'),
                "baths": home.get('baths'),
                "sqft": home.get('sqFt'),
                "price": home.get('price'),
                "price_per_sqft": home.get('pricePerSqFt'),
                "distance_miles": home.get('distanceFromCoordinate')
            } for home in homes[:10]]  # Top 10 comps
            
        except Exception as e:
            logger.error(f"Redfin comps fetch error: {e}")
            return []

class RedfinCSVFetcher:
    """
    Redfin bulk data fetcher using GIS-CSV endpoint
    Based on ryansherby/RedfinScraper methodology
    """
    
    def __init__(self):
        self.base_url = "https://www.redfin.com/stingray/api/gis-csv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_by_zipcode(self, zip_code: str, status: int = 9) -> List[Dict]:
        """
        Fetch properties by zip code from Redfin CSV endpoint
        
        Args:
            zip_code: 5-digit zip code
            status: 9 = For Sale, 1 = Sold
        """
        try:
            import pandas as pd
            import io
            
            await asyncio.sleep(uniform(2, 4))
            
            # Find region ID for zip code (simplified - would need lookup table)
            params = {
                'al': 1,
                'num_homes': 350,  # Max per request
                'region_type': 2,  # Zip code
                'status': status,
                'v': 8
            }
            
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            
            # Convert to list of dicts
            properties = df.to_dict('records')
            
            return [{
                "property_id": p.get('PROPERTY ID'),
                "address": f"{p.get('ADDRESS')}, {p.get('CITY')}, {p.get('STATE OR PROVINCE')} {p.get('ZIP OR POSTAL CODE')}",
                "bedrooms": p.get('BEDS'),
                "bathrooms": p.get('BATHS'),
                "square_feet": p.get('SQUARE FEET'),
                "lot_size_sqft": p.get('LOT SIZE'),
                "year_built": p.get('YEAR BUILT'),
                "list_price": p.get('PRICE'),
                "price_per_sqft": p.get('$/SQUARE FEET'),
                "hoa_fee": p.get('HOA/MONTH'),
                "data_source": "redfin_csv"
            } for p in properties]
            
        except Exception as e:
            logger.error(f"Redfin CSV fetch error: {e}")
            return []

# ==================== UNIFIED PROPERTY FETCHER ====================

class UnifiedPropertyFetcher:
    """
    Unified property fetcher with multi-source fallback
    Combines all free GitHub integrations
    """
    
    def __init__(self):
        # Initialize all fetchers
        self.zillow_pyzill = ZillowPyzillFetcher()
        self.zillow_scraper = ZillowScraperHeroFetcher()
        self.redfin_reteps = RedfinRetepsFetcher()
        self.redfin_csv = RedfinCSVFetcher()
        
        logger.info("✅ Unified Property Fetcher initialized")
        logger.info(f"   - Zillow pyzill: {'✅' if self.zillow_pyzill.enabled else '❌'}")
        logger.info(f"   - Redfin reteps: {'✅' if self.redfin_reteps.enabled else '❌'}")
    
    async def fetch_property(self, address: str, city: str, state: str, zip_code: str) -> Optional[PropertyDetails]:
        """
        Fetch property data with fallback chain:
        1. Zillow pyzill (most comprehensive)
        2. Redfin reteps (good coverage)
        3. Zillow scraper (basic data)
        4. Redfin CSV (bulk data)
        """
        full_address = f"{address}, {city}, {state} {zip_code}"
        data_sources_used = []
        merged_data = {}
        
        # Try Zillow pyzill first
        if self.zillow_pyzill.enabled:
            logger.info("🔍 Attempting Zillow pyzill...")
            zillow_data = await self.zillow_pyzill.fetch_property(address, city, state, zip_code)
            if zillow_data:
                merged_data.update(zillow_data)
                data_sources_used.append("zillow_pyzill")
                logger.info("✅ Zillow pyzill data retrieved")
        
        # Try Redfin reteps second
        if self.redfin_reteps.enabled:
            logger.info("🔍 Attempting Redfin reteps...")
            redfin_data = await self.redfin_reteps.fetch_property(full_address)
            if redfin_data:
                # Merge with existing data (don't overwrite)
                for key, value in redfin_data.items():
                    if key not in merged_data or merged_data[key] is None:
                        merged_data[key] = value
                data_sources_used.append("redfin_reteps")
                logger.info("✅ Redfin reteps data retrieved")
        
        # If no data yet, try scrapers
        if not merged_data:
            logger.info("🔍 Attempting fallback scrapers...")
            zillow_search = await self.zillow_scraper.fetch_by_zipcode(zip_code)
            if zillow_search:
                data_sources_used.append("zillow_scraper")
                # Basic data extraction
                merged_data = {"data_source": "zillow_scraper"}
        
        if not merged_data:
            logger.warning("❌ No property data found from any source")
            return None
        
        # Build PropertyDetails object
        try:
            property_address = PropertyAddress(
                street=address,
                city=city,
                state=state,
                zip_code=zip_code,
                full_address=full_address
            )
            
            property_details = PropertyDetails(
                address=property_address,
                **merged_data,
                data_sources_used=data_sources_used,
                confidence_score=len(data_sources_used) * 0.3  # More sources = higher confidence
            )
            
            logger.info(f"✅ Property data compiled from {len(data_sources_used)} sources")
            return property_details
            
        except Exception as e:
            logger.error(f"Error building PropertyDetails: {e}")
            return None
    
    async def fetch_comparables(self, property_details: PropertyDetails) -> List[ComparableProperty]:
        """Fetch comparable properties from all sources"""
        comps = []
        
        # Try Zillow comps if we have coordinates
        if hasattr(property_details, 'latitude') and hasattr(property_details, 'longitude'):
            if property_details.latitude and property_details.longitude:
                zillow_comps = await self.zillow_pyzill.fetch_comparables(
                    property_details.latitude,
                    property_details.longitude
                )
                comps.extend(zillow_comps)
        
        # Try Redfin comps if we have property ID
        if property_details.redfin_property_id:
            redfin_comps = await self.redfin_reteps.fetch_comparables(
                property_details.redfin_property_id
            )
            comps.extend(redfin_comps)
        
        return comps[:10]  # Return top 10 comps

# ==================== LANGGRAPH STAGE 1 DISCOVERY (ENHANCED) ====================

class CoLivingDiscoveryState(TypedDict):
    """Enhanced State for Stage 1 Discovery"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    property_address: str
    property_city: str
    property_state: str
    property_zip: str
    
    # Enhanced outputs
    property_details: Optional[PropertyDetails]
    comparable_properties: Optional[List[ComparableProperty]]
    market_data: Optional[Dict]
    
    # Metadata
    api_errors: List[str]
    data_sources_used: List[str]
    discovery_complete: bool

async def stage_01_discovery_enhanced(state: CoLivingDiscoveryState) -> CoLivingDiscoveryState:
    """
    Stage 1 Discovery - Enhanced with Free GitHub Integrations
    
    Fetches comprehensive property data from:
    - Zillow (via pyzill)
    - Redfin (via reteps/redfin)
    - Multiple fallback scrapers
    """
    logger.info("🚀 Stage 1 Discovery - Starting enhanced property fetch...")
    
    # Initialize unified fetcher
    fetcher = UnifiedPropertyFetcher()
    
    # Fetch property data
    property_details = await fetcher.fetch_property(
        address=state["property_address"],
        city=state["property_city"],
        state=state["property_state"],
        zip_code=state["property_zip"]
    )
    
    # Fetch comparables if we have property data
    comparables = []
    if property_details:
        comparables = await fetcher.fetch_comparables(property_details)
    
    # Update state
    state["property_details"] = property_details
    state["comparable_properties"] = comparables
    state["data_sources_used"] = property_details.data_sources_used if property_details else []
    state["discovery_complete"] = property_details is not None
    
    logger.info(f"✅ Stage 1 Discovery complete - Found {len(comparables)} comps")
    
    return state

# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    async def test_discovery():
        """Test the enhanced discovery stage"""
        
        # Test state
        test_state = {
            "messages": [],
            "user_query": "Analyze 20-unit property",
            "property_address": "123 Main St",
            "property_city": "Austin",
            "property_state": "TX",
            "property_zip": "78701",
            "property_details": None,
            "comparable_properties": None,
            "market_data": None,
            "api_errors": [],
            "data_sources_used": [],
            "discovery_complete": False
        }
        
        # Run discovery
        result = await stage_01_discovery_enhanced(test_state)
        
        # Print results
        print("\n" + "="*80)
        print("STAGE 1 DISCOVERY RESULTS")
        print("="*80)
        
        if result["property_details"]:
            pd = result["property_details"]
            print(f"\n📍 Address: {pd.address.full_address}")
            print(f"🏠 Bedrooms: {pd.bedrooms}")
            print(f"🛁 Bathrooms: {pd.bathrooms}")
            print(f"📐 Square Feet: {pd.square_feet:,}" if pd.square_feet else "📐 Square Feet: N/A")
            print(f"💰 List Price: ${pd.list_price:,}" if pd.list_price else "💰 List Price: N/A")
            print(f"💵 Zestimate: ${pd.zestimate:,}" if pd.zestimate else "💵 Zestimate: N/A")
            print(f"🏘️ Rent Zestimate: ${pd.rent_zestimate:,}/mo" if pd.rent_zestimate else "🏘️ Rent Zestimate: N/A")
            print(f"\n📊 Data Sources: {', '.join(pd.data_sources_used)}")
            print(f"🎯 Confidence: {pd.confidence_score:.1%}")
        else:
            print("\n❌ No property data found")
        
        print(f"\n🔍 Comparables Found: {len(result['comparable_properties'])}")
        
        print("\n" + "="*80)
    
    # Run test
    asyncio.run(test_discovery())
