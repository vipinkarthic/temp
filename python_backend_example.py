# Simple Python Backend for NLP Testing
# This is an example of how your Python backend should be structured

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import httpx
import json
import random

# Available models for NLP attacks
AVAILABLE_MODELS = [
    'vicuna-13b-v1.5',
    'llama-2-7b-chat-hf',
    'gpt-3.5-turbo-1106',
    'gpt-4-0125-preview'
]

# Available defense types for NLP
AVAILABLE_DEFENSES = [
    'sanitize_text',
    'meta-prompt wrapper', 
    'Llama Guard'
]

class AttackPayload(BaseModel):
    model_name: str
    behaviour: str

class VisionAttackPayload(BaseModel):
    attack_type: str
    csv_file: Optional[str] = None    # path as string
    image_file: Optional[str] = None  # path as string

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response Models
class TestRequest(BaseModel):
    testId: str
    category: str  # 'white' or 'black'
    modelId: Optional[str] = None
    customDatasetPath: Optional[str] = None
    curlEndpoint: Optional[str] = None
    attackCategory: Optional[str] = None
    defenseType: Optional[str] = None  # Defense type for NLP
    
    def validate_model(self):
        """Validate that modelId is in the available models list"""
        if self.modelId and self.modelId not in AVAILABLE_MODELS:
            raise ValueError(f"Model {self.modelId} not in available models: {AVAILABLE_MODELS}")
    
    def validate_defense(self):
        """Validate that defenseType is in the available defenses list"""
        if self.defenseType and self.defenseType not in AVAILABLE_DEFENSES:
            raise ValueError(f"Defense {self.defenseType} not in available defenses: {AVAILABLE_DEFENSES}")

class TestResponse(BaseModel):
    success: bool
    testId: str
    status: str  # 'completed' or 'failed'
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Webhook URL for updating test status
WEBHOOK_URL = "http://localhost:3000/api/webhooks/test-update"

