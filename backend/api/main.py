import asyncio



from pathlib import Path



from io import BytesIO



from typing import Optional



from uuid import uuid4



import hashlib



from concurrent.futures import ThreadPoolExecutor



from threading import Lock







from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile



from fastapi.middleware.cors import CORSMiddleware



from fastapi.staticfiles import StaticFiles







from backend.api.engines.worktrace_engine import WorkTraceEngine



from backend.api.engines.skill_shadow_engine import SkillShadowEngine



from backend.api.engines.workfold_engine import WorkFoldEngine



from backend.api.engines.lattice_engine import LatticeEngine







from backend.api.services.intelligence_service import IntelligenceService



from backend.api.services.lattice_generator import LatticeGenerator, LatticeGenerationError



from backend.api.services.industry_pulse_service import IndustryPulseService



from backend.api.services.ella_service import ella_service






from backend.api.services.workforce_service import (

    get_workforce_metrics,

    get_market_metrics,

    get_workforce_overview,

    get_workforce_transformation,

    get_role_distribution,

    get_skill_distribution,

    get_role_skill_gaps,

)





from backend.api.services.visual_engine.animation_planner import AnimationPlanner



from backend.api.services.visual_engine.animation_renderer import render_lesson



from backend.api.services.native_visual_engine.native_visual_lesson import router as native_visual_router











# ============================================================



# FORGE APPLICATION



# ============================================================







# Visual rendering runs in a background worker so the browser never blocks on Manim.



_VISUAL_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="forge-visual")



_VISUAL_JOBS = {}



_VISUAL_JOBS_LOCK = Lock()



VISUAL_RENDER_VERSION = "v4_voice_layout_faststart"











def _set_visual_job(job_id: str, **updates):



    with _VISUAL_JOBS_LOCK:



        job = _VISUAL_JOBS.setdefault(job_id, {})



        job.update(updates)



        return dict(job)











def _run_visual_job(job_id: str, topic: str, topic_data: dict, language: str, difficulty: str):



    try:



        print(f"[VISUAL JOB {job_id}] Worker started for topic={topic!r}", flush=True)



        _set_visual_job(job_id, status="planning", progress=8, message="Building the semantic storyboard…")



        planner = get_animation_planner()



        lesson = planner.create_lesson(topic_data=topic_data, language=language, difficulty=difficulty)



        _set_visual_job(job_id, status="rendering", progress=30, message="Storyboard ready. Starting topic-specific Manim render…", lesson=lesson)







        safe_topic = "".join(char if char.isalnum() else "_" for char in topic).strip("_") or "topic"



        cache_key = hashlib.sha1(



            f"{VISUAL_RENDER_VERSION}|{topic}|{language}|{difficulty}".encode("utf-8")



        ).hexdigest()[:12]



        output_path = VISUAL_OUTPUT_DIR / f"{safe_topic}_{cache_key}.mp4"







        if output_path.exists() and output_path.stat().st_size > 100_000:



            video_path = output_path



            print(f"[VISUAL JOB {job_id}] Cache hit -> {video_path.name}", flush=True)



        else:



            print(f"[VISUAL JOB {job_id}] Rendering {topic!r} -> {output_path.name}", flush=True)



            video_path = render_lesson(lesson, output_path)



        video_path = Path(video_path).resolve()



        if not video_path.exists():



            raise FileNotFoundError(f"Rendered video was not found: {video_path}")







        video_url = f"/api/student/visuals/{video_path.name}"



        _set_visual_job(



            job_id, status="complete", progress=100, message="Visual lesson ready.",



            lesson=lesson, video={"generated": True, "filename": video_path.name, "path": str(video_path), "url": video_url}



        )



        print(f"[VISUAL JOB {job_id}] Complete", flush=True)



    except Exception as exc:



        print(f"[VISUAL JOB {job_id}] ERROR: {exc}", flush=True)



        _set_visual_job(job_id, status="error", progress=100, message=str(exc), error=str(exc))











app = FastAPI(



    title="FORGE — Future Workforce Intelligence Engine",



    description=(



        "Future-Oriented Workforce Reconfiguration & Growth Engine. "



        "FORGE maps work to capabilities, detects capability exposure "



        "loss under AI adoption, redesigns Human-AI work allocation, "



        "and builds capability-preservation pathways."



    ),



    version="1.0.0",



)







# Native browser-based Visual Learn engine (Gemini + HTML/CSS/SVG)



app.include_router(native_visual_router)







# ============================================================



# VISUAL LESSON OUTPUTS



# ============================================================







VISUAL_OUTPUT_DIR = (



    Path(__file__).resolve().parent



    / "services"



    / "visual_engine"



    / "generated_visuals"



)







VISUAL_OUTPUT_DIR.mkdir(



    parents=True,



    exist_ok=True,



)







# Makes generated MP4 files directly playable by the frontend.



app.mount(



    "/api/student/visuals",



    StaticFiles(directory=str(VISUAL_OUTPUT_DIR)),



    name="forge_visuals",



)











# ============================================================



# CORS



# ============================================================







app.add_middleware(



    CORSMiddleware,



    allow_origins=["*"],



    allow_credentials=True,



    allow_methods=["*"],



    allow_headers=["*"],



)











