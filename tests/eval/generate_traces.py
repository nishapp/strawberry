import os
import json
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

# Set integration test mode to use mocks for LLM agents during test execution
os.environ["INTEGRATION_TEST"] = "TRUE"

from strawberry_agent.agent import app as adk_app

def get_response_text(output_val, events=None) -> str:
    """Safely extracts the response text from the output, falling back to scanning event contents."""
    if output_val is not None:
        if isinstance(output_val, dict):
            return output_val.get("response") or ""
        return getattr(output_val, "response", "")
        
    if events:
        for e in reversed(events):
            if e.content and e.content.parts:
                for part in e.content.parts:
                    if part.text:
                        try:
                            data = json.loads(part.text)
                            if isinstance(data, dict) and "response" in data:
                                return data["response"]
                        except Exception:
                            pass
                        return part.text
    return ""

async def run_case(case):
    session_service = InMemorySessionService()
    session = await session_service.create_session(user_id="eval_user", app_name="eval")
    runner = Runner(app=adk_app, session_service=session_service, app_name="eval")

    print(f"Running Case: {case['name']}...")
    message = types.Content(role="user", parts=[types.Part.from_text(text=case["input"])])
    
    events = []
    async for event in runner.run_async(
        new_message=message,
        user_id="eval_user",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    ):
        events.append(event)
        
    # Check for HIL pause
    interrupt_event = None
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call and part.function_call.name == "adk_request_input":
                    interrupt_event = event
                    break
                    
    resumed = False
    final_events = list(events)
    
    if interrupt_event and case.get("hil_expected", False):
        interrupt_id = interrupt_event.content.parts[0].function_call.id
        decision = case.get("hil_decision", True)
        print(f"  -> Workflow paused on HIL. Auto-deciding response: approved={decision}")
        
        resume_msg = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        id=interrupt_id,
                        name="adk_request_input",
                        response={"approved": decision}
                    )
                )
            ]
        )
        
        resume_events = []
        async for event in runner.run_async(
            new_message=resume_msg,
            user_id="eval_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        ):
            resume_events.append(event)
            
        final_events.extend(resume_events)
        resumed = True

    session_after = await session_service.get_session(app_name="eval", user_id="eval_user", session_id=session.id)
    final_output = final_events[-1].output
    response_text = get_response_text(final_output, final_events)
    
    # Compile trace details
    trace = {
        "case_id": case["id"],
        "case_name": case["name"],
        "input": case["input"],
        "expected_route": case["expected_route"],
        "response": response_text,
        "classified_intent": session_after.state.get("classified_intent"),
        "redacted_categories": session_after.state.get("redacted_categories"),
        "security_event_flagged": session_after.state.get("security_event_flagged", False),
        "injection_detected": session_after.state.get("injection_detected", False),
        "hil_occurred": interrupt_event is not None,
        "resumed": resumed
    }
    return trace

async def main():
    with open("tests/eval/datasets/basic-dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    traces = []
    for case in dataset:
        trace = await run_case(case)
        traces.append(trace)
        print(f"  Result: {trace['response']}")
        print(f"  Intent: {trace['classified_intent']} | Redacted: {trace['redacted_categories']} | Security Flagged: {trace['security_event_flagged']}\n")
        
    os.makedirs("tests/eval", exist_ok=True)
    with open("tests/eval/traces.json", "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)
    print("Traces successfully generated and saved to tests/eval/traces.json")

if __name__ == "__main__":
    asyncio.run(main())