async def update_test_status(test_id: str, status: str, results: Optional[Dict] = None, error: Optional[str] = None):
    """Update test status via webhook"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "testId": test_id,
                "status": status,
                "results": results,
                "error": error
            }
            response = await client.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()
    except Exception as e:
        print(f"Failed to update test status: {e}")

async def run_white_box_test(test_id: str, model_id: str, dataset_path: str, defense_type: str = None):
    """Simulate white box testing with optional defense"""
    try:
        # Update status to running
        await update_test_status(test_id, "running", {"progress": 0})
        
        # Simulate processing time
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(1)  # Simulate work
            await update_test_status(test_id, "running", {"progress": progress})
        
        # Simulate results without defense
        import random
        asr_value = round(random.uniform(0.4, 0.8), 3)  # Random ASR between 40% and 80%
        accuracy_value = round(random.uniform(0.85, 0.95), 3)  # Random accuracy between 85% and 95%
        recall_value = round(random.uniform(0.8, 0.9), 3)  # Random recall between 80% and 90%
        precision_value = round(random.uniform(0.8, 0.9), 3)  # Random precision between 80% and 90%
        f1_value = round((2 * precision_value * recall_value) / (precision_value + recall_value), 3)  # Calculate F1
        
        results = {
            "asr": asr_value,
            "accuracy": accuracy_value,
            "recall": recall_value,
            "precision": precision_value,
            "f1": f1_value
        }
        
        # If defense is applied, simulate defense results (typically better performance)
        if defense_type:
            # Defense typically reduces ASR and improves other metrics
            defense_asr_value = round(asr_value * random.uniform(0.3, 0.7), 3)  # Defense reduces ASR by 30-70%
            defense_accuracy_value = round(min(accuracy_value * random.uniform(1.0, 1.1), 0.99), 3)  # Slight improvement
            defense_recall_value = round(min(recall_value * random.uniform(1.0, 1.1), 0.99), 3)  # Slight improvement
            defense_precision_value = round(min(precision_value * random.uniform(1.0, 1.1), 0.99), 3)  # Slight improvement
            defense_f1_value = round((2 * defense_precision_value * defense_recall_value) / (defense_precision_value + defense_recall_value), 3)
            
            results.update({
                "defenseASR": defense_asr_value,
                "defenseAccuracy": defense_accuracy_value,
                "defenseRecall": defense_recall_value,
                "defensePrecision": defense_precision_value,
                "defenseF1": defense_f1_value
            })
        
        await update_test_status(test_id, "completed", results)
        
    except Exception as e:
        await update_test_status(test_id, "failed", error=str(e))

async def run_black_box_test(test_id: str, curl_endpoint: str, attack_category: str, defense_type: str = None):
    """Simulate black box testing with optional defense"""
    try:
        # Update status to running
        await update_test_status(test_id, "running", {"progress": 0})
        
        # Simulate processing time
        for progress in [20, 40, 60, 80, 100]:
            await asyncio.sleep(1)  # Simulate work
            await update_test_status(test_id, "running", {"progress": progress})
        
        # Simulate results without defense - only one category ASR since each test is for one category
        import random
        asr_value = round(random.uniform(0.3, 0.9), 3)  # Random ASR between 30% and 90%
        latency_value = round(random.uniform(1.0, 5.0), 2)  # Random latency between 1-5 seconds
        token_usage = random.randint(500, 2000)  # Random token usage
        
        results = {
            "asr": asr_value,
            "latency": latency_value,
            "tokenUsage": token_usage,
            "categoryWiseASR": {
                attack_category: asr_value  # Use the actual attack category from the test
            }
        }
        
        # If defense is applied, simulate defense results
        if defense_type:
            # Defense typically reduces ASR and may increase latency
            defense_asr_value = round(asr_value * random.uniform(0.2, 0.6), 3)  # Defense reduces ASR by 40-80%
            defense_latency_value = round(latency_value * random.uniform(1.1, 1.5), 2)  # Defense may increase latency
            defense_token_usage = int(token_usage * random.uniform(1.0, 1.3))  # Defense may increase token usage
            
            results.update({
                "defenseASR": defense_asr_value,
                "defenseLatency": defense_latency_value,
                "defenseTokenUsage": defense_token_usage,
                "defenseCategoryWiseASR": {
                    attack_category: defense_asr_value  # Only one category ASR with defense
                }
            })
        
        await update_test_status(test_id, "completed", results)
        
    except Exception as e:
        await update_test_status(test_id, "failed", error=str(e))

@app.get("/")
async def root():
    return {"message": "Python Backend is running!", "status": "healthy"}

@app.get("/api/models")
async def get_available_models():
    """Get list of available models for NLP attacks"""
    return {
        "models": AVAILABLE_MODELS,
        "count": len(AVAILABLE_MODELS)
    }

@app.get("/api/defenses")
async def get_available_defenses():
    """Get list of available defense types for NLP attacks"""
    return {
        "defenses": AVAILABLE_DEFENSES,
        "count": len(AVAILABLE_DEFENSES)
    }

@app.options("/api/tests/submit")
async def options_submit_test():
    return {"message": "OK"}

@app.options("/api/tests/{test_id}/status")
async def options_test_status(test_id: str):
    return {"message": "OK"}

@app.post("/api/tests/submit")
async def submit_test(request: TestRequest):
    """Submit a new test for processing"""
    try:
        # Validate the request
        if request.category not in ['white', 'black']:
            raise HTTPException(status_code=400, detail="Category must be 'white' or 'black'")
        
        # Validate model for white box tests
        if request.category == 'white' and request.modelId:
            request.validate_model()
        
        # Validate defense type if provided
        if request.defenseType:
            request.validate_defense()
        
        if request.category == "white":
            if not request.modelId or not request.customDatasetPath:
                raise HTTPException(status_code=400, detail="White box tests require modelId and customDatasetPath")
            
            # Start white box test asynchronously
            asyncio.create_task(run_white_box_test(request.testId, request.modelId, request.customDatasetPath, request.defenseType))
            
        elif request.category == "black":
            if not request.curlEndpoint or not request.attackCategory:
                raise HTTPException(status_code=400, detail="Black box tests require curlEndpoint and attackCategory")
            
            # Start black box test asynchronously
            asyncio.create_task(run_black_box_test(request.testId, request.curlEndpoint, request.attackCategory, request.defenseType))
            
        else:
            raise HTTPException(status_code=400, detail="Invalid category. Must be 'white' or 'black'")
        
        return {"success": True, "message": "Test submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests/{test_id}/status")
async def get_test_status(test_id: str):
    """Get test status (optional endpoint)"""
    # This is optional - the webhook handles status updates
    return {"success": True, "testId": test_id, "status": "running"}

@app.get("/api/models")
async def get_available_models():
    """Get available models for white box testing"""
    models = [
        "gpt-2",
        "bert-base-uncased", 
        "roberta-base",
        "distilbert-base-uncased",
        "t5-small"
    ]
    return {"models": models}

@app.get("/api/attack-categories")
async def get_attack_categories():
    """Get available attack categories for black box testing"""
    categories = [
        "Phishing",
        "Prompt Injection", 
        "Jailbreaking",
        "Data Extraction"
    ]
    return {"categories": categories}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
