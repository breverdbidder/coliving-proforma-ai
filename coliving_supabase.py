"""
Supabase Integration for Co-Living Proforma AI
Handles database operations and state persistence

Author: BidDeed.AI
Version: 1.0.0
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoLivingSupabaseClient:
    """
    Supabase client for Co-Living Proforma AI
    Handles all database operations for properties, analyses, reports, and conversations
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase client
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
        """
        self.url = supabase_url or os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
        self.key = supabase_key or os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable required")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info(f"✅ Supabase client initialized: {self.url}")
    
    # ==================== PROPERTY OPERATIONS ====================
    
    def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new co-living property record
        
        Args:
            property_data: Property information and assumptions
            
        Returns:
            Created property record with ID
        """
        try:
            record = {
                "property_name": property_data.get("property_name"),
                "property_location": property_data.get("property_location", "Brevard County, FL"),
                "total_units": property_data.get("total_units"),
                "total_bedrooms": property_data.get("total_bedrooms"),
                "studio_units": property_data.get("unit_mix", {}).get("studio", 0),
                "one_br_units": property_data.get("unit_mix", {}).get("1br", 0),
                "two_br_units": property_data.get("unit_mix", {}).get("2br", 0),
                "assumptions": json.dumps(property_data.get("assumptions", {})),
                "user_id": property_data.get("user_id", "anonymous"),
                "session_id": property_data.get("session_id", str(uuid.uuid4())),
                "status": "draft"
            }
            
            result = self.client.table("coliving_properties").insert(record).execute()
            
            logger.info(f"✅ Property created: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error creating property: {e}")
            raise
    
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a property by ID
        
        Args:
            property_id: UUID of property
            
        Returns:
            Property record or None
        """
        try:
            result = self.client.table("coliving_properties").select("*").eq("id", property_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving property: {e}")
            return None
    
    def list_properties(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List properties, optionally filtered by user
        
        Args:
            user_id: Optional user ID filter
            limit: Maximum number of records
            
        Returns:
            List of property records
        """
        try:
            query = self.client.table("coliving_properties").select("*").order("created_at", desc=True).limit(limit)
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error listing properties: {e}")
            return []
    
    def update_property(self, property_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a property record
        
        Args:
            property_id: UUID of property
            updates: Fields to update
            
        Returns:
            Updated property record
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table("coliving_properties").update(updates).eq("id", property_id).execute()
            
            logger.info(f"✅ Property updated: {property_id}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error updating property: {e}")
            raise
    
    # ==================== ANALYSIS OPERATIONS ====================
    
    def save_analysis(self, property_id: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save analysis results to database
        
        Args:
            property_id: UUID of property
            analysis_results: Complete analysis from LangGraph orchestrator
            
        Returns:
            Created analysis record
        """
        try:
            # Extract key metrics for easy querying
            cash_flow = analysis_results.get("cash_flow", {})
            returns = analysis_results.get("returns_metrics", {})
            
            record = {
                "property_id": property_id,
                "analysis_type": analysis_results.get("property_data", {}).get("intent", "full_analysis"),
                "pipeline_version": "v1.0.0",
                "revenue_projections": json.dumps(analysis_results.get("revenue_projections", {})),
                "expense_analysis": json.dumps(analysis_results.get("expense_analysis", {})),
                "cash_flow": json.dumps(cash_flow),
                "returns_metrics": json.dumps(returns),
                "sensitivity_analysis": json.dumps(analysis_results.get("sensitivity_analysis", {})),
                "risk_assessment": json.dumps(analysis_results.get("risk_assessment", {})),
                "noi": cash_flow.get("noi", 0),
                "cap_rate": returns.get("cap_rate", 0),
                "cash_on_cash_return": returns.get("cash_on_cash_return", 0),
                "dscr": cash_flow.get("dscr", 0),
                "recommendations": analysis_results.get("recommendations", []),
                "investment_decision": self._determine_investment_decision(returns, cash_flow),
                "stage_completed": analysis_results.get("analysis_stage", "complete")
            }
            
            result = self.client.table("coliving_analyses").insert(record).execute()
            
            logger.info(f"✅ Analysis saved: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis: {e}")
            raise
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an analysis by ID
        
        Args:
            analysis_id: UUID of analysis
            
        Returns:
            Analysis record or None
        """
        try:
            result = self.client.table("coliving_analyses").select("*").eq("id", analysis_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving analysis: {e}")
            return None
    
    def list_analyses(self, property_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List analyses, optionally filtered by property
        
        Args:
            property_id: Optional property ID filter
            limit: Maximum number of records
            
        Returns:
            List of analysis records
        """
        try:
            query = self.client.table("coliving_analyses").select("*").order("created_at", desc=True).limit(limit)
            
            if property_id:
                query = query.eq("property_id", property_id)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error listing analyses: {e}")
            return []
    
    def _determine_investment_decision(self, returns: Dict, cash_flow: Dict) -> str:
        """Determine investment recommendation based on metrics"""
        cap_rate = returns.get("cap_rate", 0)
        dscr = cash_flow.get("dscr", 0)
        cash_on_cash = returns.get("cash_on_cash_return", 0)
        
        # Decision logic
        if cap_rate >= 7.0 and dscr >= 1.3 and cash_on_cash >= 8.0:
            return "BUY"
        elif cap_rate >= 6.0 and dscr >= 1.25 and cash_on_cash >= 6.0:
            return "FURTHER_ANALYSIS"
        else:
            return "PASS"
    
    # ==================== REPORT OPERATIONS ====================
    
    def save_report(self, analysis_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save generated report metadata
        
        Args:
            analysis_id: UUID of analysis
            report_data: Report information (URLs, dashboard data, etc.)
            
        Returns:
            Created report record
        """
        try:
            record = {
                "analysis_id": analysis_id,
                "excel_url": report_data.get("excel_url"),
                "pdf_url": report_data.get("pdf_url"),
                "dashboard_data": json.dumps(report_data.get("dashboard_data", {})),
                "report_type": report_data.get("report_type", "full_proforma"),
                "file_size_bytes": report_data.get("file_size_bytes"),
                "storage_bucket": "coliving-reports",
                "storage_path": report_data.get("storage_path")
            }
            
            result = self.client.table("coliving_reports").insert(record).execute()
            
            logger.info(f"✅ Report saved: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")
            raise
    
    def get_reports(self, analysis_id: str) -> List[Dict[str, Any]]:
        """
        Get all reports for an analysis
        
        Args:
            analysis_id: UUID of analysis
            
        Returns:
            List of report records
        """
        try:
            result = self.client.table("coliving_reports").select("*").eq("analysis_id", analysis_id).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving reports: {e}")
            return []
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def log_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log a chatbot conversation
        
        Args:
            conversation_data: Conversation message and metadata
            
        Returns:
            Created conversation record
        """
        try:
            record = {
                "user_id": conversation_data.get("user_id", "anonymous"),
                "session_id": conversation_data.get("session_id", str(uuid.uuid4())),
                "property_id": conversation_data.get("property_id"),
                "user_message": conversation_data.get("user_message"),
                "assistant_response": conversation_data.get("assistant_response"),
                "intent_classified": conversation_data.get("intent_classified"),
                "entities_extracted": json.dumps(conversation_data.get("entities_extracted", {})),
                "response_time_ms": conversation_data.get("response_time_ms"),
                "model_used": conversation_data.get("model_used", "claude-sonnet-4-20250514")
            }
            
            result = self.client.table("coliving_conversations").insert(record).execute()
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error logging conversation: {e}")
            raise
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages
            
        Returns:
            List of conversation records
        """
        try:
            result = self.client.table("coliving_conversations").select("*").eq("session_id", session_id).order("created_at", desc=False).limit(limit).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving conversation history: {e}")
            return []
    
    # ==================== SCENARIO OPERATIONS ====================
    
    def save_scenario(self, property_id: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a scenario comparison
        
        Args:
            property_id: UUID of property
            scenario_data: Scenario assumptions and results
            
        Returns:
            Created scenario record
        """
        try:
            record = {
                "property_id": property_id,
                "scenario_name": scenario_data.get("scenario_name"),
                "scenario_description": scenario_data.get("scenario_description"),
                "modified_assumptions": json.dumps(scenario_data.get("modified_assumptions", {})),
                "scenario_noi": scenario_data.get("noi"),
                "scenario_cap_rate": scenario_data.get("cap_rate"),
                "scenario_cash_flow": scenario_data.get("cash_flow"),
                "scenario_dscr": scenario_data.get("dscr"),
                "base_scenario": scenario_data.get("base_scenario", False),
                "variance_from_base": json.dumps(scenario_data.get("variance_from_base", {}))
            }
            
            result = self.client.table("coliving_scenarios").insert(record).execute()
            
            logger.info(f"✅ Scenario saved: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Error saving scenario: {e}")
            raise
    
    def get_scenarios(self, property_id: str) -> List[Dict[str, Any]]:
        """
        Get all scenarios for a property
        
        Args:
            property_id: UUID of property
            
        Returns:
            List of scenario records
        """
        try:
            result = self.client.table("coliving_scenarios").select("*").eq("property_id", property_id).order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving scenarios: {e}")
            return []
    
    # ==================== ANALYTICS ====================
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get platform analytics summary
        
        Returns:
            Analytics data (total properties, analyses, avg metrics, etc.)
        """
        try:
            # Total properties
            properties_count = len(self.client.table("coliving_properties").select("id").execute().data)
            
            # Total analyses
            analyses_count = len(self.client.table("coliving_analyses").select("id").execute().data)
            
            # Average metrics
            analyses = self.client.table("coliving_analyses").select("noi,cap_rate,cash_on_cash_return,dscr").execute().data
            
            avg_noi = sum(a.get("noi", 0) for a in analyses) / len(analyses) if analyses else 0
            avg_cap_rate = sum(a.get("cap_rate", 0) for a in analyses) / len(analyses) if analyses else 0
            avg_coc = sum(a.get("cash_on_cash_return", 0) for a in analyses) / len(analyses) if analyses else 0
            avg_dscr = sum(a.get("dscr", 0) for a in analyses) / len(analyses) if analyses else 0
            
            # Investment decisions breakdown
            buy_count = len([a for a in analyses if a.get("investment_decision") == "BUY"])
            pass_count = len([a for a in analyses if a.get("investment_decision") == "PASS"])
            further_count = len([a for a in analyses if a.get("investment_decision") == "FURTHER_ANALYSIS"])
            
            return {
                "total_properties": properties_count,
                "total_analyses": analyses_count,
                "avg_noi": round(avg_noi, 2),
                "avg_cap_rate": round(avg_cap_rate, 2),
                "avg_cash_on_cash": round(avg_coc, 2),
                "avg_dscr": round(avg_dscr, 2),
                "investment_decisions": {
                    "BUY": buy_count,
                    "PASS": pass_count,
                    "FURTHER_ANALYSIS": further_count
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error retrieving analytics: {e}")
            return {}


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize client
    supabase = CoLivingSupabaseClient()
    
    # Example: Create property
    property_data = {
        "property_name": "Brevard Beach Co-Living",
        "property_location": "Satellite Beach, FL",
        "total_units": 20,
        "total_bedrooms": 30,
        "unit_mix": {"studio": 5, "1br": 10, "2br": 5},
        "assumptions": {
            "avg_rent_per_bedroom": 900,
            "occupancy_rate": 0.93,
            "purchase_price": 2000000
        },
        "user_id": "demo_user",
        "session_id": "demo_session_001"
    }
    
    property = supabase.create_property(property_data)
    print(f"✅ Property created: {property['id']}")
    
    # Example: Save analysis
    analysis_results = {
        "property_data": {"intent": "full_analysis"},
        "revenue_projections": {"annual_gpi": 324000, "effective_gross_income": 301320},
        "expense_analysis": {"total_operating_expenses": 150660},
        "cash_flow": {"noi": 150660, "dscr": 1.35},
        "returns_metrics": {"cap_rate": 7.53, "cash_on_cash_return": 8.2},
        "sensitivity_analysis": {},
        "risk_assessment": {"risks_identified": ["Market risk moderate"]},
        "recommendations": ["Strong investment opportunity", "DSCR above 1.25x"],
        "analysis_stage": "complete"
    }
    
    analysis = supabase.save_analysis(property['id'], analysis_results)
    print(f"✅ Analysis saved: {analysis['id']}")
    
    # Get analytics
    analytics = supabase.get_analytics_summary()
    print(f"📊 Platform Analytics: {analytics}")