# ============================================================



# ENGINE INITIALIZATION



# ============================================================







print("\n" + "=" * 75)



print("FORGE — FUTURE WORKFORCE INTELLIGENCE ENGINE")



print("=" * 75)







print("\n[BOOT] Loading FORGE intelligence layers...\n")











# ------------------------------------------------------------



# WORKTRACE



# ------------------------------------------------------------







try:



    worktrace_engine = WorkTraceEngine()



    print("[OK] WORKTRACE loaded")







except Exception as exc:



    worktrace_engine = None



    print(f"[ERROR] WORKTRACE failed: {exc}")











# ------------------------------------------------------------



# SKILL SHADOW



# ------------------------------------------------------------







try:



    skill_shadow_engine = SkillShadowEngine()



    print("[OK] SKILL SHADOW loaded")







except Exception as exc:



    skill_shadow_engine = None



    print(f"[ERROR] SKILL SHADOW failed: {exc}")











# ------------------------------------------------------------



# WORKFOLD



# ------------------------------------------------------------







try:



    workfold_engine = WorkFoldEngine()



    print("[OK] WORKFOLD loaded")







except Exception as exc:



    workfold_engine = None



    print(f"[ERROR] WORKFOLD failed: {exc}")











# ------------------------------------------------------------



# LATTICE



# ------------------------------------------------------------







try:



    lattice_engine = LatticeEngine()



    print("[OK] LATTICE loaded")







except Exception as exc:



    lattice_engine = None



    print(f"[ERROR] LATTICE failed: {exc}")











# ============================================================



# INTELLIGENCE SERVICE



# ============================================================







intelligence_service = IntelligenceService(



    worktrace_engine=worktrace_engine,



    skill_shadow_engine=skill_shadow_engine,



    workfold_engine=workfold_engine,



    lattice_engine=lattice_engine,



)







print("\n[OK] INTELLIGENCE SERVICE initialized")











# ============================================================



# INDUSTRY PULSE



# ============================================================







try:



    industry_pulse_service = IndustryPulseService()



    print("[OK] INDUSTRY PULSE service configured")



except Exception as exc:



    industry_pulse_service = None



    print(f"[WARN] INDUSTRY PULSE unavailable: {exc}")











# ============================================================



# LATTICE GROQ GENERATOR



# ============================================================







try:



    lattice_generator = LatticeGenerator()



    print("[OK] LATTICE Groq generator configured")



except Exception as exc:



    lattice_generator = None



    print(f"[WARN] LATTICE Groq generator unavailable: {exc}")







# ============================================================



# ELLA AI ASSISTANT



# ============================================================







try:



    ella_status = ella_service.health()



    print(f"[OK] ELLA configured | chat_model={ella_status.get("chat_model")}")



except Exception as exc:



    ella_status = {"service": "ELLA", "status": "unavailable"}



    print(f"[WARN] ELLA unavailable: {exc}")







print("\n" + "=" * 75)



print("FORGE BACKEND READY")



print("=" * 75 + "\n")











# ============================================================



# HELPER



# ============================================================







def get_animation_planner() -> AnimationPlanner:



    """



    Return the generic FORGE visual-learning animation planner.







    The planner is created on demand so backend startup does not fail



    when the LLM API key is unavailable.



    """



    try:



        return AnimationPlanner()



    except Exception as exc:



        raise HTTPException(



            status_code=503,



            detail=f"Visual animation planner is not available: {exc}"



        )











def require_engine(engine, engine_name: str):



    """



    Return the requested engine or raise a service-unavailable error.



    """







    if engine is None:



        raise HTTPException(



            status_code=503,



            detail=f"{engine_name} engine is not available."



        )







    return engine











# ============================================================



# ROOT



# ============================================================







@app.get("/")



def root():







    return {



        "project": "FORGE",







        "full_name": (



            "Future-Oriented Workforce "



            "Reconfiguration & Growth Engine"



        ),







        "tagline": (



            "Automate Work. Preserve Capability. "



            "Build the Future."



        ),







        "version": "1.0.0",







        "status": "operational",







        "architecture": {



            "WORKTRACE": "Observe",



            "SKILL_SHADOW": "Detect",



            "WORKFOLD": "Reconfigure",



            "LATTICE": "Rebuild",



            "INTELLIGENCE_SERVICE": "Orchestrate"



        },







        "modules": [



            "WORKTRACE",



            "SKILL SHADOW",



            "WORKFOLD",



            "LATTICE",



            "INTELLIGENCE SERVICE"



        ]



    }











# ============================================================



# HEALTH



# ============================================================







@app.get("/api/health")



def health():







    return {



        "status": "healthy",







        "service": "FORGE Backend",







        "engines": {



            "worktrace": worktrace_engine is not None,



            "skill_shadow": skill_shadow_engine is not None,



            "workfold": workfold_engine is not None,



            "lattice": lattice_engine is not None,



        },







        "intelligence_service": (



            intelligence_service is not None



        )



    }











# ============================================================



# WORKTRACE API



# ============================================================







@app.get("/api/worktrace/summary")



def worktrace_summary():







    engine = require_engine(



        worktrace_engine,



        "WORKTRACE"



    )







    try:



        return engine.summary()







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKTRACE summary error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKTRACE SEARCH



