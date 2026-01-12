"""
FastAPI Backend for Co-Living Proforma AI
REST API with Supabase integration

Author: BidDeed.AI
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import base64
import io

from coliving_orchestrator import CoLivingProformaAgent, CoLivingChatbot
from coliving_report_generators import CoLivingReportGenerator
from coliving_supabase import CoLivingSupabaseClient

# Initialize FastAPI app
app = FastAPI(
    title="BidDeed.AI Co-Living Proforma API",
    description="AI-Powered Co-Living Real Estate Investment Analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chatbot = CoLivingChatbot()
supabase = CoLivingSupabaseClient()

# ==================== PYDANTIC MODELS ====================

class AnalysisRequest(BaseModel):
    query: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None
    custom_assumptions: Optional[Dict[str, Any]] = None

class PropertyCreate(BaseModel):
    property_name: str
    property_location: str = "Brevard County, FL"
    total_units: int
    total_bedrooms: Optional[int] = None
    unit_mix: Optional[Dict[str, int]] = None
    assumptions: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = "anonymous"

class ScenarioCreate(BaseModel):
    property_id: str
    scenario_name: str
    scenario_description: Optional[str] = None
    modified_assumptions: Dict[str, Any]

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "BidDeed.AI Co-Living Proforma API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Supabase connection
        analytics = supabase.get_analytics_summary()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "online",
                "supabase": "connected",
                "langgraph": "ready"
            },
            "analytics": analytics
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

# ==================== ANALYSIS ENDPOINTS ====================

@app.post("/api/analyze")
async def analyze_property(request: AnalysisRequest):
    """
    Analyze co-living property via natural language query
    
    Returns complete analysis with chatbot response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Start timing
        start_time = datetime.now()
        
        # Run analysis through chatbot
        result = chatbot.process_query(request.query)
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Extract property data from analysis
        full_analysis = result['full_analysis']
        property_data_raw = full_analysis.get('property_data', {})
        
        # Create property record in Supabase
        property_data = {
            "property_name": property_data_raw.get("property_location", "Co-Living Property"),
            "property_location": property_data_raw.get("property_location", "Brevard County, FL"),
            "total_units": property_data_raw.get("unit_count", 20),
            "total_bedrooms": property_data_raw.get("total_bedrooms"),
            "unit_mix": property_data_raw.get("bedroom_mix"),
            "assumptions": full_analysis.get("assumptions", {}),
            "user_id": request.user_id,
            "session_id": session_id
        }
        
        property_record = supabase.create_property(property_data)
        property_id = property_record['id']
        
        # Save analysis to Supabase
        analysis_record = supabase.save_analysis(property_id, full_analysis)
        analysis_id = analysis_record['id']
        
        # Log conversation
        conversation_data = {
            "user_id": request.user_id,
            "session_id": session_id,
            "property_id": property_id,
            "user_message": request.query,
            "assistant_response": result['chatbot_response'],
            "intent_classified": property_data_raw.get("intent"),
            "entities_extracted": {},
            "response_time_ms": int(response_time)
        }
        supabase.log_conversation(conversation_data)
        
        return {
            "success": True,
            "property_id": property_id,
            "analysis_id": analysis_id,
            "session_id": session_id,
            "chatbot_response": result['chatbot_response'],
            "dashboard_data": result['dashboard_data'],
            "key_metrics": {
                "noi": analysis_record['noi'],
                "cap_rate": analysis_record['cap_rate'],
                "cash_on_cash_return": analysis_record['cash_on_cash_return'],
                "dscr": analysis_record['dscr']
            },
            "investment_decision": analysis_record['investment_decision'],
            "response_time_ms": int(response_time)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/properties")
async def create_property(property: PropertyCreate):
    """Create a new property record"""
    try:
        property_data = property.dict()
        record = supabase.create_property(property_data)
        return {"success": True, "property": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}")
async def get_property(property_id: str):
    """Get property by ID"""
    try:
        property_record = supabase.get_property(property_id)
        if not property_record:
            raise HTTPException(status_code=404, detail="Property not found")
        return {"success": True, "property": property_record}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties")
async def list_properties(user_id: Optional[str] = None, limit: int = 50):
    """List properties, optionally filtered by user"""
    try:
        properties = supabase.list_properties(user_id=user_id, limit=limit)
        return {"success": True, "properties": properties, "count": len(properties)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REPORT ENDPOINTS ====================

@app.get("/api/analyses/{analysis_id}/reports/excel")
async def generate_excel_report(analysis_id: str):
    """Generate Excel proforma for an analysis"""
    try:
        # Get analysis
        analysis = supabase.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Reconstruct analysis_results for report generator
        analysis_results = {
            "property_data": {},
            "assumptions": analysis.get("assumptions") or {},
            "revenue_projections": analysis.get("revenue_projections") or {},
            "expense_analysis": analysis.get("expense_analysis") or {},
            "cash_flow": analysis.get("cash_flow") or {},
            "returns_metrics": analysis.get("returns_metrics") or {},
            "sensitivity_analysis": analysis.get("sensitivity_analysis") or {},
            "risk_assessment": analysis.get("risk_assessment") or {},
            "recommendations": analysis.get("recommendations") or []
        }
        
        # Generate Excel
        generator = CoLivingReportGenerator(analysis_results)
        excel_bytes = generator.generate_excel_report()
        
        # Encode to base64 for JSON response
        excel_b64 = base64.b64encode(excel_bytes).decode('utf-8')
        
        # Save report metadata
        report_data = {
            "report_type": "excel_proforma",
            "file_size_bytes": len(excel_bytes)
        }
        supabase.save_report(analysis_id, report_data)
        
        return {
            "success": True,
            "filename": f"coliving_proforma_{analysis_id[:8]}.xlsx",
            "file_base64": excel_b64,
            "file_size_bytes": len(excel_bytes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses/{analysis_id}/reports/pdf")
async def generate_pdf_report(analysis_id: str):
    """Generate PDF executive summary for an analysis"""
    try:
        # Get analysis
        analysis = supabase.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Reconstruct analysis_results
        analysis_results = {
            "property_data": {},
            "assumptions": analysis.get("assumptions") or {},
            "revenue_projections": analysis.get("revenue_projections") or {},
            "expense_analysis": analysis.get("expense_analysis") or {},
            "cash_flow": analysis.get("cash_flow") or {},
            "returns_metrics": analysis.get("returns_metrics") or {},
            "sensitivity_analysis": analysis.get("sensitivity_analysis") or {},
            "risk_assessment": analysis.get("risk_assessment") or {},
            "recommendations": analysis.get("recommendations") or []
        }
        
        # Generate PDF
        generator = CoLivingReportGenerator(analysis_results)
        pdf_bytes = generator.generate_pdf_report()
        
        # Encode to base64
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Save report metadata
        report_data = {
            "report_type": "pdf_executive_summary",
            "file_size_bytes": len(pdf_bytes)
        }
        supabase.save_report(analysis_id, report_data)
        
        return {
            "success": True,
            "filename": f"coliving_summary_{analysis_id[:8]}.pdf",
            "file_base64": pdf_b64,
            "file_size_bytes": len(pdf_bytes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses/{analysis_id}/dashboard")
async def get_dashboard_data(analysis_id: str):
    """Get dashboard data for an analysis"""
    try:
        # Get analysis
        analysis = supabase.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Reconstruct analysis_results
        analysis_results = {
            "property_data": {},
            "assumptions": analysis.get("assumptions") or {},
            "revenue_projections": analysis.get("revenue_projections") or {},
            "expense_analysis": analysis.get("expense_analysis") or {},
            "cash_flow": analysis.get("cash_flow") or {},
            "returns_metrics": analysis.get("returns_metrics") or {},
            "sensitivity_analysis": analysis.get("sensitivity_analysis") or {},
            "risk_assessment": analysis.get("risk_assessment") or {},
            "recommendations": analysis.get("recommendations") or []
        }
        
        # Generate dashboard JSON
        generator = CoLivingReportGenerator(analysis_results)
        dashboard_json = generator.generate_dashboard_json()
        
        return {
            "success": True,
            "dashboard_data": dashboard_json
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SCENARIO ENDPOINTS ====================

@app.post("/api/scenarios")
async def create_scenario(scenario: ScenarioCreate):
    """Create a scenario comparison"""
    try:
        # Run analysis with modified assumptions
        # (Implementation would integrate with orchestrator)
        
        scenario_data = scenario.dict()
        record = supabase.save_scenario(scenario.property_id, scenario_data)
        
        return {"success": True, "scenario": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}/scenarios")
async def get_property_scenarios(property_id: str):
    """Get all scenarios for a property"""
    try:
        scenarios = supabase.get_scenarios(property_id)
        return {"success": True, "scenarios": scenarios, "count": len(scenarios)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CONVERSATION ENDPOINTS ====================

@app.get("/api/conversations/{session_id}")
async def get_conversation_history(session_id: str, limit: int = 50):
    """Get conversation history for a session"""
    try:
        conversations = supabase.get_conversation_history(session_id, limit=limit)
        return {"success": True, "conversations": conversations, "count": len(conversations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics")
async def get_analytics():
    """Get platform analytics summary"""
    try:
        analytics = supabase.get_analytics_summary()
        return {"success": True, "analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