# ------------------------------------------------------------







@app.get("/api/worktrace/search")



def worktrace_search(



    q: str = Query(..., min_length=1),



    limit: int = Query(20, ge=1, le=100)



):







    engine = require_engine(



        worktrace_engine,



        "WORKTRACE"



    )







    try:







        return engine.search_occupations(



            q,



            limit



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKTRACE search error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKTRACE OCCUPATION LIST



# ------------------------------------------------------------







@app.get("/api/intelligence/occupations")



def intelligence_occupations(



    q: Optional[str] = Query(None),



    limit: int = Query(1000, ge=1, le=1000)



):







    engine = require_engine(



        worktrace_engine,



        "WORKTRACE"



    )







    try:







        if q and q.strip():







            return engine.search_occupations(



                q,



                limit



            )







        return engine.list_occupations(



            limit



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Occupation list error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# WORKTRACE OCCUPATION



# ------------------------------------------------------------







@app.get("/api/worktrace/occupation")



def worktrace_occupation(



    occupation: str = Query(..., min_length=1)



):







    engine = require_engine(



        worktrace_engine,



        "WORKTRACE"



    )







    try:







        result = engine.get_occupation(



            occupation



        )







        if result is None:



            raise HTTPException(



                status_code=404,



                detail="Occupation not found in WORKTRACE dataset."



            )







        return result







    except HTTPException:



        raise







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKTRACE occupation error: {str(exc)}"



        )











# ============================================================



# SKILL SHADOW API



# ============================================================







@app.get("/api/skill-shadow/summary")



def skill_shadow_summary():







    engine = require_engine(



        skill_shadow_engine,



        "SKILL SHADOW"



    )







    try:



        return engine.summary()







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"SKILL SHADOW summary error: {str(exc)}"



        )











# ------------------------------------------------------------



# SKILL SHADOW SEARCH



# ------------------------------------------------------------







@app.get("/api/skill-shadow/search")



def skill_shadow_search(



    q: str = Query(..., min_length=1),



    limit: int = Query(20, ge=1, le=100)



):







    engine = require_engine(



        skill_shadow_engine,



        "SKILL SHADOW"



    )







    try:







        return engine.search_occupations(



            q,



            limit



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"SKILL SHADOW search error: {str(exc)}"



        )











# ------------------------------------------------------------



# SKILL SHADOW OCCUPATION



# ------------------------------------------------------------







@app.get("/api/skill-shadow/occupation")



def skill_shadow_occupation(



    occupation: str = Query(..., min_length=1)



):







    engine = require_engine(



        skill_shadow_engine,



        "SKILL SHADOW"



    )







    try:







        result = engine.get_occupation(



            occupation



        )







        if result is None:



            raise HTTPException(



                status_code=404,



                detail="Occupation not found in SKILL SHADOW dataset."



            )







        return result







    except HTTPException:



        raise







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"SKILL SHADOW occupation error: {str(exc)}"



        )











# ------------------------------------------------------------



# SKILL SHADOW SCENARIO



# ------------------------------------------------------------







@app.get("/api/skill-shadow/compare")



def skill_shadow_compare(



    occupation: str = Query(..., min_length=1),







    baseline_ai: float = Query(



        0.0,



        ge=0.0,



        le=1.0



    ),







    future_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    engine = require_engine(



        skill_shadow_engine,



        "SKILL SHADOW"



    )







    try:







        return engine.compare_scenarios(



            occupation=occupation,



            baseline_ai=baseline_ai,



            future_ai=future_ai



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"SKILL SHADOW comparison error: {str(exc)}"



        )











# ============================================================



# WORKFOLD API



# ============================================================







@app.get("/api/workfold/summary")



def workfold_summary():







    engine = require_engine(



        workfold_engine,



        "WORKFOLD"



    )







    try:



        return engine.summary()







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKFOLD summary error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKFOLD SEARCH



# ------------------------------------------------------------







@app.get("/api/workfold/search")



def workfold_search(



    q: str = Query(..., min_length=1),



    limit: int = Query(20, ge=1, le=100)



):







    engine = require_engine(



        workfold_engine,



        "WORKFOLD"



    )







    try:







        return engine.search_occupations(



            q,



            limit



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKFOLD search error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKFOLD OCCUPATION



# ------------------------------------------------------------







@app.get("/api/workfold/occupation")



def workfold_occupation(



    occupation: str = Query(..., min_length=1)



):







    engine = require_engine(



        workfold_engine,



        "WORKFOLD"



    )







    try:







        result = engine.get_occupation(



            occupation



        )







        if result is None:



            raise HTTPException(



                status_code=404,



                detail="Occupation not found in WORKFOLD dataset."



            )







        return result







    except HTTPException:



        raise







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKFOLD occupation error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKFOLD SIMULATION



# ------------------------------------------------------------







@app.get("/api/workfold/simulate")



def workfold_simulate(



    occupation: str = Query(..., min_length=1),







    requested_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    engine = require_engine(



        workfold_engine,



        "WORKFOLD"



    )







    try:







        return engine.simulate_occupation(



            occupation=occupation,



            requested_ai=requested_ai



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKFOLD simulation error: {str(exc)}"



        )











# ------------------------------------------------------------



# WORKFOLD SCENARIO COMPARISON



# ------------------------------------------------------------







@app.get("/api/workfold/compare")



def workfold_compare(



    occupation: str = Query(..., min_length=1),







    baseline_ai: float = Query(



        0.0,



        ge=0.0,



        le=1.0



    ),







    future_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    engine = require_engine(



        workfold_engine,



        "WORKFOLD"



    )







    try:







        return engine.compare_scenarios(



            occupation=occupation,



            baseline_ai=baseline_ai,



            future_ai=future_ai



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"WORKFOLD comparison error: {str(exc)}"



        )











# ============================================================



# LATTICE API



# ============================================================







@app.get("/api/lattice/summary")



def lattice_summary():







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:



        return engine.summary()







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"LATTICE summary error: {str(exc)}"



        )











# ------------------------------------------------------------



# LATTICE SEARCH



# ------------------------------------------------------------







@app.get("/api/lattice/search")



def lattice_search(



    q: str = Query(..., min_length=1),



    limit: int = Query(20, ge=1, le=100)



):







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:







        return engine.search_occupations(



            q,



            limit



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"LATTICE search error: {str(exc)}"



        )











# ------------------------------------------------------------



# LATTICE CAPABILITY SEARCH



# ------------------------------------------------------------







@app.get("/api/lattice/capabilities")



def lattice_capabilities(



    q: Optional[str] = Query(None),



    occupation: Optional[str] = Query(None),



    limit: int = Query(50, ge=1, le=200)



):



    """



    Return real LATTICE capabilities.







    The previous implementation called search_capabilities("")



    when no search query was supplied. LatticeEngine intentionally



    returns [] for an empty search query, so the capability selector



    appeared empty.







    This endpoint now supports:



      1. global top LATTICE capabilities,



      2. occupation-specific capabilities,



      3. capability-name search,



      4. occupation + capability-name search.



    """







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:







        query = (



            q or ""



        ).strip()







        occupation_name = (



            occupation or ""



        ).strip()







        # --------------------------------------------------------



        # OCCUPATION-SPECIFIC CAPABILITIES



        # --------------------------------------------------------







        if occupation_name:







            subset = engine._occupation_subset(



                occupation_name



            )







            if subset.empty:







                raise HTTPException(



                    status_code=404,



                    detail=(



                        "Occupation not found in LATTICE dataset: "



                        f"{occupation_name}"



                    )



                )







            # Optional capability-name filtering



            if query:







                mask = (



                    subset[



                        "Capability Name"



                    ]



                    .fillna("")



                    .astype(str)



                    .str.lower()



                    .str.contains(



                        query.lower(),



                        regex=False



                    )



                )







                subset = subset.loc[



                    mask



                ]







            return engine._top_capabilities(



                subset,



                limit=limit



            )







        # --------------------------------------------------------



        # GLOBAL CAPABILITY SEARCH



        # --------------------------------------------------------







        if query:







            return engine.search_capabilities(



                query,



                limit



            )







        # --------------------------------------------------------



        # FIX:



        # Empty search_capabilities("") returns [] by design.



        # For the capability selector we need actual capabilities,



        # so return the highest-priority capabilities from the



        # loaded LATTICE dataset.



        # --------------------------------------------------------







        return engine._top_capabilities(



            engine.df,



            limit=limit



        )







    except HTTPException:



        raise







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "LATTICE capability search error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# LATTICE OCCUPATION



# ------------------------------------------------------------







@app.get("/api/lattice/occupation")



def lattice_occupation(



    occupation: str = Query(..., min_length=1)



):







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:







        result = engine.get_occupation(



            occupation



        )







        if result is None:



            raise HTTPException(



                status_code=404,



                detail="Occupation not found in LATTICE dataset."



            )







        return result







    except HTTPException:



        raise







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"LATTICE occupation error: {str(exc)}"



        )











# ------------------------------------------------------------



# LATTICE CAPABILITY



# ------------------------------------------------------------







@app.get("/api/lattice/capability")



def lattice_capability(



    capability: str = Query(..., min_length=1)



):







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:







        return engine.get_capability(



            capability



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"LATTICE capability error: {str(exc)}"



        )











# ------------------------------------------------------------



# LATTICE PRACTICE PLAN



# ------------------------------------------------------------







@app.get("/api/lattice/practice-plan")



def lattice_practice_plan(



    occupation: str = Query(..., min_length=1),



    capability: str = Query(..., min_length=1)



):







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    try:







        return engine.build_practice_plan(



            occupation=occupation,



            capability=capability



        )







    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=(



                "LATTICE practice-plan error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# LATTICE GROQ PRACTICE GENERATION



# ------------------------------------------------------------







@app.get("/api/lattice/generate")



def lattice_generate_practice(



    occupation: str = Query(..., min_length=1),



    capability: str = Query(..., min_length=1)



):



    """



    Select a real LATTICE source task and generate a new



    synthetic apprenticeship exercise with the configured Groq LLM.







    The generator never pre-scores the learner.



    """







    engine = require_engine(



        lattice_engine,



        "LATTICE"



    )







    if lattice_generator is None:



        raise HTTPException(



            status_code=503,



            detail=(



                "LATTICE Groq generator is not configured. "



                "Set GROQ_API_KEY and restart the backend."



            )



        )







    try:



        # Resolve the requested capability against the actual LATTICE



        # occupation graph. Skill Shadow and LATTICE use different



        # capability vocabularies, so a capability such as "Critical Thinking"



        # may exist upstream but not for this occupation in LATTICE.



        resolved_capability = capability.strip()







        source_plan = engine.build_practice_plan(



            occupation=occupation,



            capability=resolved_capability



        )







        # If the upstream capability is not present in LATTICE, select the



        # highest-priority capability that actually exists for this occupation.



        if not source_plan:



            occupation_data = engine.get_occupation(occupation)







            if occupation_data is None:



                raise HTTPException(



                    status_code=404,



                    detail=f"Occupation '{occupation}' was not found in LATTICE."



                )







            candidates = occupation_data.get("top_capabilities", [])







            if not candidates:



                raise HTTPException(



                    status_code=404,



                    detail=(



                        f"No LATTICE capability context was found for '{occupation}'."



                    )



                )







            resolved_capability = str(



                candidates[0].get("capability", "")



            ).strip()







            if not resolved_capability:



                raise HTTPException(



                    status_code=404,



                    detail=(



                        f"No usable LATTICE capability was found for '{occupation}'."



                    )



                )







            source_plan = engine.build_practice_plan(



                occupation=occupation,



                capability=resolved_capability



            )







        if not source_plan:



            raise HTTPException(



                status_code=404,



                detail=(



                    f"No LATTICE practice context was found for '{occupation}'"



                    f" using capability '{resolved_capability}'."



                )



            )







        if source_plan.get("status") == "NO_PRACTICE_TASK":



            raise HTTPException(



                status_code=404,



                detail=(



                    "No practice task is available for this "



                    "occupation/capability pair."



                )



            )







        source_context = source_plan.get(



            "source_work_context",



            {}



        )







        practice_context = source_plan.get(



            "practice",



            {}



        )







        generated = lattice_generator.generate_practice_set(



            occupation=occupation,



            capability=resolved_capability,



            source_task=source_context.get("task", ""),



            assessment_focus=practice_context.get(



                "assessment_focus",



                ""



            ),



            practice_intent=practice_context.get(



                "practice_intent",



                ""



            ),



            observable_evidence=[],



            source_context={



                "source_plan": source_plan,



                "source_work_context": source_context,



                "risk": source_plan.get("risk", {}),



                "transformation": source_plan.get(



                    "transformation",



                    {}



                ),



                "practice": practice_context,



            },



        )







        return {



            "status": "success",



            "project": "FORGE",



            "occupation": occupation,



            "requested_capability": capability,



            "target_capability": resolved_capability,



            "source_plan": source_plan,



            "generation": generated,



        }







    except HTTPException:



        raise



    except LatticeGenerationError as exc:



        raise HTTPException(



            status_code=502,



            detail=f"LATTICE Groq generation error: {str(exc)}"



        )



    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=(



                "LATTICE generation endpoint error: "



                f"{str(exc)}"



            )



        )











# ============================================================



# INTELLIGENCE SERVICE API



# ============================================================







# ------------------------------------------------------------



# COMPLETE OCCUPATION INTELLIGENCE



# ------------------------------------------------------------







@app.get("/api/intelligence/occupation")



def intelligence_occupation(



    occupation: str = Query(..., min_length=1)



):







    try:







        return intelligence_service.get_occupation_intelligence(



            occupation=occupation



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Intelligence occupation analysis error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# FUTURE WORKFORCE SCENARIO



# ------------------------------------------------------------







@app.get("/api/intelligence/scenario")



def intelligence_scenario(



    occupation: str = Query(..., min_length=1),







    baseline_ai: float = Query(



        0.0,



        ge=0.0,



        le=1.0



    ),







    future_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    try:







        return intelligence_service.simulate_future_workforce(



            occupation=occupation,



            baseline_ai=baseline_ai,



            future_ai=future_ai



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Future workforce scenario error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# WORKFORCE REDESIGN



# ------------------------------------------------------------







@app.get("/api/intelligence/redesign")



def intelligence_redesign(



    occupation: str = Query(..., min_length=1),







    requested_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    try:







        return intelligence_service.workforce_redesign(



            occupation=occupation,



            requested_ai=requested_ai



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Workforce redesign error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# CAPABILITY PRESERVATION



# ------------------------------------------------------------







@app.get("/api/intelligence/preservation")



def intelligence_preservation(



    occupation: str = Query(..., min_length=1),



    capability: str = Query(..., min_length=1)



):







    try:







        return intelligence_service.capability_preservation(



            occupation=occupation,



            capability=capability



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Capability preservation error: "



                f"{str(exc)}"



            )



        )











# ------------------------------------------------------------



# COMPLETE FORGE ANALYSIS



# ------------------------------------------------------------







@app.get("/api/intelligence/complete")



def intelligence_complete(



    occupation: str = Query(..., min_length=1),







    baseline_ai: float = Query(



        0.0,



        ge=0.0,



        le=1.0



    ),







    future_ai: float = Query(



        0.5,



        ge=0.0,



        le=1.0



    )



):







    try:







        return intelligence_service.complete_analysis(



            occupation=occupation,



            baseline_ai=baseline_ai,



            future_ai=future_ai



        )







    except Exception as exc:







        raise HTTPException(



            status_code=500,



            detail=(



                "Complete FORGE analysis error: "



                f"{str(exc)}"



            )



        )











# ============================================================



# STUDENT INDUSTRY PULSE



# ============================================================







@app.get("/api/student/industry-pulse")



def student_industry_pulse(



    role: str = Query(..., min_length=1),



    subjects: str = Query(""),



):



    if industry_pulse_service is None:



        raise HTTPException(status_code=503, detail="Industry Pulse service is not available.")



    try:



        subject_list = [x.strip() for x in subjects.split(",") if x.strip()]



        return industry_pulse_service.build(role=role, subjects=subject_list)



    except FileNotFoundError as exc:



        raise HTTPException(status_code=503, detail=str(exc))



    except Exception as exc:



        raise HTTPException(status_code=500, detail=f"Industry Pulse error: {exc}")











@app.get("/api/student/industry-topic")



def student_industry_topic(



    role: str = Query(..., min_length=1),



    topic: str = Query(..., min_length=1),



    horizon: str = Query("emerging", min_length=1),



):



    """



    Return evidence-backed topic intelligence for a Student Industry Pulse topic.



    """



    if industry_pulse_service is None:



        raise HTTPException(



            status_code=503,



            detail="Industry Pulse service is not available.",



        )







    try:



        return industry_pulse_service.topic_intelligence(



            role=role.strip(),



            topic=topic.strip(),



            horizon=horizon.strip(),



        )



    except HTTPException:



        raise



    except Exception as exc:



        raise HTTPException(



            status_code=500,



            detail=f"Industry topic error: {str(exc)}",



        )











@app.post("/api/student/visual-lesson")



async def student_visual_lesson(payload: dict):



    """



    Create a generic FORGE visual-learning storyboard from Topic Intelligence.







    This endpoint does not contain topic-specific animation logic.



    The supplied Topic Intelligence is passed to the generic planner,



    which returns a renderer-ready scene structure.



    """







    if not isinstance(payload, dict):



        raise HTTPException(



            status_code=400,



            detail="Request body must be a JSON object."



        )







    topic = str(payload.get("topic", "")).strip()



    topic_intelligence = payload.get("topic_intelligence")







    if not topic:



        raise HTTPException(



            status_code=400,



            detail="Topic is required."



        )







    if not isinstance(topic_intelligence, dict):



        raise HTTPException(



            status_code=400,



            detail="topic_intelligence must be an object."



        )







    language = str(



        payload.get("language", "en") or "en"



    ).strip()







    difficulty = str(



        payload.get("difficulty", "intermediate") or "intermediate"



    ).strip()







    topic_data = dict(topic_intelligence)



    topic_data.setdefault("topic", topic)







    try:



        planner = get_animation_planner()







        lesson = planner.create_lesson(



            topic_data=topic_data,



            language=language,



            difficulty=difficulty,



        )







        return {



            "status": "success",



            "project": "FORGE",



            "topic": topic,



            "lesson": lesson,



        }







    except HTTPException:



        raise







    except Exception as exc:



        print(f"[VISUAL LESSON ERROR] {exc}")



        raise HTTPException(



            status_code=500,



            detail=f"Visual lesson generation failed: {exc}"



        )











@app.post("/api/student/visual-lesson/render")



def student_visual_lesson_render(payload: dict):



    """Queue a semantic visual lesson render and return immediately.







    The browser polls /visual-lesson/status/{job_id}; Manim never blocks



    the initial HTTP request.



    """



    if not isinstance(payload, dict):



        raise HTTPException(status_code=400, detail="Request body must be a JSON object.")







    topic = str(payload.get("topic", "")).strip()



    if not topic:



        raise HTTPException(status_code=400, detail="Topic is required.")







    topic_intelligence = payload.get("topic_intelligence")



    if not isinstance(topic_intelligence, dict):



        raise HTTPException(status_code=400, detail="topic_intelligence must be an object.")







    language = str(payload.get("language", "en") or "en").strip()



    difficulty = str(payload.get("difficulty", "intermediate") or "intermediate").strip()



    topic_data = dict(topic_intelligence)



    topic_data.setdefault("topic", topic)







    job_id = uuid4().hex[:12]



    _set_visual_job(job_id, status="queued", progress=2, message="Visual lesson queued.", topic=topic)



    _VISUAL_EXECUTOR.submit(_run_visual_job, job_id, topic, topic_data, language, difficulty)







    return {



        "status": "queued",



        "project": "FORGE",



        "job_id": job_id,



        "topic": topic,



        "message": "Visual lesson generation started."



    }











@app.get("/api/student/visual-lesson/status/{job_id}")



def student_visual_lesson_status(job_id: str):



    with _VISUAL_JOBS_LOCK:



        job = _VISUAL_JOBS.get(job_id)



    if not job:



        raise HTTPException(status_code=404, detail="Visual lesson job not found.")



    return {"project": "FORGE", "job_id": job_id, **job}











@app.get("/api/student/industry-resources")



def student_industry_resources(



    role: str = Query(..., min_length=1),



    topic: str = Query(..., min_length=1),



    horizon: str = Query("emerging", min_length=1),



):



    if industry_pulse_service is None:



        raise HTTPException(status_code=503, detail="Industry Pulse service is not available.")



    try:



        return industry_pulse_service.resources(role=role, topic=topic, horizon=horizon)



    except Exception as exc:



        raise HTTPException(status_code=500, detail=f"Industry resource error: {exc}")











# ============================================================



# ELLA AI ASSISTANT



# ============================================================







@app.get("/api/assistant/health")



def ella_health():



    try:



        return ella_service.health()



    except Exception as exc:



        raise HTTPException(status_code=503, detail=f"ELLA health check failed: {exc}")











@app.post("/api/assistant/chat")



async def ella_chat(payload: dict):



    try:



        message = str(payload.get("message", "")).strip()



        history = payload.get("history", [])



        page = payload.get("page")



        role = payload.get("role")



        topic = payload.get("topic")







        if not message:



            raise HTTPException(status_code=400, detail="Message cannot be empty.")



        if not isinstance(history, list):



            history = []







        return ella_service.chat(message=message, history=history, page=page, role=role, topic=topic)







    except HTTPException:



        raise



    except Exception as exc:



        print(f"[ELLA CHAT ERROR] {exc}")



        raise HTTPException(status_code=500, detail=f"ELLA could not process the request: {str(exc)[:300]}")











@app.post("/api/assistant/vision")



async def ella_vision(file: UploadFile = File(...), prompt: str = Form(""), page: str = Form(""), role: str = Form(""), topic: str = Form("")):



    try:



        image_bytes = await file.read()



        if not image_bytes:



            raise HTTPException(status_code=400, detail="Image is empty.")



        return ella_service.analyze_image(image_bytes=image_bytes, filename=file.filename or "image.jpg", content_type=file.content_type or "image/jpeg", prompt=prompt)



    except HTTPException:



        raise



    except Exception as exc:



        print(f"[ELLA VISION ERROR] {exc}")



        raise HTTPException(status_code=500, detail=f"ELLA could not analyze the image: {str(exc)[:300]}")











@app.post("/api/assistant/document")



async def ella_document(



    file: UploadFile = File(...),



    prompt: str = Form(""),



    role: str = Form(""),



    topic: str = Form(""),



    max_words: str = Form("360"),



):



    """Read a study PDF and answer questions from its actual contents.







    Text PDFs use pypdf/PyMuPDF extraction. If the PDF is scanned and PyMuPDF



    is available, the first pages are rendered and passed through FORGE vision.



    """



    try:



        raw = await file.read()



        if not raw:



            raise HTTPException(status_code=400, detail="PDF is empty.")







        filename = file.filename or "document.pdf"



        if not (filename.lower().endswith(".pdf") or (file.content_type or "").lower() == "application/pdf"):



            raise HTTPException(status_code=400, detail="Please upload a PDF file.")







        try:



            word_limit = max(120, min(int(max_words or 360), 1000))



        except Exception:



            word_limit = 360







        extracted = ""



        page_count = 0



        extraction_method = ""







        # Prefer PyMuPDF because it handles more real-world PDFs reliably.



        try:



            import pymupdf



            doc = pymupdf.open(stream=raw, filetype="pdf")



            page_count = len(doc)



            chunks = []



            for i, page in enumerate(doc):



                text = (page.get_text("text") or "").strip()



                if text:



                    chunks.append(f"[Page {i+1}]\n{text}")



            extracted = "\n\n".join(chunks)



            extraction_method = "pymupdf"



        except Exception:



            pass







        if extracted:



            # Keep the LLM request safely below the Groq TPM limit.



            extracted = extracted[:18000]



            message = f"""You are FORGE's document tutor.



Current topic: {topic or 'Study document'}



Student request: {prompt.strip() or 'Read the uploaded PDF and explain the important question/concept clearly.'}







PDF CONTENT:



{extracted}







Rules:



\\- Answer using the uploaded PDF content as the primary source.



\\- If the PDF contains a question, solve that question rather than merely summarizing it.



\\- Mention the page number when it helps the student locate the answer.



\\- Match the student's language; use Hinglish when appropriate.



\\- Maximum {word_limit} words.



\\- Use short headings and bullets when useful.



\\- Do not invent facts that are not supported by the PDF."""



            result = ella_service.chat(message=message, history=[], page="Ask FORGE · PDF", role=role or None, topic=topic or None)



            result.update({"filename": filename, "pages": page_count, "extraction_method": extraction_method})



            return result







        # Scanned/image-only fallback: render a small number of pages and ask vision to read them.



        try:



            import pymupdf



            doc = pymupdf.open(stream=raw, filetype="pdf")



            page_answers = []



            for i, page in enumerate(list(doc)[:3]):



                pix = page.get_pixmap(matrix=pymupdf.Matrix(1.15, 1.15), alpha=False)



                page_prompt = prompt.strip() or "Read this PDF page carefully, extract the visible question/content, and explain the answer for a student."



                page_prompt += f" This is page {i+1} of the uploaded PDF."



                result = ella_service.analyze_image(



                    image_bytes=pix.tobytes("png"),



                    filename=f"{filename}#page-{i+1}.png",



                    content_type="image/png",



                    prompt=page_prompt,



                    role=role or None,



                    topic=topic or None,



                )



                msg = str(result.get("message") or "").strip()



                if msg:



                    page_answers.append(f"Page {i+1}: {msg}")



            if page_answers:



                combined = "\n\n".join(page_answers)



                result = ella_service.chat(



                    message=f"Synthesize these page analyses into one direct answer to: {prompt.strip() or 'Explain the uploaded PDF.'}\n\n{combined}\n\nMaximum {word_limit} words.",



                    history=[], page="Ask FORGE · PDF", role=role or None, topic=topic or None,



                )



                result.update({"filename": filename, "pages": page_count or len(page_answers), "extraction_method": "vision_pages"})



                return result



        except Exception as exc:



            print(f"[ELLA PDF VISION ERROR] {exc}")







        raise HTTPException(status_code=422, detail="This PDF appears to contain no readable text. Install PyMuPDF (pip install pymupdf) for scanned-PDF vision support, or upload a clearer PDF/image.")







    except HTTPException:



        raise



    except Exception as exc:



        print(f"[ELLA DOCUMENT ERROR] {exc}")



        raise HTTPException(status_code=500, detail="FORGE could not process the PDF.")











@app.post("/api/assistant/transcribe")



async def ella_transcribe(file: UploadFile = File(...), language: str = Form("")):



    try:



        audio_bytes = await file.read()



        if not audio_bytes:



            raise HTTPException(status_code=400, detail="Audio is empty.")



        return ella_service.transcribe(audio_bytes=audio_bytes, filename=file.filename or "recording.webm", language=language or None)



    except HTTPException:



        raise



    except Exception as exc:



        print(f"[ELLA STT ERROR] {exc}")



        raise HTTPException(status_code=500, detail="ELLA could not transcribe the audio.")











# ============================================================



\
# ============================================================
@app.get("/api/organization/workforce/overview")

def organization_workforce_overview():

    """

    Organization Command Center overview powered by

    the integrated Role Radar workforce + job datasets.

    """

    try:

        return get_workforce_overview()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce overview error: {str(exc)}"

        )





@app.get("/api/organization/workforce/transformation")

def organization_workforce_transformation():

    """

    Dedicated transformation endpoint so the dashboard can request

    the time-series independently from the broader overview payload.

    """

    try:

        return get_workforce_transformation()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce transformation error: {str(exc)}"

        )





@app.get("/api/organization/workforce/metrics")

def organization_workforce_metrics():

    """

    Core workforce KPIs for the HR/Admin dashboard.

    """

    try:

        return get_workforce_metrics()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce metrics error: {str(exc)}"

        )





@app.get("/api/organization/workforce/market")

def organization_workforce_market():

    """

    Market/job demand metrics from Role Radar.

    """

    try:

        return get_market_metrics()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce market error: {str(exc)}"

        )





@app.get("/api/organization/workforce/roles")

def organization_workforce_roles():

    """

    Most represented workforce roles.

    """

    try:

        return get_role_distribution()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce role distribution error: {str(exc)}"

        )





@app.get("/api/organization/workforce/skills")

def organization_workforce_skills():

    """

    Most represented workforce skills.

    """

    try:

        return get_skill_distribution()

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"Workforce skill distribution error: {str(exc)}"

        )





# ============================================================
# STARTUP



# ============================================================







@app.on_event("startup")



async def startup_event():







    print("\n" + "=" * 75)



    print("FORGE API STARTED")



    print("=" * 75)







    print("\nINTELLIGENCE PIPELINE")







    print(



        "  WORKTRACE      → Observe work"



    )







    print(



        "  SKILL SHADOW   → Detect capability loss"



    )







    print(



        "  WORKFOLD       → Reconfigure Human-AI work"



    )







    print(



        "  LATTICE        → Preserve capability"



    )







    print(



        "  INTELLIGENCE   → Connect the complete pipeline"



    )







    print("\nCORE ENDPOINTS")







    print(



        "  /api/health"



    )







    print(



        "  /api/student/visual-lesson"



    )







    print(



        "  /api/student/visual-lesson/render"



    )







    print(



        "  /api/student/visuals/*\\<*&#x66;ilename>"



    )







    print(



        "  /api/intelligence/occupations"



    )







    print(



        "  /api/intelligence/occupation"



    )







    print(



        "  /api/intelligence/scenario"



    )







    print(



        "  /api/intelligence/redesign"



    )







    print(



        "  /api/intelligence/preservation"



    )







    print(



        "  /api/intelligence/complete"



    )







    print("  /api/assistant/health")



    print("  /api/assistant/chat")



    print("  /api/assistant/vision")



    print("  /api/assistant/document")



    print("  /api/assistant/transcribe")







    print("\nFORGE is ready.")



    print("=" * 75 + "\n")











# ============================================================



# LOCAL DEVELOPMENT



# ============================================================







if __name__ == "__main__":







    import uvicorn







    uvicorn.run(



        "backend.api.main:app",



        host="127.0.0.1",



        port=8000,



        reload=True



    )