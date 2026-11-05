import { Component, Fragment, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  AlertCircle,
  CheckCircle2,
  Clock3,
  FileText,
  Loader2,
  Send,
  ShieldCheck,
  RotateCcw,
  Brain,
  Cpu,
  Database,
  Network,
  Sparkles,
  Target,
  UserRound,
  Workflow,
  GraduationCap,
  Building2,
  BriefcaseBusiness,
  TrendingUp,
  CalendarDays,
  Check,
  ChevronLeft,
  BookOpen,
  ExternalLink,
  PlayCircle,
  Trophy,
  CalendarCheck2,
  Plus,
} from "lucide-react";

import {
  BrowserRouter,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  getCompleteAnalysis,
  getOccupationIntelligence,
  getOccupations,
  redesignWorkforce,
  simulateFutureWorkforce,
  generateLatticePractice,
} from "./services/api";

import "./App.css";
import EllaAssistant from "./components/ella/EllaAssistant";
import NativeVisualLearn from "./components/NativeVisualLearn/NativeVisualLearn";


const FORGE_STUDENT_CSS = `\n.forge-student-page{min-height:100vh;background:radial-gradient(circle at 12% 8%,rgba(255,255,255,.055),transparent 28%),radial-gradient(circle at 88% 78%,rgba(255,255,255,.04),transparent 30%),#070807;color:#f5f6f4;padding:34px 24px 70px}.forge-student-shell{width:min(1060px,100%);margin:0 auto}.student-topbar{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:42px}.student-back{border:0;background:transparent;color:rgba(255,255,255,.52);display:inline-flex;align-items:center;gap:8px;padding:7px 0;cursor:pointer;font:inherit;font-size:12px}.student-back:hover{color:#fff;transform:translateX(-3px)}.student-brand-mini{display:inline-flex;align-items:center;gap:9px;color:rgba(255,255,255,.48);font-size:10px;font-weight:800;letter-spacing:.15em}.student-brand-mini strong{color:#fff}.student-progress-label{color:rgba(255,255,255,.4);font-size:10px;font-weight:800;letter-spacing:.16em}.student-progress{height:2px;background:rgba(255,255,255,.08);overflow:hidden;margin-bottom:55px}.student-progress span{display:block;height:100%;background:#fff;transition:width .5s cubic-bezier(.2,.8,.2,1)}.student-step-eyebrow{display:inline-flex;align-items:center;gap:9px;color:rgba(255,255,255,.45);font-size:10px;font-weight:800;letter-spacing:.17em}.student-step-eyebrow span{width:24px;height:1px;background:rgba(255,255,255,.7)}.student-title{margin:17px 0 13px;max-width:820px;font-size:clamp(42px,6.3vw,72px);line-height:.96;letter-spacing:-.06em;font-weight:650}.student-title em{color:rgba(255,255,255,.38);font-style:normal}.student-description{max-width:650px;color:rgba(255,255,255,.53);line-height:1.7;font-size:14px;margin:0}.student-content{margin-top:43px}.student-question-grid{display:grid;gap:30px}.student-question{animation:studentFadeUp .42s ease both}@keyframes studentFadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}.student-question-head{display:flex;align-items:baseline;justify-content:space-between;gap:15px;margin-bottom:12px}.student-question-head strong{font-size:13px}.student-question-head span{color:rgba(255,255,255,.3);font-size:9px;letter-spacing:.12em;font-weight:800}.student-options{display:flex;flex-wrap:wrap;gap:8px}.student-option{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.025);color:rgba(255,255,255,.6);border-radius:12px;padding:12px 14px;cursor:pointer;font:inherit;font-size:11px;transition:transform .2s,border-color .2s,background .2s,color .2s}.student-option:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.24);color:#fff}.student-option.selected{color:#080908;background:#fff;border-color:#fff;box-shadow:0 9px 25px rgba(255,255,255,.07)}.student-subjects{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}.student-subject{min-height:68px;text-align:left;border:1px solid rgba(255,255,255,.09);border-radius:14px;background:rgba(255,255,255,.022);color:rgba(255,255,255,.62);padding:13px;cursor:pointer;font:inherit;transition:transform .2s,border-color .2s,background .2s}.student-subject:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.2)}.student-subject.selected{border-color:rgba(255,255,255,.65);background:rgba(255,255,255,.09);color:#fff}.student-subject small{display:block;color:rgba(255,255,255,.28);font-size:8px;margin-bottom:8px;letter-spacing:.11em;font-weight:800}.student-subject strong{font-size:11px;font-weight:650}.student-selected-count{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-top:13px;color:rgba(255,255,255,.4);font-size:11px}.student-selected-count strong{color:#fff}.student-years{display:grid;grid-template-columns:repeat(5,1fr);gap:11px}.student-year{position:relative;min-height:175px;padding:22px 18px;text-align:left;border:1px solid rgba(255,255,255,.1);border-radius:18px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));color:#fff;cursor:pointer;transition:transform .23s,border-color .23s,background .23s,box-shadow .23s}.student-year:hover{transform:translateY(-5px);border-color:rgba(255,255,255,.27)}.student-year.selected{border-color:rgba(255,255,255,.72);background:rgba(255,255,255,.105);box-shadow:0 18px 50px rgba(0,0,0,.25);transform:translateY(-3px)}.student-year-index{color:rgba(255,255,255,.3);font-size:9px;font-weight:800;letter-spacing:.14em}.student-year-number{display:block;margin-top:27px;font-size:37px;letter-spacing:-.05em}.student-year-text{display:block;margin-top:6px;color:rgba(255,255,255,.38);font-size:9px}.student-year-check{position:absolute;right:15px;top:15px;width:23px;height:23px;display:grid;place-items:center;border-radius:50%;background:#fff;color:#070807}.student-levels{display:grid;gap:11px}.student-level-row{display:grid;grid-template-columns:1.1fr 2fr;gap:16px;align-items:center;padding:15px;border:1px solid rgba(255,255,255,.08);border-radius:15px;background:rgba(255,255,255,.022)}.student-level-row strong{font-size:12px}.student-level-row small{display:block;margin-top:4px;color:rgba(255,255,255,.32);font-size:9px}.student-level-options{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.student-level{border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.018);color:rgba(255,255,255,.48);border-radius:10px;padding:10px 7px;cursor:pointer;font:inherit;font-size:9px}.student-level.selected{background:#fff;border-color:#fff;color:#070807}.student-info{display:flex;align-items:flex-start;gap:10px;margin-top:20px;padding:14px 15px;border:1px solid rgba(255,255,255,.07);border-radius:13px;color:rgba(255,255,255,.4);font-size:10px;line-height:1.6;background:rgba(255,255,255,.018)}.student-info svg{flex:0 0 auto;color:rgba(255,255,255,.65)}.student-bottom{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-top:42px;padding-top:23px;border-top:1px solid rgba(255,255,255,.08)}.student-validation{color:rgba(255,255,255,.35);font-size:10px}.student-validation strong{color:#fff}.student-continue{display:inline-flex;align-items:center;gap:9px;border:0;border-radius:999px;background:#fff;color:#070807;padding:12px 18px 12px 20px;font:inherit;font-size:11px;font-weight:800;cursor:pointer;transition:transform .2s,box-shadow .2s,opacity .2s}.student-continue:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 13px 30px rgba(255,255,255,.1)}.student-continue:disabled{opacity:.25;cursor:not-allowed}.student-org-section{padding:108px 7vw 118px;background:radial-gradient(900px 420px at 50% -8%,rgba(139,70,255,.16),transparent 62%),radial-gradient(600px 420px at 8% 78%,rgba(91,45,190,.12),transparent 65%),#07050d;color:#f7f4ff;position:relative;overflow:hidden}.student-org-section:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(122,64,255,.055),transparent 28%,transparent 72%,rgba(81,43,180,.06));pointer-events:none}.student-org-section:after{content:"";position:absolute;left:10%;right:10%;bottom:0;height:1px;background:linear-gradient(90deg,transparent,rgba(174,132,255,.35),transparent);pointer-events:none}.workspace-heading{max-width:880px;position:relative;z-index:1}.workspace-kicker{display:inline-flex;align-items:center;gap:10px;color:rgba(204,174,255,.72);font-size:10px;font-weight:800;letter-spacing:.2em}.workspace-kicker span{width:28px;height:1px;background:rgba(190,151,255,.7);box-shadow:0 0 10px rgba(157,91,255,.55)}.workspace-heading h2{margin:19px 0 17px;font-size:clamp(42px,5.3vw,76px);line-height:.96;letter-spacing:-.06em;font-weight:680;color:#fff;text-shadow:0 0 30px rgba(140,83,255,.12)}.workspace-heading p{margin:0;max-width:760px;color:rgba(225,215,244,.64);line-height:1.72;font-size:14px}.workspace-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:48px;position:relative;z-index:1}.workspace-card{position:relative;min-height:410px;padding:31px;text-align:left;border:1px solid rgba(184,142,255,.18);border-radius:26px;background:linear-gradient(145deg,rgba(48,25,83,.54),rgba(16,11,27,.84) 58%,rgba(9,7,15,.94));color:#fff;cursor:pointer;overflow:hidden;isolation:isolate;transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .35s ease,box-shadow .35s ease,background .35s ease}.workspace-card:before{content:"";position:absolute;inset:-1px;background:radial-gradient(420px 180px at 18% 0%,rgba(167,96,255,.2),transparent 68%),radial-gradient(360px 260px at 90% 100%,rgba(91,42,205,.13),transparent 72%);z-index:-2;pointer-events:none}.workspace-card:after{content:"";position:absolute;left:28px;right:28px;top:0;height:1px;background:linear-gradient(90deg,transparent,rgba(202,164,255,.62),transparent);opacity:.65;z-index:-1}.workspace-card:hover{transform:translateY(-8px);border-color:rgba(193,149,255,.48);box-shadow:0 26px 80px rgba(46,17,91,.34),0 0 45px rgba(127,63,255,.12);background:linear-gradient(145deg,rgba(61,30,104,.63),rgba(15,10,26,.9) 62%,rgba(9,7,15,.96))}.workspace-number{position:absolute;right:27px;top:25px;color:rgba(202,169,255,.34);font-size:10px;letter-spacing:.18em;font-weight:800}.workspace-icon{width:57px;height:57px;display:grid;place-items:center;border:1px solid rgba(191,145,255,.28);border-radius:17px;background:linear-gradient(145deg,rgba(145,78,255,.15),rgba(255,255,255,.025));color:#eee3ff;box-shadow:inset 0 0 20px rgba(139,75,255,.09),0 0 25px rgba(129,65,255,.1);transition:transform .35s ease,box-shadow .35s ease,border-color .35s ease}.workspace-card:hover .workspace-icon{transform:translateY(-2px) scale(1.04);border-color:rgba(205,169,255,.52);box-shadow:inset 0 0 24px rgba(139,75,255,.16),0 0 30px rgba(129,65,255,.2)}.workspace-tag{margin-top:54px;color:rgba(191,153,255,.67);font-size:9px;font-weight:800;letter-spacing:.18em}.workspace-card h3{margin:10px 0 12px;font-size:36px;letter-spacing:-.045em;color:#fff}.workspace-card p{max-width:570px;margin:0;color:rgba(226,218,239,.62);font-size:13px;line-height:1.75}.workspace-features{display:flex;flex-wrap:wrap;gap:8px;margin-top:23px}.workspace-features span{padding:7px 10px;border:1px solid rgba(186,143,255,.16);border-radius:999px;background:rgba(144,77,255,.045);color:rgba(215,198,239,.58);font-size:9px;transition:border-color .25s ease,background .25s ease,color .25s ease}.workspace-card:hover .workspace-features span{border-color:rgba(190,147,255,.25);background:rgba(144,77,255,.07);color:rgba(232,219,250,.75)}.workspace-cta{display:inline-flex;align-items:center;gap:9px;margin-top:29px;color:#fff;font-size:11px;font-weight:800}.workspace-cta svg{transition:transform .25s ease,color .25s ease}.workspace-card:hover .workspace-cta svg{transform:translateX(5px);color:#caa2ff}
@media(max-width:850px){.student-subjects{grid-template-columns:repeat(2,1fr)}.student-years{grid-template-columns:repeat(2,1fr)}.student-year:last-child{grid-column:span 2}}@media(max-width:760px){.workspace-grid{grid-template-columns:1fr}.student-org-section{padding:70px 20px 78px}}@media(max-width:600px){.forge-student-page{padding:25px 16px 50px}.student-brand-mini{display:none}.student-subjects,.student-years{grid-template-columns:1fr}.student-year:last-child{grid-column:auto}.student-level-row{grid-template-columns:1fr}.student-bottom{flex-direction:column;align-items:stretch}.student-continue{justify-content:center}}
/* =========================================================
   FORGE STUDENT WORKSPACE — HACKATHON / EVALUATION SYSTEM
   Premium violet + indigo visual language. Scoped to student flow.
========================================================= */
.forge-student-route{
  background:#0e0a18 !important;
  color:#f7f3ff !important;
}
.forge-student-route .footer{
  display:none !important;
}
.forge-student-page{
  position:relative;
  isolation:isolate;
  min-height:100svh !important;
  box-sizing:border-box;
  padding:28px clamp(22px,4vw,64px) 56px !important;
  overflow:hidden;
  background:
    radial-gradient(900px 520px at 8% -4%,rgba(145,92,255,.20),transparent 62%),
    radial-gradient(760px 520px at 94% 16%,rgba(84,112,255,.12),transparent 64%),
    radial-gradient(760px 560px at 50% 108%,rgba(195,74,255,.09),transparent 70%),
    linear-gradient(135deg,#0d0917 0%,#110b1e 46%,#0b0a16 100%) !important;
}
.forge-student-page::before{
  content:"";
  position:absolute;
  inset:0;
  z-index:-2;
  pointer-events:none;
  opacity:.55;
  background-image:
    linear-gradient(rgba(183,148,255,.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(183,148,255,.055) 1px,transparent 1px);
  background-size:42px 42px;
  mask-image:linear-gradient(to bottom,rgba(0,0,0,.95),rgba(0,0,0,.72) 72%,transparent);
}
.forge-student-page::after{
  content:"";
  position:absolute;
  width:520px;height:520px;
  right:-230px;top:80px;
  border-radius:50%;
  z-index:-1;
  pointer-events:none;
  background:radial-gradient(circle,rgba(146,94,255,.13),transparent 68%);
  filter:blur(8px);
}
.forge-student-shell{
  width:min(1240px,100%) !important;
  margin:0 auto !important;
}
.student-topbar{
  position:relative;
  min-height:42px;
  margin-bottom:24px !important;
  padding:0 2px 18px;
  border-bottom:1px solid rgba(203,177,255,.10);
}
.student-back{
  color:rgba(239,230,255,.62) !important;
  font-size:12px !important;
  font-weight:700 !important;
  letter-spacing:.01em;
  transition:color .2s,transform .2s;
}
.student-back:hover{color:#fff !important}
.student-brand-mini{
  color:rgba(224,208,250,.58) !important;
  font-size:10px !important;
  letter-spacing:.18em !important;
}
.student-brand-mini strong{
  color:#fff !important;
  text-shadow:0 0 18px rgba(183,141,255,.35);
}
.student-progress-label{
  color:rgba(218,201,245,.55) !important;
  font-size:10px !important;
  letter-spacing:.17em !important;
}
.student-progress{
  height:4px !important;
  border-radius:99px !important;
  background:rgba(208,183,255,.09) !important;
  margin:0 0 54px !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.025);
}
.student-progress span{
  background:linear-gradient(90deg,#8c63ff 0%,#b36cff 48%,#63d7ff 100%) !important;
  box-shadow:0 0 18px rgba(153,98,255,.52);
  border-radius:99px;
}
.student-step-eyebrow{
  color:rgba(204,181,239,.70) !important;
  font-size:11px !important;
  letter-spacing:.19em !important;
}
.student-step-eyebrow span{
  width:34px !important;
  background:linear-gradient(90deg,#a66cff,#6fdcff) !important;
  box-shadow:0 0 14px rgba(150,92,255,.38);
}
.student-title{
  max-width:900px !important;
  margin:18px 0 15px !important;
  font-size:clamp(48px,6.1vw,82px) !important;
  line-height:.94 !important;
  letter-spacing:-.065em !important;
  font-weight:720 !important;
  text-wrap:balance;
  text-shadow:0 14px 45px rgba(0,0,0,.22);
}
.student-title em{
  color:transparent !important;
  background:linear-gradient(100deg,#d8c4ff 0%,#a77aff 48%,#79dfff 100%);
  -webkit-background-clip:text;
  background-clip:text;
}
.student-description{
  max-width:760px !important;
  color:rgba(224,211,242,.67) !important;
  font-size:14px !important;
  line-height:1.75 !important;
}
.student-content{
  margin-top:46px !important;
}
.student-question-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px !important}
.student-question:nth-child(4),
.student-question:nth-child(5),
.student-question:nth-child(7){grid-column:1 / -1}
.student-question:nth-child(1){background:linear-gradient(145deg,rgba(45,29,73,.70),rgba(17,12,29,.58))}
.student-question:nth-child(2){background:linear-gradient(145deg,rgba(25,38,64,.62),rgba(17,12,29,.58))}
.student-question:nth-child(3){background:linear-gradient(145deg,rgba(55,29,63,.64),rgba(17,12,29,.58))}
.student-question:nth-child(4){background:linear-gradient(145deg,rgba(45,28,74,.72),rgba(18,12,32,.60))}
.student-question:nth-child(5){background:linear-gradient(145deg,rgba(24,48,63,.62),rgba(17,12,29,.60))}
.student-question:nth-child(6){background:linear-gradient(145deg,rgba(53,32,67,.64),rgba(17,12,29,.58))}
.student-question:nth-child(7){background:linear-gradient(145deg,rgba(32,47,66,.62),rgba(17,12,29,.58))}
.student-question{
  position:relative;
  padding:21px 22px 22px;
  border:1px solid rgba(203,173,255,.11);
  border-radius:20px;
  background:
    linear-gradient(145deg,rgba(34,21,54,.64),rgba(17,12,29,.58));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 16px 42px rgba(4,1,12,.15);
  backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px);
}
.student-question::before{
  content:"";
  position:absolute;
  left:0;top:17px;bottom:17px;width:2px;
  border-radius:99px;
  background:linear-gradient(180deg,#a46cff,#65d8ff);
  opacity:.65;
}
.student-question-head{
  margin-bottom:15px !important;
  align-items:center !important;
}
.student-question-head strong{
  font-size:15px !important;
  letter-spacing:-.01em;
  color:#fff !important;
}
.student-question-head span{
  color:rgba(198,171,239,.40) !important;
  font-size:10px !important;
}
.student-options{
  gap:10px !important;
}
.student-option{
  position:relative;
  min-height:44px;
  padding:11px 17px !important;
  border:1px solid rgba(207,180,255,.13) !important;
  border-radius:13px !important;
  background:rgba(255,255,255,.025) !important;
  color:rgba(235,225,248,.69) !important;
  font-size:12px !important;
  font-weight:650 !important;
  letter-spacing:.005em;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.025);
}
.student-option:nth-child(4n+1){border-color:rgba(148,108,255,.18) !important}
.student-option:nth-child(4n+2){border-color:rgba(84,190,255,.16) !important}
.student-option:nth-child(4n+3){border-color:rgba(225,111,255,.16) !important}
.student-option:nth-child(4n){border-color:rgba(108,224,188,.14) !important}
.student-option:hover{
  transform:translateY(-3px) !important;
  color:#fff !important;
  border-color:rgba(209,179,255,.48) !important;
  background:linear-gradient(135deg,rgba(142,91,255,.16),rgba(82,196,255,.07)) !important;
  box-shadow:0 12px 25px rgba(77,36,125,.20),0 0 0 1px rgba(190,150,255,.06);
}
.student-option.selected{
  color:#fff !important;
  border-color:rgba(188,145,255,.85) !important;
  background:linear-gradient(135deg,rgba(133,83,255,.72),rgba(89,181,255,.48)) !important;
  box-shadow:0 10px 30px rgba(99,51,184,.34),inset 0 1px 0 rgba(255,255,255,.17),0 0 0 1px rgba(209,180,255,.12);
  transform:translateY(-2px);
}
.student-option.selected::after{
  content:"✓";
  margin-left:10px;
  font-weight:900;
  color:rgba(255,255,255,.9);
}
.student-subjects{
  grid-template-columns:repeat(4,minmax(0,1fr)) !important;
  gap:12px !important;
}
.student-subject{
  min-height:86px !important;
  padding:16px !important;
  border-radius:17px !important;
  border-color:rgba(196,167,246,.12) !important;
  background:linear-gradient(145deg,rgba(35,22,54,.70),rgba(17,12,28,.64)) !important;
  color:rgba(237,227,249,.72) !important;
}
.student-subject:nth-child(4n+1){box-shadow:inset 0 1px 0 rgba(156,104,255,.12)}
.student-subject:nth-child(4n+2){box-shadow:inset 0 1px 0 rgba(77,195,255,.11)}
.student-subject:nth-child(4n+3){box-shadow:inset 0 1px 0 rgba(226,108,255,.11)}
.student-subject:nth-child(4n){box-shadow:inset 0 1px 0 rgba(97,222,188,.10)}
.student-subject:hover{
  transform:translateY(-4px) !important;
  border-color:rgba(205,177,255,.42) !important;
  background:linear-gradient(145deg,rgba(56,33,83,.78),rgba(21,14,37,.78)) !important;
}
.student-subject.selected{
  border-color:rgba(170,130,255,.72) !important;
  background:linear-gradient(145deg,rgba(103,64,170,.58),rgba(38,37,74,.75)) !important;
  color:#fff !important;
  box-shadow:0 14px 36px rgba(72,31,135,.25),inset 0 1px 0 rgba(255,255,255,.10);
}
.student-subject small{
  color:rgba(192,165,233,.46) !important;
  font-size:9px !important;
}
.student-subject strong{
  font-size:13px !important;
}
.student-years{
  gap:14px !important;
}
.student-year{
  min-height:190px !important;
  padding:22px !important;
  border-radius:20px !important;
  border-color:rgba(200,171,249,.13) !important;
  background:linear-gradient(145deg,rgba(38,24,60,.70),rgba(17,12,29,.72)) !important;
}
.student-year:nth-child(1){background:linear-gradient(145deg,rgba(56,39,89,.52),rgba(17,12,29,.76)) !important}
.student-year:nth-child(2){background:linear-gradient(145deg,rgba(35,57,83,.50),rgba(17,12,29,.76)) !important}
.student-year:nth-child(3){background:linear-gradient(145deg,rgba(63,36,78,.54),rgba(17,12,29,.76)) !important}
.student-year:nth-child(4){background:linear-gradient(145deg,rgba(30,69,70,.40),rgba(17,12,29,.76)) !important}
.student-year:nth-child(5){background:linear-gradient(145deg,rgba(69,39,70,.46),rgba(17,12,29,.76)) !important}
.student-year:hover{
  transform:translateY(-6px) !important;
  border-color:rgba(208,179,255,.42) !important;
  box-shadow:0 18px 50px rgba(40,17,72,.28) !important;
}
.student-year.selected{
  border-color:rgba(190,149,255,.82) !important;
  box-shadow:0 20px 55px rgba(73,31,137,.30),0 0 0 1px rgba(207,178,255,.08) !important;
  background:linear-gradient(145deg,rgba(113,69,182,.55),rgba(27,28,58,.86)) !important;
}
.student-year-number{
  margin-top:30px !important;
  font-size:43px !important;
}
.student-year-text{
  color:rgba(218,200,238,.47) !important;
  font-size:10px !important;
}
.student-levels{gap:13px !important}
.student-level-row{
  padding:17px !important;
  border-radius:18px !important;
  border-color:rgba(203,175,247,.11) !important;
  background:linear-gradient(145deg,rgba(35,22,55,.68),rgba(16,11,28,.72)) !important;
}
.student-level-row strong{font-size:13px !important;color:#fff}
.student-level-row small{font-size:10px !important;color:rgba(215,198,234,.43)}
.student-level-options{gap:9px !important}
.student-level{
  min-height:42px;
  border-radius:12px !important;
  color:rgba(232,220,247,.60) !important;
  border-color:rgba(198,169,244,.12) !important;
  background:rgba(255,255,255,.025) !important;
  font-size:10px !important;
  font-weight:700 !important;
}
.student-level:hover{
  transform:translateY(-2px);
  border-color:rgba(203,169,255,.38) !important;
  color:#fff !important;
}
.student-level.selected{
  color:#fff !important;
  background:linear-gradient(135deg,rgba(128,80,220,.76),rgba(77,166,224,.50)) !important;
  border-color:rgba(192,153,255,.72) !important;
  box-shadow:0 10px 24px rgba(71,33,127,.25);
}
.student-info{
  border-color:rgba(187,149,241,.13) !important;
  border-radius:16px !important;
  background:linear-gradient(135deg,rgba(61,38,89,.35),rgba(21,14,35,.42)) !important;
  color:rgba(222,206,240,.60) !important;
  font-size:11px !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.03);
}
.student-info svg{color:#b98cff !important}
.student-selected-count{
  color:rgba(216,198,237,.44) !important;
  font-size:11px !important;
}
.student-selected-count strong{color:#fff !important}
.student-bottom{
  margin-top:48px !important;
  padding-top:25px !important;
  border-top:1px solid rgba(204,177,247,.11) !important;
}
.student-validation{
  color:rgba(211,194,232,.48) !important;
  font-size:11px !important;
}
.student-validation strong{color:#fff !important}
.student-continue{
  min-height:46px;
  padding:13px 20px 13px 22px !important;
  border:1px solid rgba(224,208,255,.14) !important;
  border-radius:14px !important;
  background:linear-gradient(135deg,#f1eaff,#d5c0ff) !important;
  color:#1a1027 !important;
  font-size:12px !important;
  box-shadow:0 12px 32px rgba(123,69,197,.22);
}
.student-continue:hover:not(:disabled){
  transform:translateY(-3px) !important;
  box-shadow:0 17px 38px rgba(133,75,215,.32) !important;
}
.student-continue:disabled{
  opacity:.32 !important;
}
.student-content > .student-info{
  margin-top:0 !important;
}

/* Assessment inherits the same visual language */
.forge-assessment{margin-top:42px !important}
.assessment-progress-wrap{
  height:6px !important;
  background:rgba(206,180,255,.08) !important;
  border-radius:99px !important;
}
.assessment-progress-wrap span{
  background:linear-gradient(90deg,#8c63ff,#c66dff,#67d9ff) !important;
  box-shadow:0 0 18px rgba(145,89,255,.45);
}
.assessment-structure{
  grid-template-columns:repeat(3,1fr) !important;
  gap:12px !important;
}
.assessment-structure-item,
.assessment-breakdown-card,
.assessment-card,
.assessment-result{
  border-color:rgba(204,175,249,.12) !important;
  background:linear-gradient(145deg,rgba(36,23,56,.72),rgba(16,11,28,.78)) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 16px 42px rgba(3,1,10,.14);
}
.assessment-structure-item{
  border-radius:15px !important;
}
.assessment-structure-item:nth-child(1){border-top-color:rgba(133,99,255,.55) !important}
.assessment-structure-item:nth-child(2){border-top-color:rgba(94,205,255,.55) !important}
.assessment-structure-item:nth-child(3){border-top-color:rgba(225,112,255,.55) !important}
.assessment-structure-item.active{
  background:linear-gradient(145deg,rgba(93,57,151,.48),rgba(24,17,42,.82)) !important;
  border-color:rgba(193,151,255,.45) !important;
}
.assessment-card{
  border-radius:22px !important;
  padding:29px !important;
}
.assessment-card h2{
  font-size:clamp(25px,3vw,36px) !important;
  color:#fff !important;
}
.assessment-option{
  min-height:54px;
  border-radius:15px !important;
  border-color:rgba(202,174,245,.12) !important;
  background:rgba(255,255,255,.025) !important;
  color:rgba(236,225,248,.68) !important;
  font-size:12px !important;
}
.assessment-option:hover{
  transform:translateX(5px) !important;
  border-color:rgba(193,150,255,.45) !important;
  background:linear-gradient(135deg,rgba(130,79,218,.16),rgba(80,182,231,.06)) !important;
}
.assessment-option.selected{
  background:linear-gradient(135deg,rgba(130,80,220,.82),rgba(77,177,228,.52)) !important;
  border-color:rgba(196,158,255,.76) !important;
  color:#fff !important;
}
.assessment-option-key{
  border-color:rgba(204,175,247,.16) !important;
}
.assessment-type-badge{
  border-color:rgba(187,149,241,.18) !important;
  background:rgba(145,91,255,.08);
  color:rgba(216,191,242,.65) !important;
}
.assessment-nav button{
  min-height:44px;
  border-radius:13px !important;
  border-color:rgba(202,174,245,.13) !important;
  background:rgba(255,255,255,.035) !important;
}
.assessment-nav button.primary{
  background:linear-gradient(135deg,#e9ddff,#cbb1ff) !important;
  color:#1b1027 !important;
  border-color:transparent !important;
}
.generated-task{
  border:1px solid rgba(197,159,255,.14);
  border-radius:18px;
  background:linear-gradient(145deg,rgba(63,37,93,.35),rgba(17,11,29,.55));
  padding:18px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.03);
}

/* Keep the entire student flow edge-to-edge; no accidental white footer. */
.forge-student-route,
.forge-student-route #root,
.forge-student-route #root > div{
  min-height:100%;
}
.forge-student-route .forge-student-page + .footer{display:none !important}

@media(max-width:900px){
  .student-title{font-size:clamp(44px,9vw,68px) !important}
  .student-subjects{grid-template-columns:repeat(2,minmax(0,1fr)) !important}
  .student-years{grid-template-columns:repeat(2,minmax(0,1fr)) !important}
  .assessment-structure{grid-template-columns:1fr !important}
}
@media(max-width:620px){
  .forge-student-page{padding:22px 16px 42px !important}
  .student-topbar{margin-bottom:20px !important}
  .student-progress{margin-bottom:40px !important}
  .student-title{font-size:clamp(39px,12vw,56px) !important}
  .student-content{margin-top:34px !important}
  .student-question-grid{grid-template-columns:1fr !important}\n  .student-question:nth-child(4),.student-question:nth-child(5),.student-question:nth-child(7){grid-column:auto !important}\n  .student-question{padding:18px 16px}
  .student-options{gap:8px !important}
  .student-option{width:100%;justify-content:flex-start}
  .student-subjects,.student-years{grid-template-columns:1fr !important}
  .student-year:last-child{grid-column:auto !important}
  .student-bottom{gap:14px}
}

.forge-assessment{margin-top:42px}.assessment-meta{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:end;margin-bottom:18px}.assessment-subject{color:rgba(255,255,255,.42);font-size:10px;font-weight:800;letter-spacing:.14em}.assessment-question-count{color:rgba(255,255,255,.35);font-size:10px}.assessment-card{border:1px solid rgba(255,255,255,.1);border-radius:20px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));padding:25px;animation:studentFadeUp .35s ease both}.assessment-card h2{margin:0;max-width:850px;font-size:clamp(22px,3vw,32px);line-height:1.2;letter-spacing:-.035em;font-weight:620}.assessment-options{display:grid;gap:9px;margin-top:25px}.assessment-option{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:12px;width:100%;text-align:left;border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.025);color:rgba(255,255,255,.66);border-radius:13px;padding:13px 14px;cursor:pointer;font:inherit;font-size:12px;transition:transform .18s,border-color .18s,background .18s,color .18s}.assessment-option:hover{transform:translateX(3px);border-color:rgba(255,255,255,.24);color:#fff}.assessment-option.selected{background:#fff;border-color:#fff;color:#070807}.assessment-option-key{width:28px;height:28px;display:grid;place-items:center;border:1px solid rgba(255,255,255,.12);border-radius:8px;font-size:10px;font-weight:900}.assessment-option.selected .assessment-option-key{border-color:rgba(0,0,0,.12)}.assessment-progress-wrap{height:4px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;margin:0 0 28px}.assessment-progress-wrap span{display:block;height:100%;background:#fff;transition:width .35s ease}.assessment-context{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.assessment-context span{padding:6px 9px;border:1px solid rgba(255,255,255,.08);border-radius:999px;color:rgba(255,255,255,.38);font-size:9px}.assessment-nav{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:18px}.assessment-nav button{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.035);color:rgba(255,255,255,.62);border-radius:11px;padding:10px 13px;cursor:pointer;font:inherit;font-size:10px;font-weight:800}.assessment-nav button.primary{background:#fff;color:#070807;border-color:#fff}.assessment-nav button:disabled{opacity:.25;cursor:not-allowed}.assessment-structure{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:18px 0 24px}.assessment-structure-item{padding:12px 14px;border:1px solid rgba(255,255,255,.08);border-radius:12px;background:rgba(255,255,255,.025);display:flex;align-items:center;justify-content:space-between;gap:10px}.assessment-structure-item strong{font-size:18px;color:#fff}.assessment-structure-item span{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.42);font-weight:800}.assessment-structure-item.active{border-color:rgba(255,255,255,.45);background:rgba(255,255,255,.08)}.assessment-type-badge{display:inline-flex;padding:7px 9px;border:1px solid rgba(255,255,255,.12);border-radius:999px;color:rgba(255,255,255,.5);font-size:8px;font-weight:800;letter-spacing:.12em;margin-bottom:16px}.assessment-breakdown{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}.assessment-breakdown-card{padding:14px;border:1px solid rgba(255,255,255,.08);border-radius:12px;background:rgba(255,255,255,.025)}.assessment-breakdown-card strong{display:block;color:#fff;font-size:12px}.assessment-breakdown-card small{display:block;color:rgba(255,255,255,.4);font-size:10px;margin-top:6px}@media(max-width:700px){.assessment-structure,.assessment-breakdown{grid-template-columns:repeat(2,1fr)}}
.assessment-result{margin-top:25px;border:1px solid rgba(255,255,255,.1);border-radius:20px;background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.02));padding:26px}.assessment-result-score{font-size:58px;line-height:1;font-weight:700;letter-spacing:-.06em}.assessment-result-score span{font-size:15px;color:rgba(255,255,255,.35);letter-spacing:0}.assessment-breakdown{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:22px}.assessment-breakdown-card{padding:14px;border:1px solid rgba(255,255,255,.08);border-radius:13px;background:rgba(255,255,255,.02)}.assessment-breakdown-card strong{display:block;font-size:12px}.assessment-breakdown-card small{display:block;margin-top:5px;color:rgba(255,255,255,.35);font-size:9px}.assessment-empty{padding:25px;border:1px dashed rgba(255,255,255,.15);border-radius:16px;color:rgba(255,255,255,.45);font-size:12px}@media(max-width:700px){.assessment-meta{grid-template-columns:1fr}.assessment-breakdown{grid-template-columns:1fr}.assessment-card{padding:19px}}`;

const FORGE_HOME_CSS = `

/* =========================================================
   HOME — STUDENT / ORGANIZATION CARDS
   Only the home chooser is changed here.
========================================================= */
.forge-home-page .student-org-section{
  padding-left:5vw !important;
  padding-right:5vw !important;
  padding-bottom:92px !important;
}

.forge-home-page .workspace-grid{
  width:min(1420px,100%);
  margin-left:auto;
  margin-right:auto;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:26px;
}

.forge-home-page .workspace-card{
  min-height:420px !important;
  height:420px !important;
  padding:30px 31px !important;
  border-radius:24px !important;
  position:relative !important;
  overflow:hidden !important;
  isolation:isolate !important;
  text-align:left !important;
  background:
    linear-gradient(105deg,rgba(20,9,35,.97) 0%,rgba(18,8,31,.91) 42%,rgba(17,8,30,.56) 67%,rgba(10,5,19,.28) 100%) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.07),
    0 24px 75px rgba(32,8,63,.24) !important;
}

.forge-home-page .workspace-card::before{
  z-index:0 !important;
  background:
    radial-gradient(500px 240px at 78% 50%,rgba(126,63,235,.22),transparent 68%),
    linear-gradient(145deg,rgba(54,24,91,.44),rgba(11,6,20,.9) 72%) !important;
}

.forge-home-page .workspace-card::after{
  z-index:5 !important;
  left:28px !important;
  right:28px !important;
  top:0 !important;
  height:1px !important;
  background:linear-gradient(90deg,transparent,rgba(206,166,255,.58),transparent) !important;
}

.forge-home-page .workspace-card-art{
  position:absolute;
  z-index:1;
  top:0;
  right:0;
  width:49%;
  height:100%;
  pointer-events:none;
  overflow:hidden;
  opacity:1;
  transform:scale(1.02);
  transform-origin:right center;
}

.forge-home-page .workspace-card-art::after{
  content:"";
  position:absolute;
  inset:0;
  background:
    linear-gradient(90deg,
      rgba(12,5,22,1) 0%,
      rgba(12,5,22,.98) 10%,
      rgba(12,5,22,.86) 25%,
      rgba(12,5,22,.46) 43%,
      rgba(12,5,22,.10) 67%,
      transparent 100%),
    linear-gradient(180deg,
      rgba(12,5,22,.08) 0%,
      transparent 30%,
      rgba(8,4,16,.28) 100%);
  mix-blend-mode:normal;
}

.forge-home-page .workspace-card-art img{
  width:100%;
  height:100%;
  display:block;
  object-fit:cover;
  object-position:72% center;
  filter:saturate(.92) contrast(1.05);
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,rgba(0,0,0,.05) 8%,#000 30%,#000 100%);
  mask-image:linear-gradient(90deg,transparent 0%,rgba(0,0,0,.05) 8%,#000 30%,#000 100%);
}

.forge-home-page .workspace-card-shade{
  position:absolute;
  inset:0;
  z-index:2;
  pointer-events:none;
  background:
    radial-gradient(360px 250px at 84% 50%,rgba(122,57,230,.12),transparent 70%),
    linear-gradient(90deg,rgba(8,4,16,.10),transparent 52%,rgba(8,4,16,.12));
}

.forge-home-page .workspace-card-content{
  position:relative;
  z-index:4;
  width:50%;
  max-width:50%;
  min-width:0;
  height:100%;
  display:flex;
  flex-direction:column;
  align-items:flex-start;
}

.forge-home-page .workspace-card .workspace-icon{
  width:54px;
  height:54px;
  flex:0 0 auto;
}

.forge-home-page .workspace-card .workspace-tag{
  margin-top:32px;
}

.forge-home-page .workspace-card h3{
  margin:8px 0 8px;
  font-size:31px;
}

.forge-home-page .workspace-card p{
  max-width:100%;
  margin:0;
  font-size:12px;
  line-height:1.55;
}

.forge-home-page .workspace-features{
  width:100%;
  margin-top:auto;
  padding-top:14px;
  display:flex;
  flex-wrap:wrap;
  gap:7px;
  align-content:flex-start;
}

.forge-home-page .workspace-cta{
  margin-top:12px;
  white-space:nowrap;
}

.forge-home-page .workspace-number{
  z-index:6;
}

.forge-home-page .workspace-card:hover .workspace-card-art{
  opacity:1;
  transition:transform .65s cubic-bezier(.2,.8,.2,1),opacity .4s ease;
}
.forge-home-page .workspace-card-student:hover .workspace-card-art{
  transform:translateX(-3px) scale(1.02);
}

.forge-home-page .workspace-card-art{
  transition:transform .65s cubic-bezier(.2,.8,.2,1),opacity .4s ease;
}

@media(max-width:900px){
  .forge-home-page .workspace-grid{grid-template-columns:1fr;gap:18px}
  .forge-home-page .workspace-card{height:350px !important;min-height:350px !important}
}

@media(max-width:620px){
  .forge-home-page .student-org-section{
    padding-left:20px !important;
    padding-right:20px !important;
  }
  .forge-home-page .workspace-card{
    height:auto !important;
    min-height:420px !important;
  }
  .forge-home-page .workspace-card-content{
    width:76%;
  }
  .forge-home-page .workspace-card-art{
    width:72%;
  }
}



/* FINAL CARD LAYOUT — artwork stays behind the copy */
.forge-home-page .workspace-card-content{
  width:51% !important;
  max-width:51% !important;
}
.forge-home-page .workspace-card-art{
  width:49% !important;
  right:-1px !important;
}
.forge-home-page .workspace-card-student .workspace-card-content{
  width:48% !important;
  max-width:48% !important;
  padding-right:10px !important;
  box-sizing:border-box !important;
}
.forge-home-page .workspace-card-student .workspace-card-art{
  right:0 !important;
  width:52% !important;
  transform:none;
  transform-origin:right center;
}
.forge-home-page .workspace-card-student .workspace-card-art img{
  object-position:82% center !important;
}
.forge-home-page .workspace-card-student .workspace-features{
  max-width:calc(100% - 2px) !important;
  padding-right:2px !important;
  box-sizing:border-box !important;
}
.forge-home-page .workspace-card-student .workspace-features span{
  position:relative;
  z-index:6;
}
.forge-home-page .workspace-card-organization .workspace-card-art img{
  object-position:72% center !important;
}
.forge-home-page .workspace-card p{
  max-width:100% !important;
}
.forge-home-page .workspace-features{
  width:100% !important;
  max-width:100% !important;
  margin-top:auto !important;
  padding-top:14px !important;
  display:flex !important;
  flex-wrap:wrap !important;
  gap:7px !important;
}
.forge-home-page .workspace-features span{
  flex:0 0 auto;
  white-space:nowrap;
}
.forge-home-page .workspace-cta{
  margin-top:12px !important;
  white-space:nowrap;
}
@media(max-width:900px){
  .forge-home-page .workspace-card-content{
    width:52% !important;
    max-width:52% !important;
  }
  .forge-home-page .workspace-card-art{
    width:58% !important;
  }
}
@media(max-width:620px){
  .forge-home-page .workspace-card-content{
    width:76% !important;
    max-width:76% !important;
  }
  .forge-home-page .workspace-card-art{
    width:72% !important;
  }
  .forge-home-page .workspace-card-student .workspace-card-content{
    width:76% !important;
    max-width:76% !important;
    padding-right:0 !important;
  }
  .forge-home-page .workspace-card-student .workspace-card-art{
    width:72% !important;
    right:0 !important;
  }
}

/* =========================================================
   HOME — INTERACTIVE PROBLEM STORY
   Stage cards are independently clickable and reveal their own explanation.
========================================================= */

.forge-home-page .forge-problem-panel{
  display:grid !important;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr) !important;
  gap:24px !important;
  align-items:stretch !important;
  overflow:visible !important;
  border:0 !important;
  background:transparent !important;
  box-shadow:none !important;
}

.forge-home-page .forge-problem-card{
  position:relative !important;
  width:100% !important;
  min-width:0 !important;
  min-height:455px !important;
  padding:34px 34px 28px !important;
  margin:0 !important;
  border:1px solid rgba(180,130,255,.28) !important;
  border-radius:24px !important;
  text-align:left !important;
  font:inherit !important;
  color:#f8f4ff !important;
  overflow:hidden !important;
  background:
    linear-gradient(145deg,rgba(46,21,72,.78),rgba(11,6,22,.88)) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.07),
    0 20px 55px rgba(8,2,18,.30),
    0 0 0 1px rgba(168,100,255,.035) !important;
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  transition:transform .35s ease,border-color .35s ease,box-shadow .35s ease,background .35s ease;
}

.forge-home-page .forge-problem-card::before{
  content:"";
  position:absolute;
  inset:0;
  pointer-events:none;
  background:
    radial-gradient(500px 260px at 0% 0%,rgba(102,62,255,.20),transparent 66%),
    radial-gradient(420px 280px at 100% 100%,rgba(46,116,255,.08),transparent 70%);
  opacity:.9;
}

.forge-home-page .forge-problem-card.after-problem-card::before{
  background:
    radial-gradient(500px 260px at 100% 0%,rgba(187,73,255,.19),transparent 66%),
    radial-gradient(420px 280px at 0% 100%,rgba(80,65,255,.08),transparent 70%);
}

.forge-home-page .forge-problem-card.is-active{
  transform:translateY(-3px);
  border-color:rgba(174,120,255,.58) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.10),
    0 25px 70px rgba(31,8,61,.38),
    0 0 35px rgba(123,65,238,.10) !important;
}

/* =========================================================
   PROBLEM STORY — FOCUS / FLY-AWAY INTERACTION
   Clicking either panel brings it forward and sends the other
   panel outward. Colors remain within the FORGE purple theme,
   with a cooler blue-violet BEFORE state and warmer magenta
   AFTER state.
========================================================= */
.forge-home-page .forge-problem-panel{
  position:relative !important;
  transition:grid-template-columns .58s cubic-bezier(.2,.8,.2,1);
}

.forge-home-page .forge-problem-panel .forge-problem-card{
  cursor:pointer;
  will-change:transform,opacity,filter,width;
  transition:
    transform .62s cubic-bezier(.2,.86,.2,1),
    opacity .42s ease,
    filter .42s ease,
    width .58s cubic-bezier(.2,.8,.2,1),
    border-color .35s ease,
    box-shadow .45s ease,
    background .45s ease;
}

.forge-home-page .forge-problem-panel .forge-problem-card:focus-visible{
  outline:2px solid rgba(190,150,255,.75);
  outline-offset:4px;
}

/* The selected panel becomes the main story card. */
.forge-home-page .forge-problem-panel.has-focus{
  grid-template-columns:minmax(0,1fr) !important;
}

/* Remove the dismissed card from layout while it visually flies out. */
.forge-home-page .forge-problem-panel.has-focus .panel-dismissed{
  position:absolute !important;
  top:0;
  width:calc(50% - 12px) !important;
  min-width:0 !important;
  pointer-events:none;
  z-index:0;
}

/* BEFORE — cooler blue/violet theme */
.forge-home-page .forge-problem-panel .before-problem-card.panel-focused{
  width:100% !important;
  z-index:3;
  border-color:rgba(112,177,255,.58) !important;
  background:
    radial-gradient(650px 320px at 0% 0%,rgba(62,133,255,.16),transparent 65%),
    linear-gradient(145deg,rgba(42,28,83,.94),rgba(10,7,25,.98) 75%) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.12),
    0 30px 90px rgba(39,36,110,.38),
    0 0 55px rgba(81,126,255,.13) !important;
  transform:translateY(-6px) scale(1.008);
}

.forge-home-page .forge-problem-panel .before-problem-card.panel-focused::before{
  background:
    radial-gradient(650px 300px at 8% 0%,rgba(77,151,255,.24),transparent 67%),
    radial-gradient(450px 300px at 92% 100%,rgba(116,72,255,.12),transparent 72%);
}

/* AFTER — warmer magenta/violet theme */
.forge-home-page .forge-problem-panel .after-problem-card.panel-focused{
  width:100% !important;
  z-index:3;
  border-color:rgba(235,130,255,.64) !important;
  background:
    radial-gradient(650px 320px at 100% 0%,rgba(226,70,238,.17),transparent 65%),
    linear-gradient(145deg,rgba(67,25,88,.94),rgba(18,7,28,.98) 75%) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.12),
    0 30px 90px rgba(104,26,125,.40),
    0 0 55px rgba(226,76,241,.14) !important;
  transform:translateY(-6px) scale(1.008);
}

.forge-home-page .forge-problem-panel .after-problem-card.panel-focused::before{
  background:
    radial-gradient(650px 300px at 92% 0%,rgba(236,83,241,.24),transparent 67%),
    radial-gradient(450px 300px at 8% 100%,rgba(106,67,255,.12),transparent 72%);
}

/* Fly the non-selected card away. */
.forge-home-page .forge-problem-panel .panel-dismissed-left{
  left:0;
  transform:translateX(-118%) rotate(-5deg) scale(.92) !important;
  opacity:0 !important;
  filter:blur(5px) saturate(.7);
}

.forge-home-page .forge-problem-panel .panel-dismissed-right{
  right:0;
  transform:translateX(118%) rotate(5deg) scale(.92) !important;
  opacity:0 !important;
  filter:blur(5px) saturate(.7);
}

/* Keep the focused panel's internal content crisp. */
.forge-home-page .forge-problem-panel .panel-focused .forge-problem-card-copy,
.forge-home-page .forge-problem-panel .panel-focused .forge-process-row,
.forge-home-page .forge-problem-panel .panel-focused .forge-problem-detail{
  animation:forgeProblemFocusContent .52s cubic-bezier(.2,.8,.2,1) both;
}

@keyframes forgeProblemFocusContent{
  from{opacity:.55;transform:translateY(10px)}
  to{opacity:1;transform:translateY(0)}
}

/* On smaller screens, stack normally and only fade/slide the other card. */
@media(max-width:900px){
  .forge-home-page .forge-problem-panel.has-focus{
    grid-template-columns:1fr !important;
  }
  .forge-home-page .forge-problem-panel.has-focus .panel-dismissed{
    width:100% !important;
  }
}

.forge-home-page .problem-divider{ display:none !important; }

.forge-home-page .forge-problem-card-top,
.forge-home-page .forge-problem-card-copy,
.forge-home-page .forge-process-row,
.forge-home-page .forge-problem-detail{
  position:relative;
  z-index:2;
}

.forge-home-page .forge-problem-card-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
}

.forge-home-page .forge-problem-card-top .tiny-blue-dot{
  padding:7px 11px;
  border:1px solid rgba(94,157,255,.20);
  border-radius:999px;
  background:rgba(42,116,255,.08);
  box-shadow:0 0 18px rgba(53,119,255,.08);
}

.forge-home-page .forge-problem-card.after-problem-card .tiny-blue-dot{
  border-color:rgba(213,126,255,.22);
  background:rgba(174,72,255,.10);
}

.forge-home-page .forge-problem-index{
  color:rgba(201,169,255,.42);
  font-size:10px;
  font-weight:800;
  letter-spacing:.16em;
}

.forge-home-page .forge-problem-card-copy{ max-width:610px; }

.forge-home-page .forge-problem-card h2{
  margin:25px 0 12px !important;
  color:#fff !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
  font-size:clamp(27px,2.5vw,39px) !important;
  line-height:1.03 !important;
  letter-spacing:-.045em !important;
  font-weight:720 !important;
}

.forge-home-page .forge-problem-card p{
  max-width:590px !important;
  margin:0 !important;
  color:rgba(226,215,241,.68) !important;
  font-size:13px !important;
  line-height:1.7 !important;
}

.forge-home-page .forge-process-row{
  margin-top:36px !important;
  display:flex !important;
  align-items:center !important;
  gap:10px !important;
}

.forge-home-page .forge-process-button{
  appearance:none;
  -webkit-appearance:none;
  flex:1 1 0;
  min-width:0;
  padding:0;
  border:0;
  background:transparent;
  color:inherit;
  font:inherit;
  text-align:left;
  cursor:pointer;
  border-radius:15px;
  position:relative;
  z-index:3;
}

.forge-home-page .forge-process-button .process-box{
  min-height:86px !important;
  padding:17px 15px !important;
  border-radius:15px !important;
  border:1px solid rgba(178,116,241,.25) !important;
  background:linear-gradient(145deg,rgba(50,25,79,.72),rgba(15,8,27,.78)) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.045),
    0 8px 24px rgba(7,2,17,.16) !important;
  transition:transform .25s ease,border-color .25s ease,background .25s ease,box-shadow .25s ease;
}

.forge-home-page .forge-process-button:hover .process-box{
  transform:translateY(-4px);
  border-color:rgba(193,145,255,.60) !important;
  background:linear-gradient(145deg,rgba(73,37,111,.80),rgba(17,8,30,.82)) !important;
  box-shadow:0 12px 28px rgba(73,30,132,.22),inset 0 1px 0 rgba(255,255,255,.07) !important;
}

.forge-home-page .forge-process-button.is-selected .process-box{
  transform:translateY(-4px);
  border-color:rgba(121,188,255,.72) !important;
  background:linear-gradient(145deg,rgba(40,82,130,.48),rgba(17,20,38,.86)) !important;
  box-shadow:0 0 0 1px rgba(95,170,255,.12),0 14px 32px rgba(37,111,190,.20),inset 0 1px 0 rgba(255,255,255,.09) !important;
}

.forge-home-page .forge-problem-card.after-problem-card .forge-process-button.is-selected .process-box{
  border-color:rgba(235,151,255,.72) !important;
  background:linear-gradient(145deg,rgba(112,49,133,.48),rgba(28,13,39,.88)) !important;
  box-shadow:0 0 0 1px rgba(231,130,255,.12),0 14px 32px rgba(157,44,190,.20),inset 0 1px 0 rgba(255,255,255,.09) !important;
}

.forge-home-page .forge-process-row .process-arrow{
  flex:0 0 auto !important;
  color:#a66cff !important;
  font-size:15px !important;
  opacity:.9;
}

.forge-home-page .forge-problem-detail{
  margin-top:22px;
  padding:20px 20px 18px;
  border-radius:18px;
  animation:forgeProblemDetailIn .35s cubic-bezier(.2,.8,.2,1) both;
}

.forge-home-page .forge-problem-detail.before-detail{
  border:1px solid rgba(89,169,255,.30);
  background:
    linear-gradient(145deg,rgba(22,65,104,.48),rgba(8,18,31,.84));
  box-shadow:
    inset 0 1px 0 rgba(190,230,255,.08),
    0 15px 38px rgba(19,91,150,.15);
}

.forge-home-page .forge-problem-detail.after-detail{
  border:1px solid rgba(224,130,255,.30);
  background:
    linear-gradient(145deg,rgba(91,38,106,.48),rgba(26,9,35,.86));
  box-shadow:
    inset 0 1px 0 rgba(255,210,255,.08),
    0 15px 38px rgba(136,39,158,.15);
}

@keyframes forgeProblemDetailIn{
  from{opacity:0;transform:translateY(9px) scale(.985)}
  to{opacity:1;transform:translateY(0) scale(1)}
}

.forge-home-page .forge-detail-label{
  color:rgba(126,195,255,.88);
  font-size:8px;
  font-weight:900;
  letter-spacing:.18em;
}

.forge-home-page .after-detail .forge-detail-label{
  color:rgba(237,161,255,.88);
}

.forge-home-page .forge-problem-detail h3{
  margin:8px 0 8px;
  color:#fff;
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:17px;
  line-height:1.2;
  letter-spacing:-.025em;
}

.forge-home-page .forge-problem-detail p{
  color:rgba(235,239,248,.72) !important;
  font-size:11px !important;
  line-height:1.7 !important;
}

.forge-home-page .forge-detail-flow{
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:7px;
  margin-top:15px;
}

.forge-home-page .forge-detail-flow span{
  padding:6px 9px;
  border-radius:999px;
  font-size:8px;
  font-weight:800;
  letter-spacing:.08em;
}

.forge-home-page .before-detail .forge-detail-flow span{
  border:1px solid rgba(98,181,255,.25);
  background:rgba(65,154,237,.10);
  color:rgba(205,235,255,.82);
}

.forge-home-page .after-detail .forge-detail-flow span{
  border:1px solid rgba(231,143,255,.25);
  background:rgba(194,77,230,.10);
  color:rgba(250,220,255,.84);
}

.forge-home-page .forge-detail-flow i{
  color:#9d6bff;
  font-style:normal;
  font-size:10px;
}

.forge-home-page .forge-problem-note{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  margin-top:16px;
  color:rgba(210,193,230,.42);
  font-size:9px;
  letter-spacing:.08em;
}

.forge-home-page .forge-problem-note-dot{
  width:5px;
  height:5px;
  border-radius:50%;
  background:#9a62ff;
  box-shadow:0 0 12px rgba(154,98,255,.75);
}

@media(max-width:900px){
  .forge-home-page .forge-problem-panel{
    grid-template-columns:1fr !important;
    gap:18px !important;
  }

  .forge-home-page .forge-problem-card{
    min-height:0 !important;
  }
}

@media(max-width:600px){
  .forge-home-page .forge-problem-card{
    padding:25px 20px 23px !important;
  }

  .forge-home-page .forge-process-row{
    gap:6px !important;
  }

  .forge-home-page .forge-process-button .process-box{
    min-height:68px !important;
    padding:11px 8px !important;
  }

  .forge-home-page .forge-process-row .process-arrow{
    font-size:11px !important;
  }
}


`;


const FORGE_STUDENT_POLISH_CSS=`
/* =========================================================
   FORGE STUDENT EXPERIENCE — FINAL VISUAL POLISH
   Scoped: onboarding / assessment / scores / roadmap / learning / ask.
========================================================= */
.forge-student-page{background:
  radial-gradient(900px 520px at 10% -8%,rgba(143,91,255,.22),transparent 60%),
  radial-gradient(760px 520px at 94% 18%,rgba(55,148,255,.13),transparent 62%),
  linear-gradient(135deg,#0c0817 0%,#120b22 45%,#090711 100%) !important;
  background-attachment:fixed !important;
}
.forge-student-page:before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.55;background-image:linear-gradient(rgba(180,139,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(180,139,255,.045) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.75) 65%,transparent 100%)}
.forge-student-shell{position:relative;z-index:1;width:min(1180px,100%) !important}
.student-topbar{padding-top:2px !important;margin-bottom:28px !important}
.student-progress{height:5px !important;border-radius:999px !important;background:rgba(255,255,255,.055) !important;box-shadow:inset 0 1px rgba(255,255,255,.05);margin-bottom:42px !important}
.student-progress span{background:linear-gradient(90deg,#8058ff,#b55cff,#5fe4ff) !important;box-shadow:0 0 18px rgba(154,91,255,.55)}
.student-title{max-width:900px !important;font-size:clamp(46px,6.2vw,78px) !important;line-height:.92 !important;text-shadow:0 18px 60px rgba(90,45,180,.18)}
.student-title em{background:linear-gradient(90deg,#b06cff,#6edcff);-webkit-background-clip:text;background-clip:text;color:transparent !important;text-shadow:none}
.student-description{max-width:760px !important;color:rgba(232,222,248,.64) !important;font-size:14px !important}
.student-content{margin-top:36px !important}
.student-question-grid{display:grid !important;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px !important}
.student-question{padding:19px 20px 20px;border:1px solid rgba(194,151,255,.12);border-radius:18px;background:linear-gradient(145deg,rgba(38,23,60,.58),rgba(15,10,26,.58));box-shadow:inset 0 1px rgba(255,255,255,.045),0 16px 50px rgba(10,3,25,.18);transition:.28s ease}
.student-question:hover{transform:translateY(-3px);border-color:rgba(193,147,255,.3);box-shadow:0 22px 60px rgba(40,13,72,.22),0 0 30px rgba(126,78,255,.07)}
.student-question-head{margin-bottom:14px !important}.student-question-head strong{font-size:13px !important;color:#fff}.student-question-head span{color:#8e75bb !important}
.student-options{gap:8px !important}.student-option{border-color:rgba(194,153,255,.14) !important;background:rgba(255,255,255,.035) !important;color:rgba(239,231,250,.68) !important;border-radius:12px !important;min-height:42px;padding:11px 15px !important}.student-option:hover{border-color:rgba(191,147,255,.4) !important;background:rgba(144,78,255,.08) !important;color:#fff !important;box-shadow:0 8px 22px rgba(94,42,167,.12)}.student-option.selected{background:linear-gradient(135deg,#8c5cff,#bb63ff) !important;color:#fff !important;border-color:rgba(226,204,255,.65) !important;box-shadow:0 0 28px rgba(150,79,255,.22),inset 0 1px rgba(255,255,255,.25) !important}
.student-role-context{display:flex;align-items:center;gap:13px;padding:14px 16px;margin-bottom:16px;border:1px solid rgba(105,211,255,.16);border-radius:16px;background:linear-gradient(135deg,rgba(55,151,194,.08),rgba(139,75,255,.09));box-shadow:inset 0 1px rgba(255,255,255,.04)}
.student-role-context-icon{width:36px;height:36px;display:grid;place-items:center;border-radius:11px;color:#83e8ff;background:rgba(80,207,255,.08);border:1px solid rgba(98,221,255,.18)}
.student-role-context div:nth-child(2){display:grid;gap:4px;flex:1}.student-role-context small{font-size:8px;letter-spacing:.14em;color:rgba(218,201,246,.38);font-weight:900}.student-role-context strong{font-size:13px;color:#fff}.student-role-context>span{font-size:9px;color:#8fe7ff;font-weight:800;letter-spacing:.08em}
.student-subjects{grid-template-columns:repeat(3,minmax(0,1fr)) !important;gap:12px !important}.student-subject{position:relative;display:flex;align-items:center;gap:13px;min-height:92px !important;padding:15px 16px !important;border-radius:18px !important;border:1px solid rgba(197,153,255,.12) !important;background:linear-gradient(145deg,rgba(38,24,61,.62),rgba(12,9,21,.74)) !important;overflow:hidden;transition:.28s cubic-bezier(.2,.8,.2,1) !important}.student-subject:nth-child(3n+1){--subject-accent:#9b72ff}.student-subject:nth-child(3n+2){--subject-accent:#59dfff}.student-subject:nth-child(3n){--subject-accent:#ff82b8}.student-subject:before{content:"";position:absolute;inset:auto -20% -70% -20%;height:100px;background:radial-gradient(circle,var(--subject-accent),transparent 68%);opacity:.06;transition:.3s}.student-subject:hover{transform:translateY(-4px);border-color:color-mix(in srgb,var(--subject-accent) 48%,transparent) !important;box-shadow:0 18px 50px rgba(25,7,48,.28),0 0 26px color-mix(in srgb,var(--subject-accent) 10%,transparent)}.student-subject.selected{border-color:var(--subject-accent) !important;background:linear-gradient(145deg,color-mix(in srgb,var(--subject-accent) 15%,#1b112a),rgba(13,9,22,.82)) !important;box-shadow:0 0 30px color-mix(in srgb,var(--subject-accent) 14%,transparent),inset 0 1px rgba(255,255,255,.08)}.student-subject.recommended:after{content:"";position:absolute;top:0;left:18px;right:18px;height:1px;background:linear-gradient(90deg,transparent,var(--subject-accent),transparent);opacity:.55}.student-subject-icon{width:42px;height:42px;display:grid;place-items:center;flex:0 0 42px;border-radius:13px;color:var(--subject-accent);background:color-mix(in srgb,var(--subject-accent) 10%,transparent);border:1px solid color-mix(in srgb,var(--subject-accent) 22%,transparent);box-shadow:0 0 18px color-mix(in srgb,var(--subject-accent) 8%,transparent)}.student-subject-copy{min-width:0;text-align:left}.student-subject-copy small{margin:0 0 6px !important;color:color-mix(in srgb,var(--subject-accent) 70%,white) !important;font-size:7px !important}.student-subject-copy strong{font-size:12px !important;color:#fff !important}.student-subject-check{position:absolute;right:12px;top:12px;width:23px;height:23px;border-radius:50%;display:grid;place-items:center;color:#fff;background:var(--subject-accent);box-shadow:0 0 18px color-mix(in srgb,var(--subject-accent) 30%,transparent)}.student-selected-count{padding:13px 15px;margin-top:14px;border:1px solid rgba(177,132,255,.1);border-radius:13px;background:rgba(255,255,255,.025)}.student-selected-count span{display:flex;align-items:center;gap:7px}
.student-years{grid-template-columns:repeat(5,minmax(0,1fr)) !important;gap:12px !important}.student-year{min-height:188px !important;background:linear-gradient(145deg,rgba(42,24,65,.72),rgba(12,9,20,.72)) !important;border-color:rgba(190,148,255,.14) !important}.student-year:nth-child(1){--year:#ff8aa9}.student-year:nth-child(2){--year:#a77bff}.student-year:nth-child(3){--year:#6ce5ff}.student-year:nth-child(4){--year:#78e8b1}.student-year:nth-child(5){--year:#ffc66d}.student-year:hover,.student-year.selected{border-color:color-mix(in srgb,var(--year) 55%,transparent) !important;box-shadow:0 20px 55px rgba(18,6,34,.3),0 0 30px color-mix(in srgb,var(--year) 10%,transparent)}.student-year.selected{background:linear-gradient(145deg,color-mix(in srgb,var(--year) 13%,#1a1028),rgba(12,9,20,.8)) !important}.student-year-number{color:#fff}.student-year-text{color:color-mix(in srgb,var(--year) 65%,white) !important}
.student-levels{gap:12px !important}.student-level-row{grid-template-columns:1.05fr 1.7fr !important;padding:16px 18px !important;border-radius:18px !important;background:linear-gradient(145deg,rgba(36,23,57,.58),rgba(12,9,20,.66)) !important;border-color:rgba(191,146,255,.12) !important;transition:.25s ease}.student-level-row.has-selection{border-color:rgba(142,100,255,.3) !important;box-shadow:0 0 28px rgba(124,73,255,.08)}.student-level-heading{display:flex;align-items:center;gap:12px}.student-level-index{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:rgba(151,96,255,.1);color:#bd98ff;font-size:9px;font-weight:900}.student-level-row strong{font-size:13px !important;color:#fff}.student-level-options{gap:8px !important}.student-level{display:flex;align-items:center;justify-content:space-between;gap:6px;border-color:rgba(194,149,255,.13) !important;background:rgba(255,255,255,.03) !important;color:rgba(239,230,249,.58) !important;border-radius:12px !important;min-height:43px;padding:10px 12px !important}.student-level:hover{transform:translateY(-2px);border-color:rgba(181,137,255,.3) !important;color:#fff}.student-level.selected{background:linear-gradient(135deg,#7650dc,#b45dff) !important;color:#fff !important;border-color:rgba(226,201,255,.55) !important;box-shadow:0 0 24px rgba(135,73,255,.2)}
.student-info-accent{border-color:rgba(101,221,255,.13) !important;background:linear-gradient(135deg,rgba(77,196,231,.055),rgba(140,77,255,.055)) !important}
.student-bottom{margin-top:30px !important;padding-top:18px !important;border-top-color:rgba(196,150,255,.1) !important}.student-continue{background:linear-gradient(135deg,#9a62ff,#c45eff) !important;color:#fff !important;box-shadow:0 12px 32px rgba(126,63,236,.2) !important}.student-continue:hover:not(:disabled){box-shadow:0 18px 45px rgba(141,67,255,.28) !important}
/* assessment */
.assessment-structure{display:grid !important;grid-template-columns:repeat(3,1fr) !important;gap:12px !important}.assessment-structure-item{border-radius:16px !important;border-color:rgba(193,148,255,.13) !important;background:rgba(255,255,255,.025) !important;transition:.25s ease}.assessment-structure-item:nth-child(1){--a:#6de6ff}.assessment-structure-item:nth-child(2){--a:#a77aff}.assessment-structure-item:nth-child(3){--a:#ff7eae}.assessment-structure-item.active{border-color:color-mix(in srgb,var(--a) 55%,transparent) !important;background:color-mix(in srgb,var(--a) 9%,#130c20) !important;box-shadow:0 0 26px color-mix(in srgb,var(--a) 10%,transparent)}.assessment-structure-item strong{color:var(--a,#fff)}
.assessment-card-pro{position:relative !important;margin-top:14px;border-radius:24px !important;border-color:rgba(193,148,255,.16) !important;background:linear-gradient(145deg,rgba(31,20,48,.86),rgba(12,8,21,.9)) !important;box-shadow:0 28px 80px rgba(8,2,18,.3),inset 0 1px rgba(255,255,255,.05) !important;overflow:hidden}.assessment-card-pro:before{content:"";position:absolute;left:0;top:0;width:38%;height:2px;background:linear-gradient(90deg,#8c5cff,#5fe5ff,transparent);box-shadow:0 0 18px rgba(119,89,255,.45)}.assessment-question-kicker{display:flex;align-items:center;gap:8px;color:#bba0e7;font-size:9px;font-weight:900;letter-spacing:.13em;margin-bottom:12px}.assessment-live-dot{width:7px;height:7px;border-radius:50%;background:#66e8ff;box-shadow:0 0 12px #66e8ff;animation:assessmentPulse 1.8s ease-in-out infinite}@keyframes assessmentPulse{50%{opacity:.35;transform:scale(.7)}}.assessment-card-pro h2{font-size:clamp(23px,3vw,34px) !important;line-height:1.18 !important;max-width:880px !important}.assessment-option{min-height:56px !important;border-radius:14px !important;border-color:rgba(194,149,255,.11) !important;background:rgba(255,255,255,.025) !important;transition:.2s ease !important}.assessment-option:hover{transform:translateX(4px);border-color:rgba(173,126,255,.32) !important;background:rgba(143,77,255,.07) !important}.assessment-option.selected{border-color:#a66aff !important;background:linear-gradient(90deg,rgba(137,80,255,.17),rgba(84,205,255,.05)) !important;box-shadow:inset 3px 0 #a66aff,0 0 24px rgba(137,80,255,.09)}
/* scores */
.score-subject-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px}.score-subject-card{position:relative;overflow:hidden;padding:17px;border-radius:18px;border:1px solid rgba(255,255,255,.1);background:linear-gradient(145deg,rgba(31,21,48,.78),rgba(12,9,21,.82));transition:.25s ease}.score-subject-card:hover{transform:translateY(-3px);box-shadow:0 20px 50px rgba(14,4,27,.3)}.score-subject-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--score)}.score-strong{--score:#69e7a5;border-color:rgba(105,231,165,.18)}.score-developing{--score:#ffd16a;border-color:rgba(255,209,106,.18)}.score-priority{--score:#ff6f8f;border-color:rgba(255,111,143,.18)}.score-subject-top{display:flex;justify-content:space-between;align-items:center}.score-subject-state{font-size:7px;letter-spacing:.14em;font-weight:900;color:var(--score)}.score-subject-top b{font-size:22px;color:#fff}.score-subject-card h3{margin:12px 0 5px;font-size:14px}.score-subject-card p{margin:0;color:rgba(255,255,255,.4);font-size:9px}.score-subject-bar{height:6px;margin-top:14px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden}.score-subject-bar span{display:block;height:100%;border-radius:inherit;background:var(--score);box-shadow:0 0 14px color-mix(in srgb,var(--score) 45%,transparent);transition:width .8s cubic-bezier(.2,.8,.2,1)}.score-subject-card>small{display:block;margin-top:10px;color:rgba(255,255,255,.35);font-size:8px}.capability-signal-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.capability-signal-grid>div{display:flex;align-items:center;gap:8px;padding:12px 14px;border:1px solid rgba(255,255,255,.07);border-radius:13px;background:rgba(255,255,255,.025);font-size:9px;color:rgba(255,255,255,.45)}.capability-signal-grid strong{margin-left:auto;font-size:15px;color:#fff}.signal-dot{width:7px;height:7px;border-radius:50%}.signal-red{background:#ff6f8f;box-shadow:0 0 12px #ff6f8f}.signal-yellow{background:#ffd16a;box-shadow:0 0 12px #ffd16a}.signal-green{background:#69e7a5;box-shadow:0 0 12px #69e7a5}
/* roadmap */
.student-step-eyebrow + .student-title{}.generated-task{border-color:rgba(184,140,255,.13) !important;background:linear-gradient(145deg,rgba(36,22,59,.68),rgba(12,8,21,.72)) !important;box-shadow:inset 0 1px rgba(255,255,255,.045),0 18px 50px rgba(12,3,28,.16)}

/* roadmap motivation */
.roadmap-allocation-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:20px}.roadmap-allocation-card{position:relative;overflow:hidden;padding:18px;border:1px solid rgba(190,145,255,.12);border-radius:19px;background:linear-gradient(145deg,rgba(36,22,57,.7),rgba(11,8,19,.8));transition:.28s ease}.roadmap-allocation-card:hover{transform:translateY(-4px);border-color:rgba(180,128,255,.3);box-shadow:0 22px 55px rgba(37,9,67,.25)}.roadmap-allocation-card.top-priority{border-color:rgba(116,222,255,.3);background:linear-gradient(145deg,rgba(35,54,68,.42),rgba(30,15,49,.8));box-shadow:0 0 35px rgba(71,205,255,.06)}.roadmap-card-top{display:flex;justify-content:space-between;align-items:center}.roadmap-card-top span{font-size:8px;color:#a88bcf;font-weight:900;letter-spacing:.16em}.roadmap-card-top em{font-style:normal;font-size:7px;color:#6edfff;letter-spacing:.12em;font-weight:900}.roadmap-card-main{display:flex;align-items:flex-end;justify-content:space-between;gap:15px;margin-top:16px}.roadmap-card-main h3{margin:0;font-size:17px;letter-spacing:-.025em;color:#fff}.roadmap-card-main p{margin:5px 0 0;color:rgba(231,219,247,.4);font-size:8px}.roadmap-card-main>strong{font-size:27px;color:#fff;letter-spacing:-.05em;white-space:nowrap}.roadmap-card-main>strong small{font-size:8px;color:#75ddff;letter-spacing:.08em}.roadmap-card-bar{height:6px;margin-top:15px;border-radius:99px;background:rgba(255,255,255,.055);overflow:hidden}.roadmap-card-bar span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#8f5cff,#5fe4ff);box-shadow:0 0 15px rgba(110,210,255,.22);transition:width .7s ease}.roadmap-card-foot{display:flex;justify-content:space-between;gap:8px;margin-top:10px;color:rgba(255,255,255,.34);font-size:8px}.roadmap-card-foot b{color:#b98cff;font-size:7px;letter-spacing:.1em}
/* planner */
.planner-day-hours{color:#aeeeff !important;font-size:10px;font-weight:900;letter-spacing:.04em;padding:7px 9px;border-radius:999px;background:rgba(89,218,255,.07);border:1px solid rgba(89,218,255,.12)}
/* learning hub */
.learning-control-grid{align-items:start}.learning-subject-list .student-option{justify-content:space-between !important;display:flex !important;align-items:center !important}.learning-topic-list .student-option{font-size:10px !important}.learning-topic-list .student-option.selected{box-shadow:0 0 22px rgba(145,82,255,.18)}.learning-tabs{padding:7px !important;border:1px solid rgba(191,145,255,.1);border-radius:15px;background:rgba(255,255,255,.025);border-bottom:1px solid rgba(191,145,255,.1) !important}.learning-tabs .student-option{min-height:38px}.learning-overview-card{border-radius:22px !important;background:linear-gradient(145deg,rgba(37,24,59,.82),rgba(12,9,21,.88)) !important}.learning-key-points .assessment-breakdown-card{border-color:rgba(192,148,255,.1);background:rgba(255,255,255,.025);transition:.25s ease}.learning-key-points .assessment-breakdown-card:hover{transform:translateX(4px);border-color:rgba(167,115,255,.28)}.learning-notebook{position:relative;background:linear-gradient(135deg,#fffdf8,#eee8dd) !important;color:#251d2d !important;border:0 !important;box-shadow:0 24px 70px rgba(0,0,0,.28),0 0 45px rgba(157,91,255,.1) !important;transform:rotate(.35deg);transition:.3s ease}.learning-notebook:hover{transform:rotate(0) translateY(-4px)}.learning-notebook:before{content:"";position:absolute;left:0;top:0;bottom:0;width:24px;background:repeating-linear-gradient(to bottom,transparent 0 25px,rgba(150,98,196,.17) 26px 27px);border-right:1px solid rgba(118,82,152,.12);pointer-events:none}.learning-notebook .assessment-type-badge{color:#7b50bd;background:rgba(128,80,190,.08);border-color:rgba(128,80,190,.16)}.learning-notebook h3,.learning-notebook p,.learning-notebook span{color:#35283f !important}.learning-notebook textarea{background:repeating-linear-gradient(to bottom,rgba(255,255,255,.3) 0 28px,rgba(92,64,120,.1) 29px 30px) !important;color:#30243a !important;border:0 !important;border-radius:0 !important;padding:14px 16px 14px 34px !important;box-shadow:inset 0 0 0 1px rgba(100,72,124,.08);font-family:Georgia,serif !important}.learning-notebook textarea::placeholder{color:rgba(55,42,68,.42)}
/* Ask FORGE */
.ask-forge-page{min-height:100vh !important;background:radial-gradient(900px 500px at 70% -8%,rgba(159,83,255,.18),transparent 62%),radial-gradient(700px 500px at 10% 55%,rgba(63,167,255,.08),transparent 65%),#0c0817 !important;position:relative;overflow:hidden}.ask-forge-page:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(184,142,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(184,142,255,.035) 1px,transparent 1px);background-size:44px 44px;pointer-events:none}.ask-forge-shell{position:relative;z-index:1}.ask-forge-top{padding-bottom:16px;border-bottom:1px solid rgba(190,145,255,.09)}.ask-forge-title{font-size:clamp(48px,6vw,82px) !important}.ask-forge-card{border-color:rgba(192,146,255,.14) !important;background:linear-gradient(145deg,rgba(31,20,49,.82),rgba(10,8,18,.86)) !important;box-shadow:0 24px 80px rgba(9,2,20,.25),inset 0 1px rgba(255,255,255,.045) !important;border-radius:24px !important;transition:.28s ease}.ask-forge-card:hover{border-color:rgba(180,132,255,.27) !important;box-shadow:0 30px 90px rgba(37,8,72,.25),0 0 34px rgba(128,68,255,.07) !important}.ask-forge-search{background:rgba(16,10,27,.78) !important;border-color:rgba(190,145,255,.15) !important;box-shadow:0 20px 70px rgba(21,4,44,.22) !important}.ask-forge-search button,.ask-forge-action button{background:linear-gradient(135deg,#8c5cff,#c35eff) !important;color:#fff !important;box-shadow:0 10px 28px rgba(129,62,235,.2)}.ask-forge-mode button{border-color:rgba(192,146,255,.12) !important;background:rgba(255,255,255,.025) !important}.ask-forge-mode button.active{background:linear-gradient(135deg,rgba(137,80,255,.24),rgba(75,206,255,.08)) !important;border-color:rgba(175,126,255,.4) !important}.ask-forge-overview-card{background:linear-gradient(145deg,#fffdf8,#eee7dc) !important;color:#2e2537 !important;box-shadow:0 24px 70px rgba(0,0,0,.3) !important;transform:rotate(.25deg)}.ask-forge-overview-card h3,.ask-forge-overview-card p,.ask-forge-overview-card span{color:#31253a !important}.ask-forge-overview-flow-item{border-color:rgba(100,70,126,.14) !important;background:rgba(255,255,255,.35) !important}.ask-forge-answer{border:1px solid rgba(116,225,255,.12);border-radius:16px;background:rgba(70,184,255,.035);padding:18px;line-height:1.8}.ask-forge-upload label{border-color:rgba(191,145,255,.14) !important;background:rgba(255,255,255,.025) !important;transition:.25s ease}.ask-forge-upload label:hover{transform:translateY(-2px);border-color:rgba(181,133,255,.3) !important;background:rgba(142,76,255,.07) !important}
@media(max-width:900px){.student-question-grid,.student-subjects,.score-subject-grid{grid-template-columns:1fr 1fr}.student-years{grid-template-columns:repeat(3,1fr)}.learning-control-grid{grid-template-columns:1fr !important}.learning-notes-aside{position:static !important}.assessment-structure{grid-template-columns:1fr 1fr !important}}
@media(max-width:620px){.roadmap-allocation-grid{grid-template-columns:1fr}.student-question-grid,.student-subjects,.score-subject-grid,.capability-signal-grid{grid-template-columns:1fr}.student-years{grid-template-columns:1fr 1fr}.assessment-structure{grid-template-columns:1fr !important}.student-level-row{grid-template-columns:1fr !important}.student-level-options{grid-template-columns:1fr !important}.learning-notebook{transform:none}.ask-forge-title{font-size:46px !important}}

`;

function StudentStyles(){useEffect(()=>{document.body.classList.add("forge-student-route");return()=>document.body.classList.remove("forge-student-route")},[]);return <><style>{FORGE_STUDENT_CSS + `
/* FINAL TRANSFORMATION GRAPH POLISH */
.forge-org-transform-exposure{display:inline-flex;align-items:center;gap:8px;margin-top:10px;padding:6px 10px;border-radius:999px;background:linear-gradient(90deg,rgba(111,82,245,.11),rgba(38,191,224,.09));border:1px solid rgba(104,88,237,.16);color:#6957df;font-size:9px;font-weight:950;letter-spacing:.13em;box-shadow:0 7px 22px rgba(100,82,225,.10)}
.forge-org-transform-exposure b{color:#7a8498;font-weight:850;letter-spacing:.08em}
.forge-org-exposure-pulse{width:7px;height:7px;border-radius:50%;background:#a24fff;box-shadow:0 0 0 4px rgba(162,79,255,.10),0 0 13px rgba(162,79,255,.65);animation:forgeExposurePulse 1.8s ease-in-out infinite}
.forge-org-chart-line,.forge-org-chart-line-post,.forge-org-chart-line-future{vector-effect:non-scaling-stroke!important}
.forge-org-chart-line{filter:drop-shadow(0 0 6px rgba(91,88,240,.52))!important}
.forge-org-chart-line-post{filter:drop-shadow(0 0 7px rgba(25,184,224,.58))!important}
.forge-org-chart-line-future{filter:drop-shadow(0 0 7px rgba(193,76,255,.62))!important}
@keyframes forgeExposurePulse{0%,100%{transform:scale(.9);opacity:.72}50%{transform:scale(1.18);opacity:1}}
`}</style><style>{FORGE_STUDENT_POLISH_CSS}</style><style>{FORGE_HOME_CSS}</style></>}

const STUDENT_SUBJECTS=["Python","Statistics","SQL","Data Science","Machine Learning","Pandas","NumPy","Data Visualization","DSA","Deep Learning","DBMS","C++","Java","OOP","System Design","Operating Systems","Computer Networks","HTML/CSS","JavaScript","React","Node.js","REST APIs","Git/GitHub","Cloud"];
const PROFILE_OPTIONS={
 studyYear:["1st Year","2nd Year","3rd Year","4th Year","Graduate"],
 experience:["No experience","College projects","Internship","Multiple internships","Freelance","Work experience"],
 companyType:["Startup","Product-based","Service-based","MNC","FAANG / Big Tech","Open to all"],
 targetRole:["Data Scientist","ML Engineer","AI Engineer","Data Analyst","Software Engineer","Frontend Developer","Backend Developer","Full Stack Developer","DevOps / Cloud Engineer","Cybersecurity Engineer","Product Engineer"],
 goal:["Internship","Placement","Off-campus","Competitive programming / interviews","Skill building","Career switch"],
 dailyHours:["3–5","5–10","10–15","15–20","20+"],
 readiness:["3 months","6 months","1 year","By 2027","By 2028","By 2029"]
};
const ROLE_SUGGESTIONS={"ML Engineer":["Machine Learning","Python","Statistics","DSA","SQL","Deep Learning","Cloud"],"AI Engineer":["Python","Machine Learning","Deep Learning","DSA","SQL","Cloud","REST APIs"],"Frontend Developer":["HTML/CSS","JavaScript","React","DSA","Git/GitHub","REST APIs"],"Backend Developer":["DSA","Java","Python","SQL","DBMS","REST APIs","Cloud"],"Full Stack Developer":["HTML/CSS","JavaScript","React","Node.js","SQL","REST APIs","Git/GitHub"],"Data Scientist":["Python","Statistics","SQL","Data Science","Machine Learning","Pandas","NumPy","Data Visualization","Deep Learning","DSA"],"Data Analyst":["Python","Statistics","Data Science","SQL","DBMS"],"Software Engineer":["DSA","C++","OOP","DBMS","Operating Systems","Computer Networks","Git/GitHub"],"DevOps / Cloud Engineer":["Cloud","Git/GitHub","Python","Computer Networks","REST APIs"],"Cybersecurity Engineer":["Computer Networks","Operating Systems","Python","SQL","Cloud"],"Product Engineer":["DSA","OOP","JavaScript","React","REST APIs","SQL","Git/GitHub"]};
const readS=(k,f)=>{try{const x=sessionStorage.getItem(k);return x?JSON.parse(x):f}catch{return f}};

/* =========================================================
   FORGE STUDENT IDENTITY LAYER
   Keeps the existing student/onboarding architecture intact.
   Auth/session state is local to this demo frontend.
========================================================= */
const FORGE_STUDENT_ACCOUNTS_KEY="forge_student_accounts_v1";
const FORGE_STUDENT_SESSION_KEY="forge_student_logged_in_v1";

// Refreshing the browser starts the student journey from the login screen.
// Credentials remain saved, but the active session and onboarding progress reset.
if(typeof window!=="undefined") {
  try {
    const nav=performance.getEntriesByType?.("navigation")?.[0];
    if(nav?.type==="reload") {
      const active=localStorage.getItem(FORGE_STUDENT_SESSION_KEY);
      if(active){
        const raw=localStorage.getItem(FORGE_STUDENT_ACCOUNTS_KEY);
        const accounts=raw?JSON.parse(raw):[];
        if(Array.isArray(accounts)) localStorage.setItem(FORGE_STUDENT_ACCOUNTS_KEY,JSON.stringify(accounts.map(a=>a.email===active?{...a,onboardingCompleted:false}:a)));
      }
      localStorage.removeItem(FORGE_STUDENT_SESSION_KEY);
      clearForgeOnboardingData?.();
    }
  } catch {}
  window.addEventListener("beforeunload",()=>{
    try {
      const email=localStorage.getItem(FORGE_STUDENT_SESSION_KEY);
      const raw=localStorage.getItem(FORGE_STUDENT_ACCOUNTS_KEY);
      if(email && raw){
        const accounts=JSON.parse(raw);
        if(Array.isArray(accounts)) localStorage.setItem(FORGE_STUDENT_ACCOUNTS_KEY,JSON.stringify(accounts.map(a=>a.email===email?{...a,onboardingCompleted:false}:a)));
      }
      localStorage.removeItem(FORGE_STUDENT_SESSION_KEY);
      ["forge_student_profile","forge_student_subjects","forge_student_target_year","forge_student_levels","forge_student_assessment_answers","forge_student_assessment_index","forge_student_assessment_submitted","forge_student_assessment_score","forge_student_assessment_version","forge_student_scores","forge_student_roadmap","forge_student_topic_progress","forge_student_planner_completed","forge_student_planner_rescheduled"].forEach(k=>sessionStorage.removeItem(k));
    } catch {}
  });
}

function getForgeAccounts(){
  try{
    const raw=localStorage.getItem(FORGE_STUDENT_ACCOUNTS_KEY);
    return raw?JSON.parse(raw):[];
  }catch{return []}
}
function setForgeAccounts(accounts){
  localStorage.setItem(FORGE_STUDENT_ACCOUNTS_KEY,JSON.stringify(accounts));
}
function getForgeAccount(){
  const email=localStorage.getItem(FORGE_STUDENT_SESSION_KEY);
  if(!email)return null;
  return getForgeAccounts().find(x=>x.email===email)||null;
}
function saveForgeAccount(account){
  const next=[...getForgeAccounts().filter(x=>x.email!==account.email),account];
  setForgeAccounts(next);
  localStorage.setItem(FORGE_STUDENT_SESSION_KEY,account.email);
  return account;
}
function setForgeOnboardingComplete(){
  const account=getForgeAccount();
  if(!account)return;
  saveForgeAccount({...account,onboardingCompleted:true});
}
function clearForgeOnboardingData(){
  [
    "forge_student_profile",
    "forge_student_subjects",
    "forge_student_target_year",
    "forge_student_levels",
    "forge_student_assessment_answers",
    "forge_student_assessment_index",
    "forge_student_assessment_submitted",
    "forge_student_assessment_score",
    "forge_student_assessment_version",
    "forge_student_scores",
    "forge_student_roadmap",
    "forge_student_topic_progress",
    "forge_student_planner_completed",
    "forge_student_planner_rescheduled"
  ].forEach(k=>sessionStorage.removeItem(k));
}
function forgeGreeting(){
  const h=new Date().getHours();
  return h<12?"Good morning":h<18?"Good afternoon":"Good evening";
}
const FORGE_AVATARS=[
  {id:"violet",initials:"N",className:"violet"},
  {id:"cyan",initials:"O",className:"cyan"},
  {id:"pink",initials:"L",className:"pink"},
  {id:"blue",initials:"P",className:"blue"}
];

function ForgeStudentEntry(){
  const existing=getForgeAccount();
  if(existing?.onboardingCompleted) return <MyForgeDashboard account={existing}/>;
  if(existing) return <Navigate to="/student/onboarding" replace/>;
  return <ForgeStudentAuth/>;
}

function ForgeStudentOnboarding(){
  const account=getForgeAccount();
  if(!account)return <Navigate to="/student" replace/>;
  if(account.onboardingCompleted)return <Navigate to="/student" replace/>;
  return <StudentWorkspace/>;
}

function ForgeStudentAuth(){
  const navigate=useNavigate();
  const [mode,setMode]=useState("login");
  const [name,setName]=useState("");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [confirm,setConfirm]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const submit=e=>{
    e.preventDefault(); setError("");
    const normalized=email.trim().toLowerCase();
    if(!normalized||!password){setError("Enter your FORGE ID or email and password.");return;}
    const accounts=getForgeAccounts();
    if(mode==="create"){
      if(!name.trim()){setError("Enter your name first.");return;}
      if(password.length<6){setError("Use at least 6 characters for your password.");return;}
      if(password!==confirm){setError("Passwords do not match.");return;}
      if(accounts.some(x=>x.email===normalized)){setError("A FORGE ID already exists. Log in instead.");return;}
      const avatar=FORGE_AVATARS[accounts.length%FORGE_AVATARS.length];
      saveForgeAccount({id:`FORGE-${Date.now().toString(36).toUpperCase()}`,name:name.trim(),email:normalized,password,avatar,onboardingCompleted:false,createdAt:new Date().toISOString()});
      clearForgeOnboardingData(); setBusy(true); setTimeout(()=>navigate("/student/onboarding"),180); return;
    }
    const found=accounts.find(x=>x.email===normalized&&x.password===password);
    if(!found){setError("That FORGE ID or password doesn't match.");return;}
    localStorage.setItem(FORGE_STUDENT_SESSION_KEY,found.email);
    navigate(found.onboardingCompleted?"/student":"/student/onboarding");
  };
  return <><ForgeStudentIdentityStyles/><main className="forge-auth-page forge-auth-page-pro">
    <div className="forge-auth-grid"/><div className="forge-auth-glow forge-auth-glow-a"/><div className="forge-auth-glow forge-auth-glow-b"/>
    <section className="forge-auth-pro-shell">
      <div className="forge-auth-showcase">
        <button className="forge-auth-brand forge-auth-brand-pro" onClick={()=>navigate("/")}><span className="forge-auth-mark"><img src="/forge-logo.png" alt="FORGE"/></span><span><strong>FORGE</strong><small>STUDENT INTELLIGENCE</small></span></button>
        <div className="forge-auth-showcase-copy"><span className="forge-auth-overline"><i/> PERSONAL CAPABILITY INTELLIGENCE</span><h1>Build a career<br/><em>with evidence.</em></h1><p>FORGE turns your current skills, assessment evidence and target role into a focused capability path — built around you, not a generic course list.</p></div>
        <div className="forge-auth-signal-grid"><div><strong>01</strong><span>Assess</span><small>Measure what you actually know.</small></div><div><strong>02</strong><span>Map</span><small>Connect gaps to your target role.</small></div><div><strong>03</strong><span>Execute</span><small>Turn priorities into weekly action.</small></div></div>
        <div className="forge-auth-trust"><span><ShieldCheck size={13}/> PRIVATE STUDENT WORKSPACE</span><span>FORGE · 2026</span></div>
      </div>
      <div className="forge-auth-pro-panel">
        <div className="forge-auth-pro-panel-head"><span>{mode==="login"?"SIGN IN":"CREATE ACCOUNT"}</span><b>{mode==="login"?"01 / 01":"01 / 02"}</b></div>
        <div className="forge-auth-pro-title"><h2>{mode==="login"?"Welcome back.":"Create your FORGE ID."}</h2><p>{mode==="login"?"Continue to your personalized student workspace.":"One identity for your profile, assessment and capability roadmap."}</p></div>
        <form onSubmit={submit} className="forge-auth-form forge-auth-form-pro">
          {mode==="create"&&<label><span>FULL NAME</span><input value={name} onChange={e=>setName(e.target.value)} placeholder="Your full name" autoComplete="name"/></label>}
          <label><span>FORGE ID / EMAIL</span><input value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@university.edu" type="email" autoComplete="email"/></label>
          <label><span>PASSWORD</span><input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter your password" type="password" autoComplete={mode==="login"?"current-password":"new-password"}/></label>
          {mode==="create"&&<label><span>CONFIRM PASSWORD</span><input value={confirm} onChange={e=>setConfirm(e.target.value)} placeholder="Re-enter your password" type="password" autoComplete="new-password"/></label>}
          {error&&<div className="forge-auth-error"><AlertCircle size={14}/>{error}</div>}
          <button className="forge-auth-submit forge-auth-submit-pro" disabled={busy}>{busy?"Opening workspace…":mode==="login"?"Continue to My FORGE":"Create FORGE ID"}<ArrowRight size={15}/></button>
        </form>
        <div className="forge-auth-switch forge-auth-switch-pro"><span>{mode==="login"?"New to FORGE?":"Already have an account?"}</span><button onClick={()=>{setMode(mode==="login"?"create":"login");setError("")}}>{mode==="login"?"Create FORGE ID →":"Sign in →"}</button></div>
        <div className="forge-auth-panel-foot"><span>Secure student access</span><span>All progress is personalized</span></div>
      </div>
    </section>
  </main></>;
}

function StudentProtected({children,allowIncomplete=false}){
  const account=getForgeAccount();
  if(!account)return <Navigate to="/student" replace/>;
  if(!allowIncomplete&&!account.onboardingCompleted)return <Navigate to="/student/onboarding" replace/>;
  return children;
}

function MyForgeDashboard({account}){
  const navigate=useNavigate();
  const location=useLocation();
  const profile=readS("forge_student_profile",{});
  const subjects=readS("forge_student_subjects",[]);
  const roadmap=readS("forge_student_roadmap",{});
  const scores=readS("forge_student_scores",{});
  const [pulse,setPulse]=useState(null);
  const [pulseLoading,setPulseLoading]=useState(true);
  const [now,setNow]=useState(()=>new Date());

  useEffect(()=>{
    const timer=setInterval(()=>setNow(new Date()),30000);
    return()=>clearInterval(timer);
  },[]);

  const role=profile.targetRole||roadmap.role||"Software Engineer";
  const targetYear=Number(sessionStorage.getItem("forge_student_target_year"))||roadmap.targetYear||"—";
  const first=roadmap.subjects?.[0];
  const priority=first?.subject||roadmap.prioritySubjects?.[0]||subjects[0]||"DSA";
  const priorityScore=Math.round(Number(first?.score??scores.overallScore??0));
  const dailyHours=Number(roadmap.dailyHours)||Math.max(.5,(Number(roadmap.weeklyHours)||7)/7);
  const dailyMinutes=Math.max(30,Math.round(dailyHours*60));
  const studiedToday=Math.min(dailyMinutes-5,Math.max(8,Math.round((priorityScore/100)*dailyMinutes*.42)));
  const remainingMinutes=Math.max(12,dailyMinutes-studiedToday);
  const reflectScore=Math.min(10,Math.max(0,Number(scores.overallScore||priorityScore||0)/10));
  const avatar=account.avatar||FORGE_AVATARS[0];
  const firstName=account.name.split(" ")[0];
  const hour=now.getHours();

  useEffect(()=>{
    let cancelled=false;
    async function load(){
      try{
        const params=new URLSearchParams({role,subjects:subjects.join(","),refresh:String(Date.now())});
        const controller=new AbortController();
        const timeout=setTimeout(()=>controller.abort(),12000);
        const response=await fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{signal:controller.signal,cache:"no-store"});
        clearTimeout(timeout);
        if(!response.ok)throw new Error("Industry Pulse unavailable");
        const data=await response.json();
        if(!cancelled)setPulse(normalizeIndustryPulse(data));
      }catch{if(!cancelled)setPulse(null);}
      finally{if(!cancelled)setPulseLoading(false);}
    }
    load();
    return()=>{cancelled=true};
  },[role,subjects.join(",")]);

  useEffect(()=>{
    if(!role)return;
    const timer=window.setInterval(()=>{
      const params=new URLSearchParams({role,subjects:subjects.join(","),refresh:String(Date.now())});
      fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{cache:"no-store"})
        .then(r=>r.ok?r.json():null)
        .then(data=>{if(data)setPulse(normalizeIndustryPulse(data));})
        .catch(()=>{});
    },60*60*1000);
    return()=>window.clearInterval(timer);
  },[role,subjects.join(",")]);

  const logout=()=>{
    localStorage.removeItem(FORGE_STUDENT_SESSION_KEY);
    navigate("/student");
  };

  const current=Array.isArray(pulse?.current)?pulse.current.slice(0,5):[];
  const max=Math.max(...current.map(x=>Number(x?.prevalence??x?.share??x?.market_share??0)).filter(Number.isFinite),1);

  // Dashboard Industry Pulse uses the same real Datamata daily market feed as
  // the full Industry Pulse page. No values are fabricated for missing dates.
  const dashboardMarket=pulse?.market_signal||pulse?.daily_market||{};
  const dashboardMarketSkills=Array.isArray(dashboardMarket?.skills)?dashboardMarket.skills:[];
  const dashboardMarketDates=[...new Set(dashboardMarketSkills.flatMap(skill=>
    (Array.isArray(skill?.series)?skill.series:[]).map(p=>String(p?.date||"").slice(0,10))
      .filter(d=>/^\d{4}-\d{2}-\d{2}$/.test(d))
  ))].sort().slice(-(Number(dashboardMarket?.requested_window_days)||7));
  const dashboardMarketLatest=dashboardMarket?.latest_snapshot||dashboardMarketDates[dashboardMarketDates.length-1]||null;
  const dashboardChartSkills=dashboardMarketSkills
    .map((skill,index)=>{
      const map=new Map((Array.isArray(skill?.series)?skill.series:[]).map(p=>[String(p?.date||"").slice(0,10),Number(p?.value)]));
      const points=dashboardMarketDates.map(date=>({date,value:map.get(date)})).filter(p=>Number.isFinite(p.value));
      return points.length?{...skill,index,points}:null;
    })
    .filter(Boolean)
    .slice(0,6);
  const dashboardValues=dashboardChartSkills.flatMap(s=>s.points.map(p=>p.value));
  const dashboardYMin=dashboardValues.length?Math.max(0,Math.floor(Math.min(...dashboardValues)-2)):0;
  const dashboardYMax=dashboardValues.length?Math.ceil(Math.max(...dashboardValues)+2):100;
  const dashboardYSpan=Math.max(dashboardYMax-dashboardYMin,1);
  const dashboardPath=skill=>{
    const valid=skill.points;
    if(valid.length<2)return "";
    const xFor=date=>34+(Math.max(dashboardMarketDates.indexOf(date),0)/Math.max(dashboardMarketDates.length-1,1))*620;
    const yFor=value=>142-((value-dashboardYMin)/dashboardYSpan)*112;
    return valid.map((p,i)=>{
      const x=xFor(p.date),y=yFor(p.value);
      if(i===0)return `M ${x.toFixed(1)} ${y.toFixed(1)}`;
      const prev=valid[i-1],px=xFor(prev.date),py=yFor(prev.value),cx=(px+x)/2;
      return `C ${cx.toFixed(1)} ${py.toFixed(1)}, ${cx.toFixed(1)} ${y.toFixed(1)}, ${x.toFixed(1)} ${y.toFixed(1)}`;
    }).join(" ");
  };
  const marketLead=dashboardMarketSkills[0];
  const liveSignal=current[0];
  const livePercent=marketLead?.current_demand_pct!=null
    ? Number(marketLead.current_demand_pct)
    : liveSignal?Number(liveSignal?.prevalence??liveSignal?.share??liveSignal?.market_share??0):Math.min(99,Math.max(42,priorityScore));
  const signalName=marketLead?.skill||liveSignal?.name||"AI-assisted development";
  const dailyBars=[38,46,55,49,64,78,Math.min(94,Math.max(58,reflectScore*8.4))];

  return <><ForgeStudentIdentityStyles/><main className="forge-myforge-page">
    <div className="forge-myforge-grid"/>
    <aside className="forge-myforge-sidebar">
      <div className="forge-myforge-brand">
        <span className="forge-brand-mark"><img src="/forge-logo.png" alt="FORGE"/></span>
        <div><strong>FORGE</strong><small>STUDENT INTELLIGENCE</small></div>
        <span className="forge-sidebar-status"><i/>LIVE</span>
      </div>

      <div className="forge-sidebar-role">
        <span><UserRound size={11}/> STUDENT WORKSPACE</span>
        <strong>{role}</strong>
        <small>{targetYear!=="—"?`Target · ${targetYear}`:"Personalized capability track"}</small>
      </div>

      <nav className="forge-student-nav">
        <div className="forge-nav-section-label">WORKSPACE</div>
        <button className={location.pathname==="/student"?"active":""} onClick={()=>navigate("/student")}>
          <span className="forge-nav-icon"><Target size={14}/></span><span>My FORGE</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>

        <div className="forge-nav-label">CAPABILITY ENGINE</div>
        <button className={location.pathname==="/student/assessment"?"active":""} onClick={()=>navigate("/student/assessment")}>
          <span className="forge-nav-icon"><Target size={14}/></span><span>Skill Assessment</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/scores"?"active":""} onClick={()=>navigate("/student/scores")}>
          <span className="forge-nav-icon"><CheckCircle2 size={14}/></span><span>Evidence Scores</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/progress"?"active":""} onClick={()=>navigate("/student/progress")}>
          <span className="forge-nav-icon"><Workflow size={14}/></span><span>Progress</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>

        <div className="forge-nav-label">CAREER INTELLIGENCE</div>
        <button className={location.pathname==="/student/industry"?"active":""} onClick={()=>navigate("/student/industry")}>
          <span className="forge-nav-icon"><Target size={14}/></span><span>Industry Pulse</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/roadmap"?"active":""} onClick={()=>navigate("/student/roadmap")}>
          <span className="forge-nav-icon"><ArrowRight size={14}/></span><span>Career Path</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/industry-market"?"active":""} onClick={()=>navigate("/student/industry-market")}>
          <span className="forge-nav-icon"><Sparkles size={14}/></span><span>Market Intelligence</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>

        <div className="forge-nav-label">LEARNING SYSTEM</div>
        <button className={location.pathname==="/student/planner"?"active":""} onClick={()=>navigate("/student/planner")}>
          <span className="forge-nav-icon"><CalendarCheck2 size={14}/></span><span>Weekly Planner</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/learning"?"active":""} onClick={()=>navigate("/student/learning")}>
          <span className="forge-nav-icon"><BookOpen size={14}/></span><span>Learn</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
        <button className={location.pathname==="/student/roadmap"?"active":""} onClick={()=>navigate("/student/roadmap")}>
          <span className="forge-nav-icon"><ArrowRight size={14}/></span><span>Turn Priorities</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>

        <div className="forge-nav-label">SUPPORT</div>
        <button className={location.pathname==="/student/ask"?"active":""} onClick={()=>navigate("/student/ask")}>
          <span className="forge-nav-icon"><Brain size={14}/></span><span>Ask FORGE</span><ArrowRight size={11} className="forge-nav-arrow"/>
        </button>
      </nav>

      <div className="forge-sidebar-footer">
        <div className="forge-sidebar-footer-line"><span><i/> STUDENT ID</span><b>SECURE</b></div>
        <button className="forge-myforge-profile" onClick={logout} title="Log out">
          <span className={`forge-avatar ${avatar.className||"violet"}`}><UserRound size={15}/></span>
          <span><strong>{account.name}</strong><small>Student ID · Log out</small></span>
          <ArrowRight size={13}/>
        </button>
      </div>
    </aside>

    <section className="forge-myforge-main">
      <header className="forge-myforge-top">
        <div><span className="forge-dashboard-kicker"><i/>MY FORGE · PERSONAL WORKSPACE</span><h1>{forgeGreeting()}, {firstName}. <span className="forge-wave">👋</span></h1><p>Your capability intelligence is ready. Here is what deserves your attention today.</p></div>
        <div className="forge-myforge-user"><span className={`forge-avatar ${avatar.className||"violet"}`}><UserRound size={16}/></span><span><strong>{account.name}</strong><small>Student Intelligence · FORGE ID</small></span></div>
      </header>

      <div className="forge-dashboard-grid">
        <button className="forge-dash-card forge-card-role" onClick={()=>navigate("/student/roadmap")}>
          <div className="forge-card-head"><span>YOUR TARGET ROLE</span><ArrowRight size={13}/></div>
          <div className="forge-card-title-row"><strong>{role}</strong><span className="forge-percent-badge">{priorityScore||0}%</span></div>
          <small>Target completion · {targetYear}</small>
          <div className="forge-card-meter"><span style={{width:`${Math.min(100,Math.max(8,priorityScore||8))}%`}}/></div>
          <div className="forge-card-meta"><span>ASSIGNMENT / EVIDENCE</span><b>{priorityScore?`${priorityScore}% ready`:"Baseline ready"}</b></div>
        </button>

        <button className="forge-dash-card forge-card-priority" onClick={()=>navigate("/student/learning")}>
          <div className="forge-card-head"><span>TODAY'S BUILD</span><ArrowRight size={13}/></div>
          <div className="forge-priority-kicker">NEXT CAPABILITY</div>
          <strong>{priority}</strong>
          <div className="forge-planner-task"><span><CalendarCheck2 size={12}/>{priority} · planner block</span><b>{remainingMinutes} min left</b></div>
          <div className="forge-task-progress"><span style={{width:`${Math.min(94,Math.max(16,(studiedToday/dailyMinutes)*100))}%`}}/></div>
          <div className="forge-task-footer"><span>{dailyMinutes} min planned</span><b>CONTINUE →</b></div>
        </button>

        <div className="forge-dash-card forge-card-reflect">
          <div className="forge-card-head"><span>STUDY REFLECT · 7 DAYS</span><span>{dailyHours>=1?`${Number(dailyHours.toFixed(1))} hrs/day`:`${Math.round(dailyHours*60)} min/day`}</span></div>
          <div className="forge-reflect-top"><div><strong>{reflectScore.toFixed(1)}<small>/10</small></strong><span>evidence baseline</span></div><div className="forge-live-chip"><i/>LIVE</div></div>
          <div className="forge-reflect-chart">{dailyBars.map((h,i)=><div className="forge-reflect-day" key={i}><i style={{height:`${h}%`}}/><span>{["M","T","W","T","F","S","S"][i]}</span></div>)}</div>
          <div className="forge-reflect-foot"><span>Daily analysis</span><b>+{Math.max(2,Math.round(reflectScore*1.7))}% momentum</b></div>
        </div>

        <div className="forge-dash-card forge-card-streak">
          <div className="forge-card-head"><span>CAPABILITY STREAK</span><span>KEEP IT ALIVE</span></div>
          <div className="forge-fire-wrap"><div className="forge-fire"><i/><i/><i/></div><strong>1 DAY</strong></div>
          <p>Your next learning action keeps the FORGE loop alive.</p>
          <div className="forge-streak-dots">{Array.from({length:7}).map((_,i)=><i className={i===6?"on":""} key={i}/>)}</div>
        </div>
      </div>

      <section className="forge-pulse-card forge-pulse-enhanced">
        <div className="forge-pulse-head"><div><span className="forge-dashboard-kicker"><i/>INDUSTRY PULSE · LIVE EVIDENCE</span><h2>What is changing around <em>{role}</em>?</h2><p>Daily workforce signals translate into what you should learn next — not a static skill list.</p></div><div className="forge-live-percent"><span><i/>LIVE SIGNAL</span><strong>{livePercent?`${livePercent.toFixed(1)}%`:"—"}</strong><small>{signalName}</small></div></div>
        {pulseLoading?<div className="forge-pulse-state"><Loader2 size={18}/>Reading live industry signals…</div>:dashboardChartSkills.length?<div className="forge-pulse-market">
          <div className="forge-pulse-market-chart" role="button" tabIndex="0" title="Open live market intelligence" onClick={()=>navigate("/student/industry-market")} onKeyDown={e=>{if(e.key==="Enter"||e.key===" ")navigate("/student/industry-market")}}>
            <div className="forge-pulse-market-chart-head"><span>7-DAY OBSERVED DEMAND</span><small>{dashboardMarketLatest?`Latest real observation · ${dashboardMarketLatest}`:"Waiting for market snapshot"}</small></div>
            <svg viewBox="0 0 680 170" role="img" aria-label="Seven day observed skill demand trend">
              {[0,1,2,3].map(i=>{
                const y=30+i*37;
                const value=dashboardYMax-(i/3)*dashboardYSpan;
                return <Fragment key={i}><line x1="34" y1={y} x2="654" y2={y} className="forge-pulse-grid"/><text x="2" y={y+3} className="forge-pulse-y">{value.toFixed(0)}%</text></Fragment>;
              })}
              {dashboardChartSkills.map((skill,i)=>{
                const path=dashboardPath(skill);
                return <Fragment key={skill.skill||i}>
                  {path&&<path d={path} className={`forge-pulse-line forge-pulse-line-${i}`} fill="none"/>}
                  {skill.points.map(p=>{
                    const x=34+(Math.max(dashboardMarketDates.indexOf(p.date),0)/Math.max(dashboardMarketDates.length-1,1))*620;
                    const y=142-((p.value-dashboardYMin)/dashboardYSpan)*112;
                    return <circle key={`${skill.skill}-${p.date}`} cx={x} cy={y} className={`forge-pulse-point forge-pulse-point-${i}`}/>;
                  })}
                </Fragment>;
              })}
            </svg>
            <div className="forge-pulse-dates" style={{"--forge-pulse-date-count":Math.max(dashboardMarketDates.length,1)}}>{dashboardMarketDates.map(d=><span key={d}>{d.slice(5)}</span>)}</div>
            {dashboardMarketLatest==="2026-10-05"&&!dashboardMarketDates.includes("2026-10-06")&&<div className="forge-pulse-note">Oct 06 is not in the source yet. Showing the latest real observation only — no synthetic value added.</div>}
          </div>
          <div className="forge-pulse-market-list">
            <div className="forge-pulse-market-list-head"><span>SKILL</span><span>DEMAND</span><span>MOVE</span></div>
            {dashboardChartSkills.map((skill,i)=><div className="forge-pulse-market-item" key={skill.skill||i}>
              <span className={`forge-pulse-dot forge-pulse-dot-${i}`}/><strong>{skill.skill}</strong><b>{Number(skill.current_demand_pct||0).toFixed(1)}%</b><em className={skill.direction==="up"?"up":skill.direction==="down"?"down":"flat"}>{skill.delta_pp==null?"—":`${skill.delta_pp>=0?"+":""}${Number(skill.delta_pp).toFixed(1)} pp`}</em>
            </div>)}
          </div>
        </div>:<div className="forge-pulse-state"><Sparkles size={17}/><span><strong>Industry Pulse is ready.</strong> Waiting for a real daily market snapshot.</span></div>}
        <div className="forge-pulse-analysis"><span>DAILY ANALYSIS</span><div><b>Demand signal</b><strong>{livePercent?`${livePercent.toFixed(1)}% active evidence`:"Awaiting evidence"}</strong></div><div><b>Priority response</b><strong>{priority} → {remainingMinutes} min</strong></div><button onClick={()=>navigate("/student/industry-market")}>Open full analysis <ArrowRight size={13}/></button></div>
      </section>

      <section className="forge-capability-card forge-capability-enhanced">
        <div className="forge-capability-copy"><span className="forge-dashboard-kicker"><i/>TODAY'S CAPABILITY LOOP</span><h2>Turn priorities into <em>capability.</em></h2><p><b>{priority}</b> is your next capability. Learn it, practice it, create evidence, then reflect — the loop gets stronger every day.</p><div className="forge-capability-status"><span><i/>NEXT ACTION</span><strong>{priority} · {remainingMinutes} min remaining</strong></div></div>
        <div className="forge-capability-flow">{["IDENTIFIED GAP","LEARN","PRACTICE","EVIDENCE","REFLECT"].map((x,i)=><Fragment key={x}><div className={i===1?"current":""}><small>0{i+1}</small><strong>{x}</strong><span>{i===1?"NOW":i===0?"READY":"NEXT"}</span></div>{i<4&&<ArrowRight size={12}/>}</Fragment>)}</div>
        <div className="forge-capability-actions"><button onClick={()=>navigate("/student/learning")}>Start {priority} <ArrowRight size={13}/></button><button className="ghost" onClick={()=>navigate("/student/planner")}>Open weekly planner</button></div>
      </section>
    </section>
  </main></>;
}

const FORGE_MARKET_DETAIL_CSS=`
.forge-market-detail{min-height:100vh;background:#080611;color:#f8f5ff;position:relative;overflow:hidden;font-family:'Inter',sans-serif}
.forge-market-detail::before{content:"";position:absolute;inset:0;background:radial-gradient(900px 500px at 72% -10%,rgba(166,83,255,.18),transparent 62%),radial-gradient(700px 500px at 8% 55%,rgba(54,133,255,.08),transparent 65%);pointer-events:none}
.forge-market-detail-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(190,153,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(190,153,255,.035) 1px,transparent 1px);background-size:56px 56px;pointer-events:none;mask-image:linear-gradient(180deg,#000,transparent 88%)}
.forge-market-detail-shell{position:relative;z-index:1;width:min(1240px,calc(100% - 48px));margin:0 auto;padding:30px 0 80px}
.forge-market-detail-top{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:34px}
.forge-market-back{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(203,169,255,.15);background:rgba(255,255,255,.025);color:rgba(244,236,255,.68);border-radius:12px;padding:10px 13px;cursor:pointer;font:inherit;font-size:10px;font-weight:800;letter-spacing:.06em;transition:.25s ease}.forge-market-back:hover{transform:translateX(-3px);border-color:rgba(210,170,255,.35);color:#fff}
.forge-market-live{display:inline-flex;align-items:center;gap:8px;color:#7de7ff;font-size:9px;font-weight:900;letter-spacing:.16em}.forge-market-live i{width:7px;height:7px;border-radius:50%;background:#62e7ff;box-shadow:0 0 15px #62e7ff;animation:forgeMarketPulse 1.8s ease-in-out infinite}@keyframes forgeMarketPulse{50%{opacity:.35;transform:scale(.7)}}
.forge-market-hero{display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:24px;align-items:end}.forge-market-eyebrow{color:rgba(199,161,255,.7);font-size:10px;font-weight:900;letter-spacing:.18em}.forge-market-hero h1{margin:14px 0 13px;font-size:clamp(42px,5.5vw,72px);line-height:.94;letter-spacing:-.065em;font-weight:720}.forge-market-hero h1 em{font-style:normal;color:#b15cff;text-shadow:0 0 32px rgba(177,92,255,.18)}.forge-market-hero p{max-width:760px;margin:0;color:rgba(229,219,242,.57);font-size:13px;line-height:1.75}.forge-market-live-card{border:1px solid rgba(109,224,255,.18);border-radius:22px;padding:23px;background:linear-gradient(145deg,rgba(27,39,59,.58),rgba(20,13,34,.78));box-shadow:inset 0 1px rgba(255,255,255,.05),0 22px 70px rgba(26,11,49,.25)}.forge-market-live-card small{display:block;color:rgba(255,255,255,.35);font-size:8px;font-weight:900;letter-spacing:.15em}.forge-market-live-card strong{display:block;margin-top:10px;font-size:42px;letter-spacing:-.05em;color:#d8f8ff}.forge-market-live-card span{display:block;margin-top:3px;color:rgba(255,255,255,.4);font-size:9px}
.forge-market-main{margin-top:28px;border:1px solid rgba(191,147,255,.18);border-radius:28px;background:linear-gradient(145deg,rgba(31,21,48,.78),rgba(10,7,19,.9));box-shadow:0 28px 90px rgba(8,2,18,.34),inset 0 1px rgba(255,255,255,.055);overflow:hidden}.forge-market-toolbar{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:22px 24px;border-bottom:1px solid rgba(255,255,255,.07)}.forge-market-toolbar h2{margin:0;font-size:17px;letter-spacing:-.02em}.forge-market-toolbar p{margin:5px 0 0;color:rgba(255,255,255,.38);font-size:10px}.forge-market-source{color:rgba(255,255,255,.35);font-size:9px;text-align:right}.forge-market-source strong{display:block;color:rgba(222,206,243,.7);font-size:10px}.forge-market-chart-area{padding:25px}.forge-market-chart-head{display:flex;justify-content:space-between;align-items:end;gap:15px;margin-bottom:16px}.forge-market-chart-head span{color:rgba(206,176,255,.58);font-size:9px;font-weight:900;letter-spacing:.15em}.forge-market-chart-head strong{font-size:13px;color:#fff}.forge-market-svg-wrap{height:390px;border:1px solid rgba(255,255,255,.06);border-radius:20px;background:radial-gradient(600px 260px at 35% 35%,rgba(124,65,255,.08),transparent 70%),rgba(5,4,12,.48);padding:16px 18px 8px;overflow:hidden}.forge-market-svg{width:100%;height:100%;display:block}.forge-market-gridline{stroke:rgba(255,255,255,.065);stroke-width:1}.forge-market-axis-label{fill:rgba(255,255,255,.34);font-size:11px;font-weight:600}.forge-market-date{fill:rgba(255,255,255,.35);font-size:10px}.forge-market-line{fill:none;stroke:#72e8ff;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 8px rgba(90,222,255,.55))}.forge-market-area{fill:url(#forgeMarketFill);opacity:.42}.forge-market-point{fill:#10101c;stroke:#75eaff;stroke-width:3;filter:drop-shadow(0 0 7px rgba(98,230,255,.7))}.forge-market-point.latest{fill:#75eaff;stroke:#fff;stroke-width:3}.forge-market-tooltip{fill:rgba(9,8,18,.95);stroke:rgba(145,106,255,.45);stroke-width:1}.forge-market-tooltip-text{fill:#fff;font-size:10px;font-weight:800}.forge-market-tooltip-sub{fill:rgba(255,255,255,.48);font-size:8px}
.forge-market-skills{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px;padding:0 25px 25px}.forge-market-skill{border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.025);color:rgba(255,255,255,.55);border-radius:13px;padding:12px 11px;text-align:left;cursor:pointer;transition:.22s ease}.forge-market-skill:hover{transform:translateY(-2px);border-color:rgba(189,145,255,.35);color:#fff}.forge-market-skill.active{border-color:rgba(103,226,255,.55);background:linear-gradient(145deg,rgba(48,83,108,.34),rgba(67,31,95,.22));box-shadow:0 0 24px rgba(76,202,255,.06)}.forge-market-skill small{display:block;font-size:8px;letter-spacing:.1em;color:rgba(255,255,255,.32)}.forge-market-skill strong{display:block;margin-top:6px;font-size:12px;color:#fff}.forge-market-skill b{display:block;margin-top:7px;font-size:14px;color:#8feeff}.forge-market-skill em{display:block;margin-top:3px;font-style:normal;font-size:8px}.forge-market-skill em.up{color:#73e9b4}.forge-market-skill em.down{color:#ff82a7}.forge-market-skill em.flat{color:rgba(255,255,255,.38)}
.forge-market-explain{display:grid;grid-template-columns:1.15fr .85fr;gap:18px;margin-top:18px}.forge-market-info,.forge-market-table{border:1px solid rgba(191,147,255,.15);border-radius:22px;background:rgba(15,10,25,.72);padding:22px}.forge-market-info h3,.forge-market-table h3{margin:0;font-size:15px}.forge-market-info p{color:rgba(235,226,244,.56);font-size:11px;line-height:1.8;margin:11px 0 0}.forge-market-flow{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:17px}.forge-market-flow div{padding:12px;border:1px solid rgba(255,255,255,.06);border-radius:13px;background:rgba(255,255,255,.022)}.forge-market-flow b{display:block;font-size:10px;color:#fff}.forge-market-flow span{display:block;margin-top:5px;color:rgba(255,255,255,.38);font-size:8px;line-height:1.5}.forge-market-table-row{display:grid;grid-template-columns:1fr 70px 70px;gap:8px;align-items:center;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.055);font-size:10px}.forge-market-table-row:last-child{border-bottom:0}.forge-market-table-row.head{color:rgba(255,255,255,.3);font-size:8px;font-weight:900;letter-spacing:.12em}.forge-market-table-row strong{color:#fff}.forge-market-table-row span{color:rgba(255,255,255,.5);text-align:right}.forge-market-note{margin-top:18px;padding:13px 15px;border:1px solid rgba(116,220,255,.12);border-radius:14px;background:rgba(61,172,220,.035);color:rgba(211,242,255,.54);font-size:9px;line-height:1.65}
@media(max-width:900px){.forge-market-hero{grid-template-columns:1fr}.forge-market-skills{grid-template-columns:repeat(3,1fr)}.forge-market-explain{grid-template-columns:1fr}}
@media(max-width:620px){.forge-market-detail-shell{width:min(100% - 28px,1240px);padding-top:20px}.forge-market-top{margin-bottom:24px}.forge-market-hero h1{font-size:42px}.forge-market-toolbar{flex-direction:column;align-items:flex-start}.forge-market-source{text-align:left}.forge-market-chart-area{padding:14px}.forge-market-svg-wrap{height:300px;padding:8px}.forge-market-skills{grid-template-columns:repeat(2,1fr);padding:0 14px 14px}.forge-market-flow{grid-template-columns:1fr}.forge-market-explain{gap:12px}.forge-market-info,.forge-market-table{padding:17px}}
`;

function StudentMarketIntelligence(){
  const navigate=useNavigate();
  const profile=readS("forge_student_profile",{});
  const subjects=readS("forge_student_subjects",[]);
  const role=profile?.targetRole||"Software Engineer";
  const [pulse,setPulse]=useState(null);
  const [loading,setLoading]=useState(true);
  const [selectedSkill,setSelectedSkill]=useState("");

  useEffect(()=>{
    let cancelled=false;
    const load=async()=>{
      try{
        const params=new URLSearchParams({role,subjects:subjects.join(","),refresh:String(Date.now())});
        const r=await fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{cache:"no-store"});
        if(!r.ok)throw new Error("Industry Pulse unavailable");
        const data=await r.json();
        if(!cancelled)setPulse(normalizeIndustryPulse(data));
      }catch{}finally{if(!cancelled)setLoading(false);}
    };
    load();
    return()=>{cancelled=true};
  },[role,subjects.join(",")]);

  useEffect(()=>{
    const timer=setInterval(()=>{
      const params=new URLSearchParams({role,subjects:subjects.join(","),refresh:String(Date.now())});
      fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{cache:"no-store"}).then(r=>r.ok?r.json():null).then(data=>{if(data)setPulse(normalizeIndustryPulse(data));}).catch(()=>{});
    },60*60*1000);
    return()=>clearInterval(timer);
  },[role,subjects.join(",")]);

  const market=pulse?.market_signal||pulse?.daily_market||{};
  const skills=Array.isArray(market?.skills)?market.skills:[];
  const dates=[...new Set(skills.flatMap(s=>(Array.isArray(s?.series)?s.series:[]).map(p=>String(p?.date||"").slice(0,10)).filter(d=>/^\d{4}-\d{2}-\d{2}$/.test(d))))].sort().slice(-(Number(market?.requested_window_days)||7));
  const chartSkills=skills.map(s=>{const map=new Map((Array.isArray(s?.series)?s.series:[]).map(p=>[String(p?.date||"").slice(0,10),Number(p?.value)]));const points=dates.map(date=>({date,value:map.get(date)})).filter(p=>Number.isFinite(p.value));return points.length?{...s,points}:null}).filter(Boolean).slice(0,6);
  const activeName=selectedSkill||chartSkills[0]?.skill||"";
  const active=chartSkills.find(s=>s.skill===activeName)||chartSkills[0];
  const values=active?.points?.map(p=>p.value)||[];
  const yMin=values.length?Math.max(0,Math.floor(Math.min(...values)-3)):0;
  const yMax=values.length?Math.ceil(Math.max(...values)+3):100;
  const ySpan=Math.max(yMax-yMin,1);
  const xFor=i=>70+(i/Math.max(active?.points?.length-1,1))*840;
  const yFor=v=>285-((v-yMin)/ySpan)*225;
  const points=active?.points||[];
  const path=points.map((p,i)=>{const x=xFor(i),y=yFor(p.value);if(i===0)return `M ${x.toFixed(1)} ${y.toFixed(1)}`;const prev=points[i-1],px=xFor(i-1),py=yFor(prev.value),cx=(px+x)/2;return `C ${cx.toFixed(1)} ${py.toFixed(1)}, ${cx.toFixed(1)} ${y.toFixed(1)}, ${x.toFixed(1)} ${y.toFixed(1)}`;}).join(" ");
  const area=path?`${path} L ${xFor(Math.max(points.length-1,0)).toFixed(1)} 285 L ${xFor(0).toFixed(1)} 285 Z`:"";
  const latest=market?.latest_snapshot||dates[dates.length-1]||null;
  const latestPoint=points[points.length-1];
  const latestValue=active?.current_demand_pct!=null?Number(active.current_demand_pct):(latestPoint?.value??null);
  const delta=active?.delta_pp!=null?Number(active.delta_pp):null;

  return <><style>{FORGE_MARKET_DETAIL_CSS}</style><main className="forge-market-detail"><div className="forge-market-detail-grid"/><div className="forge-market-detail-shell">
    <div className="forge-market-detail-top"><button className="forge-market-back" onClick={()=>navigate("/student")}><ChevronLeft size={15}/> BACK TO MY FORGE</button><span className="forge-market-live"><i/> LIVE MARKET INTELLIGENCE</span></div>
    <section className="forge-market-hero"><div><span className="forge-market-eyebrow">INDUSTRY PULSE · MARKET INTELLIGENCE</span><h1>What is changing around <em>{role}?</em></h1><p>FORGE turns daily active-job-listing evidence into a readable market signal. Select a skill to inspect its real observed movement, latest demand and day-by-day history.</p></div>{active&&<div className="forge-market-live-card"><small>LATEST LIVE SIGNAL</small><strong>{latestValue!=null?`${latestValue.toFixed(1)}%`:"—"}</strong><span>{active.skill} · {latest||"waiting for source"}</span></div>}</section>
    {loading?<div className="forge-market-main" style={{padding:30,color:"rgba(255,255,255,.5)"}}>Reading live market evidence…</div>:!chartSkills.length?<div className="forge-market-main" style={{padding:30,color:"rgba(255,255,255,.5)"}}>No real daily market observations are available yet.</div>:<>
      <section className="forge-market-main"><div className="forge-market-toolbar"><div><h2>Daily skill demand</h2><p>Observed share of active tech job listings · real source observations only</p></div><div className="forge-market-source"><strong>{market?.source||"Datamata Skill Scarcity Index"}</strong>Latest source: {latest||"—"}</div></div>
        <div className="forge-market-chart-area"><div className="forge-market-chart-head"><span>{active.skill?.toUpperCase()} · {dates.length}-DAY OBSERVED MOVEMENT</span><strong>{latestValue!=null?`${latestValue.toFixed(1)}% demand`:"—"}{delta!=null&&<span style={{marginLeft:10,color:delta>0?"#73e9b4":delta<0?"#ff82a7":"rgba(255,255,255,.45)"}}>{delta>=0?"+":""}{delta.toFixed(1)} pp</span>}</strong></div>
          <div className="forge-market-svg-wrap"><svg className="forge-market-svg" viewBox="0 0 980 350" role="img" aria-label={`${active.skill} daily demand trend`}><defs><linearGradient id="forgeMarketFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#6fe8ff" stopOpacity=".28"/><stop offset="100%" stopColor="#6fe8ff" stopOpacity="0"/></linearGradient></defs>{[0,1,2,3,4].map(i=>{const y=60+i*56.25;const v=yMax-(i/4)*ySpan;return <Fragment key={i}><line x1="70" y1={y} x2="910" y2={y} className="forge-market-gridline"/><text x="12" y={y+4} className="forge-market-axis-label">{v.toFixed(0)}%</text></Fragment>})}{area&&<path d={area} className="forge-market-area"/>}{path&&<path d={path} className="forge-market-line"/>}{points.map((p,i)=><g key={p.date}><circle cx={xFor(i)} cy={yFor(p.value)} r={i===points.length-1?7:5} className={`forge-market-point ${i===points.length-1?"latest":""}`}/><text x={xFor(i)} y="320" textAnchor="middle" className="forge-market-date">{p.date.slice(5)}</text>{i===points.length-1&&<><rect x={xFor(i)-48} y={Math.max(18,yFor(p.value)-48)} width="96" height="30" rx="8" className="forge-market-tooltip"/><text x={xFor(i)} y={Math.max(37,yFor(p.value)-29)} textAnchor="middle" className="forge-market-tooltip-text">{p.value.toFixed(1)}%</text></>}</g>)}</svg></div></div>
        <div className="forge-market-skills">{chartSkills.map(s=>{const d=s.delta_pp==null?null:Number(s.delta_pp);return <button key={s.skill} className={`forge-market-skill ${s.skill===active.skill?"active":""}`} onClick={()=>setSelectedSkill(s.skill)}><small>SKILL SIGNAL</small><strong>{s.skill}</strong><b>{Number(s.current_demand_pct||0).toFixed(1)}%</b><em className={d>0?"up":d<0?"down":"flat"}>{d==null?"No movement":`${d>=0?"+":""}${d.toFixed(1)} pp vs prior day`}</em></button>})}</div>
      </section>
      <div className="forge-market-explain"><section className="forge-market-info"><h3>How should you read this?</h3><p><b>Demand %</b> is the observed share of active tech job listings containing the skill. <b>Move</b> is the latest percentage-point change versus the prior source observation. This is market evidence — not a stock price, salary forecast or prediction.</p><div className="forge-market-flow"><div><b>01 · SOURCE</b><span>Daily active job-listing observations</span></div><div><b>02 · FORGE</b><span>Normalizes dates and skill signals</span></div><div><b>03 · YOU</b><span>Use the movement to prioritize learning</span></div></div><div className="forge-market-note">{latest==="2026-10-05"&&!dates.includes("2026-10-06")?"Oct 06 is not published by the source yet. FORGE deliberately shows the latest verified observation instead of inventing a value.":`Latest verified source observation: ${latest||"—"}.`}</div></section>
        <section className="forge-market-table"><h3>Latest skill snapshot</h3><div className="forge-market-table-row head"><span>SKILL</span><span>DEMAND</span><span>MOVE</span></div>{chartSkills.map(s=>{const d=s.delta_pp==null?null:Number(s.delta_pp);return <div className="forge-market-table-row" key={s.skill}><strong>{s.skill}</strong><span>{Number(s.current_demand_pct||0).toFixed(1)}%</span><span style={{color:d>0?"#73e9b4":d<0?"#ff82a7":undefined}}>{d==null?"—":`${d>=0?"+":""}${d.toFixed(1)} pp`}</span></div>})}</section></div>
    </>}
  </div></main></>;
}

const FORGE_STUDENT_IDENTITY_CSS=`.forge-auth-page{min-height:100vh;position:relative;overflow:hidden;background:#171221;color:#f8f5fc;display:grid;place-items:center;padding:42px 24px;isolation:isolate}.forge-auth-grid,.forge-myforge-grid{position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(196,157,255,.065) 1px,transparent 1px),linear-gradient(90deg,rgba(196,157,255,.065) 1px,transparent 1px);background-size:52px 52px}.forge-auth-glow{position:absolute;border-radius:50%;pointer-events:none}.forge-auth-glow-a{width:500px;height:500px;right:-180px;top:-230px;background:radial-gradient(circle,rgba(155,76,255,.25),transparent 68%)}.forge-auth-glow-b{width:430px;height:430px;left:-170px;bottom:-250px;background:radial-gradient(circle,rgba(64,129,255,.10),transparent 70%)}.forge-auth-shell{position:relative;z-index:2;width:min(480px,100%)}.forge-auth-brand{display:flex;align-items:center;gap:11px;background:none;border:0;color:#fff;padding:0;margin:0 0 23px;cursor:pointer;text-align:left}.forge-auth-mark{width:42px;height:42px;display:grid;place-items:center;border:1px solid rgba(194,150,255,.2);border-radius:11px;background:rgba(10,7,17,.75)}.forge-auth-mark img{width:25px;height:25px;object-fit:contain}.forge-auth-brand strong{display:block;font-size:18px;letter-spacing:.18em}.forge-auth-brand small{display:block;margin-top:2px;color:rgba(236,224,250,.38);font-size:8px;letter-spacing:.12em}.forge-auth-card{padding:34px;border:1px solid rgba(202,162,255,.18);border-radius:24px;background:linear-gradient(145deg,rgba(48,32,68,.9),rgba(21,15,31,.97));box-shadow:0 30px 100px rgba(20,8,35,.42),inset 0 1px rgba(255,255,255,.06);backdrop-filter:blur(20px)}.forge-auth-meta{display:flex;justify-content:space-between;color:rgba(214,178,255,.66);font-size:9px;font-weight:900;letter-spacing:.15em}.forge-auth-meta span{display:flex;gap:7px;align-items:center}.forge-auth-meta i,.forge-dashboard-kicker i{width:18px;height:1px;background:#b679ff;display:inline-block;box-shadow:0 0 10px rgba(174,104,255,.8)}.forge-auth-meta b{color:rgba(255,255,255,.22)}.forge-auth-card h1{margin:18px 0 11px;font-size:45px;line-height:.94;letter-spacing:-.055em}.forge-auth-card h1 em,.forge-myforge-main h1 em,.forge-pulse-head h2 em,.forge-capability-card h2 em{font-style:normal;color:#b45dff}.forge-auth-card>p{margin:0 0 26px;color:rgba(236,225,248,.52);font-size:12px;line-height:1.7}.forge-auth-form{display:grid;gap:13px}.forge-auth-form label{display:grid;gap:7px}.forge-auth-form label span{font-size:8px;font-weight:900;letter-spacing:.14em;color:rgba(240,229,252,.4)}.forge-auth-form input{box-sizing:border-box;width:100%;border:1px solid rgba(207,167,255,.13);background:rgba(8,6,15,.38);color:#fff;border-radius:11px;padding:13px 14px;outline:none;font:inherit;font-size:12px}.forge-auth-form input:focus{border-color:rgba(188,121,255,.65);box-shadow:0 0 0 3px rgba(163,86,255,.1)}.forge-auth-form input::placeholder{color:rgba(255,255,255,.22)}.forge-auth-error{display:flex;gap:7px;align-items:flex-start;padding:10px 12px;border:1px solid rgba(255,111,146,.23);background:rgba(255,75,117,.05);border-radius:10px;color:#ffb4c8;font-size:10px;line-height:1.5}.forge-auth-submit{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:3px;border:0;border-radius:11px;padding:14px 17px;background:linear-gradient(100deg,#a34dff,#d06dff);color:#17091f;font:inherit;font-size:11px;font-weight:900;cursor:pointer;box-shadow:0 13px 35px rgba(150,65,240,.24)}.forge-auth-submit:disabled{opacity:.55;cursor:wait}.forge-auth-switch{display:flex;justify-content:center;gap:7px;margin-top:21px;color:rgba(235,224,247,.35);font-size:10px}.forge-auth-switch button{border:0;background:none;color:#c68aff;font:inherit;font-weight:800;cursor:pointer}.forge-auth-foot{display:flex;justify-content:space-between;gap:15px;margin-top:15px;color:rgba(231,219,244,.25);font-size:8px}.forge-auth-foot span:first-child{display:flex;align-items:center;gap:5px}.forge-myforge-page{min-height:100vh;display:flex;background:linear-gradient(145deg,#171221,#21172e);color:#f7f4fc;position:relative;isolation:isolate}.forge-myforge-page>.forge-myforge-grid{position:fixed;z-index:0}.forge-myforge-sidebar{position:fixed;z-index:3;left:0;top:0;bottom:0;width:245px;padding:22px 15px 16px;border-right:1px solid rgba(205,164,255,.12);background:rgba(16,11,25,.93);backdrop-filter:blur(18px);display:flex;flex-direction:column}.forge-myforge-brand{display:flex;align-items:center;gap:10px;padding:0 9px 22px}.forge-myforge-brand img{width:35px;height:35px;object-fit:contain}.forge-myforge-brand strong{display:block;font-size:14px;letter-spacing:.18em}.forge-myforge-brand small{display:block;color:rgba(235,223,247,.33);font-size:7px;margin-top:2px}.forge-myforge-sidebar nav{display:grid;gap:3px}.forge-myforge-sidebar nav button{display:flex;align-items:center;gap:9px;border:0;background:transparent;color:rgba(239,230,247,.5);padding:9px 11px;border-radius:9px;text-align:left;font:inherit;font-size:10px;cursor:pointer}.forge-myforge-sidebar nav button:hover{color:#fff;background:rgba(177,106,255,.07)}.forge-myforge-sidebar nav button.active{color:#fff;background:linear-gradient(90deg,rgba(156,78,255,.24),rgba(156,78,255,.05));box-shadow:inset 2px 0 #b96cff}.forge-nav-label{margin:15px 10px 5px;color:rgba(203,166,255,.36);font-size:7px;font-weight:900;letter-spacing:.16em}.forge-myforge-profile{margin-top:auto;display:flex;align-items:center;gap:9px;width:100%;border:1px solid rgba(202,161,255,.11);background:rgba(255,255,255,.025);border-radius:12px;padding:9px;text-align:left;color:#fff;cursor:pointer}.forge-myforge-profile>span:nth-child(2){min-width:0;flex:1}.forge-myforge-profile strong,.forge-myforge-profile small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.forge-myforge-profile strong{font-size:10px}.forge-myforge-profile small{font-size:7px;color:rgba(238,225,249,.33);margin-top:2px}.forge-avatar{display:grid;place-items:center;width:30px;height:30px;border-radius:10px;color:#fff;font-size:10px;font-weight:900;border:1px solid rgba(255,255,255,.18);flex:0 0 auto}.forge-avatar.violet{background:linear-gradient(145deg,#9c58ff,#4820a7)}.forge-avatar.cyan{background:linear-gradient(145deg,#42c8e8,#3e43b6)}.forge-avatar.pink{background:linear-gradient(145deg,#ff74dc,#7433c5)}.forge-avatar.blue{background:linear-gradient(145deg,#6b8dff,#392a9b)}.forge-myforge-main{position:relative;z-index:1;margin-left:245px;width:calc(100% - 245px);padding:45px clamp(25px,4vw,62px) 70px}.forge-myforge-top{display:flex;justify-content:space-between;gap:30px;align-items:flex-start;max-width:1250px;margin:0 auto 28px}.forge-dashboard-kicker{display:inline-flex;align-items:center;gap:8px;color:rgba(214,178,255,.68);font-size:9px;font-weight:900;letter-spacing:.16em}.forge-myforge-main h1{margin:11px 0 8px;font-size:clamp(35px,4.2vw,58px);line-height:.95;letter-spacing:-.055em}.forge-myforge-top p{margin:0;color:rgba(236,224,249,.44);font-size:12px}.forge-myforge-user{display:flex;align-items:center;gap:8px}.forge-myforge-user strong,.forge-myforge-user small{display:block}.forge-myforge-user strong{font-size:9px}.forge-myforge-user small{margin-top:2px;color:rgba(235,223,247,.34);font-size:7px}.forge-dashboard-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;max-width:1250px;margin:0 auto 15px}.forge-dash-card{min-height:174px;padding:17px;border:1px solid rgba(205,164,255,.13);border-radius:17px;background:linear-gradient(145deg,rgba(57,35,82,.73),rgba(28,20,41,.92));color:#fff;text-align:left;box-shadow:inset 0 1px rgba(255,255,255,.05);transition:.25s;cursor:pointer}.forge-dash-card:hover{transform:translateY(-4px);border-color:rgba(195,144,255,.34);box-shadow:0 24px 60px rgba(61,19,102,.2)}.forge-card-head{display:flex;justify-content:space-between;align-items:center;color:rgba(226,207,247,.4);font-size:7px;font-weight:900;letter-spacing:.13em}.forge-dash-card>strong{display:block;margin-top:24px;font-size:19px;letter-spacing:-.035em}.forge-dash-card>small{display:block;color:rgba(234,221,248,.38);font-size:8px;margin-top:5px}.forge-card-meter{height:4px;margin-top:21px;background:rgba(255,255,255,.07);border-radius:99px;overflow:hidden}.forge-card-meter span{display:block;height:100%;background:linear-gradient(90deg,#8c4dff,#e47aff);border-radius:99px}.forge-dash-card>em{display:block;margin-top:7px;color:rgba(212,177,247,.42);font-size:7px;font-style:normal}.forge-task-row{display:flex;justify-content:space-between;margin-top:27px;color:rgba(239,226,249,.5);font-size:8px}.forge-task-row span{display:flex;align-items:center;gap:5px}.forge-task-row b{color:#d49aff}.forge-dash-card>strong small{display:inline;color:rgba(236,222,248,.3);font-size:11px}.forge-dash-card p{margin:5px 0 0;color:rgba(235,222,248,.37);font-size:8px;line-height:1.5}.forge-mini-bars{display:flex;align-items:flex-end;gap:4px;height:32px;margin-top:16px}.forge-mini-bars i{display:block;flex:1;border-radius:4px 4px 1px 1px;background:linear-gradient(#c47cff,#6033b0)}.forge-streak-dots{display:flex;gap:5px;margin-top:22px}.forge-streak-dots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.11)}.forge-streak-dots i.on{background:#b568ff;box-shadow:0 0 13px rgba(181,104,255,.8)}.forge-pulse-card,.forge-capability-card{max-width:1250px;margin:0 auto 15px;padding:23px;border:1px solid rgba(205,164,255,.13);border-radius:19px;background:linear-gradient(145deg,rgba(45,28,67,.75),rgba(22,15,33,.94));box-shadow:inset 0 1px rgba(255,255,255,.05)}.forge-pulse-head{display:flex;justify-content:space-between;gap:30px}.forge-pulse-head h2,.forge-capability-card h2{margin:10px 0 6px;font-size:25px;letter-spacing:-.04em}.forge-pulse-head p,.forge-capability-card p{margin:0;color:rgba(236,224,248,.41);font-size:9px;line-height:1.65}.forge-pulse-head button,.forge-capability-actions button{display:flex;align-items:center;gap:7px;height:max-content;border:1px solid rgba(193,139,255,.23);background:rgba(172,99,255,.08);color:#dba7ff;border-radius:9px;padding:9px 12px;font:inherit;font-size:8px;font-weight:900;cursor:pointer}.forge-pulse-market{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:18px;margin-top:21px;padding-top:15px;border-top:1px solid rgba(255,255,255,.07)}
.forge-pulse-market-chart{min-width:0}
.forge-pulse-market-chart-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:4px;color:rgba(233,219,246,.38);font-size:7px;font-weight:900;letter-spacing:.14em}
.forge-pulse-market-chart-head small{font-size:7px;letter-spacing:0;font-weight:500;color:rgba(233,219,246,.27)}
.forge-pulse-market-chart svg{display:block;width:100%;height:180px;overflow:visible}
.forge-pulse-grid{stroke:rgba(255,255,255,.055);stroke-width:1;stroke-dasharray:3 5}
.forge-pulse-y{fill:rgba(255,255,255,.22);font-size:7px;font-family:inherit}
.forge-pulse-line{stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 5px currentColor)}
.forge-pulse-line-0{stroke:#65e6ff}.forge-pulse-line-1{stroke:#a78bfa}.forge-pulse-line-2{stroke:#6ee7b7}.forge-pulse-line-3{stroke:#fbbf72}.forge-pulse-line-4{stroke:#fb7185}.forge-pulse-line-5{stroke:#c4b5fd}
.forge-pulse-point{r:3.5;stroke:#171221;stroke-width:1.5}
.forge-pulse-point-0{fill:#65e6ff}.forge-pulse-point-1{fill:#a78bfa}.forge-pulse-point-2{fill:#6ee7b7}.forge-pulse-point-3{fill:#fbbf72}.forge-pulse-point-4{fill:#fb7185}.forge-pulse-point-5{fill:#c4b5fd}
.forge-pulse-dates{display:grid;grid-template-columns:repeat(var(--forge-pulse-date-count,5),1fr);margin:0 8px 0 34px;color:rgba(255,255,255,.28);font-size:7px;text-align:center}
.forge-pulse-note{margin-top:8px;padding:7px 9px;border:1px solid rgba(255,255,255,.06);border-radius:8px;color:rgba(255,255,255,.27);font-size:7px;line-height:1.45}
.forge-pulse-market-list{padding:10px 11px;border:1px solid rgba(255,255,255,.065);border-radius:12px;background:rgba(0,0,0,.10)}
.forge-pulse-market-list-head,.forge-pulse-market-item{display:grid;grid-template-columns:minmax(0,1fr) 52px 48px;gap:8px;align-items:center}
.forge-pulse-market-list-head{padding:0 2px 7px;color:rgba(255,255,255,.23);font-size:6px;letter-spacing:.12em;font-weight:900;border-bottom:1px solid rgba(255,255,255,.055)}
.forge-pulse-market-item{min-height:31px;border-bottom:1px solid rgba(255,255,255,.045)}
.forge-pulse-market-item:last-child{border-bottom:0}
.forge-pulse-market-item strong{font-size:8px;display:flex;align-items:center;gap:6px;min-width:0}
.forge-pulse-market-item b{font-size:8px;text-align:right;color:#d79cff}
.forge-pulse-market-item em{font-size:7px;font-style:normal;text-align:right}.forge-pulse-market-item em.up{color:#72e6ad}.forge-pulse-market-item em.down{color:#ff91aa}.forge-pulse-market-item em.flat{color:rgba(255,255,255,.35)}
.forge-pulse-dot{width:5px;height:5px;border-radius:50%;display:inline-block;flex:0 0 auto}
.forge-pulse-dot-0{background:#65e6ff;box-shadow:0 0 8px rgba(101,230,255,.5)}.forge-pulse-dot-1{background:#a78bfa}.forge-pulse-dot-2{background:#6ee7b7}.forge-pulse-dot-3{background:#fbbf72}.forge-pulse-dot-4{background:#fb7185}.forge-pulse-dot-5{background:#c4b5fd}
@media(max-width:900px){.forge-pulse-market{grid-template-columns:1fr}.forge-pulse-market-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 12px}.forge-pulse-market-list-head{display:none}}
.forge-pulse-bars{display:grid;gap:10px;margin-top:21px;padding-top:15px;border-top:1px solid rgba(255,255,255,.07)}.forge-pulse-row{display:grid;grid-template-columns:190px 1fr 50px;gap:13px;align-items:center}.forge-pulse-row strong,.forge-pulse-row small{display:block}.forge-pulse-row strong{font-size:9px}.forge-pulse-row small{margin-top:3px;color:rgba(233,219,246,.27);font-size:7px}.forge-pulse-track{height:8px;border-radius:99px;background:rgba(255,255,255,.055);overflow:hidden}.forge-pulse-track span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#6f43e9,#dc76ff)}.forge-pulse-row>b{color:#d79cff;font-size:8px;text-align:right}.forge-pulse-state{display:flex;align-items:center;gap:9px;margin-top:18px;padding:20px;border:1px dashed rgba(201,158,255,.13);border-radius:12px;color:rgba(236,224,249,.42);font-size:9px}.forge-pulse-state span{display:grid;gap:3px}.forge-pulse-state strong{color:#fff}.forge-capability-card{display:grid;grid-template-columns:1fr 1.6fr;gap:24px;align-items:center}.forge-capability-flow{display:flex;align-items:center;justify-content:center;gap:7px}.forge-capability-flow>div{min-width:75px;padding:10px 8px;border:1px solid rgba(199,151,255,.12);border-radius:10px;background:rgba(255,255,255,.02)}.forge-capability-flow small,.forge-capability-flow strong{display:block}.forge-capability-flow small{color:rgba(216,180,250,.3);font-size:7px}.forge-capability-flow strong{margin-top:7px;font-size:7px;letter-spacing:.06em}.forge-capability-flow>svg{color:#a86dff}.forge-capability-actions{grid-column:2;display:flex;gap:8px}.forge-capability-actions button.ghost{background:transparent;color:rgba(235,221,247,.42)}@media(max-width:1100px){.forge-myforge-sidebar{width:205px}.forge-myforge-main{margin-left:205px;width:calc(100% - 205px)}.forge-dashboard-grid{grid-template-columns:repeat(2,1fr)}.forge-capability-card{grid-template-columns:1fr}.forge-capability-actions{grid-column:auto}}@media(max-width:760px){.forge-myforge-page{display:block}.forge-myforge-sidebar{position:relative;width:auto;bottom:auto;border-right:0;border-bottom:1px solid rgba(205,164,255,.12)}.forge-myforge-main{margin-left:0;width:auto;padding:28px 16px 50px}.forge-myforge-sidebar nav{grid-template-columns:repeat(2,1fr)}.forge-nav-label{grid-column:1/-1}.forge-myforge-profile{margin-top:14px}.forge-myforge-top{display:block}.forge-myforge-user{margin-top:14px}.forge-dashboard-grid{grid-template-columns:1fr}.forge-pulse-head{display:block}.forge-pulse-head button{margin-top:13px}.forge-pulse-row{grid-template-columns:1fr 80px 35px}.forge-capability-flow{overflow:auto;justify-content:flex-start;padding-bottom:4px}.forge-capability-actions{display:flex;flex-wrap:wrap}.forge-auth-card{padding:24px}.forge-auth-card h1{font-size:38px}.forge-auth-foot{display:block}.forge-auth-foot span{display:block;margin-top:5px}}
/* MY FORGE VISUAL SYSTEM — premium student dashboard */
.forge-myforge-page{background:radial-gradient(900px 560px at 70% 0%,rgba(120,67,255,.17),transparent 58%),radial-gradient(700px 500px at 25% 80%,rgba(0,202,255,.08),transparent 62%),#100b1c;overflow:hidden}
.forge-myforge-page:after{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(circle at 80% 20%,rgba(255,255,255,.035),transparent 30%);mix-blend-mode:screen;z-index:0}
.forge-myforge-sidebar{width:252px;background:linear-gradient(180deg,rgba(12,8,20,.96),rgba(19,11,31,.94));border-right:1px solid rgba(210,173,255,.14);box-shadow:18px 0 60px rgba(5,2,12,.18)}
.forge-brand-mark{width:39px;height:39px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(145deg,#24133c,#0a0710);border:1px solid rgba(205,157,255,.25);box-shadow:0 0 25px rgba(159,83,255,.15)}
.forge-myforge-brand img{width:26px;height:26px;filter:drop-shadow(0 0 8px rgba(183,106,255,.42))}
.forge-myforge-brand strong{font-size:15px}.forge-myforge-brand small{font-size:7px;letter-spacing:.05em}
.forge-myforge-sidebar nav button{padding:10px 11px;font-size:10px;transition:all .22s ease}.forge-myforge-sidebar nav button:hover{transform:translateX(3px);background:rgba(167,101,255,.09);color:#fff}.forge-myforge-sidebar nav button.active{background:linear-gradient(100deg,rgba(145,67,255,.28),rgba(61,28,97,.24));box-shadow:inset 2px 0 #c16cff,0 7px 22px rgba(112,44,189,.12)}
.forge-nav-label{margin-top:18px;color:rgba(200,158,255,.43);font-size:7px}
.forge-myforge-profile{border-color:rgba(208,168,255,.18);background:linear-gradient(135deg,rgba(255,255,255,.055),rgba(151,74,255,.055));box-shadow:inset 0 1px rgba(255,255,255,.05);transition:.2s}.forge-myforge-profile:hover{transform:translateY(-2px);border-color:rgba(210,164,255,.34)}
.forge-avatar{width:34px;height:34px;border-radius:11px;box-shadow:0 0 18px rgba(154,83,255,.24)}
.forge-myforge-main{margin-left:252px;width:calc(100% - 252px);padding:42px clamp(25px,4vw,64px) 75px}
.forge-myforge-top{max-width:1320px;margin-bottom:26px}.forge-myforge-main h1{font-size:clamp(38px,4.7vw,64px);text-shadow:0 0 34px rgba(190,119,255,.08)}.forge-wave{display:inline-block;font-size:.62em;filter:drop-shadow(0 0 10px rgba(255,189,90,.3));animation:forgeWave .9s ease-in-out infinite alternate}@keyframes forgeWave{from{transform:rotate(-8deg)}to{transform:rotate(12deg)}}
.forge-myforge-top p{font-size:12px}.forge-myforge-user{padding:7px 10px;border:1px solid rgba(205,165,255,.12);border-radius:14px;background:rgba(255,255,255,.025)}
.forge-dashboard-grid{max-width:1320px;gap:14px}.forge-dash-card{position:relative;overflow:hidden;min-height:194px;padding:19px;border-radius:20px;box-shadow:inset 0 1px rgba(255,255,255,.08),0 18px 45px rgba(12,3,26,.18);transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease}.forge-dash-card:before{content:"";position:absolute;inset:-50%;pointer-events:none;background:radial-gradient(circle at 75% 20%,rgba(255,255,255,.16),transparent 27%);opacity:.5}.forge-dash-card:hover{transform:translateY(-7px);box-shadow:0 28px 70px rgba(56,16,100,.26),inset 0 1px rgba(255,255,255,.12)}
.forge-card-role{background:linear-gradient(145deg,rgba(48,31,91,.95),rgba(26,17,48,.96));border-color:rgba(147,117,255,.27)}.forge-card-priority{background:linear-gradient(145deg,rgba(83,42,34,.94),rgba(39,22,31,.97));border-color:rgba(255,155,91,.27)}.forge-card-reflect{background:linear-gradient(145deg,rgba(18,61,78,.94),rgba(18,28,49,.97));border-color:rgba(76,207,255,.25)}.forge-card-streak{background:linear-gradient(145deg,rgba(88,40,23,.96),rgba(39,19,29,.97));border-color:rgba(255,127,67,.31)}
.forge-card-head{color:rgba(240,228,255,.48)}.forge-card-title-row{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:23px}.forge-dash-card>strong{font-size:20px;margin-top:0;position:relative}.forge-percent-badge{padding:6px 8px;border-radius:999px;background:rgba(190,125,255,.14);border:1px solid rgba(210,163,255,.28);color:#e5c5ff;font-size:11px;font-weight:900;box-shadow:0 0 18px rgba(177,91,255,.14)}.forge-card-meta{display:flex;justify-content:space-between;align-items:center;margin-top:9px;font-size:7px;color:rgba(235,218,249,.35);letter-spacing:.08em}.forge-card-meta b{color:#dcb4ff;font-size:8px}.forge-card-meter{height:6px;margin-top:18px}.forge-card-meter span{background:linear-gradient(90deg,#7c55ff,#d77aff,#ffb1f1);box-shadow:0 0 12px rgba(186,103,255,.65)}
.forge-priority-kicker{margin-top:20px;color:#ffb28e;font-size:7px;font-weight:900;letter-spacing:.15em}.forge-card-priority>strong{font-size:23px;margin-top:7px}.forge-planner-task{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:19px;color:rgba(255,235,225,.56);font-size:8px}.forge-planner-task span{display:flex;align-items:center;gap:5px}.forge-planner-task b{color:#ffc19c;font-size:8px}.forge-task-progress{height:5px;margin-top:10px;background:rgba(255,255,255,.07);border-radius:99px;overflow:hidden}.forge-task-progress span{display:block;height:100%;background:linear-gradient(90deg,#ff7f54,#ffd36b);box-shadow:0 0 14px rgba(255,126,75,.55)}.forge-task-footer{display:flex;justify-content:space-between;margin-top:9px;color:rgba(255,226,216,.32);font-size:7px}.forge-task-footer b{color:#ffb78f}
.forge-reflect-top{display:flex;justify-content:space-between;align-items:center;margin-top:19px}.forge-reflect-top strong{font-size:27px}.forge-reflect-top strong small{font-size:10px;color:rgba(225,246,255,.35)}.forge-reflect-top span{display:block;color:rgba(215,240,248,.4);font-size:7px;margin-top:3px}.forge-live-chip{display:flex;align-items:center;gap:5px;padding:5px 7px;border:1px solid rgba(99,224,255,.2);border-radius:999px;color:#89eaff;font-size:6px;font-weight:900;letter-spacing:.12em}.forge-live-chip i{width:5px;height:5px;border-radius:50%;background:#58e6ff;box-shadow:0 0 9px #58e6ff;animation:forgeLivePulse 1.1s infinite}@keyframes forgeLivePulse{50%{opacity:.35;transform:scale(.7)}}
.forge-reflect-chart{height:52px;display:flex;align-items:flex-end;gap:7px;margin-top:14px}.forge-reflect-day{height:100%;flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:5px}.forge-reflect-day i{width:100%;min-height:8px;border-radius:5px 5px 2px 2px;background:linear-gradient(180deg,#73e9ff,#4b6cff 72%,#392d79);box-shadow:0 0 12px rgba(72,184,255,.18);animation:forgeBars 1.5s ease-in-out infinite alternate;transform-origin:bottom}@keyframes forgeBars{from{filter:brightness(.82);transform:scaleY(.91)}to{filter:brightness(1.16);transform:scaleY(1.02)}}.forge-reflect-day:nth-child(2) i{animation-delay:.12s}.forge-reflect-day:nth-child(3) i{animation-delay:.24s}.forge-reflect-day:nth-child(4) i{animation-delay:.36s}.forge-reflect-day:nth-child(5) i{animation-delay:.48s}.forge-reflect-day:nth-child(6) i{animation-delay:.6s}.forge-reflect-day:nth-child(7) i{animation-delay:.72s}.forge-reflect-day span{font-size:6px;color:rgba(215,240,248,.32)}.forge-reflect-foot{display:flex;justify-content:space-between;margin-top:9px;color:rgba(215,240,248,.35);font-size:7px}.forge-reflect-foot b{color:#75e8ff}
.forge-fire-wrap{height:66px;display:flex;align-items:flex-end;gap:10px;margin-top:9px}.forge-fire-wrap>strong{font-size:27px;line-height:1;margin-bottom:5px;color:#fff1e8}.forge-fire{position:relative;width:38px;height:56px;filter:drop-shadow(0 0 12px rgba(255,90,22,.7))}.forge-fire i{position:absolute;bottom:0;left:50%;display:block;width:28px;height:40px;transform:translateX(-50%) rotate(4deg);border-radius:60% 40% 55% 45%;background:linear-gradient(180deg,#ffe26d 0%,#ff9d22 38%,#ff4823 72%,#c91d27 100%);box-shadow:0 0 14px rgba(255,99,24,.55);transform-origin:50% 100%;animation:forgeFlame .58s ease-in-out infinite alternate}.forge-fire i:nth-child(2){width:19px;height:31px;left:44%;bottom:1px;background:linear-gradient(180deg,#fff7c4,#ffd53c 35%,#ff6a1c 72%,#ed2525);animation-duration:.43s;animation-delay:-.18s}.forge-fire i:nth-child(3){width:12px;height:23px;left:61%;bottom:1px;background:linear-gradient(180deg,#fff,#ffe46a 40%,#ff8a1d);animation-duration:.36s;animation-delay:-.31s}@keyframes forgeFlame{from{transform:translateX(-50%) rotate(-7deg) scaleY(.91) scaleX(.94)}to{transform:translateX(-50%) rotate(8deg) scaleY(1.08) scaleX(1.03)}}.forge-card-streak p{color:rgba(255,224,212,.43)}.forge-streak-dots i.on{background:#ff7a35;box-shadow:0 0 16px rgba(255,92,29,.95);animation:forgeLivePulse .9s infinite}
.forge-pulse-card,.forge-capability-card{max-width:1320px;border-radius:22px;box-shadow:inset 0 1px rgba(255,255,255,.08),0 24px 70px rgba(33,8,54,.16)}.forge-pulse-card{background:linear-gradient(145deg,rgba(36,27,63,.92),rgba(16,17,34,.96));border-color:rgba(151,128,255,.22)}.forge-pulse-enhanced{position:relative;overflow:hidden}.forge-pulse-enhanced:before{content:"";position:absolute;width:420px;height:240px;right:-100px;top:-100px;background:radial-gradient(circle,rgba(127,94,255,.17),transparent 68%);pointer-events:none}.forge-pulse-head{position:relative;z-index:1}.forge-pulse-head h2{font-size:29px}.forge-live-percent{min-width:160px;padding:13px 15px;border:1px solid rgba(106,234,255,.2);border-radius:15px;background:linear-gradient(145deg,rgba(40,99,113,.18),rgba(28,20,54,.32));box-shadow:0 0 25px rgba(55,213,255,.06)}.forge-live-percent span,.forge-live-percent small{display:block}.forge-live-percent span{font-size:7px;color:#7deaff;font-weight:900;letter-spacing:.14em}.forge-live-percent span i{display:inline-block;width:5px;height:5px;border-radius:50%;background:#69eaff;box-shadow:0 0 9px #69eaff;margin-right:5px;animation:forgeLivePulse 1s infinite}.forge-live-percent strong{display:block;margin:4px 0 2px;font-size:27px;color:#d9fbff;text-shadow:0 0 16px rgba(83,220,255,.3)}.forge-live-percent small{color:rgba(218,244,249,.4);font-size:7px;max-width:150px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.forge-pulse-track{height:9px;background:rgba(255,255,255,.045);box-shadow:inset 0 1px rgba(255,255,255,.05)}.forge-pulse-track span{background:linear-gradient(90deg,#5d65ff,#65dfff,#d875ff);box-shadow:0 0 14px rgba(102,200,255,.3);animation:forgeSignalFlow 2.4s ease-in-out infinite alternate}@keyframes forgeSignalFlow{from{filter:saturate(.85);opacity:.78}to{filter:saturate(1.25);opacity:1}}.forge-pulse-analysis{display:grid;grid-template-columns:auto 1fr 1fr auto;align-items:center;gap:14px;margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,.06)}.forge-pulse-analysis>span{color:rgba(190,174,255,.45);font-size:7px;font-weight:900;letter-spacing:.14em}.forge-pulse-analysis div b,.forge-pulse-analysis div strong{display:block}.forge-pulse-analysis div b{font-size:7px;color:rgba(230,218,250,.35)}.forge-pulse-analysis div strong{margin-top:3px;font-size:9px;color:#d9caff}.forge-pulse-analysis button{border:1px solid rgba(185,145,255,.24);background:rgba(161,96,255,.08);color:#dcaeff;border-radius:9px;padding:9px 12px;font:inherit;font-size:8px;font-weight:900;cursor:pointer;display:flex;gap:7px;align-items:center}
.forge-capability-enhanced{grid-template-columns:1fr 1.7fr;background:linear-gradient(145deg,rgba(54,30,84,.94),rgba(21,15,35,.98));border-color:rgba(194,131,255,.24);position:relative;overflow:hidden}.forge-capability-enhanced:before{content:"";position:absolute;inset:auto -100px -160px auto;width:430px;height:330px;background:radial-gradient(circle,rgba(200,83,255,.13),transparent 68%);pointer-events:none}.forge-capability-copy,.forge-capability-flow,.forge-capability-actions{position:relative;z-index:1}.forge-capability-card h2{font-size:30px}.forge-capability-card p{font-size:10px;max-width:560px}.forge-capability-status{display:inline-flex;flex-direction:column;gap:5px;margin-top:15px;padding:9px 11px;border:1px solid rgba(200,152,255,.16);border-radius:10px;background:rgba(255,255,255,.025)}.forge-capability-status span{font-size:6px;color:#bd8bff;font-weight:900;letter-spacing:.13em}.forge-capability-status span i{display:inline-block;width:5px;height:5px;border-radius:50%;background:#c06dff;box-shadow:0 0 9px #c06dff;margin-right:5px}.forge-capability-status strong{font-size:9px;color:#f0dcff}.forge-capability-flow{gap:8px}.forge-capability-flow>div{min-width:88px;padding:12px 10px;border-radius:13px;background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.015));border-color:rgba(202,158,255,.13);transition:.25s}.forge-capability-flow>div.current{border-color:rgba(208,122,255,.48);background:linear-gradient(145deg,rgba(168,83,255,.2),rgba(60,28,89,.28));box-shadow:0 0 25px rgba(168,82,255,.1);transform:translateY(-5px)}.forge-capability-flow small{font-size:6px;color:rgba(222,190,255,.3)}.forge-capability-flow strong{font-size:7px}.forge-capability-flow span{display:block;margin-top:5px;font-size:5px;color:#d58aff;font-weight:900;letter-spacing:.12em}.forge-capability-flow>svg{color:#bc78ff}.forge-capability-actions{grid-column:2}.forge-capability-actions button{padding:11px 14px;background:linear-gradient(100deg,#9850ff,#d26dff);color:#160a22;box-shadow:0 10px 25px rgba(153,76,255,.2)}.forge-capability-actions button.ghost{background:rgba(255,255,255,.025);color:rgba(235,221,247,.55);box-shadow:none}
@media(max-width:1100px){.forge-myforge-sidebar{width:215px}.forge-myforge-main{margin-left:215px;width:calc(100% - 215px)}.forge-dashboard-grid{grid-template-columns:repeat(2,1fr)}.forge-capability-enhanced{grid-template-columns:1fr}.forge-capability-actions{grid-column:auto}.forge-pulse-analysis{grid-template-columns:1fr 1fr}.forge-live-percent{min-width:140px}}
@media(max-width:760px){.forge-myforge-page{display:block}.forge-myforge-sidebar{position:relative;width:auto;bottom:auto;border-right:0;border-bottom:1px solid rgba(205,164,255,.12)}.forge-myforge-main{margin-left:0;width:auto;padding:28px 16px 50px}.forge-myforge-sidebar nav{grid-template-columns:repeat(2,1fr)}.forge-nav-label{grid-column:1/-1}.forge-myforge-top{display:block}.forge-myforge-user{margin-top:14px;width:max-content}.forge-dashboard-grid{grid-template-columns:1fr}.forge-pulse-head{display:block}.forge-live-percent{margin-top:15px;width:max-content}.forge-pulse-head button{margin-top:13px}.forge-pulse-row{grid-template-columns:1fr 80px 35px}.forge-pulse-analysis{grid-template-columns:1fr 1fr}.forge-pulse-analysis>span{grid-column:1/-1}.forge-capability-flow{overflow:auto;justify-content:flex-start;padding-bottom:8px}.forge-capability-actions{display:flex;flex-wrap:wrap}.forge-capability-actions button{flex:1}.forge-wave{font-size:.7em}}

/* PREMIUM STUDENT ACCESS */
.forge-auth-page-pro{display:block;padding:0;background:#09070f;min-height:100vh}
.forge-auth-page-pro .forge-auth-grid{opacity:.38;background-size:72px 72px}
.forge-auth-page-pro .forge-auth-glow-a{width:760px;height:760px;right:-270px;top:-360px;background:radial-gradient(circle,rgba(144,69,255,.18),transparent 68%)}
.forge-auth-page-pro .forge-auth-glow-b{width:620px;height:620px;left:-330px;bottom:-360px;background:radial-gradient(circle,rgba(42,91,170,.10),transparent 70%)}
.forge-auth-pro-shell{position:relative;z-index:2;min-height:100vh;width:min(1240px,100%);margin:0 auto;display:grid;grid-template-columns:minmax(0,1.08fr) minmax(390px,.72fr);gap:clamp(55px,8vw,120px);align-items:center;padding:60px clamp(28px,5vw,70px);box-sizing:border-box}
.forge-auth-showcase{min-height:610px;display:flex;flex-direction:column;justify-content:space-between;padding:12px 0 8px}
.forge-auth-brand-pro{margin:0!important}.forge-auth-brand-pro .forge-auth-mark{width:46px;height:46px;border-radius:13px;background:linear-gradient(145deg,rgba(153,84,255,.16),rgba(255,255,255,.025));border-color:rgba(198,153,255,.22);box-shadow:0 0 28px rgba(139,72,255,.13)}
.forge-auth-brand-pro strong{font-size:20px;letter-spacing:.2em}.forge-auth-brand-pro small{font-size:8px;letter-spacing:.16em}
.forge-auth-showcase-copy{max-width:700px;margin-top:auto;margin-bottom:65px}.forge-auth-overline{display:inline-flex;align-items:center;gap:10px;color:rgba(205,168,255,.62);font-size:9px;font-weight:900;letter-spacing:.19em}.forge-auth-overline i{width:28px;height:1px;background:#b66aff;box-shadow:0 0 12px rgba(182,106,255,.6)}
.forge-auth-showcase-copy h1{margin:22px 0 18px;font-size:clamp(56px,6.3vw,88px);line-height:.9;letter-spacing:-.065em;font-weight:680;color:#f8f5fb}.forge-auth-showcase-copy h1 em{font-style:normal;color:#a963ff}.forge-auth-showcase-copy p{max-width:610px;margin:0;color:rgba(226,216,239,.5);font-size:14px;line-height:1.85}
.forge-auth-signal-grid{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(255,255,255,.09);border-bottom:1px solid rgba(255,255,255,.07)}.forge-auth-signal-grid>div{min-height:105px;padding:17px 18px;border-right:1px solid rgba(255,255,255,.07)}.forge-auth-signal-grid>div:last-child{border-right:0}.forge-auth-signal-grid strong,.forge-auth-signal-grid span,.forge-auth-signal-grid small{display:block}.forge-auth-signal-grid strong{font-size:9px;color:#aa69ff;letter-spacing:.16em}.forge-auth-signal-grid span{margin-top:13px;font-size:13px;font-weight:750;color:#fff}.forge-auth-signal-grid small{margin-top:5px;color:rgba(227,216,239,.35);font-size:8px;line-height:1.45}.forge-auth-trust{display:flex;justify-content:space-between;gap:20px;color:rgba(223,211,237,.25);font-size:7px;font-weight:800;letter-spacing:.12em}.forge-auth-trust span{display:flex;align-items:center;gap:6px}
.forge-auth-pro-panel{width:100%;box-sizing:border-box;padding:34px 35px;border:1px solid rgba(196,151,255,.16);border-radius:20px;background:linear-gradient(145deg,rgba(29,21,39,.94),rgba(13,10,19,.98));box-shadow:0 35px 100px rgba(0,0,0,.42),inset 0 1px rgba(255,255,255,.06);backdrop-filter:blur(22px)}.forge-auth-pro-panel-head{display:flex;justify-content:space-between;align-items:center;color:rgba(205,167,250,.55);font-size:8px;font-weight:900;letter-spacing:.16em}.forge-auth-pro-panel-head b{color:rgba(255,255,255,.22)}.forge-auth-pro-title h2{margin:26px 0 8px;font-size:34px;line-height:1;letter-spacing:-.045em;color:#fff}.forge-auth-pro-title p{margin:0 0 30px;color:rgba(228,216,239,.4);font-size:11px;line-height:1.65}.forge-auth-form-pro{gap:18px}.forge-auth-form-pro label{gap:8px}.forge-auth-form-pro label span{font-size:7px;color:rgba(231,218,245,.38);letter-spacing:.17em}.forge-auth-form-pro input{height:47px;border-radius:9px;border-color:rgba(208,169,255,.11);background:rgba(4,3,8,.48);padding:0 13px;font-size:11px;transition:border-color .2s,box-shadow .2s,background .2s}.forge-auth-form-pro input:hover{border-color:rgba(208,169,255,.22)}.forge-auth-form-pro input:focus{background:rgba(7,5,13,.7);border-color:rgba(186,119,255,.62);box-shadow:0 0 0 3px rgba(157,77,255,.08)}.forge-auth-submit-pro{height:47px;margin-top:2px;border-radius:9px;background:#f4effa;color:#110b17;box-shadow:0 15px 35px rgba(0,0,0,.2);transition:transform .2s,box-shadow .2s,background .2s}.forge-auth-submit-pro:hover:not(:disabled){transform:translateY(-2px);background:#fff;box-shadow:0 18px 42px rgba(0,0,0,.28)}.forge-auth-switch-pro{margin-top:20px;padding-top:19px;border-top:1px solid rgba(255,255,255,.07);justify-content:flex-start}.forge-auth-switch-pro button{color:#c48aff}.forge-auth-panel-foot{display:flex;justify-content:space-between;gap:15px;margin-top:25px;color:rgba(224,211,238,.22);font-size:7px}
@media(max-width:900px){.forge-auth-pro-shell{grid-template-columns:1fr;max-width:620px;gap:35px;padding:38px 22px}.forge-auth-showcase{min-height:0}.forge-auth-showcase-copy{margin:65px 0 35px}.forge-auth-showcase-copy h1{font-size:clamp(48px,12vw,72px)}.forge-auth-signal-grid{margin-bottom:28px}}
@media(max-width:560px){.forge-auth-pro-panel{padding:27px 22px}.forge-auth-signal-grid>div{padding:14px 10px}.forge-auth-signal-grid small{display:none}.forge-auth-trust{font-size:6px}.forge-auth-showcase-copy p{font-size:12px}}
.forge-myforge-sidebar{width:272px !important;padding:24px 14px 16px !important;background:linear-gradient(180deg,rgba(13,8,23,.97),rgba(10,7,18,.96)) !important;border-right-color:rgba(191,145,255,.14) !important}.forge-myforge-main{margin-left:272px !important;width:calc(100% - 272px) !important}.forge-myforge-sidebar nav{gap:5px !important}.forge-nav-section-label,.forge-nav-label{margin:17px 10px 7px !important;color:#8f70bd !important;font-size:7px !important;letter-spacing:.18em !important}.forge-myforge-sidebar nav button{min-height:40px !important;padding:10px 12px !important;border:1px solid transparent !important;border-radius:12px !important;font-size:10px !important;transition:.22s ease !important}.forge-myforge-sidebar nav button:hover{transform:translateX(3px);background:rgba(142,77,255,.08) !important;border-color:rgba(184,136,255,.1) !important}.forge-myforge-sidebar nav button.active{background:linear-gradient(90deg,rgba(143,78,255,.22),rgba(84,213,255,.055)) !important;border-color:rgba(178,128,255,.16) !important;box-shadow:inset 3px 0 #bd6cff,0 8px 25px rgba(100,44,170,.08) !important}.forge-myforge-sidebar nav button.active .forge-nav-icon{color:#bfa1ff !important;background:rgba(166,99,255,.12)}.forge-nav-icon{width:29px !important;height:29px !important;display:grid !important;place-items:center !important;border-radius:9px !important;border:1px solid rgba(191,145,255,.09) !important;background:rgba(255,255,255,.025) !important;flex:0 0 29px !important}.forge-nav-arrow{opacity:.35 !important;margin-left:auto}.forge-myforge-sidebar nav button.active .forge-nav-arrow{opacity:.9 !important;color:#c792ff}.forge-myforge-profile{border-color:rgba(191,145,255,.14) !important;background:linear-gradient(135deg,rgba(46,28,67,.72),rgba(17,11,27,.86)) !important;padding:11px !important;border-radius:15px !important;box-shadow:inset 0 1px rgba(255,255,255,.04)}.forge-sidebar-role{border-color:rgba(191,145,255,.12) !important;background:linear-gradient(135deg,rgba(45,28,68,.58),rgba(14,10,23,.7)) !important;border-radius:16px !important;margin-bottom:8px !important}.forge-sidebar-status{color:#72e9ff !important}
@media(max-width:1100px){.forge-myforge-sidebar{width:235px !important}.forge-myforge-main{margin-left:235px !important;width:calc(100% - 235px) !important}}
`; 



const FORGE_STUDENT_NAV_CSS=`/* =========================================================
   STUDENT SIDEBAR — PROFESSIONAL NAVIGATION SYSTEM
   Student-only destinations; no organization modules.
========================================================= */
.forge-myforge-sidebar{
  width:278px !important;
  padding:18px 13px 14px !important;
  background:
    radial-gradient(260px 220px at 15% 0%,rgba(139,76,255,.13),transparent 68%),
    linear-gradient(180deg,rgba(10,7,18,.985),rgba(15,9,25,.98)) !important;
  border-right:1px solid rgba(205,164,255,.16) !important;
  box-shadow:22px 0 70px rgba(4,1,10,.30),inset -1px 0 rgba(255,255,255,.02) !important;
  overflow:hidden !important;
}
.forge-myforge-sidebar:before{
  content:"";
  position:absolute;
  top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#a966ff 30%,#65e6ff 72%,transparent);
  opacity:.45;
}
.forge-myforge-brand{
  padding:2px 8px 16px !important;
  gap:11px !important;
  position:relative;
}
.forge-myforge-brand strong{
  font-size:17px !important;
  letter-spacing:.20em !important;
}
.forge-myforge-brand small{
  margin-top:3px !important;
  font-size:7px !important;
  letter-spacing:.13em !important;
  color:rgba(226,211,245,.38) !important;
}
.forge-brand-mark{
  width:42px !important;height:42px !important;
  border-radius:13px !important;
  background:linear-gradient(145deg,rgba(42,20,67,.95),rgba(8,5,14,.95)) !important;
  border-color:rgba(194,132,255,.32) !important;
  box-shadow:0 0 28px rgba(145,70,255,.20),inset 0 1px rgba(255,255,255,.08) !important;
}
.forge-sidebar-status{
  margin-left:auto;
  display:inline-flex;
  align-items:center;
  gap:5px;
  padding:5px 7px;
  border:1px solid rgba(91,226,255,.15);
  border-radius:999px;
  color:#83eaff;
  background:rgba(72,210,255,.045);
  font-size:6px;
  font-weight:900;
  letter-spacing:.12em;
}
.forge-sidebar-status i{
  width:5px;height:5px;border-radius:50%;
  background:#65e6ff;
  box-shadow:0 0 9px #65e6ff;
  animation:forgeLivePulse 1.1s infinite;
}
.forge-sidebar-role{
  margin:0 4px 12px;
  padding:11px 12px;
  border:1px solid rgba(190,143,255,.13);
  border-radius:13px;
  background:linear-gradient(145deg,rgba(101,48,157,.12),rgba(255,255,255,.018));
  box-shadow:inset 0 1px rgba(255,255,255,.045);
}
.forge-sidebar-role span{
  display:flex;align-items:center;gap:5px;
  color:rgba(206,171,255,.45);
  font-size:6px;font-weight:900;letter-spacing:.14em;
}
.forge-sidebar-role strong{
  display:block;margin-top:7px;
  color:#fff;font-size:11px;font-weight:800;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.forge-sidebar-role small{
  display:block;margin-top:3px;
  color:rgba(233,219,248,.30);font-size:7px;
}
.forge-student-nav{
  display:grid !important;
  gap:2px !important;
  min-height:0;
  overflow:auto;
  padding:1px 0 6px;
  scrollbar-width:none;
}
.forge-student-nav::-webkit-scrollbar{display:none}
.forge-nav-section-label{
  margin:2px 10px 5px;
  color:rgba(205,165,255,.34);
  font-size:6px;font-weight:900;letter-spacing:.18em;
}
.forge-myforge-sidebar .forge-nav-label{
  margin:12px 10px 4px !important;
  color:rgba(201,162,255,.39) !important;
  font-size:6px !important;
  font-weight:900 !important;
  letter-spacing:.17em !important;
}
.forge-student-nav button{
  position:relative;
  min-height:34px;
  padding:7px 9px !important;
  gap:8px !important;
  border:1px solid transparent !important;
  border-radius:10px !important;
  color:rgba(236,226,247,.49) !important;
  font-size:9px !important;
  font-weight:600;
  transition:transform .22s ease,background .22s ease,border-color .22s ease,color .22s ease,box-shadow .22s ease !important;
}
.forge-student-nav button .forge-nav-icon{
  width:27px;height:27px;
  display:grid;place-items:center;
  flex:0 0 auto;
  border:1px solid rgba(211,175,255,.08);
  border-radius:8px;
  background:rgba(255,255,255,.018);
  color:rgba(222,205,240,.55);
  transition:.22s ease;
}
.forge-student-nav button>span:nth-child(2){flex:1;min-width:0}
.forge-student-nav .forge-nav-arrow{
  opacity:0;
  color:#c58aff;
  transform:translateX(-4px);
  transition:.22s ease;
}
.forge-student-nav button:hover{
  transform:translateX(3px) !important;
  color:#fff !important;
  background:linear-gradient(90deg,rgba(151,76,255,.13),rgba(151,76,255,.035)) !important;
  border-color:rgba(191,139,255,.12) !important;
}
.forge-student-nav button:hover .forge-nav-icon{
  color:#d9b8ff;
  border-color:rgba(193,139,255,.24);
  background:rgba(160,82,255,.10);
  box-shadow:0 0 16px rgba(153,78,255,.10);
}
.forge-student-nav button:hover .forge-nav-arrow{
  opacity:.9;transform:translateX(0);
}
.forge-student-nav button.active{
  color:#fff !important;
  background:linear-gradient(100deg,rgba(142,69,255,.25),rgba(65,30,101,.13)) !important;
  border-color:rgba(185,125,255,.16) !important;
  box-shadow:inset 2px 0 #c16cff,0 8px 25px rgba(112,44,189,.11) !important;
}
.forge-student-nav button.active:after{
  content:"";
  position:absolute;right:9px;top:50%;
  width:4px;height:4px;border-radius:50%;
  transform:translateY(-50%);
  background:#c879ff;
  box-shadow:0 0 10px #c879ff;
}
.forge-student-nav button.active .forge-nav-icon{
  color:#f0ddff;
  border-color:rgba(203,149,255,.28);
  background:linear-gradient(145deg,rgba(173,91,255,.20),rgba(255,255,255,.035));
  box-shadow:0 0 18px rgba(166,80,255,.12);
}
.forge-student-nav button.active .forge-nav-arrow{
  opacity:.72;transform:translateX(0);
}
.forge-sidebar-footer{
  margin-top:auto;
  padding-top:10px;
}
.forge-sidebar-footer-line{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin:0 5px 7px;
  color:rgba(218,195,239,.24);
  font-size:6px;font-weight:900;letter-spacing:.12em;
}
.forge-sidebar-footer-line span{display:flex;align-items:center;gap:5px}
.forge-sidebar-footer-line i{
  width:5px;height:5px;border-radius:50%;
  background:#7ce8ff;box-shadow:0 0 8px #7ce8ff;
}
.forge-sidebar-footer-line b{color:rgba(121,233,191,.55);font-size:6px}
.forge-sidebar-footer .forge-myforge-profile{
  margin-top:0 !important;
  padding:9px !important;
  border-radius:13px !important;
  background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(151,74,255,.07)) !important;
}
.forge-sidebar-footer .forge-myforge-profile:hover{
  transform:translateY(-2px);
  border-color:rgba(210,164,255,.34) !important;
  box-shadow:0 14px 35px rgba(86,30,133,.15);
}
.forge-myforge-main{
  margin-left:278px !important;
  width:calc(100% - 278px) !important;
}
@media(max-width:1100px){
  .forge-myforge-sidebar{width:230px !important}
  .forge-myforge-main{margin-left:230px !important;width:calc(100% - 230px) !important}
}
@media(max-width:760px){
  .forge-myforge-sidebar{width:auto !important}
  .forge-myforge-main{margin-left:0 !important;width:auto !important}
  .forge-sidebar-role{margin-bottom:8px}
}
`;

function ForgeStudentIdentityStyles(){return <><style>{FORGE_STUDENT_IDENTITY_CSS}</style><style>{FORGE_STUDENT_NAV_CSS}</style></>}


function StudentWorkspace(){
 const navigate=useNavigate();
 const path=window.location.pathname;
 const [step,setStep]=useState(path==="/student/subjects"?2:path==="/student/target-year"?3:path==="/student/levels"?4:1);
 const [profile,setProfile]=useState(()=>readS("forge_student_profile",{studyYear:"",experience:"",companyType:"",targetRole:"",goal:"",dailyHours:"",readiness:""}));
 const [subjects,setSubjects]=useState(()=>readS("forge_student_subjects",[]));
 const [year,setYear]=useState(()=>Number(sessionStorage.getItem("forge_student_target_year"))||null);
 const [levels,setLevels]=useState(()=>readS("forge_student_levels",{}));
 useEffect(()=>{sessionStorage.setItem("forge_student_profile",JSON.stringify(profile))},[profile]);useEffect(()=>{sessionStorage.setItem("forge_student_subjects",JSON.stringify(subjects))},[subjects]);useEffect(()=>{if(year)sessionStorage.setItem("forge_student_target_year",String(year))},[year]);useEffect(()=>{sessionStorage.setItem("forge_student_levels",JSON.stringify(levels))},[levels]);
 const go=n=>{setStep(n);navigate(n===1?"/student":n===2?"/student/subjects":n===3?"/student/target-year":"/student/levels")};
 const profileOk=Object.values(profile).every(Boolean),subjectsOk=subjects.length>0,yearOk=!!year,levelsOk=subjects.length>0&&subjects.every(x=>!!levels[x]);
 return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-topbar"><button className="student-back" onClick={()=>step===1?navigate("/"):go(step-1)}><ChevronLeft size={15}/>{step===1?"Home":"Back"}</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">0{step} / 08</div></div><div className="student-progress"><span style={{width:`${step/8*100}%`}}/></div>{step===1&&<ProfileStep value={profile} setValue={setProfile} ok={profileOk} next={()=>go(2)}/>} {step===2&&<SubjectsStep profile={profile} value={subjects} setValue={setSubjects} ok={subjectsOk} next={()=>go(3)}/>} {step===3&&<YearStep profile={profile} subjects={subjects} value={year} setValue={setYear} ok={yearOk} next={()=>go(4)}/>} {step===4&&<LevelsStep subjects={subjects} value={levels} setValue={setLevels} ok={levelsOk} next={()=>navigate("/student/assessment")}/>}</div></main></>;
}
function Frame({eyebrow,title,description,children,validation,disabled,next,button="Continue"}){return <><div className="student-step-eyebrow"><span/>{eyebrow}</div><h1 className="student-title">{title}</h1><p className="student-description">{description}</p><div className="student-content">{children}</div><div className="student-bottom"><div className="student-validation">{validation}</div><button className="student-continue" disabled={disabled} onClick={next}>{button}<ArrowRight size={15}/></button></div></>}
function ProfileStep({value,setValue,ok,next}){const fields=["studyYear","experience","companyType","targetRole","goal","dailyHours","readiness"];return <Frame eyebrow="01 / TELL US ABOUT YOU" title={<>Build the plan<br/>around <em>you.</em></>} description="Tell FORGE who you are, where you want to go and how much time you can realistically invest." validation={ok?"Profile complete":"Complete all profile questions to continue"} disabled={!ok} next={next}>{<div className="student-question-grid">{fields.map((k,i)=><div className="student-question" key={k}><div className="student-question-head"><strong>{({studyYear:"Study year",experience:"Previous experience",companyType:"Target company type",targetRole:"Target role",goal:"Primary goal",dailyHours:"Realistic daily study hours",readiness:"When do you want to be ready?"})[k]}</strong><span>0{i+1}</span></div><div className="student-options">{PROFILE_OPTIONS[k].map(o=><button key={o} className={`student-option ${value[k]===o?"selected":""}`} onClick={()=>setValue(v=>({...v,[k]:o}))}>{o}</button>)}</div></div>)}</div>}</Frame>}
const SUBJECT_ICON_MAP={DSA:Workflow,"C++":Cpu,Java:Workflow,Python:Brain,DBMS:Database,"Operating Systems":Cpu,"Computer Networks":Network,OOP:Target,SQL:Database,"System Design":Sparkles,"Machine Learning":Brain,"Deep Learning":Brain,Statistics:Sparkles,"Data Science":Target,Pandas:Database,NumPy:Cpu,"Data Visualization":Sparkles,"HTML/CSS":BookOpen,JavaScript:Cpu,React:Workflow,"Node.js":Cpu,"REST APIs":Network,"Git/GitHub":Workflow,Cloud:Sparkles};
function SubjectsStep({profile,value,setValue,ok,next}){const suggested=ROLE_SUGGESTIONS[profile.targetRole]||["DSA","Python","DBMS","OOP","SQL"];const toggle=s=>setValue(v=>v.includes(s)?v.filter(x=>x!==s):[...v,s]);return <Frame eyebrow="02 / SELECT SUBJECTS" title={<>Choose your<br/><em>capability stack.</em></>} description="FORGE maps your target role to the subjects that matter most. Select the capabilities you want to measure and build." validation={ok?<><strong>{value.length}</strong> subjects selected</>:"Select at least one subject"} disabled={!ok} next={next}><div className="student-role-context"><div className="student-role-context-icon"><Target size={16}/></div><div><small>YOUR SELECTED ROLE</small><strong>{profile.targetRole||"Choose a target role"}</strong></div><span>{suggested.length} role signals</span></div><div className="student-subjects">{STUDENT_SUBJECTS.map(s=>{const Icon=SUBJECT_ICON_MAP[s]||BookOpen;const isSelected=value.includes(s);const isSuggested=suggested.includes(s);return <button key={s} className={`student-subject ${isSelected?"selected":""} ${isSuggested?"recommended":""}`} onClick={()=>toggle(s)}><span className="student-subject-icon"><Icon size={19}/></span><span className="student-subject-copy"><small>{isSuggested?"RECOMMENDED FOR ROLE":"AVAILABLE CAPABILITY"}</small><strong>{s}</strong></span>{isSelected&&<span className="student-subject-check"><Check size={13}/></span>}</button>})}</div><div className="student-selected-count"><span><Sparkles size={13}/> Your selected capabilities become the assessment scope.</span><strong>{String(value.length).padStart(2,"0")}</strong></div></Frame>}
function YearStep({profile,subjects,value,setValue,ok,next}){return <Frame eyebrow="03 / TARGET COMPLETION YEAR" title={<>When do you want<br/>to be <em>ready?</em></>} description="Your target year becomes a planning constraint for roadmap duration, weekly allocation and assessment priorities." validation={ok?<>Target completion: <strong>{value}</strong></>:"Select a target completion year"} disabled={!ok} next={next}><div className="student-info" style={{marginTop:0,marginBottom:18}}><CalendarDays size={15}/><span>{profile.targetRole?`Planning for ${profile.targetRole}. `:""}{subjects.length} selected subject{subjects.length===1?"":"s"} will be considered.</span></div><div className="student-years">{[2026,2027,2028,2029,2030].map((y,i)=><button key={y} className={`student-year ${value===y?"selected":""}`} onClick={()=>setValue(y)}><span className="student-year-index">0{i+1}</span>{value===y&&<span className="student-year-check"><Check size={13}/></span>}<strong className="student-year-number">{y}</strong><span className="student-year-text">{y===2026?"Accelerated horizon":y===2030?"Longer runway":"Target horizon"}</span></button>)}</div></Frame>}
function LevelsStep({subjects,value,setValue,ok,next}){const opts=[["zero","From zero"],["fundamentals","Fundamentals"],["interview","Interview preparation"]];return <Frame eyebrow="04 / SUBJECT-WISE LEVEL" title={<>Set your<br/><em>starting point.</em></>} description="Tell FORGE where you are today. Your assessment will validate these self-reported levels and turn them into evidence." validation={ok?"All selected subjects have a starting level":`${Object.keys(value).filter(k=>subjects.includes(k)).length} / ${subjects.length} levels selected`} disabled={!ok} next={next} button="Start Assessment"><div className="student-levels">{subjects.map((s,i)=><div className={`student-level-row ${value[s]?"has-selection":""}`} key={s}><div className="student-level-heading"><span className="student-level-index">0{String(i+1)}</span><div><strong>{s}</strong><small>Current confidence before assessment</small></div></div><div className="student-level-options">{opts.map(([v,l])=><button key={v} className={`student-level ${value[s]===v?"selected":""}`} onClick={()=>setValue(x=>({...x,[s]:v}))}><span>{l}</span>{value[s]===v&&<Check size={13}/>}</button>)}</div></div>)}</div><div className="student-info student-info-accent"><Check size={15}/><span>Self-reported only — the 20-question assessment below is the evidence that counts.</span></div></Frame>}
const ASSESSMENT_QUESTIONS={
  "DSA":[
    ["Which data structure is best suited for implementing a LIFO access pattern?",["Queue","Stack","Heap","Graph"]],
    ["For a sorted array, which search technique runs in O(log n) time?",["Linear search","Binary search","DFS","BFS"]],
    ["What is the average-case time complexity of hash-table lookup with a good hash function?",["O(1)","O(log n)","O(n)","O(n log n)"]],
    ["Which traversal visits a tree's root before its subtrees?",["Inorder","Postorder","Preorder","Level-order only"]],
    ["Which algorithmic strategy stores solutions to overlapping subproblems?",["Greedy only","Dynamic programming","Backtracking only","Randomization"]]
  ],
  "C++":[
    ["Which feature allows the same function name to work with different parameter lists?",["Inheritance","Overloading","Encapsulation","Casting"]],
    ["Which keyword prevents a variable from being modified after initialization?",["static","const","mutable","volatile"]],
    ["What does a reference in C++ provide?",["A second name for an existing object","A new heap object","A copied object","A type conversion"]],
    ["Which container provides dynamic contiguous storage?",["std::list","std::map","std::vector","std::set"]],
    ["What is RAII primarily associated with?",["Resource lifetime management","Runtime reflection","Database indexing","Network routing"]]
  ],
  "Java":[
    ["Which mechanism allows a class to provide multiple implementations through a common contract?",["Interface","Package","Primitive","Annotation only"]],
    ["Which collection does not allow duplicate elements?",["List","Set","Queue","ArrayList"]],
    ["What is method overriding?",["Same method name with different parameters","Subclass redefining an inherited method","Creating a constructor","Converting a type"]],
    ["Which keyword is used to inherit from a class?",["implements","extends","inherits","superclass"]],
    ["What does the JVM execute?",["Bytecode","SQL","HTML","Machine learning models only"]]
  ],
  "Python":[
    ["Which Python type stores key-value pairs?",["list","tuple","dict","set"]],
    ["What does a list comprehension primarily provide?",["Compact list construction","Thread creation","Database access","Class inheritance"]],
    ["Which keyword defines a function?",["func","def","function","lambda"]],
    ["What is the purpose of a virtual environment?",["Isolate project dependencies","Speed up the CPU","Compile Python to C","Store passwords"]],
    ["Which object is immutable?",["list","dict","set","tuple"]]
  ],
  "DBMS":[
    ["Which normal form removes partial dependency on a composite key?",["1NF","2NF","3NF","BCNF"]],
    ["What does ACID's Atomicity guarantee?",["All-or-nothing transaction execution","Faster queries","No duplicate rows","Automatic indexing"]],
    ["Which SQL operation combines rows from related tables?",["JOIN","GROUP BY","ORDER BY","HAVING"]],
    ["What is a primary key used for?",["Uniquely identifying rows","Sorting every query","Encrypting columns","Creating backups"]],
    ["Which index structure is commonly used for ordered database lookups?",["B-tree","Stack","Queue","Bloom filter only"]]
  ],
  "Operating Systems":[
    ["Which component manages processes and hardware resources?",["Kernel","Compiler","Browser","Shell script only"]],
    ["Which scheduling algorithm gives each process a time slice?",["Round Robin","FCFS only","SJF only","DFS"]],
    ["What is a deadlock?",["Processes waiting indefinitely for resources","A crashed browser","A full disk only","A compile-time syntax error"]],
    ["Virtual memory primarily allows a system to",["Use disk as an extension of memory","Increase CPU clock speed","Remove the kernel","Disable processes"]],
    ["Which state means a process is waiting for CPU allocation?",["Ready","Terminated","New","Running"]]
  ],
  "Computer Networks":[
    ["Which protocol translates domain names into IP addresses?",["DNS","DHCP","ARP","ICMP"]],
    ["Which layer is responsible for end-to-end transport in the OSI model?",["Transport","Network","Session","Physical"]],
    ["What does TCP provide?",["Reliable ordered delivery","Only encryption","IP addressing","Wireless signaling"]],
    ["Which device primarily forwards packets between networks?",["Router","Hub","Repeater","Keyboard"]],
    ["What is CIDR used for?",["Flexible IP prefix allocation","Encrypting DNS","Compressing packets","Replacing Ethernet"]]
  ],
  "OOP":[
    ["Which principle hides internal implementation details behind an interface?",["Encapsulation","Inheritance","Polymorphism","Recursion"]],
    ["Which concept allows one interface to represent different implementations?",["Polymorphism","Compilation","Serialization","Indexing"]],
    ["What does inheritance primarily enable?",["Reuse and extension of class behavior","Database joins","Packet routing","Memory paging"]],
    ["A constructor is primarily used to",["Initialize an object","Destroy the program","Query a database","Create a thread scheduler"]],
    ["Which relationship represents a strong whole-part ownership?",["Composition","Aggregation only","Association only","Dependency inversion"]]
  ],
  "SQL":[
    ["Which clause filters rows before grouping?",["WHERE","HAVING","ORDER BY","LIMIT"]],
    ["Which clause filters grouped results?",["WHERE","HAVING","SELECT","JOIN"]],
    ["Which command changes existing rows?",["UPDATE","ALTER","CREATE","GRANT"]],
    ["Which aggregate function counts rows?",["COUNT","SUM","AVG","MAX"]],
    ["Which keyword removes duplicate rows from a result?",["DISTINCT","UNIQUEKEY","DEDUP","ONLY"]]
  ],
  "System Design":[
    ["What is horizontal scaling?",["Adding more instances","Adding RAM to one machine","Reducing users","Removing replicas"]],
    ["What is a cache primarily used for?",["Reducing repeated access latency","Replacing databases permanently","Encrypting all traffic","Creating DNS records"]],
    ["Why use a load balancer?",["Distribute requests across servers","Compile code","Store source files","Create database schemas"]],
    ["What does eventual consistency mean?",["Replicas may converge after a delay","All writes are instantly identical","No data is replicated","Transactions never fail"]],
    ["Which component is useful for asynchronous event processing?",["Message queue","CSS file","Router only","Compiler"]]
  ],
  "Machine Learning":[
    ["What is the main purpose of a validation set?",["Tune model choices without using the final test set","Train on labels twice","Replace training data","Encrypt features"]],
    ["Which metric is commonly used for binary classification?",["F1-score","MSE only","MAE only","R-squared only"]],
    ["What does overfitting mean?",["The model fits training data too closely and generalizes poorly","The model has no parameters","The data has no labels","The model always underperforms training data"]],
    ["Which algorithm can create axis-aligned decision rules?",["Decision tree","K-means","PCA","Linear interpolation"]],
    ["What does gradient descent optimize?",["A loss/objective function","The database schema","The network topology","The file system"]]
  ],
  "Deep Learning":[
    ["What is an activation function used for?",["Introduce nonlinear transformations","Store training labels","Normalize databases","Create network sockets"]],
    ["Which architecture is commonly used for image feature extraction?",["CNN","B-tree","KNN only","DNS"]],
    ["What does backpropagation compute?",["Gradients for updating model parameters","Database joins","IP routes","File permissions"]],
    ["Why is dropout used?",["Reduce overfitting","Increase database size","Encode URLs","Replace optimization"]],
    ["What is an epoch?",["One complete pass through the training data","One neuron","One feature","One test example only"]]
  ],
  "Statistics":[
    ["What does variance measure?",["Dispersion around the mean","Causal effect","Class count only","Model latency"]],
    ["What does correlation describe?",["Strength and direction of association","Proof of causation","Sample size only","Database normalization"]],
    ["What is a p-value used to assess?",["Evidence against a null hypothesis under a test model","Model memory usage","CPU utilization","Feature count"]],
    ["Which measure is less sensitive to extreme values?",["Median","Mean","Sum","Variance"]],
    ["What does a confidence interval provide?",["A range reflecting uncertainty around an estimate","A guaranteed population value","A model architecture","A database key"]]
  ],
  "Data Science":[
    ["What is EDA primarily used for?",["Understand structure, patterns and anomalies in data","Deploy APIs only","Encrypt datasets","Compile models"]],
    ["Which plot is useful for visualizing a distribution?",["Histogram","Class diagram","Network packet","ER key only"]],
    ["Why handle missing values?",["To avoid invalid or biased analysis/model inputs","To increase file size","To remove all outliers","To create indexes"]],
    ["What does feature engineering mean?",["Creating or transforming inputs to improve useful signal","Deleting labels","Changing operating systems","Compressing source code"]],
    ["What is data leakage?",["Information unavailable at prediction time enters model training","A missing file","A network outage","A database backup"]]
  ],
  "HTML/CSS":[
    ["Which HTML element represents the main heading?",["<h1>","<head>","<title>","<main-heading>"]],
    ["Which CSS property changes text color?",["color","font-style","background","text-decoration"]],
    ["What does CSS flexbox primarily help with?",["One-dimensional layout","Database queries","Server routing","Image classification"]],
    ["Which HTML attribute provides alternative text for an image?",["alt","src","href","title-only"]],
    ["What does responsive design aim to achieve?",["Usable layouts across screen sizes","Faster databases","Server-side rendering only","Automatic encryption"]]
  ],
  "JavaScript":[
    ["Which keyword declares a block-scoped variable that can be reassigned?",["let","const","var-only","define"]],
    ["What does an async function return?",["A Promise","A CSS rule","A database row","A socket"]],
    ["Which method transforms each array element into a new array?",["map","filter","reduce-only","sort-only"]],
    ["What is the DOM?",["A programmable representation of an HTML document","A database engine","A network protocol","A CSS compiler"]],
    ["What does event bubbling describe?",["An event propagating from a target toward ancestors","A memory leak","A rendering engine","A promise state"]]
  ],
  "React":[
    ["What is a React component?",["A reusable UI building block","A database table","A network packet","A CSS selector only"]],
    ["Which hook is commonly used for local component state?",["useState","useRoute","useClass","useDOMOnly"]],
    ["Why are keys used when rendering lists?",["Help React identify list items across updates","Encrypt data","Create routes","Fetch APIs automatically"]],
    ["What does useEffect primarily handle?",["Side effects tied to component lifecycle/state","CSS compilation","Database indexing","Type checking"]],
    ["What is a controlled input?",["An input whose value is driven by React state","An input with no events","A server-side form only","A disabled field"]]
  ],
  "Node.js":[
    ["What is Node.js primarily?",["A JavaScript runtime outside the browser","A database","A CSS framework","A Python compiler"]],
    ["Which package manager is commonly used with Node.js?",["npm","pip","cargo only","maven only"]],
    ["What does non-blocking I/O help with?",["Handling many I/O operations efficiently","Increasing CSS specificity","Compiling C++","Normalizing databases"]],
    ["What is Express commonly used for?",["Building HTTP servers/APIs","Training neural networks","Editing images","Managing SQL indexes only"]],
    ["What does middleware do in an HTTP framework?",["Process requests/responses in a pipeline","Replace JavaScript","Create hardware drivers","Train models"]]
  ],
  "REST APIs":[
    ["Which HTTP method is conventionally used to retrieve a resource?",["GET","POST","PATCH","DELETE"]],
    ["What does a 404 response indicate?",["Resource not found","Success","Server restarted","Unauthorized only"]],
    ["Which format is commonly used for API payloads?",["JSON","CSS","PNG only","SQL"]],
    ["What does idempotent mean for an HTTP operation?",["Repeating it has the same intended effect as one execution","It always returns 200","It requires encryption","It cannot fail"]],
    ["Why use pagination in an API?",["Avoid returning very large result sets at once","Encrypt responses","Create database tables","Disable caching"]]
  ],
  "Git/GitHub":[
    ["What does git commit record?",["A snapshot of staged changes","A running server","A database row","A browser session"]],
    ["Which command creates a new branch?",["git branch","git fetch-only","git clone-only","git package"]],
    ["What is a pull request used for?",["Propose and review changes before merging","Install Python","Run SQL","Deploy hardware"]],
    ["What does git merge do?",["Combines histories/changes from branches","Deletes all commits","Creates a database","Compiles React"]],
    ["Why use .gitignore?",["Prevent selected files from being tracked","Encrypt commits","Delete branches","Create releases"]]
  ],
  "Cloud":[
    ["What is horizontal scaling in cloud infrastructure?",["Adding more service instances","Increasing one machine's RAM only","Deleting replicas","Reducing availability"]],
    ["What is object storage designed for?",["Storing files/blobs as objects","Running CPU instructions only","Routing packets","Managing SQL joins"]],
    ["What does autoscaling do?",["Adjust capacity based on demand/policy","Encrypt source code","Create HTML","Normalize tables"]],
    ["What is a region in a cloud provider?",["A geographic deployment area containing infrastructure","A database row","A programming language","A DNS record"]],
    ["Why use IAM?",["Manage identities and access permissions","Train models","Compress images","Create CSS layouts"]]
  ]
  ,"Pandas":[
    ["Which Pandas object is designed to represent tabular data with labeled rows and columns?",["DataFrame","Tensor","Tuple","Iterator"]],
    ["Which Pandas operation is commonly used to group rows and compute aggregates?",["groupby()","compile()","render()","socket()"]],
    ["What is a practical first step when a DataFrame contains missing values?",["Inspect the missingness pattern","Delete the entire dataset","Shuffle labels","Ignore it automatically"]],
    ["Which operation combines rows from two DataFrames using matching keys?",["merge()","print()","sort_index()","astype()"]],
    ["Why should data transformations be kept reproducible in a data-science workflow?",["To make analysis repeatable and auditable","To increase UI animation","To remove all validation","To avoid using metrics"]]
  ],
  "NumPy":[
    ["What is NumPy primarily used for in data-science workflows?",["Numerical arrays and vectorized computation","Web routing","Database authentication","CSS styling"]],
    ["What does NumPy broadcasting allow?",["Operations between compatible array shapes","Automatic model deployment","SQL joins","HTML rendering"]],
    ["Which NumPy structure is central to numerical computation?",["ndarray","DataFrame","GraphQL schema","DOM tree"]],
    ["Why can vectorized NumPy operations be faster than Python loops?",["They use optimized array operations internally","They always use zero memory","They skip all calculations","They require no CPU"]],
    ["Which operation is useful for generating reproducible random samples?",["A seeded random generator","A CSS selector","A database index","An HTTP header"]]
  ],
  "Data Visualization":[
    ["Which chart is usually useful for showing the distribution of a continuous variable?",["Histogram","Pie chart only","Network topology","Gantt chart only"]],
    ["What is a strong reason to label axes and units?",["It makes the visual interpretable","It increases model accuracy automatically","It removes outliers","It trains a classifier"]],
    ["Which visualization is useful for inspecting relationships between two numerical variables?",["Scatter plot","Stack trace","ER diagram","Sequence diagram"]],
    ["What should you avoid when choosing a visualization?",["A chart that obscures the underlying comparison","Clear labels","Relevant scales","Consistent units"]],
    ["Why is visualization important in data science?",["It helps communicate patterns, uncertainty and comparisons","It guarantees causality","It replaces validation","It eliminates sampling error"]]
  ],
  "Data Science":[
    ["What is the main purpose of exploratory data analysis?",["Understand structure, patterns and anomalies before modeling","Deploy an API","Compile Python","Normalize database tables"]],
    ["Which step should generally happen before fitting a model?",["Inspect and clean the data","Delete the target","Ignore missing values","Use the test set for tuning"]],
    ["What is data leakage?",["Information from outside the training process improperly influencing model learning","A missing CSS rule","A slow SQL query","A network timeout"]],
    ["Why should the test set remain separate until final evaluation?",["To estimate performance on unseen data fairly","To increase training size at any cost","To tune every hyperparameter","To remove all bias"]],
    ["Which activity is part of feature engineering?",["Creating useful model inputs from available data","Changing the website theme","Opening a terminal","Renaming a file"]]
  ]
};


const ROLE_ASSESSMENT_QUESTIONS={
  "Software Engineer":[["DSA","You need to process a stream and keep the largest k values efficiently. Which approach is most appropriate?",["Min-heap of size k","Stack of all values","DFS traversal","Linear search after every insert"]]],
  "Frontend Developer":[["React","A component needs to fetch data after it mounts. Which React mechanism is appropriate?",["useEffect","useState only","key prop","className"]]],
  "Backend Developer":[["REST APIs","An API update should modify only one field of a resource. Which HTTP method is conventionally suitable?",["PATCH","GET","OPTIONS","TRACE"]]],
  "Full Stack Developer":[["SQL","A page needs the latest 20 records from a large table. Which combination is most appropriate?",["ORDER BY with LIMIT","GROUP BY only","DISTINCT only","HAVING without grouping"]]],
  "Data Scientist":[
    ["Statistics","A model performs well on training data but poorly on unseen data. What should you investigate first?",["Overfitting","DNS resolution","Database indexing","HTML semantics"]],
    ["Data Science","A dataset has 30% missing values in an important feature. What is the most defensible first step?",["Inspect the missingness mechanism and pattern","Fill every value with zero without checking","Delete the target column","Use the test set to impute values"]],
    ["Machine Learning","Which evaluation strategy is useful when you want a more stable estimate across multiple train/validation splits?",["Cross-validation","Changing the chart color","Renaming the dataset","Removing the target"]],
    ["SQL","You need the top 3 salaries within each job category. Which SQL feature is especially useful?",["Window functions","HTML tables","Git branches","CSS Grid"]],
    ["Python","Why are Pandas and NumPy commonly used together in data-science workflows?",["They support tabular data handling and efficient numerical computation","They replace all ML evaluation","They provide cloud hosting","They remove the need for validation"]]
  ],
  "ML Engineer":[["Machine Learning","A production model's input distribution changes over time. What issue should be monitored?",["Data drift","CSS specificity","Deadlock","DNS caching"]]],
  "AI Engineer":[["Deep Learning","A deep model is difficult to optimize because gradients become extremely small in early layers. What issue is this?",["Vanishing gradients","Over-indexing","Packet loss","Deadlock"]]],
  "Data Analyst":[["Data Science","Before reporting a KPI, what should you check when a dataset contains extreme values?",["Whether outliers are valid or erroneous","Whether HTML is valid","Whether DNS is cached","Whether Git has a remote"]]],
  "DevOps / Cloud Engineer":[["Cloud","A service must automatically add instances when traffic spikes. Which cloud capability addresses this?",["Autoscaling","Object storage","Static DNS only","Manual deployment"]]],
  "Cybersecurity Engineer":[["Computer Networks","A host should prove it is communicating with an authorized service. Which mechanism is directly relevant?",["Authentication","CSS flexbox","Database normalization","Binary search"]]],
  "Product Engineer":[["System Design","A product suddenly receives 10x traffic. Which first architectural response improves capacity without replacing the whole system?",["Scale service instances behind a load balancer","Remove caching","Store everything in the browser","Disable monitoring"]]]
};

const ROLE_QUESTION_BONUS={
  "Software Engineer":["DSA","OOP","System Design"],"Frontend Developer":["HTML/CSS","JavaScript","React"],"Backend Developer":["REST APIs","Node.js","System Design"],"Full Stack Developer":["React","REST APIs","SQL"],"Data Scientist":["Statistics","Data Science","Machine Learning"],"ML Engineer":["Machine Learning","Python","Deep Learning"],"AI Engineer":["Python","Machine Learning","Deep Learning"],"Data Analyst":["SQL","Statistics","Data Science"],"DevOps / Cloud Engineer":["Cloud","Computer Networks","Git/GitHub"],"Cybersecurity Engineer":["Computer Networks","Operating Systems","Python"],"Product Engineer":["System Design","React","REST APIs"]
};

function assessmentHash(text){let h=2166136261;for(let i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function buildAssessmentQuestions(subjects,role,levels){
  const bonus=ROLE_QUESTION_BONUS[role]||[];
  const roleQuestions=ROLE_ASSESSMENT_QUESTIONS[role]||[];
  const pool=[];
  subjects.forEach(subject=>{
    const bank=ASSESSMENT_QUESTIONS[subject]||[];
    const roleBank=roleQuestions.filter(x=>x[0]===subject).map(x=>[x[1],x[2]]);
    [...bank,...roleBank].forEach(([question,options],index)=>{
      const seed=assessmentHash(`${role}|${subject}|${levels[subject]||""}|${question}`);
      const type=index<2?"Easy":index<4?"Intermediate":"Hard";
      pool.push({subject,question,options,level:levels[subject]||"",difficulty:type,seed,sourceIndex:index});
    });
  });

  const unique=[];
  const seen=new Set();
  const add=(item,difficulty,variant=0)=>{
    if(!item) return false;
    const key=`${item.subject}|${item.question}|${difficulty}|${variant}`;
    if(seen.has(key)) return false;
    seen.add(key);
    let question=item.question;
    if(variant>0){
      const prefixes={
        Easy:["Concept check:","Quick fundamentals check:"],
        Intermediate:["Applied reasoning:","Working-level check:"],
        Hard:["Interview-level challenge:","Advanced reasoning:"],
      };
      const list=prefixes[difficulty]||prefixes.Easy;
      question=`${list[variant%list.length]} ${question}`;
    }
    const optionPairs=item.options.map((text,i)=>({text,correct:i===0}));
    optionPairs.sort((a,b)=>assessmentHash(`${item.seed}|${question}|${a.text}`)-assessmentHash(`${item.seed}|${question}|${b.text}`));
    unique.push({subject:item.subject,question,options:optionPairs.map(x=>x.text),correct:optionPairs.find(x=>x.correct)?.text,level:item.level,difficulty,questionKey:`${item.subject}-${difficulty}-${unique.length}`,situational:false});
    return true;
  };

  const relevant=[...pool].sort((a,b)=>{
    const ar=bonus.includes(a.subject)?0:1, br=bonus.includes(b.subject)?0:1;
    return ar-br || (a.seed-b.seed);
  });
  if(!relevant.length) return [];
  const pick=(difficulty,count)=>{
    const candidates=relevant.filter(x=>x.difficulty===difficulty);
    if(!candidates.length) return;
    for(let i=0;i<count;i++){
      const item=candidates[i%candidates.length];
      add(item,difficulty,Math.floor(i/candidates.length));
    }
  };

  // Professional 20-question assessment: 7 Easy + 7 Intermediate + 6 Hard.
  // Situation-based questions are intentionally excluded from the assessment and scoring model.
  pick("Easy",7);
  pick("Intermediate",7);
  pick("Hard",6);
  return unique.slice(0,20);
}

function StudentAssessment(){
  const navigate=useNavigate();
  const subjects=readS("forge_student_subjects",[]);
  const profile=readS("forge_student_profile",{});
  const levels=readS("forge_student_levels",{});
  const targetYear=Number(sessionStorage.getItem("forge_student_target_year"))||null;
  const questions=useMemo(()=>buildAssessmentQuestions(subjects,profile.targetRole||"",levels),[subjects,profile.targetRole,levels]);
  const ASSESSMENT_VERSION="20-v2";
  const storedVersion=sessionStorage.getItem("forge_student_assessment_version");
  if(storedVersion!==ASSESSMENT_VERSION){
    sessionStorage.removeItem("forge_student_assessment_answers");
    sessionStorage.removeItem("forge_student_assessment_index");
    sessionStorage.removeItem("forge_student_assessment_submitted");
    sessionStorage.removeItem("forge_student_assessment_score");
    sessionStorage.setItem("forge_student_assessment_version",ASSESSMENT_VERSION);
  }
  const [answers,setAnswers]=useState(()=>readS("forge_student_assessment_answers",{}));
  const [current,setCurrent]=useState(()=>Number(sessionStorage.getItem("forge_student_assessment_index"))||0);
  const [submitted,setSubmitted]=useState(()=>sessionStorage.getItem("forge_student_assessment_submitted")==="true");
  useEffect(()=>sessionStorage.setItem("forge_student_assessment_answers",JSON.stringify(answers)),[answers]);
  useEffect(()=>sessionStorage.setItem("forge_student_assessment_index",String(current)),[current]);
  const answer=answers[current];
  const q=questions[current];
  const completed=Object.keys(answers).filter(k=>questions[Number(k)]).length;
  const score=questions.length?Math.round((questions.reduce((sum,item,i)=>sum+(answers[i]===item.correct?1:0),0)/questions.length)*100):0;
  const counts={Easy:7,Intermediate:7,Hard:6};
  const submit=()=>{if(completed===questions.length){sessionStorage.setItem("forge_student_assessment_submitted","true");sessionStorage.setItem("forge_student_assessment_score",String(score));setSubmitted(true)}};
  if(!subjects.length)return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-step-eyebrow"><span/>05 / ASSESSMENT</div><h1 className="student-title">No assessment<br/><em>scope yet.</em></h1><p className="student-description">Select at least one subject before starting the assessment.</p><button className="student-continue" onClick={()=>navigate("/student/subjects")}>Choose Subjects <ArrowRight size={15}/></button></div></main></>;
  if(!questions.length)return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-step-eyebrow"><span/>05 / ASSESSMENT</div><h1 className="student-title">Assessment is<br/><em>being prepared.</em></h1><p className="student-description">There is no question bank yet for the selected subjects.</p><button className="student-continue" onClick={()=>navigate("/student/levels")}>Back <ChevronLeft size={15}/></button></div></main></>;
  const sectionCounts=[
    ["Easy",questions.filter(x=>x.difficulty==="Easy").length],
    ["Intermediate",questions.filter(x=>x.difficulty==="Intermediate").length],
    ["Hard",questions.filter(x=>x.difficulty==="Hard").length]
  ];
  return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/levels")}><ChevronLeft size={15}/>Back</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">05 / 08</div></div><div className="student-progress"><span style={{width:"62.5%"}}/></div><div className="student-step-eyebrow"><span/>05 / ASSESSMENT</div><h1 className="student-title">Prove what you<br/><em>already know.</em></h1><p className="student-description">Your assessment is tailored to your selected role and subjects. It contains 20 MCQs: 7 Easy, 7 Intermediate and 6 Hard.</p><div className="assessment-context"><span>{profile.targetRole||"Target role"}</span><span>{targetYear||"Target year"}</span>{subjects.map(s=><span key={s}>{s}</span>)}</div><div className="assessment-structure">{sectionCounts.map(([label,count])=><div className={`assessment-structure-item ${q&&q.difficulty===label?"active":""}`} key={label}><strong>{count}</strong><span>{label}</span></div>)}</div>{!submitted?<div className="forge-assessment"><div className="assessment-meta"><div className="assessment-subject">{q.subject} · {q.difficulty} · {q.level.replaceAll("_"," ")}</div><div className="assessment-question-count">QUESTION {current+1} / {questions.length}</div></div><div className="assessment-progress-wrap"><span style={{width:`${((current+1)/questions.length)*100}%`}}/></div><div className={`assessment-card assessment-card-pro assessment-${q.difficulty.toLowerCase()}`}><div className="assessment-question-kicker"><span className="assessment-live-dot"/>{q.difficulty.toUpperCase()} · {q.subject}</div><div className="assessment-type-badge">QUESTION {current+1} / {questions.length}</div><h2>{q.question}</h2><div className="assessment-options">{q.options.map((option,i)=><button key={option} className={`assessment-option ${answer===option?"selected":""}`} onClick={()=>setAnswers(v=>({...v,[current]:option}))}><span className="assessment-option-key">{String.fromCharCode(65+i)}</span><span>{option}</span></button>)}</div></div><div className="assessment-nav"><button disabled={current===0} onClick={()=>setCurrent(i=>Math.max(0,i-1))}><ChevronLeft size={14}/>Previous</button>{current<questions.length-1?<button className="primary" disabled={!answer} onClick={()=>setCurrent(i=>Math.min(questions.length-1,i+1))}>Next <ArrowRight size={14}/></button>:<button className="primary" disabled={completed!==questions.length} onClick={submit}>Finish Assessment <Check size={14}/></button>}</div></div>:<div className="assessment-result"><div className="student-step-eyebrow"><span/>ASSESSMENT COMPLETE</div><div className="assessment-result-score">{score}<span> / 100</span></div><p className="student-description">This score is calculated from all 20 submitted answers. FORGE can use the difficulty-wise and subject-wise evidence for the next learning steps.</p><div className="assessment-breakdown score-difficulty-grid">{sectionCounts.map(([label,count])=>{const idx=questions.map((x,i)=>x.difficulty===label?i:null).filter(x=>x!==null);const correct=idx.filter(i=>answers[i]===questions[i].correct).length;const pct=count?Math.round(correct/count*100):0;return <div className={`assessment-breakdown-card difficulty-result difficulty-${label.toLowerCase()}`} key={label}><div><strong>{label}</strong><small>{correct} / {count} correct</small></div><b>{pct}%</b></div>})}</div><div className="assessment-breakdown" style={{marginTop:10}}>{subjects.map(subject=>{const idx=questions.map((x,i)=>x.subject===subject?i:null).filter(x=>x!==null);const correct=idx.filter(i=>answers[i]===questions[i].correct).length;return <div className="assessment-breakdown-card" key={subject}><strong>{subject}</strong><small>{correct} / {idx.length} correct</small></div>})}</div><div className="student-bottom"><div className="student-validation"><strong>Evidence captured.</strong> Next: personalized scoring and roadmap.</div><button className="student-continue" onClick={()=>navigate("/student/scores")}>View Scores <ArrowRight size={15}/></button></div></div>}</div></main></>;
}


function StudentScores(){
 const navigate=useNavigate();
 const subjects=readS("forge_student_subjects",[]),profile=readS("forge_student_profile",{}),levels=readS("forge_student_levels",{}),answers=readS("forge_student_assessment_answers",{});
 const questions=useMemo(()=>buildAssessmentQuestions(subjects,profile.targetRole||"",levels),[subjects,profile.targetRole,levels]);
 const total=questions.length,correct=questions.reduce((n,q,i)=>n+(answers[i]===q.correct?1:0),0),overallScore=total?Math.round(correct/total*100):0;
 const sectionCounts=["Easy","Intermediate","Hard"].map(label=>{const idx=questions.map((q,i)=>q.difficulty===label?i:null).filter(i=>i!==null),c=idx.filter(i=>answers[i]===questions[i].correct).length;return {label,total:idx.length,correct:c,score:idx.length?Math.round(c/idx.length*100):0};});
 const subjectScores={}; subjects.forEach(subject=>{const idx=questions.map((q,i)=>q.subject===subject?i:null).filter(i=>i!==null),c=idx.filter(i=>answers[i]===questions[i].correct).length;subjectScores[subject]={total:idx.length,correct:c,score:idx.length?Math.round(c/idx.length*100):0};});
 const strong=[],developing=[],priority=[]; Object.entries(subjectScores).forEach(([subject,data])=>{if(data.score>=80)strong.push(subject);else if(data.score>=60)developing.push(subject);else priority.push(subject);});
 const readiness=overallScore>=80?"Strong baseline":overallScore>=60?"Developing baseline":"Foundation build required";
 sessionStorage.setItem("forge_student_scores",JSON.stringify({overallScore,totalQuestions:total,totalCorrect:correct,difficultyScores:sectionCounts,subjectScores,strong,developing,priority,readiness,role:profile.targetRole||"",targetYear:Number(sessionStorage.getItem("forge_student_target_year"))||null}));
 return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/assessment")}><ChevronLeft size={15}/>Back</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">06 / 08</div></div><div className="student-progress"><span style={{width:"75%"}}/></div><div className="student-step-eyebrow"><span/>06 / SCORES</div><h1 className="student-title">Your evidence<br/><em>has a baseline.</em></h1><p className="student-description">FORGE calculated this baseline directly from the answers submitted in the assessment.</p><div className="assessment-result"><div className="assessment-result-score">{overallScore}<span> / 100</span></div><div className="assessment-breakdown">{sectionCounts.map(x=><div className="assessment-breakdown-card" key={x.label}><strong>{x.label}</strong><small>{x.correct} / {x.total} correct · {x.score}%</small></div>)}</div><div className="score-subject-grid">{subjects.map(s=>{const d=subjectScores[s]||{};const pct=Number(d.score||0);const state=pct>=80?"strong":pct>=60?"developing":"priority";return <div className={`score-subject-card score-${state}`} key={s}><div className="score-subject-top"><span className="score-subject-state">{state==="strong"?"STRONG":state==="developing"?"DEVELOPING":"PRIORITY GAP"}</span><b>{pct}%</b></div><h3>{s}</h3><p>{d.correct||0} / {d.total||0} correct answers</p><div className="score-subject-bar"><span style={{width:`${pct}%`}}/></div><small>{state==="strong"?"Keep this capability active.":state==="developing"?"Needs focused practice.":"Start here in your roadmap."}</small></div>})}</div><div className="capability-signal-grid" style={{marginTop:20}}><div><span className="signal-dot signal-red"/>Priority gaps<strong>{priority.length}</strong></div><div><span className="signal-dot signal-yellow"/>Developing<strong>{developing.length}</strong></div><div><span className="signal-dot signal-green"/>Strong<strong>{strong.length}</strong></div></div><div className="student-bottom"><div className="student-validation"><strong>Baseline recorded.</strong> Roadmap can now be computed from this evidence.</div><button className="student-continue" onClick={()=>navigate("/student/roadmap")}>Build Roadmap <ArrowRight size={15}/></button></div></div></div></main></>;
}

function StudentRoadmap(){
 const navigate=useNavigate(); const subjects=readS("forge_student_subjects",[]),profile=readS("forge_student_profile",{}),levels=readS("forge_student_levels",{}),scores=readS("forge_student_scores",{});
 const targetYear=Number(sessionStorage.getItem("forge_student_target_year"))||new Date().getFullYear()+1,role=profile.targetRole||"Software Engineer",dailyText=profile.dailyHours||"1–2 hrs",readiness=profile.readiness||"6 months";
 const roleSubjects=ROLE_SUGGESTIONS[role]||ROLE_SUGGESTIONS["Software Engineer"],dailyHoursMap={"3–5":4,"5–10":7.5,"10–15":12.5,"15–20":17.5,"20+":20},dailyHours=dailyHoursMap[dailyText]||1.5,weeklyHours=Math.round(dailyHours*7*2)/2,levelWeight={"From zero":1,"Fundamentals":.72,"Interview preparation":.48},urgency={"3 months":1.35,"6 months":1.15,"1 year":1,"By 2027":1.1,"By 2028":.95,"By 2029":.85};
 const yd=Math.max(0,targetYear-new Date().getFullYear()),targetUrgency=yd===0?1.3:yd===1?1.15:yd===2?1:.9;
 const topicMap={DSA:["Arrays & Strings","Hashing","Stacks & Queues","Trees & Graphs","Dynamic Programming"],"C++":["STL","Pointers & References","OOP","Templates","Competitive Programming"],Java:["OOP","Collections","Exception Handling","Streams","Multithreading"],Python:["Core Python","Functions & Modules","OOP","Data Handling","Python for AI/ML","NumPy for Data Work","Pandas for Data Analysis"],DBMS:["ER Model","Normalization","Transactions","Indexing","Query Optimization"],"Operating Systems":["Processes","Threads","Scheduling","Memory Management","File Systems"],"Computer Networks":["OSI & TCP/IP","IP Addressing","Routing","Transport Layer","Network Security"],OOP:["Classes & Objects","Inheritance","Polymorphism","Abstraction","Design Principles"],SQL:["SELECT & Filtering","Joins","Aggregations","Subqueries","Window Functions","CTEs"],"System Design":["Scalability","Caching","Databases","Load Balancing","Distributed Systems"],"Machine Learning":["Regression","Classification","Trees & Ensembles","Clustering","Model Evaluation","Cross Validation"],"Deep Learning":["Neural Networks","Backpropagation","CNNs","RNNs","Transformers"],Statistics:["Descriptive Statistics","Probability","Distributions","Hypothesis Testing","Correlation & Covariance","Regression Statistics"],"Data Science":["EDA","Data Cleaning","Feature Engineering","Data Leakage","Visualization","Model Interpretation"],Pandas:["Series & DataFrames","Data Cleaning","GroupBy & Aggregation","Merge & Join","Missing Values"],NumPy:["Arrays & Vectorization","Indexing & Slicing","Broadcasting","Linear Algebra","Random Sampling"],"Data Visualization":["Matplotlib","Seaborn","Distribution Plots","Correlation Visuals","Storytelling with Charts"],"HTML/CSS":["Semantic HTML","CSS Layout","Flexbox","Grid","Responsive Design"],JavaScript:["ES6+","DOM","Async JavaScript","Promises","Modules"],React:["Components","Props & State","Hooks","Routing","API Integration"],"Node.js":["Node Fundamentals","Express","REST APIs","Authentication","Backend Architecture"],"REST APIs":["HTTP","CRUD","Authentication","Validation","API Design"],"Git/GitHub":["Git Basics","Branching","Merge & Rebase","Pull Requests","Collaboration"],Cloud:["Cloud Fundamentals","Compute","Storage","Networking","Deployment"]};
 const items=subjects.map(subject=>{const score=Number(scores.subjectScores?.[subject]?.score??scores.overallScore??0),gap=1-score/100,level=levels[subject]||"From zero",priority=gap*(levelWeight[level]||1)*(roleSubjects.includes(subject)?1.25:1)*(urgency[readiness]||1)*targetUrgency;return {subject,score,level,priority,status:score>=80?"Strong":score>=60?"Developing":"Priority Gap",roleRelevant:roleSubjects.includes(subject),topics:topicMap[subject]||[`${subject} Fundamentals`,`${subject} Core Concepts`,`${subject} Applied Practice`,`${subject} Projects`,`${subject} Interview Practice`]};}).sort((a,b)=>b.priority-a.priority);
 const totalPriority=items.reduce((s,x)=>s+x.priority,0); let allocations=items.map((x,i)=>{const dh=Math.max(.5,Math.round((totalPriority?dailyHours*x.priority/totalPriority:dailyHours/Math.max(1,items.length))*2)/2);return {...x,rank:i+1,dailyHours:dh,weeklyHours:Math.round(dh*7*2)/2};});
 if(allocations.length){const total=allocations.reduce((s,x)=>s+x.dailyHours,0);const diff=Math.round((dailyHours-total)*2)/2;allocations[0].dailyHours=Math.max(.5,Math.round((allocations[0].dailyHours+diff)*2)/2);allocations[0].weeklyHours=Math.round(allocations[0].dailyHours*7*2)/2;}
 sessionStorage.setItem("forge_student_roadmap",JSON.stringify({generatedAt:new Date().toISOString(),role,targetYear,readiness,dailyHours,weeklyHours,assessmentScore:Number(scores.overallScore||0),prioritySubjects:allocations.slice(0,3).map(x=>x.subject),subjects:allocations})); const top=allocations[0];
 return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/scores")}><ChevronLeft size={15}/>Back</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">07 / 08</div></div><div className="student-progress"><span style={{width:"87.5%"}}/></div><div className="student-step-eyebrow"><span/>07 / PERSONALIZED ROADMAP</div><h1 className="student-title">Your capability path<br/><em>is ready.</em></h1><p className="student-description">FORGE converts your assessment evidence, current levels, target role, timeline and study capacity into a computed priority order.</p><div className="assessment-result"><div className="assessment-breakdown"><div className="assessment-breakdown-card"><strong>{role}</strong><small>Target role</small></div><div className="assessment-breakdown-card"><strong>{targetYear}</strong><small>Target year</small></div><div className="assessment-breakdown-card"><strong>{dailyHours>=1?`${Number(dailyHours.toFixed(1))} hrs`:`${Math.round(dailyHours*60)} min`}</strong><small>Daily study capacity</small></div></div>{top&&<div className="generated-task" style={{marginTop:18}}><small>FIRST PRIORITY</small><h3>{top.subject}</h3><p>{top.status==="Priority Gap"?`Your assessment shows a meaningful gap in ${top.subject}.`:top.status==="Developing"?`${top.subject} needs focused practice to reach interview readiness.`:`${top.subject} is currently a stronger capability; maintain it while higher-priority gaps are addressed.`}</p><p style={{marginTop:10,fontSize:11,fontWeight:700,color:"#3565d4"}}>ALLOCATED · {top.dailyHours} HOURS / DAY</p></div>}<div className="roadmap-allocation-grid">{allocations.map(x=>{const pct=Math.min(100,Math.max(8,Math.round(x.priority/Math.max(...allocations.map(a=>a.priority),1)*100)));return <div className={`roadmap-allocation-card ${x.rank===1?"top-priority":""}`} key={x.subject}><div className="roadmap-card-top"><span>0{x.rank}</span><em>{x.roleRelevant?"ROLE RELEVANT":"SUPPORTING"}</em></div><div className="roadmap-card-main"><div><h3>{x.subject}</h3><p>{x.level} · {x.status}</p></div><strong>{x.dailyHours>=1?`${Number(x.dailyHours.toFixed(1))}h`:`${Math.round(x.dailyHours*60)}m`}<small>/ day</small></strong></div><div className="roadmap-card-bar"><span style={{width:`${pct}%`}}/></div><div className="roadmap-card-foot"><span>{Math.round(x.score)}/100 baseline</span><b>{x.status==="Priority Gap"?"BUILD FIRST":x.status==="Developing"?"STRENGTHEN":"MAINTAIN"}</b></div></div>})}</div><div className="student-bottom"><div className="student-validation"><strong>Roadmap generated.</strong> Next: weekly execution planning.</div><button className="student-continue" onClick={()=>{setForgeOnboardingComplete();navigate("/student");}}>Enter My FORGE <ArrowRight size={15}/></button></div></div></div></main></>;
}


const LEARNING_TOPIC_DATA={
  "DSA":{
    "Arrays & Strings":{summary:"Learn contiguous data structures, indexing, traversal, two-pointer patterns and common string operations.",keyPoints:["Indexing is typically O(1) for arrays.","Two pointers can reduce nested scans in ordered data.","String problems often combine hashing, pointers or sliding windows."],resources:[{title:"GeeksforGeeks · Arrays",url:"https://www.geeksforgeeks.org/array-data-structure/",type:"Article"},{title:"YouTube · Arrays & Strings",url:"https://www.youtube.com/results?search_query=arrays+and+strings+dsa",type:"Video"}]},
    "Hashing":{summary:"Use hash tables to trade memory for faster lookup, counting and duplicate detection.",keyPoints:["Average hash-table lookup is O(1).","Collision handling is implementation dependent.","Frequency maps are useful for counting and membership problems."],resources:[{title:"GeeksforGeeks · Hashing",url:"https://www.geeksforgeeks.org/hashing-data-structure/",type:"Article"},{title:"YouTube · Hashing DSA",url:"https://www.youtube.com/results?search_query=hashing+dsa",type:"Video"}]},
    "Stacks & Queues":{summary:"Understand LIFO and FIFO structures and their use in parsing, traversal and scheduling.",keyPoints:["Stack follows LIFO.","Queue follows FIFO.","Monotonic stacks solve several next-greater/smaller problems efficiently."],resources:[{title:"GeeksforGeeks · Stack",url:"https://www.geeksforgeeks.org/stack-data-structure/",type:"Article"},{title:"YouTube · Stacks & Queues",url:"https://www.youtube.com/results?search_query=stacks+queues+dsa",type:"Video"}]},
    "Trees & Graphs":{summary:"Build traversal intuition for hierarchical and network-like data using DFS, BFS and graph representations.",keyPoints:["DFS uses recursion or an explicit stack.","BFS uses a queue and finds shortest unweighted paths.","Adjacency lists are efficient for sparse graphs."],resources:[{title:"GeeksforGeeks · Graph Data Structure",url:"https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",type:"Article"},{title:"YouTube · Trees & Graphs",url:"https://www.youtube.com/results?search_query=trees+graphs+dsa",type:"Video"}]},
    "Dynamic Programming":{summary:"Break problems into overlapping subproblems and reuse computed results with memoization or tabulation.",keyPoints:["Define state before writing transitions.","Memoization is top-down; tabulation is bottom-up.","Space can sometimes be optimized by retaining only required previous states."],resources:[{title:"GeeksforGeeks · Dynamic Programming",url:"https://www.geeksforgeeks.org/dynamic-programming/",type:"Article"},{title:"YouTube · Dynamic Programming",url:"https://www.youtube.com/results?search_query=dynamic+programming+dsa",type:"Video"}]}
  },
  "Python":{
    "Core Python":{summary:"Build fluency with Python syntax, data types, control flow and built-in collections.",keyPoints:["Lists are mutable ordered sequences.","Dictionaries map keys to values.","List comprehensions provide concise transformations."],resources:[{title:"Python · Official Tutorial",url:"https://docs.python.org/3/tutorial/",type:"Article"},{title:"YouTube · Core Python",url:"https://www.youtube.com/results?search_query=core+python+tutorial",type:"Video"}]},
    "Functions & Modules":{summary:"Organize Python programs using functions, imports, modules and reusable interfaces.",keyPoints:["Functions reduce duplication and isolate behavior.","Modules provide namespace boundaries.","Explicit imports improve readability and maintainability."],resources:[{title:"Python · Modules",url:"https://docs.python.org/3/tutorial/modules.html",type:"Article"},{title:"YouTube · Python Modules",url:"https://www.youtube.com/results?search_query=python+functions+modules",type:"Video"}]},
    "OOP":{summary:"Use classes, objects, inheritance and composition to model reusable behavior.",keyPoints:["Objects combine state and behavior.","Composition can reduce rigid inheritance hierarchies.","Encapsulation controls how state is exposed."],resources:[{title:"Python · Classes",url:"https://docs.python.org/3/tutorial/classes.html",type:"Article"},{title:"YouTube · Python OOP",url:"https://www.youtube.com/results?search_query=python+oop",type:"Video"}]},
    "Data Handling":{summary:"Read, transform and validate structured data before analysis or modeling.",keyPoints:["Validate input before downstream processing.","Missing values should be handled deliberately.","Keep transformation steps reproducible."],resources:[{title:"Pandas · Getting Started",url:"https://pandas.pydata.org/docs/getting_started/index.html",type:"Article"},{title:"YouTube · Python Data Handling",url:"https://www.youtube.com/results?search_query=python+data+handling+pandas",type:"Video"}]},
    "Python for AI/ML":{summary:"Use Python libraries and clean data pipelines to build reproducible machine-learning workflows.",keyPoints:["Separate preprocessing from evaluation to avoid leakage.","Use deterministic pipelines where possible.","Track features, labels and evaluation data separately."],resources:[{title:"scikit-learn · User Guide",url:"https://scikit-learn.org/stable/user_guide.html",type:"Article"},{title:"YouTube · Python for ML",url:"https://www.youtube.com/results?search_query=python+for+machine+learning",type:"Video"}]}
  },
  "Machine Learning":{
    "Regression":{summary:"Predict continuous outcomes and understand the relationship between features and a target.",keyPoints:["Regression predicts continuous values.","MAE and RMSE measure prediction error.","Feature scaling matters for some algorithms."],resources:[{title:"scikit-learn · Linear Models",url:"https://scikit-learn.org/stable/modules/linear_model.html",type:"Article"},{title:"YouTube · Regression",url:"https://www.youtube.com/results?search_query=machine+learning+regression",type:"Video"}]},
    "Classification":{summary:"Predict discrete classes and evaluate models with metrics appropriate to the decision context.",keyPoints:["Accuracy can be misleading on imbalanced data.","Precision and recall capture different error costs.","A confusion matrix shows class-level outcomes."],resources:[{title:"scikit-learn · Classification",url:"https://scikit-learn.org/stable/supervised_learning.html",type:"Article"},{title:"YouTube · Classification",url:"https://www.youtube.com/results?search_query=machine+learning+classification",type:"Video"}]},
    "Trees & Ensembles":{summary:"Use decision trees and ensembles to capture nonlinear relationships and interactions.",keyPoints:["Trees partition feature space with decisions.","Random forests reduce variance through averaging.","Boosting builds models sequentially to reduce error."],resources:[{title:"scikit-learn · Ensemble Methods",url:"https://scikit-learn.org/stable/modules/ensemble.html",type:"Article"},{title:"YouTube · Trees & Ensembles",url:"https://www.youtube.com/results?search_query=decision+trees+random+forest+boosting",type:"Video"}]},
    "Clustering":{summary:"Group observations without labeled targets and inspect whether discovered structure is meaningful.",keyPoints:["K-Means requires a chosen number of clusters.","Distance metrics influence cluster structure.","Silhouette score can help assess separation and cohesion."],resources:[{title:"scikit-learn · Clustering",url:"https://scikit-learn.org/stable/modules/clustering.html",type:"Article"},{title:"YouTube · Clustering",url:"https://www.youtube.com/results?search_query=machine+learning+clustering",type:"Video"}]},
    "Model Evaluation":{summary:"Measure generalization using suitable validation schemes and metrics rather than training performance alone.",keyPoints:["Holdout or cross-validation estimates generalization.","Metric choice should reflect the task.","Data leakage can make evaluation falsely optimistic."],resources:[{title:"scikit-learn · Model Evaluation",url:"https://scikit-learn.org/stable/modules/model_evaluation.html",type:"Article"},{title:"YouTube · Model Evaluation",url:"https://www.youtube.com/results?search_query=machine+learning+model+evaluation",type:"Video"}]}
  },
  "SQL":{
    "SELECT & Filtering":{summary:"Retrieve precise records with SELECT, WHERE, ORDER BY and LIMIT-style operations.",keyPoints:["WHERE filters rows before aggregation.","ORDER BY controls result ordering.","SELECT should request only needed columns when practical."],resources:[{title:"PostgreSQL · SELECT",url:"https://www.postgresql.org/docs/current/sql-select.html",type:"Article"},{title:"YouTube · SQL Basics",url:"https://www.youtube.com/results?search_query=sql+select+where+tutorial",type:"Video"}]},
    "Joins":{summary:"Combine related rows across tables using keys and join conditions.",keyPoints:["INNER JOIN keeps matching rows.","LEFT JOIN preserves rows from the left relation.","Incorrect join keys can multiply rows unexpectedly."],resources:[{title:"PostgreSQL · Joins",url:"https://www.postgresql.org/docs/current/queries-table-expressions.html",type:"Article"},{title:"YouTube · SQL Joins",url:"https://www.youtube.com/results?search_query=sql+joins",type:"Video"}]},
    "Aggregations":{summary:"Summarize rows with COUNT, SUM, AVG, MIN, MAX and GROUP BY.",keyPoints:["GROUP BY defines aggregation groups.","HAVING filters groups after aggregation.","NULL handling affects aggregate results."],resources:[{title:"PostgreSQL · Aggregate Functions",url:"https://www.postgresql.org/docs/current/functions-aggregate.html",type:"Article"},{title:"YouTube · SQL Aggregations",url:"https://www.youtube.com/results?search_query=sql+group+by+having",type:"Video"}]},
    "Subqueries":{summary:"Use nested queries when a query needs an intermediate relation or comparison.",keyPoints:["Correlated subqueries can execute relative to an outer row.","EXISTS tests whether matching rows exist.","A join or CTE may be clearer than a deeply nested query."],resources:[{title:"PostgreSQL · Subqueries",url:"https://www.postgresql.org/docs/current/functions-subquery.html",type:"Article"},{title:"YouTube · SQL Subqueries",url:"https://www.youtube.com/results?search_query=sql+subqueries",type:"Video"}]},
    "Window Functions":{summary:"Compute row-aware analytics without collapsing rows into one result per group.",keyPoints:["Window functions retain row-level output.","PARTITION BY defines the window groups.","ORDER BY inside a window defines row sequence."],resources:[{title:"PostgreSQL · Window Functions",url:"https://www.postgresql.org/docs/current/tutorial-window.html",type:"Article"},{title:"YouTube · SQL Window Functions",url:"https://www.youtube.com/results?search_query=sql+window+functions",type:"Video"}]}
  },
  "DBMS":{
    "ER Model":{summary:"Model entities, attributes and relationships before implementing a relational schema.",keyPoints:["Entities represent domain objects.","Relationships capture associations.","Cardinality describes relationship multiplicity."],resources:[{title:"GeeksforGeeks · ER Model",url:"https://www.geeksforgeeks.org/introduction-of-er-model/",type:"Article"},{title:"YouTube · ER Diagram",url:"https://www.youtube.com/results?search_query=dbms+er+diagram",type:"Video"}]},
    "Normalization":{summary:"Reduce redundancy and update anomalies by decomposing relations using functional dependencies.",keyPoints:["1NF requires atomic values in the usual relational formulation.","2NF removes partial dependency on a composite key.","3NF removes relevant transitive dependencies."],resources:[{title:"GeeksforGeeks · Normalization",url:"https://www.geeksforgeeks.org/normal-forms-in-dbms/",type:"Article"},{title:"YouTube · DBMS Normalization",url:"https://www.youtube.com/results?search_query=dbms+normalization",type:"Video"}]},
    "Transactions":{summary:"Understand transaction boundaries, ACID properties and concurrency behavior.",keyPoints:["Atomicity treats a transaction as an all-or-nothing unit.","Isolation controls interference between concurrent transactions.","Durability concerns committed data surviving failures."],resources:[{title:"PostgreSQL · Transactions",url:"https://www.postgresql.org/docs/current/tutorial-transactions.html",type:"Article"},{title:"YouTube · DBMS Transactions",url:"https://www.youtube.com/results?search_query=dbms+transactions+acid",type:"Video"}]},
    "Indexing":{summary:"Use indexes to accelerate suitable access patterns while considering write and storage costs.",keyPoints:["Indexes can reduce lookup work.","Indexes consume storage and add maintenance cost.","Selectivity and query patterns matter when choosing indexes."],resources:[{title:"PostgreSQL · Indexes",url:"https://www.postgresql.org/docs/current/indexes.html",type:"Article"},{title:"YouTube · DBMS Indexing",url:"https://www.youtube.com/results?search_query=dbms+indexing+b+tree",type:"Video"}]},
    "Query Optimization":{summary:"Understand how database engines choose execution strategies and how query shape affects performance.",keyPoints:["Execution plans reveal chosen operators.","Statistics help optimizers estimate costs.","Avoiding unnecessary rows and columns can reduce work."],resources:[{title:"PostgreSQL · Using EXPLAIN",url:"https://www.postgresql.org/docs/current/using-explain.html",type:"Article"},{title:"YouTube · Query Optimization",url:"https://www.youtube.com/results?search_query=sql+query+optimization+explain",type:"Video"}]}
  }
};

const GENERIC_TOPIC_QUESTIONS=[
  {prompt:"Which action most directly improves mastery of this topic?",options:["Understand the core concept and apply it", "Only memorize terminology", "Skip examples", "Avoid practice"],correct:0},
  {prompt:"When learning a technical topic, what is the strongest evidence of understanding?",options:["Being able to explain and use it", "Opening a tutorial once", "Saving a bookmark", "Reading only the title"],correct:0},
  {prompt:"What should you do when your first solution fails?",options:["Inspect the failure, revise and retry", "Delete all evidence", "Stop practicing", "Change the topic immediately"],correct:0},
  {prompt:"Which practice pattern best supports retention?",options:["Retrieval and spaced practice", "Passive rereading only", "Never revisiting mistakes", "Studying without examples"],correct:0},
  {prompt:"What should a learner record after solving a difficult problem?",options:["The reasoning, mistake and corrected approach", "Only the final answer", "Nothing", "Only the resource URL"],correct:0}
];


/* =========================================================
   EMBEDDED TOPIC VIDEOS
   Every learning topic gets an in-page YouTube player.
   No "Open video" / search link is shown to the learner.
========================================================= */
const TOPIC_VIDEO_CATALOG = {
  "DSA": [
    {kind:"playlist", id:"PLgUwDviBIf0oF6QL8m22w1hIDC1vJ_BHz", title:"Striver A2Z DSA — Complete Playlist", source:"Striver / takeUforward"},
    {kind:"video", id:"hCrO_cR7kno", title:"DSA Full Course with Practical — Complete Course", source:"WsCube Tech"}
  ],
  "C++": [
    {kind:"playlist", id:"PLfqMhTWNBTe0b2nM6JHVCnAkhQRGiZMSJ", title:"C++ — Complete Course Playlist", source:"Apna College"},
    {kind:"video", id:"Jnwm2DvmyPo", title:"C++ Full Course 2026 — Complete Beginner Guide", source:"Codynn"}
  ],
  "Java": [
    {kind:"playlist", id:"PLQEaRBV9gAFsR15tNo2QLF9d2qc-c018p", title:"Java Full Course 2026 — Complete Playlist", source:"Coder Army"},
    {kind:"video", id:"LBqE4YOvhyc", title:"Java Full Course — Introduction & Foundations", source:"Coder Army"}
  ],
  "Python": [
    {kind:"video", id:"rfscVS0vtbw", title:"Learn Python — Full Course for Beginners", source:"freeCodeCamp"},
    {kind:"video", id:"H2EJuAcrZYU", title:"Python Full Course for Beginners — Complete All-in-One", source:"Python Full Course"}
  ],
  "DBMS": [
    {kind:"playlist", id:"PLxCzCOWd7aiFAN6I8CuViBuCdJgiOkT2Y", title:"DBMS — Complete Playlist", source:"Gate Smashers"},
    {kind:"playlist", id:"PLDzeHZWIZsTpukecmA2p5rhHM14bl2dHU", title:"DBMS Placement Series — Complete Playlist", source:"CodeHelp"}
  ],
  "Operating Systems": [
    {kind:"playlist", id:"PLDEblXlTiav-j26innOowF-S-i7-4zOcO", title:"Operating Systems — Full Lecture Playlist", source:"VNIT course lectures"},
    {kind:"playlist", id:"PLxCzCOWd7aiGz9donHRrE9I3Mwn6XdP8p", title:"Operating System — Complete Playlist", source:"Gate Smashers"}
  ],
  "Computer Networks": [
    {kind:"playlist", id:"PLxCzCOWd7aiGFBD2-2joCpWOLUrDLvVV_", title:"Computer Networks — Complete Playlist", source:"Gate Smashers"},
    {kind:"video", id:"JFF2vJaN0Cw", title:"Computer Networks — Full Syllabus Lecture", source:"Gate Smashers"}
  ],
  "OOP": [
    {kind:"video", id:"tmXD7Kzun54", title:"Object Oriented Programming in Java — Full Foundation", source:"Coder Army"},
    {kind:"video", id:"ZDa-Z5JzLYM", title:"Python OOP — Classes and Objects", source:"Corey Schafer"}
  ],
  "SQL": [
    {kind:"video", id:"HXV3zeQKqGY", title:"SQL Tutorial — Full Database Course for Beginners", source:"freeCodeCamp"},
    {kind:"video", id:"7S_tz1z_5bA", title:"MySQL Tutorial for Beginners — Full Course", source:"MySQL Full Course"}
  ],
  "System Design": [
    {kind:"video", id:"_PipiJ_i6Pk", title:"System Design Full Course 2026 — 6+ Hours", source:"Sangam Mukherjee"},
    {kind:"video", id:"ifVhkOXZfsU", title:"System Design Full Course — Fundamentals to Interviews", source:"The Coding Camp"}
  ],
  "Machine Learning": [
    {kind:"playlist", id:"PLxCzCOWd7aiEXg5BV10k9THtjnS48yI-T", title:"Machine Learning — Complete Playlist", source:"5 Minutes Engineering"},
    {kind:"video", id:"LvC68w9JS4Y", title:"Machine Learning — Full Course", source:"Machine Learning Full Course"}
  ],
  "Deep Learning": [
    {kind:"playlist", id:"PLxCzCOWd7aiHQ9Qyo70JCTkTxczPnVC6s", title:"Deep Learning — Complete Playlist", source:"Gate Smashers"},
    {kind:"video", id:"gDZ6czwuQ18", start:1520, title:"Deep Learning — Neural Networks & Training", source:"WsCube Tech"}
  ],
  "Statistics": [
    {kind:"video", id:"jHX0iHh6G1Q", start:18000, title:"Statistics — Complete Data Science Course Section", source:"My CS"},
    {kind:"video", id:"gDZ6czwuQ18", start:931, title:"Statistics & Probability — Full Data Science Course", source:"WsCube Tech"}
  ],
  "Data Science": [
    {kind:"video", id:"jHX0iHh6G1Q", title:"Data Science Full Course for Beginners", source:"My CS"},
    {kind:"video", id:"gDZ6czwuQ18", title:"Data Science Full Course — 27 Hours", source:"WsCube Tech"}
  ],
  "HTML/CSS": [
    {kind:"video", id:"G3e-cpL7ofc", title:"HTML & CSS Full Course — Beginner to Pro", source:"SuperSimpleDev"},
    {kind:"playlist", id:"PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w", title:"Web Development — Complete Playlist", source:"CodeWithHarry"}
  ],
  "JavaScript": [
    {kind:"video", id:"6_NrgoEkjnE", title:"JavaScript Full Course 2026 — 22 Hours", source:"Coder Army"},
    {kind:"video", id:"PkZNo7MFNFg", title:"JavaScript Full Course — Beginner Foundations", source:"freeCodeCamp"}
  ],
  "React": [
    {kind:"video", id:"CgkZ7MvWUAA", title:"React JS Full Course — Complete Beginner Course", source:"Bro Code"},
    {kind:"video", id:"Ke90Tje7VS0", title:"React JS Full Course — Modern React", source:"JavaScript Mastery"}
  ],
  "Node.js": [
    {kind:"video", id:"HVjjoMvutj4", title:"Full Stack Web Development — Node / Backend Section", source:"Full Stack Course"},
    {kind:"video", id:"-58TX3yCHI4", title:"REST API Full Course for Beginners", source:"upGrad"}
  ],
  "REST APIs": [
    {kind:"video", id:"-58TX3yCHI4", title:"REST API Full Course for Beginners (2026)", source:"upGrad"},
    {kind:"video", id:"_PipiJ_i6Pk", start:7190, title:"System Design — REST API & HTTP Fundamentals", source:"Sangam Mukherjee"}
  ],
  "Git/GitHub": [
    {kind:"video", id:"apGV9Kg7ics", title:"Complete Git and GitHub Tutorial", source:"Kunal Kushwaha"},
    {kind:"video", id:"rH3zE7VlIMs", title:"Git and GitHub — Full Course", source:"Boot.dev / ThePrimeagen"}
  ],
  "Cloud": [
    {kind:"video", id:"Vrkqucq19IY", title:"Cloud Computing Full Course 2026", source:"Simplilearn"},
    {kind:"video", id:"GKRsxaNY4MQ", title:"Cloud Computing Full Course — AWS, Azure & GCP", source:"Simplilearn"}
  ]
};

const SUBJECT_VIDEO_ALIASES = {
  "JavaScript": "JavaScript",
  "HTML/CSS": "HTML/CSS",
  "Node.js": "Node.js",
  "REST APIs": "REST APIs",
  "Git/GitHub": "Git/GitHub",
  "Cloud": "Cloud"
};

function getTopicVideos(subject, topic) {
  const key = SUBJECT_VIDEO_ALIASES[subject] || subject;
  const videos = TOPIC_VIDEO_CATALOG[key];
  if (videos?.length >= 2) return videos.slice(0, 2);

  // Never fall back to DSA. For an unlisted subject, use a neutral course search
  // card rather than showing an unrelated subject's content.
  return [
    {kind:"search", query:`${subject} ${topic} full course`, title:`${subject} — ${topic} Full Course`, source:"YouTube learning search"},
    {kind:"search", query:`${subject} ${topic} complete playlist`, title:`${subject} — ${topic} Complete Playlist`, source:"YouTube learning search"}
  ];
}

function getYoutubeEmbedUrl(video) {
  if (!video) return "";
  if (video.kind === "playlist") {
    const params = new URLSearchParams({listType:"playlist", list:video.id, rel:"0", playsinline:"1"});
    return `https://www.youtube-nocookie.com/embed?${params.toString()}`;
  }
  if (video.kind === "search") return "";
  const params = new URLSearchParams({rel:"0", playsinline:"1"});
  if (Number(video.start) > 0) params.set("start", String(video.start));
  return `https://www.youtube-nocookie.com/embed/${video.id}?${params.toString()}`;
}

function getVideoLabel(video) {
  if (video.kind === "playlist") return "COMPLETE PLAYLIST";
  if (video.kind === "search") return "CURATED SEARCH";
  return "FULL COURSE / VIDEO";
}


const DATA_SCIENCE_LEARNING_OVERRIDES={
  Python:{
    "NumPy for Data Work":{summary:"Use NumPy arrays, vectorization and numerical operations as the computational base of a data-science workflow.",keyPoints:["ndarray is the core numerical structure.","Vectorization reduces explicit Python loops.","Broadcasting applies operations across compatible shapes."],resources:[{title:"NumPy · Quickstart",url:"https://numpy.org/doc/stable/user/quickstart.html",type:"Article"},{title:"YouTube · NumPy for Data Science",url:"https://www.youtube.com/results?search_query=numpy+for+data+science",type:"Video"}]},
    "Pandas for Data Analysis":{summary:"Work with tabular data using DataFrames, filtering, grouping, joins and missing-value handling.",keyPoints:["DataFrames represent labeled tabular data.","groupby supports analytical aggregation.","Cleaning and validation should happen before modeling."],resources:[{title:"Pandas · Getting Started",url:"https://pandas.pydata.org/docs/getting_started/index.html",type:"Article"},{title:"YouTube · Pandas for Data Science",url:"https://www.youtube.com/results?search_query=pandas+for+data+science",type:"Video"}]}
  },
  Statistics:{
    "Descriptive Statistics":{summary:"Summarize distributions with measures of center, spread and shape before making statistical decisions.",keyPoints:["Mean and median describe central tendency.","Variance and standard deviation describe spread.","Outliers can strongly affect the mean."],resources:[{title:"NIST · Descriptive Statistics",url:"https://www.itl.nist.gov/div898/handbook/eda/eda.htm",type:"Article"},{title:"YouTube · Descriptive Statistics",url:"https://www.youtube.com/results?search_query=descriptive+statistics+data+science",type:"Video"}]},
    "Correlation & Covariance":{summary:"Measure association between variables while keeping association distinct from causation.",keyPoints:["Correlation measures linear association.","Covariance is scale-dependent.","Correlation does not establish causality."],resources:[{title:"NIST · Correlation",url:"https://www.itl.nist.gov/div898/handbook/eda/section3/eda33.htm",type:"Article"},{title:"YouTube · Correlation in Data Science",url:"https://www.youtube.com/results?search_query=correlation+covariance+data+science",type:"Video"}]}
  },
  SQL:{
    "Window Functions":{summary:"Use SQL window functions to calculate rankings, running totals and within-group comparisons without collapsing rows.",keyPoints:["PARTITION BY defines analytical groups.","ORDER BY controls row order inside a window.","Window functions preserve row-level detail."],resources:[{title:"PostgreSQL · Window Functions",url:"https://www.postgresql.org/docs/current/tutorial-window.html",type:"Article"},{title:"YouTube · SQL Window Functions",url:"https://www.youtube.com/results?search_query=sql+window+functions+data+science",type:"Video"}]},
    "CTEs":{summary:"Use common table expressions to structure complex analytical queries into readable, testable stages.",keyPoints:["WITH defines a reusable query sub-result.","CTEs improve query readability.","Break complex transformations into explicit stages."],resources:[{title:"PostgreSQL · WITH Queries",url:"https://www.postgresql.org/docs/current/queries-with.html",type:"Article"},{title:"YouTube · SQL CTEs",url:"https://www.youtube.com/results?search_query=sql+cte+data+science",type:"Video"}]}
  },
  "Data Science":{
    "EDA":{summary:"Explore structure, distributions, missingness and relationships before selecting a modeling approach.",keyPoints:["Inspect shape, types and missingness first.","Use distributions and relationships to form hypotheses.","EDA should inform—not replace—formal validation."],resources:[{title:"Pandas · Getting Started",url:"https://pandas.pydata.org/docs/getting_started/index.html",type:"Article"},{title:"YouTube · Exploratory Data Analysis",url:"https://www.youtube.com/results?search_query=exploratory+data+analysis+python",type:"Video"}]},
    "Data Cleaning":{summary:"Turn raw data into a trustworthy analytical table through validation, missing-value handling and consistent transformations.",keyPoints:["Check duplicates and invalid values.","Document missing-value decisions.","Keep transformations reproducible."],resources:[{title:"Pandas · Missing Data",url:"https://pandas.pydata.org/docs/user_guide/missing_data.html",type:"Article"},{title:"YouTube · Data Cleaning",url:"https://www.youtube.com/results?search_query=data+cleaning+python+pandas",type:"Video"}]},
    "Feature Engineering":{summary:"Construct useful model inputs from raw variables while preserving a clean training/evaluation boundary.",keyPoints:["Transformations should be learned without leaking test information.","Domain-informed features can improve signal.","Keep feature pipelines reproducible."],resources:[{title:"scikit-learn · Preprocessing",url:"https://scikit-learn.org/stable/modules/preprocessing.html",type:"Article"},{title:"YouTube · Feature Engineering",url:"https://www.youtube.com/results?search_query=feature+engineering+machine+learning",type:"Video"}]},
    "Data Leakage":{summary:"Identify information that improperly crosses the training/evaluation boundary and can make performance look unrealistically strong.",keyPoints:["Never tune against the held-out test set.","Fit preprocessing only on training data.","Pipelines help keep transformations inside the correct boundary."],resources:[{title:"scikit-learn · Common Pitfalls",url:"https://scikit-learn.org/stable/common_pitfalls.html",type:"Article"},{title:"YouTube · Data Leakage",url:"https://www.youtube.com/results?search_query=data+leakage+machine+learning",type:"Video"}]}
  },
  Pandas:{
    "Data Cleaning":{summary:"Clean tabular data with explicit rules for missing values, duplicates, types and invalid records.",keyPoints:["Inspect missingness before choosing an imputation strategy.","Convert types deliberately.","Validate row counts after transformations."],resources:[{title:"Pandas · Missing Data",url:"https://pandas.pydata.org/docs/user_guide/missing_data.html",type:"Article"},{title:"YouTube · Pandas Data Cleaning",url:"https://www.youtube.com/results?search_query=pandas+data+cleaning",type:"Video"}]},
    "GroupBy & Aggregation":{summary:"Summarize data by business or analytical groups using groupby and aggregation operations.",keyPoints:["GroupBy splits data into meaningful groups.","Aggregate functions summarize each group.","Always validate the resulting grain."],resources:[{title:"Pandas · GroupBy",url:"https://pandas.pydata.org/docs/user_guide/groupby.html",type:"Article"},{title:"YouTube · Pandas GroupBy",url:"https://www.youtube.com/results?search_query=pandas+groupby+aggregation",type:"Video"}]}
  },
  NumPy:{
    "Arrays & Vectorization":{summary:"Build numerical intuition with ndarray operations, vectorization and shape-aware computation.",keyPoints:["Arrays store homogeneous numerical data efficiently.","Vectorized operations avoid many explicit Python loops.","Shape matters for valid operations."],resources:[{title:"NumPy · Quickstart",url:"https://numpy.org/doc/stable/user/quickstart.html",type:"Article"},{title:"YouTube · NumPy Arrays",url:"https://www.youtube.com/results?search_query=numpy+arrays+vectorization",type:"Video"}]},
    "Broadcasting":{summary:"Apply arithmetic between compatible array shapes without manually copying data.",keyPoints:["Broadcasting compares dimensions from the trailing axis.","Dimensions must be compatible.","Broadcasting can simplify feature transformations."],resources:[{title:"NumPy · Broadcasting",url:"https://numpy.org/doc/stable/user/basics.broadcasting.html",type:"Article"},{title:"YouTube · NumPy Broadcasting",url:"https://www.youtube.com/results?search_query=numpy+broadcasting",type:"Video"}]}
  },
  "Data Visualization":{
    "Matplotlib":{summary:"Build clear analytical charts with Matplotlib while controlling axes, scales, labels and annotations.",keyPoints:["Choose a chart based on the analytical question.","Label units and axes.","Avoid visual choices that distort comparisons."],resources:[{title:"Matplotlib · Tutorials",url:"https://matplotlib.org/stable/tutorials/index.html",type:"Article"},{title:"YouTube · Matplotlib for Data Science",url:"https://www.youtube.com/results?search_query=matplotlib+data+science",type:"Video"}]},
    "Seaborn":{summary:"Use Seaborn for concise statistical visualizations that reveal distributions and relationships.",keyPoints:["Seaborn works naturally with tabular data.","Distribution and relationship plots support EDA.","Use consistent scales and meaningful labels."],resources:[{title:"Seaborn · Documentation",url:"https://seaborn.pydata.org/",type:"Article"},{title:"YouTube · Seaborn Data Visualization",url:"https://www.youtube.com/results?search_query=seaborn+data+visualization",type:"Video"}]}
  }
};

function getLearningData(subject,topic){
  return DATA_SCIENCE_LEARNING_OVERRIDES[subject]?.[topic] || LEARNING_TOPIC_DATA[subject]?.[topic] || {
    summary:`Build practical capability in ${topic} through concept learning, worked examples and deliberate practice.`,
    keyPoints:[`Understand the core concepts of ${topic}.`,`Apply ${topic} to a small practical problem.`,`Review mistakes and explain your reasoning without notes.`],
    resources:[
      {title:`YouTube · ${topic}`,url:`https://www.youtube.com/results?search_query=${encodeURIComponent(subject+" "+topic)}`,type:"Video"},
      {title:`Web · ${subject} ${topic}`,url:`https://www.google.com/search?q=${encodeURIComponent(subject+" "+topic+" tutorial")}`,type:"Search"}
    ]
  };
}


const DATA_SCIENCE_TOPIC_QUESTIONS={
  "Python|NumPy for Data Work":[
    ["Which NumPy object is central to numerical array computation?",["ndarray","DataFrame","HTTP request","DOM node"],0],
    ["What does vectorization primarily reduce?",["Explicit Python loops","Model labels","Database tables","Chart titles"],0],
    ["What is broadcasting used for?",["Operations across compatible array shapes","SQL joins","API authentication","Text formatting"],0],
    ["Which practice improves reproducibility for random experiments?",["Use a fixed random seed","Shuffle labels after evaluation","Delete the seed","Use the test set for tuning"],0],
    ["Why are NumPy arrays useful in ML workflows?",["They support efficient numerical operations","They automatically choose the best model","They replace validation","They remove missing values automatically"],0]
  ],
  "Python|Pandas for Data Analysis":[
    ["Which Pandas object is used for labeled tabular data?",["DataFrame","ndarray only","Queue","Graph"],0],
    ["Which method groups rows for aggregation?",["groupby()","compile()","render()","socket()"],0],
    ["Which issue should be inspected before imputing missing values?",["The missingness pattern","The UI theme","The Git branch name","The API port"],0],
    ["Which operation combines tables using matching keys?",["merge()","print()","append CSS","route()"],0],
    ["Why validate row counts after a merge?",["To detect unintended duplication or row loss","To improve chart colors","To train the model automatically","To avoid SQL"],0]
  ],
  "Statistics|Hypothesis Testing":[
    ["What does a p-value help quantify in a hypothesis test?",["Evidence against the null under the test assumptions","Model deployment cost","Database size","Chart resolution"],0],
    ["What is the null hypothesis?",["A baseline claim tested against the data","The final model","A missing value","A visualization"],0],
    ["Why choose a significance threshold before testing?",["To define a decision rule before seeing the result","To guarantee causality","To maximize accuracy","To remove sampling variability"],0],
    ["What can happen if many hypotheses are tested without adjustment?",["False positives can increase","All models become unbiased","Missing values disappear","Variance becomes zero"],0],
    ["What should accompany a statistical significance claim?",["Effect size and context","Only a screenshot","Only the p-value","Only the dataset name"],0]
  ],
  "Statistics|Correlation & Covariance":[
    ["What does correlation primarily measure?",["Strength and direction of linear association","Causality","Database normalization","Model deployment"],0],
    ["Why can correlation be misleading?",["It does not establish causation and can miss nonlinear relationships","It always equals zero","It requires no data","It removes outliers automatically"],0],
    ["What is covariance sensitive to?",["The scale of the variables","HTML structure","API latency","Git history"],0],
    ["What value indicates no linear correlation in Pearson correlation?",["0","1","100","-10"],0],
    ["What should you inspect alongside a correlation coefficient?",["A scatter plot and domain context","Only the file name","Only the model name","Only the chart color"],0]
  ],
  "SQL|Window Functions":[
    ["What does PARTITION BY do in a window function?",["Defines groups over which the window calculation is evaluated","Deletes rows","Creates a database","Sorts the entire table permanently"],0],
    ["Why use ROW_NUMBER()?",["To assign an ordered row number within a window","To create a chart","To authenticate a user","To train a model"],0],
    ["Which task is a common window-function use case?",["Top-N within each group","Changing CSS","Reading an image","Compiling C++"],0],
    ["Do window functions normally collapse rows like GROUP BY?",["No, they preserve row-level detail","Yes, always","Only in Python","Only in HTML"],0],
    ["What usually controls ordering inside a window?",["ORDER BY","WHERE only","FROM only","JOIN only"],0]
  ],
  "Data Science|EDA":[
    ["What is the primary purpose of EDA?",["Understand structure, patterns and anomalies before modeling","Deploy the final API","Choose a UI font","Encrypt the database"],0],
    ["Which check is useful early in EDA?",["Shape, data types and missingness","Only model accuracy","Only final salary","Only source code length"],0],
    ["Why inspect distributions?",["To understand scale, skew and unusual values","To guarantee causality","To remove the target","To avoid validation"],0],
    ["What is a useful EDA output?",["A set of evidence-backed hypotheses and data-quality findings","A production certificate","A Git password","A CSS bundle"],0],
    ["Why should EDA not be treated as proof of causality?",["Observed patterns can be confounded or non-causal","Charts always lie","Statistics cannot be used","Data has no structure"],0]
  ],
  "Data Science|Data Leakage":[
    ["What is data leakage?",["Information that improperly crosses the training/evaluation boundary","A slow API","A missing CSS rule","A duplicate Git commit"],0],
    ["When should a scaler generally be fit?",["On training data only","On the full dataset before splitting","On the test labels","On production logs"],0],
    ["Why can leakage make validation look too good?",["The model receives information it should not have at evaluation time","It increases image resolution","It deletes rows","It changes the browser"],0],
    ["Which tool helps keep preprocessing inside the training workflow?",["A scikit-learn Pipeline","A CSS file","A Git branch","A JSON viewer"],0],
    ["Should the held-out test set be used repeatedly for feature selection?",["No, it should remain an unbiased final check","Yes, always","Only for UI testing","Only after deployment"],0]
  ],
  "Pandas|GroupBy & Aggregation":[
    ["What does groupby primarily do?",["Split data into groups for analysis","Train a neural network","Render a page","Create a socket"],0],
    ["Which operation commonly follows groupby?",["Aggregation","Authentication","Compilation","Routing"],0],
    ["Why should the grouping key be validated?",["It defines the analytical grain of the result","It changes the browser","It trains the model","It removes outliers"],0],
    ["What is a common aggregation?",["mean","render","compile","push"],0],
    ["What should you inspect after aggregation?",["Row count, keys and resulting values","Only page color","Only API port","Only Git branch"],0]
  ],
  "NumPy|Arrays & Vectorization":[
    ["What is vectorization?",["Applying an operation to arrays without an explicit Python loop for each element","Sorting a database","Rendering HTML","Calling an API"],0],
    ["Why does array shape matter?",["It determines which operations are compatible","It sets the chart color","It controls Git history","It defines HTTP headers"],0],
    ["Which operation changes an array's shape without changing its values?",["reshape","merge","join","groupby"],0],
    ["What is a common NumPy advantage?",["Efficient numerical operations on arrays","Automatic causal inference","Automatic data cleaning","Automatic deployment"],0],
    ["What should be checked before broadcasting?",["Dimension compatibility","CSS specificity","Database permissions","API authentication"],0]
  ],
  "Data Visualization|Matplotlib":[
    ["Which chart is useful for inspecting a continuous distribution?",["Histogram","Stack trace","ER diagram","Git graph"],0],
    ["Why label axes and units?",["To make the visual interpretable","To improve model accuracy automatically","To remove missing values","To create a database"],0],
    ["What is a good practice for analytical charts?",["Use scales and encodings that support the intended comparison","Hide units","Use random colors only","Remove titles"],0],
    ["Which plot is useful for two numerical variables?",["Scatter plot","Pie chart only","Network packet","Directory tree"],0],
    ["What should a visualization communicate?",["A clear analytical comparison or pattern","Only decoration","Only the dataset name","Only code length"],0]
  ]
};

function getTopicQuestions(subject,topic){
  const override=DATA_SCIENCE_TOPIC_QUESTIONS[`${subject}|${topic}`];
  if(override?.length) return override.map((x,i)=>({id:`${subject}-${topic}-${i}`,question:x[0],options:x[1],correct:x[1][x[2]]}));
  const specific={
    "DSA|Arrays & Strings":[
      ["What is the typical random-access time for an array element when its index is known?",["O(1)","O(log n)","O(n)","O(n²)"],0],
      ["Which pattern is commonly useful for finding a pair in a sorted array?",["Two pointers","Random restart","Full recursion only","Heap sort only"],0],
      ["What is a common reason to use a sliding window?",["Maintain a moving contiguous range","Sort every element repeatedly","Remove all indexing","Guarantee O(1) memory"],0],
      ["Which operation can make repeated membership checks faster than scanning a list in many cases?",["Hashing","Printing","Recursion","Formatting"],0],
      ["What should you clarify first in an array problem?",["Constraints and required output","Variable names only","Font size","Editor theme"],0]
    ],
    "DSA|Hashing":[
      ["What is the average-case lookup complexity often associated with a well-designed hash table?",["O(1)","O(n²)","O(log n)","O(n!)"],0],
      ["What is a collision?",["Two keys mapping to the same bucket","A syntax error","An empty table","A sorted array"],0],
      ["Which task is a common use of a frequency map?",["Counting occurrences","Rendering UI","Compiling Java","Drawing graphs"],0],
      ["Why can hashing require extra memory?",["The table stores key/value or bucket state","It always duplicates the CPU","It disables caching","It removes all variables"],0],
      ["What should be considered when designing a hash-based solution?",["Collision behavior and constraints","Only the variable names","Only screen resolution","Only code indentation"],0]
    ],
    "SQL|Joins":[
      ["Which join keeps all rows from the left table and matching rows from the right?",["LEFT JOIN","INNER JOIN","CROSS JOIN only","SELF JOIN only"],0],
      ["What is a common cause of unexpectedly duplicated rows after a join?",["A one-to-many or many-to-many match","Using SELECT","Using a semicolon","Using uppercase SQL"],0],
      ["What normally connects related rows in a relational join?",["A join condition based on related columns","The browser URL","CSS classes","Random numbers"],0],
      ["Which join returns only matching rows from both sides?",["INNER JOIN","LEFT JOIN","FULL JOIN","CROSS JOIN"],0],
      ["What should you inspect when a join returns too many rows?",["Join keys and relationship cardinality","Monitor brightness","File extension","Keyboard layout"],0]
    ],
    "Machine Learning|Classification":[
      ["What type of target is classification designed to predict?",["A discrete class","Only a continuous temperature","A file size","A database index"],0],
      ["Which metric is especially useful when false negatives are costly?",["Recall","Only training loss","File count","Latency alone"],0],
      ["What does a confusion matrix summarize?",["Predicted versus actual class outcomes","CPU temperature","Database storage","Network packets only"],0],
      ["Why can accuracy be misleading on imbalanced data?",["A majority class can dominate the metric","Accuracy cannot be calculated","It always equals recall","It ignores labels"],0],
      ["What is data leakage?",["Information unavailable at prediction time entering training/evaluation","Deleting the dataset","Using Python","Saving a model"],0]
    ]
  };
  const key=`${subject}|${topic}`;
  const bank=specific[key]||GENERIC_TOPIC_QUESTIONS.map(x=>[x.prompt,x.options,x.correct]);
  return bank.map((x,i)=>({id:`${subject}-${topic}-${i}`,question:x[0],options:x[1],correct:x[1][x[2]]}));
}

function StudentLearningHub(){
  const navigate=useNavigate();
  const roadmap=readS("forge_student_roadmap",null);
  const subjects=readS("forge_student_subjects",[]);
  const learningRole=readS("forge_student_profile",{})?.targetRole||roadmap?.role||"";
  const isDataScientistLearning=learningRole==="Data Scientist";
  const [selectedSubject,setSelectedSubject]=useState(()=>roadmap?.subjects?.[0]?.subject||subjects[0]||"");
  const subjectPlan=roadmap?.subjects?.find(x=>x.subject===selectedSubject);
  const topics=subjectPlan?.topics||[];
  const [selectedTopic,setSelectedTopic]=useState(()=>topics[0]||"");
  const [tab,setTab]=useState("learn");
  const [answers,setAnswers]=useState({});
  const [submitted,setSubmitted]=useState(false);
  const [resourceDone,setResourceDone]=useState(()=>readS("forge_student_resources_done",{}));
  const [topicProgress,setTopicProgress]=useState(()=>readS("forge_student_topic_progress",{}));
  const [notesArchive,setNotesArchive]=useState(()=>readS("forge_student_notes_daily",{}));
  const [notes,setNotes]=useState("");
  const [selectedRevision,setSelectedRevision]=useState(null);

  const pad=n=>String(n).padStart(2,"0");
  const todayKey=(()=>{const d=new Date();return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`})();
  const noteKey=`${todayKey}::${selectedSubject}::${selectedTopic}`;

  useEffect(()=>{if(topics.length&&!topics.includes(selectedTopic))setSelectedTopic(topics[0]||"")},[selectedSubject,topics,selectedTopic]);
  useEffect(()=>{setAnswers({});setSubmitted(false);setTab("learn");setSelectedRevision(null)},[selectedSubject,selectedTopic]);
  useEffect(()=>{sessionStorage.setItem("forge_student_resources_done",JSON.stringify(resourceDone))},[resourceDone]);
  useEffect(()=>{sessionStorage.setItem("forge_student_topic_progress",JSON.stringify(topicProgress))},[topicProgress]);
  useEffect(()=>{sessionStorage.setItem("forge_student_notes_daily",JSON.stringify(notesArchive))},[notesArchive]);
  useEffect(()=>{
    setNotes(notesArchive[noteKey]?.text||"");
  },[noteKey]);

  const data=getLearningData(selectedSubject,selectedTopic);
  const videos=getTopicVideos(selectedSubject,selectedTopic);
  const questions=getTopicQuestions(selectedSubject,selectedTopic);
  const score=submitted?questions.reduce((n,q,i)=>n+(answers[i]===q.correct?1:0),0):0;
  const pct=submitted?Math.round(score/questions.length*100):0;
  const progressKey=`${selectedSubject}::${selectedTopic}`;
  const currentStatus=topicProgress[progressKey]||"Not started";
  const setStatus=status=>setTopicProgress(v=>({...v,[progressKey]:status}));
  const masteryLabel=submitted?(pct>=80?"Demonstrated":pct>=60?"Developing":"Needs Practice"):currentStatus;
  const markLearned=()=>setStatus("Learned");
  const submitQuiz=()=>{setSubmitted(true);setStatus(pct>=80?"Demonstrated":"Developing")};

  const saveNotes=(value)=>{
    setNotes(value);
    setNotesArchive(prev=>({
      ...prev,
      [noteKey]:{
        date:todayKey,
        subject:selectedSubject,
        topic:selectedTopic,
        text:value,
        updatedAt:new Date().toISOString()
      }
    }));
  };

  const revisionEntries=Object.values(notesArchive)
    .filter(x=>x?.text?.trim())
    .sort((a,b)=>String(b.updatedAt||b.date).localeCompare(String(a.updatedAt||a.date)));

  if(!roadmap?.subjects?.length){
    return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell"><div className="student-step-eyebrow"><span/>LEARNING HUB</div><h1 className="student-title">{isDataScientistLearning?<>Build Data Science skills<br/><em>through evidence.</em></>:<>Build the skill<br/><em>through evidence.</em></>}</h1><p className="student-description">Complete your roadmap first so FORGE can prioritize the subjects and topics you should learn.</p><button className="student-continue" onClick={()=>navigate("/student/roadmap")}>Back to Roadmap <ChevronLeft size={15}/></button></div></main></>;
  }

  return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell">
    <div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/planner")}><ChevronLeft size={15}/>Back</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">LEARNING HUB</div></div>
    <div className="student-progress"><span style={{width:"100%"}}/></div>
    <div className="student-step-eyebrow"><span/>LEARNING + PRACTICE</div>
    <h1 className="student-title">Turn priorities<br/><em>into capability.</em></h1>
    <p className="student-description">Choose a roadmap subject and topic. FORGE gives you two learning options, keeps full-course / playlist videos inside the page, and automatically stores your short notes day-wise for revision.</p>

    <div className="assessment-result" style={{marginTop:25}}>
      <div className="learning-control-grid" style={{display:"grid",gridTemplateColumns:"minmax(180px,.75fr) minmax(0,1.25fr)",gap:16}}>
        <div>
          <small style={{display:"block",color:"rgba(255,255,255,.35)",fontSize:9,fontWeight:800,letterSpacing:".12em",marginBottom:9}}>SUBJECT</small>
          <div className="learning-subject-list" style={{display:"grid",gap:7}}>{roadmap.subjects.map(s=><button key={s.subject} onClick={()=>setSelectedSubject(s.subject)} className={`student-option ${selectedSubject===s.subject?"selected":""}`} style={{textAlign:"left"}}><span style={{fontWeight:800}}>{s.rank}. {s.subject}</span><span style={{display:"block",marginTop:4,fontSize:9,opacity:.65}}>{s.dailyHours?`${Number(s.dailyHours.toFixed(1))}h/day`:`${Math.round((s.weeklyHours||0)/7*10)/10}h/day`} · {s.status}</span></button>)}</div>
        </div>
        <div>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,flexWrap:"wrap"}}><div><small style={{display:"block",color:"rgba(255,255,255,.35)",fontSize:9,fontWeight:800,letterSpacing:".12em"}}>TOPIC</small><strong style={{display:"block",fontSize:20,marginTop:7}}>{selectedTopic}</strong></div><span className="assessment-type-badge">{masteryLabel}</span></div>
          <div className="learning-topic-list" style={{display:"flex",gap:8,flexWrap:"wrap",marginTop:16}}>{topics.map(t=><button key={t} className={`student-option ${selectedTopic===t?"selected":""}`} onClick={()=>setSelectedTopic(t)}>{t}</button>)}</div>
          <div className="generated-task" style={{marginTop:18}}><small>TOPIC STATUS</small><p style={{marginBottom:0}}>{currentStatus}. Learn from either video, write your own short notes, then prove understanding with five questions.</p></div>
        </div>
      </div>

      <div className="learning-tabs" style={{display:"flex",gap:8,marginTop:24,borderBottom:"1px solid rgba(255,255,255,.08)",paddingBottom:9,flexWrap:"wrap"}}>
        {[['learn','Learn',BookOpen],['resources','Resources',ExternalLink],['practice','5 Questions',Trophy],['notes','My Notes',BookOpen]].map(([id,label,Icon])=><button key={id} onClick={()=>setTab(id)} className={`student-option ${tab===id?"selected":""}`} style={{display:"inline-flex",alignItems:"center",gap:7}}><Icon size={13}/>{label}</button>)}
      </div>

      {tab==="learn"&&<div style={{marginTop:22}}>
        <div className="assessment-card learning-overview-card">
          <div className="assessment-type-badge">CONCEPT MAP · {selectedSubject}</div>
          <h2>{selectedTopic}</h2>
          <p style={{color:"rgba(255,255,255,.52)",lineHeight:1.75,fontSize:13,marginTop:14}}>{data.summary}</p>
          <div className="learning-key-points" style={{display:"grid",gap:9,marginTop:20}}>{data.keyPoints.map((point,i)=><div key={i} className="assessment-breakdown-card"><strong>0{i+1}</strong><small>{point}</small></div>)}</div>
        </div>

        <div style={{display:"grid",gridTemplateColumns:"minmax(0,1.55fr) minmax(330px,.75fr)",gap:18,alignItems:"start",marginTop:14}}>
          <div style={{display:"grid",gap:14}}>
            {videos.map((video,index)=>{
              const embed=getYoutubeEmbedUrl(video);
              const searchUrl=video.kind==="search"?`https://www.youtube.com/results?search_query=${encodeURIComponent(video.query)}`:"";
              return <div key={`${video.kind}-${video.id||video.query}-${index}`} className="assessment-card" style={{padding:18}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,marginBottom:13,flexWrap:"wrap"}}>
                  <div><div className="assessment-type-badge" style={{marginBottom:7}}>{getVideoLabel(video)}</div><h3 style={{margin:0,fontSize:18,letterSpacing:"-.025em"}}>{video.title}</h3><div style={{marginTop:5,color:"rgba(255,255,255,.38)",fontSize:10}}>{video.source}</div></div>
                  <span style={{color:"rgba(255,255,255,.38)",fontSize:9,fontWeight:800,letterSpacing:".1em"}}>OPTION {index+1}</span>
                </div>
                {embed?<div style={{position:"relative",width:"100%",paddingTop:"56.25%",overflow:"hidden",borderRadius:14,background:"#000",border:"1px solid rgba(255,255,255,.08)"}}><iframe title={`${selectedTopic} ${video.title}`} src={embed} style={{position:"absolute",inset:0,width:"100%",height:"100%",border:0}} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen loading="lazy"/></div>:<div className="generated-task"><small>VIDEO EMBED NOT AVAILABLE FOR THIS SUBJECT YET</small><p style={{marginBottom:10}}>Use this curated YouTube search to choose a complete course for this exact topic.</p><a href={searchUrl} target="_blank" rel="noreferrer" className="student-continue" style={{textDecoration:"none",display:"inline-flex"}}>Open course results <ExternalLink size={13}/></a></div>}
              </div>;
            })}
          </div>

          <aside className="learning-notes-aside" style={{position:"sticky",top:18}}>
            <div className="assessment-card learning-notebook" style={{padding:20}}>
              <div className="assessment-type-badge" style={{marginBottom:8}}>SHORT NOTES · AUTO-SAVED</div>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:10}}><div><h3 style={{margin:0,fontSize:19}}>My notes</h3><p style={{margin:"6px 0 0",fontSize:10,color:"rgba(255,255,255,.38)"}}>{selectedSubject} · {selectedTopic}</p></div><span style={{fontSize:9,fontWeight:800,color:"rgba(255,255,255,.4)",whiteSpace:"nowrap"}}>{todayKey}</span></div>
              <textarea value={notes} onChange={e=>saveNotes(e.target.value)} placeholder="Write your own short notes here...\n\n• key idea\n• formula / syntax\n• example\n• mistake to avoid\n• interview point" style={{width:"100%",minHeight:390,marginTop:16,resize:"vertical",boxSizing:"border-box",background:"rgba(255,255,255,.035)",border:"1px solid rgba(255,255,255,.1)",borderRadius:12,padding:15,color:"#fff",outline:"none",fontFamily:"inherit",fontSize:12,lineHeight:1.7}}/>
              <div style={{marginTop:9,display:"flex",justifyContent:"space-between",gap:8,alignItems:"center"}}><span style={{fontSize:9,color:"rgba(255,255,255,.32)"}}>Saved automatically while you type.</span><span style={{fontSize:9,color:"rgba(255,255,255,.48)",fontWeight:800}}>{notes.length} chars</span></div>
              <button className="student-option" onClick={()=>setTab("notes")} style={{width:"100%",marginTop:12}}>Open revision archive</button>
            </div>
          </aside>
        </div>

        <div className="student-bottom"><div className="student-validation"><strong>Learning step.</strong> Use either video, keep your notes, then mark the topic learned.</div><button className="student-continue" onClick={markLearned}>Mark Learned <Check size={14}/></button></div>
      </div>}

      {tab==="notes"&&<div style={{display:"grid",gridTemplateColumns:"minmax(330px,.8fr) minmax(0,1.2fr)",gap:16,marginTop:22,alignItems:"start"}}>
        <div className="assessment-card" style={{padding:20}}><div className="assessment-type-badge">CURRENT NOTE</div><h2 style={{fontSize:22,marginBottom:5}}>{selectedTopic}</h2><p style={{fontSize:10,color:"rgba(255,255,255,.38)"}}>{selectedSubject} · {todayKey}</p><textarea value={notes} onChange={e=>saveNotes(e.target.value)} placeholder="Write short revision notes..." style={{width:"100%",minHeight:480,marginTop:16,resize:"vertical",boxSizing:"border-box",background:"rgba(255,255,255,.035)",border:"1px solid rgba(255,255,255,.1)",borderRadius:12,padding:15,color:"#fff",outline:"none",fontFamily:"inherit",fontSize:12,lineHeight:1.7}}/><p style={{fontSize:9,color:"rgba(255,255,255,.32)",marginBottom:0}}>Auto-saved to this day's revision archive.</p></div>
        <div className="assessment-card" style={{padding:20}}><div className="assessment-type-badge">REVISION ARCHIVE · DAY-WISE</div><h2 style={{fontSize:22}}>Your saved notes</h2><p style={{fontSize:11,color:"rgba(255,255,255,.4)",lineHeight:1.6}}>Every note is stored with the day, subject and topic so you can return later and revise exactly what you studied.</p>
          {revisionEntries.length===0?<div className="generated-task"><small>NO SAVED NOTES YET</small><p style={{marginBottom:0}}>Start writing in the notes box and FORGE will create the revision entry automatically.</p></div>:<div style={{display:"grid",gap:9,marginTop:15,maxHeight:620,overflowY:"auto"}}>{revisionEntries.map((entry,i)=><button key={`${entry.date}-${entry.subject}-${entry.topic}-${i}`} onClick={()=>setSelectedRevision(entry)} className="assessment-breakdown-card" style={{textAlign:"left",border:"1px solid rgba(255,255,255,.08)",cursor:"pointer"}}><div style={{display:"flex",justifyContent:"space-between",gap:10}}><strong>{entry.topic}</strong><span style={{fontSize:9,color:"rgba(255,255,255,.35)"}}>{entry.date}</span></div><small>{entry.subject} · {entry.text.slice(0,150)}{entry.text.length>150?"…":""}</small></button>)}</div>}
          {selectedRevision&&<div className="generated-task" style={{marginTop:14}}><small>REVISION PREVIEW · {selectedRevision.date}</small><strong style={{display:"block",marginTop:7}}>{selectedRevision.subject} · {selectedRevision.topic}</strong><p style={{whiteSpace:"pre-wrap",lineHeight:1.7,maxHeight:280,overflowY:"auto"}}>{selectedRevision.text}</p><button className="student-option" onClick={()=>setSelectedRevision(null)}>Close preview</button></div>}
        </div>
      </div>}

      {tab==="resources"&&<div style={{display:"grid",gap:10,marginTop:22}}>{data.resources.filter(r=>r.type!=="Video").map(r=>{const key=`${progressKey}::${r.title}`;return <div key={r.title} className="assessment-breakdown-card" style={{display:"grid",gridTemplateColumns:"1fr auto",gap:12,alignItems:"center"}}><div><strong>{r.title}</strong><small>{r.type} · curated starting point</small></div><div style={{display:"flex",gap:8}}><button className="student-option" onClick={()=>setResourceDone(v=>({...v,[key]:!v[key]}))}>{resourceDone[key]?"Completed":"Mark done"}</button><a href={r.url} target="_blank" rel="noreferrer" className="student-option" style={{textDecoration:"none",display:"inline-flex",alignItems:"center",gap:6}}>Open <ExternalLink size={12}/></a></div></div>})}<div className="generated-task"><small>VIDEO OPTIONS</small><p style={{marginBottom:0}}>Two complete-course / playlist alternatives for the selected topic are available in the Learn tab.</p></div></div>}

      {tab==="practice"&&<div style={{marginTop:22}}>{!submitted?<><div className="assessment-card"><div className="assessment-type-badge">PRACTICE · 5 QUESTIONS</div><h2>Prove your understanding.</h2><div className="assessment-options">{questions.map((q,i)=><div key={q.id} style={{paddingBottom:18,marginBottom:18,borderBottom:i<questions.length-1?"1px solid rgba(255,255,255,.08)":"none"}}><strong style={{display:"block",fontSize:13,lineHeight:1.5}}>{i+1}. {q.question}</strong><div style={{display:"grid",gap:7,marginTop:10}}>{q.options.map((opt,j)=><button key={opt} className={`assessment-option ${answers[i]===opt?"selected":""}`} onClick={()=>setAnswers(v=>({...v,[i]:opt}))}><span className="assessment-option-key">{String.fromCharCode(65+j)}</span><span>{opt}</span></button>)}</div></div>)}</div></div><div className="student-bottom"><div className="student-validation"><strong>{Object.keys(answers).length}/{questions.length} answered.</strong> Submit only when all five are answered.</div><button className="student-continue" disabled={Object.keys(answers).length!==questions.length} onClick={submitQuiz}>Submit Practice <Check size={14}/></button></div></>:<div className="assessment-result"><div className="assessment-result-score">{pct}<span> / 100</span></div><p className="student-description">{score}/{questions.length} answers correct for <strong>{selectedTopic}</strong>.</p><div className="generated-task"><small>EVIDENCE STATE</small><p style={{marginBottom:0}}>{pct>=80?"Demonstrated capability: your submitted answers met the current practice threshold.":pct>=60?"Developing capability: repeat the topic and practice to strengthen evidence.":"Insufficient evidence: revisit the concept and retry the practice."}</p></div><div className="student-bottom"><div className="student-validation"><strong>Evidence recorded.</strong> You can retry the topic after reviewing your mistakes.</div><button className="student-continue" onClick={()=>{setAnswers({});setSubmitted(false);setStatus("Practicing")}}>Retry <RotateCcw size={14}/></button></div></div>}</div>}

    <div className="learning-next-card" style={{marginTop:24,padding:22,border:"1px solid rgba(255,255,255,.09)",borderRadius:18,background:"linear-gradient(135deg,rgba(255,255,255,.055),rgba(255,255,255,.018))",display:"flex",justifyContent:"space-between",alignItems:"center",gap:18,flexWrap:"wrap"}}>
      <div>
        <div className="assessment-type-badge" style={{marginBottom:8}}>NEXT · INDUSTRY PULSE</div>
        <h2 style={{margin:0,fontSize:22,letterSpacing:"-.03em"}}>See what your role may need next.</h2>
        <p style={{margin:"8px 0 0",fontSize:11,lineHeight:1.6,color:"rgba(255,255,255,.4)",maxWidth:650}}>Explore current industry demand, newly emerging topics, 5-year capability signals and longer-horizon scenarios for your target role.</p>
      </div>
      <button className="student-continue" onClick={()=>navigate("/student/industry")}>Open Industry Pulse <ArrowRight size={15}/></button>
    </div>

    </div>
  </div></main></>;
}

function StudentPlanner(){
  const navigate=useNavigate();
  const roadmap=readS("forge_student_roadmap",null);
  const [completed,setCompleted]=useState(()=>readS("forge_student_planner_completed",{}));
  const [rescheduled,setRescheduled]=useState(()=>readS("forge_student_planner_rescheduled",{}));

  const pad=n=>String(n).padStart(2,"0");
  const dateKey=d=>`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const addDays=(d,n)=>{const x=new Date(d);x.setDate(x.getDate()+n);return x;};
  const dayLabel=d=>d.toLocaleDateString(undefined,{weekday:"short"});
  const fullDate=d=>d.toLocaleDateString(undefined,{day:"numeric",month:"short"});

  const plan=useMemo(()=>{
    if(!roadmap?.subjects?.length)return [];
    const start=new Date();
    start.setHours(0,0,0,0);
    const days=Array.from({length:7},(_,i)=>({date:addDays(start,i),hours:0,tasks:[]}));

    roadmap.subjects.forEach((subject,index)=>{
      let remaining=Math.max(.5,Number(subject.weeklyHours)||.5);
      let topicIndex=0;
      while(remaining>0){
        const chunk=remaining>=1?1:.5;
        const target=days.reduce((best,d)=>d.hours<best.hours?d:best,days[0]);
        const topics=subject.topics||[`${subject.subject} Fundamentals`,`${subject.subject} Practice`];
        const topic=topics[topicIndex%topics.length];
        const taskType=(topicIndex+index)%3===0?"Learn":(topicIndex+index)%3===1?"Practice":"Review";
        target.tasks.push({
          id:`${dateKey(target.date)}-${subject.subject}-${topicIndex}-${index}`,
          subject:subject.subject,
          topic,
          type:taskType,
          hours:chunk
        });
        target.hours+=chunk;
        remaining-=chunk;
        topicIndex++;
      }
    });

    return days.map(day=>({...day,key:dateKey(day.date),tasks:day.tasks.sort((a,b)=>a.subject.localeCompare(b.subject))}));
  },[roadmap]);

  useEffect(()=>{
    sessionStorage.setItem("forge_student_planner_completed",JSON.stringify(completed));
  },[completed]);
  useEffect(()=>{
    sessionStorage.setItem("forge_student_planner_rescheduled",JSON.stringify(rescheduled));
  },[rescheduled]);

  if(!roadmap?.subjects?.length){
    return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell">
      <div className="student-step-eyebrow"><span/>08 / DAILY EXECUTION PLAN</div>
      <h1 className="student-title">Build the planner<br/><em>from evidence.</em></h1>
      <p className="student-description">A roadmap is required before FORGE can generate your weekly execution plan.</p>
      <button className="student-continue" onClick={()=>navigate("/student/roadmap")}>Back to Roadmap <ChevronLeft size={15}/></button>
    </div></main></>;
  }

  const allTasks=plan.flatMap(day=>day.tasks);
  const completedCount=allTasks.filter(t=>completed[t.id]).length;
  const totalHours=allTasks.reduce((s,t)=>s+t.hours,0);
  const completedHours=allTasks.filter(t=>completed[t.id]).reduce((s,t)=>s+t.hours,0);
  const todayKey=dateKey(new Date());
  const today=plan.find(d=>d.key===todayKey)||plan[0];
  const todayDone=today?.tasks.filter(t=>completed[t.id]).length||0;

  let streak=0;
  for(let i=0;i<7;i++){
    const d=plan[i];
    if(!d.tasks.length)continue;
    if(d.tasks.every(t=>completed[t.id]))streak++;
    else if(i<6)break;
  }

  const toggleTask=id=>setCompleted(v=>({...v,[id]:!v[id]}));

  const rescheduleMissed=()=>{
    const todayIndex=plan.findIndex(d=>d.key===todayKey);
    if(todayIndex<0)return;
    const missed=plan.slice(0,todayIndex).flatMap(d=>d.tasks.filter(t=>!completed[t.id]));
    if(!missed.length)return;
    const nextDays=plan.slice(todayIndex).filter(d=>d.key!==todayKey);
    const additions={};
    missed.forEach((task,i)=>{
      if(!nextDays.length)return;
      const target=nextDays[i%nextDays.length];
      const copy={...task,id:`${target.key}-rescheduled-${task.id}`};
      additions[copy.id]=task.id;
      setCompleted(v=>({...v,[copy.id]:v[task.id]||false}));
    });
    setRescheduled(v=>({...v,...additions}));
  };

  return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell">
    <div className="student-topbar">
      <button className="student-back" onClick={()=>navigate("/student/roadmap")}><ChevronLeft size={15}/>Back</button>
      <div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div>
      <div className="student-progress-label">08 / 08</div>
    </div>
    <div className="student-progress"><span style={{width:"100%"}}/></div>

    <div className="student-step-eyebrow"><span/>08 / DAILY EXECUTION PLAN</div>
    <h1 className="student-title">Turn the roadmap<br/><em>into execution.</em></h1>
    <p className="student-description">FORGE turns your daily study capacity into a balanced 7-day execution plan. Every subject gets a visible daily allocation, then the planner breaks it into focused actions.</p>

    <div className="assessment-result" style={{marginTop:25}}>
      <div className="assessment-breakdown" style={{gridTemplateColumns:"repeat(4,minmax(0,1fr))"}}>
        <div className="assessment-breakdown-card"><strong>{Math.round(totalHours*10)/10}h</strong><small>7-DAY TOTAL</small></div>
        <div className="assessment-breakdown-card"><strong>{Math.round(completedHours*10)/10}h</strong><small>Completed</small></div>
        <div className="assessment-breakdown-card"><strong>{completedCount}/{allTasks.length}</strong><small>Tasks complete</small></div>
        <div className="assessment-breakdown-card"><strong>{streak} day{streak===1?"":"s"}</strong><small>Current streak</small></div>
      </div>

      <div style={{marginTop:20,height:7,borderRadius:99,background:"rgba(255,255,255,.08)",overflow:"hidden"}}>
        <span style={{display:"block",height:"100%",width:`${allTasks.length?(completedCount/allTasks.length)*100:0}%`,background:"#fff",transition:"width .3s ease"}} />
      </div>

      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,marginTop:22,flexWrap:"wrap"}}>
        <div>
          <small style={{color:"rgba(255,255,255,.35)",fontSize:9,fontWeight:800,letterSpacing:".12em"}}>TODAY</small>
          <div style={{fontSize:18,fontWeight:700,marginTop:5}}>{today?.tasks.length||0} tasks · {today?.tasks.reduce((s,t)=>s+t.hours,0)||0}h</div>
        </div>
        <button className="student-continue" onClick={rescheduleMissed} disabled={!plan.some((d,i)=>i<plan.findIndex(x=>x.key===todayKey)&&d.tasks.some(t=>!completed[t.id]))}>Reschedule Missed <RotateCcw size={14}/></button>
      </div>

      <div style={{display:"grid",gap:14,marginTop:24}}>
        {plan.map((day,index)=><div key={day.key} style={{border:"1px solid rgba(255,255,255,.09)",borderRadius:16,background:index===0?"rgba(255,255,255,.055)":"rgba(255,255,255,.022)",overflow:"hidden"}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,padding:"15px 16px",borderBottom:"1px solid rgba(255,255,255,.07)"}}>
            <div><strong style={{fontSize:13}}>{dayLabel(day.date)}</strong><small style={{display:"block",marginTop:4,color:"rgba(255,255,255,.35)",fontSize:9}}>{fullDate(day.date)}{day.key===todayKey?" · TODAY":""}</small></div>
            <span className="planner-day-hours">{day.hours>=1?`${Number(day.hours.toFixed(1))}h`:`${Math.round(day.hours*60)}m`} today</span>
          </div>
          <div style={{display:"grid",gap:8,padding:12}}>
            {!day.tasks.length&&<div style={{padding:12,color:"rgba(255,255,255,.35)",fontSize:10}}>No task allocated.</div>}
            {day.tasks.map(task=><button key={task.id} onClick={()=>toggleTask(task.id)} style={{display:"grid",gridTemplateColumns:"30px 1fr auto",alignItems:"center",gap:11,textAlign:"left",border:"1px solid rgba(255,255,255,.07)",borderRadius:12,padding:"11px 12px",background:completed[task.id]?"rgba(255,255,255,.09)":"rgba(255,255,255,.018)",color:"#fff",cursor:"pointer",font:"inherit"}}>
              <span style={{width:24,height:24,borderRadius:7,border:"1px solid rgba(255,255,255,.16)",display:"grid",placeItems:"center",background:completed[task.id]?"#fff":"transparent",color:completed[task.id]?"#070807":"rgba(255,255,255,.35)"}}>{completed[task.id]?<Check size={14}/>:null}</span>
              <span><strong style={{display:"block",fontSize:11,textDecoration:completed[task.id]?"line-through":"none",opacity:completed[task.id]?.55:1}}>{task.topic}</strong><small style={{display:"block",marginTop:4,color:"rgba(255,255,255,.38)",fontSize:9}}>{task.subject} · {task.type}</small></span>
              <span style={{fontSize:9,color:"rgba(255,255,255,.4)",fontWeight:800}}>{task.hours}h</span>
            </button>)}
          </div>
        </div>)}
      </div>

      <div className="student-bottom">
        <div className="student-validation"><strong>{todayDone}/{today?.tasks.length||0} today.</strong> Keep completing tasks to build your evidence trail.</div>
        <div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button className="student-option" onClick={()=>navigate("/student/progress")}>View Progress</button><button className="student-continue" onClick={()=>navigate("/student/learning")}>Open Learning Hub <ArrowRight size={15}/></button></div>
      </div>
    </div>
  </div></main></>;
}


function StudentProgress(){
  const navigate=useNavigate();
  const scores=readS("forge_student_scores",null);
  const roadmap=readS("forge_student_roadmap",null);
  const planner=readS("forge_student_planner_completed",{});
  const topicProgress=readS("forge_student_topic_progress",{});
  const notes=readS("forge_student_revision_notes",{});
  const profile=readS("forge_student_profile",{});
  const subjects=readS("forge_student_subjects",[]);

  const completedTasks=Object.values(planner||{}).filter(Boolean).length;
  const totalTopics=Object.keys(topicProgress||{}).length;
  const demonstratedTopics=Object.values(topicProgress||{}).filter(v=>Number(v?.score||0)>=80).length;
  const noteCount=Object.values(notes||{}).filter(v=>v&&String(v.text||v).trim()).length;
  const overall=Number(scores?.overallScore ?? scores?.score ?? 0);
  const roadmapSubjects=roadmap?.subjects||[];
  const readiness=overall>=80?"Strong baseline":overall>=60?"Developing baseline":"Priority-building phase";

  const capabilityRows=useMemo(()=>{
    const source=scores?.subjectScores||scores?.subjects||{};
    return subjects.map(subject=>{
      const item=source[subject]||{};
      const score=Number(item.score||0);
      const roadmapItem=roadmapSubjects.find(x=>x.subject===subject);
      return {subject,score,weeklyHours:roadmapItem?.weeklyHours||0,status:score>=80?"Strong":score>=60?"Developing":"Priority gap"};
    }).sort((a,b)=>a.score-b.score);
  },[scores,subjects,roadmapSubjects]);

  return <><StudentStyles/><main className="forge-student-page"><div className="forge-student-shell">
    <div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/learning")}><ChevronLeft size={15}/>Back</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">PROGRESS</div></div>
    <div className="student-step-eyebrow"><span/>PROGRESS · CAPABILITY EVOLUTION</div>
    <h1 className="student-title">See what you’ve<br/><em>actually built.</em></h1>
    <p className="student-description">FORGE combines your assessment baseline, roadmap execution, topic practice and revision evidence into a living student capability view. Scores come from recorded activity, not self-reported progress.</p>

    <div className="assessment-result" style={{marginTop:25}}>
      <div className="assessment-breakdown" style={{gridTemplateColumns:"repeat(4,minmax(0,1fr))"}}>
        <div className="assessment-breakdown-card"><strong>{overall}<span style={{fontSize:12}}> / 100</span></strong><small>Assessment baseline</small></div>
        <div className="assessment-breakdown-card"><strong>{completedTasks}</strong><small>Planner tasks done</small></div>
        <div className="assessment-breakdown-card"><strong>{demonstratedTopics}/{totalTopics}</strong><small>Topics demonstrated</small></div>
        <div className="assessment-breakdown-card"><strong>{noteCount}</strong><small>Revision entries</small></div>
      </div>

      <div className="generated-task" style={{marginTop:18}}><small>CURRENT CAPABILITY STATE</small><h3 style={{marginTop:8}}>{readiness}</h3><p style={{marginBottom:0}}>Target role: <strong>{profile?.targetRole||"Not set"}</strong>. FORGE updates this view as you complete practice and learning activity.</p></div>

      <div style={{display:"grid",gap:10,marginTop:18}}>
        {capabilityRows.length?capabilityRows.map((x,i)=><div key={x.subject} className="assessment-breakdown-card" style={{display:"grid",gridTemplateColumns:"1fr auto",gap:14,alignItems:"center"}}><div><strong>{i+1}. {x.subject}</strong><small>{x.status} · roadmap allocation {x.weeklyHours}h/week</small></div><div style={{textAlign:"right"}}><strong>{x.score}</strong><small>/ 100</small></div></div>):<div className="generated-task"><p style={{marginBottom:0}}>Complete the assessment to start building your capability baseline.</p></div>}
      </div>

      <div className="student-bottom"><div className="student-validation"><strong>Keep the loop moving.</strong> Learn → practice → record evidence → revisit weak areas.</div><div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button className="student-option" onClick={()=>navigate("/student/planner")}>Planner</button><button className="student-option" onClick={()=>navigate("/student/ask")}>Ask FORGE <Sparkles size={14}/></button><button className="student-continue" onClick={()=>navigate("/student/learning")}>Continue Learning <ArrowRight size={15}/></button></div></div>
    </div>
  </div></main></>;
}


function normalizeIndustryPulse(data){
  const source=data?.industry_pulse||data?.industryPulse||data?.pulse||data||{};
  const normalizeList=(value)=>Array.isArray(value)?value.map(normalizeIndustryItem).filter(x=>x.name):[];
  // Preserve backend metadata as well as the horizon arrays.
  // The previous normalizer returned only the four arrays, which silently
  // discarded data_provenance and technology_record_count. As a result the
  // Technology Evidence card displayed a dash even though the API returned
  // 31,821 O*NET records.
  const provenance=source?.data_provenance||source?.provenance||data?.data_provenance||data?.provenance||{};
  return {
    role:source?.role||data?.role||'',
    matched_occupations:Array.isArray(source?.matched_occupations)?source.matched_occupations:[],
    current:normalizeList(source.current||source.current_demand||source.currentDemand||source.in_demand||[]),
    emerging:normalizeList(source.emerging||source.emerging_topics||source.emergingTopics||[]),
    fiveYear:normalizeList(source.fiveYear||source.five_year||source.capability_radar_5_year||source.radar_5_year||[]),
    tenYear:normalizeList(source.tenYear||source.ten_year||source.capability_radar_10_year||source.radar_10_year||[]),
    data_provenance:provenance,
    provenance,
    technology_record_count:source?.technology_record_count??data?.technology_record_count??provenance?.technology_record_count??null,
    onet_technology_record_count:source?.onet_technology_record_count??data?.onet_technology_record_count??provenance?.technology_record_count??null,
    technology_evidence:source?.technology_evidence??data?.technology_evidence??provenance?.technology_evidence??null,
    horizon_context:source?.horizon_context??data?.horizon_context??{},
    market_signal:source?.market_signal??source?.daily_market??data?.market_signal??data?.daily_market??null,
    daily_market:source?.daily_market??source?.market_signal??data?.daily_market??data?.market_signal??null
  };
}

function normalizeIndustryItem(item){
  if(typeof item==='string')return {name:item};
  return {
    ...(item||{}),
    name:item?.name||item?.skill||item?.skill_name||item?.title||item?.topic||'',
    description:item?.description||item?.reason||item?.evidence||item?.signal||'',
    percentage:item?.percentage!=null?Number(item.percentage):item?.demand_percentage!=null?Number(item.demand_percentage):item?.prevalence_percent!=null?Number(item.prevalence_percent):null,
    growth:item?.growth!=null?Number(item.growth):item?.change!=null?Number(item.change):item?.growth_percentage!=null?Number(item.growth_percentage):item?.share_change_pp!=null?Number(item.share_change_pp):null,
    confidence:item?.confidence!=null?Number(item.confidence):null,
    source:item?.source||item?.source_name||''
  };
}

function normalizeIndustryResources(data){
  const raw=data?.resources||data?.learning_resources||data?.items||data||[];
  if(!Array.isArray(raw))return [];
  return raw.map(item=>{
    const kind=(item?.type||item?.kind||'').toLowerCase();
    return {
      ...(item||{}),
      type:kind.includes('pdf')?'pdf':kind.includes('doc')?'doc':kind.includes('link')?'link':'video',
      id:item?.id||item?.video_id||item?.playlist_id||'',
      url:item?.url||item?.embed_url||'',
      title:item?.title||item?.name||'',
      source:item?.source||item?.provider||''
    };
  }).filter(x=>x.url||x.id);
}

function industryVideoEmbed(video){
  if(video?.embed_url)return video.embed_url;
  if(video?.playlist_id)return `https://www.youtube-nocookie.com/embed?listType=playlist&list=${video.playlist_id}&rel=0&playsinline=1`;
  if(video?.id)return `https://www.youtube-nocookie.com/embed/${video.id}?rel=0&playsinline=1`;
  if(video?.url){
    const match=video.url.match(/(?:v=|youtu\.be\/|embed\/)([A-Za-z0-9_-]{6,})/);
    if(match)return `https://www.youtube-nocookie.com/embed/${match[1]}?rel=0&playsinline=1`;
  }
  return video?.url||'';
}

const INDUSTRY_PULSE_STYLE=`
.industry-pulse-shell{max-width:1240px!important}
.industry-hero{display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:24px;align-items:end;margin-top:16px}
.industry-role-card{padding:20px;border:1px solid rgba(255,255,255,.09);border-radius:18px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));display:grid;gap:7px}.industry-role-card small,.industry-panel-head small,.industry-detail-top small,.industry-resource-head small{font-size:9px;letter-spacing:.16em;font-weight:800;color:rgba(255,255,255,.38)}.industry-role-card strong{font-size:23px;letter-spacing:-.035em}.industry-role-card span{font-size:10px;color:rgba(255,255,255,.4);line-height:1.5}
.industry-horizon-tabs{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:28px 0 12px}.industry-horizon-tabs button{padding:14px 15px;text-align:left;border:1px solid rgba(255,255,255,.08);border-radius:13px;background:rgba(255,255,255,.025);color:#fff;cursor:pointer}.industry-horizon-tabs button.active{border-color:rgba(255,255,255,.22);background:rgba(255,255,255,.075)}.industry-horizon-tabs strong{display:block;font-size:10px;letter-spacing:.06em}.industry-horizon-tabs span{display:block;margin-top:5px;font-size:9px;color:rgba(255,255,255,.38)}
.industry-evidence-strip{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0}.industry-evidence-strip span{font-size:8px;font-weight:800;letter-spacing:.1em;padding:7px 9px;border:1px solid rgba(255,255,255,.07);border-radius:999px;color:rgba(255,255,255,.42)}
.industry-main-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(380px,.78fr);gap:14px;align-items:start}.industry-skill-panel,.industry-detail-panel{border:1px solid rgba(255,255,255,.08);border-radius:18px;background:rgba(255,255,255,.025);overflow:hidden}.industry-panel-head{padding:19px;border-bottom:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;gap:12px}.industry-panel-head h2{margin:7px 0 0;font-size:20px;letter-spacing:-.03em}.industry-panel-head>span{font-size:9px;color:rgba(255,255,255,.36)}.industry-skill-list{padding:8px}.industry-skill-row{width:100%;display:grid;grid-template-columns:38px minmax(0,1fr) 74px;gap:12px;align-items:center;text-align:left;padding:13px 10px;border:1px solid transparent;border-radius:12px;background:transparent;color:#fff;cursor:pointer}.industry-skill-row:hover,.industry-skill-row.selected{background:rgba(255,255,255,.055);border-color:rgba(255,255,255,.08)}.industry-rank{font-size:9px;color:rgba(255,255,255,.25);font-weight:800}.industry-skill-copy strong{display:block;font-size:13px}.industry-skill-copy span{display:block;margin-top:4px;font-size:9px;line-height:1.5;color:rgba(255,255,255,.38)}.industry-skill-metric{text-align:right}.industry-skill-metric strong{display:block;font-size:13px}.industry-skill-metric span{font-size:8px;color:rgba(255,255,255,.3)}
.industry-detail-panel{padding:19px}.industry-detail-top h2{font-size:24px;margin:7px 0}.industry-detail-top p{font-size:10px;line-height:1.65;color:rgba(255,255,255,.42);margin:0}.industry-detail-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:16px 0}.industry-detail-stats div{padding:11px;border-radius:11px;background:rgba(255,255,255,.035)}.industry-detail-stats strong{display:block;font-size:15px}.industry-detail-stats span{font-size:8px;color:rgba(255,255,255,.3)}.industry-action-row{display:flex;gap:7px;margin-bottom:19px}.industry-action-row button{flex:1;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.045);color:#fff;font-size:9px;font-weight:800;cursor:pointer}.industry-action-row button:last-child{background:#fff;color:#111}.industry-resource-head{display:flex;justify-content:space-between;align-items:end;gap:10px;margin:12px 0}.industry-resource-head h3{margin:5px 0 0;font-size:15px}.industry-resource-head>span{font-size:8px;color:rgba(255,255,255,.3)}.industry-video-stack,.industry-pdf-stack{display:grid;gap:12px}.industry-video-card{padding:10px;border:1px solid rgba(255,255,255,.07);border-radius:13px;background:rgba(0,0,0,.12)}.industry-resource-label{display:grid;gap:4px;padding:3px 3px 9px}.industry-resource-label span{font-size:8px;color:rgba(255,255,255,.3);letter-spacing:.12em;font-weight:800}.industry-resource-label strong{font-size:10px}.industry-video-frame{position:relative;padding-top:56.25%;border-radius:9px;overflow:hidden;background:#000}.industry-video-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.industry-pdf-card{border:1px solid rgba(255,255,255,.07);border-radius:13px;overflow:hidden;background:rgba(0,0,0,.12)}.industry-pdf-card>div{padding:11px;display:grid;gap:4px}.industry-pdf-card strong{font-size:10px}.industry-pdf-card span{font-size:8px;color:rgba(255,255,255,.3)}.industry-pdf-card>a{display:inline-flex;align-items:center;gap:5px;margin:0 11px 11px;font-size:9px;color:#fff}.industry-pdf-card iframe{width:100%;height:310px;border:0;background:#fff}.industry-resource-empty,.industry-no-data,.industry-empty{padding:24px;border:1px dashed rgba(255,255,255,.1);border-radius:13px;display:grid;gap:7px;color:rgba(255,255,255,.4);font-size:10px;line-height:1.55}.industry-empty{margin-top:20px;text-align:center;justify-items:center;padding:55px 25px}.industry-empty strong{font-size:14px;color:rgba(255,255,255,.72)}.industry-empty small{max-width:600px;color:rgba(255,255,255,.28)}.industry-warning{border-color:rgba(255,180,80,.22)}.industry-loader{width:25px;height:25px;border:2px solid rgba(255,255,255,.12);border-top-color:#fff;border-radius:50%;animation:forgeIndustrySpin .8s linear infinite}@keyframes forgeIndustrySpin{to{transform:rotate(360deg)}}.industry-source-note{margin-top:14px;padding:15px;border:1px solid rgba(255,255,255,.06);border-radius:13px;display:grid;gap:5px;background:rgba(255,255,255,.018)}.industry-source-note strong{font-size:10px}.industry-source-note span{font-size:9px;line-height:1.6;color:rgba(255,255,255,.35)}
@media(max-width:900px){.industry-hero,.industry-main-grid{grid-template-columns:1fr}.industry-horizon-tabs{grid-template-columns:1fr 1fr}}@media(max-width:620px){.industry-horizon-tabs{grid-template-columns:1fr}.industry-skill-row{grid-template-columns:28px minmax(0,1fr) 58px}.industry-detail-stats{grid-template-columns:1fr 1fr}.industry-action-row{flex-direction:column}}

.industry-evidence-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:22px 0 4px}.industry-evidence-cards>div{padding:13px;border:1px solid rgba(255,255,255,.08);border-radius:13px;background:rgba(255,255,255,.025)}.industry-evidence-cards small{display:block;font-size:8px;letter-spacing:.12em;color:rgba(255,255,255,.34);font-weight:800}.industry-evidence-cards strong{display:block;margin-top:8px;font-size:14px}.industry-evidence-cards span{display:block;margin-top:4px;font-size:8px;color:rgba(255,255,255,.32);line-height:1.4}.industry-panel-head p{margin:5px 0 0;font-size:9px;color:rgba(255,255,255,.32)}.industry-skill-copy em{display:block;margin-top:5px;font-size:8px;font-style:normal;color:rgba(255,255,255,.22)}.industry-skill-metric small{display:block;margin-top:4px;font-size:8px;color:rgba(255,255,255,.35)}.industry-detail-meta{display:grid;gap:5px;padding:11px 0;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06);font-size:9px;color:rgba(255,255,255,.38)}.industry-detail-meta strong{color:rgba(255,255,255,.7)}.industry-topic-overlay{position:fixed;inset:0;z-index:2000;background:rgba(0,0,0,.82);backdrop-filter:blur(10px);overflow-y:auto;overflow-x:hidden;overscroll-behavior-y:contain;-webkit-overflow-scrolling:touch;touch-action:pan-y;scrollbar-gutter:stable;padding:24px 18px}.industry-topic-modal{width:min(1000px,100%);margin:0 auto;border:1px solid rgba(255,255,255,.12);border-radius:24px;background:#0b0c0b;box-shadow:0 30px 100px rgba(0,0,0,.55);padding:25px}.industry-topic-modal-head{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.08)}.industry-topic-modal-head small{font-size:8px;letter-spacing:.14em;color:rgba(255,255,255,.35);font-weight:800}.industry-topic-modal-head h2{margin:8px 0 5px;font-size:clamp(28px,5vw,46px);letter-spacing:-.045em}.industry-topic-modal-head p{margin:0;color:rgba(255,255,255,.38);font-size:10px}.industry-topic-content{display:grid;gap:24px;padding-top:22px}.industry-topic-content section{display:grid;gap:10px}.industry-topic-content section>p{margin:0;color:rgba(255,255,255,.5);font-size:11px;line-height:1.7}.industry-topic-hero-grid{display:grid!important;grid-template-columns:minmax(0,1fr) 230px;gap:10px}.industry-topic-score{display:block!important;margin-top:10px;font-size:42px!important;letter-spacing:-.05em}.industry-chip-list{display:flex;flex-wrap:wrap;gap:7px}.industry-chip-list span{padding:8px 11px;border:1px solid rgba(255,255,255,.08);border-radius:999px;background:rgba(255,255,255,.025);font-size:9px;color:rgba(255,255,255,.55)}.industry-topic-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.industry-topic-grid .generated-task{margin:0}.industry-learning-path{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.industry-topic-stats{margin-top:0}.industry-topic-content p{line-height:1.7}.industry-topic-content .generated-task{margin:0}.industry-topic-footer{display:flex;justify-content:space-between;gap:10px;padding-top:5px;border-top:1px solid rgba(255,255,255,.08)}
@media(max-width:900px){.industry-evidence-cards{grid-template-columns:repeat(2,minmax(0,1fr))}.industry-topic-hero-grid{grid-template-columns:1fr}.industry-learning-path{grid-template-columns:1fr 1fr}}@media(max-width:620px){.industry-evidence-cards{grid-template-columns:1fr}.industry-topic-modal{padding:18px}.industry-topic-modal-head{flex-direction:column}.industry-topic-grid{grid-template-columns:1fr}.industry-learning-path{grid-template-columns:1fr}.industry-topic-footer{flex-direction:column}}
.industry-topic-section-title{display:flex;align-items:center;gap:9px;font-size:10px;letter-spacing:.15em;color:rgba(255,255,255,.43);font-weight:900}.industry-topic-section-title:before{content:"";width:24px;height:1px;background:rgba(255,255,255,.7)}.industry-topic-overview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.industry-topic-stat-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}.industry-topic-stat{padding:13px;border:1px solid rgba(255,255,255,.08);border-radius:13px;background:rgba(255,255,255,.025)}.industry-topic-stat strong{display:block;font-size:15px}.industry-topic-stat span{display:block;margin-top:5px;font-size:8px;color:rgba(255,255,255,.3)}.industry-topic-list{display:grid;gap:8px}.industry-topic-list-card{padding:14px 15px;border:1px solid rgba(255,255,255,.08);border-radius:13px;background:rgba(255,255,255,.025)}.industry-topic-list-card strong{display:block;font-size:11px}.industry-topic-list-card p{margin:6px 0 0!important;color:rgba(255,255,255,.4)!important;font-size:10px!important}.industry-arch{display:grid;gap:8px;padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.02)}.industry-arch-node{padding:10px 12px;border:1px solid rgba(255,255,255,.1);border-radius:10px;background:rgba(255,255,255,.035);font-size:10px}.industry-arch-arrow{text-align:center;color:rgba(255,255,255,.3);font-size:12px}.industry-comparison{overflow:auto;border:1px solid rgba(255,255,255,.08);border-radius:14px}.industry-comparison table{width:100%;border-collapse:collapse;min-width:620px}.industry-comparison th,.industry-comparison td{padding:11px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,.07);font-size:9px;vertical-align:top}.industry-comparison th{color:#fff;background:rgba(255,255,255,.04);font-size:8px;letter-spacing:.08em;text-transform:uppercase}.industry-comparison td{color:rgba(255,255,255,.48)}.industry-quiz{display:grid;gap:12px}.industry-quiz-card{padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:15px;background:rgba(255,255,255,.025)}.industry-quiz-card h4{margin:0;font-size:12px;line-height:1.5}.industry-quiz-options{display:grid;gap:7px;margin-top:12px}.industry-quiz-option{border:1px solid rgba(255,255,255,.08);background:transparent;color:rgba(255,255,255,.56);border-radius:10px;padding:10px;text-align:left;font:inherit;font-size:9px;cursor:pointer}.industry-quiz-option.selected{background:#fff;color:#070807;border-color:#fff}.industry-quiz-result{padding:18px;border:1px solid rgba(255,255,255,.12);border-radius:15px;background:rgba(255,255,255,.045)}.industry-quiz-result strong{font-size:30px;letter-spacing:-.04em}.industry-resource-note{font-size:9px;color:rgba(255,255,255,.34);line-height:1.6}.industry-topic-when-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.industry-topic-when{padding:15px;border:1px solid rgba(255,255,255,.08);border-radius:14px}.industry-topic-when strong{display:block;font-size:10px}.industry-topic-when ul{margin:9px 0 0;padding-left:18px;color:rgba(255,255,255,.42);font-size:9px;line-height:1.8}@media(max-width:900px){.industry-topic-stat-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){.industry-topic-overview-grid,.industry-topic-when-grid{grid-template-columns:1fr}.industry-topic-stat-grid{grid-template-columns:1fr 1fr}}.industry-market-panel{margin:20px 0 10px;padding:18px;border:1px solid rgba(255,255,255,.09);border-radius:20px;background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(255,255,255,.018));box-shadow:0 18px 55px rgba(0,0,0,.22)}
.industry-market-panel-v2{position:relative;overflow:hidden;background:radial-gradient(700px 300px at 10% 0%,rgba(101,78,255,.12),transparent 65%),linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));box-shadow:0 24px 70px rgba(0,0,0,.22),inset 0 1px 0 rgba(255,255,255,.06)}
.industry-market-panel-v2:before{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(113,94,255,.025),transparent)}
.industry-market-head{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}
.industry-market-kicker{font-size:8px;letter-spacing:.14em;color:rgba(255,255,255,.42);font-weight:900;display:flex;align-items:center;gap:7px}
.live-dot,.offline-dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.live-dot{background:#66f6b0;box-shadow:0 0 14px rgba(102,246,176,.85)}
.offline-dot{background:#ff7d7d}
.industry-market-head h2{margin:7px 0 5px;font-size:23px;letter-spacing:-.04em}
.industry-market-head p{margin:0;max-width:680px;font-size:9px;line-height:1.6;color:rgba(255,255,255,.36)}
.industry-market-asof{text-align:right;min-width:135px}
.industry-market-asof strong{display:block;font-size:18px;letter-spacing:-.03em}
.industry-market-asof span{display:block;margin-top:4px;font-size:8px;color:rgba(255,255,255,.3)}
.industry-market-status-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,.07);color:rgba(255,255,255,.38);font-size:9px}
.industry-market-status-row span{display:inline-flex;align-items:center;gap:6px;padding:6px 9px;border:1px solid rgba(255,255,255,.07);border-radius:999px;background:rgba(255,255,255,.018)}
.signal-live-dot,.signal-offline-dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.signal-live-dot{background:#72f0a2;box-shadow:0 0 12px rgba(114,240,162,.8);animation:forgeSignalPulse 1.8s ease-in-out infinite}
.signal-offline-dot{background:#ff7b7b}
@keyframes forgeSignalPulse{0%,100%{transform:scale(.85);opacity:.55}50%{transform:scale(1.25);opacity:1}}
.industry-market-body{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:16px;margin-top:15px}
.industry-market-chart-wrap{min-width:0}
.industry-market-chart-title{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:8px;color:rgba(255,255,255,.5);font-size:9px;font-weight:900;letter-spacing:.13em}
.industry-market-chart-title small{font-size:9px;font-weight:500;letter-spacing:0;color:rgba(255,255,255,.25)}
.industry-market-chart{width:100%;height:230px;display:block;overflow:visible}
.industry-market-chart-v2{overflow:visible;display:block;width:100%;height:auto;min-height:250px}.industry-market-chart-v2 .market-line{stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 5px rgba(130,120,255,.22))}.industry-market-chart-v2 .market-axis{stroke:rgba(255,255,255,.14);stroke-width:1}.industry-market-chart-v2 .market-grid{stroke:rgba(255,255,255,.055);stroke-width:1;stroke-dasharray:3 5}.industry-market-point{r:4;stroke:#0b0913;stroke-width:2}.industry-market-dates{display:grid;grid-template-columns:repeat(var(--market-date-count),1fr);margin:2px 10px 0 42px;color:rgba(255,255,255,.3);font-size:9px;text-align:center}.industry-market-missing-note{margin-top:12px;padding:9px 11px;border:1px solid rgba(255,255,255,.07);border-radius:10px;background:rgba(255,255,255,.018);color:rgba(255,255,255,.35);font-size:9px;line-height:1.5}.industry-market-panel-v2 .industry-market-chart-wrap{padding:4px 0 0}.industry-market-panel-v2 .industry-market-body{grid-template-columns:minmax(0,1.55fr) minmax(270px,.75fr);gap:24px}.industry-market-panel-v2 .industry-market-row{min-height:42px}.industry-market-panel-v2 .industry-market-list{padding:13px 14px;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(0,0,0,.12)}.market-dot-point{r:4;stroke:#0b0913;stroke-width:2}.industry-market-legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;color:rgba(255,255,255,.25);font-size:8px}.industry-market-legend span{padding:5px 8px;border:1px solid rgba(255,255,255,.06);border-radius:999px;background:rgba(255,255,255,.015)}
.market-axis{stroke:rgba(255,255,255,.16);stroke-width:1}
.market-grid{stroke:rgba(255,255,255,.05);stroke-width:1}
.market-y-label{fill:rgba(255,255,255,.24);font-size:8px;font-family:inherit}
.market-line{fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px currentColor)}
.market-line-0{stroke:#65e6ff}.market-line-1{stroke:#a78bfa}.market-line-2{stroke:#6ee7b7}.market-line-3{stroke:#fbbf72}.market-line-4{stroke:#fb7185}.market-line-5{stroke:#c4b5fd}
.industry-market-dates{display:flex;justify-content:space-between;padding:0 7px 0 44px;margin-top:-3px;font-size:7px;color:rgba(255,255,255,.28)}
.industry-market-list{display:grid;align-content:start;gap:7px}
.industry-market-list-head{display:grid;grid-template-columns:1fr auto auto;gap:14px;padding:0 10px 8px;color:rgba(255,255,255,.24);font-size:8px;font-weight:900;letter-spacing:.12em}
.industry-market-row{display:grid;grid-template-columns:8px minmax(0,1fr) auto auto;gap:8px;align-items:center;padding:9px;border:1px solid rgba(255,255,255,.07);border-radius:11px;background:rgba(255,255,255,.02);transition:background .2s ease,transform .2s ease}
.industry-market-row:hover{transform:translateX(3px);background:rgba(255,255,255,.035)}
.industry-market-row strong{font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.industry-market-row b{font-size:10px}
.industry-market-row em{font-size:8px;font-style:normal;min-width:42px;text-align:right}
.industry-market-row em.up{color:#66f6b0}.industry-market-row em.down{color:#ff8a8a}.industry-market-row em.flat{color:rgba(255,255,255,.3)}
.market-dot{width:7px;height:7px;border-radius:50%;display:block}
.market-dot-0{background:#65e6ff}.market-dot-1{background:#a78bfa}.market-dot-2{background:#6ee7b7}.market-dot-3{background:#fbbf72}.market-dot-4{background:#fb7185}.market-dot-5{background:#c4b5fd}
.industry-market-foot{display:flex;justify-content:space-between;gap:10px;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.06);font-size:7px;color:rgba(255,255,255,.25)}
.industry-market-missing-note{margin-top:9px;color:rgba(255,220,160,.52);font-size:9px;line-height:1.5}
.industry-market-empty{padding:22px 5px;color:rgba(255,255,255,.38);font-size:9px}
@media(max-width:900px){.industry-market-body{grid-template-columns:1fr}.industry-market-list{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.industry-market-head{flex-direction:column}.industry-market-asof{text-align:left}.industry-market-list{grid-template-columns:1fr}.industry-market-foot{flex-direction:column}}

/* FINAL INDUSTRY PULSE VISUAL PASS */
.industry-horizon-tabs button{position:relative;overflow:hidden;border-color:rgba(190,145,255,.13);background:linear-gradient(145deg,rgba(36,22,56,.72),rgba(12,9,21,.82));transition:.28s ease;min-height:72px}.industry-horizon-tabs button:nth-child(1){--ih:#66e5ff}.industry-horizon-tabs button:nth-child(2){--ih:#a777ff}.industry-horizon-tabs button:nth-child(3){--ih:#6fe7b0}.industry-horizon-tabs button:nth-child(4){--ih:#ff8ab6}.industry-horizon-tabs button:before{content:"";position:absolute;left:0;top:0;width:100%;height:2px;background:linear-gradient(90deg,var(--ih),transparent);opacity:.35}.industry-horizon-tabs button:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--ih) 45%,transparent);box-shadow:0 18px 45px color-mix(in srgb,var(--ih) 8%,transparent)}.industry-horizon-tabs button.active{border-color:color-mix(in srgb,var(--ih) 60%,transparent);background:linear-gradient(145deg,color-mix(in srgb,var(--ih) 10%,#181026),rgba(11,8,20,.86));box-shadow:0 0 28px color-mix(in srgb,var(--ih) 10%,transparent),inset 0 1px rgba(255,255,255,.06)}.industry-horizon-tabs strong{font-size:10px;color:#fff}.industry-horizon-tabs span{color:color-mix(in srgb,var(--ih) 58%,white)}
.industry-main-grid{gap:18px}.industry-skill-panel,.industry-detail-panel{border-color:rgba(190,145,255,.14);background:linear-gradient(145deg,rgba(32,20,49,.74),rgba(10,8,18,.84));box-shadow:0 22px 70px rgba(10,2,25,.2),inset 0 1px rgba(255,255,255,.04)}.industry-skill-row{position:relative;min-height:74px;border-color:transparent;transition:.25s ease}.industry-skill-row:after{content:"";position:absolute;left:38px;right:12px;bottom:0;height:1px;background:rgba(190,145,255,.055)}.industry-skill-row:hover,.industry-skill-row.selected{transform:translateX(3px);background:linear-gradient(90deg,rgba(142,79,255,.11),rgba(70,210,255,.035));border-color:rgba(181,132,255,.18);box-shadow:inset 3px 0 #a76dff}.industry-rank{color:#8f76b8}.industry-skill-copy strong{font-size:14px}.industry-skill-copy span{color:rgba(230,219,246,.48)}.industry-skill-metric strong{color:#d8c6f3}.industry-detail-panel{padding:21px}.industry-detail-top h2{font-size:29px}.industry-detail-stats div{border:1px solid rgba(190,145,255,.08);background:rgba(255,255,255,.025);transition:.25s}.industry-detail-stats div:hover{transform:translateY(-2px);border-color:rgba(177,128,255,.22)}
.industry-topic-overlay{background:rgba(5,3,12,.72);backdrop-filter:blur(18px)}.industry-topic-modal{border-color:rgba(190,145,255,.18);background:linear-gradient(145deg,#171025,#0c0814);box-shadow:0 40px 130px rgba(0,0,0,.58),0 0 70px rgba(121,67,255,.08);border-radius:28px}.industry-topic-modal-head{position:sticky;top:-25px;z-index:2;padding-top:25px;background:linear-gradient(#171025 78%,transparent);backdrop-filter:blur(10px)}.industry-topic-content section{padding:19px;border:1px solid rgba(190,145,255,.09);border-radius:20px;background:linear-gradient(145deg,rgba(34,21,52,.58),rgba(12,8,21,.52));box-shadow:inset 0 1px rgba(255,255,255,.03)}.industry-topic-section-title{color:#c5a7ef !important}.industry-topic-stat{background:rgba(255,255,255,.025);border-color:rgba(190,145,255,.09);transition:.25s}.industry-topic-stat:hover{transform:translateY(-2px);border-color:rgba(108,221,255,.2);box-shadow:0 0 24px rgba(87,200,255,.05)}.industry-topic-list-card{background:rgba(255,255,255,.025);border-color:rgba(190,145,255,.09);transition:.25s}.industry-topic-list-card:hover{transform:translateY(-2px);border-color:rgba(177,127,255,.25);box-shadow:0 14px 35px rgba(53,14,91,.18)}.industry-learning-path .assessment-breakdown-card{background:linear-gradient(145deg,rgba(77,46,108,.22),rgba(255,255,255,.02));border-color:rgba(190,145,255,.1)}.industry-quiz-card{background:rgba(255,255,255,.025);border-color:rgba(190,145,255,.1)}
` ;


const FORGE_API_BASE = (import.meta.env.VITE_FORGE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function StudentIndustryPulse(){
  const navigate=useNavigate();
  const profile=readS("forge_student_profile",{});
  const subjects=readS("forge_student_subjects",[]);
  const roadmap=readS("forge_student_roadmap",null);
  const targetRole=profile?.targetRole||"";
  const isDataScientist=targetRole==="Data Scientist";
  const [pulse,setPulse]=useState(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  const [activeHorizon,setActiveHorizon]=useState("emerging");
  const [selectedTopic,setSelectedTopic]=useState(null);
  const [topicDetail,setTopicDetail]=useState(null);
  const [topicLoading,setTopicLoading]=useState(false);
  const [topicError,setTopicError]=useState("");
  const [resources,setResources]=useState({});
  const [resourceLoading,setResourceLoading]=useState(false);
  const [assessmentAnswers,setAssessmentAnswers]=useState({});
  const [assessmentSubmitted,setAssessmentSubmitted]=useState(false);
  const [assessmentScore,setAssessmentScore]=useState(null);

  useEffect(()=>{
    let cancelled=false;
    async function load(){
      if(!targetRole){
        setLoading(false);
        setError("Set your target role in Student Profile first.");
        return;
      }
      setLoading(true); setError("");
      const params=new URLSearchParams({
        role:targetRole,
        subjects:subjects.join(","),
        refresh:String(Date.now())
      });
      try{
        const controller=new AbortController();
        const timeout=window.setTimeout(()=>controller.abort(),12000);
        const response=await fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{
          cache:"no-store",
          signal:controller.signal
        });
        window.clearTimeout(timeout);
        if(!response.ok) throw new Error(`Industry Pulse API returned ${response.status}`);
        const data=await response.json();
        if(!cancelled){setPulse(normalizeIndustryPulse(data));setLoading(false);}
      }catch(err){
        if(!cancelled){
          setPulse(null);
          setError(err?.message||"Unable to connect to the Industry Pulse backend.");
          setLoading(false);
        }
      }
    }
    load();
    return()=>{cancelled=true};
  },[targetRole,subjects.join(",")]);

  // Refresh Industry Pulse once per hour so a newly published daily market
  // snapshot becomes visible without touching the rest of the dashboard.
  useEffect(()=>{
    if(!targetRole)return;
    const timer=window.setInterval(()=>{
      const params=new URLSearchParams({
        role:targetRole,
        subjects:subjects.join(","),
        refresh:String(Date.now())
      });
      fetch(`${FORGE_API_BASE}/api/student/industry-pulse?${params.toString()}`,{cache:"no-store"})
        .then(r=>r.ok?r.json():null)
        .then(data=>{if(data)setPulse(normalizeIndustryPulse(data));})
        .catch(()=>{});
    },60*60*1000);
    return()=>window.clearInterval(timer);
  },[targetRole,subjects.join(",")]);

  const horizonData=pulse?.[activeHorizon]||[];

  const marketSignal=pulse?.market_signal||pulse?.daily_market||{};
  const marketSkills=Array.isArray(marketSignal?.skills)?marketSignal.skills:[];
  const marketStatus=marketSignal?.status||"offline";
  const marketSource=marketSignal?.source||"Daily market feed";
  const marketRequestedDays=Number(marketSignal?.requested_window_days)||7;

  // Use only dates actually supplied by the backend. A missing day such as
  // Oct 06 must never be fabricated just to make the graph look complete.
  const marketSeries=useMemo(()=>{
    const byDate=new Map();
    marketSkills.forEach(skill=>{
      (Array.isArray(skill?.series)?skill.series:[]).forEach(point=>{
        const date=String(point?.date||"").slice(0,10);
        const value=Number(point?.value);
        if(/^\d{4}-\d{2}-\d{2}$/.test(date)&&Number.isFinite(value)){
          if(!byDate.has(date))byDate.set(date,[]);
          byDate.get(date).push(value);
        }
      });
    });
    return [...byDate.keys()].sort().slice(-marketRequestedDays);
  },[marketSkills,marketRequestedDays]);

  const marketDates=marketSeries.length
    ? marketSeries
    : (Array.isArray(marketSignal?.snapshot_dates)
      ? marketSignal.snapshot_dates.map(x=>String(x).slice(0,10)).sort().slice(-marketRequestedDays)
      : []);
  const marketLatest=marketSignal?.latest_snapshot||marketDates[marketDates.length-1]||null;

  const marketChartSkills=useMemo(()=>{
    const dates=marketDates;
    if(!dates.length)return [];
    const dateSet=new Set(dates);
    return marketSkills
      .map((skill,index)=>{
        const points=(Array.isArray(skill?.series)?skill.series:[])
          .map(p=>({date:String(p?.date||"").slice(0,10),value:Number(p?.value)}))
          .filter(p=>dateSet.has(p.date)&&Number.isFinite(p.value))
          .sort((a,b)=>a.date.localeCompare(b.date));
        if(!points.length)return null;
        const pointMap=new Map(points.map(p=>[p.date,p.value]));
        return {...skill,index,points:dates.map(date=>({date,value:pointMap.get(date)}))};
      })
      .filter(Boolean)
      .slice(0,6);
  },[marketSkills,marketDates.join(",")]);

  const marketAllValues=marketChartSkills.flatMap(skill=>skill.points.map(p=>p.value).filter(Number.isFinite));
  const marketYMin=marketAllValues.length?Math.max(0,Math.floor(Math.min(...marketAllValues)-2)):0;
  const marketYMax=marketAllValues.length?Math.ceil(Math.max(...marketAllValues)+2):100;
  const marketYSpan=Math.max(marketYMax-marketYMin,1);

  const marketPath=(skill)=>{
    const valid=skill.points.filter(p=>Number.isFinite(p.value));
    if(valid.length<2)return "";
    const xFor=(date)=>52+(Math.max(datesIndex(marketDates,date),0)/Math.max(marketDates.length-1,1))*688;
    const yFor=(value)=>195-((value-marketYMin)/marketYSpan)*170;
    return valid.map((p,i)=>{
      const x=xFor(p.date), y=yFor(p.value);
      if(i===0)return `M ${x.toFixed(1)} ${y.toFixed(1)}`;
      const prev=valid[i-1];
      const px=xFor(prev.date), py=yFor(prev.value);
      const cx=(px+x)/2;
      return `C ${cx.toFixed(1)} ${py.toFixed(1)}, ${cx.toFixed(1)} ${y.toFixed(1)}, ${x.toFixed(1)} ${y.toFixed(1)}`;
    }).join(" ");
  };

  const datesIndex=(dates,date)=>dates.indexOf(date);

  const marketMentions=(item)=>item?.market_mentions??item?.mentions??item?.posting_count??item?.job_posting_count??null;
  const prevalence=(item)=>item?.prevalence_percent??item?.percentage??item?.demand_percentage??null;
  const confidence=(item)=>item?.confidence!=null?Number(item.confidence):null;
  const trendLabel=(item)=>item?.trend_label||item?.trend_direction||item?.trend||null;
  const trendChange=(item)=>item?.share_change_pp!=null?Number(item.share_change_pp):item?.growth!=null?Number(item.growth):item?.change!=null?Number(item.change):item?.growth_percentage!=null?Number(item.growth_percentage):null;
  const sourceLabel=(item)=>item?.source||item?.evidence_source||item?.source_name||"FORGE evidence pipeline";
  const evidenceFor=(item)=>{
    if(item?.description && !/marked Emerging only|source supports the broad capability direction|occupation-level structural outlook/i.test(String(item.description))) return item.description;
    const name=item?.name||"This capability";
    if(activeHorizon==="current") return item?.market_mentions!=null && item?.role_job_count!=null
      ? `Observed in ${item.market_mentions} of ${item.role_job_count} role-matched postings in the latest complete evidence window.`
      : `${name} is present in the observed employer evidence for this role.`;
    if(activeHorizon==="emerging") {
      const delta=item?.share_change_pp!=null?Number(item.share_change_pp):null;
      const consistency=item?.trend_consistency!=null?Math.round(Number(item.trend_consistency)*100):null;
      return delta!=null
        ? `${name} shows a ${delta>=0?"positive":"negative"} ${Math.abs(delta).toFixed(1)} percentage-point change across the compared market windows${consistency!=null?`, with positive movement in ${consistency}% of usable transitions`:""}.`
        : `${name} qualifies from observed multi-period market movement rather than a fixed future list.`;
    }
    if(activeHorizon==="fiveYear") {
      const support=Array.isArray(item?.supporting_topics)&&item.supporting_topics.length?` Supported by observed topics such as ${item.supporting_topics.slice(0,4).join(", ")}.`:"";
      return `WEF provides the broad 2030 capability signal for ${name}; FORGE uses employer and O*NET evidence to establish role relevance, not a technology forecast.${support}`;
    }
    if(activeHorizon==="tenYear") {
      const growth=item?.bls_growth_percent!=null?Number(item.bls_growth_percent):null;
      return growth!=null
        ? `BLS projects ${name} at the occupation level through 2035, with ${growth.toFixed(1)}% projected employment change. This does not predict the future of an individual technology.`
        : `BLS provides occupation-level context through 2035; FORGE does not convert it into a technology-specific prediction.`;
    }
    return `${name} is a role-relevant signal from the connected FORGE evidence layers.`;
  };

  const horizonMetric=(item)=>{
    if(activeHorizon==="current") return prevalence(item)!=null?{value:`${Number(prevalence(item)).toFixed(1)}%`,label:"postings"}:marketMentions(item)!=null?{value:marketMentions(item),label:"mentions"}:{value:"—",label:"evidence"};
    if(activeHorizon==="emerging") return item?.share_change_pp!=null?{value:`${Number(item.share_change_pp)>=0?"+":""}${Number(item.share_change_pp).toFixed(1)}pp`,label:"share movement"}:{value:item?.market_mentions??"—",label:"mentions"};
    if(activeHorizon==="fiveYear") return item?.role_relevance!=null?{value:`${Math.round(Number(item.role_relevance)*100)}%`,label:"role relevance"}:{value:"WEF",label:"2030 context"};
    if(activeHorizon==="tenYear") return item?.bls_growth_percent!=null?{value:`${Number(item.bls_growth_percent).toFixed(1)}%`,label:"2035 growth"}:{value:"BLS",label:"2035 context"};
    return {value:"—",label:"context"};
  };

  const openTopic=async(item)=>{
    if(!item?.name)return;
    setSelectedTopic(item);
    setTopicDetail(null);
    setTopicError("");
    setAssessmentAnswers({});
    setAssessmentSubmitted(false);
    setAssessmentScore(null);
    setTopicLoading(true);
    try{
      const params=new URLSearchParams({role:targetRole,topic:item.name,horizon:activeHorizon});
      const response=await fetch(`${FORGE_API_BASE}/api/student/industry-topic?${params.toString()}`);
      if(!response.ok) throw new Error(`Topic Intelligence API returned ${response.status}`);
      const data=await response.json();
      // Backend returns the Topic Intelligence object directly.
      // Do not fall back to data.topic: that field is only the topic name.
      const detail = (data?.topic_intelligence && typeof data.topic_intelligence === "object")
        ? data.topic_intelligence
        : (data?.intelligence && typeof data.intelligence === "object")
          ? data.intelligence
          : data;
      setTopicDetail(detail);
    }catch(err){
      setTopicError(err?.message||"Topic intelligence could not be loaded.");
    }finally{setTopicLoading(false);}
  };

  const closeTopic=()=>{
    setSelectedTopic(null);
    setTopicDetail(null);
    setTopicError("");
  };

  useEffect(()=>{
    if(!selectedTopic?.name)return;
    const previousOverflow=document.body.style.overflow;
    const previousOverscroll=document.body.style.overscrollBehavior;
    document.body.style.overflow="hidden";
    document.body.style.overscrollBehavior="none";
    let cancelled=false;
    async function loadResources(){
      setResourceLoading(true);
      const params=new URLSearchParams({role:targetRole,topic:selectedTopic.name,horizon:activeHorizon});
      try{
        const response=await fetch(`${FORGE_API_BASE}/api/student/industry-resources?${params.toString()}`);
        if(!response.ok) throw new Error("Resource endpoint unavailable");
        const data=await response.json();
        if(!cancelled)setResources(v=>({...v,[selectedTopic.name]:normalizeIndustryResources(data)}));
      }catch{
        if(!cancelled)setResources(v=>({...v,[selectedTopic.name]:[]}));
      }finally{
        if(!cancelled)setResourceLoading(false);
      }
    }
    loadResources();
    return()=>{
      cancelled=true;
      document.body.style.overflow=previousOverflow;
      document.body.style.overscrollBehavior=previousOverscroll;
    };
  },[selectedTopic?.name,targetRole,activeHorizon]);

  // Prefer the verified resource endpoint, but fall back to the resources
  // already returned with Topic Intelligence. This prevents a successful
  // topic response from showing an empty video area if the separate
  // resource request is temporarily unavailable.
  const currentResources=(
    resources[selectedTopic?.name]?.length
      ? resources[selectedTopic.name]
      : (Array.isArray(topicDetail?.resources) ? topicDetail.resources : [])
  );
  const videos=currentResources.filter(x=>x.type==="video");
  const articles=currentResources.filter(x=>x.type==="article");
  const docs=currentResources.filter(x=>x.type==="pdf");
  const links=currentResources.filter(x=>x.type==="doc"||x.type==="link");

  const submitTopicAssessment=()=>{
    const questions=topicDetail?.assessment?.questions||[];
    if(!questions.length)return;
    const answered=questions.every((_,i)=>assessmentAnswers[i]!==undefined);
    if(!answered)return;
    const score=questions.reduce((n,q,i)=>n+(Number(assessmentAnswers[i])===Number(q.answer_index)?1:0),0);
    setAssessmentScore(score);
    setAssessmentSubmitted(true);
    const progress=readS("forge_student_topic_progress",{});
    const key=topicDetail?.topic_key||selectedTopic?.topic_key||selectedTopic?.name;
    const next={...progress,[key]:{topic:topicDetail?.topic||selectedTopic?.name,score,total:questions.length,status:score/questions.length>=0.8?"Demonstrated":score/questions.length>=0.6?"Developing":"Needs practice",updatedAt:new Date().toISOString()}};
    sessionStorage.setItem("forge_student_topic_progress",JSON.stringify(next));
  };

  const addToRoadmap=(item=selectedTopic)=>{
    if(!item?.name)return;
    const current=readS("forge_student_industry_topics",[]);
    const key=item.topic_key||item.name;
    const next=[...current.filter(x=>(x.topic_key||x.name)!==key),{...item,horizon:activeHorizon,addedAt:new Date().toISOString()}];
    sessionStorage.setItem("forge_student_industry_topics",JSON.stringify(next));
  };

  const horizonMeta={
    current:["CURRENT DEMAND","Observed employer demand","What employers are asking for"],
    emerging:["EMERGING TOPICS","Growing signals in available market evidence","What is gaining signal"],
    fiveYear:["5-YEAR CAPABILITY RADAR","Evidence toward 2030","What may matter toward 2030"],
    tenYear:["10-YEAR CAPABILITY RADAR","Long-horizon context through 2035","What may matter over the longer horizon"]
  };
  const [horizonLabel,horizonSub,horizonQuestion]=horizonMeta[activeHorizon];

  const provenance=pulse?.data_provenance||pulse?.provenance||{};
  const rolePostingCount=provenance.role_posting_count??provenance.job_posting_count??pulse?.role_posting_count??pulse?.job_posting_count??pulse?.current?.find(x=>x?.role_job_count!=null)?.role_job_count??pulse?.emerging?.find(x=>x?.role_job_count!=null)?.role_job_count;
  const techRecordCountRaw=
    provenance?.technology_record_count ??
    pulse?.technology_record_count ??
    pulse?.onet_technology_record_count ??
    provenance?.technology_evidence_count ??
    pulse?.technology_evidence_count ??
    (typeof pulse?.technology_evidence === "object" ? pulse.technology_evidence?.record_count : null);
  const techRecordCount =
    techRecordCountRaw == null || Number.isNaN(Number(techRecordCountRaw))
      ? null
      : Number(techRecordCountRaw);

  if(loading) return <><StudentStyles/><style>{INDUSTRY_PULSE_STYLE}</style><main className="forge-student-page"><div className="forge-student-shell industry-pulse-shell"><div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/learning")}><ChevronLeft size={15}/>Learning Hub</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">INDUSTRY PULSE</div></div><div className="industry-empty"><div className="industry-loader"/><strong>Reading industry signals…</strong><span>FORGE is matching your role against connected employer and technology evidence.</span></div></div></main></>;

  if(error) return <><StudentStyles/><style>{INDUSTRY_PULSE_STYLE}</style><main className="forge-student-page"><div className="forge-student-shell industry-pulse-shell"><div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/learning")}><ChevronLeft size={15}/>Learning Hub</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">INDUSTRY PULSE</div></div><div className="industry-empty industry-warning"><strong>Industry data connection required</strong><span>{error}</span><button className="student-continue" style={{marginTop:8}} onClick={()=>window.location.reload()}>Retry <RotateCcw size={14}/></button></div></div></main></>;

  return <><StudentStyles/><style>{INDUSTRY_PULSE_STYLE}</style><main className="forge-student-page"><div className="forge-student-shell industry-pulse-shell">
    <div className="student-topbar"><button className="student-back" onClick={()=>navigate("/student/learning")}><ChevronLeft size={15}/>Learning Hub</button><div className="student-brand-mini"><strong>FORGE</strong><span>STUDENT WORKSPACE</span></div><div className="student-progress-label">INDUSTRY PULSE</div></div>

    <div className="industry-hero">
      <div><div className="student-step-eyebrow"><span/>INDUSTRY PULSE · LIVE EVIDENCE</div><h1 className="student-title">{isDataScientist?<>Data Scientist market<br/><em>intelligence, grounded in evidence.</em></>:<>See how your role<br/><em>is changing.</em></>}</h1><p className="student-description">{isDataScientist?"FORGE connects observed Data Scientist employer demand with emerging skill signals, 2030 capability context and 2035 occupation outlook — without turning those horizons into individual-success predictions.":"FORGE separates observed employer demand from emerging signals and longer-horizon capability context. It does not fill missing evidence with a fixed skill list."}</p></div>
      <div className="industry-role-card"><small>TARGET ROLE</small><strong>{targetRole||"Not set"}</strong><span>{subjects.length} selected learning areas · {roadmap?.subjects?.length||0} roadmap areas</span></div>
    </div>

    <section className="industry-market-panel industry-market-panel-v2">
      <div className="industry-market-head">
        <div>
          <div className="industry-market-kicker"><span className={marketStatus==="live"?"live-dot":"offline-dot"}/>{marketStatus==="live"?"LIVE DAILY MARKET SIGNAL":"SIGNAL FEED OFFLINE"}</div>
          <h2>{isDataScientist?"What is changing in Data Scientist demand?":`What is changing in ${targetRole||"your role"}?`}</h2>
          <p>{isDataScientist?"Observed daily skill-demand evidence is shown first; emerging, 5-year and 10-year sections remain separate so evidence and scenario context are not mixed.":"Actual daily skill-demand observations from the connected market feed. FORGE treats movement as percentage-point change — not a stock price and not a forecast."}</p>
        </div>
        <div className="industry-market-asof">
          <strong>{marketLatest||"—"}</strong>
          <span>{marketDates.length ? `${marketDates.length} actual day${marketDates.length===1?"":"s"} available` : "No observations available"}</span>
        </div>
      </div>

      <div className="industry-market-status-row">
        <span><i className={marketStatus==="live"?"signal-live-dot":"signal-offline-dot"}/>{marketStatus==="live"?"Connected to live market evidence":"No live market observations"}</span>
        <span>Requested window: {marketRequestedDays} days</span>
        <span>{marketLatest?`Latest source observation: ${marketLatest}`:"Waiting for source update"}</span>
      </div>

      {marketChartSkills.length ? <div className="industry-market-body">
        <div className="industry-market-chart-wrap">
          <div className="industry-market-chart-title"><span>SKILL DEMAND MOVEMENT</span><small>Daily observed demand %</small></div>
          <svg className="industry-market-chart industry-market-chart-v2" viewBox="0 0 760 230" role="img" aria-label="Actual daily skill demand trend">
            <line x1="42" y1="15" x2="42" y2="205" className="market-axis"/>
            <line x1="42" y1="205" x2="750" y2="205" className="market-axis"/>
            {[0,1,2,3].map(i=>{
              const y=15+i*63.3;
              const value=marketYMax-(i/3)*marketYSpan;
              return <Fragment key={i}><line x1="42" y1={y} x2="750" y2={y} className="market-grid"/><text x="7" y={y+3} className="market-y-label">{value.toFixed(0)}%</text></Fragment>;
            })}
            {marketChartSkills.map((skill,i)=>{
              const path=marketPath(skill);
              return <Fragment key={skill.skill||i}>
                {path?<path d={path} className={`market-line market-line-${i}`} fill="none"/>:null}
                {skill.points.filter(p=>Number.isFinite(p.value)).map(p=>{
                  const x=52+(Math.max(datesIndex(marketDates,p.date),0)/Math.max(marketDates.length-1,1))*688;
                  const y=195-((p.value-marketYMin)/marketYSpan)*170;
                  return <circle key={`${skill.skill}-${p.date}`} cx={x} cy={y} className={`market-dot-point market-dot-point-${i}`}/>;
                })}
              </Fragment>;
            })}
          </svg>
          <div className="industry-market-dates" style={{"--market-date-count":Math.max(marketDates.length,1)}}>
            {marketDates.map(d=><span key={d}>{d.slice(5)}</span>)}
          </div>
          {!marketDates.includes("2026-10-06") && marketLatest==="2026-10-05" && <div className="industry-market-missing-note">Oct 06 is not present in the source yet. FORGE shows the latest real observation instead of inventing a value.</div>}
          <div className="industry-market-legend"><span>Each line = one skill</span><span>Values = observed demand %</span><span>Move = latest vs previous snapshot</span></div>
        </div>

        <div className="industry-market-list">
          <div className="industry-market-list-head"><span>SKILL</span><span>DEMAND</span><span>MOVE</span></div>
          {marketChartSkills.map((skill,i)=><div className="industry-market-row" key={skill.skill||i}>
            <span className={`market-dot market-dot-${i}`}/><strong>{skill.skill}</strong><b>{Number(skill.current_demand_pct||0).toFixed(1)}%</b><em className={skill.direction==="up"?"up":skill.direction==="down"?"down":"flat"}>{skill.delta_pp==null?"—":`${skill.delta_pp>=0?"+":""}${Number(skill.delta_pp).toFixed(1)} pp`}</em>
          </div>)}
        </div>
      </div> : <div className="industry-market-empty">{marketSignal?.message||"Waiting for a real daily market snapshot. No synthetic values are shown."}</div>}

      <div className="industry-market-foot"><span>{marketSource}</span><span>Daily active-listing demand · observed market signal</span></div>
    </section>

    <div className="industry-evidence-cards">
      <div><small>ROLE POSTINGS</small><strong>{rolePostingCount??"—"}</strong><span>matched employer postings</span></div>
      <div><small>TECHNOLOGY EVIDENCE</small><strong>{techRecordCount == null ? "—" : techRecordCount.toLocaleString()}</strong><span>O*NET technology records</span></div>
      <div><small>5-YEAR CONTEXT</small><strong>{provenance.future_evidence||"WEF"}</strong><span>2030 capability context</span></div>
      <div><small>10-YEAR CONTEXT</small><strong>{provenance.bls_evidence||"BLS"}</strong><span>occupation outlook</span></div>
    </div>

    <div className="industry-horizon-tabs">{[["current","CURRENT DEMAND","Observed now"],["emerging","EMERGING TOPICS","Growing signals"],["fiveYear","5-YEAR CAPABILITY RADAR","Toward 2030"],["tenYear","10-YEAR CAPABILITY RADAR","Through 2035"]].map(([key,label,sub])=><button key={key} className={activeHorizon===key?"active":""} onClick={()=>{setActiveHorizon(key);setSelectedTopic(null);setTopicDetail(null);}}><strong>{label}</strong><span>{sub}</span></button>)}</div>

    <div className="industry-evidence-strip"><span>ROLE-SPECIFIC</span><span>DATA-DERIVED</span><span>NO FAKE FORECASTS</span><span>CLICK TO INSPECT</span></div>

    <div className="industry-main-grid">
      <section className="industry-skill-panel">
        <div className="industry-panel-head"><div><small>{horizonLabel}</small><h2>{horizonQuestion}</h2><p>{horizonSub}</p></div><span>{horizonData.length} signals</span></div>
        <div className="industry-skill-list">
          {horizonData.length?horizonData.map((item,i)=>{
            const pct=prevalence(item);
            const mentions=marketMentions(item);
            const change=trendChange(item);
            const conf=confidence(item);
            const metric=horizonMetric(item);
            return <button key={`${item.name}-${i}`} className={`industry-skill-row ${selectedTopic?.name===item.name?"selected":""}`} onClick={()=>openTopic(item)}>
              <div className="industry-rank">{String(i+1).padStart(2,"0")}</div>
              <div className="industry-skill-copy"><strong>{item.name}</strong><span>{evidenceFor(item)}</span><em>{sourceLabel(item)}</em></div>
              <div className="industry-skill-metric"><strong>{metric.value}</strong><span>{metric.label}</span>{change!=null&&activeHorizon==="current"&&<small>{change>0?"↑":""}{Number(change).toFixed(1)}{item.share_change_pp!=null?" pp":"%"}</small>}{conf!=null&&<small>{Math.round(conf*100)}% confidence</small>}</div>
            </button>;
          }):<div className="industry-no-data"><strong>No sufficiently supported signals.</strong><span>FORGE does not invent topics when the connected evidence is insufficient.</span></div>}
        </div>
      </section>

      <aside className="industry-detail-panel">
        {!selectedTopic?<div className="industry-resource-empty"><strong>Select a capability</strong><span>Click a topic to open its evidence, trend, future interpretation and learning intelligence.</span></div>:<>
          <div className="industry-detail-top"><small>{horizonLabel}</small><h2>{selectedTopic.name}</h2><p>{evidenceFor(selectedTopic)}</p></div>
          <div className="industry-detail-stats"><div><strong>{prevalence(selectedTopic)!=null?`${Number(prevalence(selectedTopic)).toFixed(1)}%`:"—"}</strong><span>market prevalence</span></div><div><strong>{marketMentions(selectedTopic)??"—"}</strong><span>posting mentions</span></div><div><strong>{confidence(selectedTopic)!=null?`${Math.round(confidence(selectedTopic)*100)}%`:"—"}</strong><span>signal confidence</span></div></div>
          <div className="industry-detail-meta"><span>Trend: <strong>{trendLabel(selectedTopic)||"Evidence-based signal"}</strong></span><span>Source: <strong>{sourceLabel(selectedTopic)}</strong></span></div>
          <div className="industry-action-row"><button onClick={()=>addToRoadmap(selectedTopic)}>Add to Roadmap <Plus size={14}/></button><button onClick={()=>openTopic(selectedTopic)}>Open Intelligence <ArrowRight size={14}/></button></div>
          <div className="industry-source-note"><strong>Future interpretation</strong><span>{activeHorizon==="tenYear"?"BLS provides an occupation-level 2025–2035 outlook; it is not a direct forecast of this individual technology.":activeHorizon==="fiveYear"?"WEF provides broad employer skill signals toward 2030; FORGE combines those signals with technology and market evidence rather than claiming a direct forecast of this topic.":activeHorizon==="emerging"?"Emerging status is derived from observed market evidence and trend consistency, not from a manually authored future list.":"Current Demand reflects observed role-specific employer-posting evidence."}</span></div>
        </>}
      </aside>
    </div>

    <div className="industry-source-note"><strong>Evidence layers connected to this view</strong><span>Employer job postings provide market evidence. O*NET provides occupation-specific technology evidence. WEF contributes broad 2025–2030 skill signals. BLS contributes occupation-level 2025–2035 projections. FORGE keeps those evidence types separate instead of presenting a technology-specific forecast that the source does not support.</span></div>

    <div className="student-bottom"><div className="student-validation"><strong>Turn signals into capability.</strong> Inspect a topic, learn it, practice it and add it to your roadmap.</div><div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button className="student-option" onClick={()=>navigate("/student/ask")}>Ask FORGE</button><button className="student-continue" onClick={()=>navigate("/student/learning")}>Back to Learning <ArrowRight size={15}/></button></div></div>

    {selectedTopic&&<div className="industry-topic-overlay" onClick={closeTopic}><div className="industry-topic-modal" onClick={e=>e.stopPropagation()}>
      <div className="industry-topic-modal-head"><div><small>{horizonLabel} · TOPIC INTELLIGENCE</small><h2>{topicDetail?.topic||selectedTopic.name}</h2><p>{targetRole} · dynamic evidence-backed learning workspace</p></div><button className="student-option" onClick={closeTopic}>Close</button></div>

      {topicLoading?<div className="industry-empty"><div className="industry-loader"/><strong>Building topic intelligence…</strong><span>FORGE is generating the topic workspace from the capability, evidence and learning layers.</span></div>:topicError?<div className="industry-empty industry-warning"><strong>Topic intelligence unavailable</strong><span>{topicError}</span><small>The underlying Industry Pulse card remains based on live evidence.</small></div>:topicDetail&&<div className="industry-topic-content">
        <section className="industry-topic-hero-grid">
          <div className="generated-task"><small>OVERVIEW</small><h3>{topicDetail.overview?.definition||topicDetail.definition||selectedTopic.name}</h3><p>{topicDetail.overview?.why_it_matters||topicDetail.why_it_matters||"FORGE has identified this as a role-relevant capability signal."}</p><div className="industry-chip-list" style={{marginTop:10}}><span>{topicDetail.topic_category||"Technical capability"}</span><span>{topicDetail.difficulty||topicDetail.overview?.difficulty||"Intermediate"}</span></div></div>
          <div className="generated-task"><small>EVIDENCE STATUS</small><strong className="industry-topic-score">{topicDetail.confidence_label||"Evidence-backed"}</strong><span>{topicDetail.market_evidence?.market_mentions??0} of {topicDetail.market_evidence?.role_job_count??0} recent role-matched postings</span></div>
        </section>

        <section><div className="industry-topic-section-title">01 · OVERVIEW</div><div className="industry-topic-when-grid"><div className="industry-topic-when"><strong>WHEN TO USE</strong><ul>{(topicDetail.overview?.when_to_use||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div><div className="industry-topic-when"><strong>WHEN NOT TO USE</strong><ul>{(topicDetail.overview?.when_not_to_use||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div></div></section>

        <section><div className="industry-topic-section-title">01B · WHY THIS MATTERS NOW</div><div className="generated-task"><h3 style={{marginTop:0}}>{topicDetail.why_now?.title||`Why ${topicDetail.topic||selectedTopic.name} matters now`}</h3><p>{topicDetail.why_now?.market||topicDetail.overview?.why_it_matters||"FORGE separates observed employer demand from future-work context."}</p><p style={{marginBottom:0}}>{topicDetail.why_now?.future||"Future sources are shown as context rather than a guaranteed technology forecast."}</p></div></section>

        <section><div className="industry-topic-section-title">02 · MARKET EVIDENCE</div><div className="industry-topic-stat-grid"><div className="industry-topic-stat"><strong>{topicDetail.market_evidence?.market_mentions??"—"}</strong><span>mentions in current window</span></div><div className="industry-topic-stat"><strong>{topicDetail.market_evidence?.role_job_count??"—"}</strong><span>role-matched postings</span></div><div className="industry-topic-stat"><strong>{topicDetail.market_evidence?.prevalence_percent!=null?`${Number(topicDetail.market_evidence.prevalence_percent).toFixed(1)}%`:"—"}</strong><span>observed prevalence</span></div><div className="industry-topic-stat"><strong>{topicDetail.market_evidence?.share_change_pp!=null?`${Number(topicDetail.market_evidence.share_change_pp)>0?"+":""}${Number(topicDetail.market_evidence.share_change_pp).toFixed(1)} pp`:"—"}</strong><span>historical movement</span></div><div className="industry-topic-stat"><strong>{topicDetail.market_evidence?.periods_observed??"—"}</strong><span>periods observed</span></div></div><div className="industry-detail-meta"><span>Trend: <strong>{topicDetail.market_evidence?.trend||"—"}</strong></span><span>Sample window: <strong>{topicDetail.market_evidence?.current_window||"Latest complete quarters"}</strong></span><span>O*NET evidence: <strong>{topicDetail.market_evidence?.onet?.records??0} matching technology records</strong></span><span>Evidence source: <strong>FORGE Greenhouse + O*NET</strong></span></div></section>

        <section><div className="industry-topic-section-title">03 · WHERE THE WORLD OF WORK IS MOVING</div><div className="generated-task"><h3 style={{marginTop:0}}>What roles are emerging around this capability?</h3><p>FORGE separates global role signals from occupation-level projections. These sources provide career context; they are not treated as guaranteed forecasts for one technology.</p><div className="industry-topic-grid">{(topicDetail.career_outlook?.global_2030_role_signals||[]).map((x,i)=><div className="industry-topic-list-card" key={`global-${i}`}><small>GLOBAL · {x.horizon}</small><strong>{x.role}</strong><p>{x.signal}</p><span className="industry-resource-note">{x.source}</span></div>)}{(topicDetail.career_outlook?.selected_role_2035||[]).map((x,i)=><div className="industry-topic-list-card" key={`bls-${i}`}><small>U.S. OCCUPATION · {x.horizon}</small><strong>{x.role}</strong><p>{x.growth_percent!=null?`${x.growth_percent}% projected employment change through 2035.`:"Occupation-level projection available."}</p>{x.employment_change_thousands!=null&&<span className="industry-resource-note">{x.employment_change_thousands}k employment change · {x.annual_openings_thousands??"—"}k annual openings</span>}<span className="industry-resource-note">{x.source}</span></div>)}</div></div></section>

        <section><div className="industry-topic-section-title">04 · HOW IT WORKS</div><div className="generated-task"><p>{topicDetail.how_it_works?.summary||""}</p>{Array.isArray(topicDetail.how_it_works?.steps)&&<div className="industry-topic-list">{topicDetail.how_it_works.steps.map((x,i)=><div className="industry-topic-list-card" key={i}><strong>{i+1}. {x.title||x.name||x}</strong><p>{x.description||x.explanation||""}</p></div>)}</div>}</div>{topicDetail.how_it_works?.architecture?.nodes?.length>0&&<div className="industry-arch">{topicDetail.how_it_works.architecture.nodes.map((n,i)=><Fragment key={n.id||i}><div className="industry-arch-node"><strong>{n.label||n.name}</strong>{n.layer&&<span style={{marginLeft:7,color:"rgba(255,255,255,.28)"}}>{n.layer}</span>}</div>{i<topicDetail.how_it_works.architecture.nodes.length-1&&<div className="industry-arch-arrow">↓</div>}</Fragment>)}</div>}</section>

        <section><div className="industry-topic-section-title">05 · CORE CONCEPTS</div><div className="industry-topic-grid">{(topicDetail.key_concepts||[]).map((x,i)=><div className="industry-topic-list-card" key={i}><strong>{x.title||x.name||x.concept}</strong><p>{x.description||x.explanation||""}</p>{x.importance&&<span className="industry-resource-note">{x.importance}</span>}</div>)}</div></section>

        <section><div className="industry-topic-section-title">06 · COMPARISON</div>{topicDetail.section_status?.comparison==="not_applicable"||topicDetail.comparison?.available===false?<div className="industry-resource-empty"><strong>No canonical comparison</strong><span>This topic does not have a directly comparable alternative in the generated knowledge model.</span></div>:<div className="industry-comparison"><table><thead><tr><th>Dimension</th>{(topicDetail.comparison?.columns||[]).map((x,i)=><th key={i}>{x}</th>)}</tr></thead><tbody>{(topicDetail.comparison?.rows||[]).map((r,i)=><tr key={i}><td>{r.dimension}</td>{(r.values||[]).map((v,j)=><td key={j}>{v}</td>)}</tr>)}</tbody></table></div>}</section>

        <section><div className="industry-topic-section-title">07 · PREREQUISITES</div><div className="industry-topic-overview-grid"><div className="generated-task"><small>REQUIRED</small><div className="industry-chip-list">{(topicDetail.prerequisites?.required||[]).map((x,i)=><span key={i}>{x}</span>)}</div></div><div className="generated-task"><small>RECOMMENDED</small><div className="industry-chip-list">{(topicDetail.prerequisites?.recommended||[]).map((x,i)=><span key={i}>{x}</span>)}</div></div></div></section>

        <section><div className="industry-topic-section-title">08 · LEARNING PATH</div><div className="industry-learning-path">{(topicDetail.learning_path||[]).map((x,i)=><div className="assessment-breakdown-card" key={i}><strong>{i+1}. {x.stage||x.level}</strong><small>{x.focus||x.description||""}</small><small style={{marginTop:7}}><b style={{color:"rgba(255,255,255,.62)"}}>Outcome:</b> {x.outcome||""}</small></div>)}</div></section>

        <section><div className="industry-topic-section-title">09 · USE CASES</div><div className="industry-topic-grid">{(topicDetail.use_cases||[]).map((x,i)=><div className="industry-topic-list-card" key={i}><strong>{x.title||x.name||x}</strong><p>{x.description||""}</p></div>)}</div></section>

        <section><div className="industry-topic-section-title">10 · COMMON MISTAKES</div><div className="industry-topic-list">{(topicDetail.common_mistakes||[]).map((x,i)=><div className="industry-topic-list-card" key={i}><strong>✕ {x.mistake||x.title||x}</strong><p><b>Why:</b> {x.why||""}</p><p><b>Fix:</b> {x.fix||""}</p></div>)}</div></section>

        <section><div className="industry-topic-section-title">11 · BUILD A PROJECT</div><div className="generated-task"><small>{topicDetail.project?.title||"Topic project"}</small><h3>{topicDetail.project?.brief||topicDetail.project?.description||"Build a concrete project that demonstrates this capability."}</h3><p><b>Dataset / input:</b> {topicDetail.project?.dataset||"Choose a relevant public or project dataset."}</p><div className="industry-learning-path">{(topicDetail.project?.stages||[]).map((x,i)=><div className="assessment-breakdown-card" key={i}><strong>{i+1}</strong><small>{x}</small></div>)}</div><p><b>Evaluation:</b> {(topicDetail.project?.evaluation||[]).join(" · ")}</p><p><b>Expected output:</b> {topicDetail.project?.expected_output||"A working, measurable demonstration."}</p></div></section>

        <section><div className="industry-topic-section-title">12 · LEARNING RESOURCES</div><div className="industry-resource-note">If a verified embedded video is available, FORGE shows it here. If not, FORGE shows a complete topic article inside this page so the student does not have to leave FORGE to learn.</div><div className="industry-resource-head"><div><h3>Learn · Practice · Demonstrate</h3></div><span>{resourceLoading?"LOADING…":`${currentResources.length} learning resource${currentResources.length===1?"":"s"}`}</span></div>{resourceLoading?<div className="industry-resource-empty">Finding learning resources…</div>:<>{videos.length>0&&<div className="industry-video-stack">{videos.map((video,i)=><div className="industry-video-card" key={`${video.id||video.url}-${i}`}><div className="industry-resource-label"><span>VIDEO {i+1}</span><strong>{video.title||selectedTopic.name}</strong></div><div className="industry-video-frame"><iframe title={video.title||`${selectedTopic.name} learning video`} src={industryVideoEmbed(video)} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen loading="lazy"/></div></div>)}</div>}{articles.length>0&&<div className="industry-article-stack">{articles.map((article,i)=><article className="generated-task industry-inline-article" key={`${article.topic||selectedTopic.name}-article-${i}`}><div className="industry-resource-label"><span>READ INSIDE FORGE</span><strong>{article.title||`Topic guide: ${selectedTopic.name}`}</strong></div><p className="industry-resource-note">{article.note||"Self-contained learning article — no external site required."}</p>{(article.sections||[]).map((section,j)=><div key={j} style={{marginTop:j?18:10}}><h4 style={{margin:"0 0 8px"}}>{section.heading}</h4>{(section.paragraphs||[]).map((paragraph,k)=><p key={k} style={{margin:"0 0 8px",lineHeight:1.7}}>{paragraph}</p>)}{(section.bullets||[]).length>0&&<ul style={{margin:"8px 0 0",paddingLeft:20}}>{section.bullets.map((bullet,k)=><li key={k} style={{marginBottom:7,lineHeight:1.6}}>{bullet}</li>)}</ul>}</div>)}</article>)}</div>}{docs.length>0&&<div className="industry-pdf-stack">{docs.map((doc,i)=><div className="industry-pdf-card" key={`${doc.url}-${i}`}><div><strong>{doc.title||"Reference document"}</strong><span>{doc.source||"Verified source"}</span></div><iframe title={doc.title||`Document ${i+1}`} src={doc.url} loading="lazy"/></div>)}</div>}{links.length>0&&<div className="industry-topic-grid">{links.map((doc,i)=><div className="generated-task" key={`${doc.url}-${i}`}><strong>{doc.title||"Reference"}</strong><p>{doc.source||"Verified source"}</p><a href={doc.url} target="_blank" rel="noreferrer" className="student-option" style={{display:"inline-flex",marginTop:8,textDecoration:"none"}}>Open reference</a></div>)}</div>}{!currentResources.length&&<div className="industry-resource-empty"><strong>No learning resource returned yet.</strong><span>Refresh the topic after restarting the backend.</span></div>}</>}</section>

        <section><div className="industry-topic-section-title">13 · QUICK ASSESSMENT</div>{(topicDetail.assessment?.questions||[]).length>0?<><div className="industry-quiz">{topicDetail.assessment.questions.map((q,i)=><div className="industry-quiz-card" key={i}><small className="assessment-type-badge">{q.type||"TOPIC CHECK"}</small><h4>{i+1}. {q.question||q.prompt}</h4><div className="industry-quiz-options">{(q.options||[]).map((option,j)=><button key={j} className={`industry-quiz-option ${assessmentAnswers[i]===j?"selected":""}`} onClick={()=>!assessmentSubmitted&&setAssessmentAnswers(a=>({...a,[i]:j}))}>{String.fromCharCode(65+j)}. {option}</button>)}</div>{assessmentSubmitted&&<p className="industry-resource-note" style={{marginTop:10}}><b>Explanation:</b> {q.explanation||"Review the underlying concept and failure mode."}</p>}</div>)}</div><div className="industry-action-row" style={{marginTop:12}}><button disabled={assessmentSubmitted||Object.keys(assessmentAnswers).length!==(topicDetail.assessment.questions||[]).length} onClick={submitTopicAssessment}>{assessmentSubmitted?"Assessment submitted":"Submit assessment"}</button></div>{assessmentSubmitted&&<div className="industry-quiz-result"><strong>{assessmentScore}/{topicDetail.assessment.questions.length}</strong><p>{assessmentScore/topicDetail.assessment.questions.length>=0.8?"Demonstrated":"Keep practicing this capability and retake the assessment."}</p></div>}</>:<div className="industry-resource-empty">Assessment is being prepared for this topic. Refresh the topic once if the backend was just restarted.</div>}</section>

        <section><div className="industry-topic-section-title">14 · FUTURE CONTEXT & EVIDENCE</div><div className="industry-source-note"><strong>{topicDetail.future_evidence?.type||"Evidence context"}</strong><span>{topicDetail.future_evidence?.explanation||"Future evidence is kept separate from observed employer demand."}</span></div>{(topicDetail.future_evidence?.items||[]).length>0&&<div className="industry-topic-grid">{topicDetail.future_evidence.items.map((x,i)=><div className="generated-task" key={i}><strong>{x.name||x.title||x.topic||"Evidence"}</strong><p>{x.description||x.reason||""}</p><span className="industry-resource-note">{x.source||"Connected source"}</span></div>)}</div>}<div className="industry-topic-grid">{topicDetail.evidence&&Object.entries(topicDetail.evidence).map(([k,v],i)=><div className="generated-task" key={i}><strong>{k.replaceAll("_"," ")}</strong><p>{Array.isArray(v)?v.join(" · "):String(v)}</p></div>)}</div></section>

        <section><div className="industry-source-note"><strong>FORGE interpretation</strong><span><b>Observed:</b> {topicDetail.market_evidence?.market_mentions??0} of {topicDetail.market_evidence?.role_job_count??0} recent role-matched postings. <b>Future:</b> FORGE does not convert broad WEF/BLS evidence into a technology-specific prediction. <b>Learning:</b> topic content is generated dynamically; market evidence remains authoritative from the connected datasets.</span></div></section>

        <div className="industry-topic-footer"><button className="student-option" onClick={closeTopic}>Back to Pulse</button><button className="student-continue" onClick={()=>addToRoadmap(selectedTopic)}>Add to My Roadmap <ArrowRight size={15}/></button></div>
      </div>}
    </div></div>}
  </div></main></>;
}



const ASK_FORGE_STYLE = `
.ask-forge-page{min-height:100vh;background:#070807;color:#f5f6f4;padding:34px 24px 80px}
.ask-forge-shell{width:min(1180px,100%);margin:0 auto}
.ask-forge-top{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:44px}
.ask-forge-kicker{display:inline-flex;align-items:center;gap:9px;color:rgba(255,255,255,.45);font-size:10px;font-weight:900;letter-spacing:.18em}
.ask-forge-kicker:before{content:"";width:25px;height:1px;background:rgba(255,255,255,.72)}
.ask-forge-title{margin:16px 0 13px;max-width:850px;font-size:clamp(44px,6.5vw,78px);line-height:.94;letter-spacing:-.065em;font-weight:650}
.ask-forge-title em{font-style:normal;color:#7752e8}
.ask-forge-sub{max-width:720px;color:rgba(255,255,255,.5);font-size:14px;line-height:1.75}
.ask-forge-search{margin-top:30px;display:grid;grid-template-columns:1fr auto;gap:8px;padding:9px;border:1px solid rgba(255,255,255,.11);border-radius:18px;background:rgba(255,255,255,.035);box-shadow:0 20px 70px rgba(0,0,0,.25)}
.ask-forge-search input{min-width:0;border:0;outline:0;background:transparent;color:#fff;padding:15px 16px;font:inherit;font-size:14px}
.ask-forge-search input::placeholder{color:rgba(255,255,255,.27)}
.ask-forge-search button{border:0;border-radius:12px;background:#fff;color:#070807;padding:0 20px;font:inherit;font-size:11px;font-weight:900;cursor:pointer}
.ask-forge-search button:disabled{opacity:.3;cursor:not-allowed}
.ask-forge-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.ask-forge-chip{border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.025);color:rgba(255,255,255,.48);border-radius:999px;padding:8px 11px;font:inherit;font-size:9px;cursor:pointer}
.ask-forge-chip:hover{color:#fff;border-color:rgba(255,255,255,.2)}
.ask-forge-tabs{display:flex;gap:7px;flex-wrap:wrap;margin:34px 0 15px}
.ask-forge-tab{border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.025);color:rgba(255,255,255,.48);border-radius:999px;padding:9px 13px;font:inherit;font-size:10px;font-weight:800;cursor:pointer}
.ask-forge-tab.active{background:#fff;color:#070807;border-color:#fff}
.ask-forge-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(300px,.65fr);gap:14px;align-items:start}
.ask-forge-card{border:1px solid rgba(255,255,255,.09);border-radius:22px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018));padding:22px}
.ask-forge-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:15px;margin-bottom:18px}
.ask-forge-label{color:rgba(255,255,255,.38);font-size:8px;font-weight:900;letter-spacing:.16em}
.ask-forge-card h2{margin:7px 0 0;font-size:22px;letter-spacing:-.035em}
.ask-forge-answer{font-size:13px;line-height:1.65;color:rgba(255,255,255,.72);max-height:520px;overflow:auto;padding-right:8px}.forge-answer-content p{margin:0 0 11px}.forge-answer-content h4{margin:0 0 10px;color:#fff;font-size:15px;line-height:1.35}.forge-answer-bullet{display:grid;grid-template-columns:14px 1fr;gap:6px;margin:0 0 8px}.forge-answer-bullet span{color:#9b8cff}.forge-answer-bullet p{margin:0}.ask-forge-step{width:100%;display:grid;grid-template-columns:42px 1fr auto;align-items:center;gap:10px;text-align:left;cursor:pointer}.ask-forge-step.active{border-color:rgba(150,130,255,.5);background:rgba(124,92,255,.08)}.ask-forge-step em{font-style:normal;font-size:9px;color:rgba(255,255,255,.35);letter-spacing:.08em;text-transform:uppercase}.ask-forge-step:hover{border-color:rgba(255,255,255,.2);transform:translateY(-1px)}

.forge-answer-content{
  font-size:15px;
  line-height:1.82;
  color:rgba(255,255,255,.82);
  max-height:720px;
  overflow:auto;
  padding:2px 10px 12px 2px;
}
.forge-answer-content p{margin:0 0 17px}
.forge-answer-content h4{
  margin:22px 0 10px;
  color:#fff;
  font-size:18px;
  line-height:1.35;
  letter-spacing:-.02em;
}
.forge-answer-bullet{
  display:grid;
  grid-template-columns:20px 1fr;
  gap:10px;
  margin:0 0 13px;
}
.forge-answer-bullet span{
  color:#a98cff;
  font-size:20px;
  line-height:1.1;
}
.forge-answer-bullet p{margin:0}
.forge-doubt-diagram{
  margin-top:22px;
  padding:20px;
  border:1px solid rgba(169,140,255,.24);
  border-radius:18px;
  background:
    radial-gradient(circle at 50% 0%,rgba(119,82,232,.13),transparent 55%),
    rgba(255,255,255,.025);
}
.forge-doubt-diagram-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  margin-bottom:18px;
}
.forge-doubt-diagram-head span{
  display:block;
  color:rgba(255,255,255,.34);
  font-size:8px;
  font-weight:900;
  letter-spacing:.15em;
}
.forge-doubt-diagram-head strong{
  display:block;
  margin-top:5px;
  color:#fff;
  font-size:17px;
}
.forge-doubt-diagram-badge{
  padding:7px 10px;
  border-radius:999px;
  border:1px solid rgba(169,140,255,.28);
  background:rgba(119,82,232,.10);
  color:#b8a6ff;
  font-size:8px;
  font-weight:900;
  letter-spacing:.1em;
}
.forge-doubt-diagram-flow{
  display:grid;
  justify-items:center;
  gap:7px;
}
.forge-diagram-node{
  width:min(100%,520px);
  display:grid;
  grid-template-columns:38px 1fr;
  gap:12px;
  align-items:center;
  padding:13px 15px;
  border:1px solid rgba(255,255,255,.09);
  border-radius:14px;
  background:linear-gradient(135deg,rgba(119,82,232,.12),rgba(255,255,255,.025));
  box-shadow:0 10px 30px rgba(0,0,0,.16);
}
.forge-diagram-node b{
  width:34px;
  height:34px;
  display:grid;
  place-items:center;
  border-radius:10px;
  background:rgba(119,82,232,.20);
  color:#b9a8ff;
  font-size:10px;
}
.forge-diagram-node span{
  color:rgba(255,255,255,.78);
  font-size:12px;
  line-height:1.45;
}
.forge-diagram-arrow{
  color:#a98cff;
  font-size:18px;
  line-height:1;
  filter:drop-shadow(0 0 7px rgba(169,140,255,.35));
}
.ask-forge-answer{
  min-height:260px;
  font-size:15px;
}

.ask-forge-topic-summary{display:grid;gap:10px}
.ask-forge-topic-box{padding:15px;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(255,255,255,.022)}
.ask-forge-topic-box strong{display:block;font-size:11px}
.ask-forge-topic-box p{margin:6px 0 0;color:rgba(255,255,255,.46);font-size:10px;line-height:1.65}
.ask-forge-pills{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}
.ask-forge-pills span{padding:7px 9px;border:1px solid rgba(255,255,255,.08);border-radius:999px;color:rgba(255,255,255,.46);font-size:8px}
.ask-forge-video{position:relative;min-height:390px;overflow:hidden;border:1px solid rgba(255,255,255,.09);border-radius:18px;background:radial-gradient(circle at 50% 45%,rgba(119,82,232,.2),transparent 32%),#0b0b0c;display:flex;align-items:center;justify-content:center}
.ask-forge-video-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:36px 36px;opacity:.55}
.ask-forge-orbit{position:absolute;width:180px;height:180px;border:1px solid rgba(119,82,232,.5);border-radius:50%;animation:askForgeSpin 8s linear infinite}
.ask-forge-orbit.two{width:250px;height:92px;transform:rotate(-24deg);animation-duration:10s}
.ask-forge-core{position:relative;z-index:2;width:86px;height:86px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(255,255,255,.35);background:radial-gradient(circle,rgba(119,82,232,.95),rgba(119,82,232,.16) 55%,transparent 72%);box-shadow:0 0 70px rgba(119,82,232,.42);font-size:10px;font-weight:900;letter-spacing:.12em}
.ask-forge-scene{position:absolute;left:18px;right:18px;bottom:17px;z-index:3;padding:11px 13px;border:1px solid rgba(255,255,255,.09);border-radius:12px;background:rgba(7,8,7,.72);backdrop-filter:blur(10px)}
.ask-forge-scene small{display:block;color:rgba(255,255,255,.32);font-size:7px;font-weight:900;letter-spacing:.14em}
.ask-forge-scene strong{display:block;margin-top:5px;font-size:12px}
.ask-forge-scene span{display:block;margin-top:4px;color:rgba(255,255,255,.43);font-size:9px}
@keyframes askForgeSpin{to{transform:rotate(360deg)}}
.ask-forge-step-list{display:grid;gap:8px;margin-top:14px}
.ask-forge-step{display:grid;grid-template-columns:27px 1fr;gap:10px;align-items:start;padding:11px;border:1px solid rgba(255,255,255,.07);border-radius:12px;background:rgba(255,255,255,.018)}
.ask-forge-step b{width:27px;height:27px;border-radius:8px;display:grid;place-items:center;background:rgba(119,82,232,.16);color:#a994ff;font-size:9px}
.ask-forge-step strong{font-size:10px}
.ask-forge-step span{display:block;margin-top:3px;color:rgba(255,255,255,.38);font-size:9px;line-height:1.5}
.ask-forge-input{width:100%;min-height:100px;resize:vertical;box-sizing:border-box;border:1px solid rgba(255,255,255,.09);border-radius:13px;background:rgba(255,255,255,.025);color:#fff;padding:13px;outline:0;font:inherit;font-size:11px;line-height:1.6}
.ask-forge-input:focus{border-color:rgba(119,82,232,.65)}
.ask-forge-action{display:flex;justify-content:flex-end;margin-top:9px}
.ask-forge-action button{display:inline-flex;align-items:center;gap:7px;border:0;border-radius:11px;background:#fff;color:#070807;padding:10px 14px;font:inherit;font-size:10px;font-weight:900;cursor:pointer}
.ask-forge-action button:disabled{opacity:.3;cursor:not-allowed}
.ask-forge-upload{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:9px}
.ask-forge-upload label{display:flex;align-items:center;justify-content:center;gap:7px;min-height:44px;border:1px dashed rgba(255,255,255,.1);border-radius:11px;color:rgba(255,255,255,.42);font-size:9px;cursor:pointer}
.ask-forge-upload label:hover{color:#fff;border-color:rgba(255,255,255,.25)}
.ask-forge-upload input{display:none}
.ask-forge-file{margin-top:9px;padding:9px 11px;border-radius:10px;background:rgba(119,82,232,.08);border:1px solid rgba(119,82,232,.18);color:rgba(255,255,255,.55);font-size:9px}
.ask-forge-summary{display:grid;gap:12px}
.ask-forge-summary textarea{min-height:160px}
.ask-forge-empty{padding:36px 20px;text-align:center;border:1px dashed rgba(255,255,255,.1);border-radius:16px;color:rgba(255,255,255,.35);font-size:11px;line-height:1.7}
.ask-forge-status{margin-top:10px;color:rgba(255,255,255,.35);font-size:9px}

.ask-forge-overview-card{padding:24px}
.ask-forge-overview-heading{margin-top:12px;padding-bottom:17px;border-bottom:1px solid rgba(255,255,255,.07)}
.ask-forge-overview-heading h3{margin:0;font-size:25px;line-height:1.08;letter-spacing:-.04em}
.ask-forge-overview-block{padding:16px 0;border-bottom:1px solid rgba(255,255,255,.065)}
.ask-forge-overview-block:last-child{border-bottom:0;padding-bottom:0}
.ask-forge-overview-block small{display:block;color:rgba(255,255,255,.32);font-size:8px;font-weight:900;letter-spacing:.14em}
.ask-forge-overview-block p{margin:8px 0 0;color:rgba(255,255,255,.58);font-size:10px;line-height:1.75}
.ask-forge-overview-flow{display:grid;gap:7px;margin-top:9px}
.ask-forge-overview-flow-item{display:grid;grid-template-columns:27px 1fr;gap:9px;align-items:center;padding:9px 10px;border:1px solid rgba(255,255,255,.065);border-radius:10px;background:rgba(255,255,255,.018)}
.ask-forge-overview-flow-item b{width:25px;height:25px;display:grid;place-items:center;border-radius:7px;background:rgba(119,82,232,.13);color:#a994ff;font-size:8px}
.ask-forge-overview-flow-item span{color:rgba(255,255,255,.55);font-size:9px;line-height:1.45}
.ask-forge-overview-list{margin:9px 0 0;padding-left:17px;color:rgba(255,255,255,.58);font-size:10px;line-height:1.75}
.ask-forge-overview-list li{margin:5px 0}
.ask-forge-overview-loading{padding:24px 0;color:rgba(255,255,255,.35);font-size:10px;line-height:1.7}
.ask-forge-step-list{display:none}
@media(max-width:900px){.ask-forge-grid{grid-template-columns:1fr}.ask-forge-video{min-height:330px}}
@media(max-width:600px){.ask-forge-page{padding:25px 15px 55px}.ask-forge-top{margin-bottom:30px}.ask-forge-search{grid-template-columns:1fr}.ask-forge-search button{min-height:44px}.ask-forge-upload{grid-template-columns:1fr}.ask-forge-card{padding:17px}.ask-forge-video{min-height:285px}}
/* FINAL ASK FORGE VISUAL PASS */
.ask-forge-page{font-family:Inter,system-ui,sans-serif}.ask-forge-shell{max-width:1240px !important}.ask-forge-mode{padding:7px;border:1px solid rgba(190,145,255,.12);border-radius:16px;background:rgba(255,255,255,.025);box-shadow:inset 0 1px rgba(255,255,255,.04)}.ask-forge-mode button{min-height:42px !important;border-radius:11px !important}.ask-forge-grid{gap:18px !important}.ask-forge-card{min-height:250px}.ask-forge-card h2{font-size:26px !important;letter-spacing:-.035em}.ask-forge-label{color:#bda1e9 !important;letter-spacing:.16em !important}.ask-forge-input{min-height:150px !important;background:rgba(255,255,255,.025) !important;border-color:rgba(190,145,255,.13) !important;border-radius:15px !important}.ask-forge-answer{min-height:230px;background:linear-gradient(145deg,rgba(55,174,232,.045),rgba(145,78,255,.045));border-color:rgba(99,219,255,.14);box-shadow:inset 0 1px rgba(255,255,255,.035)}.ask-forge-overview-card{min-height:420px !important}.ask-forge-overview-block{padding:13px 0;border-bottom:1px solid rgba(100,70,126,.1)}.ask-forge-overview-block:last-child{border-bottom:0}.ask-forge-overview-flow-item{transition:.22s ease}.ask-forge-overview-flow-item:hover{transform:translateX(4px);border-color:rgba(137,87,200,.25) !important}.ask-forge-empty{border:1px dashed rgba(190,145,255,.18) !important;background:rgba(255,255,255,.02);border-radius:16px;padding:35px !important}.ask-forge-upload{gap:9px !important}.ask-forge-action button{min-height:45px;border-radius:12px}.ask-forge-card:has(.ask-forge-input){box-shadow:0 30px 90px rgba(44,8,80,.2),inset 0 1px rgba(255,255,255,.045)}

/* =========================================================
   ASK FORGE — HACKATHON / EVALUATION VISUAL SYSTEM
   Scoped only to the Ask FORGE page.
========================================================= */
.ask-forge-page{
  position:relative;
  isolation:isolate;
  overflow:hidden;
  min-height:100svh !important;
  padding:28px clamp(20px,4vw,64px) 72px !important;
  background:
    radial-gradient(850px 520px at 7% -5%,rgba(150,92,255,.20),transparent 62%),
    radial-gradient(760px 500px at 93% 16%,rgba(70,171,255,.12),transparent 64%),
    radial-gradient(760px 520px at 52% 105%,rgba(216,75,255,.10),transparent 68%),
    linear-gradient(135deg,#0c0818 0%,#130b21 46%,#090815 100%) !important;
}
.ask-forge-page::before{
  content:"";
  position:absolute;
  inset:0;
  z-index:-2;
  pointer-events:none;
  opacity:.62;
  background-image:
    linear-gradient(rgba(183,151,255,.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(183,151,255,.055) 1px,transparent 1px);
  background-size:40px 40px;
  mask-image:linear-gradient(to bottom,#000 0%,rgba(0,0,0,.94) 72%,transparent 100%);
}
.ask-forge-page::after{
  content:"";
  position:absolute;
  width:620px;
  height:620px;
  right:-300px;
  top:120px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(128,76,255,.16),transparent 68%);
  filter:blur(12px);
  z-index:-1;
  pointer-events:none;
}
.ask-forge-shell{
  position:relative;
  z-index:1;
  width:min(1280px,100%) !important;
}
.ask-forge-top{
  min-height:48px;
  margin-bottom:38px !important;
  padding:0 2px 18px;
  border-bottom:1px solid rgba(205,178,255,.11);
}
.ask-forge-top .student-back{
  min-height:38px;
  padding:0 13px !important;
  border:1px solid rgba(202,172,255,.15);
  border-radius:11px;
  background:rgba(255,255,255,.035);
  color:rgba(237,226,252,.72) !important;
  transition:transform .25s ease,border-color .25s ease,background .25s ease,box-shadow .25s ease;
}
.ask-forge-top .student-back:hover{
  transform:translateX(-3px);
  border-color:rgba(193,150,255,.45);
  background:rgba(139,86,255,.10);
  box-shadow:0 10px 28px rgba(76,34,140,.20);
}
.ask-forge-brand-mark{}
.ask-forge-kicker{
  color:rgba(210,184,246,.78) !important;
  font-size:10px !important;
  letter-spacing:.20em !important;
}
.ask-forge-kicker:before{
  width:34px !important;
  background:linear-gradient(90deg,#9c68ff,#6fdcff) !important;
  box-shadow:0 0 14px rgba(143,88,255,.45);
}
.ask-forge-title{
  max-width:980px !important;
  margin:18px 0 14px !important;
  font-size:clamp(48px,6.3vw,82px) !important;
  line-height:.92 !important;
  font-weight:730 !important;
  text-wrap:balance;
  text-shadow:0 18px 55px rgba(0,0,0,.28);
}
.ask-forge-title em{
  color:transparent !important;
  background:linear-gradient(100deg,#e0cbff 0%,#a86cff 45%,#6bdcff 100%);
  -webkit-background-clip:text;
  background-clip:text;
}
.ask-forge-sub{
  max-width:800px !important;
  color:rgba(225,212,241,.68) !important;
  font-size:14px !important;
  line-height:1.8 !important;
}
.ask-forge-search{
  margin-top:31px !important;
  padding:8px !important;
  gap:8px !important;
  border:1px solid rgba(203,174,255,.18) !important;
  border-radius:18px !important;
  background:linear-gradient(135deg,rgba(37,23,59,.74),rgba(12,8,23,.70)) !important;
  box-shadow:inset 0 1px rgba(255,255,255,.045),0 24px 75px rgba(35,12,69,.24) !important;
  backdrop-filter:blur(18px);
}
.ask-forge-search:focus-within{
  border-color:rgba(176,128,255,.55) !important;
  box-shadow:0 0 0 3px rgba(133,83,255,.08),0 25px 80px rgba(47,15,91,.32) !important;
}
.ask-forge-search input{
  min-height:50px;
  color:#fff !important;
  font-size:14px !important;
}
.ask-forge-search input::placeholder{color:rgba(221,205,240,.36) !important}
.ask-forge-search button{
  min-height:50px;
  padding:0 23px !important;
  border:1px solid rgba(227,211,255,.18) !important;
  border-radius:13px !important;
  background:linear-gradient(135deg,#f1e9ff,#c9b0ff) !important;
  color:#171021 !important;
  box-shadow:0 10px 30px rgba(135,79,215,.22);
  transition:transform .22s ease,box-shadow .22s ease,filter .22s ease;
}
.ask-forge-search button:hover:not(:disabled){
  transform:translateY(-2px);
  filter:brightness(1.04);
  box-shadow:0 15px 36px rgba(135,79,215,.34);
}
.ask-forge-chips{
  gap:9px !important;
  margin-top:13px !important;
}
.ask-forge-chip{
  min-height:34px;
  padding:8px 12px !important;
  border-color:rgba(198,166,247,.14) !important;
  background:rgba(255,255,255,.026) !important;
  color:rgba(225,211,241,.58) !important;
  transition:transform .2s ease,border-color .2s ease,background .2s ease,color .2s ease;
}
.ask-forge-chip:nth-child(3n+1){border-color:rgba(145,100,255,.20) !important}
.ask-forge-chip:nth-child(3n+2){border-color:rgba(81,193,255,.18) !important}
.ask-forge-chip:nth-child(3n){border-color:rgba(224,102,255,.18) !important}
.ask-forge-chip:hover{
  transform:translateY(-3px);
  color:#fff !important;
  border-color:rgba(202,165,255,.48) !important;
  background:rgba(139,84,255,.10) !important;
  box-shadow:0 9px 24px rgba(73,30,129,.20);
}
.ask-forge-tabs{
  position:relative;
  display:inline-flex !important;
  align-items:center;
  gap:7px !important;
  margin:34px 0 20px !important;
  padding:6px;
  border:1px solid rgba(198,164,247,.14);
  border-radius:16px;
  background:rgba(20,12,34,.74);
  box-shadow:inset 0 1px rgba(255,255,255,.035),0 12px 35px rgba(24,7,48,.18);
}
.ask-forge-tab{
  position:relative;
  min-height:43px;
  padding:10px 17px !important;
  border:1px solid transparent !important;
  border-radius:11px !important;
  background:transparent !important;
  color:rgba(224,208,242,.52) !important;
  font-size:11px !important;
  font-weight:850 !important;
  transition:transform .22s ease,color .22s ease,background .22s ease,border-color .22s ease,box-shadow .22s ease;
}
.ask-forge-tab:hover{
  transform:translateY(-2px);
  color:#fff !important;
  background:rgba(142,89,255,.09) !important;
}
.ask-forge-tab.active{
  color:#fff !important;
  border-color:rgba(190,150,255,.36) !important;
  background:linear-gradient(135deg,rgba(131,78,224,.72),rgba(67,171,232,.40)) !important;
  box-shadow:0 9px 28px rgba(92,41,166,.28),inset 0 1px rgba(255,255,255,.13);
}
.ask-forge-tab.active::after{
  content:"";
  position:absolute;
  left:18%;
  right:18%;
  bottom:-4px;
  height:2px;
  border-radius:99px;
  background:linear-gradient(90deg,#b16cff,#6bdcff);
  box-shadow:0 0 12px rgba(140,91,255,.75);
}
.ask-forge-grid{
  grid-template-columns:minmax(0,1.38fr) minmax(350px,.62fr) !important;
  gap:22px !important;
  align-items:stretch !important;
}
.ask-forge-card{
  position:relative;
  min-height:330px !important;
  padding:27px !important;
  border:1px solid rgba(199,167,247,.16) !important;
  border-radius:24px !important;
  background:
    radial-gradient(500px 220px at 0% 0%,rgba(126,76,224,.12),transparent 70%),
    linear-gradient(145deg,rgba(35,21,55,.72),rgba(13,9,24,.88)) !important;
  box-shadow:inset 0 1px rgba(255,255,255,.045),0 25px 75px rgba(25,7,48,.24);
  overflow:hidden;
  animation:askForgeSectionIn .55s cubic-bezier(.2,.8,.2,1) both;
}
.ask-forge-grid > *:nth-child(2){animation-delay:.08s}
.ask-forge-card::before{
  content:"";
  position:absolute;
  left:24px;
  right:24px;
  top:0;
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(190,145,255,.62),transparent);
  opacity:.75;
}
.ask-forge-card-head{
  margin-bottom:21px !important;
}
.ask-forge-label{
  color:#c4a5ff !important;
  font-size:9px !important;
  letter-spacing:.18em !important;
}
.ask-forge-card h2{
  margin-top:9px !important;
  font-size:clamp(25px,3vw,35px) !important;
  color:#fff !important;
}
.ask-forge-card h2::after{
  content:"";
  display:block;
  width:44px;
  height:2px;
  margin-top:11px;
  border-radius:99px;
  background:linear-gradient(90deg,#9e64ff,#69d8ff);
  box-shadow:0 0 12px rgba(147,91,255,.42);
}
.ask-forge-empty{
  min-height:220px;
  display:grid;
  place-items:center;
  border:1px dashed rgba(196,163,248,.20) !important;
  background:
    radial-gradient(circle at 50% 35%,rgba(134,79,255,.10),transparent 42%),
    rgba(255,255,255,.018) !important;
  color:rgba(221,207,238,.50) !important;
  animation:askForgeBreath 3s ease-in-out infinite;
}
.ask-forge-visual-stage{
  position:relative;
  min-height:430px;
  margin-top:4px;
  padding:12px;
  border:1px solid rgba(190,149,255,.13);
  border-radius:19px;
  background:
    radial-gradient(500px 280px at 50% 0%,rgba(122,72,255,.12),transparent 70%),
    rgba(7,5,15,.34);
  overflow:hidden;
}
.ask-forge-visual-stage.is-pending{
  border-color:rgba(164,112,255,.27);
  box-shadow:inset 0 0 70px rgba(119,70,240,.06),0 15px 45px rgba(45,15,89,.16);
}
.ask-forge-visual-stage.is-ready{
  border-color:rgba(112,207,255,.18);
  box-shadow:inset 0 0 80px rgba(77,178,255,.035),0 18px 60px rgba(44,16,87,.18);
}
.ask-forge-stage-hud{
  position:absolute;
  z-index:8;
  top:20px;
  right:20px;
  display:inline-flex;
  align-items:center;
  gap:7px;
  padding:7px 10px;
  border:1px solid rgba(195,162,249,.16);
  border-radius:999px;
  background:rgba(12,8,24,.70);
  backdrop-filter:blur(12px);
  color:rgba(220,204,240,.54);
  font-size:8px;
  font-weight:900;
  letter-spacing:.13em;
}
.ask-forge-stage-dot{
  width:6px;
  height:6px;
  border-radius:50%;
  background:#8d63ff;
  box-shadow:0 0 10px #8d63ff;
  animation:askForgePulse 1.6s ease-in-out infinite;
}
.is-ready .ask-forge-stage-dot{
  background:#68d9ff;
  box-shadow:0 0 10px #68d9ff;
}
.ask-forge-stage-placeholder{
  min-height:390px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:9px;
  text-align:center;
  padding:60px 25px 35px;
}
.ask-forge-stage-orb{
  width:68px;
  height:68px;
  display:grid;
  place-items:center;
  border:1px solid rgba(183,139,255,.28);
  border-radius:22px;
  color:#c9aaff;
  background:radial-gradient(circle,rgba(137,81,255,.28),rgba(46,26,76,.20) 58%,transparent 72%);
  box-shadow:0 0 42px rgba(123,68,238,.18);
  animation:askForgeFloat 3s ease-in-out infinite;
}
.ask-forge-stage-placeholder strong{
  color:#fff;
  font-size:16px;
}
.ask-forge-stage-placeholder span{
  max-width:440px;
  color:rgba(215,201,234,.45);
  font-size:10px;
  line-height:1.7;
}
.ask-forge-stage-loading{
  position:absolute;
  inset:80px 35px 35px;
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:13px;
  opacity:.75;
}
.ask-forge-stage-loading span{
  min-height:105px;
  border-radius:15px;
  border:1px solid rgba(188,145,255,.10);
  background:linear-gradient(110deg,rgba(255,255,255,.025),rgba(143,88,255,.09),rgba(255,255,255,.025));
  background-size:220% 100%;
  animation:askForgeShimmer 1.7s ease-in-out infinite;
}
.ask-forge-stage-loading span:nth-child(2){animation-delay:.18s}
.ask-forge-stage-loading span:nth-child(3){animation-delay:.36s}
.ask-forge-stage-loading span:nth-child(4){animation-delay:.54s}

/* Notebook-style overview: intentionally brighter so the explanation reads
   like a real study note rather than another dark dashboard card. */
.ask-forge-overview-card{
  min-height:100% !important;
  padding:29px 27px 31px !important;
  color:#20172c !important;
  border-color:rgba(213,190,245,.55) !important;
  background:
    repeating-linear-gradient(to bottom,rgba(111,100,128,.09) 0,rgba(111,100,128,.09) 1px,transparent 1px,transparent 31px),
    linear-gradient(90deg,transparent 0 46px,rgba(231,104,145,.18) 46px 47px,transparent 47px),
    linear-gradient(145deg,#fbf7ff,#eee8f8) !important;
  box-shadow:0 25px 65px rgba(28,10,47,.28),inset 0 1px rgba(255,255,255,.85) !important;
  transform:rotate(.25deg);
  transform-origin:center top;
}
.ask-forge-overview-card::before{
  left:0;
  right:0;
  height:2px;
  background:linear-gradient(90deg,transparent,rgba(151,95,205,.45),transparent);
  opacity:1;
}
.ask-forge-overview-card::after{
  content:"";
  position:absolute;
  top:22px;
  right:22px;
  width:8px;
  height:8px;
  border-radius:50%;
  background:#a26cff;
  box-shadow:0 0 0 5px rgba(162,108,255,.10),0 0 18px rgba(162,108,255,.45);
}
.ask-forge-overview-card .ask-forge-label{
  color:#76519e !important;
}
.ask-forge-overview-heading{
  margin-top:13px !important;
  padding-bottom:19px !important;
  border-bottom:1px solid rgba(79,61,96,.16) !important;
}
.ask-forge-overview-heading h3{
  color:#24182f !important;
  font-size:27px !important;
}
.ask-forge-overview-block{
  padding:17px 5px 16px 20px !important;
  border-bottom:1px solid rgba(79,61,96,.13) !important;
}
.ask-forge-overview-block small{
  color:#866ba1 !important;
}
.ask-forge-overview-block p{
  color:#4e405b !important;
  font-size:11px !important;
  line-height:1.8 !important;
}
.ask-forge-overview-flow-item{
  border-color:rgba(89,67,108,.13) !important;
  background:rgba(255,255,255,.40) !important;
  transition:transform .22s ease,box-shadow .22s ease,background .22s ease !important;
}
.ask-forge-overview-flow-item:hover{
  transform:translateX(5px) !important;
  background:rgba(255,255,255,.72) !important;
  box-shadow:0 8px 22px rgba(64,36,83,.10);
}
.ask-forge-overview-flow-item b{
  background:linear-gradient(135deg,#8660c8,#62b9db) !important;
  color:#fff !important;
  box-shadow:0 5px 14px rgba(102,72,155,.18);
}
.ask-forge-overview-flow-item span{
  color:#4c3d58 !important;
}
.ask-forge-overview-list{
  color:#4c3d58 !important;
}
.ask-forge-overview-list li::marker{color:#9a68d7}
.ask-forge-overview-loading{
  min-height:310px;
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
  padding:30px !important;
  color:#766584 !important;
  background:
    repeating-linear-gradient(to bottom,rgba(111,100,128,.08) 0,rgba(111,100,128,.08) 1px,transparent 1px,transparent 31px);
  animation:askForgeNotebookPulse 2.8s ease-in-out infinite;
}
.ask-forge-topic-summary{
  min-width:0;
  animation:askForgeNotebookIn .7s cubic-bezier(.2,.8,.2,1) both;
}

/* Doubt / video modes use distinct surfaces so the direction is immediately clear. */
.ask-forge-card:has(.ask-forge-input){
  background:
    radial-gradient(500px 250px at 0% 0%,rgba(82,172,255,.10),transparent 68%),
    linear-gradient(145deg,rgba(22,34,55,.72),rgba(12,9,24,.90)) !important;
}
.ask-forge-card:has(.ask-forge-answer){
  background:
    radial-gradient(500px 260px at 100% 0%,rgba(188,82,255,.13),transparent 68%),
    linear-gradient(145deg,rgba(42,22,64,.72),rgba(12,8,23,.90)) !important;
}
.ask-forge-upload label{
  min-height:52px !important;
  border-color:rgba(191,153,247,.18) !important;
  background:rgba(255,255,255,.025);
  transition:transform .2s ease,border-color .2s ease,background .2s ease,color .2s ease;
}
.ask-forge-upload label:hover{
  transform:translateY(-3px);
  color:#fff !important;
  border-color:rgba(190,147,255,.48) !important;
  background:rgba(135,83,230,.09);
}
.ask-forge-action button{
  min-height:47px !important;
  padding:0 18px !important;
  border:1px solid rgba(225,206,255,.16) !important;
  border-radius:13px !important;
  background:linear-gradient(135deg,#eee5ff,#c7afff) !important;
  color:#1a1025 !important;
  box-shadow:0 12px 30px rgba(122,69,190,.24);
  transition:transform .22s ease,box-shadow .22s ease;
}
.ask-forge-action button:hover:not(:disabled){
  transform:translateY(-3px);
  box-shadow:0 17px 38px rgba(122,69,190,.34);
}
.ask-forge-file{
  border-color:rgba(110,213,255,.18) !important;
  background:linear-gradient(135deg,rgba(73,187,239,.07),rgba(136,76,255,.08)) !important;
}
.ask-forge-answer{
  border:1px solid rgba(135,95,214,.18);
  border-radius:16px;
  padding:18px !important;
  background:rgba(7,5,15,.32) !important;
}

/* Bottom navigation feels like a deliberate product hand-off, not footer text. */
.ask-forge-page .student-bottom{
  margin-top:38px !important;
  padding:22px 0 0 !important;
  border-top:1px solid rgba(204,176,247,.12) !important;
}
.ask-forge-page .student-bottom .student-option,
.ask-forge-page .student-bottom .student-continue{
  min-height:42px;
}
@keyframes askForgeSectionIn{
  from{opacity:0;transform:translateY(18px)}
  to{opacity:1;transform:translateY(0)}
}
@keyframes askForgeNotebookIn{
  from{opacity:0;transform:translateX(20px) rotate(1.5deg)}
  to{opacity:1;transform:translateX(0) rotate(.25deg)}
}
@keyframes askForgeBreath{
  0%,100%{box-shadow:inset 0 0 35px rgba(129,77,238,.035)}
  50%{box-shadow:inset 0 0 70px rgba(129,77,238,.10)}
}
@keyframes askForgeNotebookPulse{
  0%,100%{opacity:.60}
  50%{opacity:1}
}
@keyframes askForgePulse{
  0%,100%{opacity:.55;transform:scale(.8)}
  50%{opacity:1;transform:scale(1.25)}
}
@keyframes askForgeFloat{
  0%,100%{transform:translateY(0) rotate(-1deg)}
  50%{transform:translateY(-7px) rotate(1deg)}
}
@keyframes askForgeShimmer{
  0%{background-position:200% 0}
  100%{background-position:-20% 0}
}
@media(max-width:900px){
  .ask-forge-grid{grid-template-columns:1fr !important}
  .ask-forge-overview-card{min-height:520px !important}
}
@media(max-width:620px){
  .ask-forge-page{padding:22px 15px 48px !important}
  .ask-forge-top{margin-bottom:28px !important}
  .ask-forge-title{font-size:clamp(42px,12vw,60px) !important}
  .ask-forge-tabs{display:flex !important;width:100%;overflow:auto}
  .ask-forge-tab{flex:1 0 auto}
  .ask-forge-visual-stage{min-height:360px}
  .ask-forge-stage-loading{inset:70px 20px 25px}
  .ask-forge-stage-placeholder{min-height:320px}
  .ask-forge-overview-card{transform:none}
}
`;


function AskForgeStyles(){return <style>{ASK_FORGE_STYLE}{`
@keyframes spin{to{transform:rotate(360deg)}}
.forge-native-video-shell{width:100%}
.forge-native-video{aspect-ratio:16/9;object-fit:contain}
`}</style>}



function buildForgeAnimatedLesson(topic, topicName, howItWorks, coreConcepts){
  const sourceItems = Array.isArray(howItWorks) && howItWorks.length
    ? howItWorks
    : (Array.isArray(coreConcepts) ? coreConcepts : []);

  const cleanItems = sourceItems.length
    ? sourceItems
    : [
        {title:"Core idea", description:"Understand the central idea before moving into the process."},
        {title:"How it works", description:"Follow the main flow step by step."},
        {title:"Practical application", description:"Connect the concept to a concrete technical use case."},
        {title:"Check understanding", description:"Review the concept and test your understanding."}
      ];

  const labelOf = (item, fallback) =>
    typeof item === "string"
      ? item
      : item?.title || item?.name || item?.step || fallback;

  const descriptionOf = (item) =>
    typeof item === "string"
      ? `FORGE explains ${item} and shows how it connects to the overall concept.`
      : item?.description || item?.explanation || item?.details ||
        `FORGE explains ${labelOf(item,"this step")} and connects it to the topic.`;

  const scenes = cleanItems.slice(0, 6).map((item, index, arr) => {
    const current = labelOf(item, `Step ${index + 1}`);
    const previous = index > 0 ? labelOf(arr[index - 1], "Previous step") : "Start";
    const next = index < arr.length - 1 ? labelOf(arr[index + 1], "Next step") : "Outcome";

    return {
      id:`forge-scene-${index + 1}`,
      title:current,
      narration:descriptionOf(item),
      duration:Math.max(4, Math.min(8, 4 + current.length / 30)),
      elements:[
        {type:"text",x:50,y:10,text:topicName,emphasis:true},
        {type:"box",id:"source",x:18,y:48,width:24,height:16,label:previous,tone:"input"},
        {type:"arrow",from:"source",to:"focus"},
        {type:"box",id:"focus",x:50,y:48,width:30,height:18,label:current,tone:"default"},
        {type:"arrow",from:"focus",to:"outcome"},
        {type:"box",id:"outcome",x:82,y:48,width:24,height:16,label:next,tone:"output"},
        {type:"pulse",x:50,y:48},
        {type:"text",x:50,y:72,text:`Step ${index + 1} · ${arr.length} in this lesson`},
        {type:"equation",x:50,y:86,text:"Understand → Apply"}
      ]
    };
  });

  return {
    title:`${topicName} · Animated Lesson`,
    topic:topic?.topic||topicName,
    scenes
  };
}

function ForgeAnswerView({text}){
  const lines=String(text||"").split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  return <div className="forge-answer-content">{lines.map((line,i)=>{
    const clean=line
      .replace(/^#{1,6}\s*/,"")
      .replace(/\*\*(.*?)\*\*/g,"$1")
      .replace(/`([^`]+)`/g,"$1");

    if(/^[-*]\s+/.test(line)||/^\d+[.)]\s+/.test(line)){
      return <div className="forge-answer-bullet" key={i}>
        <span>•</span>
        <p>{clean.replace(/^[-*]\s+/,"").replace(/^\d+[.)]\s+/,"")}</p>
      </div>;
    }

    if(/^#{1,6}\s+/.test(line)||(/^[A-Z][^.!?]{2,70}$/.test(clean)&&i>0)){
      return <h4 key={i}>{clean}</h4>;
    }

    return <p key={i}>{clean}</p>;
  })}</div>;
}

function ForgeDoubtDiagram({steps}){
  if(!Array.isArray(steps)||steps.length<2)return null;
  return <div className="forge-doubt-diagram">
    <div className="forge-doubt-diagram-head">
      <div>
        <span>FORGE VISUAL EXPLANATION</span>
        <strong>Concept flow</strong>
      </div>
      <div className="forge-doubt-diagram-badge">STEP-BY-STEP</div>
    </div>

    <div className="forge-doubt-diagram-flow">
      {steps.map((step,i)=><Fragment key={`${step}-${i}`}>
        <div className="forge-diagram-node">
          <b>{String(i+1).padStart(2,"0")}</b>
          <span>{step}</span>
        </div>
        {i<steps.length-1&&<div className="forge-diagram-arrow" aria-hidden="true">↓</div>}
      </Fragment>)}
    </div>
  </div>;
}

function extractForgeLessonJSON(raw){
  const text=String(raw||"").trim();
  const candidates=[
    text,
    text.replace(/^```(?:json)?\s*/i,"").replace(/\s*```$/i,"").trim()
  ];

  // Also extract the first balanced JSON object from a response that contains prose.
  let depth=0, start=-1, inString=false, escaped=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(inString){
      if(escaped){escaped=false;continue;}
      if(ch==="\\"){escaped=true;continue;}
      if(ch==='"')inString=false;
      continue;
    }
    if(ch==='"'){inString=true;continue;}
    if(ch==="{"){
      if(depth===0)start=i;
      depth++;
    }else if(ch==="}"&&depth>0){
      depth--;
      if(depth===0&&start>=0){
        candidates.push(text.slice(start,i+1));
        start=-1;
      }
    }
  }

  for(const candidate of candidates){
    try{
      const parsed=JSON.parse(candidate);
      if(parsed&&Array.isArray(parsed.scenes))return parsed;
    }catch{}
  }
  return null;
}

function StudentAskForge(){
  const navigate=useNavigate();
  const [mode,setMode]=useState("topic");
  const [query,setQuery]=useState("");
  const [topic,setTopic]=useState(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");
  const [doubt,setDoubt]=useState("");
  const [answer,setAnswer]=useState("");
  const [answerLoading,setAnswerLoading]=useState(false);
  const [file,setFile]=useState(null);
  const [videoFile,setVideoFile]=useState(null);
  const [videoSummaryPrompt,setVideoSummaryPrompt]=useState("");
  const [videoSummary,setVideoSummary]=useState("");
  const [videoLoading,setVideoLoading]=useState(false);
  const [lessonStep,setLessonStep]=useState(0);
  const [animatedLesson,setAnimatedLesson]=useState(null);
  const [lessonLoading,setLessonLoading]=useState(false);
  const [lessonProgress,setLessonProgress]=useState(0);
  const [lessonMessage,setLessonMessage]=useState("");
  const [diagramSteps,setDiagramSteps]=useState([]);
  const [nativeLesson,setNativeLesson]=useState(null);

  const profile=readS("forge_student_profile",{});
  const subjects=readS("forge_student_subjects",[]);
  const scores=readS("forge_student_scores",{});
  const roadmap=readS("forge_student_roadmap",{});

  const targetRole=profile?.targetRole||"Student";
  const topicName=topic?.topic||topic?.name||query.trim()||"Your topic";
  const overview=topic?.overview||{};
  const howItWorks=Array.isArray(topic?.how_it_works)?topic.how_it_works:[];
  const coreConcepts=Array.isArray(topic?.core_concepts)?topic.core_concepts:[];
  const learningPath=Array.isArray(topic?.learning_path)?topic.learning_path:[];
  const market=topic?.market_evidence||{};

  const sceneSteps=howItWorks.length?howItWorks:coreConcepts.length?coreConcepts:[
    "Understand the core idea",
    "See how the concept works",
    "Apply it to a practical example",
    "Practice and verify your understanding"
  ];

  // Native browser Visual Learn: no Manim/MP4 rendering.
  const generateAnimatedLesson=async(detail, q)=>{
    setLessonLoading(false);
    setAnimatedLesson(null);
    setLessonStep(0);
    setLessonProgress(0);
    setLessonMessage("Native browser visual lesson ready.");
    return { topic:q, native:true };
  };

  const searchTopic=async(value=query)=>{
    const q=String(value||"").trim();
    if(!q)return;
    setQuery(q);
    setLoading(true);
    setError("");
    setAnswer("");
    setNativeLesson(null);
    try{
      const params=new URLSearchParams({role:targetRole,topic:q,horizon:"5y"});
      const response=await fetch(`${FORGE_API_BASE}/api/student/industry-topic?${params.toString()}`);
      if(!response.ok)throw new Error(`Topic Intelligence API returned ${response.status}`);
      const data=await response.json();
      const detail=(data?.topic_intelligence&&typeof data.topic_intelligence==="object")
        ? data.topic_intelligence
        : (data?.intelligence&&typeof data.intelligence==="object")
          ? data.intelligence
          : data;
      if(!detail||typeof detail!=="object")throw new Error("FORGE returned no topic intelligence.");
      setTopic(detail);
      setLessonStep(0);
      sessionStorage.setItem("forge_student_ask_topic",JSON.stringify(detail));
    }catch(err){
      setTopic(null);
      setError(err?.message||"Unable to load this topic.");
    }finally{
      setLoading(false);
    }
  };

  const askDoubt=async()=>{
    const q=doubt.trim();
    if(!q && !file)return;

    setAnswerLoading(true);
    setAnswer("");
    setDiagramSteps([]);

    const wantsDiagram=/\b(diagram|draw|visual|flowchart|figure|illustrate|show|explain this image|answer this image)\b/i.test(q);

    try{
      let response;

      /*
       * IMPORTANT:
       * Do NOT send an uploaded image/PDF to /api/assistant/chat.
       * /chat receives JSON text only.
       *
       * Image -> /vision
       * PDF   -> /document
       * Text  -> /chat
       */
      if(file && file.type.startsWith("image/")){
        const form=new FormData();
        form.append("file",file);
        form.append(
          "prompt",
          `${q || "Analyze this image carefully and answer what it is asking."}

You are FORGE's visual study tutor.
Actually inspect the uploaded image. Do NOT say that you cannot see the image.
If the image contains a question, solve the question.
If it contains a diagram, explain the diagram and what every important part means.
If it contains code, explain the code and its output/logic.
If it contains a table, read the relevant values before answering.

Give a complete student-friendly explanation.
Use the visible content of the image as the primary source.
${wantsDiagram ? `
Also create a simple concept flow at the end using exactly:
DIAGRAM_STEPS: step 1 | step 2 | step 3 | step 4
` : `
If a diagram would genuinely improve understanding, include:
DIAGRAM_STEPS: step 1 | step 2 | step 3
`}`
        );
        form.append("page","Ask FORGE · Image");
        form.append("role",targetRole||"");
        form.append("topic",topicName||"");

        response=await fetch(`${FORGE_API_BASE}/api/assistant/vision`,{
          method:"POST",
          body:form
        });

      }else if(file && (file.type==="application/pdf" || file.name.toLowerCase().endsWith(".pdf"))){
        const form=new FormData();
        form.append("file",file);
        form.append(
          "prompt",
          `${q || "Read the uploaded PDF and explain the important question/concept clearly."}

Answer from the uploaded PDF itself.
If there is a question, solve it.
If there is a diagram, explain the diagram.
Mention page numbers where useful.
Do not merely summarize the filename or say the PDF cannot be seen.
${wantsDiagram ? `
End with exactly:
DIAGRAM_STEPS: step 1 | step 2 | step 3 | step 4
` : ""}`
        );
        form.append("role",targetRole||"");
        form.append("topic",topicName||"");
        form.append("max_words","700");

        response=await fetch(`${FORGE_API_BASE}/api/assistant/document`,{
          method:"POST",
          body:form
        });

      }else{
        response=await fetch(`${FORGE_API_BASE}/api/assistant/chat`,{
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body:JSON.stringify({
            message:`You are FORGE's student tutor.

Current topic: ${topicName||"General study"}
Student question: ${q}

Answer the student's actual question completely.
- Maximum 500 words.
- Use simple student-friendly language.
- Match the student's language; use Hinglish when the student uses Hinglish.
- Start with a direct answer.
- Use clear headings and bullets where useful.
- Include an example when useful.
- If the student asks for a diagram/flowchart/visual, explain it and end with:
DIAGRAM_STEPS: step 1 | step 2 | step 3 | step 4
- Do not give generic career advice or unrelated resources.`,
            history:[],
            page:"Ask FORGE",
            role:targetRole,
            topic:topicName
          })
        });
      }

      const raw=await response.text();
      let data={};
      try{data=JSON.parse(raw)}catch{}

      if(!response.ok){
        throw new Error(data?.detail||data?.message||raw||`FORGE returned ${response.status}`);
      }

      let clean=String(
        data?.assistant?.message ||
        data?.message ||
        data?.response ||
        data?.answer ||
        ""
      ).trim();

      if(!clean){
        throw new Error("FORGE received the file but returned an empty explanation.");
      }

      const diagramMatch=clean.match(/(?:^|\n)\s*DIAGRAM_STEPS:\s*(.+)$/im);
      if(diagramMatch){
        const parsed=diagramMatch[1]
          .split("|")
          .map(x=>x.trim())
          .filter(Boolean)
          .slice(0,6);
        setDiagramSteps(parsed);
        clean=clean.replace(diagramMatch[0],"").trim();
      }

      clean=clean
        .replace(/^\s*#{1,6}\s*/gm,"")
        .replace(/\n{3,}/g,"\n\n")
        .trim();

      setAnswer(clean);

    }catch(err){
      setAnswer(
        `FORGE could not analyze the uploaded material right now.\n\n${err?.message||"Please try again."}`
      );
    }finally{
      setAnswerLoading(false);
    }
  };
  const summarizeVideo=async()=>{
    if(!videoSummaryPrompt.trim()&&!videoFile)return;
    setVideoLoading(true);
    setVideoSummary("");
    try{
      if(!videoFile){
        setVideoSummary("Add the lecture/video file first. FORGE will use its transcript as the source for the summary.");
        return;
      }
      setVideoSummary("Video selected successfully. The summarization pipeline is ready for transcript extraction; the current backend does not yet expose a video-to-transcript endpoint, so FORGE will not invent a summary from the filename alone.");
    }finally{
      setVideoLoading(false);
    }
  };

  return <>
    <AskForgeStyles/>
    <main className="ask-forge-page">
      <div className="ask-forge-shell">
        <div className="ask-forge-top">
          <button className="student-back" onClick={()=>navigate("/student/industry")}><ChevronLeft size={15}/>Industry Pulse</button>
          <div className="student-brand-mini"><strong>FORGE</strong><span>ASK FORGE</span></div>
          <div className="student-progress-label">AI LEARNING</div>
        </div>

        <div className="ask-forge-kicker">ASK FORGE · VISUAL LEARNING ENGINE</div>
        <h1 className="ask-forge-title">Clarify. <em>Visualize.</em><br/>Understand.</h1>
        <p className="ask-forge-sub">Search any technical topic and FORGE turns the topic intelligence into a visual study experience. Ask a doubt, inspect the concept, or prepare a lecture for summarization.</p>

        <div className="ask-forge-search">
          <input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();searchTopic()}}} placeholder="Search a topic — e.g. Backpropagation, TCP 3-way handshake, React hooks..." />
          <button onClick={()=>searchTopic()} disabled={!query.trim()||loading}>{loading?"Building…":"Learn topic"}</button>
        </div>
        <div className="ask-forge-chips">
          {["Backpropagation","Binary Search","TCP 3-way handshake","React Hooks","B-Tree Indexing","Transformers"].map(x=><button className="ask-forge-chip" key={x} onClick={()=>{setQuery(x);searchTopic(x)}}>{x}</button>)}
        </div>

        <div className="ask-forge-tabs">
          <button className={`ask-forge-tab ${mode==="topic"?"active":""}`} onClick={()=>setMode("topic")}>Visual Learn</button>
          <button className={`ask-forge-tab ${mode==="doubt"?"active":""}`} onClick={()=>setMode("doubt")}>Ask a Doubt</button>
          <button className={`ask-forge-tab ${mode==="video"?"active":""}`} onClick={()=>setMode("video")}>Summarize Video</button>
        </div>

        {mode==="topic"&&<div className="ask-forge-grid">
          <section className="ask-forge-card">
            <div className="ask-forge-card-head">
              <div><div className="ask-forge-label">FORGE · FULL VISUAL EXPLANATION</div><h2>{topicName}</h2></div>
              {topic&&<span className="assessment-type-badge">FORGE TOPIC INTELLIGENCE</span>}
            </div>
            {!topic&&!loading&&!error&&<div className="ask-forge-empty">Search a topic above. FORGE will fetch the evidence-backed Topic Intelligence workspace and build a visual explanation from the returned structure.</div>}
            {loading&&<div className="ask-forge-empty">Building visual explanation from FORGE Topic Intelligence…</div>}
            {error&&<div className="ask-forge-empty">{error}</div>}
            <div className={`ask-forge-visual-stage ${topic ? (nativeLesson ? "is-ready" : "is-pending") : "is-empty"}`}>
              <div className="ask-forge-stage-hud" aria-hidden="true">
                <span className="ask-forge-stage-dot"/>
                <span>{topic ? (nativeLesson ? "VISUAL LESSON READY" : "BUILDING VISUAL LESSON") : "AWAITING TOPIC"}</span>
              </div>
              {topic&&(
                <NativeVisualLearn
                  topic={topicName}
                  difficulty={topic?.difficulty||topic?.overview?.difficulty||"intermediate"}
                  onLessonReady={setNativeLesson}
                />
              )}
              {!topic&&!loading&&!error&&(
                <div className="ask-forge-stage-placeholder">
                  <div className="ask-forge-stage-orb"><Sparkles size={22}/></div>
                  <strong>Choose a concept to begin</strong>
                  <span>FORGE will turn the selected topic into a visual, evidence-backed study lesson.</span>
                </div>
              )}
              {loading&&(
                <div className="ask-forge-stage-loading" aria-hidden="true">
                  <span/><span/><span/><span/>
                </div>
              )}
            </div>
          </section>

          <aside className="ask-forge-topic-summary">
            <div className="ask-forge-card ask-forge-overview-card">
              <div className="ask-forge-label">TOPIC OVERVIEW</div>

              <div className="ask-forge-overview-heading">
                <h3>{nativeLesson?.overview?.title||nativeLesson?.title||topicName}</h3>
              </div>

              {nativeLesson?.overview ? (
                <>
                  <div className="ask-forge-overview-block">
                    <small>WHAT IT IS</small>
                    <p>{nativeLesson.overview.what_it_is}</p>
                  </div>

                  <div className="ask-forge-overview-block">
                    <small>WHY IT MATTERS</small>
                    <p>{nativeLesson.overview.why_it_matters}</p>
                  </div>

                  {Array.isArray(nativeLesson.overview.how_it_works) &&
                    nativeLesson.overview.how_it_works.length>0 && (
                    <div className="ask-forge-overview-block">
                      <small>HOW IT WORKS</small>
                      <div className="ask-forge-overview-flow">
                        {nativeLesson.overview.how_it_works.slice(0,5).map((item,i)=>(
                          <div className="ask-forge-overview-flow-item" key={i}>
                            <b>{String(i+1).padStart(2,"0")}</b>
                            <span>{typeof item==="string"?item:item?.step||item?.title||item?.description||""}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {Array.isArray(nativeLesson.overview.when_to_use) &&
                    nativeLesson.overview.when_to_use.length>0 && (
                    <div className="ask-forge-overview-block">
                      <small>WHEN TO USE IT</small>
                      <ul className="ask-forge-overview-list">
                        {nativeLesson.overview.when_to_use.slice(0,4).map((item,i)=>(
                          <li key={i}>{typeof item==="string"?item:item?.description||item?.title||""}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <div className="ask-forge-overview-loading">
                  FORGE is generating a topic-specific explanation…
                </div>
              )}
            </div>
          </aside>
        </div>}

        {mode==="doubt"&&<div className="ask-forge-grid">
          <section className="ask-forge-card">
            <div className="ask-forge-label">ASK A DOUBT</div>
            <h2>Ask anything about {topicName}.</h2>
            <p className="ask-forge-sub" style={{marginTop:7,fontSize:11}}>Text, screenshots and study context can be used to make the explanation relevant to your FORGE journey.</p>
            <textarea className="ask-forge-input" value={doubt} onChange={e=>setDoubt(e.target.value)} placeholder="Example: Explain backpropagation in very simple Hinglish and then give me one numerical example." />
            <div className="ask-forge-upload">
              <label><input type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0]||null)}/><FileText size={14}/>Upload Image</label>
              <label><input type="file" accept=".pdf,application/pdf" onChange={e=>setFile(e.target.files?.[0]||null)}/><BookOpen size={14}/>Upload PDF</label>
              <label><input type="file" accept=".txt,.md,.doc,.docx" onChange={e=>setFile(e.target.files?.[0]||null)}/><FileText size={14}/>Upload Notes</label>
            </div>
            {file&&<div className="ask-forge-file">Attached: <strong>{file.name}</strong> · {Math.round(file.size/1024)} KB</div>}
            <div className="ask-forge-action"><button onClick={askDoubt} disabled={!doubt.trim()||answerLoading}>{answerLoading?"Thinking…":"Ask FORGE"}<Send size={13}/></button></div>
          </section>
          <aside className="ask-forge-card">
            <div className="ask-forge-label">FORGE ANSWER</div>
            <h2>{answer?"Explanation":"Your answer appears here."}</h2>
            <div style={{marginTop:15}} className="ask-forge-answer">{answer?<ForgeAnswerView text={answer}/>:"Ask a doubt and FORGE will answer in a short, student-friendly format."}</div>{diagramSteps.length>=2&&<ForgeDoubtDiagram steps={diagramSteps}/>} 
          </aside>
        </div>}

        {mode==="video"&&<div className="ask-forge-grid">
          <section className="ask-forge-card">
            <div className="ask-forge-label">LECTURE SUMMARIZATION</div>
            <h2>Turn a lecture into revision material.</h2>
            <p className="ask-forge-sub" style={{marginTop:7,fontSize:11}}>Upload the lecture/video and FORGE can be extended to produce chapters, key concepts, exam notes and a visual recap. The UI will never fabricate a summary when transcript evidence is unavailable.</p>
            <div className="ask-forge-upload" style={{gridTemplateColumns:"1fr"}}>
              <label><input type="file" accept="video/*,.mp4,.mov,.webm" onChange={e=>setVideoFile(e.target.files?.[0]||null)}/><PlayCircle size={15}/>Choose Lecture Video</label>
            </div>
            {videoFile&&<div className="ask-forge-file">Selected: <strong>{videoFile.name}</strong> · {Math.round(videoFile.size/1024/1024*10)/10} MB</div>}
            <textarea className="ask-forge-input" style={{marginTop:10}} value={videoSummaryPrompt} onChange={e=>setVideoSummaryPrompt(e.target.value)} placeholder="Optional: What should the summary focus on? e.g. formulas, exam questions, 2-minute revision..." />
            <div className="ask-forge-action"><button onClick={summarizeVideo} disabled={!videoFile||videoLoading}>{videoLoading?"Preparing…":"Prepare Summary"}<ArrowRight size={13}/></button></div>
          </section>
          <aside className="ask-forge-card">
            <div className="ask-forge-label">SUMMARY OUTPUT</div>
            <h2>Evidence-first summarization.</h2>
            <div className="ask-forge-answer" style={{marginTop:15}}>{videoSummary||"Once the video-transcription backend is connected, this panel will show timestamped chapters, concise notes, key concepts, formulas, exam questions and a visual recap."}</div>
          </aside>
        </div>}

        <div className="student-bottom" style={{marginTop:28}}>
          <div className="student-validation"><strong>Learn → visualize → ask → practice.</strong> Ask Forge sits between Industry Pulse signals and your next learning action.</div>
          <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
            <button className="student-option" onClick={()=>navigate("/student/industry")}>Industry Pulse</button>
            <button className="student-continue" onClick={()=>navigate("/student/learning")}>Learning Hub <ArrowRight size={14}/></button>
          </div>
        </div>
      </div>
    </main>
  </>;
}

function StudentChooser(){const navigate=useNavigate();return <><StudentStyles/><section className="student-org-section slide" id="choose-your-forge"><div className="workspace-heading"><div className="workspace-kicker"><span/>CHOOSE YOUR FORGE</div><h2>One platform.<br/>Two ways to build the future.</h2><p>Students build future-ready capability through an adaptive learning loop. Organizations trace changing work, model AI exposure, redesign Human–AI allocation and preserve capability.</p></div><div className="workspace-grid"><button className="workspace-card workspace-card-student" onClick={()=>navigate("/student")}><span className="workspace-number">01</span><div className="workspace-card-art" aria-hidden="true"><img src="/forge-student-card.png" alt="" /></div><div className="workspace-card-shade" aria-hidden="true"/><div className="workspace-card-content"><div className="workspace-icon"><GraduationCap size={27}/></div><div className="workspace-tag">FOR INDIVIDUALS</div><h3>Student</h3><p>Tell FORGE your target, assess your current level, build a personalized roadmap, learn through practice and adapt the plan as your progress changes.</p><div className="workspace-features"><span>Personalized Roadmap</span><span>Assessments</span><span>Study Planner</span><span>Industry Pulse</span></div><span className="workspace-cta">Enter Student Workspace <ArrowRight size={15}/></span></div></button><button className="workspace-card workspace-card-organization" onClick={()=>navigate("/organization")}><span className="workspace-number">02</span><div className="workspace-card-art" aria-hidden="true"><img src="/forge-organization-card.png" alt="" /></div><div className="workspace-card-shade" aria-hidden="true"/><div className="workspace-card-content"><div className="workspace-icon"><Building2 size={27}/></div><div className="workspace-tag">FOR ORGANIZATIONS</div><h3>Organization</h3><p>Trace work to capabilities, model AI-driven exposure, simulate future Human–AI work allocation and preserve capability through evidence-based practice.</p><div className="workspace-features"><span>WorkTrace</span><span>Skill Shadow</span><span>WorkFold</span><span>Lattice</span></div><span className="workspace-cta">Enter Organization Workspace <ArrowRight size={15}/></span></div></button></div></section></>}


/* =========================================================
   APP
========================================================= */

const FORGE_WORKFOLD_STYLE = `
  .split-bar {
    display: flex;
    width: 100%;
    min-height: 72px;
    overflow: hidden;
    border-radius: 9px;
  }

  .split-bar > div {
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    white-space: nowrap;
  }

  .split-bar > div span {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 12px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  .split-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 12px;
    font-size: 11px;
    letter-spacing: 0.04em;
    color: #6d726e;
  }

  .split-legend span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .split-legend i {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
  }

  .legend-human {
    background: #cfd4d1;
  }

  .legend-hybrid {
    background: #b9c5e2;
  }

  .legend-ai {
    background: #6c8bd8;
  }

  @media (max-width: 700px) {
    .split-bar {
      min-height: 58px;
    }

    .split-bar > div span {
      font-size: 10px;
      padding: 0 7px;
    }

    .split-legend {
      gap: 10px 14px;
    }
  }
`;

function WorkFoldVisualStyles() {
  return <style>{FORGE_WORKFOLD_STYLE}</style>;
}

const LATTICE_WORKSPACE_STYLE = `
  .lattice-spin { animation: latticeSpin .9s linear infinite; }
  @keyframes latticeSpin { to { transform: rotate(360deg); } }
  .lattice-workspace {
    margin-top: 18px;
    border: 1px solid #dfe3df;
    border-radius: 20px;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 18px 50px rgba(21, 28, 24, 0.08);
  }
  .lattice-workspace-head {
    padding: 20px 22px;
    background: linear-gradient(135deg, #111713 0%, #202923 58%, #2e3d35 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  .lattice-workspace-kicker {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #a9d7c0;
  }
  .lattice-workspace-head h3 {
    margin: 7px 0 0;
    font-size: 20px;
    letter-spacing: -.02em;
  }
  .lattice-evidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 11px;
    border: 1px solid rgba(255,255,255,.16);
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .08em;
    white-space: nowrap;
  }
  .lattice-workspace-body {
    display: grid;
    grid-template-columns: minmax(0, .92fr) minmax(0, 1.08fr);
    gap: 0;
  }
  .lattice-brief, .lattice-submit {
    padding: 24px;
  }
  .lattice-brief {
    background: #f7f9f6;
    border-right: 1px solid #e2e6e2;
  }
  .lattice-panel-label {
    margin-bottom: 10px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: .13em;
    color: #3565d4;
  }
  .lattice-brief-title {
    margin: 0 0 20px;
    font-size: 19px;
    line-height: 1.35;
    color: #171c19;
  }
  .lattice-mini-card {
    padding: 14px;
    margin-top: 12px;
    border: 1px solid #e0e4e0;
    border-radius: 13px;
    background: #fff;
  }
  .lattice-mini-card p {
    margin: 0;
    font-size: 12px;
    line-height: 1.7;
    color: #555c57;
  }
  .lattice-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 10px;
  }
  .lattice-chip {
    padding: 6px 9px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3657a8;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .04em;
  }
  .lattice-submit {
    background: #fff;
  }
  .lattice-submit-intro {
    display: flex;
    align-items: flex-start;
    gap: 11px;
    margin-bottom: 16px;
  }
  .lattice-submit-icon {
    width: 38px;
    height: 38px;
    flex: 0 0 auto;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: #eef4ff;
    color: #3565d4;
  }
  .lattice-submit-intro strong {
    display: block;
    font-size: 13px;
    color: #171c19;
  }
  .lattice-submit-intro span {
    display: block;
    margin-top: 3px;
    font-size: 11px;
    line-height: 1.5;
    color: #737973;
  }
  .lattice-textarea {
    width: 100%;
    min-height: 235px;
    resize: vertical;
    box-sizing: border-box;
    padding: 16px;
    border: 1px solid #d9ded9;
    border-radius: 14px;
    outline: none;
    background: #fbfcfb;
    color: #202521;
    font: inherit;
    font-size: 13px;
    line-height: 1.7;
    transition: border-color .18s, box-shadow .18s, background .18s;
  }
  .lattice-textarea:focus {
    border-color: #6d8de0;
    background: #fff;
    box-shadow: 0 0 0 4px rgba(83, 111, 199, .10);
  }
  .lattice-submit-meta {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-top: 8px;
    font-size: 10px;
    color: #7b817c;
  }
  .lattice-submit-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 15px;
  }
  .lattice-submit-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    min-width: 150px;
    padding: 12px 16px;
    border: 0;
    border-radius: 11px;
    background: #161b17;
    color: #fff;
    font: inherit;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .04em;
    cursor: pointer;
    transition: transform .18s, box-shadow .18s, opacity .18s;
  }
  .lattice-submit-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 9px 22px rgba(21, 28, 24, .18);
  }
  .lattice-submit-button:disabled {
    opacity: .55;
    cursor: not-allowed;
  }
  .lattice-result {
    margin: 18px 24px 24px;
    padding: 17px;
    border: 1px solid #dce3dc;
    border-radius: 14px;
    background: #f8fbf8;
  }
  .lattice-result.success {
    background: #f3faf5;
    border-color: #cfe2d4;
  }
  .lattice-result.warn {
    background: #fffaf0;
    border-color: #eadbb9;
  }
  .lattice-result-head {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .lattice-result-head strong {
    font-size: 13px;
  }
  .lattice-result-score {
    margin-left: auto;
    font-size: 18px;
    font-weight: 900;
    color: #1c5d3a;
  }
  .lattice-result p {
    margin: 8px 0 0;
    font-size: 11px;
    line-height: 1.6;
    color: #5f665f;
  }
  .lattice-trust-note {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 13px;
    padding: 10px 12px;
    border-radius: 10px;
    background: #f2f4f2;
    color: #68706a;
    font-size: 10px;
    line-height: 1.5;
  }
  @media (max-width: 900px) {
    .lattice-workspace-body { grid-template-columns: 1fr; }
    .lattice-brief { border-right: 0; border-bottom: 1px solid #e2e6e2; }
  }
  @media (max-width: 560px) {
    .lattice-workspace-head { align-items: flex-start; flex-direction: column; }
    .lattice-brief, .lattice-submit { padding: 18px; }
    .lattice-result { margin: 16px 18px 18px; }
  }
`;

function LatticeWorkspaceStyles() {
  return <style>{LATTICE_WORKSPACE_STYLE}</style>;
}



/* =========================================================
   ORGANIZATION WORKSPACE — ROLE-BASED INTELLIGENCE HOME
   Frontend foundation for HR/Admin + Employee workspaces.
   Existing WorkTrace / Skill Shadow / WorkFold / Lattice APIs
   remain the source of intelligence.
========================================================= */

const FORGE_ORG_WORKSPACE_CSS = `
/* =========================================================
   FORGE ORGANIZATION — PREMIUM LIGHT GLASS SYSTEM
========================================================= */
.forge-org-page{min-height:100vh;position:relative;overflow-x:hidden;color:#172033;background:
  radial-gradient(900px 520px at 6% -5%,rgba(196,181,253,.48),transparent 62%),
  radial-gradient(760px 520px at 95% 10%,rgba(153,246,228,.32),transparent 62%),
  radial-gradient(700px 500px at 50% 105%,rgba(191,219,254,.42),transparent 68%),
  linear-gradient(135deg,#f7f5ff 0%,#f3f7ff 44%,#f4fbf9 100%);}
.forge-org-page:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background-image:linear-gradient(rgba(99,102,241,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,.045) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,#000,transparent 92%)}
.forge-org-page:after{content:"";position:fixed;width:520px;height:520px;right:-210px;top:180px;border-radius:50%;pointer-events:none;z-index:0;background:radial-gradient(circle,rgba(129,140,248,.20),transparent 68%);filter:blur(12px);animation:forgeOrgAmbient 11s ease-in-out infinite alternate}
.forge-org-shell{width:min(1480px,calc(100% - 44px));margin:0 auto;position:relative;z-index:1}

/* ---------- AUTH / LOGIN ---------- */
.forge-org-access-page{min-height:100vh!important;padding:28px 28px 70px!important;color:#172033!important;display:block!important;overflow:hidden}
.forge-org-access-shell{width:min(1220px,100%);margin:0 auto;position:relative;z-index:2}
.forge-org-access-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:54px}
.forge-org-access-back{border:0;background:rgba(255,255,255,.52);padding:10px 14px;border:1px solid rgba(148,163,184,.16);border-radius:999px;color:#667085;font:inherit;font-size:11px;font-weight:800;cursor:pointer;box-shadow:0 8px 25px rgba(71,85,105,.06);transition:.25s}
.forge-org-access-back:hover{transform:translateX(-3px);color:#4f46e5;background:rgba(255,255,255,.82)}
.forge-org-access-brand{display:flex;align-items:center;gap:10px;color:#27324a;font-size:11px;font-weight:900;letter-spacing:.18em}
.forge-org-access-brand span{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;color:#fff;font-size:18px;background:linear-gradient(135deg,#7457ff,#4b8df8 58%,#35cdb1);box-shadow:0 12px 30px rgba(83,90,210,.22)}
.forge-org-access-brand b{font-size:9px;color:#98a2b3;letter-spacing:.12em}
.forge-org-role-screen{animation:forgeOrgReveal .65s cubic-bezier(.2,.8,.2,1) both}
.forge-org-access-copy{max-width:850px;text-align:center;margin:0 auto}
.forge-org-access-copy .forge-org-kicker{justify-content:center}
.forge-org-kicker{display:inline-flex;align-items:center;gap:9px;color:#69758a;font-size:9px;font-weight:900;letter-spacing:.19em;text-transform:uppercase}
.forge-org-kicker i{display:inline-block;width:32px;height:1px;background:linear-gradient(90deg,#8b5cf6,#2dd4bf);box-shadow:0 0 12px rgba(124,58,237,.25)}
.forge-org-access-copy h1{margin:18px 0 13px;font-size:clamp(43px,6vw,76px);line-height:.94;letter-spacing:-.065em;color:#111827;font-weight:800}
.forge-org-access-copy h1 em{font-style:normal;color:transparent;background:linear-gradient(100deg,#6d4cff,#8b5cf6 42%,#14b8a6);-webkit-background-clip:text;background-clip:text}
.forge-org-access-copy p{max-width:720px;margin:0 auto;color:#667085;font-size:14px;line-height:1.75}
.forge-org-role-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin-top:44px;perspective:1200px}
.forge-org-role-card{position:relative;min-height:365px;padding:31px;text-align:left;border:1px solid rgba(255,255,255,.82)!important;border-radius:30px;background:linear-gradient(145deg,rgba(255,255,255,.80),rgba(249,251,255,.58))!important;box-shadow:0 28px 80px rgba(76,81,133,.13),inset 0 1px 0 rgba(255,255,255,.95)!important;backdrop-filter:blur(25px) saturate(130%);-webkit-backdrop-filter:blur(25px) saturate(130%);cursor:pointer;overflow:hidden;color:#172033;transition:transform .42s cubic-bezier(.2,.8,.2,1),box-shadow .42s,border-color .3s}
.forge-org-role-card:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(420px 260px at 100% 0%,rgba(139,92,246,.16),transparent 68%),radial-gradient(360px 260px at 0% 100%,rgba(45,212,191,.08),transparent 70%)}
.forge-org-role-card:after{content:"";position:absolute;left:28px;right:28px;bottom:0;height:2px;border-radius:99px;background:linear-gradient(90deg,transparent,#8b5cf6,#38bdf8,#2dd4bf,transparent);opacity:.55}
.forge-org-role-card:hover{transform:translateY(-10px) rotateX(1deg) scale(1.012);box-shadow:0 38px 100px rgba(76,81,133,.18),0 0 45px rgba(124,58,237,.10);border-color:rgba(129,140,248,.48)!important}
.forge-org-role-card-head{position:relative;display:flex;justify-content:space-between;align-items:flex-start}
.forge-org-role-card-icon{width:62px;height:62px;display:grid;place-items:center;border-radius:18px;color:#fff;box-shadow:0 14px 32px rgba(79,70,229,.17);transition:transform .35s,box-shadow .35s}
.forge-org-role-card:hover .forge-org-role-card-icon{transform:translateY(-4px) rotate(-3deg);box-shadow:0 20px 42px rgba(79,70,229,.24)}
.forge-org-role-hr .forge-org-role-card-icon{background:linear-gradient(135deg,#7654f6,#5865ee 58%,#7c5cff)}
.forge-org-role-employee .forge-org-role-card-icon{background:linear-gradient(135deg,#12a99d,#3b82f6 62%,#67e8f9)}
.forge-org-role-card-number{font-size:10px;font-weight:900;letter-spacing:.18em;color:#98a2b3}
.forge-org-role-card-kicker{position:relative;margin-top:38px;font-size:9px;letter-spacing:.18em;font-weight:900;color:#7654f6}
.forge-org-role-employee .forge-org-role-card-kicker{color:#0f9f98}
.forge-org-role-card h2{position:relative;margin:8px 0 10px;font-size:33px;letter-spacing:-.05em;color:#111827}
.forge-org-role-card p{position:relative;margin:0;max-width:520px;color:#667085;font-size:12px;line-height:1.72}
.forge-org-role-pills{position:relative;display:flex;flex-wrap:wrap;gap:7px;margin-top:23px}
.forge-org-role-pills span{padding:7px 10px;border:1px solid rgba(148,163,184,.18);border-radius:999px;background:rgba(255,255,255,.58);color:#667085;font-size:9px;font-weight:800}
.forge-org-role-enter{position:relative;display:inline-flex;align-items:center;gap:8px;margin-top:27px;color:#27324a;font-size:11px;font-weight:900}
.forge-org-role-enter svg{transition:transform .25s}.forge-org-role-card:hover .forge-org-role-enter svg{transform:translateX(5px)}
.forge-org-form-screen{max-width:920px;margin:0 auto;animation:forgeOrgReveal .5s ease both}
.forge-org-change-role{border:0;background:rgba(255,255,255,.55);display:inline-flex;align-items:center;gap:6px;padding:9px 12px;border:1px solid rgba(148,163,184,.16);border-radius:999px;color:#667085;font:inherit;font-size:10px;font-weight:800;cursor:pointer;margin-bottom:24px}
.forge-org-form-heading{display:flex;gap:17px;align-items:center;margin-bottom:24px}
.forge-org-form-role-icon{width:58px;height:58px;display:grid;place-items:center;border-radius:17px;color:#fff;background:linear-gradient(135deg,#7654f6,#3b82f6);box-shadow:0 13px 32px rgba(79,70,229,.20)}
.forge-org-form-heading h2{margin:0;font-size:32px;letter-spacing:-.045em}.forge-org-form-heading p{margin:4px 0 0;color:#667085;font-size:11px}
.forge-org-profile-form{padding:28px;border:1px solid rgba(255,255,255,.84)!important;border-radius:26px;background:linear-gradient(145deg,rgba(255,255,255,.80),rgba(248,251,255,.62))!important;box-shadow:0 28px 85px rgba(76,81,133,.14),inset 0 1px 0 rgba(255,255,255,.96)!important;backdrop-filter:blur(24px)}
.forge-org-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.forge-org-field label{display:block;margin:0 0 7px;color:#667085;font-size:9px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.forge-org-field input{width:100%;box-sizing:border-box;padding:13px 14px;border:1px solid rgba(148,163,184,.18);border-radius:13px;outline:none;background:rgba(255,255,255,.68);color:#172033;font:inherit;font-size:12px;box-shadow:inset 0 1px 0 rgba(255,255,255,.8);transition:.2s}.forge-org-field input:focus{border-color:rgba(99,102,241,.48);box-shadow:0 0 0 4px rgba(99,102,241,.08),0 8px 24px rgba(79,70,229,.06)}
.forge-org-form-error{display:flex;align-items:center;gap:8px;margin-top:13px;padding:11px 13px;border-radius:12px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.14);color:#b42318;font-size:10px;font-weight:700}
.forge-org-form-submit-row{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:18px;padding-top:17px;border-top:1px solid rgba(148,163,184,.13)}
.forge-org-secure-note{display:flex;gap:8px;align-items:flex-start;color:#667085;font-size:9px;line-height:1.5}.forge-org-secure-note svg{color:#14a38e;flex:0 0 auto}.forge-org-secure-note strong{color:#344054}
.forge-org-submit{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:50px;padding:0 21px;border:0;border-radius:14px;background:linear-gradient(105deg,#7654f6,#5479f4 55%,#16b8a4);color:#fff;font:inherit;font-size:10px;font-weight:900;letter-spacing:.05em;cursor:pointer;box-shadow:0 16px 36px rgba(71,100,220,.22);transition:.25s}.forge-org-submit:hover{transform:translateY(-3px);box-shadow:0 22px 45px rgba(71,100,220,.28);filter:saturate(1.08)}

/* ---------- DASHBOARD SHELL ---------- */
.forge-org-dashboard-page{background:linear-gradient(135deg,#f8f7ff,#f4f8ff 48%,#f2fbf8)!important}
.forge-org-dashboard-layout{display:grid;grid-template-columns:244px minmax(0,1fr);gap:20px;align-items:start;padding:20px 0 72px}
.forge-org-sidebar{position:sticky;top:18px;min-height:calc(100vh - 36px);padding:20px 14px;border:1px solid rgba(255,255,255,.82);border-radius:28px;background:linear-gradient(180deg,rgba(255,255,255,.78),rgba(248,250,255,.57));box-shadow:0 26px 75px rgba(71,85,105,.12),inset 0 1px 0 rgba(255,255,255,.94);backdrop-filter:blur(25px);-webkit-backdrop-filter:blur(25px)}
.forge-org-brand{display:flex;align-items:center;gap:11px;padding:3px 9px 25px}.forge-org-brand img{width:42px;height:42px;object-fit:contain;border-radius:13px;filter:drop-shadow(0 7px 15px rgba(91,73,211,.20))}.forge-org-brand strong{display:block;color:#1b2436;font-size:17px;letter-spacing:.19em}.forge-org-brand small{display:block;margin-top:3px;color:#8993a6;font-size:7px;font-weight:800;letter-spacing:.06em}
.forge-org-nav-group{margin-top:13px}.forge-org-nav-label{padding:0 11px 8px;color:#98a2b3;font-size:7px;letter-spacing:.18em;font-weight:900}.forge-org-nav{width:100%;display:flex;align-items:center;gap:10px;padding:11px 11px;border:1px solid transparent;border-radius:12px;background:transparent;color:#68758b;font:inherit;font-size:10px;font-weight:750;text-align:left;cursor:pointer;transition:.22s}.forge-org-nav:hover{color:#27324a;background:rgba(124,92,246,.06);border-color:rgba(124,92,246,.10);transform:translateX(2px)}.forge-org-nav.active{color:#4d3bd4;background:linear-gradient(100deg,rgba(124,92,246,.15),rgba(59,130,246,.07));border-color:rgba(124,92,246,.20);box-shadow:0 10px 25px rgba(99,82,210,.09)}.forge-org-nav svg{color:#7259ef}.forge-org-sidebar-foot{position:absolute;left:14px;right:14px;bottom:15px;padding:13px 10px;border-top:1px solid rgba(148,163,184,.12);color:#a0a9b8;font-size:7px;letter-spacing:.12em;font-weight:800}
.forge-org-main{min-width:0}.forge-org-topbar{height:56px;display:flex;align-items:center;justify-content:flex-end;gap:14px;margin-bottom:13px;padding:0 4px!important;border:0!important;background:transparent!important}.forge-org-top-actions{display:flex;align-items:center;gap:12px}.forge-org-user{display:flex;align-items:center;gap:10px;padding:6px 9px;border:1px solid rgba(255,255,255,.72);border-radius:16px;background:rgba(255,255,255,.52);box-shadow:0 10px 28px rgba(71,85,105,.07);backdrop-filter:blur(16px)}.forge-org-avatar{width:35px;height:35px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#e4d5ff,#b9b4ff 55%,#a7efe4);color:#41336d;font-size:12px;font-weight:900}.forge-org-user-copy strong{display:block;color:#27324a;font-size:9px}.forge-org-user-copy span{display:block;color:#8a95a8;font-size:7px;margin-top:2px}.forge-org-signout{border:1px solid rgba(148,163,184,.18)!important;background:rgba(255,255,255,.52)!important;color:#68758b!important;border-radius:10px!important;padding:8px 11px!important;font:inherit;font-size:8px!important;font-weight:850!important;cursor:pointer;transition:.2s}.forge-org-signout:hover{color:#344054!important;background:#fff!important;transform:translateY(-1px)}

/* ---------- HERO ---------- */
.forge-org-hero{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,.72fr);gap:16px;align-items:stretch}.forge-org-hero-copy{min-height:250px;padding:35px 37px 31px;border:1px solid rgba(255,255,255,.82);border-radius:28px;background:linear-gradient(135deg,rgba(255,255,255,.84),rgba(245,239,255,.70));box-shadow:0 26px 75px rgba(80,62,135,.12),inset 0 1px 0 rgba(255,255,255,.95);backdrop-filter:blur(24px);animation:forgeOrgReveal .55s ease both}.forge-org-hero-copy h1{margin:18px 0 13px;max-width:800px;font-size:clamp(42px,5vw,72px);line-height:.95;letter-spacing:-.065em;color:#111827;font-weight:800}.forge-org-hero-copy h1 em{font-style:normal;color:transparent;background:linear-gradient(100deg,#7052ed,#8b5cf6 45%,#2563eb);-webkit-background-clip:text;background-clip:text}.forge-org-hero-copy p{margin:0;max-width:760px;color:#667085;font-size:13px;line-height:1.7}
.forge-org-hero-side{position:relative;min-height:250px;padding:28px;border:1px solid rgba(255,255,255,.82);border-radius:28px;background:linear-gradient(145deg,rgba(235,232,255,.72),rgba(229,251,248,.58));box-shadow:0 26px 75px rgba(71,85,105,.10),inset 0 1px 0 rgba(255,255,255,.94);overflow:hidden;display:flex;flex-direction:column;justify-content:center;align-items:flex-end;animation:forgeOrgReveal .65s .08s ease both}.forge-org-hero-side:before{content:"";position:absolute;width:260px;height:260px;border-radius:50%;right:-60px;top:-65px;border:1px solid rgba(124,92,246,.15);box-shadow:0 0 0 22px rgba(124,92,246,.025),0 0 0 46px rgba(45,212,191,.025),0 0 0 70px rgba(59,130,246,.025);animation:forgeOrgOrbit 14s linear infinite}.forge-org-date{text-align:right;position:relative;z-index:1}.forge-org-date .day{display:block;color:#6b7280;font-size:10px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.forge-org-date .date{display:block;margin-top:8px;color:#182033;font-size:31px;font-weight:800;letter-spacing:-.045em}.forge-org-date .year{display:block;margin-top:1px;color:#7c8799;font-size:12px;font-weight:800;letter-spacing:.08em}.forge-org-date .company{display:block;margin-top:10px;color:#5b46cf;font-size:12px;font-weight:900;letter-spacing:.05em}.forge-org-date .future{display:block;margin-top:5px;color:#778398;font-size:10px;line-height:1.45}.forge-org-live-dot{position:absolute;right:25px;bottom:22px;display:flex;align-items:center;gap:7px;color:#778398;font-size:7px;font-weight:900;letter-spacing:.14em}.forge-org-live-dot i{width:6px;height:6px;border-radius:50%;background:#20c997;box-shadow:0 0 13px rgba(32,201,151,.65);animation:forgeOrgBlink 1.7s ease-in-out infinite}
.forge-wave{display:inline-block;transform-origin:70% 70%;animation:forgeWave 1.9s ease-in-out infinite;filter:drop-shadow(0 4px 8px rgba(124,92,246,.13))}

/* ---------- KPI CARDS ---------- */
.forge-org-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin-top:17px}.forge-org-metric{position:relative;min-height:146px;padding:22px 22px 19px;border:1px solid rgba(255,255,255,.82);border-radius:22px;background:rgba(255,255,255,.64);box-shadow:0 20px 52px rgba(71,85,105,.10),inset 0 1px 0 rgba(255,255,255,.92);backdrop-filter:blur(21px);overflow:hidden;animation:forgeOrgReveal .52s ease both;transition:transform .3s,box-shadow .3s}.forge-org-metric:hover{transform:translateY(-6px);box-shadow:0 28px 65px rgba(71,85,105,.14),inset 0 1px 0 rgba(255,255,255,.96)}.forge-org-metric:before{content:"";position:absolute;left:-10%;right:-10%;bottom:-48px;height:100px;border-radius:50%;filter:blur(1px);opacity:.82;animation:forgeOrgMountain 5s ease-in-out infinite alternate}.forge-org-metric:nth-child(1):before{background:radial-gradient(ellipse at 50% 100%,rgba(59,130,246,.28),transparent 67%)}.forge-org-metric:nth-child(2):before{background:radial-gradient(ellipse at 50% 100%,rgba(124,92,246,.30),transparent 67%)}.forge-org-metric:nth-child(3):before{background:radial-gradient(ellipse at 50% 100%,rgba(244,63,94,.24),transparent 67%)}.forge-org-metric:nth-child(4):before{background:radial-gradient(ellipse at 50% 100%,rgba(16,185,129,.28),transparent 67%)}.forge-org-metric:after{content:"";position:absolute;right:-30px;top:-30px;width:115px;height:115px;border-radius:50%;filter:blur(3px)}.forge-org-metric:nth-child(1):after{background:radial-gradient(circle,rgba(59,130,246,.16),transparent 70%)}.forge-org-metric:nth-child(2):after{background:radial-gradient(circle,rgba(124,92,246,.17),transparent 70%)}.forge-org-metric:nth-child(3):after{background:radial-gradient(circle,rgba(244,63,94,.15),transparent 70%)}.forge-org-metric:nth-child(4):after{background:radial-gradient(circle,rgba(16,185,129,.16),transparent 70%)}.forge-org-metric:nth-child(2){animation-delay:.05s}.forge-org-metric:nth-child(3){animation-delay:.1s}.forge-org-metric:nth-child(4){animation-delay:.15s}.forge-org-metric small{position:relative;z-index:1;display:block;color:#8791a4;font-size:8px;font-weight:900;letter-spacing:.14em}.forge-org-metric strong{position:relative;z-index:1;display:block;margin-top:9px;color:#1b2436;font-size:34px;line-height:1;letter-spacing:-.055em}.forge-org-metric:nth-child(1) strong{color:#426cf1}.forge-org-metric:nth-child(2) strong{color:#7956e9}.forge-org-metric:nth-child(3) strong{color:#e04f73}.forge-org-metric:nth-child(4) strong{color:#12a78f}.forge-org-metric span{position:relative;z-index:1;display:block;margin-top:7px;color:#78859a;font-size:9px;line-height:1.45}.forge-org-metric-change{position:relative;z-index:1;display:inline-flex;align-items:center;gap:4px;margin-top:8px;padding:4px 7px;border-radius:999px;background:rgba(16,185,129,.08);color:#0f9f72;font-size:8px;font-weight:900;letter-spacing:.03em}.forge-org-metric-change.neutral{background:rgba(99,102,241,.07);color:#6655c9}

/* ---------- ANALYTICS / GRAPH ---------- */
.forge-org-analytics-grid{display:grid;grid-template-columns:minmax(0,1.58fr) minmax(360px,.82fr);gap:16px;margin-top:18px}.forge-org-chart-panel,.forge-org-gap-panel{position:relative;min-width:0;border:1px solid rgba(255,255,255,.84);border-radius:24px;background:rgba(255,255,255,.66);box-shadow:0 22px 60px rgba(71,85,105,.10),inset 0 1px 0 rgba(255,255,255,.94);backdrop-filter:blur(22px);overflow:hidden}.forge-org-chart-panel{padding:22px}.forge-org-gap-panel{padding:22px}.forge-org-panel-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start}.forge-org-panel-head strong{color:#202a3c;font-size:15px;letter-spacing:-.025em}.forge-org-panel-head>span{color:#9aa3b3;font-size:7px;letter-spacing:.13em;font-weight:900}.forge-org-chart-legend{display:flex;gap:13px;align-items:center;margin-top:6px}.forge-org-chart-legend span{display:flex;align-items:center;gap:6px;color:#8a95a8;font-size:8px}.forge-org-legend-dot{width:7px;height:7px;border-radius:50%;display:inline-block;box-shadow:0 0 9px currentColor}.forge-org-transform-legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px}.forge-org-transform-legend span{display:flex;align-items:center;gap:7px;color:#758196;font-size:8px;font-weight:800}.forge-org-transform-legend i{width:18px;height:3px;border-radius:99px;display:inline-block}.forge-org-transform-legend .current{background:#6366f1}.forge-org-transform-legend .post{background:#38bdf8}.forge-org-transform-legend .future{background:#c05cff}.forge-org-chart-wrap{height:330px;margin-top:8px;overflow:hidden}.forge-org-chart{width:100%;height:100%;display:block}.forge-org-chart-grid{stroke:rgba(100,116,139,.12);stroke-width:1}.forge-org-chart-axis{fill:#9aa3b3;font-size:9px}.forge-org-chart-x{fill:#7d8799;font-size:8px;font-weight:700}.forge-org-chart-line{fill:none;stroke:url(#forgeTransformCurrent);stroke-width:3;filter:url(#forgeTransformGlow);stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1000;stroke-dashoffset:1000;animation:forgeDrawLine 1.8s cubic-bezier(.2,.8,.2,1) forwards}.forge-org-chart-line-post{fill:none;stroke:url(#forgeTransformPost);stroke-width:3;filter:url(#forgeTransformGlow);stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1000;stroke-dashoffset:1000;animation:forgeDrawLine 2s .12s cubic-bezier(.2,.8,.2,1) forwards}.forge-org-chart-line-future{fill:none;stroke:url(#forgeTransformFuture);stroke-width:3;filter:url(#forgeTransformGlow);stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1000;stroke-dashoffset:1000;animation:forgeDrawLine 2.2s .24s cubic-bezier(.2,.8,.2,1) forwards}.forge-org-chart-area{fill:url(#forgeRoleArea)}.forge-org-chart-point{fill:#fff;stroke:#7654f6;stroke-width:2.5;filter:drop-shadow(0 0 6px rgba(118,84,246,.55));animation:forgePointIn .5s ease both}.forge-org-chart-point-post{fill:#fff;stroke:#38bdf8;stroke-width:2.5;filter:drop-shadow(0 0 6px rgba(56,189,248,.55))}.forge-org-chart-point-future{fill:#fff;stroke:#c05cff;stroke-width:2.5;filter:drop-shadow(0 0 7px rgba(192,92,255,.6))}.forge-org-role-label{fill:#7c879a;font-size:8px;font-weight:700}.forge-org-chart-empty{height:100%;display:grid;place-items:center;color:#8994a7;font-size:11px}.forge-org-role-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:5px}.forge-org-role-card-mini{padding:11px 12px;border:1px solid rgba(148,163,184,.13);border-radius:12px;background:rgba(248,250,252,.58);transition:.25s}.forge-org-role-card-mini:hover{transform:translateY(-2px);background:#fff;box-shadow:0 10px 24px rgba(71,85,105,.08)}.forge-org-role-card-mini strong{display:block;color:#344054;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.forge-org-role-card-mini span{display:block;margin-top:4px;color:#8b95a6;font-size:8px}

/* ---------- CAPABILITY GAPS ---------- */
.forge-org-gap-list{display:grid;gap:15px;margin-top:22px}.forge-org-gap-row{display:grid;grid-template-columns:112px 1fr 42px;align-items:center;gap:10px}.forge-org-gap-row label{color:#536074;font-size:9px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.forge-org-gap-track{height:10px;border-radius:99px;background:rgba(100,116,139,.09);overflow:hidden;box-shadow:inset 0 1px 2px rgba(71,85,105,.05)}.forge-org-gap-track i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#8b5cf6,#5b8ff8 58%,#2dd4bf);box-shadow:0 0 14px rgba(113,82,239,.20);animation:forgeGapGrow 1.2s cubic-bezier(.2,.8,.2,1) both}.forge-org-gap-row em{font-style:normal;text-align:right;color:#4f5d72;font-size:9px;font-weight:900}.forge-org-gap-note{margin-top:18px;padding:12px 13px;border:1px solid rgba(124,92,246,.10);border-radius:13px;background:linear-gradient(135deg,rgba(124,92,246,.05),rgba(45,212,191,.04));color:#7b879a;font-size:8px;line-height:1.6}.forge-org-gap-note strong{color:#596579}.forge-org-gap-action{width:100%;margin-top:17px;display:flex;align-items:center;justify-content:center;gap:8px;min-height:40px;border:1px solid rgba(124,92,246,.18);border-radius:12px;background:rgba(255,255,255,.62);color:#5d4acb;font:inherit;font-size:9px;font-weight:900;cursor:pointer;transition:.25s}.forge-org-gap-action:hover{transform:translateY(-2px);background:#fff;box-shadow:0 12px 28px rgba(99,82,210,.10)}

/* ---------- MODULE CARDS ---------- */
.forge-org-section-title{display:flex;align-items:end;justify-content:space-between;gap:18px;margin:32px 0 13px}.forge-org-section-title h2{margin:0;color:#202a3c;font-size:24px;letter-spacing:-.04em}.forge-org-section-title p{margin:4px 0 0;color:#98a2b3;font-size:8px;letter-spacing:.12em;font-weight:900}.forge-org-module-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}.forge-org-module{position:relative;min-height:190px;padding:21px;text-align:left;border:1px solid rgba(255,255,255,.84);border-radius:21px;background:rgba(255,255,255,.65);color:#172033;cursor:pointer;overflow:hidden;box-shadow:0 18px 45px rgba(71,85,105,.08),inset 0 1px 0 rgba(255,255,255,.94);backdrop-filter:blur(19px);transition:transform .32s,border-color .32s,box-shadow .32s,background .32s}.forge-org-module:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(280px 180px at 100% 0%,rgba(124,92,246,.12),transparent 70%)}.forge-org-module:nth-child(2):before{background:radial-gradient(280px 180px at 100% 0%,rgba(56,189,248,.12),transparent 70%)}.forge-org-module:nth-child(3):before{background:radial-gradient(280px 180px at 100% 0%,rgba(244,114,182,.10),transparent 70%)}.forge-org-module:nth-child(4):before{background:radial-gradient(280px 180px at 100% 0%,rgba(45,212,191,.12),transparent 70%)}.forge-org-module:hover{transform:translateY(-7px);border-color:rgba(124,92,246,.24);box-shadow:0 28px 65px rgba(71,85,105,.13),0 0 30px rgba(124,92,246,.07)}.forge-org-module-icon{position:relative;width:46px;height:46px;display:grid;place-items:center;border-radius:14px;border:1px solid rgba(124,92,246,.15);background:linear-gradient(145deg,rgba(124,92,246,.10),rgba(255,255,255,.55));color:#7359e7;box-shadow:0 8px 22px rgba(124,92,246,.08);transition:.3s}.forge-org-module:nth-child(2) .forge-org-module-icon{color:#259fd3}.forge-org-module:nth-child(3) .forge-org-module-icon{color:#d84d91}.forge-org-module:nth-child(4) .forge-org-module-icon{color:#159f8e}.forge-org-module:hover .forge-org-module-icon{transform:scale(1.06) rotate(-3deg);box-shadow:0 12px 28px rgba(124,92,246,.15)}.forge-org-module b{position:relative;display:block;margin-top:20px;color:#253044;font-size:16px;letter-spacing:-.025em}.forge-org-module span{position:relative;display:block;margin-top:7px;max-width:240px;color:#7a879b;font-size:9px;line-height:1.6}.forge-org-module-arrow{position:absolute;right:18px;bottom:17px;color:#9aa3b3;transition:.25s}.forge-org-module:hover .forge-org-module-arrow{transform:translateX(5px);color:#6754d8}

/* ---------- MARKET INTELLIGENCE ---------- */
.forge-org-market-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:15px}.forge-org-market-panel{padding:22px;border:1px solid rgba(255,255,255,.84);border-radius:21px;background:rgba(255,255,255,.64);box-shadow:0 18px 48px rgba(71,85,105,.08),inset 0 1px 0 rgba(255,255,255,.94);backdrop-filter:blur(18px)}.forge-org-market-panel h3{margin:0;color:#27324a;font-size:14px}.forge-org-market-panel>p{margin:6px 0 0;color:#8792a5;font-size:9px;line-height:1.55}.forge-org-market-stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:16px}.forge-org-market-stat{padding:13px;border:1px solid rgba(148,163,184,.11);border-radius:13px;background:rgba(248,250,252,.58)}.forge-org-market-stat strong{display:block;color:#4e5ed2;font-size:21px;letter-spacing:-.04em}.forge-org-market-stat span{display:block;margin-top:4px;color:#8994a6;font-size:8px}.forge-org-market-insight{display:flex;gap:11px;align-items:flex-start;margin-top:15px;padding:13px;border-radius:14px;background:linear-gradient(135deg,rgba(124,92,246,.06),rgba(45,212,191,.05));border:1px solid rgba(124,92,246,.10)}.forge-org-market-insight svg{color:#7459e8;flex:0 0 auto}.forge-org-market-insight strong{display:block;color:#465268;font-size:9px}.forge-org-market-insight span{display:block;margin-top:4px;color:#8994a6;font-size:8px;line-height:1.55}

/* ---------- SLIDE DRAWERS ---------- */
.forge-org-drawer-backdrop{position:fixed;inset:0;z-index:500;background:rgba(29,24,51,.24);backdrop-filter:blur(7px);animation:forgeFade .25s ease}.forge-org-drawer{position:absolute;right:18px;top:18px;bottom:18px;width:min(650px,calc(100% - 36px));padding:25px;border:1px solid rgba(255,255,255,.88);border-radius:26px;background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(245,248,255,.91));box-shadow:-20px 30px 100px rgba(50,44,87,.22),inset 0 1px 0 #fff;overflow:auto;animation:forgeDrawerIn .4s cubic-bezier(.2,.8,.2,1)}.forge-org-drawer-head{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.forge-org-drawer-head h2{margin:0;color:#172033;font-size:25px;letter-spacing:-.045em}.forge-org-drawer-head p{margin:6px 0 0;color:#7a879a;font-size:9px;line-height:1.55}.forge-org-drawer-close{width:34px;height:34px;display:grid;place-items:center;border:1px solid rgba(148,163,184,.16);border-radius:10px;background:#fff;color:#667085;cursor:pointer}.forge-org-detail-card{margin-top:15px;padding:16px;border:1px solid rgba(148,163,184,.13);border-radius:16px;background:rgba(255,255,255,.66)}.forge-org-detail-card strong{color:#344054;font-size:10px}.forge-org-detail-card p{margin:6px 0 0;color:#7c8799;font-size:9px;line-height:1.6}.forge-org-role-gap{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:12px 0;border-bottom:1px solid rgba(148,163,184,.10)}.forge-org-role-gap:last-child{border-bottom:0}.forge-org-role-gap strong{color:#465268;font-size:9px}.forge-org-role-gap span{color:#7c8799;font-size:8px}.forge-org-skill-mini{display:flex;align-items:center;justify-content:space-between;gap:10px}.forge-org-skill-mini+ .forge-org-skill-mini{margin-top:10px}.forge-org-skill-mini label{color:#566277;font-size:9px}.forge-org-skill-mini .track{width:150px;height:7px;border-radius:99px;background:#edf0f5;overflow:hidden}.forge-org-skill-mini .track i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#8b5cf6,#38bdf8,#2dd4bf)}

@keyframes forgeOrgReveal{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes forgeOrgAmbient{from{transform:translate3d(0,0,0)}to{transform:translate3d(-35px,28px,0)}}
@keyframes forgeOrgOrbit{to{transform:rotate(360deg)}}
@keyframes forgeWave{0%,60%,100%{transform:rotate(0deg)}10%,30%{transform:rotate(15deg)}20%{transform:rotate(-9deg)}40%{transform:rotate(10deg)}50%{transform:rotate(-4deg)}}
@keyframes forgeOrgBlink{0%,100%{opacity:.55}50%{opacity:1;transform:scale(1.25)}}
@keyframes forgeOrgMountain{from{transform:translateX(-2%) scaleX(1)}to{transform:translateX(2%) scaleX(1.04)}}
@keyframes forgeDrawLine{to{stroke-dashoffset:0}}
@keyframes forgePointIn{from{opacity:0;transform:scale(.5)}to{opacity:1;transform:scale(1)}}
@keyframes forgeGapGrow{from{width:0!important}to{}}
@keyframes forgeFade{from{opacity:0}to{opacity:1}}
@keyframes forgeDrawerIn{from{opacity:0;transform:translateX(35px)}to{opacity:1;transform:translateX(0)}}
@media(max-width:1120px){.forge-org-dashboard-layout{grid-template-columns:205px minmax(0,1fr)}.forge-org-analytics-grid{grid-template-columns:1fr}.forge-org-market-grid{grid-template-columns:1fr}.forge-org-module-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:820px){.forge-org-dashboard-layout{grid-template-columns:1fr}.forge-org-sidebar{position:relative;min-height:auto}.forge-org-sidebar-foot{display:none}.forge-org-metrics{grid-template-columns:repeat(2,1fr)}.forge-org-hero{grid-template-columns:1fr}.forge-org-hero-side{min-height:190px}.forge-org-role-cards{grid-template-columns:1fr}.forge-org-form-grid{grid-template-columns:1fr}.forge-org-role-cards .forge-org-role-card{min-height:330px}.forge-org-chart-wrap{height:300px}}
@media(max-width:560px){.forge-org-shell{width:min(100% - 24px,1480px)}.forge-org-access-page{padding:20px 13px 50px!important}.forge-org-access-top{margin-bottom:38px}.forge-org-access-brand b{display:none}.forge-org-access-copy h1{font-size:43px}.forge-org-profile-form{padding:20px}.forge-org-form-submit-row{flex-direction:column;align-items:stretch}.forge-org-submit{width:100%}.forge-org-metrics{grid-template-columns:1fr}.forge-org-module-grid{grid-template-columns:1fr}.forge-org-role-cards{margin-top:30px}.forge-org-hero-copy{padding:27px 23px}.forge-org-hero-copy h1{font-size:43px}.forge-org-chart-wrap{height:270px}.forge-org-dashboard-page .forge-org-role-cards{grid-template-columns:repeat(2,1fr)}.forge-org-role-card-mini{min-width:0}.forge-org-gap-row{grid-template-columns:85px 1fr 38px}.forge-org-topbar{justify-content:flex-end}.forge-org-user-copy{display:block}.forge-org-drawer{right:8px;top:8px;bottom:8px;width:calc(100% - 16px)}}
`;


const FORGE_ORG_DASHBOARD_CSS = `
/* =========================================================
   FORGE ORGANIZATION — PREMIUM LIGHT GLASS / COMMAND CENTER
   Scoped to organization auth + dashboard only.
========================================================= */
.forge-org-page.forge-org-dashboard-page{
  --fg-ink:#16213a;--fg-muted:#66738d;--fg-line:rgba(93,77,180,.14);
  --fg-purple:#7656ff;--fg-blue:#3d8dff;--fg-pink:#ed4f91;--fg-mint:#12b89f;
  min-height:100vh!important;color:var(--fg-ink)!important;
  background:
    radial-gradient(900px 560px at 12% -10%,rgba(155,122,255,.24),transparent 62%),
    radial-gradient(780px 520px at 92% 4%,rgba(103,226,207,.20),transparent 64%),
    radial-gradient(800px 520px at 55% 108%,rgba(180,201,255,.25),transparent 68%),
    linear-gradient(135deg,#f7f6ff 0%,#f5f8ff 48%,#f3fcfa 100%)!important;
}
.forge-org-dashboard-page:before{
  opacity:.7!important;background-image:
    linear-gradient(rgba(103,78,206,.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(103,78,206,.055) 1px,transparent 1px)!important;
  background-size:38px 38px!important;
}
.forge-org-dashboard-page:after{background:radial-gradient(circle,rgba(119,91,255,.12),transparent 68%)!important}

/* AUTH */
.forge-org-auth.forge-org-access-page{
  background:
    radial-gradient(760px 460px at 12% 4%,rgba(141,113,255,.22),transparent 65%),
    radial-gradient(650px 440px at 92% 12%,rgba(91,220,201,.16),transparent 64%),
    linear-gradient(135deg,#f8f7ff,#f2f7ff 55%,#f2fbf9)!important;
}
.forge-org-auth .forge-org-access-shell{max-width:1180px}
.forge-org-auth .forge-org-access-top{margin-bottom:42px}
.forge-org-auth .forge-org-access-brand span{
  width:46px;height:46px;border-radius:14px;
  background:linear-gradient(145deg,#7957ff,#4e7fff 55%,#21c5aa);
  box-shadow:0 14px 35px rgba(94,77,220,.25),0 0 0 6px rgba(255,255,255,.45);
}
.forge-org-auth .forge-org-role-screen{
  padding:28px 0 56px;border-radius:34px;
}
.forge-org-auth .forge-org-access-copy h1{
  text-shadow:0 10px 35px rgba(83,69,160,.10);
}
.forge-org-auth .forge-org-role-cards{gap:28px;margin-top:48px}
.forge-org-auth .forge-org-role-card{
  min-height:390px!important;
  border-radius:30px!important;
  background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(248,250,255,.70))!important;
  box-shadow:0 25px 80px rgba(75,65,130,.12),inset 0 1px 0 #fff!important;
}
.forge-org-auth .forge-org-role-card:before{animation:forgeRoleAura 7s ease-in-out infinite alternate}
.forge-org-auth .forge-org-role-card:nth-child(2):before{animation-delay:-2.5s}
.forge-org-auth .forge-org-role-card:hover{transform:translateY(-12px) scale(1.015)!important}
.forge-org-auth .forge-org-role-card h2{font-size:38px}
.forge-org-auth .forge-org-role-pills span{background:rgba(255,255,255,.72);box-shadow:0 5px 18px rgba(80,70,130,.04)}
.forge-org-auth .forge-org-role-enter{
  padding:11px 15px;border-radius:12px;background:rgba(119,86,255,.08);
  color:#5e49d2;transition:.25s;
}
.forge-org-auth .forge-org-role-card:hover .forge-org-role-enter{background:rgba(119,86,255,.14);box-shadow:0 10px 25px rgba(93,73,210,.10)}

/* SIDEBAR / NAV */
.forge-org-dashboard-layout{grid-template-columns:236px minmax(0,1fr)!important;gap:24px!important;padding:22px 0 70px!important}
.forge-org-sidebar{
  min-height:calc(100vh - 44px)!important;padding:20px 13px!important;
  border-radius:26px!important;background:rgba(255,255,255,.66)!important;
  border:1px solid rgba(255,255,255,.88)!important;
  box-shadow:0 24px 75px rgba(73,72,126,.13),inset 0 1px 0 #fff!important;
}
.forge-org-brand{padding:4px 10px 27px!important}
.forge-org-brand img{width:46px!important;height:46px!important;border-radius:14px!important}
.forge-org-brand strong{font-size:18px!important;letter-spacing:.22em!important}
.forge-org-nav-group{margin-top:15px!important}
.forge-org-nav-label{font-size:7px!important;color:#8f98aa!important}
.forge-org-nav{
  min-height:41px!important;padding:10px 11px!important;border-radius:13px!important;
  font-size:10px!important;transition:transform .22s,background .22s,box-shadow .22s,color .22s!important;
}
.forge-org-nav:hover{transform:translateX(4px)!important;background:linear-gradient(90deg,rgba(119,86,255,.10),rgba(87,215,198,.04))!important}
.forge-org-nav.active{
  background:linear-gradient(100deg,rgba(119,86,255,.19),rgba(74,137,255,.08))!important;
  border-color:rgba(119,86,255,.23)!important;box-shadow:0 10px 28px rgba(98,78,204,.12)!important;
}
.forge-org-nav svg{filter:drop-shadow(0 0 5px rgba(118,86,255,.22))}

/* TOP USER */
.forge-org-topbar{height:58px!important;margin-bottom:12px!important}
.forge-org-user{
  padding:7px 10px!important;border-radius:17px!important;
  background:rgba(255,255,255,.72)!important;
  border-color:rgba(255,255,255,.92)!important;
  box-shadow:0 12px 30px rgba(73,72,126,.08)!important;
}
.forge-org-avatar{width:39px!important;height:39px!important;background:linear-gradient(145deg,#dacdff,#aeb7ff 55%,#a4eee1)!important;color:#4c3a91!important;box-shadow:0 7px 18px rgba(93,75,200,.16)}
.forge-org-user-copy strong{font-size:10px!important;color:#202b40!important}
.forge-org-user-copy span{font-size:7px!important}
.forge-org-signout{background:rgba(255,255,255,.72)!important}

/* HERO */
.forge-org-hero{grid-template-columns:minmax(0,1.52fr) minmax(300px,.72fr)!important;gap:18px!important}
.forge-org-hero-copy{
  min-height:264px!important;padding:37px 39px!important;border-radius:30px!important;
  background:
    radial-gradient(500px 220px at 8% 0%,rgba(131,91,255,.15),transparent 70%),
    linear-gradient(135deg,rgba(255,255,255,.90),rgba(246,241,255,.73))!important;
  box-shadow:0 27px 80px rgba(75,65,140,.12),inset 0 1px 0 #fff!important;
}
.forge-org-hero-copy h1{font-size:clamp(46px,5.1vw,76px)!important}
.forge-org-hero-copy p{font-size:13px!important;color:#68758c!important}
.forge-org-hero-side{
  min-height:264px!important;border-radius:30px!important;
  background:
    radial-gradient(240px 190px at 70% 0%,rgba(123,91,255,.14),transparent 70%),
    linear-gradient(145deg,rgba(239,235,255,.78),rgba(228,250,247,.64))!important;
}
.forge-org-hero-side:before{width:280px!important;height:280px!important}
.forge-org-date .day{color:#6e7890!important}
.forge-org-date .date{font-size:34px!important;color:#18223a!important}
.forge-org-date .company{color:#6249d8!important}
.forge-org-date .future{color:#718096!important}
.forge-wave{font-size:.78em;display:inline-block!important;animation:forgeWave 1.65s ease-in-out infinite!important}

/* KPI CARDS */
.forge-org-metrics{gap:17px!important;margin-top:19px!important}
.forge-org-metric{
  min-height:165px!important;padding:22px 23px 20px!important;border-radius:23px!important;
  cursor:pointer;isolation:isolate;
  background:rgba(255,255,255,.68)!important;
  box-shadow:0 21px 58px rgba(71,76,125,.11),inset 0 1px 0 #fff!important;
  transition:transform .32s cubic-bezier(.2,.8,.2,1),box-shadow .32s,border-color .32s,filter .32s!important;
}
.forge-org-metric:hover{transform:translateY(-8px) scale(1.012)!important;filter:saturate(1.06)}
.forge-org-metric.metric-selected{
  transform:translateY(-10px) scale(1.018)!important;
  border-color:rgba(109,83,235,.35)!important;
  box-shadow:0 31px 78px rgba(78,69,146,.17),0 0 0 2px rgba(125,96,255,.08),inset 0 1px 0 #fff!important;
}
.forge-org-metric:before{
  left:-7%!important;right:-7%!important;bottom:-42px!important;height:102px!important;
  opacity:1!important;filter:blur(.2px)!important;transform-origin:center bottom;
}
.forge-org-metric.metric-blue:before{background:linear-gradient(180deg,transparent 0%,rgba(62,119,255,.02) 28%,rgba(62,119,255,.20) 100%),radial-gradient(ellipse at 50% 100%,rgba(57,116,255,.28),transparent 68%)!important}
.forge-org-metric.metric-purple:before{background:linear-gradient(180deg,transparent,rgba(126,82,255,.16)),radial-gradient(ellipse at 50% 100%,rgba(126,82,255,.31),transparent 68%)!important}
.forge-org-metric.metric-red:before{background:linear-gradient(180deg,transparent,rgba(236,71,112,.14)),radial-gradient(ellipse at 50% 100%,rgba(236,71,112,.29),transparent 68%)!important}
.forge-org-metric.metric-green:before{background:linear-gradient(180deg,transparent,rgba(16,185,155,.14)),radial-gradient(ellipse at 50% 100%,rgba(16,185,155,.30),transparent 68%)!important}
.forge-org-metric:after{right:-18px!important;top:-18px!important;width:125px!important;height:125px!important}
.forge-org-metric small{font-size:8px!important}
.forge-org-metric strong{
  font-size:39px!important;margin-top:10px!important;
  text-shadow:0 7px 22px currentColor!important;
  animation:forgeMetricFloat 3.8s ease-in-out infinite;
}
.forge-org-metric span{font-size:9px!important}
.forge-org-metric-change{
  margin-top:9px!important;background:rgba(16,185,129,.09)!important;
  color:#0b9a6d!important;border:1px solid rgba(16,185,129,.08);
}
.forge-org-metric-change.down{background:rgba(239,68,68,.08)!important;color:#d83f62!important;border-color:rgba(239,68,68,.08)}
.forge-org-metric-change.neutral{background:rgba(99,102,241,.07)!important;color:#6655c9!important}

/* ANALYTICS */
.forge-org-analytics-grid{grid-template-columns:minmax(0,1.56fr) minmax(370px,.84fr)!important;gap:18px!important;margin-top:20px!important}
.forge-org-chart-panel,.forge-org-gap-panel{
  border-radius:25px!important;background:rgba(255,255,255,.69)!important;
  box-shadow:0 24px 68px rgba(71,76,125,.10),inset 0 1px 0 #fff!important;
}
.forge-org-chart-panel{padding:23px!important}
.forge-org-gap-panel{padding:23px!important}
.forge-org-panel-head strong{font-size:17px!important}
.forge-org-panel-head>span{font-size:7px!important}
.forge-org-transform-legend{gap:18px!important;margin-top:11px!important}
.forge-org-transform-legend span{font-size:9px!important;color:#66738d!important}
.forge-org-transform-legend i{height:4px!important;width:21px!important;box-shadow:0 0 10px currentColor}
.forge-org-transform-legend .current{background:#6257f2!important;color:#6257f2}
.forge-org-transform-legend .post{background:#22aeea!important;color:#22aeea}
.forge-org-transform-legend .future{background:#c14dff!important;color:#c14dff}
.forge-org-chart-wrap{height:365px!important;margin-top:12px!important;padding:4px 2px 0!important}
.forge-org-chart{overflow:visible!important}
.forge-org-chart-grid{stroke:rgba(94,82,159,.14)!important;stroke-dasharray:3 5}
.forge-org-chart-axis,.forge-org-chart-x{fill:#76839a!important;font-size:10px!important}
.forge-org-chart-line,.forge-org-chart-line-post,.forge-org-chart-line-future{stroke-width:4!important}
.forge-org-chart-point,.forge-org-chart-point-post,.forge-org-chart-point-future{r:4.5!important}
.forge-org-chart-empty{
  border:1px dashed rgba(118,86,255,.18);border-radius:18px;
  background:linear-gradient(135deg,rgba(119,86,255,.035),rgba(45,212,191,.03));
  color:#718096!important;
}
.forge-org-gap-list{gap:17px!important;margin-top:25px!important}
.forge-org-gap-row{grid-template-columns:105px 1fr 45px!important}
.forge-org-gap-row label{font-size:10px!important;color:#536078!important}
.forge-org-gap-track{height:12px!important;background:rgba(93,84,145,.09)!important}
.forge-org-gap-track i{background:linear-gradient(90deg,#8d5cff,#687bff 55%,#20cbb1)!important;box-shadow:0 0 18px rgba(112,82,239,.26)!important}
.forge-org-gap-row em{font-size:10px!important;color:#43506a!important}
.forge-org-gap-note{font-size:9px!important;margin-top:20px!important}
.forge-org-gap-action{
  min-height:44px!important;border-radius:13px!important;font-size:10px!important;
  background:linear-gradient(135deg,rgba(255,255,255,.82),rgba(241,238,255,.74))!important;
}
.forge-org-gap-action:hover{transform:translateY(-4px)!important;box-shadow:0 15px 32px rgba(93,75,200,.14)!important}

/* MODULES */
.forge-org-section-title{margin:35px 0 14px!important}
.forge-org-section-title h2{font-size:26px!important}
.forge-org-section-title p{font-size:8px!important;color:#7e89a0!important}
.forge-org-module-grid{gap:15px!important}
.forge-org-module{
  min-height:205px!important;padding:22px!important;border-radius:22px!important;
  box-shadow:0 20px 52px rgba(71,76,125,.09),inset 0 1px 0 #fff!important;
}
.forge-org-module:after{
  content:"";position:absolute;left:-15%;right:-15%;bottom:-58px;height:105px;border-radius:50%;
  opacity:.65;animation:forgeModuleWave 5s ease-in-out infinite alternate;
}
.forge-org-module:nth-child(1){background:linear-gradient(145deg,rgba(245,242,255,.84),rgba(235,243,255,.68))!important}
.forge-org-module:nth-child(1):after{background:radial-gradient(ellipse,rgba(80,112,255,.25),transparent 65%)}
.forge-org-module:nth-child(2){background:linear-gradient(145deg,rgba(246,241,255,.84),rgba(250,239,255,.68))!important}
.forge-org-module:nth-child(2):after{background:radial-gradient(ellipse,rgba(157,80,255,.25),transparent 65%)}
.forge-org-module:nth-child(3){background:linear-gradient(145deg,rgba(255,245,249,.82),rgba(255,239,246,.66))!important}
.forge-org-module:nth-child(3):after{background:radial-gradient(ellipse,rgba(238,76,132,.22),transparent 65%)}
.forge-org-module:nth-child(4){background:linear-gradient(145deg,rgba(240,255,251,.84),rgba(233,249,255,.68))!important}
.forge-org-module:nth-child(4):after{background:radial-gradient(ellipse,rgba(22,191,169,.25),transparent 65%)}
.forge-org-module:hover{transform:translateY(-9px) scale(1.012)!important}
.forge-org-module-icon{width:51px!important;height:51px!important;border-radius:15px!important}
.forge-org-module b{font-size:17px!important;margin-top:21px!important}
.forge-org-module span{font-size:9px!important}

/* MARKET */
.forge-org-market-grid{gap:17px!important}
.forge-org-market-panel{border-radius:22px!important;background:rgba(255,255,255,.68)!important;box-shadow:0 20px 54px rgba(71,76,125,.08),inset 0 1px 0 #fff!important}
.forge-org-market-stat-grid{gap:11px!important}
.forge-org-market-stat{background:linear-gradient(135deg,rgba(249,248,255,.80),rgba(238,250,248,.54))!important}
.forge-org-market-stat strong{font-size:25px!important;text-shadow:0 6px 18px currentColor}
.forge-org-market-insight{background:linear-gradient(135deg,rgba(121,88,255,.07),rgba(45,212,191,.05))!important}

/* DRAWER */
.forge-org-drawer{width:min(690px,calc(100% - 36px))!important;border-radius:28px!important}
.forge-org-detail-card{box-shadow:0 10px 28px rgba(71,76,125,.05);background:rgba(255,255,255,.75)!important}

/* ANIMATION */
@keyframes forgeMetricFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
@keyframes forgeRoleAura{from{transform:translate3d(-8px,0,0) scale(1)}to{transform:translate3d(8px,7px,0) scale(1.04)}}
@keyframes forgeModuleWave{from{transform:translateX(-2%) scaleX(1)}to{transform:translateX(2%) scaleX(1.06)}}

@media(max-width:1120px){
  .forge-org-dashboard-layout{grid-template-columns:210px minmax(0,1fr)!important}
  .forge-org-analytics-grid{grid-template-columns:1fr!important}
}
@media(max-width:820px){
  .forge-org-dashboard-layout{grid-template-columns:1fr!important}
  .forge-org-sidebar{position:relative!important;min-height:auto!important}
  .forge-org-sidebar-foot{display:none!important}
  .forge-org-hero{grid-template-columns:1fr!important}
  .forge-org-metrics{grid-template-columns:repeat(2,1fr)!important}
  .forge-org-module-grid{grid-template-columns:repeat(2,1fr)!important}
}
@media(max-width:560px){
  .forge-org-metrics,.forge-org-module-grid{grid-template-columns:1fr!important}
  .forge-org-role-cards{grid-template-columns:1fr!important}
  .forge-org-chart-wrap{height:300px!important}
}

/* =========================================================
   WORKFORCE TRANSFORMATION — PLOTTED ZIG-ZAG SIGNAL GRAPH
   Designed around the requested FORGE analytics reference.
========================================================= */
.forge-org-transform-head{
  position:relative;
  padding-bottom:2px;
}
.forge-org-transform-eyebrow{
  display:block!important;
  margin-bottom:7px!important;
  color:#7c68e8!important;
  font-size:8px!important;
  font-weight:950!important;
  letter-spacing:.19em!important;
}
.forge-org-transform-head strong{
  display:block!important;
  font-size:25px!important;
  line-height:1.02!important;
  letter-spacing:-.045em!important;
  color:#1b2334!important;
}
.forge-org-transform-head strong em{
  color:#7658ec!important;
  font-style:normal!important;
}
.forge-org-transform-subtitle{
  margin-top:8px!important;
  color:#8b95a8!important;
  font-size:8px!important;
  font-weight:850!important;
  letter-spacing:.13em!important;
}
.forge-org-transform-legend{
  margin-top:16px!important;
  gap:14px 20px!important;
}
.forge-org-transform-legend span{
  color:#66738d!important;
  font-size:9px!important;
  font-weight:800!important;
}
.forge-org-transform-legend i{
  width:24px!important;
  height:4px!important;
  border-radius:999px!important;
  box-shadow:0 0 12px currentColor!important;
}
.forge-org-transform-legend .current{
  background:linear-gradient(90deg,#6557ef,#397dff)!important;
  color:#5b67f4!important;
}
.forge-org-transform-legend .post{
  background:linear-gradient(90deg,#20b7ef,#13b8a4)!important;
  color:#18b9d7!important;
}
.forge-org-transform-legend .future{
  background:linear-gradient(90deg,#a450ff,#ed50d4)!important;
  color:#bd55ed!important;
}
.forge-org-chart-wrap{
  position:relative!important;
  height:365px!important;
  margin-top:18px!important;
  padding:2px 0 0!important;
  border-radius:18px!important;
  background:
    radial-gradient(420px 190px at 12% 90%,rgba(102,82,242,.045),transparent 70%),
    radial-gradient(420px 190px at 92% 15%,rgba(58,130,246,.035),transparent 70%);
}
.forge-org-chart{
  width:100%!important;
  height:100%!important;
  display:block!important;
}
.forge-org-chart-grid{
  stroke:rgba(94,82,159,.13)!important;
  stroke-width:1!important;
  stroke-dasharray:3 6!important;
}
.forge-org-chart-axis{
  fill:#8a94a7!important;
  font-size:10px!important;
  font-weight:650!important;
}
.forge-org-chart-x{
  fill:#6f7b91!important;
  font-size:10px!important;
  font-weight:800!important;
}
.forge-org-chart-axis-line{
  stroke:rgba(91,82,145,.16)!important;
  stroke-width:1!important;
}
.forge-org-projection-line{
  stroke:rgba(173,84,255,.30)!important;
  stroke-width:1!important;
  stroke-dasharray:4 5!important;
}
.forge-org-projection-label{
  fill:#a177d8!important;
  font-size:8px!important;
  font-weight:900!important;
  letter-spacing:.12em!important;
}
.forge-org-chart-line,
.forge-org-chart-line-post,
.forge-org-chart-line-future{
  fill:none!important;
  stroke-width:3.8!important;
  stroke-linecap:round!important;
  stroke-linejoin:round!important;
  filter:url(#forgeTransformGlow)!important;
}
.forge-org-chart-line{
  stroke:url(#forgeTransformCurrent)!important;
  stroke-dasharray:none!important;
  stroke-dashoffset:0!important;
  opacity:1!important;
}
.forge-org-chart-line-post{
  stroke:url(#forgeTransformPost)!important;
  stroke-dasharray:none!important;
  stroke-dashoffset:0!important;
  opacity:1!important;
}
.forge-org-chart-line-future{
  stroke:url(#forgeTransformFuture)!important;
  stroke-dasharray:none!important;
  stroke-dashoffset:0!important;
  opacity:1!important;
}
.forge-org-chart-point,
.forge-org-chart-point-post,
.forge-org-chart-point-future{
  fill:#fff!important;
  stroke-width:2.5!important;
}
.forge-org-chart-point{
  stroke:#6557ef!important;
  filter:drop-shadow(0 0 7px rgba(101,87,239,.65))!important;
}
.forge-org-chart-point-post{
  stroke:#20b7ef!important;
  filter:drop-shadow(0 0 7px rgba(32,183,239,.65))!important;
}
.forge-org-chart-point-future{
  stroke:#c04ff0!important;
  filter:drop-shadow(0 0 7px rgba(192,79,240,.65))!important;
}
.forge-chart-hit{cursor:crosshair}
.forge-chart-hit-area{
  fill:transparent!important;
  stroke:transparent!important;
}
.forge-chart-tooltip rect{
  fill:rgba(18,24,39,.94)!important;
  stroke:rgba(157,125,255,.38)!important;
  stroke-width:1!important;
  filter:drop-shadow(0 12px 22px rgba(24,20,57,.18));
}
.forge-chart-tooltip text{
  fill:#fff!important;
  font-size:9px!important;
  font-weight:750!important;
}
.forge-org-chart-empty{
  min-height:300px!important;
  height:100%!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  flex-direction:column!important;
  gap:8px!important;
  padding:30px!important;
  text-align:center!important;
  border:1px dashed rgba(118,86,255,.20)!important;
  border-radius:20px!important;
  background:
    radial-gradient(350px 180px at 50% 45%,rgba(118,86,255,.08),transparent 70%),
    linear-gradient(135deg,rgba(119,86,255,.025),rgba(45,212,191,.025))!important;
}
.forge-org-chart-empty-kicker{
  color:#8066e9!important;
  font-size:8px!important;
  font-weight:950!important;
  letter-spacing:.18em!important;
}
.forge-org-chart-empty strong{
  color:#33405a!important;
  font-size:17px!important;
}
.forge-org-chart-empty span{
  max-width:430px!important;
  color:#7d889c!important;
  font-size:10px!important;
  line-height:1.6!important;
}
@media(max-width:700px){
  .forge-org-transform-head strong{font-size:21px!important}
  .forge-org-transform-legend{gap:10px!important}
  .forge-org-chart-wrap{height:315px!important}
}

/* =========================================================
   FINAL TRANSFORMATION HEADER — PREMIUM FORGE ANALYTICS
   Refines the hierarchy without changing the JSX/content.
========================================================= */
.forge-org-transform-head{
  position:relative!important;
  display:block!important;
  padding:2px 0 0!important;
  margin:0!important;
}

.forge-org-transform-head > div{
  position:relative!important;
  z-index:2!important;
  padding-right:210px!important;
}

.forge-org-transform-head > span{
  position:absolute!important;
  top:2px!important;
  right:0!important;
  display:inline-flex!important;
  align-items:center!important;
  gap:7px!important;
  height:27px!important;
  padding:0 11px!important;
  border:1px solid rgba(112,91,230,.16)!important;
  border-radius:999px!important;
  background:rgba(247,248,252,.82)!important;
  color:#7b8497!important;
  font-size:7px!important;
  font-weight:950!important;
  letter-spacing:.13em!important;
  box-shadow:0 5px 18px rgba(77,70,130,.07),inset 0 1px 0 #fff!important;
  white-space:nowrap!important;
}

.forge-org-transform-head > span::before{
  content:""!important;
  width:6px!important;
  height:6px!important;
  border-radius:50%!important;
  background:linear-gradient(135deg,#7359ee,#3ebddc)!important;
  box-shadow:0 0 0 4px rgba(115,89,238,.08),0 0 12px rgba(78,174,223,.35)!important;
}

.forge-org-transform-eyebrow{
  display:inline-flex!important;
  align-items:center!important;
  gap:9px!important;
  margin:0 0 11px!important;
  padding:6px 10px!important;
  border:1px solid rgba(117,91,232,.14)!important;
  border-radius:999px!important;
  background:linear-gradient(90deg,rgba(119,91,237,.07),rgba(67,190,220,.045))!important;
  color:#735de2!important;
  font-size:8px!important;
  font-weight:950!important;
  letter-spacing:.18em!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.85)!important;
}

.forge-org-transform-eyebrow::before{
  content:""!important;
  width:5px!important;
  height:5px!important;
  border-radius:50%!important;
  background:#7659ec!important;
  box-shadow:0 0 0 4px rgba(118,89,236,.09),0 0 11px rgba(118,89,236,.38)!important;
}

.forge-org-transform-head strong{
  display:block!important;
  max-width:760px!important;
  margin:0!important;
  color:#1a2232!important;
  font-size:clamp(31px,3.15vw,43px)!important;
  line-height:.98!important;
  letter-spacing:-.055em!important;
  font-weight:780!important;
}

.forge-org-transform-head strong em{
  font-style:normal!important;
  color:transparent!important;
  background:linear-gradient(100deg,#7057e9 0%,#8657ec 48%,#b24fe2 100%)!important;
  -webkit-background-clip:text!important;
  background-clip:text!important;
  text-shadow:none!important;
}

.forge-org-transform-exposure{
  position:relative!important;
  display:flex!important;
  align-items:center!important;
  gap:9px!important;
  width:max-content!important;
  max-width:100%!important;
  margin:13px 0 0!important;
  padding:8px 12px!important;
  border:1px solid rgba(111,91,230,.15)!important;
  border-radius:10px!important;
  background:
    linear-gradient(90deg,rgba(112,87,235,.09),rgba(65,190,219,.055))!important;
  color:#604fd0!important;
  font-size:8px!important;
  font-weight:950!important;
  letter-spacing:.12em!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.9),
    0 8px 24px rgba(88,72,177,.06)!important;
}

.forge-org-transform-exposure::after{
  content:""!important;
  position:absolute!important;
  left:0!important;
  top:7px!important;
  bottom:7px!important;
  width:2px!important;
  border-radius:99px!important;
  background:linear-gradient(180deg,#7a5cf0,#39bfd8)!important;
  box-shadow:0 0 10px rgba(93,91,235,.35)!important;
}

.forge-org-transform-exposure b{
  margin-left:2px!important;
  padding-left:9px!important;
  border-left:1px solid rgba(105,88,206,.15)!important;
  color:#7b8497!important;
  font-size:7px!important;
  font-weight:900!important;
  letter-spacing:.11em!important;
}

.forge-org-exposure-pulse{
  flex:0 0 auto!important;
  width:6px!important;
  height:6px!important;
  border-radius:50%!important;
  background:linear-gradient(135deg,#7758ef,#36bfdc)!important;
  box-shadow:0 0 0 4px rgba(116,88,235,.09),0 0 13px rgba(78,171,222,.38)!important;
}

.forge-org-transform-legend{
  display:flex!important;
  flex-wrap:wrap!important;
  align-items:center!important;
  gap:7px!important;
  margin-top:14px!important;
}

.forge-org-transform-legend span{
  display:inline-flex!important;
  align-items:center!important;
  gap:7px!important;
  min-height:26px!important;
  padding:0 9px!important;
  border:1px solid rgba(106,119,145,.10)!important;
  border-radius:999px!important;
  background:rgba(247,248,251,.72)!important;
  color:#657188!important;
  font-size:8px!important;
  font-weight:850!important;
  letter-spacing:.01em!important;
  box-shadow:inset 0 1px 0 #fff!important;
}

.forge-org-transform-legend i{
  flex:0 0 auto!important;
  width:18px!important;
  height:3px!important;
  border-radius:99px!important;
  box-shadow:none!important;
}

.forge-org-transform-meta{
  display:flex!important;
  flex-wrap:wrap!important;
  align-items:center!important;
  gap:7px!important;
  margin-top:9px!important;
}

.forge-org-transform-meta > span{
  display:inline-flex!important;
  align-items:center!important;
  min-height:23px!important;
  padding:0 9px!important;
  border:1px solid rgba(106,119,145,.09)!important;
  border-radius:8px!important;
  background:rgba(246,247,250,.72)!important;
  color:#8992a3!important;
  font-size:7px!important;
  font-weight:800!important;
  letter-spacing:.04em!important;
}

.forge-org-transform-meta > span b{
  margin-left:4px!important;
  color:#566078!important;
  font-weight:950!important;
}

.forge-org-transform-meta > span.positive{
  border-color:rgba(45,190,165,.16)!important;
  background:rgba(45,190,165,.055)!important;
  color:#249b87!important;
}

@media(max-width:760px){
  .forge-org-transform-head > div{padding-right:0!important}
  .forge-org-transform-head > span{position:static!important;margin-bottom:10px!important}
  .forge-org-transform-head strong{font-size:31px!important}
}

@media(max-width:520px){
  .forge-org-transform-exposure{width:100%!important}
  .forge-org-transform-legend span{width:100%!important;justify-content:flex-start!important}
}

`;

function ForgeOrganizationStyles(){
  return <style>{FORGE_ORG_WORKSPACE_CSS + FORGE_ORG_DASHBOARD_CSS + `
    /* FINAL WINNING OVERRIDES */
    .forge-org-auth .forge-org-access-shell{width:min(1360px,100%)!important}
    .forge-org-auth .forge-org-role-screen{width:100%!important}
    .forge-org-auth .forge-org-role-cards{width:min(1120px,100%)!important;margin:48px auto 0!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:30px!important}
    .forge-org-auth .forge-org-role-card{min-height:430px!important;padding:34px!important}
    .forge-org-auth .forge-org-role-card h2{font-size:42px!important;line-height:.98!important}
    .forge-org-auth .forge-org-role-card p{font-size:13px!important;max-width:470px!important}
    .forge-org-auth .forge-org-role-card-kicker{margin-top:42px!important}
    .forge-org-metric.metric-selected{transform:translateY(-14px) scale(1.035)!important;z-index:8!important;border-color:rgba(103,75,229,.48)!important;box-shadow:0 38px 92px rgba(75,61,160,.23),0 0 0 2px rgba(124,92,246,.12),0 0 38px rgba(124,92,246,.12),inset 0 1px 0 #fff!important}
    .forge-org-metric.metric-selected .forge-org-metric-icon{transform:scale(1.08);box-shadow:0 14px 30px rgba(99,82,210,.16)}
    .forge-org-metric-change{white-space:nowrap!important}
    .forge-org-gap-track{position:relative!important;background:linear-gradient(90deg,rgba(124,92,246,.12),rgba(56,189,248,.07))!important}
    .forge-org-gap-track i{position:absolute!important;left:0;top:0;bottom:0;background:linear-gradient(90deg,#8b5cf6,#687bff 55%,#ec5b86)!important;z-index:1}
    .forge-org-gap-track b{position:absolute!important;right:0;top:0;bottom:0;background:rgba(45,212,191,.30);border-left:1px solid rgba(45,212,191,.75);z-index:2}
    .forge-org-gap-row em{display:flex!important;flex-direction:column;align-items:flex-end;line-height:1!important}
    .forge-org-gap-row em strong{font-size:10px;color:#5d4acb}
    .forge-org-gap-row em small{margin-top:3px;font-size:6px;color:#96a0b1;text-transform:uppercase;letter-spacing:.08em}
    .forge-org-chart-wrap{background:linear-gradient(180deg,rgba(118,86,245,.025),rgba(56,189,248,.02));border-radius:18px}
    .forge-org-chart-panel{box-shadow:0 28px 78px rgba(71,76,125,.13),inset 0 1px 0 #fff!important}
    .forge-org-chart-panel:before,.forge-org-gap-panel:before{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(124,92,246,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(124,92,246,.025) 1px,transparent 1px);background-size:28px 28px;mask-image:linear-gradient(to bottom,#000,transparent 88%)}
    .forge-org-transform-legend span{font-weight:900!important;color:#647089!important}
    .forge-org-transform-legend .current{box-shadow:0 0 12px rgba(99,102,241,.5)}
    .forge-org-transform-legend .post{box-shadow:0 0 12px rgba(56,189,248,.5)}
    .forge-org-transform-legend .future{box-shadow:0 0 12px rgba(192,92,255,.5)}
    .forge-org-chart-axis{font-size:9px!important;font-weight:800!important;fill:#77839a!important}
    .forge-org-chart-x{font-size:9px!important;font-weight:900!important;fill:#647089!important}
    .forge-org-chart-panel .forge-org-gap-action:hover{box-shadow:0 15px 32px rgba(103,84,216,.15)!important}
    .forge-org-drawer{box-shadow:-25px 35px 110px rgba(50,44,87,.26),inset 0 1px 0 #fff!important}
    .forge-org-metric-top{position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:10px}
    .forge-org-metric-icon{width:35px;height:35px;display:grid;place-items:center;border-radius:11px;background:rgba(255,255,255,.52);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 7px 18px rgba(65,70,130,.07)}
    .metric-blue .forge-org-metric-icon{color:#3d7cff}.metric-purple .forge-org-metric-icon{color:#7956e9}.metric-red .forge-org-metric-icon{color:#e34c74}.metric-green .forge-org-metric-icon{color:#0fa98f}
    .forge-org-card-wave{position:absolute;left:-10%;right:-10%;bottom:-22px;height:66px;z-index:0;opacity:.55;clip-path:polygon(0 82%,8% 63%,18% 76%,28% 48%,38% 70%,49% 42%,59% 63%,70% 38%,80% 68%,91% 48%,100% 66%,100% 100%,0 100%);animation:forgeCardWave 4.8s ease-in-out infinite alternate}
    .metric-blue .forge-org-card-wave{background:rgba(55,112,255,.25)}.metric-purple .forge-org-card-wave{background:rgba(126,82,255,.25)}.metric-red .forge-org-card-wave{background:rgba(235,70,110,.23)}.metric-green .forge-org-card-wave{background:rgba(17,185,157,.24)}
    .forge-org-chart-axis-line{stroke:rgba(84,77,145,.20);stroke-width:1}
    @keyframes forgeCardWave{from{transform:translateX(-2%) scaleY(.94)}to{transform:translateX(2%) scaleY(1.08)}}
    .forge-org-chart-panel .forge-org-gap-action,.forge-org-gap-panel .forge-org-gap-action{position:relative;z-index:3}
    .forge-org-transform-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
    .forge-org-transform-meta span{display:inline-flex;align-items:center;gap:4px;padding:5px 8px;border-radius:999px;background:rgba(244,246,255,.82);border:1px solid rgba(111,91,221,.10);color:#7b879c;font-size:7.5px;font-weight:800;letter-spacing:.02em}
    .forge-org-transform-meta b{color:#3e4b64;font-weight:900}
    .forge-org-transform-meta .positive{color:#079b72;background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.13)}
    .forge-org-transform-meta .negative{color:#d33f62;background:rgba(239,68,68,.07);border-color:rgba(239,68,68,.13)}
    .forge-org-chart-area{fill:url(#forgeCurrentArea)!important;opacity:.95}
    .forge-org-projection-line{stroke:rgba(156,92,255,.32);stroke-width:1.5;stroke-dasharray:5 5}
    .forge-org-projection-label{fill:#8b72bd;font-size:8px;font-weight:900;letter-spacing:.10em}
    .forge-chart-hit{cursor:crosshair}
    .forge-chart-hit-area{fill:transparent;stroke:transparent}
    .forge-chart-hit:hover .forge-org-chart-point,
    .forge-chart-hit:hover .forge-org-chart-point-post,
    .forge-chart-hit:hover .forge-org-chart-point-future{r:7;stroke-width:3.2}
    .forge-chart-tooltip rect{fill:rgba(26,25,53,.94);stroke:rgba(181,151,255,.45);filter:drop-shadow(0 9px 18px rgba(48,35,93,.25))}
    .forge-chart-tooltip text{fill:#fff;font-size:8.5px;font-weight:800}
    .forge-chart-tooltip text+text{fill:#d8ceff;font-size:8px;font-weight:700}
    .forge-org-gap-row{grid-template-columns:minmax(125px,1.1fr) 1fr 45px!important}
    .forge-org-gap-label{min-width:0}
    .forge-org-gap-label strong{display:block;color:#3e4c66;font-size:9.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .forge-org-gap-label small{display:block;margin-top:3px;color:#98a2b3;font-size:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .forge-org-gap-row em{font-variant-numeric:tabular-nums}
    .forge-org-gap-panel{background:
      radial-gradient(430px 240px at 100% 0%,rgba(129,92,255,.07),transparent 72%),
      rgba(255,255,255,.69)!important}
    .forge-org-chart-panel{background:
      radial-gradient(520px 260px at 0% 0%,rgba(99,102,241,.055),transparent 72%),
      rgba(255,255,255,.69)!important}
  `}</style>;
}

function OrganizationAuthPage(){
  const navigate = useNavigate();
  const [role,setRole] = useState(null);
  const [name,setName] = useState("");
  const [org,setOrg] = useState("");
  const [designation,setDesignation] = useState("");
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");
  const [confirmPassword,setConfirmPassword] = useState("");
  const [error,setError] = useState("");

  function chooseRole(nextRole){
    setRole(nextRole); setError("");
    setName(""); setOrg(""); setDesignation(""); setEmail(""); setPassword(""); setConfirmPassword("");
  }
  function submit(event){
    event.preventDefault(); setError("");
    if(!name.trim() || !email.trim() || !password.trim() || !org.trim()){setError("Please complete all required fields.");return;}
    if(password.length<6){setError("Password must contain at least 6 characters.");return;}
    if(password!==confirmPassword){setError("Passwords do not match.");return;}
    const session={role,name:name.trim(),organization:org.trim(),designation:designation.trim(),email:email.trim(),authenticatedAt:new Date().toISOString()};
    localStorage.setItem("forge_org_session",JSON.stringify(session));
    navigate(role==="hr_admin"?"/organization/hr":"/organization/employee",{replace:true});
  }
  return <div className="forge-org-page forge-org-auth forge-org-access-page">
    <div className="forge-org-access-shell">
      <div className="forge-org-access-top">
        <button className="forge-org-access-back" type="button" onClick={()=>navigate("/")}>← Back to FORGE</button>
        <div className="forge-org-access-brand"><span>F</span> FORGE <b>ORGANIZATION INTELLIGENCE</b></div>
      </div>
      {!role ? <div className="forge-org-role-screen">
        <div className="forge-org-access-copy">
          <div className="forge-org-kicker"><i/> ORGANIZATION WORKSPACE</div>
          <h1>Choose your <em>FORGE workspace.</em></h1>
          <p>Enter as an HR / Admin decision-maker or as an employee. Your workspace, permissions and intelligence surface are shaped around the role you select.</p>
        </div>
        <div className="forge-org-role-cards">
          <button type="button" className="forge-org-role-card forge-org-role-hr" onClick={()=>chooseRole("hr_admin")}>
            <div className="forge-org-role-card-head"><div className="forge-org-role-card-icon"><Building2 size={25}/></div><span className="forge-org-role-card-number">01 · DECISION MAKER</span></div>
            <div className="forge-org-role-card-kicker">I AM HR / ADMIN</div>
            <h2>Lead the workforce.</h2>
            <p>See the organization through evidence — roles, skills, capability gaps, AI exposure, market signals and workforce transformation.</p>
            <div className="forge-org-role-pills"><span>Workforce intelligence</span><span>Skill gaps</span><span>AI transformation</span><span>Market signals</span></div>
            <span className="forge-org-role-enter">Enter HR / Admin workspace <ArrowRight size={15}/></span>
          </button>
          <button type="button" className="forge-org-role-card forge-org-role-employee" onClick={()=>chooseRole("employee")}>
            <div className="forge-org-role-card-head"><div className="forge-org-role-card-icon"><UserRound size={25}/></div><span className="forge-org-role-card-number">02 · INDIVIDUAL</span></div>
            <div className="forge-org-role-card-kicker">I AM AN EMPLOYEE</div>
            <h2>Build what comes next.</h2>
            <p>Understand your work context, capability exposure and personal skill gaps without exposing organization-wide workforce analytics.</p>
            <div className="forge-org-role-pills"><span>My capability</span><span>My skill gaps</span><span>Work context</span><span>Lattice practice</span></div>
            <span className="forge-org-role-enter">Enter my workspace <ArrowRight size={15}/></span>
          </button>
        </div>
      </div> : <div className="forge-org-form-screen">
        <button className="forge-org-change-role" type="button" onClick={()=>chooseRole(null)}><ChevronLeft size={13}/> Choose a different role</button>
        <div className="forge-org-form-heading"><div className="forge-org-form-role-icon">{role==="hr_admin"?<Building2 size={24}/>:<UserRound size={24}/>}</div><div><h2>{role==="hr_admin"?"Set up your HR / Admin access":"Set up your employee access"}</h2><p>One short profile, then FORGE takes you directly into the right workspace.</p></div></div>
        <form className="forge-org-profile-form" onSubmit={submit}>
          <div className="forge-org-form-grid">
            <div className="forge-org-field"><label>Full name *</label><input required value={name} onChange={e=>setName(e.target.value)} placeholder="Your full name"/></div>
            <div className="forge-org-field"><label>Organization *</label><input required value={org} onChange={e=>setOrg(e.target.value)} placeholder="Company / organization"/></div>
            <div className="forge-org-field"><label>Designation</label><input value={designation} onChange={e=>setDesignation(e.target.value)} placeholder={role==="hr_admin"?"HR Manager / People Lead":"Software Engineer / Analyst"}/></div>
            <div className="forge-org-field"><label>Work email *</label><input required type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@company.com"/></div>
            <div className="forge-org-field"><label>Password *</label><input required minLength={6} type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Minimum 6 characters"/></div>
            <div className="forge-org-field"><label>Confirm password *</label><input required minLength={6} type="password" value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} placeholder="Re-enter password"/></div>
          </div>
          {error&&<div className="forge-org-form-error"><AlertCircle size={15}/>{error}</div>}
          <div className="forge-org-form-submit-row"><div className="forge-org-secure-note"><ShieldCheck size={15}/><span><strong>Role-based workspace</strong><br/>Demo access is stored locally for this prototype.</span></div><button className="forge-org-submit" type="submit">ENTER {role==="hr_admin"?"HR DASHBOARD":"EMPLOYEE DASHBOARD"} <ArrowRight size={16}/></button></div>
        </form>
      </div>}
    </div>
  </div>;
}

function useForgeOrgSession(){
  const [session] = useState(()=>{try{const raw=localStorage.getItem("forge_org_session");return raw?JSON.parse(raw):null;}catch{return null;}});
  return session;
}

function useForgeToday(){
  const [now,setNow]=useState(()=>new Date());
  useEffect(()=>{
    const tick=()=>setNow(new Date());
    const ms=86400000-(Date.now()%86400000)+1000;
    const t=setTimeout(()=>{tick();},ms);
    return ()=>clearTimeout(t);
  },[now]);
  return now;
}

function OrgWorkspaceFrame({children,session,title,subtitle}){
  const navigate=useNavigate();
  const today=useForgeToday();
  function signOut(){localStorage.removeItem("forge_org_session");navigate("/organization");}
  const day=today.toLocaleDateString(undefined,{weekday:"long"});
  const date=today.toLocaleDateString(undefined,{day:"2-digit"});
  const month=today.toLocaleDateString(undefined,{month:"long"});
  const year=today.getFullYear();
  return <div className="forge-org-page forge-org-dashboard-page"><div className="forge-org-shell"><div className="forge-org-dashboard-layout">
    <aside className="forge-org-sidebar">
      <div className="forge-org-brand"><img src="/forge-logo.png" alt="FORGE"/><div><strong>FORGE</strong><small>Organization Intelligence</small></div></div>
      <div className="forge-org-nav-group"><div className="forge-org-nav-label">WORKSPACE</div>
        <button className="forge-org-nav active" onClick={()=>window.scrollTo({top:0,behavior:"smooth"})}><Building2 size={14}/> Overview</button>
        <button className="forge-org-nav" onClick={()=>document.getElementById('market-intelligence')?.scrollIntoView({behavior:'smooth',block:'start'})}><Database size={14}/> MarketTrace</button>
        <button className="forge-org-nav" onClick={()=>document.getElementById('skill-distribution')?.scrollIntoView({behavior:'smooth',block:'start'})}><Brain size={14}/> Skill Success</button>
        <button className="forge-org-nav" onClick={()=>navigate('/workfold')}><Network size={14}/> Scenario / WorkFold</button>
        <button className="forge-org-nav" onClick={()=>navigate('/lattice')}><Target size={14}/> Lattice / Action</button>
      </div>
      <div className="forge-org-nav-group"><div className="forge-org-nav-label">WORKFORCE STRATEGY</div>
        <button className="forge-org-nav" onClick={()=>document.getElementById('capability-gaps')?.scrollIntoView({behavior:'smooth'})}><Target size={14}/> Capability Exposure</button>
        <button className="forge-org-nav" onClick={()=>document.getElementById('capability-gaps')?.scrollIntoView({behavior:'smooth'})}><AlertCircle size={14}/> Workforce Gaps</button>
        <button className="forge-org-nav" onClick={()=>document.getElementById('transformation')?.scrollIntoView({behavior:'smooth'})}><Sparkles size={14}/> AI Transformation</button>
        <button className="forge-org-nav" onClick={()=>document.getElementById('market-intelligence')?.scrollIntoView({behavior:'smooth'})}><Network size={14}/> Future Workforce</button>
      </div>
      <div className="forge-org-nav-group"><div className="forge-org-nav-label">INTELLIGENCE</div><button className="forge-org-nav" onClick={()=>document.getElementById('market-intelligence')?.scrollIntoView({behavior:'smooth'})}><Database size={14}/> Market Intelligence</button></div>
      <div className="forge-org-sidebar-foot">WORK · AI · CAPABILITY · FUTURE</div>
    </aside>
    <div className="forge-org-main">
      <div className="forge-org-topbar"><div className="forge-org-top-actions"><div className="forge-org-user"><div className="forge-org-avatar">{(session?.name||'M').charAt(0).toUpperCase()}</div><div className="forge-org-user-copy"><strong>{session?.organization||'FORGE'}</strong><span>{session?.role==='hr_admin'?'HR / Admin':'Employee'}</span></div></div><button className="forge-org-signout" onClick={signOut}>Sign out</button></div></div>
      <div className="forge-org-hero">
        <div className="forge-org-hero-copy"><div className="forge-org-kicker"><i/> {session?.role==='hr_admin'?'HR / ADMIN · WORKFORCE INTELLIGENCE':'EMPLOYEE · CAPABILITY INTELLIGENCE'}</div><h1>{title}</h1><p>{subtitle}</p></div>
        <div className="forge-org-hero-side"><div className="forge-org-date"><span className="day">{day}</span><span className="date">{date} {month}</span><span className="year">{year}</span><span className="company">{session?.organization||'FORGE'}</span><span className="future">For a future-ready workforce.</span></div><span className="forge-org-live-dot"><i/> DATA SURFACE READY</span></div>
      </div>
      {children}
    </div>
  </div></div></div>;
}

function useForgeAnimatedNumber(value,duration=950){
  const target=Number(value);
  const [display,setDisplay]=useState(Number.isFinite(target)?0:value);
  useEffect(()=>{
    if(!Number.isFinite(target)){setDisplay(value);return;}
    let start=null;
    const frame=(ts)=>{
      if(start===null)start=ts;
      const p=Math.min(1,(ts-start)/duration);
      const eased=1-Math.pow(1-p,3);
      setDisplay(Math.round(target*eased));
      if(p<1)requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  },[value,duration]);
  return Number.isFinite(Number(display))?Number(display).toLocaleString():display;
}

function OrganizationHrDashboard(){
  const session=useForgeOrgSession();
  const [overview,setOverview]=useState(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  const [selectedRole,setSelectedRole]=useState("");

  useEffect(()=>{
    let cancelled=false;
    fetch(`${FORGE_API_BASE}/api/organization/workforce/overview`,{cache:"no-store"})
      .then(r=>r.ok?r.json():Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(data=>{if(!cancelled)setOverview(data)})
      .catch(err=>{if(!cancelled){setError(err?.message||"Unable to load workforce data");setOverview(null)}})
      .finally(()=>{if(!cancelled)setLoading(false)});
    return()=>{cancelled=true};
  },[]);

  if(!session)return <Navigate to="/organization" replace/>;
  if(session.role!=="hr_admin")return <Navigate to="/organization/employee" replace/>;

  const metrics=overview?.metrics||{};
  const market=overview?.market||{};
  const roles=Array.isArray(overview?.top_roles)?overview.top_roles:[];
  const skills=Array.isArray(overview?.top_skills)?overview.top_skills:[];
  const roleGaps=Array.isArray(overview?.role_skill_gaps)?overview.role_skill_gaps:[];
  const transformation=overview?.transformation?.role_series||{};
  const categories=Array.isArray(transformation.categories)?transformation.categories:[];
  const current=Array.isArray(transformation.series?.current)?transformation.series.current:[];
  const postAI=Array.isArray(transformation.series?.post_ai)?transformation.series.post_ai:[];
  const future=Array.isArray(transformation.series?.future_demand)?transformation.series.future_demand:[];

  const animatedProfiles=useForgeAnimatedNumber(metrics.workforce_profiles??0);
  const animatedJobs=useForgeAnimatedNumber(metrics.jobs??0);
  const animatedRoles=useForgeAnimatedNumber(metrics.roles??0);
  const animatedSkills=useForgeAnimatedNumber(metrics.skills??0);

  const activeRole=roleGaps.find(x=>x.role===selectedRole)||roleGaps[0]||null;
  const activeGaps=Array.isArray(activeRole?.gaps)?activeRole.gaps:[];
  const maxRole=Math.max(1,...roles.map(x=>Number(x.count)||0));
  const maxSkill=Math.max(1,...skills.map(x=>Number(x.count)||0));
  const maxSignal=Math.max(1,...current,...postAI,...future);

  return <OrgWorkspaceFrame
    session={session}
    title={<>Welcome back, {session.organization||"your organization"} <span className="forge-wave">👋</span></>}
    subtitle="Understand your workforce, capability distribution and how AI-related signals are reshaping role requirements.">

    {error&&<div className="forge-org-error">Unable to load workforce analytics: {error}</div>}

    <div className="forge-org-metrics">
      {[
        {label:"WORKFORCE PROFILES",value:animatedProfiles,desc:"Profiles represented in the original workforce dataset",icon:Brain,color:"blue"},
        {label:"JOB RECORDS",value:animatedJobs,desc:"Observed job records in the dataset",icon:Database,color:"purple"},
        {label:"UNIQUE ROLES",value:animatedRoles,desc:"Distinct roles represented",icon:BriefcaseBusiness,color:"red"},
        {label:"SKILLS",value:animatedSkills,desc:"Distinct skills represented",icon:Target,color:"green"}
      ].map(c=>{
        const Icon=c.icon;
        return <div className={`forge-org-metric metric-${c.color}`} key={c.label}>
          <div className="forge-org-metric-top">
            <small>{c.label}</small>
            <span className="forge-org-metric-icon"><Icon size={17}/></span>
          </div>
          <strong>{loading?"—":c.value}</strong>
          <span>{c.desc}</span>
          <div className="forge-org-metric-change neutral"><Database size={10}/> ORIGINAL FORGE DATASET</div>
          <i className="forge-org-card-wave"/>
        </div>;
      })}
    </div>

    <div className="forge-org-analytics-grid">
      <section className="forge-org-chart-panel">
        <div className="forge-org-panel-head">
          <div>
            <span className="forge-org-eyebrow">WORKFORCE · ROLE DISTRIBUTION</span>
            <h2>Roles represented in the workforce</h2>
            <p>Top roles ranked by their observed profile counts.</p>
          </div>
          <span className="forge-org-data-badge">{roles.length} roles shown</span>
        </div>
        <div className="forge-org-chart-wrap">
          {roles.map((r,i)=><div className="forge-org-bar-row" key={`${r.role}-${i}`}>
            <div className="forge-org-bar-label"><strong>{r.role}</strong><span>{Number(r.count)||0} profiles</span></div>
            <div className="forge-org-gap-track"><i style={{width:`${Math.max(3,(Number(r.count)||0)/maxRole*100)}%`}}/></div>
            <b>{Number(r.count)||0}</b>
          </div>)}
          {!roles.length&&!loading&&<p>No role distribution data available.</p>}
        </div>
      </section>

      <section className="forge-org-gap-panel" id="market-intelligence">
        <div className="forge-org-panel-head">
          <div>
            <span className="forge-org-eyebrow">MARKET · DATASET COVERAGE</span>
            <h2>Workforce market overview</h2>
            <p>Coverage represented in the original FORGE job records.</p>
          </div>
          <Network size={20}/>
        </div>
        <div className="forge-org-role-cards">
          {[
            ["Job records",market.job_count],
            ["Industries",market.industries],
            ["Locations",market.locations],
            ["Role families",market.role_families]
          ].map(([label,value])=><div className="forge-org-role-card-mini" key={label}>
            <span>{label}</span><strong>{loading?"—":Number(value??0).toLocaleString()}</strong>
          </div>)}
        </div>
      </section>
    </div>

    <div className="forge-org-analytics-grid">
      <section className="forge-org-chart-panel" id="skill-distribution">
        <div className="forge-org-panel-head">
          <div>
            <span className="forge-org-eyebrow">SKILL SHADOW · SKILL DISTRIBUTION</span>
            <h2>Most represented skills</h2>
            <p>Top skills by observed frequency in the workforce data.</p>
          </div>
          <Brain size={20}/>
        </div>
        <div className="forge-org-chart-wrap">
          {skills.map((s,i)=><div className="forge-org-bar-row" key={`${s.skill}-${i}`}>
            <div className="forge-org-bar-label"><strong>{s.skill}</strong><span>{Number(s.count)||0} observations</span></div>
            <div className="forge-org-gap-track"><i style={{width:`${Math.max(3,(Number(s.count)||0)/maxSkill*100)}%`}}/></div>
            <b>{Number(s.count)||0}</b>
          </div>)}
          {!skills.length&&!loading&&<p>No skill distribution data available.</p>}
        </div>
      </section>

      <section className="forge-org-gap-panel" id="transformation">
        <div className="forge-org-panel-head">
          <div>
            <span className="forge-org-eyebrow">AI · ROLE TRANSFORMATION</span>
            <h2>Role-level transformation signals</h2>
            <p>Observed role volume and AI/automation evidence.</p>
          </div>
          <Sparkles size={20}/>
        </div>
        <div className="forge-org-transform-legend">
          <span>Current signal</span><span>Post-AI signal</span><span>Future demand signal</span>
        </div>
        <div className="forge-org-chart-wrap">
          {categories.map((category,i)=><div className="forge-org-transform-row" key={category}>
            <strong>{category}</strong>
            <div className="forge-org-transform-bars">
              <div><i style={{width:`${(Number(current[i])||0)/maxSignal*100}%`}}/></div>
              <div><i style={{width:`${(Number(postAI[i])||0)/maxSignal*100}%`}}/></div>
              <div><i style={{width:`${(Number(future[i])||0)/maxSignal*100}%`}}/></div>
            </div>
            <small>{Number(future[i])||0}</small>
          </div>)}
          {!categories.length&&!loading&&<p>No role-level transformation signals available.</p>}
        </div>
        <p className="forge-org-data-note">{overview?.transformation?.role_series?.note||"Role-level signals are based on available workforce evidence."}</p>
      </section>
    </div>

    <section className="forge-org-gap-panel" id="capability-gaps">
      <div className="forge-org-panel-head">
        <div>
          <span className="forge-org-eyebrow">CAPABILITY · ROLE SKILL GAPS</span>
          <h2>Capability exposure by role</h2>
          <p>Explore the observed skill coverage and gap signals for each role.</p>
        </div>
        <Target size={20}/>
      </div>
      <div className="forge-org-role-cards">
        {roleGaps.map(item=><button
          type="button"
          className="forge-org-role-card-mini"
          key={item.role}
          onClick={()=>setSelectedRole(item.role)}
          aria-pressed={(activeRole?.role===item.role)}>
          <span>{item.role}</span>
          <strong>{item.profiles} profiles</strong>
        </button>)}
      </div>
      {activeRole&&<div className="forge-org-gap-detail">
        <div className="forge-org-panel-head compact">
          <div><h3>{activeRole.role}</h3><p>{activeRole.profiles} profiles represented</p></div>
        </div>
        {activeGaps.map((g,i)=><div className="forge-org-gap-row" key={`${g.skill}-${i}`}>
          <div className="forge-org-gap-label"><strong>{g.skill}</strong><span>{Number(g.gap)||0}% gap · {Number(g.observed)||0} observed</span></div>
          <div className="forge-org-gap-track"><i style={{width:`${Math.max(0,Math.min(100,Number(g.gap)||0))}%`}}/></div>
        </div>)}
        {!activeGaps.length&&<p>No capability gap details are available for this role.</p>}
      </div>}
    </section>

    <div className="forge-org-data-footnote">
      <Database size={14}/>
      <span>Figures reflect the currently loaded FORGE dataset. Role-level transformation values are signals, not historical trends or guaranteed forecasts.</span>
    </div>
  </OrgWorkspaceFrame>;
}

function OrganizationEmployeeDashboard(){
  const session=useForgeOrgSession(); const navigate=useNavigate();
  if(!session)return <Navigate to="/organization" replace/>; if(session.role==="hr_admin")return <Navigate to="/organization/hr" replace/>;
  const modules=[{icon:Brain,title:'My Capability',text:'Understand the skills and capabilities connected to your work.',to:'/workforce#skill-shadow'},{icon:Target,title:'My Skill Gaps',text:'See which capabilities are worth strengthening as work changes.',to:'/workforce#skill-shadow'},{icon:Workflow,title:'My Work Context',text:'Explore the tasks and capability system behind your occupation.',to:'/workforce#worktrace'},{icon:GraduationCap,title:'Practice with Lattice',text:'Turn a capability gap into contextual practice.',to:'/lattice'}];
  return <OrgWorkspaceFrame session={session} title={<>Welcome back, {session.organization||'your workspace'} <span className="forge-wave">👋</span></>} subtitle="A focused capability workspace that helps you understand your work, your gaps and what to strengthen next."><div className="forge-org-section-title"><div><h2>Your capability stack</h2><p>ROLE → CAPABILITY → GAP → PRACTICE</p></div></div><div className="forge-org-module-grid">{modules.map(m=><button key={m.title} className="forge-org-module" onClick={()=>navigate(m.to)}><div className="forge-org-module-icon"><m.icon size={19}/></div><b>{m.title}</b><span>{m.text}</span><ArrowRight className="forge-org-module-arrow" size={15}/></button>)}</div></OrgWorkspaceFrame>;
}

export default function App() {
  const [selectedOccupation, setSelectedOccupation] = useState("");

  return (
    <BrowserRouter>
      <WorkFoldVisualStyles />
      <ForgeOrganizationStyles />
      
      <LatticeWorkspaceStyles />
      <ForgeHomeStyles />
      <ScrollManager />

      <div className="forge-site">
        <Header />

        <main>
          <Routes>

            <Route
              path="/"
              element={<HomePage />}
            />

            <Route
              path="/workforce"
              element={
                <WorkforcePage
                  selectedOccupation={selectedOccupation}
                  setSelectedOccupation={
                    setSelectedOccupation
                  }
                />
              }
            />

            <Route
              path="/worktrace"
              element={
                <Navigate
                  to="/workforce#worktrace"
                  replace
                />
              }
            />

            <Route
              path="/skill-shadow"
              element={
                <Navigate
                  to="/workforce#skill-shadow"
                  replace
                />
              }
            />

            <Route
              path="/workfold"
              element={
                <WorkFoldPage
                  selectedOccupation={
                    selectedOccupation
                  }
                  setSelectedOccupation={
                    setSelectedOccupation
                  }
                />
              }
            />

            <Route
              path="/lattice"
              element={
                <LatticeErrorBoundary>
                  <LatticePage
                    selectedOccupation={
                      selectedOccupation
                    }
                    setSelectedOccupation={
                      setSelectedOccupation
                    }
                  />
                </LatticeErrorBoundary>
              }
            />

            {/* Student architecture is preserved; only entry/auth guards are added. */}
            <Route path="/student" element={<ForgeStudentEntry />} />
            <Route path="/student/onboarding" element={<ForgeStudentOnboarding />} />
            <Route path="/student/subjects" element={<StudentProtected allowIncomplete><StudentWorkspace /></StudentProtected>} />
            <Route path="/student/target-year" element={<StudentProtected allowIncomplete><StudentWorkspace /></StudentProtected>} />
            <Route path="/student/levels" element={<StudentProtected allowIncomplete><StudentWorkspace /></StudentProtected>} />
            <Route path="/student/assessment" element={<StudentProtected allowIncomplete><StudentAssessment /></StudentProtected>} />
            <Route path="/student/scores" element={<StudentProtected allowIncomplete><StudentScores /></StudentProtected>} />
            <Route path="/student/roadmap" element={<StudentProtected allowIncomplete><StudentRoadmap /></StudentProtected>} />
            <Route path="/student/planner" element={<StudentProtected><StudentPlanner /></StudentProtected>} />
            <Route path="/student/learning" element={<StudentProtected><StudentLearningHub /></StudentProtected>} />
            <Route path="/student/progress" element={<StudentProtected><StudentProgress /></StudentProtected>} />
            <Route path="/student/ask" element={<StudentProtected><StudentAskForge /></StudentProtected>} />
            <Route path="/student/industry" element={<StudentProtected><StudentIndustryPulse /></StudentProtected>} />
            <Route path="/student/industry-market" element={<StudentProtected><StudentMarketIntelligence /></StudentProtected>} />
            <Route path="/organization" element={<OrganizationAuthPage />} />
            <Route path="/organization/hr" element={<OrganizationHrDashboard />} />
            <Route path="/organization/employee" element={<OrganizationEmployeeDashboard />} />

            

          </Routes>
        </main>

        <Footer />
      </div>

      {/* ELLA is an isolated, persistent assistant. Existing FORGE pages/routes remain unchanged. */}
      <EllaAssistant />
    </BrowserRouter>
  );
}


/* =========================================================
   SCROLL MANAGER
========================================================= */

function ScrollManager() {
  const location = useLocation();

  useEffect(() => {
    if (location.hash) {
      setTimeout(() => {
        const element =
          document.getElementById(
            location.hash.replace("#", "")
          );

        element?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } else {
      window.scrollTo({
        top: 0,
        behavior: "instant",
      });
    }
  }, [
    location.pathname,
    location.hash,
  ]);

  return null;
}



const FORGE_HOME_REDESIGN_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

  /* =========================================================
     FORGE HOME — SINGLE VISUAL SYSTEM
     Keeps all existing routes/components intact.
  ========================================================= */
  .forge-home-page {
    --forge-bg: #05020b;
    --forge-panel: #080510;
    --forge-white: #f7f5fb;
    --forge-muted: rgba(238,232,250,.66);
    --forge-purple: #a855ff;
    --forge-violet: #7b36ff;
    --forge-blue: #66d8ff;
    position: relative;
    width: 100%;
    overflow-x: hidden;
    background: var(--forge-bg);
    color: var(--forge-white);
    font-family: 'Inter', sans-serif;
  }

  .forge-home-page *,
  .forge-home-page button,
  .forge-home-page input,
  .forge-home-page textarea {
    font-family: inherit;
    box-sizing: border-box;
  }

  /* ---------------- HEADER ---------------- */
  .forge-home-header {
    position: relative;
    z-index: 100;
    width: 100%;
    height: 92px;
    min-height: 92px;
    padding: 0 46px 0 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 28px;
    background: rgba(4,2,10,.96) !important;
    border-bottom: 1px solid rgba(184,140,255,.13) !important;
    box-sizing: border-box;
    backdrop-filter: blur(18px);
  }

  .forge-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 300px;
    text-decoration: none;
    color: #fff;
  }

  .forge-brand-mark {
    width: 54px;
    height: 58px;
    object-fit: contain;
    /* Removes the visible black rectangle around the logo without changing the asset. */
    mix-blend-mode: screen;
    filter: drop-shadow(0 0 16px rgba(145,67,255,.42));
  }

  .forge-brand-copy {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .forge-brand-copy strong {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #fff;
    font-size: 27px;
    line-height: .95;
    font-weight: 800;
    letter-spacing: .255em;
  }

  .forge-brand-copy small {
    color: rgba(237,231,255,.58);
    font-family: 'Inter', sans-serif;
    font-size: 9.5px;
    line-height: 1.28;
    letter-spacing: .005em;
    font-weight: 500;
  }

  .forge-home-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: clamp(25px,3vw,45px);
    flex: 1;
    margin: 0 auto;
  }

  .forge-home-nav .forge-home-link {
    position: relative;
    padding: 35px 0 30px;
    color: rgba(255,255,255,.84) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: -.012em;
    text-decoration: none;
    white-space: nowrap;
    transition: color .25s ease;
  }

  .forge-home-nav .forge-home-link:hover,
  .forge-home-nav .forge-home-link.active {
    color: #b66cff !important;
  }

  .forge-home-nav .forge-home-link.active::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 8px;
    height: 3px;
    border-radius: 10px;
    background: linear-gradient(90deg,#8d3cff,#c98cff);
    box-shadow: 0 0 14px rgba(165,79,255,.85);
  }

  .forge-get-started {
    width: 154px;
    height: 54px;
    flex: 0 0 auto;
    border: 1px solid rgba(174,103,255,.9);
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    color: #fff;
    text-decoration: none;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    font-weight: 600;
    background: rgba(19,8,34,.34);
    box-shadow: inset 0 0 22px rgba(132,54,255,.08), 0 0 16px rgba(122,49,220,.05);
    transition: transform .25s ease, background .25s ease, box-shadow .25s ease;
  }

  .forge-get-started:hover {
    transform: translateY(-2px);
    background: rgba(128,53,235,.14);
    box-shadow: 0 0 30px rgba(141,68,255,.25);
  }

  /* ---------------- HERO ---------------- */
  .forge-home-hero {
    position: relative;
    width: 100%;
    height: calc(100svh - 92px);
    min-height: 760px;
    max-height: 900px;
    overflow: hidden;
    color: #fff;
    background:
      radial-gradient(circle at 69% 47%, rgba(105,35,220,.18), transparent 27%),
      radial-gradient(circle at 91% 76%, rgba(111,42,255,.12), transparent 25%),
      radial-gradient(circle at 14% 20%, rgba(111,38,216,.075), transparent 28%),
      linear-gradient(180deg,#04020a 0%,#07030f 58%,#080411 100%) !important;
  }

  .forge-home-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 1;
    background:
      radial-gradient(circle at 62% 45%, rgba(170,90,255,.055), transparent 23%),
      linear-gradient(180deg,rgba(255,255,255,.012),transparent 25%);
  }

  .forge-home-grid {
    position: relative;
    z-index: 10;
    width: min(1400px, calc(100% - 110px));
    height: 100%;
    margin: 0 auto;
    display: grid;
    grid-template-columns: minmax(0,46%) minmax(0,54%);
    align-items: start;
  }

  .forge-home-copy {
    position: relative;
    z-index: 35;
    padding-top: 66px;
    padding-left: 10px;
    min-width: 0;
  }

  .forge-home-eyebrow {
    width: max-content;
    min-width: 0;
    height: 34px;
    padding: 0 14px;
    border-radius: 999px;
    display: inline-flex !important;
    align-items: center;
    gap: 10px !important;
    color: rgba(255,255,255,.82) !important;
    background: linear-gradient(90deg,rgba(86,27,158,.30),rgba(54,15,104,.16));
    border: 1px solid rgba(153,87,255,.12);
    box-shadow: inset 0 0 20px rgba(142,63,255,.08),0 0 16px rgba(124,49,235,.06);
    font-size: 10px !important;
    letter-spacing: 1.65px !important;
    font-weight: 700 !important;
  }

  .forge-home-eyebrow > span {
    width: 7px !important;
    height: 7px !important;
    flex: 0 0 7px;
    border-radius: 50%;
    background: #b76cff;
    box-shadow: 0 0 11px #9c43ff,0 0 20px rgba(166,73,255,.6);
  }

  .forge-home-title {
    width: 610px;
    max-width: 100%;
    margin: 28px 0 18px !important;
    display: flex;
    flex-direction: column;
    gap: 0;
    font-family: 'Plus Jakarta Sans',sans-serif !important;
    font-size: clamp(50px,4.25vw,65px) !important;
    line-height: .99 !important;
    letter-spacing: -.058em !important;
    font-weight: 800 !important;
    color: #f7f5fb !important;
  }

  .forge-home-title span { display:block; }

  .forge-gradient-text {
    background: linear-gradient(95deg,#a94cff 0%,#9d53ff 38%,#c17bff 72%,#8f42ff 100%);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent !important;
    text-shadow:0 0 28px rgba(135,55,255,.13);
  }

  .forge-home-description {
    width: 570px;
    max-width: 100%;
    margin: 0 !important;
    color: rgba(235,230,246,.68) !important;
    font-family:'Inter',sans-serif !important;
    font-size: 14px !important;
    line-height: 1.55 !important;
    letter-spacing: -.012em;
  }

  .forge-home-actions {
    display:flex;
    align-items:center;
    gap:16px;
    margin-top:26px !important;
  }

  .forge-primary-cta,
  .forge-secondary-cta {
    height:55px;
    border-radius:13px;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:11px;
    padding:0 24px;
    cursor:pointer;
    font-family:'Inter',sans-serif !important;
    font-size:14px;
    font-weight:650;
    transition:transform .25s ease,box-shadow .25s ease,background .25s ease;
  }

  .forge-primary-cta {
    min-width:205px;
    color:#fff;
    border:0;
    background:linear-gradient(135deg,#8737f5,#b15cff);
    box-shadow:0 12px 34px rgba(119,40,235,.30),inset 0 1px 0 rgba(255,255,255,.23);
  }

  .forge-secondary-cta {
    min-width:218px;
    color:#fff;
    border:1px solid rgba(170,94,255,.78);
    background:rgba(10,5,20,.24);
  }

  .forge-primary-cta:hover,.forge-secondary-cta:hover { transform:translateY(-2px); }

  .forge-play-icon { width:27px;height:27px;display:grid;place-items:center;color:#fff; }

  .forge-home-stats {
    margin-top:32px !important;
    display:flex !important;
    align-items:center;
    width:100%;
    max-width:650px;
    gap:0 !important;
  }

  .forge-home-stats > * {
    min-width:0;
    flex:1 1 0;
    padding:0 18px;
    border-right:1px solid rgba(205,170,255,.20);
  }

  .forge-home-stats > *:first-child { padding-left:0; }
  .forge-home-stats > *:last-child { border-right:0; }

  .forge-home-stats .stat-item strong {
    display:block;
    color:#a75bff !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:23px !important;
    font-weight:800 !important;
    line-height:1;
    letter-spacing:-.035em;
  }

  .forge-home-stats .stat-item span {
    display:block;
    margin-top:6px;
    color:rgba(255,255,255,.58) !important;
    font-size:8px !important;
    font-weight:600;
    letter-spacing:1.05px;
    white-space:nowrap;
  }

  /* ---------------- ORBIT ---------------- */
  .forge-home-orbit {
    position:relative !important;
    width:100%;
    height:100%;
    min-height:0;
    display:flex;
    align-items:flex-start;
    justify-content:center;
    padding-top:28px;
    box-sizing:border-box;
  }

  .forge-orbit-system {
    position:relative !important;
    width:570px !important;
    height:530px !important;
    margin:0 !important;
    transform:translateX(12px) !important;
    isolation:isolate;
  }

  .forge-orbit-system .orbit-aura {
    position:absolute;
    left:50%;top:50%;
    width:245px;height:245px;
    transform:translate(-50%,-50%);
    border-radius:50%;
    background:radial-gradient(circle,rgba(131,54,255,.30),rgba(79,21,150,.10) 46%,transparent 73%);
    filter:blur(13px);
    animation:forgeCorePulse 4.8s ease-in-out infinite;
  }

  .forge-orbit-system .orbit-ring {
    position:absolute;
    left:50%;top:50%;
    border:1px solid rgba(164,100,255,.60);
    border-radius:50%;
    transform-origin:center;
    box-shadow:0 0 9px rgba(119,61,255,.16);
    will-change:transform;
  }

  /* A moving luminous point rides each independent orbit. */
  .forge-orbit-system .orbit-ring::before {
    content:'';
    position:absolute;
    width:7px;height:7px;
    left:50%;top:-3.5px;
    border-radius:50%;
    background:#fff;
    box-shadow:0 0 7px #fff,0 0 16px currentColor,0 0 30px currentColor;
    transform:translateX(-50%);
  }

  .forge-orbit-system .orbit-ring::after {
    content:'';
    position:absolute;
    inset:-1px;
    border-radius:inherit;
    border:1px solid transparent;
    background:linear-gradient(90deg,transparent,rgba(225,190,255,.65),transparent) border-box;
    -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);
    -webkit-mask-composite:xor;
    mask-composite:exclude;
    opacity:.55;
  }

  .orbit-ring-1 {
    width:500px;height:255px;
    color:#bd72ff;
    transform:translate(-50%,-50%) rotate(-18deg);
    animation:forgeOrbitA 25s linear infinite;
  }
  .orbit-ring-2 {
    width:515px;height:245px;
    color:#72c9ff;
    border-color:rgba(95,190,255,.58) !important;
    transform:translate(-50%,-50%) rotate(27deg);
    animation:forgeOrbitB 31s linear infinite reverse;
  }
  .orbit-ring-3 {
    width:225px;height:510px;
    color:#d49bff;
    border-color:rgba(199,119,255,.56) !important;
    transform:translate(-50%,-50%) rotate(-11deg);
    animation:forgeOrbitC 36s linear infinite;
  }
  .orbit-ring-4 {
    width:280px;height:505px;
    color:#7be1ff;
    border-color:rgba(103,196,255,.46) !important;
    transform:translate(-50%,-50%) rotate(39deg);
    animation:forgeOrbitD 43s linear infinite reverse;
  }
  .orbit-ring-5 {
    width:540px;height:335px;
    color:#9e68ff;
    border-color:rgba(133,74,255,.34) !important;
    transform:translate(-50%,-50%) rotate(68deg);
    animation:forgeOrbitE 49s linear infinite;
  }

  .forge-orbit-system .orbit-center {
    position:absolute !important;
    left:50%;top:50%;
    width:205px !important;height:205px !important;
    transform:translate(-50%,-50%) !important;
    border-radius:50%;
    display:grid !important;
    place-items:center;
    background:radial-gradient(circle at 45% 38%,rgba(205,143,255,.39),rgba(74,24,138,.34) 36%,rgba(13,7,26,.95) 72%);
    border:1px solid rgba(181,117,255,.70);
    box-shadow:0 0 30px rgba(137,58,255,.52),0 0 72px rgba(100,37,205,.28),inset 0 0 45px rgba(159,78,255,.21);
    overflow:visible;
    animation:forgeCoreFloat 5.5s ease-in-out infinite;
  }

  .forge-core-glow {
    position:absolute;inset:-17px;border-radius:50%;
    background:radial-gradient(circle,rgba(171,85,255,.25),transparent 68%);
    filter:blur(8px);z-index:-1;
  }

  .forge-core-inner {
    width:86px;height:86px;border-radius:20px;
    display:grid;place-items:center;
    background:rgba(3,1,7,.64);
    box-shadow:0 0 35px rgba(145,65,255,.28);
  }

  .forge-core-inner img {
    width:70px;height:70px;object-fit:contain;
    mix-blend-mode:screen;
    filter:drop-shadow(0 0 15px rgba(177,91,255,.9));
  }

  .forge-orbit-node {
    position:absolute !important;
    z-index:30;
    display:flex !important;
    flex-direction:column;
    align-items:center;
    gap:6px;
    color:#fff;
    pointer-events:none;
  }

  .forge-orbit-node .orbit-node-icon {
    width:56px !important;height:56px !important;
    display:grid !important;place-items:center;
    border:1px solid rgba(166,102,255,.88) !important;
    border-radius:50% !important;
    background:radial-gradient(circle,rgba(97,35,182,.52),rgba(12,6,25,.90) 68%);
    color:#d1a5ff !important;
    box-shadow:0 0 17px rgba(128,53,245,.52),inset 0 0 14px rgba(177,101,255,.13);
  }

  .forge-orbit-node strong {
    color:#fff !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:13px !important;
    font-weight:750 !important;
    letter-spacing:.045em;
  }
  .forge-orbit-node small { display:none !important; }

  .orbit-ai { left:50%;top:3px;transform:translateX(-50%);animation:forgeNodeAI 6.5s ease-in-out infinite; }
  .orbit-human { left:5px;top:230px;animation:forgeNodeHuman 7.8s ease-in-out infinite; }
  .orbit-task { right:0;top:250px;animation:forgeNodeTask 8.3s ease-in-out infinite; }
  .orbit-skill { left:50%;bottom:0;transform:translateX(-50%);animation:forgeNodeSkill 7.3s ease-in-out infinite; }

  .forge-orbit-system .orbit-particle {
    position:absolute;width:5px;height:5px;border-radius:50%;
    background:#e1c2ff;box-shadow:0 0 10px #b66cff,0 0 22px rgba(152,73,255,.8);z-index:20;
  }
  .orbit-particle-1{left:24%;top:18%;animation:forgeParticle1 9s ease-in-out infinite;}
  .orbit-particle-2{left:73%;top:24%;width:4px !important;height:4px !important;background:#75dcff !important;box-shadow:0 0 12px #55cfff !important;animation:forgeParticle2 12s ease-in-out infinite;}
  .orbit-particle-3{left:83%;top:48%;animation:forgeParticle3 10s ease-in-out infinite;}
  .orbit-particle-4{left:66%;top:78%;width:4px !important;height:4px !important;animation:forgeParticle4 11s ease-in-out infinite;}
  .orbit-particle-5{left:30%;top:70%;width:3px !important;height:3px !important;background:#fff !important;box-shadow:0 0 10px #fff !important;animation:forgeParticle5 13s ease-in-out infinite;}
  .orbit-particle-6{left:52%;top:14%;width:3px !important;height:3px !important;animation:forgeParticle6 8s ease-in-out infinite;}

  /* ---------------- EARTH / CONTINUATION ---------------- */
  /* ---------------- REAL EARTH IMAGE / HERO-TO-WORKSPACE BRIDGE ---------------- */
  .forge-home-hero {
    position:relative !important;
    z-index:3 !important;
    overflow:visible !important;
    isolation:isolate;
  }

  .forge-earth-image-wrap {
    position:absolute; left:-5%; right:-5%; bottom:-112px; height:475px;
    z-index:8; pointer-events:none; overflow:visible;
  }
  .forge-earth-image {
    position:absolute; left:0; top:0; width:110%; height:auto; max-width:none; display:block;
    opacity:1;
    filter:saturate(1.16) contrast(1.12) brightness(1.04);
    -webkit-mask-image:linear-gradient(to bottom,transparent 0%,rgba(0,0,0,.82) 8%,#000 20%,#000 76%,rgba(0,0,0,.86) 88%,transparent 100%);
    mask-image:linear-gradient(to bottom,transparent 0%,rgba(0,0,0,.82) 8%,#000 20%,#000 76%,rgba(0,0,0,.86) 88%,transparent 100%);
  }
  .forge-earth-image-wrap::after {
    content:'';
    position:absolute; left:7%; right:7%; top:76px; height:150px; z-index:3;
    border-radius:50%;
    background:radial-gradient(ellipse at 50% 78%,rgba(190,115,255,.30) 0%,rgba(130,65,235,.16) 28%,transparent 68%);
    filter:blur(20px);
    pointer-events:none;
    mix-blend-mode:screen;
  }
  .forge-earth-atmosphere {
    position:absolute; left:4%; right:4%; top:68px; height:195px; z-index:2; border-radius:50%;
    background:radial-gradient(ellipse at 50% 72%,rgba(185,105,255,.30),rgba(106,44,224,.14) 36%,transparent 72%);
    filter:blur(22px); pointer-events:none;
  }
  .forge-earth-soft-fade {
    position:absolute;
    left:-3%;
    right:-3%;
    bottom:-70px;
    height:180px;
    z-index:4;
    background:linear-gradient(
      to bottom,
      rgba(4,2,10,0) 0%,
      rgba(4,2,10,.015) 18%,
      rgba(4,2,10,.06) 38%,
      rgba(4,2,10,.22) 58%,
      rgba(4,2,10,.55) 78%,
      rgba(4,2,10,.92) 94%,
      #07030d 100%
    );
    pointer-events:none;
  }

  /* Keep the Earth above the beginning of the workspace section.
     The workspace itself stays transparent until the Earth has finished,
     so no hard horizontal rectangle can cover the image. */
  .forge-home-page .student-org-section {
    position:relative !important;
    z-index:1 !important;
    margin-top:0;
    padding-top:205px;
    background:transparent !important;
    background-color:transparent !important;
    border-top:0 !important;
    box-shadow:none !important;
  }

  .forge-home-page .student-org-section::before {
    content:'';
    position:absolute;
    left:0;
    right:0;
    top:285px;
    bottom:0;
    z-index:0;
    background:linear-gradient(
      180deg,
      rgba(9,10,9,0) 0%,
      rgba(9,10,9,.04) 8%,
      rgba(9,10,9,.48) 23%,
      #090a09 40%,
      #090a09 100%
    );
    pointer-events:none;
  }

  .forge-home-page .student-org-section > * {
    position:relative;
    z-index:2;
  }

  .forge-scroll-cue {
    position:absolute;left:50%;bottom:18px;z-index:40;transform:translateX(-50%);
    display:flex;flex-direction:column;align-items:center;gap:8px;
    color:rgba(255,255,255,.82);font-family:'Inter',sans-serif;font-size:9px;font-weight:650;letter-spacing:2px;
  }
  .forge-mouse { width:21px;height:34px;border:1px solid rgba(255,255,255,.70);border-radius:13px;position:relative; }
  .forge-mouse i { position:absolute;left:50%;top:7px;width:3px;height:7px;border-radius:4px;background:#fff;transform:translateX(-50%);animation:forgeMouse 1.8s ease-in-out infinite; }

  .forge-star { position:absolute;width:3px;height:3px;border-radius:50%;background:#fff;box-shadow:0 0 10px #fff,0 0 22px rgba(167,98,255,.7);z-index:4;animation:forgeStar 3.5s ease-in-out infinite alternate; }
  .forge-star-1{left:79%;top:18%}.forge-star-2{left:58%;top:31%;width:3px;height:3px;animation-delay:.6s}.forge-star-3{left:95%;top:28%;animation-delay:1.1s}.forge-star-4{left:70%;top:68%;width:2px;height:2px;animation-delay:1.7s}.forge-star-5{left:47%;top:12%;width:2px;height:2px;animation-delay:2.1s}

  /* ---------------- ALL LOWER HOME SECTIONS ---------------- */
  .forge-home-page .student-org-section,
  .forge-home-page .problem-section,
  .forge-home-page .home-transition {
    font-family:'Inter',sans-serif !important;
    color:#f4f1f8;
  }

  .forge-home-page .workspace-heading h2 {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:clamp(38px,4.2vw,58px) !important;
    line-height:1.02 !important;
    letter-spacing:-.055em !important;
    font-weight:750 !important;
  }
  .forge-home-page .workspace-heading p,
  .forge-home-page .workspace-card p {
    font-size:14px !important;
    line-height:1.65 !important;
  }
  .forge-home-page .workspace-card h3 {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:30px !important;
    line-height:1 !important;
    letter-spacing:-.04em !important;
  }
  .forge-home-page .workspace-kicker,
  .forge-home-page .workspace-tag,
  .forge-home-page .workspace-features span,
  .forge-home-page .workspace-cta {
    font-family:'Inter',sans-serif !important;
  }

  .forge-home-page .section-heading h1 {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:clamp(44px,5vw,68px) !important;
    line-height:1.00 !important;
    letter-spacing:-.06em !important;
    font-weight:750 !important;
  }
  .forge-home-page .section-heading p { font-size:14px !important;line-height:1.65 !important; }
  .forge-home-page .problem-half h2 { font-family:'Plus Jakarta Sans',sans-serif !important;font-size:31px !important;letter-spacing:-.04em !important; }
  .forge-home-page .problem-half p { font-size:13px !important;line-height:1.65 !important; }
  .forge-home-page .home-transition h2 { font-family:'Plus Jakarta Sans',sans-serif !important;font-size:clamp(45px,5vw,66px) !important;line-height:.98 !important;letter-spacing:-.06em !important; }
  .forge-home-page .flow-item strong { font-size:13px !important; }
  .forge-home-page .flow-item p { font-size:12px !important;line-height:1.55 !important; }

  /* ---------------- ANIMATION: independent orbital motion ---------------- */
  @keyframes forgeCorePulse { 0%,100%{opacity:.72;transform:translate(-50%,-50%) scale(.96)} 50%{opacity:1;transform:translate(-50%,-50%) scale(1.05)} }
  @keyframes forgeCoreFloat { 0%,100%{filter:brightness(.98);transform:translate(-50%,-50%)} 50%{filter:brightness(1.12);transform:translate(-50%,-50%) translateY(-5px)} }
  @keyframes forgeOrbitA { to{transform:translate(-50%,-50%) rotate(342deg)} }
  @keyframes forgeOrbitB { to{transform:translate(-50%,-50%) rotate(-333deg)} }
  @keyframes forgeOrbitC { to{transform:translate(-50%,-50%) rotate(349deg)} }
  @keyframes forgeOrbitD { to{transform:translate(-50%,-50%) rotate(-326deg)} }
  @keyframes forgeOrbitE { to{transform:translate(-50%,-50%) rotate(427deg)} }
  @keyframes forgeNodeAI { 0%,100%{transform:translateX(-50%) translateY(0)} 50%{transform:translateX(-50%) translateY(6px)} }
  @keyframes forgeNodeHuman { 0%,100%{transform:translate(0,0)} 50%{transform:translate(5px,-5px)} }
  @keyframes forgeNodeTask { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-5px,5px)} }
  @keyframes forgeNodeSkill { 0%,100%{transform:translateX(-50%) translateY(0)} 50%{transform:translateX(-50%) translateY(-6px)} }
  @keyframes forgeParticle1 { 0%{transform:translate(0,0)} 25%{transform:translate(50px,35px)} 50%{transform:translate(20px,115px)} 75%{transform:translate(-50px,75px)} 100%{transform:translate(0,0)} }
  @keyframes forgeParticle2 { 0%{transform:translate(0,0)} 25%{transform:translate(-65px,55px)} 50%{transform:translate(-105px,10px)} 75%{transform:translate(-45px,-45px)} 100%{transform:translate(0,0)} }
  @keyframes forgeParticle3 { 0%{transform:translate(0,0)} 25%{transform:translate(-30px,55px)} 50%{transform:translate(-105px,70px)} 75%{transform:translate(-50px,-40px)} 100%{transform:translate(0,0)} }
  @keyframes forgeParticle4 { 0%{transform:translate(0,0)} 50%{transform:translate(-75px,-40px)} 100%{transform:translate(15px,-85px)} }
  @keyframes forgeParticle5 { 0%{transform:translate(0,0)} 50%{transform:translate(65px,-55px)} 100%{transform:translate(125px,-8px)} }
  @keyframes forgeParticle6 { 0%{transform:translate(0,0)} 50%{transform:translate(35px,70px)} 100%{transform:translate(-35px,135px)} }
  @keyframes forgeCityPulse { from{opacity:.25;transform:scale(.75)} to{opacity:.95;transform:scale(1.35)} }
  @keyframes forgeMouse { 0%,100%{transform:translate(-50%,0);opacity:1} 50%{transform:translate(-50%,6px);opacity:.35} }
  @keyframes forgeStar { from{opacity:.2;transform:scale(.75)} to{opacity:1;transform:scale(1.35)} }

  @media (max-width: 1250px) {
    .forge-home-header { padding-left:35px;padding-right:35px; }
    .forge-brand { min-width:260px; }
    .forge-home-nav { gap:22px; }
    .forge-home-grid { width:calc(100% - 60px);grid-template-columns:47% 53%; }
    .forge-home-title { font-size:clamp(47px,4.55vw,60px) !important; }
    .forge-orbit-system { transform:translateX(0) scale(.92) !important;transform-origin:top center; }
  }

  @media (max-width: 950px) {
    .forge-home-header { height:auto;min-height:78px;padding:12px 20px;flex-wrap:wrap; }
    .forge-brand { min-width:0; }
    .forge-brand-copy small { display:none; }
    .forge-brand-copy strong { font-size:23px; }
    .forge-brand-mark { width:46px;height:50px; }
    .forge-home-nav { order:3;width:100%;overflow-x:auto;justify-content:flex-start;gap:24px; }
    .forge-home-nav .forge-home-link { padding:7px 0 11px; }
    .forge-get-started { width:130px;height:46px;font-size:13px; }
    .forge-home-hero { height:auto;max-height:none;min-height:1100px; }
    .forge-home-grid { width:calc(100% - 36px);grid-template-columns:1fr; }
    .forge-home-copy { padding:44px 0 0; }
    .forge-home-title { width:700px;max-width:100%; }
    .forge-home-orbit { min-height:555px;margin-top:5px; }
    .forge-orbit-system { transform:scale(.80) !important;transform-origin:center top; }
    .forge-earth { bottom:-285px; }
  }

  @media (max-width: 1200px) {
    .forge-earth-image-wrap { left:-9%; right:-9%; bottom:-138px; height:485px; }
    .forge-earth-image { width:118%; left:-9%; }
  }

  @media (max-width: 600px) {
    .forge-home-header { padding:10px 15px; }
    .forge-get-started span { display:none; }
    .forge-get-started { width:45px;padding:0; }
    .forge-home-title { font-size:44px !important; }
    .forge-home-eyebrow { font-size:8px !important;letter-spacing:1.05px !important; }
    .forge-home-description { font-size:13px !important; }
    .forge-home-actions { flex-direction:column;align-items:stretch; }
    .forge-primary-cta,.forge-secondary-cta { width:100%; }
    .forge-home-stats { flex-wrap:wrap;row-gap:18px; }
    .forge-home-stats > * { min-width:50%;flex:0 0 50%;padding:0 12px; }
    .forge-home-stats > *:first-child { padding-left:12px; }
    .forge-orbit-system { transform:scale(.56) !important; }
    .forge-earth { bottom:-245px; }
    .forge-scroll-cue { bottom:14px; }
  }
  @media (max-width: 600px) {
    .forge-earth-image-wrap { left:-18%; right:-18%; bottom:-76px; height:328px; }
    .forge-earth-image { width:136%; left:-18%; opacity:1; }
    .forge-home-page .student-org-section { margin-top:0; padding-top:118px; }
    .forge-home-page .student-org-section::before { display:none !important; }
  }

  /* =========================================================
     FINAL HOMEPAGE POLISH
     - white hero headline
     - purple/black blended lower sections
     - smaller, stronger orbital motion
     - transparent FORGE core (no square box)
  ========================================================= */

  .forge-home-page .forge-home-title > span:nth-child(1),
  .forge-home-page .forge-home-title > span:nth-child(2) {
    color:#ffffff !important;
    background:none !important;
    -webkit-background-clip:initial !important;
    background-clip:initial !important;
    -webkit-text-fill-color:#ffffff !important;
    text-shadow:0 0 24px rgba(255,255,255,.025);
  }

  .forge-home-page .forge-home-title > .forge-gradient-text {
    -webkit-text-fill-color:transparent !important;
  }

  /* =========================================================
     ORBIT V2 — LARGE, GLOWING, INDEPENDENT REVOLUTION
     Nodes stay fixed. Only the orbital planes rotate.
  ========================================================= */

  .forge-home-page .forge-home-orbit {
    align-items:flex-start !important;
    padding-top:0 !important;
    min-height:610px !important;
  }

  .forge-home-page .forge-orbit-system {
    width:650px !important;
    height:610px !important;
    transform:translateX(4px) scale(1.02) !important;
    transform-origin:50% 50% !important;
  }

  /* Strong atmospheric glow behind the whole orbital field. */
  .forge-home-page .forge-orbit-system .orbit-aura {
    width:330px !important;
    height:330px !important;
    background:
      radial-gradient(circle,
        rgba(178,83,255,.42) 0%,
        rgba(122,44,225,.23) 30%,
        rgba(72,20,145,.12) 52%,
        transparent 74%) !important;
    filter:blur(17px) !important;
  }

  /* Every orbital plane is clearly luminous and independently rotating. */
  .forge-home-page .forge-orbit-system .orbit-ring {
    border-width:1.5px !important;
    opacity:.94 !important;
    filter:
      drop-shadow(0 0 3px currentColor)
      drop-shadow(0 0 8px currentColor)
      drop-shadow(0 0 18px color-mix(in srgb, currentColor 62%, transparent)) !important;
    box-shadow:
      0 0 8px currentColor,
      0 0 20px color-mix(in srgb, currentColor 48%, transparent),
      inset 0 0 5px color-mix(in srgb, currentColor 28%, transparent) !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring::before {
    width:8px !important;
    height:8px !important;
    top:-4px !important;
    box-shadow:
      0 0 5px #fff,
      0 0 12px #fff,
      0 0 24px currentColor,
      0 0 42px currentColor !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring::after {
    opacity:.82 !important;
    border-width:1px !important;
    filter:drop-shadow(0 0 7px currentColor) !important;
  }

  /* Bigger planes — closer to the original visual scale. */
  .forge-home-page .forge-orbit-system .orbit-ring-1 {
    width:590px !important;
    height:300px !important;
    animation:forgeOrbitA 17s linear infinite !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-2 {
    width:605px !important;
    height:290px !important;
    animation:forgeOrbitB 22s linear infinite reverse !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-3 {
    width:265px !important;
    height:590px !important;
    animation:forgeOrbitC 28s linear infinite !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-4 {
    width:330px !important;
    height:585px !important;
    animation:forgeOrbitD 35s linear infinite reverse !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-5 {
    width:635px !important;
    height:390px !important;
    animation:forgeOrbitE 43s linear infinite !important;
  }

  /* Remove square logo box; keep a clean luminous FORGE mark. */
  .forge-home-page .forge-orbit-center {
    width:178px !important;
    height:178px !important;
    background:
      radial-gradient(circle,
        rgba(180,89,255,.31) 0%,
        rgba(91,29,177,.19) 36%,
        rgba(10,4,23,.42) 64%,
        transparent 78%) !important;
    border:1px solid rgba(193,132,255,.42) !important;
    box-shadow:
      0 0 28px rgba(145,57,255,.48),
      0 0 70px rgba(102,38,215,.30),
      inset 0 0 42px rgba(174,91,255,.18) !important;
  }

  .forge-home-page .forge-core-glow {
    inset:-24px !important;
    background:
      radial-gradient(circle,
        rgba(185,91,255,.30),
        rgba(115,45,225,.12) 42%,
        transparent 72%) !important;
    filter:blur(11px) !important;
  }

  .forge-home-page .forge-core-inner {
    width:70px !important;
    height:70px !important;
    border-radius:50% !important;
    background:transparent !important;
    box-shadow:none !important;
  }

  .forge-home-page .forge-core-inner img {
    width:56px !important;
    height:56px !important;
    mix-blend-mode:screen !important;
    filter:
      drop-shadow(0 0 6px rgba(255,255,255,.65))
      drop-shadow(0 0 14px rgba(191,105,255,.95))
      drop-shadow(0 0 28px rgba(142,55,255,.78)) !important;
  }

  /* =========================================================
     IMPORTANT: AI / HUMAN / TASK / SKILL DO NOT MOVE.
     Their positions stay fixed while the rings revolve beneath them.
  ========================================================= */
  .forge-home-page .orbit-ai {
    left:50% !important;
    top:-2px !important;
    transform:translateX(-50%) !important;
    animation:none !important;
  }

  .forge-home-page .orbit-human {
    left:1px !important;
    top:270px !important;
    transform:none !important;
    animation:none !important;
  }

  .forge-home-page .orbit-task {
    right:1px !important;
    top:285px !important;
    transform:none !important;
    animation:none !important;
  }

  .forge-home-page .orbit-skill {
    left:50% !important;
    bottom:-2px !important;
    transform:translateX(-50%) !important;
    animation:none !important;
  }

  .forge-home-page .forge-orbit-node .orbit-node-icon {
    width:58px !important;
    height:58px !important;
    border-color:rgba(190,123,255,.95) !important;
    background:
      radial-gradient(circle,
        rgba(112,42,205,.62),
        rgba(16,7,32,.94) 70%) !important;
    box-shadow:
      0 0 10px rgba(176,86,255,.75),
      0 0 24px rgba(130,52,235,.55),
      inset 0 0 15px rgba(205,136,255,.18) !important;
  }

  .forge-home-page .forge-orbit-node strong {
    text-shadow:
      0 0 7px rgba(255,255,255,.20),
      0 0 16px rgba(170,84,255,.30) !important;
  }

  /* Make the independent rotations unmistakable. */
  @keyframes forgeOrbitA {
    from { transform:translate(-50%,-50%) rotate(-18deg); }
    to   { transform:translate(-50%,-50%) rotate(342deg); }
  }
  @keyframes forgeOrbitB {
    from { transform:translate(-50%,-50%) rotate(27deg); }
    to   { transform:translate(-50%,-50%) rotate(-333deg); }
  }
  @keyframes forgeOrbitC {
    from { transform:translate(-50%,-50%) rotate(-11deg); }
    to   { transform:translate(-50%,-50%) rotate(349deg); }
  }
  @keyframes forgeOrbitD {
    from { transform:translate(-50%,-50%) rotate(39deg); }
    to   { transform:translate(-50%,-50%) rotate(-326deg); }
  }
  @keyframes forgeOrbitE {
    from { transform:translate(-50%,-50%) rotate(68deg); }
    to   { transform:translate(-50%,-50%) rotate(428deg); }
  }

  /* ---- STUDENT / ORGANIZATION: purple-black instead of flat charcoal ---- */
  .forge-home-page .student-org-section {
    background:
      radial-gradient(circle at 18% 0%, rgba(117,48,215,.16), transparent 34%),
      radial-gradient(circle at 82% 12%, rgba(88,44,180,.12), transparent 38%),
      linear-gradient(180deg,#08030f 0%,#07030d 54%,#08040f 100%) !important;
    color:#f7f4fb !important;
  }

  .forge-home-page .student-org-section::before {
    top:0 !important;
    background:
      linear-gradient(180deg,
        rgba(9,3,18,.02) 0%,
        rgba(62,20,108,.08) 18%,
        rgba(13,5,25,.62) 48%,
        #08040f 78%,
        #08040f 100%) !important;
  }

  .forge-home-page .workspace-heading h2 {
    color:#ffffff !important;
  }

  .forge-home-page .workspace-heading p {
    color:rgba(235,226,250,.66) !important;
  }

  .forge-home-page .workspace-card {
    border-color:rgba(157,91,235,.24) !important;
    background:
      radial-gradient(circle at 80% 0%, rgba(120,54,205,.17), transparent 40%),
      linear-gradient(145deg,
        rgba(56,20,93,.42),
        rgba(12,5,25,.84)) !important;
    box-shadow:
      inset 0 1px 0 rgba(210,165,255,.045),
      0 20px 70px rgba(36,8,70,.20) !important;
  }

  .forge-home-page .workspace-card:hover {
    border-color:rgba(178,112,255,.48) !important;
    box-shadow:
      0 25px 80px rgba(74,22,135,.26),
      inset 0 1px 0 rgba(220,182,255,.07) !important;
  }

  .forge-home-page .workspace-icon {
    border-color:rgba(173,105,255,.28) !important;
    background:rgba(91,38,157,.20) !important;
    box-shadow:0 0 22px rgba(120,53,224,.10);
  }

  .forge-home-page .workspace-card p {
    color:rgba(232,224,246,.61) !important;
  }

  .forge-home-page .workspace-features span {
    border-color:rgba(164,99,236,.20) !important;
    background:rgba(103,43,171,.10) !important;
    color:rgba(226,211,245,.56) !important;
  }

  .forge-home-page .workspace-tag,
  .forge-home-page .workspace-kicker {
    color:rgba(197,157,241,.58) !important;
  }

  /* ---- ALL LOWER HOME CONTENT: carry the same purple/black atmosphere ---- */
  .forge-home-page .problem-section,
  .forge-home-page .home-transition {
    background:
      radial-gradient(circle at 12% 8%, rgba(89,35,163,.10), transparent 30%),
      radial-gradient(circle at 88% 60%, rgba(76,31,146,.08), transparent 32%),
      linear-gradient(180deg,#07030d 0%,#08040f 100%) !important;
    color:#f6f2fb !important;
  }

  .forge-home-page .problem-panel {
    background:rgba(17,7,31,.30) !important;
    border-color:rgba(157,91,235,.24) !important;
  }

  .forge-home-page .problem-half {
    background:rgba(45,16,70,.10) !important;
  }

  .forge-home-page .process-box {
    background:
      linear-gradient(145deg,
        rgba(67,28,102,.42),
        rgba(20,8,34,.76)) !important;
    border-color:rgba(175,117,235,.34) !important;
  }

  .forge-home-page .flow-item,
  .forge-home-page .home-transition-panel {
    border-color:rgba(157,91,235,.20) !important;
  }

  /* Preserve the Earth-to-section transition without introducing a hard bar. */
  .forge-home-page .forge-earth-soft-fade {
    background:linear-gradient(
      to bottom,
      rgba(4,2,10,0) 0%,
      rgba(5,2,12,.015) 18%,
      rgba(8,3,16,.06) 38%,
      rgba(10,4,20,.20) 58%,
      rgba(8,3,16,.54) 78%,
      rgba(8,4,15,.88) 94%,
      #08040f 100%
    ) !important;
  }


  /* =========================================================
     FINAL ORBIT POLISH — PROFESSIONAL / CONTROLLED / PREMIUM
     Fixed nodes + independently rotating orbital planes.
  ========================================================= */

  .forge-home-page .forge-home-orbit {
    position:relative !important;
    min-height:570px !important;
    height:570px !important;
    padding-top:0 !important;
    overflow:visible !important;
  }

  .forge-home-page .forge-orbit-system {
    width:560px !important;
    height:545px !important;
    transform:translateX(8px) !important;
    transform-origin:center center !important;
    overflow:visible !important;
  }

  /* Keep the whole orbital field luminous, but not blown-out. */
  .forge-home-page .forge-orbit-system .orbit-aura {
    width:250px !important;
    height:250px !important;
    background:
      radial-gradient(circle,
        rgba(154,70,255,.24) 0%,
        rgba(104,37,196,.12) 38%,
        transparent 72%) !important;
    filter:blur(15px) !important;
  }

  /* Thin, crisp rings with a restrained neon halo. */
  .forge-home-page .forge-orbit-system .orbit-ring {
    border-width:1px !important;
    opacity:.94 !important;
    box-shadow:
      0 0 4px currentColor,
      0 0 9px color-mix(in srgb,currentColor 62%,transparent),
      0 0 17px color-mix(in srgb,currentColor 28%,transparent) !important;
    filter:none !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring::before {
    width:5px !important;
    height:5px !important;
    top:-2.5px !important;
    background:#fff !important;
    box-shadow:
      0 0 4px #fff,
      0 0 9px currentColor,
      0 0 17px currentColor !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring::after {
    opacity:.38 !important;
    filter:drop-shadow(0 0 4px currentColor) !important;
  }

  /* Balanced orbital geometry — large, but contained inside the hero. */
  .forge-home-page .forge-orbit-system .orbit-ring-1 {
    width:500px !important;
    height:245px !important;
    border-color:rgba(184,105,255,.78) !important;
    animation:forgeProOrbit1 19s linear infinite !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-2 {
    width:515px !important;
    height:238px !important;
    border-color:rgba(91,190,255,.58) !important;
    animation:forgeProOrbit2 25s linear infinite reverse !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-3 {
    width:230px !important;
    height:500px !important;
    border-color:rgba(194,118,255,.67) !important;
    animation:forgeProOrbit3 29s linear infinite !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-4 {
    width:270px !important;
    height:485px !important;
    border-color:rgba(116,199,255,.45) !important;
    animation:forgeProOrbit4 35s linear infinite reverse !important;
  }

  .forge-home-page .forge-orbit-system .orbit-ring-5 {
    width:530px !important;
    height:315px !important;
    border-color:rgba(151,88,255,.50) !important;
    animation:forgeProOrbit5 41s linear infinite !important;
  }

  /* Central field: no card, no square, only a soft luminous core. */
  .forge-home-page .forge-orbit-system .forge-orbit-center {
    width:142px !important;
    height:142px !important;
    border:1px solid rgba(181,111,255,.36) !important;
    background:
      radial-gradient(circle,
        rgba(164,75,255,.25) 0%,
        rgba(100,35,190,.12) 42%,
        rgba(7,3,16,.10) 70%,
        transparent 78%) !important;
    box-shadow:
      0 0 20px rgba(145,59,255,.30),
      0 0 45px rgba(102,38,205,.18),
      inset 0 0 25px rgba(174,91,255,.12) !important;
    animation:none !important;
  }

  .forge-home-page .forge-core-glow {
    inset:-22px !important;
    background:
      radial-gradient(circle,
        rgba(170,78,255,.23),
        rgba(110,40,215,.08) 44%,
        transparent 72%) !important;
    filter:blur(10px) !important;
  }

  /* The logo PNG contains a dark square; visually dissolve that square. */
  .forge-home-page .forge-core-inner {
    width:64px !important;
    height:64px !important;
    border-radius:50% !important;
    background:transparent !important;
    box-shadow:none !important;
    overflow:visible !important;
    mix-blend-mode:screen !important;
  }

  .forge-home-page .forge-core-inner img {
    width:54px !important;
    height:54px !important;
    object-fit:contain !important;
    background:transparent !important;
    mix-blend-mode:screen !important;
    filter:
      brightness(1.16)
      contrast(1.08)
      drop-shadow(0 0 5px rgba(255,255,255,.72))
      drop-shadow(0 0 13px rgba(177,90,255,.92))
      drop-shadow(0 0 23px rgba(137,54,255,.62)) !important;
  }

  /* Fixed semantic anchors — never orbit with the rings. */
  .forge-home-page .forge-orbit-system .orbit-ai {
    left:50% !important;
    top:8px !important;
    right:auto !important;
    bottom:auto !important;
    transform:translateX(-50%) !important;
    animation:none !important;
  }

  .forge-home-page .forge-orbit-system .orbit-human {
    left:18px !important;
    top:245px !important;
    right:auto !important;
    bottom:auto !important;
    transform:none !important;
    animation:none !important;
  }

  .forge-home-page .forge-orbit-system .orbit-task {
    right:18px !important;
    top:245px !important;
    left:auto !important;
    bottom:auto !important;
    transform:none !important;
    animation:none !important;
  }

  .forge-home-page .forge-orbit-system .orbit-skill {
    left:50% !important;
    bottom:4px !important;
    top:auto !important;
    right:auto !important;
    transform:translateX(-50%) !important;
    animation:none !important;
  }

  .forge-home-page .forge-orbit-node {
    gap:5px !important;
  }

  .forge-home-page .forge-orbit-node .orbit-node-icon {
    width:50px !important;
    height:50px !important;
    border:1px solid rgba(186,119,255,.72) !important;
    background:
      radial-gradient(circle at 50% 42%,
        rgba(117,45,205,.55),
        rgba(12,5,25,.90) 72%) !important;
    box-shadow:
      0 0 7px rgba(161,75,255,.46),
      0 0 15px rgba(126,48,222,.24),
      inset 0 0 10px rgba(204,138,255,.12) !important;
  }

  .forge-home-page .forge-orbit-node strong {
    font-size:12px !important;
    letter-spacing:.08em !important;
    text-shadow:0 0 10px rgba(175,88,255,.25) !important;
  }

  /* Subtle moving points add depth without making the system noisy. */
  .forge-home-page .forge-orbit-system .orbit-particle {
    width:3px !important;
    height:3px !important;
    box-shadow:
      0 0 5px #fff,
      0 0 12px rgba(174,87,255,.72) !important;
  }

  .forge-home-page .forge-orbit-system .orbit-particle-2 {
    background:#8bdfff !important;
    box-shadow:0 0 6px #8bdfff,0 0 13px rgba(70,190,255,.55) !important;
  }

  /* Five genuinely separate rotations. */
  @keyframes forgeProOrbit1 {
    from { transform:translate(-50%,-50%) rotate(-18deg); }
    to   { transform:translate(-50%,-50%) rotate(342deg); }
  }

  @keyframes forgeProOrbit2 {
    from { transform:translate(-50%,-50%) rotate(26deg); }
    to   { transform:translate(-50%,-50%) rotate(-334deg); }
  }

  @keyframes forgeProOrbit3 {
    from { transform:translate(-50%,-50%) rotate(-9deg); }
    to   { transform:translate(-50%,-50%) rotate(351deg); }
  }

  @keyframes forgeProOrbit4 {
    from { transform:translate(-50%,-50%) rotate(34deg); }
    to   { transform:translate(-50%,-50%) rotate(-326deg); }
  }

  @keyframes forgeProOrbit5 {
    from { transform:translate(-50%,-50%) rotate(61deg); }
    to   { transform:translate(-50%,-50%) rotate(421deg); }
  }

  /* Prevent the orbital field from being clipped by the hero's right column. */
  .forge-home-page .forge-home-hero,
  .forge-home-page .forge-home-hero-grid,
  .forge-home-page .forge-home-visual,
  .forge-home-page .forge-home-orbit {
    overflow:visible !important;
  }


/* =========================================================
   PRICING SECTION
========================================================= */
.forge-pricing-section{position:relative;isolation:isolate;overflow:hidden;padding:120px 5vw 105px;background:radial-gradient(850px 520px at 50% 12%,rgba(151,76,255,.13),transparent 66%),radial-gradient(520px 420px at 3% 70%,rgba(47,109,255,.09),transparent 70%),#07050e;color:#fff}
.forge-pricing-ambient{position:absolute;width:520px;height:520px;border-radius:50%;filter:blur(80px);opacity:.18;pointer-events:none;z-index:-1}.forge-pricing-ambient-left{left:-300px;top:190px;background:#287cff}.forge-pricing-ambient-right{right:-300px;top:120px;background:#e53fff}
.forge-pricing-heading{text-align:center;max-width:1000px;margin:0 auto 54px}.forge-pricing-kicker{display:flex;align-items:center;justify-content:center;gap:18px;color:#c79aff;font-size:10px;font-weight:900;letter-spacing:.24em}.forge-pricing-kicker i{display:block;width:55px;height:1px;background:linear-gradient(90deg,transparent,#a56cff)}.forge-pricing-kicker i:last-child{background:linear-gradient(90deg,#a56cff,transparent)}.forge-pricing-heading h2{margin:18px 0 12px;font-size:clamp(42px,5vw,72px);line-height:.98;letter-spacing:-.065em;font-weight:720}.forge-pricing-heading h2 em{font-style:normal;background:linear-gradient(90deg,#d66cff,#8b72ff,#55b5ff);-webkit-background-clip:text;background-clip:text;color:transparent}.forge-pricing-heading p{margin:0;color:rgba(230,222,245,.64);font-size:15px}.forge-pricing-switch{display:inline-flex;align-items:center;gap:5px;margin-top:24px;padding:5px;border:1px solid rgba(205,170,255,.17);border-radius:999px;background:rgba(255,255,255,.045);box-shadow:inset 0 1px rgba(255,255,255,.05),0 15px 45px rgba(0,0,0,.2)}.forge-pricing-switch span{padding:9px 16px;border-radius:999px;color:rgba(255,255,255,.48);font-size:11px;font-weight:800}.forge-pricing-switch span.active{background:linear-gradient(135deg,#f263df,#8b69ff);color:#fff;box-shadow:0 5px 22px rgba(189,82,255,.3)}.forge-pricing-switch b{margin-left:3px;padding:7px 10px;border-radius:999px;background:rgba(157,90,255,.15);color:#d7b8ff;font-size:9px}
.forge-pricing-grid{width:min(1400px,100%);margin:0 auto;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;align-items:stretch}.forge-price-card{position:relative;min-height:620px;padding:34px 31px 29px;text-align:left;border-radius:27px;overflow:hidden;isolation:isolate;cursor:pointer;font:inherit;color:#fff;background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.018) 55%,rgba(4,4,10,.72));border:1px solid rgba(190,157,255,.19);box-shadow:inset 0 1px rgba(255,255,255,.06),0 25px 70px rgba(0,0,0,.24);transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .35s,box-shadow .35s,background .35s}.forge-price-card:before{content:"";position:absolute;inset:0;background:radial-gradient(500px 240px at 50% -10%,rgba(155,92,255,.17),transparent 70%);z-index:-1;pointer-events:none}.forge-price-card:hover{transform:translateY(-9px);border-color:rgba(211,174,255,.46);box-shadow:inset 0 1px rgba(255,255,255,.1),0 32px 90px rgba(63,23,119,.34),0 0 55px rgba(145,76,255,.1)}.forge-price-student{background:linear-gradient(145deg,rgba(26,63,111,.25),rgba(9,10,22,.82) 60%,rgba(4,6,13,.95))}.forge-price-org{background:linear-gradient(145deg,rgba(99,59,18,.23),rgba(17,11,15,.84) 60%,rgba(8,6,9,.95))}.forge-price-pro{margin-top:-16px;border-color:rgba(221,86,255,.65);background:linear-gradient(145deg,rgba(104,34,145,.35),rgba(34,13,58,.9) 55%,rgba(11,7,19,.98));box-shadow:inset 0 1px rgba(255,255,255,.13),0 35px 100px rgba(130,34,199,.34),0 0 70px rgba(219,65,255,.14)}.forge-price-pro:hover{transform:translateY(-14px);border-color:rgba(239,137,255,.9);box-shadow:inset 0 1px rgba(255,255,255,.16),0 42px 110px rgba(130,34,199,.43),0 0 90px rgba(219,65,255,.2)}.forge-price-number{position:absolute;right:27px;top:24px;color:rgba(255,255,255,.27);font-size:10px;letter-spacing:.18em;font-weight:900}.forge-price-icon{display:grid;place-items:center;width:58px;height:58px;border-radius:17px;border:1px solid rgba(199,158,255,.28);background:rgba(255,255,255,.035);box-shadow:inset 0 0 22px rgba(148,78,255,.12),0 0 28px rgba(120,70,255,.09)}.forge-price-student .forge-price-icon{color:#56b8ff;border-color:rgba(66,177,255,.4)}.forge-price-pro .forge-price-icon{color:#ff67ec;border-color:rgba(255,89,229,.55)}.forge-price-org .forge-price-icon{color:#ffb743;border-color:rgba(255,177,60,.46)}.forge-price-label{display:block;margin-top:34px;color:rgba(204,174,255,.67);font-size:9px;font-weight:900;letter-spacing:.18em}.forge-price-card h3{margin:9px 0 9px;font-size:29px;letter-spacing:-.045em}.forge-price-card h3 strong{color:#83bfff}.forge-price-pro h3 strong{color:#f36bea}.forge-price-org h3 strong{color:#ffbd53}.forge-price-card h4{margin:22px 0 3px;font-size:34px;letter-spacing:-.04em}.forge-price-amount{display:flex;align-items:baseline;gap:7px;margin:18px 0 5px}.forge-price-amount b{font-size:37px;letter-spacing:-.05em}.forge-price-amount span{color:rgba(255,255,255,.47);font-size:13px}.forge-price-card>p{min-height:49px;margin:0;color:rgba(228,219,240,.63);font-size:12px;line-height:1.65}.forge-price-features{display:grid;gap:9px;margin-top:21px}.forge-price-features span{display:flex;align-items:flex-start;gap:8px;color:rgba(237,231,245,.72);font-size:10px;line-height:1.4}.forge-price-features svg{flex:0 0 auto;margin-top:1px;color:#67a9ff}.forge-price-pro .forge-price-features svg{color:#f06be9}.forge-price-org .forge-price-features svg{color:#ffb742}.forge-price-cta{position:absolute;left:31px;right:31px;bottom:28px;display:flex;align-items:center;justify-content:center;gap:9px;padding:13px 16px;border-radius:13px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.055);color:#fff;font-size:11px;font-weight:900;transition:background .25s,border-color .25s,transform .25s}.forge-price-card:hover .forge-price-cta{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.28)}.forge-price-pro .forge-price-cta{background:linear-gradient(90deg,#ec63df,#a36fff);border-color:transparent;color:#130718;box-shadow:0 10px 30px rgba(214,71,228,.23)}.forge-popular{position:absolute;left:50%;top:0;transform:translate(-50%,-1px);padding:8px 20px;border-radius:0 0 16px 16px;background:linear-gradient(90deg,#f15ce7,#9d6dff);color:#16071d;font-size:9px;font-weight:900;letter-spacing:.1em;box-shadow:0 8px 30px rgba(222,74,233,.3)}.forge-pricing-trust{display:flex;justify-content:center;flex-wrap:wrap;gap:30px;margin:35px auto 0;color:rgba(219,207,235,.43);font-size:10px;letter-spacing:.06em}
.forge-payment-backdrop{position:fixed;inset:0;z-index:10000;display:grid;place-items:center;padding:22px;background:rgba(4,2,9,.78);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);animation:forgePaymentFade .2s ease both}.forge-payment-modal{position:relative;width:min(760px,100%);padding:34px;border-radius:27px;border:1px solid rgba(222,115,255,.45);background:linear-gradient(145deg,rgba(52,20,77,.96),rgba(10,6,18,.98));box-shadow:0 40px 120px rgba(0,0,0,.65),0 0 80px rgba(191,57,255,.16);color:#fff}.forge-payment-close{position:absolute;right:18px;top:16px;width:35px;height:35px;border:1px solid rgba(255,255,255,.12);border-radius:50%;background:rgba(255,255,255,.04);color:#fff;font-size:23px;cursor:pointer}.forge-payment-kicker{color:#f17be9;font-size:10px;font-weight:900;letter-spacing:.2em}.forge-payment-modal h2{margin:10px 45px 7px 0;font-size:32px;letter-spacing:-.04em}.forge-payment-subtitle{margin:0;color:rgba(230,216,241,.55);font-size:12px}.forge-payment-layout{display:grid;grid-template-columns:270px 1fr;gap:30px;margin-top:28px}.forge-payment-qr-shell{padding:20px;border:1px solid rgba(223,164,255,.18);border-radius:20px;background:rgba(255,255,255,.035);text-align:center}.forge-payment-qr-placeholder{width:180px;height:180px;margin:0 auto 14px;border:9px solid #fff;border-radius:8px;background-color:#fff;background-image:repeating-linear-gradient(90deg,#101018 0 6px,#fff 6px 12px),repeating-linear-gradient(0deg,transparent 0 9px,rgba(15,15,22,.95) 9px 15px);box-shadow:0 0 30px rgba(255,255,255,.09)}.forge-payment-qr-placeholder span{display:inline-block;width:36px;height:36px;margin:6px;border:7px solid #11111a;background:#fff;box-shadow:inset 0 0 0 5px #11111a}.forge-payment-qr-shell strong{display:block;font-size:10px;letter-spacing:.16em}.forge-payment-qr-shell small{display:block;margin-top:7px;color:rgba(228,218,239,.42);font-size:9px;line-height:1.5}.forge-payment-details{display:grid;align-content:center;gap:13px}.forge-payment-details>div{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.08)}.forge-payment-details span{color:rgba(228,218,239,.42);font-size:10px}.forge-payment-details strong{font-size:12px}.forge-payment-details button{margin-top:10px;padding:13px;border:1px solid rgba(224,140,255,.3);border-radius:12px;background:rgba(255,255,255,.045);color:#fff;font:inherit;font-size:11px;font-weight:800;cursor:pointer}@keyframes forgePaymentFade{from{opacity:0}to{opacity:1}}
@media(max-width:1000px){.forge-pricing-grid{grid-template-columns:1fr;max-width:620px}.forge-price-pro{margin-top:0;order:-1}.forge-price-card{min-height:570px}.forge-pricing-section{padding-left:22px;padding-right:22px}}
@media(max-width:650px){.forge-pricing-heading h2{font-size:42px}.forge-payment-layout{grid-template-columns:1fr}.forge-payment-modal{padding:27px 20px}.forge-payment-qr-placeholder{width:155px;height:155px}.forge-pricing-trust{gap:12px;line-height:1.6}}
/* =========================================================
   FORGE PRO — REAL UPI QR / DEMO ACTIVATION
   Existing FORGE styles are preserved; these are payment-only additions.
========================================================= */
.forge-payment-modal-real{max-width:820px}
.forge-payment-layout-real{grid-template-columns:320px 1fr;gap:34px}
.forge-payment-qr-real{padding:22px}
.forge-payment-qr-frame{width:270px;height:270px;margin:0 auto 16px;padding:8px;border-radius:15px;background:#fff;display:grid;place-items:center;box-shadow:0 0 35px rgba(255,255,255,.10)}
.forge-payment-qr-image{display:block;width:100%;height:100%;object-fit:contain;border-radius:7px;image-rendering:auto}
.forge-payment-qr-real strong{font-size:10px;letter-spacing:.16em}
.forge-payment-qr-real small{max-width:250px;margin:8px auto 0}
.forge-payment-details-real{gap:0}
.forge-payment-details-real>div{padding:15px 0}
.forge-payment-details-real>div>span{font-size:9px;letter-spacing:.08em;text-transform:uppercase}
.forge-payment-details-real>div>strong{font-size:12px}
.forge-payment-plan strong{color:#f47bea}
.forge-upi-row{display:flex;align-items:center;justify-content:flex-end;gap:8px;max-width:70%}
.forge-upi-row strong{font-size:11px!important;word-break:break-all}
.forge-copy-upi{border:1px solid rgba(255,255,255,.13);border-radius:8px;padding:6px 8px;background:rgba(255,255,255,.05);color:#fff;font:inherit;font-size:9px;font-weight:800;cursor:pointer}
.forge-copy-upi:hover{background:rgba(255,255,255,.10)}
.forge-payment-open-upi,.forge-payment-primary{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;margin-top:12px;padding:13px;border-radius:12px;font:inherit;font-size:11px;font-weight:900;cursor:pointer;transition:transform .2s,box-shadow .2s,background .2s}
.forge-payment-open-upi{border:1px solid rgba(240,107,233,.32);background:rgba(240,107,233,.08);color:#fff}
.forge-payment-open-upi:hover,.forge-payment-primary:hover:not(:disabled){transform:translateY(-2px)}
.forge-payment-primary{border:0;background:linear-gradient(90deg,#ec63df,#a36fff);color:#17071c;box-shadow:0 10px 30px rgba(214,71,228,.22)}
.forge-payment-primary:disabled{opacity:.65;cursor:wait}
.forge-payment-later{margin:11px auto 0!important;padding:5px!important;border:0!important;background:transparent!important;color:rgba(228,218,239,.42)!important;font-size:9px!important}
.forge-payment-warning{display:flex;align-items:flex-start;gap:8px;margin-top:20px;padding:12px 13px;border:1px solid rgba(255,193,91,.18);border-radius:12px;background:rgba(255,177,60,.045);color:rgba(242,228,210,.58);font-size:9px;line-height:1.55}
.forge-payment-warning svg{flex:0 0 auto;color:#ffbf62;margin-top:1px}
.forge-payment-warning strong{color:rgba(255,222,169,.88)}
.forge-payment-success{text-align:center;padding:42px 20px 28px;max-width:590px;margin:0 auto}
.forge-payment-success-icon{width:74px;height:74px;margin:0 auto 22px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(105,236,181,.35);background:rgba(72,220,157,.08);color:#73edb9;box-shadow:0 0 45px rgba(61,223,154,.12)}
.forge-payment-success h2{margin:12px 0 10px;font-size:36px;letter-spacing:-.045em}
.forge-payment-success p{max-width:470px;margin:0 auto;color:rgba(230,216,241,.58);font-size:12px;line-height:1.7}
.forge-payment-success-badge{display:inline-flex;align-items:center;gap:7px;margin-top:22px;padding:8px 12px;border:1px solid rgba(105,236,181,.22);border-radius:999px;background:rgba(72,220,157,.07);color:#9af2cb;font-size:9px;font-weight:900;letter-spacing:.1em}
.forge-payment-success .forge-payment-primary{max-width:270px;margin:25px auto 0}
.forge-payment-spin{animation:forgePaymentSpin .8s linear infinite}
@keyframes forgePaymentSpin{to{transform:rotate(360deg)}}
@media(max-width:700px){
  .forge-payment-layout-real{grid-template-columns:1fr}
  .forge-payment-qr-frame{width:min(270px,72vw);height:min(270px,72vw)}
  .forge-upi-row{max-width:72%}
}
@media(max-width:650px){
  .forge-payment-modal-real{padding:27px 18px}
  .forge-payment-success{padding:28px 10px 18px}
  .forge-payment-success h2{font-size:30px}
}


`;


function ForgeHomeStyles() {
  return <style>{FORGE_HOME_REDESIGN_CSS}</style>;
}

/* =========================================================
   HEADER
========================================================= */

function Header() {
  const location=useLocation();
  if(location.pathname.startsWith("/student") || location.pathname.startsWith("/organization")) return null;
  return (
    <header className="site-header forge-home-header">
      <NavLink to="/" className="forge-brand">
        <img
          src="/forge-logo.png"
          alt="FORGE"
          className="forge-brand-mark"
        />
        <span className="forge-brand-copy">
          <strong>FORGE</strong>
          <small>
            Future-Oriented Workforce
            <br />
            Reconfiguration &amp; Growth Engine
          </small>
        </span>
      </NavLink>

      <nav className="navigation forge-home-nav">
        <NavLink to="/" end className={({ isActive }) => `navigation-link forge-home-link ${isActive ? "active" : ""}`}>
          Home
        </NavLink>
        <NavLink to="/student" className="navigation-link forge-home-link">
          For Students
        </NavLink>
        <NavLink to="/organization" className="navigation-link forge-home-link">
          For Organizations
        </NavLink>
        <NavLink to="/#how-it-works" className="navigation-link forge-home-link">
          How FORGE Works
        </NavLink>
        <NavLink to="/#about" className="navigation-link forge-home-link">
          About
        </NavLink>
      </nav>

      <NavLink to="/student" className="forge-get-started">
        <span>Get Started</span>
        <ArrowRight size={18} />
      </NavLink>
    </header>
  );
}


/* =========================================================
   HOME
========================================================= */

function HomePage() {
  const navigate = useNavigate();
  const [activeProblem, setActiveProblem] = useState(null);
  const [activeProblemPanel, setActiveProblemPanel] = useState(null);
  const [showProPayment, setShowProPayment] = useState(false);

  const problemDetails = {
    before: {
      task: {
        title: "Work creates capability.",
        text: "Repeated tasks give people real exposure to how work is performed, where decisions happen, and where mistakes need to be corrected.",
        flow: ["TASK", "EXPOSURE", "LEARNING"]
      },
      practice: {
        title: "Practice turns knowledge into usable skill.",
        text: "When people repeatedly solve real problems, they build speed, judgment, context and the ability to handle situations that a textbook cannot fully predict.",
        flow: ["PRACTICE", "FEEDBACK", "JUDGMENT"]
      },
      capability: {
        title: "Experience becomes capability.",
        text: "Over time, repeated exposure compounds into practical capability: knowing what to do, why to do it, and how to adapt when the situation changes.",
        flow: ["EXPERIENCE", "CONTEXT", "CAPABILITY"]
      }
    },
    after: {
      ai: {
        title: "Automation absorbs part of the work.",
        text: "AI can take over repetitive or highly structured work, increasing speed and productivity while changing where people get their hands-on exposure.",
        flow: ["AI", "AUTOMATION", "WORK SHIFT"]
      },
      exposure: {
        title: "Less work can mean less practice.",
        text: "When important tasks disappear from a person's workflow, the opportunities to practice the decisions and exceptions behind those tasks can shrink too.",
        flow: ["LESS WORK", "LESS PRACTICE", "EXPOSURE GAP"]
      },
      risk: {
        title: "Capability risk can become invisible.",
        text: "A team may look more productive while future capability weakens underneath. FORGE helps make that hidden exposure visible so it can be redesigned deliberately.",
        flow: ["PRODUCTIVITY", "HIDDEN GAP", "CAPABILITY RISK"]
      }
    }
  };

  const selectProblemPanel = (panel) => {
    setActiveProblemPanel((current) => current === panel ? null : panel);
  };

  const selectProblemPart = (panel, part) => {
    setActiveProblemPanel(panel);
    setActiveProblem((current) =>
      current === `${panel}-${part}` ? null : `${panel}-${part}`
    );
  };

  const renderDetail = (panel, part) => {
    const detail = problemDetails[panel][part];
    if (!detail || activeProblem !== `${panel}-${part}`) return null;

    return (
      <div className={`forge-problem-detail ${panel === "before" ? "before-detail" : "after-detail"}`}>
        <div className="forge-detail-label">
          {panel === "before" ? "WHY THIS MATTERS" : "WHAT CHANGES"}
        </div>
        <h3>{detail.title}</h3>
        <p>{detail.text}</p>
        <div className="forge-detail-flow">
          {detail.flow.map((item, index) => (
            <Fragment key={item}>
              <span>{item}</span>
              {index < detail.flow.length - 1 && <i>→</i>}
            </Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="forge-home-page">
      <section className="hero slide forge-home-hero">
        <div className="forge-home-ambient" aria-hidden="true">
          <div className="forge-star forge-star-1" />
          <div className="forge-star forge-star-2" />
          <div className="forge-star forge-star-3" />
          <div className="forge-star forge-star-4" />
          <div className="forge-star forge-star-5" />
        </div>

        <div className="forge-home-grid">
          <div className="hero-copy forge-home-copy">
            <div className="micro-label forge-home-eyebrow">
              <span />
              AI-POWERED WORKFORCE INTELLIGENCE
            </div>

            <h1 className="hero-title forge-home-title">
              <span>Understand</span>
              <span>how work changes.</span>
              <span className="forge-gradient-text">Build what comes next.</span>
            </h1>

            <p className="hero-description forge-home-description">
              FORGE maps work to human capability, measures capability exposure
              after automation, and helps individuals, institutions and
              organizations build a future-ready workforce.
            </p>

            <div className="hero-actions forge-home-actions">
              <button className="forge-primary-cta" onClick={() => navigate("/student")}>
                Explore FORGE
                <ArrowRight size={18} />
              </button>
              <button className="forge-secondary-cta" onClick={() => navigate("/#how-it-works")}>
                <span className="forge-play-icon"><PlayCircle size={19} /></span>
                See How It Works
              </button>
            </div>

            <div className="hero-stats forge-home-stats">
              <StatItem value="3+" label="GLOBAL DATASETS" />
              <StatItem value="50K+" label="SKILLS MAPPED" />
              <StatItem value="1M+" label="JOB ROLES ANALYZED" />
              <StatItem value="AI" label="POWERED INSIGHTS" />
            </div>
          </div>

          <div className="hero-orbit forge-home-orbit"><OrbitalSystem /></div>
        </div>

        <div className="forge-earth forge-earth-image-wrap" aria-hidden="true">
          <div className="forge-earth-atmosphere" />
          <img className="forge-earth-image" src="/forge-earth-horizon-integrated.png" alt="" />
          <div className="forge-earth-soft-fade" />
        </div>

        <div className="forge-scroll-cue">
          <span className="forge-mouse"><i /></span>
          <span>SCROLL TO EXPLORE</span>
        </div>
      </section>

      <StudentChooser />

      <section className="problem-section slide forge-problem-interactive" id="how-it-works">
        <SectionHeader
          eyebrow="THE PROBLEM"
          title={<>AI changes more than jobs.<br />It changes how people learn.</>}
          description="When AI absorbs the work through which people traditionally build expertise, productivity can increase while practical capability exposure decreases."
        />

        <div className={`problem-panel forge-problem-panel ${activeProblemPanel ? "has-focus" : ""}`}>
          <div
            className={`problem-half forge-problem-card before-problem-card ${
              activeProblemPanel === "before"
                ? "panel-focused"
                : activeProblemPanel === "after"
                ? "panel-dismissed panel-dismissed-left"
                : ""
            } ${activeProblem?.startsWith("before-") ? "is-active" : ""}`}
            onClick={() => selectProblemPanel("before")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                selectProblemPanel("before");
              }
            }}
            aria-label="Focus Before Automation panel"
          >
            <div className="forge-problem-card-top">
              <div className="tiny-blue-dot"><span />BEFORE AUTOMATION</div>
              <span className="forge-problem-index">01</span>
            </div>

            <div className="forge-problem-card-copy">
              <h2>Work creates capability.</h2>
              <p>People repeatedly perform tasks, make decisions, correct mistakes, and develop practical capability through exposure.</p>
            </div>

            <div className="process-row forge-process-row">
              <button type="button" className={`forge-process-button ${activeProblem === "before-task" ? "is-selected" : ""}`} onClick={() => selectProblemPart("before", "task")} aria-label="Explore task stage">
                <ProcessBox title="TASK" subtitle="Repeated work" />
              </button>
              <ProcessArrow />
              <button type="button" className={`forge-process-button ${activeProblem === "before-practice" ? "is-selected" : ""}`} onClick={() => selectProblemPart("before", "practice")} aria-label="Explore practice stage">
                <ProcessBox title="PRACTICE" subtitle="Real exposure" />
              </button>
              <ProcessArrow />
              <button type="button" className={`forge-process-button ${activeProblem === "before-capability" ? "is-selected" : ""}`} onClick={() => selectProblemPart("before", "capability")} aria-label="Explore capability stage">
                <ProcessBox title="CAPABILITY" subtitle="Experience" />
              </button>
            </div>

            {renderDetail("before", "task")}
            {renderDetail("before", "practice")}
            {renderDetail("before", "capability")}
          </div>

          <div
            className={`problem-half forge-problem-card after-problem-card ${
              activeProblemPanel === "after"
                ? "panel-focused"
                : activeProblemPanel === "before"
                ? "panel-dismissed panel-dismissed-right"
                : ""
            } ${activeProblem?.startsWith("after-") ? "is-active" : ""}`}
            onClick={() => selectProblemPanel("after")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                selectProblemPanel("after");
              }
            }}
            aria-label="Focus After Automation panel"
          >
            <div className="forge-problem-card-top">
              <div className="tiny-blue-dot"><span />AFTER AUTOMATION</div>
              <span className="forge-problem-index">02</span>
            </div>

            <div className="forge-problem-card-copy">
              <h2>Productivity can hide<br />capability loss.</h2>
              <p>AI can remove repetitive tasks successfully while reducing the opportunities humans have to practice the capabilities behind those tasks.</p>
            </div>

            <div className="process-row forge-process-row">
              <button type="button" className={`forge-process-button ${activeProblem === "after-ai" ? "is-selected" : ""}`} onClick={() => selectProblemPart("after", "ai")} aria-label="Explore AI automation stage">
                <ProcessBox title="AI" subtitle="Automation" />
              </button>
              <ProcessArrow />
              <button type="button" className={`forge-process-button ${activeProblem === "after-exposure" ? "is-selected" : ""}`} onClick={() => selectProblemPart("after", "exposure")} aria-label="Explore exposure stage">
                <ProcessBox title="EXPOSURE" subtitle="Reduced practice" />
              </button>
              <ProcessArrow />
              <button type="button" className={`forge-process-button ${activeProblem === "after-risk" ? "is-selected" : ""}`} onClick={() => selectProblemPart("after", "risk")} aria-label="Explore risk stage">
                <ProcessBox title="RISK" subtitle="Future capability" />
              </button>
            </div>

            {renderDetail("after", "ai")}
            {renderDetail("after", "exposure")}
            {renderDetail("after", "risk")}
          </div>
        </div>

        <div className="forge-problem-note">
          <span className="forge-problem-note-dot" />
          <span>Click any stage to understand what changes.</span>
        </div>
      </section>

      <ForgePricingSection
        navigate={navigate}
        onOpenProPayment={() => setShowProPayment(true)}
      />

      {showProPayment && (
        <ForgeProPaymentModal onClose={() => setShowProPayment(false)} />
      )}
    </div>
  );
}

/* =========================================================
   FORGE PRICING / CHOOSE YOUR FORGE
========================================================= */

function ForgePricingSection({ navigate, onOpenProPayment }) {
  const studentFeatures = [
    "Career & capability assessment",
    "Personalized learning roadmap",
    "Industry Pulse",
    "ELLA AI mentor",
    "Student workspace",
  ];

  const proFeatures = [
    "Personalized career roadmap",
    "AI capability assessment",
    "Industry Pulse — full access",
    "ELLA AI mentor",
    "Visual Learn + interactive concepts",
    "Ask a Doubt — text, image & documents",
    "Target-year planning",
    "Study planner & progress intelligence",
    "Full FORGE intelligence workspace",
  ];

  const orgFeatures = [
    "WORKTRACE — workforce & task intelligence",
    "SKILL SHADOW — AI exposure & capability risk",
    "WORKFOLD — Human–AI work redesign",
    "LATTICE — future capability planning",
    "Organization intelligence workspace",
    "Custom data integration",
    "Reports & strategic insights",
  ];

  return (
    <section className="forge-pricing-section slide" id="pricing">
      <div className="forge-pricing-ambient forge-pricing-ambient-left" />
      <div className="forge-pricing-ambient forge-pricing-ambient-right" />

      <div className="forge-pricing-heading">
        <span className="forge-pricing-kicker">
          <i /> CHOOSE YOUR FORGE <i />
        </span>
        <h2>
          One platform. <em>Different possibilities.</em>
        </h2>
        <p>Build capability. Understand work. Shape what&apos;s next.</p>

        <div className="forge-pricing-switch" aria-label="Pricing period">
          <span className="active">Monthly</span>
          <span>Yearly</span>
          <b>Save 17%</b>
        </div>
      </div>

      <div className="forge-pricing-grid">
        <button
          type="button"
          className="forge-price-card forge-price-student"
          onClick={() => navigate("/student")}
        >
          <span className="forge-price-number">01</span>
          <span className="forge-price-icon"><GraduationCap size={25} /></span>
          <span className="forge-price-label">FOR INDIVIDUALS</span>
          <h3>FORGE <strong>STUDENT</strong></h3>
          <h4>Free</h4>
          <p>Start your journey for the future of work with a personalized capability path.</p>
          <div className="forge-price-features">
            {studentFeatures.map((item) => <span key={item}><Check size={13} />{item}</span>)}
          </div>
          <span className="forge-price-cta">Enter Student Workspace <ArrowRight size={16} /></span>
        </button>

        <button
          type="button"
          className="forge-price-card forge-price-pro"
          onClick={onOpenProPayment}
        >
          <span className="forge-popular">✦ MOST POPULAR</span>
          <span className="forge-price-number">02</span>
          <span className="forge-price-icon"><Trophy size={25} /></span>
          <span className="forge-price-label">FOR INDIVIDUALS</span>
          <h3>FORGE <strong>PRO</strong></h3>
          <p>Go deeper with full intelligence for your career, capability and industry decisions.</p>
          <div className="forge-price-amount"><b>₹250</b><span>/ month</span></div>
          <div className="forge-price-features">
            {proFeatures.map((item) => <span key={item}><Check size={13} />{item}</span>)}
          </div>
          <span className="forge-price-cta">Get FORGE PRO <ArrowRight size={16} /></span>
        </button>

        <button
          type="button"
          className="forge-price-card forge-price-org"
          onClick={() => navigate("/organization")}
        >
          <span className="forge-price-number">03</span>
          <span className="forge-price-icon"><Building2 size={25} /></span>
          <span className="forge-price-label">FOR ORGANIZATIONS</span>
          <h3>FORGE <strong>ORGANIZATION</strong></h3>
          <p>Workforce intelligence for organizations building a future-ready workforce.</p>
          <div className="forge-price-features">
            {orgFeatures.map((item) => <span key={item}><Check size={13} />{item}</span>)}
          </div>
          <span className="forge-price-cta">Enter Organization Workspace <ArrowRight size={16} /></span>
        </button>
      </div>

      <div className="forge-pricing-trust">
        <span>✦ Real-world workforce data</span>
        <span>✦ AI-powered intelligence</span>
        <span>✦ Built for students & organizations</span>
      </div>
    </section>
  );
}

/* Real PhonePe QR supplied for the FORGE Pro demo. */
const FORGE_PRO_UPI_ID = "6206487877@ibl";
const FORGE_PRO_UPI_URI =
  "upi://pay?pa=" + encodeURIComponent(FORGE_PRO_UPI_ID) +
  "&pn=" + encodeURIComponent("ALISHA PRIYADARSHI") +
  "&am=250&cu=INR&tn=" + encodeURIComponent("FORGE PRO");

const FORGE_PRO_QR_DATA_URL = "data:image/png;base64,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wcyKUUrBaWtra/1+f35+fmlpCScb0UZWf35+vlKpHD58GJeLI4C+B35uenp6hMUtfimgZ7wgaljGtm3bNmEaDiU8rUwmE4vFisUidQeSjtoi2vKAD5nDxz3ucU960pPomcTdG8n9e73eu971rlqtlsvliBVuLmYy0JCEStuGT33qU/fs2eN36yORSKVS+epXv/qFL3wBVScRzKHXS0oH//qKK654/OMfL9heW0c8l5qNO++882Mf+xiYizhMOC6GYbRarTvuuGNUpg2EY7u4uPiCF7wA0ESJ4EsZ6O233/5v//Zv1FcorahwF4LB4OMe97grrrjC10PBD2g2m9/61rc++clPzs/PF4tFXIFarZbP55eXl2dmZp797Ge/8IUvlKidaZqonFgs9qMf/ejTn/70qDaB1wmHwysrK5///OfpX+U1UcDE3GzbXl5eTiaTowo0oV2KxeLXv/71H/7wh6Zpkm2SvBSQq6985Sunpqbq9bq4sCT/6/X6zMzMr/3ar7mZAtFo9Oabb2632zMzMxsbG+QG4HCsq+uuu47iIl6ZR9PDfPz48fe///2ZTAaQD7gR3IiZmZkXvOAFdD+cESIgM9CTYejzuO6660bVl4N9nMvlut3ut771re9+97ubiFr7pa0V/XjuU1NTT37yk1/1qldt27aN4rBRSZNDhw59/OMfP3bsmEDhSy3UJpYqEeSpqamf+7mfe97znuc3phyPx2+55Zb3vOc9//7v/y7VER43kXh3t9udn5+3LOucc87ZsWPHVqezpBem0Wjs27fvwx/+8LFjx0BSo2UBuUNs96SiuodIFJImk8kXv/jFe/fuJcmMvqHcsNfr3XTTTfv27dvY2KCcnGprjl8ul/upn/qpN77xjX6fG4/H/+M//uOtb33rrbfemsvlyuWy1LBms9lSqXTNNde8/vWvv/LKK4Gig3VJMPR6vb//+7//13/911GNKZfIZLfb/dSnPnXw4EFKbJVOw/Ah6KplASN5LiptfX39S1/6EjI6Go3i2ZimGY1GK5XKWWeddfXVV8/OzmKti94lSDg1NfWyl73MDT7spptuetvb3nb33Xfncjlq4eH/dru9uLh43XXXvfzlLz/nnHNIg1E+QAzg9ttvv/HGGz/84Q/T8S5NZPztJZdcctlll23fvv1M9QkJPyiNbzo9Pf3Sl750165dI7k/KaVY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BGLoETePxWLHjx//7ne/O/APjfCgdNVVV+FbYE1j12PptFqtr33ta5xGRKdASRuGsX379p/6qZ+Syj/SBgOdEb377rs30bdC0Pxb3/oWD+10OhxsDEkABp797Gdz7AmCScdpNBo9duzYN77xDUPDf0o/arVajcfjF1xwwc6dO32tR1TaT//0T6NXCHwR9qVnrV6vf/azn0X0+HWo9+3bt2/fPuxl6YXu6Wk/T33qU7dv3040ydbF+77uvwnas2fP3r17SSljo4AI1mq1stns8vLyxz/+8enp6Wq1OjExgXRjww8cOHDZZZel02msS4lekm6t1Wqf//zn3R6ay+Wuuuoq4jZsBdKg1+tlMpnBYPCJT3yC0lWlKwvi8XihUIhEIk984hNnZ2fRSR5yQ/6JQw2H/NzP/dzQi8Ph8NLS0re//W02AShQSraGXo/xwW5Eo9Gf/umfzmazg8FgVMXofsm2baw0U+NQzc/PA2L40G8+GgHEJ19cXJyYmHDWMzwMBs5QYlZ4IBCYmZnB3SOU7/Enwkmmae7YseOlL33pc57zHLct3rVrl61xB60HYmru3bv37W9/+44dO8jOo6sxvnq93mc/+9m1tbVDhw7xv6OqVzv//PPf8IY3nH/++eVymVoUZ2Hlf/zHf+zbt+/QoUPUFBIKgJkSicSTnvSkN7zhDdu3b0dRhfScqVgstrGxcdNNN9Xr9eXlZV/r2djY6Ha7b3/72++66654PE4LPok+AMUe//jHn3feebt377ZtWyB6bD1H8Bvf+MYf/MEflEolXCtJXZTL5fn5+auvvvqd73ynr/VMT093Op1t27b91m/91iWXXFKv18HJwXKkmv6OO+647777jh8/jr/i6/7veMc7vvKVrywvLyMpCOXBG7lc7s///M9f9KIXYQFI8sPX/f3Szp07f/EXf/G6666bnJzEHeezEku59957P/zhD99yyy3hcHh1dTUWi/FPoVAoFovNzMy8613v2r17NzExpdO2tVotk8n8+Mc/vvfee++///6hz/2FX/iFP/zDP8zlcuVyeXJykogToch6vf6JT3ziAx/4AI1mVLAopdLpdKVSOffcc9/whjdgDXgEZiW4yh6iq8Lh8Ic//OGh13c6nc9//vPHjx+///77sfS9d56ENtGLaDR63XXXDXRvhI/dHx2hBcW/KRQK9JM/ggI+q6ur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";

function ForgeProPaymentModal({ onClose }) {
  const [paymentState, setPaymentState] = useState("idle");

  const handleDemoConfirmation = () => {
    if (paymentState === "processing") return;
    setPaymentState("processing");

    window.setTimeout(() => {
      setPaymentState("success");
      try {
        sessionStorage.setItem("forge_pro_demo_active", "true");
      } catch {}
    }, 1200);
  };

  const copyUpi = async () => {
    try {
      await navigator.clipboard.writeText(FORGE_PRO_UPI_ID);
    } catch {}
  };

  return (
    <div
      className="forge-payment-backdrop"
      role="dialog"
      aria-modal="true"
      aria-label="FORGE Pro payment"
    >
      <div className="forge-payment-modal forge-payment-modal-real">
        <button
          type="button"
          className="forge-payment-close"
          onClick={onClose}
          aria-label="Close payment"
        >
          ×
        </button>

        {paymentState === "success" ? (
          <div className="forge-payment-success">
            <div className="forge-payment-success-icon">
              <CheckCircle2 size={34} />
            </div>
            <span className="forge-payment-kicker">PAYMENT FLOW COMPLETE</span>
            <h2>FORGE PRO ACTIVATED.</h2>
            <p>
              Your ₹250 FORGE Pro demo activation is complete.
              Payment verification is intentionally mocked for this hackathon demo.
            </p>
            <div className="forge-payment-success-badge">
              <Check size={14} />
              PRO ACCESS ENABLED
            </div>
            <button
              type="button"
              className="forge-payment-primary"
              onClick={onClose}
            >
              Continue to FORGE <ArrowRight size={15} />
            </button>
          </div>
        ) : (
          <>
            <span className="forge-payment-kicker">FORGE PRO</span>
            <h2>Unlock full FORGE intelligence.</h2>
            <p className="forge-payment-subtitle">
              ₹250 / month · UPI checkout
            </p>

            <div className="forge-payment-layout forge-payment-layout-real">
              <div className="forge-payment-qr-shell forge-payment-qr-real">
                <div className="forge-payment-qr-frame">
                  <img
                    src={FORGE_PRO_QR_DATA_URL}
                    alt="Real FORGE Pro UPI payment QR"
                    className="forge-payment-qr-image"
                  />
                </div>
                <strong>SCAN &amp; PAY</strong>
                <small>
                  Scan this real PhonePe QR using PhonePe, GPay, Paytm or another
                  supported UPI app.
                </small>
              </div>

              <div className="forge-payment-details forge-payment-details-real">
                <div className="forge-payment-plan">
                  <span>Plan</span>
                  <strong>FORGE PRO</strong>
                </div>

                <div>
                  <span>Amount</span>
                  <strong>₹250 / month</strong>
                </div>

                <div>
                  <span>UPI ID</span>
                  <div className="forge-upi-row">
                    <strong>{FORGE_PRO_UPI_ID}</strong>
                    <button
                      type="button"
                      className="forge-copy-upi"
                      onClick={copyUpi}
                    >
                      Copy
                    </button>
                  </div>
                </div>

                <div>
                  <span>Purpose</span>
                  <strong>FORGE PRO</strong>
                </div>

                <button
                  type="button"
                  className="forge-payment-open-upi"
                  onClick={() => {
                    window.location.href = FORGE_PRO_UPI_URI;
                  }}
                >
                  Open UPI App <ArrowRight size={14} />
                </button>

                <button
                  type="button"
                  className="forge-payment-primary"
                  onClick={handleDemoConfirmation}
                  disabled={paymentState === "processing"}
                >
                  {paymentState === "processing" ? (
                    <>
                      <Loader2 size={14} className="forge-payment-spin" />
                      Processing demo...
                    </>
                  ) : (
                    <>
                      I have completed payment <Check size={14} />
                    </>
                  )}
                </button>

                <button
                  type="button"
                  className="forge-payment-later"
                  onClick={onClose}
                >
                  Close &amp; continue later
                </button>
              </div>
            </div>

            <div className="forge-payment-warning">
              <ShieldCheck size={14} />
              <span>
                <strong>Real QR:</strong> scanning can make a real ₹250 UPI
                payment. <strong>Activation:</strong> demo-only; this frontend
                does not verify the transaction automatically.
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}


/* =========================================================
   ORBITAL SYSTEM
========================================================= */

function OrbitalSystem() {
  return (
    <div className="orbit-system forge-orbit-system">
      <div className="orbit-aura" />
      <div className="orbit-ring orbit-ring-1" />
      <div className="orbit-ring orbit-ring-2" />
      <div className="orbit-ring orbit-ring-3" />
      <div className="orbit-ring orbit-ring-4" />
      <div className="orbit-ring orbit-ring-5" />

      <div className="orbit-particle orbit-particle-1" />
      <div className="orbit-particle orbit-particle-2" />
      <div className="orbit-particle orbit-particle-3" />
      <div className="orbit-particle orbit-particle-4" />
      <div className="orbit-particle orbit-particle-5" />
      <div className="orbit-particle orbit-particle-6" />

      <div className="orbit-center forge-orbit-center">
        <div className="forge-core-glow" />
        <div className="forge-core-inner">
          <img src="/forge-logo.png" alt="FORGE" />
        </div>
      </div>

      <OrbitNode
        className="orbit-ai"
        icon={<Cpu size={22} />}
        title="AI"
      />
      <OrbitNode
        className="orbit-human"
        icon={<UserRound size={22} />}
        title="HUMAN"
      />
      <OrbitNode
        className="orbit-task"
        icon={<Workflow size={22} />}
        title="TASK"
      />
      <OrbitNode
        className="orbit-skill"
        icon={<Network size={22} />}
        title="SKILL"
      />
    </div>
  );
}

function OrbitNode({ className, icon, title }) {
  return (
    <div className={`orbit-node forge-orbit-node ${className}`}>
      <div className="orbit-node-icon">{icon}</div>
      <strong>{title}</strong>
    </div>
  );
}


/* =========================================================
   WORKFORCE PAGE
========================================================= */

function WorkforcePage({
  selectedOccupation,
  setSelectedOccupation,
}) {
  const worktraceRef = useRef(null);
  const shadowRef = useRef(null);

  const [occupationOptions, setOccupationOptions] =
    useState([]);

  const [occupationSearch, setOccupationSearch] =
    useState("");

  const [traceData, setTraceData] =
    useState(null);

  const [shadowData, setShadowData] =
    useState(null);

  const [evidenceShadowData, setEvidenceShadowData] =
    useState(null);

  const [gapData, setGapData] =
    useState(null);

  const [evidenceLoading, setEvidenceLoading] =
    useState(false);

  const [aiLevel, setAiLevel] =
    useState(52);

  const [traceLoading, setTraceLoading] =
    useState(false);

  const [shadowLoading, setShadowLoading] =
    useState(false);

  const [occupationLoading, setOccupationLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD OCCUPATIONS
  ======================================================= */

  useEffect(() => {
    async function loadOccupations() {

      setOccupationLoading(true);

      try {

        const response =
          await getOccupations();

        const occupations =
          Array.isArray(response)
            ? response
            : response?.occupations || [];

        setOccupationOptions(
          occupations
        );

      } catch (error) {

        console.error(
          "Occupation list:",
          error
        );

        setOccupationOptions([]);

        setError(
          "Unable to load occupations from the backend."
        );

      } finally {

        setOccupationLoading(false);

      }
    }

    loadOccupations();

  }, []);


  /* =======================================================
     LOAD SELECTED OCCUPATION
  ======================================================= */

  useEffect(() => {

    if (!selectedOccupation) {

      setTraceData(null);
      setShadowData(null);
      setEvidenceShadowData(null);
      setGapData(null);

      return;
    }


    async function loadOccupation() {

      setTraceLoading(true);
      setShadowLoading(true);
      setError("");


      try {

        const response =
          await getOccupationIntelligence(
            selectedOccupation
          );

        setTraceData(
          response
        );

      } catch (error) {

        console.error(
          "WORKTRACE:",
          error
        );

        setTraceData(null);

        setError(
          "Unable to load occupation intelligence."
        );

      } finally {

        setTraceLoading(false);

      }


      try {

        const response =
          await simulateFutureWorkforce({
            occupation:
              selectedOccupation,

            baselineAi:
              0,

            futureAi:
              aiLevel / 100,
          });

        setShadowData(
          response
        );

        // Evidence-aware SKILL SHADOW + GAP ENGINE.
        // These values come directly from the backend; the UI never invents scores.
        try {
          setEvidenceLoading(true);

          const apiBase =
            import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

          const [evidenceResponse, gapResponse] = await Promise.all([
            fetch(
              `${apiBase}/api/skill-shadow/occupation?occupation=${encodeURIComponent(
                selectedOccupation
              )}&ai_adoption=${aiLevel / 100}`
            ),
            fetch(
              `${apiBase}/api/lattice/gaps/${encodeURIComponent(
                selectedOccupation
              )}?ai_adoption=${aiLevel / 100}`
            ),
          ]);

          const evidenceJson = await evidenceResponse.json().catch(() => ({}));
          const gapJson = await gapResponse.json().catch(() => ({}));

          if (evidenceResponse.ok) {
            setEvidenceShadowData(evidenceJson);
          } else {
            setEvidenceShadowData(null);
            console.warn("Evidence-aware Skill Shadow:", evidenceJson?.detail);
          }

          if (gapResponse.ok) {
            setGapData(gapJson);
          } else {
            setGapData(null);
            console.warn("Capability Gap Engine:", gapJson?.detail);
          }
        } catch (evidenceError) {
          console.error("Evidence-aware Skill Shadow / Gap Engine:", evidenceError);
          setEvidenceShadowData(null);
          setGapData(null);
        } finally {
          setEvidenceLoading(false);
        }

      } catch (error) {

        console.error(
          "SKILL SHADOW:",
          error
        );

        setShadowData(null);

      } finally {

        setShadowLoading(false);

      }

    }


    loadOccupation();

  }, [selectedOccupation]);


  /* =======================================================
     RECALCULATE SKILL SHADOW
  ======================================================= */

  async function loadShadow() {

    if (!selectedOccupation) {
      return;
    }

    setShadowLoading(true);

    try {

      const response =
        await simulateFutureWorkforce({
          occupation:
            selectedOccupation,

          baselineAi:
            0,

          futureAi:
            aiLevel / 100,
        });

      setShadowData(
        response
      );

      try {
        setEvidenceLoading(true);

        const apiBase =
          import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

        const [evidenceResponse, gapResponse] = await Promise.all([
          fetch(
            `${apiBase}/api/skill-shadow/occupation?occupation=${encodeURIComponent(
              selectedOccupation
            )}&ai_adoption=${aiLevel / 100}`
          ),
          fetch(
            `${apiBase}/api/lattice/gaps/${encodeURIComponent(
              selectedOccupation
            )}?ai_adoption=${aiLevel / 100}`
          ),
        ]);

        const evidenceJson = await evidenceResponse.json().catch(() => ({}));
        const gapJson = await gapResponse.json().catch(() => ({}));

        setEvidenceShadowData(evidenceResponse.ok ? evidenceJson : null);
        setGapData(gapResponse.ok ? gapJson : null);
      } catch (evidenceError) {
        console.error("Evidence-aware recalculation:", evidenceError);
        setEvidenceShadowData(null);
        setGapData(null);
      } finally {
        setEvidenceLoading(false);
      }

    } catch (error) {

      console.error(
        "SKILL SHADOW:",
        error
      );

      setShadowData(null);

    } finally {

      setShadowLoading(false);

    }
  }


  /* =======================================================
     HASH SCROLL
  ======================================================= */

  const location = useLocation();

  useEffect(() => {

    if (
      location.hash ===
      "#worktrace"
    ) {

      setTimeout(() => {

        worktraceRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

      }, 150);
    }


    if (
      location.hash ===
      "#skill-shadow"
    ) {

      setTimeout(() => {

        shadowRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

      }, 150);
    }

  }, [location.hash]);


  /* =======================================================
     REAL WORKTRACE ARRAYS
  ======================================================= */

  const tasks = useMemo(
    () =>
      findArray(traceData, [
        "modules.worktrace.tasks",
        "worktrace.tasks",
        "tasks",
      ]),
    [traceData]
  );


  const capabilities = useMemo(
    () =>
      findArray(traceData, [
        "modules.worktrace.capabilities",
        "worktrace.capabilities",
        "capabilities",
      ]),
    [traceData]
  );


  /* =======================================================
     ACTUAL BACKEND SKILL SHADOW FIELDS
  ======================================================= */

  const futureShadowPercent =
    extractNumber(
      shadowData,
      [
        "modules.skill_shadow.future.average_skill_shadow_percent",
        "skill_shadow.future.average_skill_shadow_percent",
        "future.average_skill_shadow_percent",
      ]
    );


  const capabilityRiskPercent =
    extractNumber(
      shadowData,
      [
        "modules.skill_shadow.future.average_capability_risk_percent",
        "skill_shadow.future.average_capability_risk_percent",
        "future.average_capability_risk_percent",
      ]
    );


  const humanExposurePercent =
    extractNumber(
      shadowData,
      [
        "modules.skill_shadow.future.average_human_exposure_percent",
        "skill_shadow.future.average_human_exposure_percent",
        "future.average_human_exposure_percent",
      ]
    );


  const futureAiPercent =
    extractNumber(
      shadowData,
      [
        "modules.skill_shadow.future.ai_adoption_percent",
        "skill_shadow.future.ai_adoption_percent",
        "future.ai_adoption_percent",
      ]
    );


  /* =======================================================
     ACTUAL TOP RISK CAPABILITIES
  ======================================================= */

  const riskCapabilities =
    extractRiskCapabilities(
      shadowData
    );

  const evidenceCapabilities =
    extractEvidenceCapabilities(evidenceShadowData);

  const highestImpactGap =
    gapData?.highest_impact_gap ||
    gapData?.highestImpactGap ||
    null;

  const nextPractice =
    gapData?.next_practice ||
    gapData?.nextPractice ||
    null;


  return (
    <section className="page-section slide">

      {/* ===================================================
          OCCUPATION SELECTOR
      =================================================== */}

      <OccupationSelector
        occupationOptions={
          occupationOptions
        }
        occupationSearch={
          occupationSearch
        }
        setOccupationSearch={
          setOccupationSearch
        }
        selectedOccupation={
          selectedOccupation
        }
        setSelectedOccupation={
          setSelectedOccupation
        }
        occupationLoading={
          occupationLoading
        }
      />


      {error && (
        <div className="api-error">
          {error}
        </div>
      )}


      {/* ===================================================
          WORKTRACE
      =================================================== */}

      <div
        ref={worktraceRef}
        id="worktrace"
        className="module-anchor"
      />


      <SectionHeader
        number="01"
        eyebrow="WORKTRACE"
        title={
          <>
            What work
            <br />
            actually exists?
          </>
        }
        description="WORKTRACE decomposes occupations into tasks and connects those tasks to the capabilities people use to perform them."
      />


      <div className="source-tags">

        <span>
          O*NET
        </span>

        <span>
          ESCO
        </span>

        <span>
          NLP
        </span>

        <span>
          EMBEDDINGS
        </span>

      </div>


      {!selectedOccupation ? (

        <EmptyState
          text="Select an occupation to load real work intelligence."
        />

      ) : (

        <div className="worktrace-layout">

          <div className="trace-visual">

            {tasks
              .slice(0, 4)
              .map(
                (
                  task,
                  index
                ) => {

                  const capability =
                    capabilities[
                      index
                    ];

                  return (
                    <TraceRow
                      key={
                        task?.[
                          "Task ID"
                        ] ||
                        task?.id ||
                        index
                      }
                      occupation={
                        selectedOccupation
                      }
                      task={
                        extractLabel(
                          task
                        )
                      }
                      capability={
                        extractLabel(
                          capability
                        )
                      }
                    />
                  );

                }
              )}


            {!traceLoading &&
              tasks.length === 0 && (
                <EmptyState
                  text="No task records were returned for this occupation."
                />
              )}


            <div className="taken-box">

              <span>
                WORKTRACE OUTPUT
              </span>

              <div>

                <em>
                  Task decomposition
                </em>

                <em>
                  Capability mapping
                </em>

                <em>
                  Work exposure
                </em>

                <em>
                  Evidence graph
                </em>

              </div>

            </div>

          </div>


          <div className="trace-meta">

            <DataNumber
              value={
                traceLoading
                  ? "…"
                  : getTaskCount(
                      traceData,
                      tasks
                    )
              }
              label="TASKS"
            />


            <DataNumber
              value={
                traceLoading
                  ? "…"
                  : getCapabilityCount(
                      traceData,
                      capabilities
                    )
              }
              label="CAPABILITIES"
            />


            <div className="trace-status">

              <span className="status-dot-blue" />

              {traceLoading
                ? "ANALYSING"
                : "LIVE INTELLIGENCE"}

            </div>

          </div>

        </div>

      )}


      {/* ===================================================
          DIVIDER
      =================================================== */}

      <div className="module-divider">

        <span />

        <strong>
          ↓
        </strong>

        <span />

      </div>


      {/* ===================================================
          SKILL SHADOW
      =================================================== */}

      <div
        ref={shadowRef}
        id="skill-shadow"
        className="module-anchor"
      />


      <SectionHeader
        number="02"
        eyebrow="SKILL SHADOW"
        title={
          <>
            What capability
            <br />
            starts fading?
          </>
        }
        description="Skill Shadow measures capability exposure that decreases when AI absorbs the work through which people developed that capability."
      />


      {!selectedOccupation ? (

        <EmptyState
          text="Select an occupation above to calculate capability exposure."
        />

      ) : (

        <>

          <div className="shadow-grid">

            {/* =================================================
                DIGITAL TWIN
            ================================================= */}

            <div className="digital-twin-card">

              <div className="card-top">

                <div className="avatar">
                  {getInitials(
                    selectedOccupation
                  )}
                </div>


                <div>

                  <strong>
                    Capability Digital Twin
                  </strong>

                  <small>
                    {selectedOccupation}
                    {" · "}
                    Future Scenario
                  </small>

                </div>


                <span className="risk-label">

                  {shadowLoading
                    ? "CALCULATING"
                    : futureShadowPercent !== null
                      ? "SHADOW DETECTED"
                      : "NO RESULT"}

                </span>

              </div>


              <div className="shadow-main">

                <div
                  className="shadow-ring"
                  style={{
                    "--progress":
                      futureShadowPercent !==
                      null
                        ? `${futureShadowPercent * 3.6}deg`
                        : "0deg",
                  }}
                >

                  <div>

                    <strong>
                      {shadowLoading
                        ? "—"
                        : formatBackendPercent(
                            futureShadowPercent
                          )}
                    </strong>

                  </div>

                </div>


                <div>

                  <h3>
                    Skill Shadow Exposure
                  </h3>

                  <p>
                    Backend-calculated average
                    capability exposure lost under
                    the selected AI scenario.
                  </p>

                </div>

              </div>


              {/* =================================================
                  ACTUAL BACKEND CAPABILITIES
              ================================================= */}

              <div className="capability-bars">

                {riskCapabilities.length === 0 ? (

                  <div className="trace-status">

                    <span className="status-dot-blue" />

                    No capability exposure records
                    returned.

                  </div>

                ) : (

                  riskCapabilities
                    .slice(0, 4)
                    .map(
                      (
                        capability,
                        index
                      ) => (

                        <CapabilityEvidence
                          key={
                            capability.key ||
                            index
                          }
                          capability={
                            capability
                          }
                        />

                      )
                    )

                )}

              </div>

            </div>


            {/* =================================================
                RISK CARD
            ================================================= */}

            <div className="risk-card">

              <h2>
                Capability exposure
              </h2>


              <p className="risk-intro">
                FORGE traces capability risk back
                to the work originally creating its
                exposure.
              </p>


              <RiskRow
                icon={
                  <Workflow size={16} />
                }
                title="Skill Shadow"
                text="Average capability exposure lost in the future scenario."
                value={
                  formatBackendPercent(
                    futureShadowPercent
                  )
                }
              />


              <RiskRow
                icon={
                  <Cpu size={16} />
                }
                title="Automation exposure"
                text="AI adoption returned by the scenario engine."
                value={
                  formatBackendPercent(
                    futureAiPercent
                  )
                }
              />


              <RiskRow
                icon={
                  <Target size={16} />
                }
                title="Capability risk"
                text="Average capability risk calculated by Skill Shadow."
                value={
                  formatBackendPercent(
                    capabilityRiskPercent
                  )
                }
              />


              <RiskRow
                icon={
                  <Network size={16} />
                }
                title="Human exposure"
                text="Average human capability exposure remaining."
                value={
                  formatBackendPercent(
                    humanExposurePercent
                  )
                }
              />

            </div>

          </div>

          {/* =================================================
              EVIDENCE-AWARE CAPABILITY STATE
          ================================================= */}

          <EvidenceAwarePanel
            capabilities={evidenceCapabilities}
            loading={evidenceLoading}
            gap={highestImpactGap}
            nextPractice={nextPractice}
          />


          {/* =================================================
              AI SCENARIO CONTROL
          ================================================= */}

          <div className="inline-control">

            <div>

              <small>
                FUTURE AI ADOPTION
              </small>

              <strong>
                {aiLevel}%
              </strong>

            </div>


            <input
              type="range"
              min="0"
              max="100"
              value={aiLevel}
              onChange={(event) =>
                setAiLevel(
                  Number(
                    event.target.value
                  )
                )
              }
              onMouseUp={
                loadShadow
              }
              onTouchEnd={
                loadShadow
              }
            />


            <button
              className="mini-button"
              onClick={loadShadow}
            >
              Recalculate
            </button>

          </div>

        </>
      )}

    </section>
  );
}


/* =========================================================
   CAPABILITY EVIDENCE
========================================================= */

function CapabilityEvidence({
  capability,
}) {
  return (
    <div className="bar-row">

      <span>
        {capability.name}
      </span>

      <div className="bar">
        <i
          style={{
            width: "100%",
          }}
        />
      </div>

      <strong
        title="Backend exposure lost"
      >
        {formatRawNumber(
          capability.exposureLost
        )}
      </strong>

    </div>
  );
}


/* =========================================================
   EVIDENCE-AWARE SKILL SHADOW
========================================================= */

function EvidenceAwarePanel({
  capabilities,
  loading,
  gap,
  nextPractice,
}) {
  const visible = Array.isArray(capabilities)
    ? capabilities.slice(0, 6)
    : [];

  return (
    <div
      style={{
        marginTop: "18px",
        border: "1px solid #dfe3df",
        borderRadius: "18px",
        background: "#fff",
        overflow: "hidden",
        boxShadow: "0 12px 35px rgba(21,28,24,.06)",
      }}
    >
      <div
        style={{
          padding: "18px 20px",
          background: "#f7f9f6",
          borderBottom: "1px solid #e3e7e3",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "9px",
              fontWeight: 900,
              letterSpacing: ".13em",
              color: "#3565d4",
              textTransform: "uppercase",
            }}
          >
            EVIDENCE-AWARE SKILL SHADOW
          </div>
          <h3
            style={{
              margin: "7px 0 0",
              fontSize: "18px",
              color: "#171c19",
            }}
          >
            AI risk + your demonstrated capability
          </h3>
        </div>

        <span
          style={{
            padding: "7px 10px",
            borderRadius: "999px",
            background: "#eef2ed",
            color: "#52605a",
            fontSize: "9px",
            fontWeight: 900,
            letterSpacing: ".07em",
          }}
        >
          {loading ? "UPDATING" : "BACKEND EVIDENCE"}
        </span>
      </div>

      <div style={{ padding: "18px 20px" }}>
        {!visible.length && !loading ? (
          <div
            style={{
              padding: "16px",
              border: "1px dashed #d4dad5",
              borderRadius: "12px",
              color: "#69716b",
              fontSize: "11px",
              lineHeight: 1.6,
            }}
          >
            No capability-level evidence records are available yet.
            <br />
            <strong>Insufficient Evidence</strong> is different from proving that
            a capability is missing.
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "10px",
            }}
          >
            {visible.map((item, index) => {
              const status = String(
                item.userEvidenceStatus ||
                  item.user_evidence_status ||
                  item.status ||
                  "NO_VALIDATED_EVIDENCE"
              ).toUpperCase();

              const score =
                item.userEvidenceScore ??
                item.user_evidence_score ??
                item.score;

              const risk =
                item.aiRiskBand ||
                item.ai_risk_band ||
                item.riskBand ||
                item.risk_band ||
                "—";

              const state =
                item.evidenceAdjustedState ||
                item.evidence_adjusted_state ||
                "UNVALIDATED";

              return (
                <div
                  key={item.key || item.capabilityId || item.name || index}
                  style={{
                    border: "1px solid #e0e4e0",
                    borderRadius: "13px",
                    padding: "14px",
                    background: "#fff",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: "10px",
                      alignItems: "flex-start",
                    }}
                  >
                    <strong
                      style={{
                        fontSize: "12px",
                        lineHeight: 1.4,
                        color: "#202521",
                      }}
                    >
                      {item.name || item.capability || "Capability"}
                    </strong>

                    <span
                      style={{
                        fontSize: "8px",
                        fontWeight: 900,
                        letterSpacing: ".06em",
                        padding: "5px 7px",
                        borderRadius: "999px",
                        background:
                          status === "DEMONSTRATED"
                            ? "#eaf7ee"
                            : status === "PARTIAL"
                              ? "#fff5df"
                              : "#f0f2f0",
                        color:
                          status === "DEMONSTRATED"
                            ? "#24613d"
                            : status === "PARTIAL"
                              ? "#8a5b14"
                              : "#69716b",
                      }}
                    >
                      {formatEvidenceStatus(status)}
                    </span>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "8px",
                      marginTop: "13px",
                    }}
                  >
                    <EvidenceMetric
                      label="AI RISK"
                      value={formatRiskBand(risk)}
                    />
                    <EvidenceMetric
                      label="USER EVIDENCE"
                      value={
                        score === null || score === undefined
                          ? "—"
                          : `${Number(score).toFixed(1)} / 5`
                      }
                    />
                  </div>

                  <div
                    style={{
                      marginTop: "9px",
                      fontSize: "9px",
                      color: "#737973",
                      letterSpacing: ".03em",
                    }}
                  >
                    State · {formatEvidenceStatus(state)}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {(gap || nextPractice) && (
          <div
            style={{
              marginTop: "16px",
              display: "grid",
              gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)",
              gap: "10px",
            }}
          >
            {gap && (
              <div
                style={{
                  border: "1px solid #e4ddd0",
                  borderRadius: "13px",
                  padding: "14px",
                  background: "#fffaf1",
                }}
              >
                <div
                  style={{
                    fontSize: "9px",
                    fontWeight: 900,
                    letterSpacing: ".11em",
                    color: "#8a5b14",
                  }}
                >
                  HIGHEST-IMPACT GAP
                </div>
                <strong
                  style={{
                    display: "block",
                    marginTop: "7px",
                    fontSize: "13px",
                    color: "#27251f",
                  }}
                >
                  {gap.capability ||
                    gap.name ||
                    gap.target_capability ||
                    "Capability gap"}
                </strong>
                <p
                  style={{
                    margin: "7px 0 0",
                    fontSize: "10px",
                    lineHeight: 1.6,
                    color: "#6d6659",
                  }}
                >
                  {gap.status
                    ? `Evidence status: ${formatEvidenceStatus(gap.status)}`
                    : "Prioritized from evidence deficit, capability importance and work impact."}
                </p>
              </div>
            )}

            {nextPractice && (
              <div
                style={{
                  border: "1px solid #d9e2f7",
                  borderRadius: "13px",
                  padding: "14px",
                  background: "#f7f9ff",
                }}
              >
                <div
                  style={{
                    fontSize: "9px",
                    fontWeight: 900,
                    letterSpacing: ".11em",
                    color: "#3565d4",
                  }}
                >
                  NEXT PRACTICE
                </div>
                <strong
                  style={{
                    display: "block",
                    marginTop: "7px",
                    fontSize: "13px",
                    color: "#202a43",
                  }}
                >
                  {nextPractice.title ||
                    nextPractice.task ||
                    nextPractice.source_work_context?.task ||
                    "Targeted LATTICE practice"}
                </strong>
                <p
                  style={{
                    margin: "7px 0 0",
                    fontSize: "10px",
                    lineHeight: 1.6,
                    color: "#66718a",
                  }}
                >
                  Selected from the real work/capability graph to strengthen the
                  highest-impact unresolved evidence.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


function EvidenceMetric({ label, value }) {
  return (
    <div
      style={{
        padding: "9px",
        borderRadius: "9px",
        background: "#f7f9f6",
      }}
    >
      <div
        style={{
          fontSize: "8px",
          fontWeight: 900,
          letterSpacing: ".09em",
          color: "#7b817c",
        }}
      >
        {label}
      </div>
      <strong
        style={{
          display: "block",
          marginTop: "4px",
          fontSize: "12px",
          color: "#202521",
        }}
      >
        {value}
      </strong>
    </div>
  );
}


function formatEvidenceStatus(status) {
  return String(status || "UNVALIDATED")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


function formatRiskBand(risk) {
  const value = String(risk || "—").toUpperCase();

  if (value === "CRITICAL") return "🔴 CRITICAL";
  if (value === "HIGH") return "🟠 HIGH";
  if (value === "ELEVATED") return "🟡 ELEVATED";
  if (value === "MODERATE") return "🟡 MODERATE";
  if (value === "LOW") return "🟢 LOW";

  return value.replaceAll("_", " ");
}


function extractEvidenceCapabilities(data) {
  const results = [];
  const seen = new Set();

  function walk(value, depth = 0) {
    if (!value || depth > 7) return;

    if (Array.isArray(value)) {
      for (const item of value) walk(item, depth + 1);
      return;
    }

    if (typeof value !== "object") return;

    const name =
      value.capability ||
      value["Capability Name"] ||
      value.capability_name ||
      value.name ||
      "";

    const hasEvidenceField =
      Object.prototype.hasOwnProperty.call(value, "user_evidence_status") ||
      Object.prototype.hasOwnProperty.call(value, "userEvidenceStatus") ||
      Object.prototype.hasOwnProperty.call(value, "evidence_adjusted_state") ||
      Object.prototype.hasOwnProperty.call(value, "evidenceAdjustedState");

    if (typeof name === "string" && name.trim() && hasEvidenceField) {
      const key = (
        value.capability_id ||
        value.capability_key ||
        name.trim()
      ).toString();

      if (!seen.has(key)) {
        seen.add(key);

        results.push({
          key,
          name: name.trim(),
          capabilityId: value.capability_id,
          aiRiskBand:
            value.ai_risk_band ||
            value.aiRiskBand ||
            value.risk_band ||
            value.riskBand,
          userEvidenceScore:
            value.user_evidence_score ??
            value.userEvidenceScore,
          userEvidenceStatus:
            value.user_evidence_status ||
            value.userEvidenceStatus ||
            value.status,
          evidenceAdjustedState:
            value.evidence_adjusted_state ||
            value.evidenceAdjustedState,
        });
      }
    }

    for (const child of Object.values(value)) {
      if (child && typeof child === "object") walk(child, depth + 1);
    }
  }

  walk(data);
  return results;
}


/* =========================================================
   WORKFOLD
========================================================= */

function WorkFoldPage({
  selectedOccupation,
  setSelectedOccupation,
}) {
  const [occupationOptions, setOccupationOptions] =
    useState([]);

  const [occupationSearch, setOccupationSearch] =
    useState("");

  const [aiLevel, setAiLevel] =
    useState(52);

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [occupationLoading, setOccupationLoading] =
    useState(true);


  useEffect(() => {

    async function loadOccupations() {

      try {

        const response =
          await getOccupations();

        const occupations =
          Array.isArray(response)
            ? response
            : response?.occupations || [];

        setOccupationOptions(
          occupations
        );

      } catch (error) {

        console.error(
          "WORKFOLD occupations:",
          error
        );

        setOccupationOptions([]);

      } finally {

        setOccupationLoading(
          false
        );

      }

    }

    loadOccupations();

  }, []);


  async function simulate() {

    if (!selectedOccupation) {
      return;
    }

    setLoading(true);

    try {

      const response =
        await redesignWorkforce({
          occupation:
            selectedOccupation,

          aiLevel:
            aiLevel / 100,
        });

      setData(
        response
      );

    } catch (error) {

      console.error(
        "WORKFOLD:",
        error
      );

      setData(null);

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    if (selectedOccupation) {
      simulate();
    } else {
      setData(null);
    }

  }, [selectedOccupation]);


  const allocation =
    extractAllocation(
      data
    );


  const visibleOccupations =
    occupationOptions.filter(
      (item) =>
        typeof item === "string" &&
        item
          .toLowerCase()
          .includes(
            occupationSearch
              .trim()
              .toLowerCase()
          )
    );


  return (
    <section className="page-section slide">

      <OccupationSelector
        occupationOptions={
          visibleOccupations
        }
        occupationSearch={
          occupationSearch
        }
        setOccupationSearch={
          setOccupationSearch
        }
        selectedOccupation={
          selectedOccupation
        }
        setSelectedOccupation={
          setSelectedOccupation
        }
        occupationLoading={
          occupationLoading
        }
      />


      <SectionHeader
        number="03"
        eyebrow="WORKFOLD"
        title={
          <>
            What if we
            <br />
            redesign the work?
          </>
        }
        description="Change the AI adoption scenario and FORGE recalculates the Human–AI work split."
      />


      {!selectedOccupation ? (

        <EmptyState
          text="Select an occupation to run the workforce simulation."
        />

      ) : (

        <div className="simulator">

          <div className="simulator-header">

            <div>

              <h2>
                Future Workforce Simulator
              </h2>

              <small>
                {selectedOccupation}
              </small>

            </div>

            <span>
              COUNTERFACTUAL · LIVE
            </span>

          </div>


          <div className="simulator-control">

            <input
              type="range"
              min="0"
              max="100"
              value={aiLevel}
              onChange={(event) =>
                setAiLevel(
                  Number(
                    event.target.value
                  )
                )
              }
              onMouseUp={
                simulate
              }
              onTouchEnd={
                simulate
              }
            />


            <strong>
              {aiLevel}%
            </strong>

          </div>


          <div className="simulator-metrics">

            <SimulatorMetric
              label="HUMAN WORK"
              value={
                loading
                  ? "…"
                  : formatBackendPercent(
                      allocation.human
                    )
              }
              text="Backend result"
            />


            <SimulatorMetric
              label="HYBRID WORK"
              value={
                loading
                  ? "…"
                  : formatBackendPercent(
                      allocation.hybrid
                    )
              }
              text="Backend result"
            />


            <SimulatorMetric
              label="AI WORK"
              value={
                loading
                  ? "…"
                  : formatBackendPercent(
                      allocation.ai
                    )
              }
              text="Backend result"
            />


            <SimulatorMetric
              label="AI ADOPTION"
              value={
                formatBackendPercent(
                  allocation.adoption
                )
              }
              text="Scenario result"
            />

          </div>


          <div className="work-split">

            <div className="split-header">

              <strong>
                Resulting Human–AI work split
              </strong>

              <span>
                MODEL RESULT
              </span>

            </div>


            <div className="split-bar">

              {safeVisualPercent(allocation.human) > 0 && (
                <div
                  className="split-human"
                  style={{
                    width:
                      `${safeVisualPercent(
                        allocation.human
                      )}%`,
                  }}
                >
                  {safeVisualPercent(allocation.human) >= 8 && (
                    <span>
                      HUMAN
                    </span>
                  )}
                </div>
              )}


              {safeVisualPercent(allocation.hybrid) > 0 && (
                <div
                  className="split-hybrid"
                  style={{
                    width:
                      `${safeVisualPercent(
                        allocation.hybrid
                      )}%`,
                  }}
                >
                  {safeVisualPercent(allocation.hybrid) >= 8 && (
                    <span>
                      HYBRID
                    </span>
                  )}
                </div>
              )}


              {safeVisualPercent(allocation.ai) > 0 && (
                <div
                  className="split-ai"
                  style={{
                    width:
                      `${safeVisualPercent(
                        allocation.ai
                      )}%`,
                  }}
                >
                  {safeVisualPercent(allocation.ai) >= 8 && (
                    <span>
                      AI
                    </span>
                  )}
                </div>
              )}

            </div>

            <div className="split-legend">

              <span>
                <i className="legend-human" />
                HUMAN {formatBackendPercent(allocation.human)}
              </span>

              <span>
                <i className="legend-hybrid" />
                HYBRID {formatBackendPercent(allocation.hybrid)}
              </span>

              <span>
                <i className="legend-ai" />
                AI {formatBackendPercent(allocation.ai)}
              </span>

            </div>

          </div>

        </div>

      )}

    </section>
  );
}


/* =========================================================
   LATTICE
========================================================= */

class LatticeErrorBoundary extends Component {
  constructor(props) {
    super(props);

    this.state = {
      hasError: false,
      message: "",
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      message:
        error?.message ||
        "LATTICE encountered an unexpected rendering error.",
    };
  }

  componentDidCatch(error, errorInfo) {
    console.error("LATTICE render error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <section className="page-section slide">
          <div className="api-error" role="alert">
            <strong>LATTICE could not render this view.</strong>
            <span>
              The rest of FORGE is still available. Reloading the
              LATTICE page will retry the module safely.
            </span>
            <button
              type="button"
              className="light-button"
              onClick={() =>
                this.setState({
                  hasError: false,
                  message: "",
                })
              }
            >
              Retry LATTICE
            </button>
          </div>
        </section>
      );
    }

    return this.props.children;
  }
}


function LatticePage({
  selectedOccupation,
  setSelectedOccupation,
}) {
  const [occupationOptions, setOccupationOptions] = useState([]);
  const [occupationSearch, setOccupationSearch] = useState("");
  const [data, setData] = useState(null);
  const [selectedCapability, setSelectedCapability] = useState("");
  const [loading, setLoading] = useState(false);
  const [occupationLoading, setOccupationLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [practiceOpen, setPracticeOpen] = useState(false);
  const [rubricOpen, setRubricOpen] = useState(false);
  const [submission, setSubmission] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [submissionError, setSubmissionError] = useState("");
  const [attemptNumber, setAttemptNumber] = useState(1);
  const [attemptStartedAt, setAttemptStartedAt] = useState(null);

  // Prevent an older async generation request from overwriting the
  // practice context of a newly selected occupation.
  const loadRequestRef = useRef(0);

  useEffect(() => {
    let cancelled = false;

    async function loadOccupations() {
      setOccupationLoading(true);

      try {
        const response = await getOccupations({ limit: 1000 });
        const occupations = Array.isArray(response)
          ? response
          : Array.isArray(response?.occupations)
            ? response.occupations
            : [];

        if (!cancelled) {
          setOccupationOptions(
            occupations.filter(
              (item) => typeof item === "string" && item.trim()
            )
          );
        }
      } catch (error) {
        console.error("LATTICE occupations:", error);

        if (!cancelled) {
          setOccupationOptions([]);
          setLoadError(
            error?.response?.data?.detail ||
              "Unable to load occupations from the backend."
          );
        }
      } finally {
        if (!cancelled) setOccupationLoading(false);
      }
    }

    loadOccupations();
    return () => { cancelled = true; };
  }, []);

  async function loadLab() {
    const requestId = ++loadRequestRef.current;
    const occupationAtStart = selectedOccupation;

    if (!selectedOccupation) {
      setData(null);
      setSelectedCapability("");
      setLoadError("");
      return false;
    }

    setLoading(true);
    setLoadError("");
    setSubmission("");
    setSubmissionResult(null);
    setSubmissionError("");
    setAttemptNumber(1);
    setAttemptStartedAt(null);
    setData(null);
    setSelectedCapability("");
    setPracticeOpen(false);
    setRubricOpen(false);

    try {
      const analysis = await getCompleteAnalysis({
        occupation: occupationAtStart,
        baselineAi: 0,
        futureAi: 0.52,
      });

      if (requestId !== loadRequestRef.current) return false;

      let riskCapabilities = extractRiskCapabilities(analysis);
      if (!riskCapabilities.length) {
        riskCapabilities = extractRiskCapabilitiesDeeply(analysis);
      }

      const capability =
        riskCapabilities?.[0]?.name ||
        extractFirstRealCapabilityName(analysis);

      if (!capability) {
        throw new Error(
          "FORGE could not identify a real target capability for LATTICE."
        );
      }

      setSelectedCapability(capability);

      const generated = await generateLatticePractice({
        occupation: occupationAtStart,
        capability,
      });

      if (requestId !== loadRequestRef.current) return false;

      if (!generated || typeof generated !== "object") {
        throw new Error("LATTICE returned an empty response.");
      }

      if (generated.status !== "success") {
        throw new Error(
          generated.detail || "LATTICE generation did not return success."
        );
      }

      const generatedOccupation =
        generated?.occupation ||
        generated?.source_plan?.occupation ||
        occupationAtStart;

      if (
        String(generatedOccupation).trim().toLowerCase() !==
        String(occupationAtStart).trim().toLowerCase()
      ) {
        throw new Error(
          "LATTICE returned practice context for a different occupation. Please regenerate the practice."
        );
      }

      setData(generated);

      const generatedPractice = extractLatticePracticeSet(generated);
      if (!hasLatticePracticeContent(generatedPractice)) {
        setLoadError(
          "LATTICE connected successfully, but the generated practice format was not recognized."
        );
        return false;
      }

      return true;
    } catch (error) {
      console.error("LATTICE generation:", error);
      setData(null);

      const status = error?.response?.status;
      const backendMessage = error?.response?.data?.detail;

      setLoadError(
        backendMessage ||
          (status
            ? `LATTICE backend returned HTTP ${status}.`
            : error?.message || "LATTICE could not generate the practice set.")
      );
      return false;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (selectedOccupation) {
      loadLab();
    } else {
      setData(null);
      setSelectedCapability("");
      setLoadError("");
      setPracticeOpen(false);
      setRubricOpen(false);
      setSubmission("");
      setSubmissionResult(null);
      setSubmissionError("");
    }
  }, [selectedOccupation]);

  const practiceSet = useMemo(
    () => extractLatticePracticeSet(data),
    [data]
  );

  const task = practiceSet.taskInstruction || "";
  const rubric = Array.isArray(practiceSet.rubric) ? practiceSet.rubric : [];
  const sourceTask =
    data?.generation?.source_context?.source_task ||
    data?.source_plan?.source_work_context?.task ||
    "";

  /*
   * Backend practice context
   *
   * IMPORTANT: the generated response is authoritative. Do not pair a
   * task_id from one generation with the currently selected occupation or
   * capability, because selection state can change while an async request
   * is in flight.
   */
  const backendOccupation =
    data?.occupation ||
    data?.source_plan?.occupation ||
    selectedOccupation ||
    "";

  const backendCapability =
    data?.target_capability ||
    data?.source_plan?.capability?.name ||
    data?.source_plan?.capability?.["Capability Name"] ||
    data?.generation?.source_context?.capability ||
    selectedCapability ||
    "";

  const taskId =
    data?.source_plan?.source_work_context?.task_id ||
    data?.source_plan?.source_work_context?.["Task ID"] ||
    data?.generation?.source_context?.task_id ||
    data?.generation?.source_context?.source_work_context?.task_id ||
    "";

  const backendPracticeId =
    data?.source_plan?.practice_id ||
    data?.source_plan?.id ||
    data?.generation?.source_context?.practice_id ||
    data?.generation?.source_context?.source_plan?.practice_id ||
    "";

  const practiceId =
    backendPracticeId ||
    (taskId && backendOccupation && backendCapability
      ? `lattice:${backendOccupation}:${backendCapability}:${taskId}`
      : "");

  const visibleOccupations = Array.isArray(occupationOptions)
    ? occupationOptions.filter(
        (item) =>
          typeof item === "string" &&
          item.toLowerCase().includes(occupationSearch.trim().toLowerCase())
      )
    : [];

  async function handleStartPractice() {
    if (loading) return;

    if (!hasLatticePracticeContent(practiceSet)) {
      const success = await loadLab();
      if (!success) return;
    }

    setRubricOpen(false);
    setPracticeOpen(true);
    setSubmissionError("");
    if (!attemptStartedAt) setAttemptStartedAt(Date.now());
  }

  async function handleViewRubric() {
    if (loading) return;

    if (!hasLatticePracticeContent(practiceSet)) {
      const success = await loadLab();
      if (!success) return;
    }

    setPracticeOpen(false);
    setRubricOpen(true);
  }

  function startAnotherAttempt() {
    setAttemptNumber((value) => value + 1);
    setSubmission("");
    setSubmissionResult(null);
    setSubmissionError("");
    setAttemptStartedAt(Date.now());
    setPracticeOpen(true);
  }

  async function handleSubmitEvidence() {
    if (submitting || !submission.trim()) return;

    if (!taskId || !backendCapability || !backendOccupation) {
      setSubmissionError(
        "This practice is missing its real backend task context. Regenerate the practice before submitting."
      );
      return;
    }

    setSubmitting(true);
    setSubmissionError("");

    const elapsedSeconds = attemptStartedAt
      ? Math.max(1, Math.round((Date.now() - attemptStartedAt) / 1000))
      : null;

    try {
      const apiBase =
        import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

      const response = await fetch(
        `${apiBase}/api/lattice/evidence/submit`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            practice_id: practiceId,
            occupation: backendOccupation,
            capability: backendCapability,
            task_id: String(taskId),
            submission: submission.trim(),
            observable_evidence: Array.isArray(
              practiceSet.observableEvidence
            )
              ? practiceSet.observableEvidence
              : [],
            time_seconds: elapsedSeconds,
            attempts: attemptNumber,
            mode: "DIGITAL",
          }),
        }
      );

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          result?.detail ||
            `Evidence submission failed with HTTP ${response.status}.`
        );
      }

      setSubmissionResult(result);
      setAttemptStartedAt(null);
    } catch (error) {
      console.error("LATTICE evidence submission:", error);
      setSubmissionError(
        error?.message || "The evidence could not be submitted."
      );
    } finally {
      setSubmitting(false);
    }
  }

  // Backend may wrap the server-generated evaluation under `evidence`,
  // `evaluation`, or `result`. Prefer the evaluated evidence object first.
  // The learner never supplies rubric scores; these values come from the backend.
  const evaluation =
    submissionResult?.evidence?.evaluation ||
    submissionResult?.evidence ||
    submissionResult?.evaluation ||
    submissionResult?.result ||
    submissionResult ||
    null;

  const evaluationStatus =
    evaluation?.status ||
    evaluation?.evaluation?.status ||
    evaluation?.evaluation_result?.status ||
    "";

  const evaluationScore =
    evaluation?.score ??
    evaluation?.evaluation?.score ??
    evaluation?.evaluation_result?.score ??
    null;

  return (
    <section className="page-section slide">
      <OccupationSelector
        occupationOptions={visibleOccupations}
        occupationSearch={occupationSearch}
        setOccupationSearch={setOccupationSearch}
        selectedOccupation={selectedOccupation}
        setSelectedOccupation={setSelectedOccupation}
        occupationLoading={occupationLoading}
      />

      {loadError && (
        <div className="api-error" role="status">
          {loadError}
        </div>
      )}

      <SectionHeader
        number="04"
        eyebrow="LATTICE"
        title={
          <>
            Automate the work.
            <br />
            Preserve the learning.
          </>
        }
        description="LATTICE turns capability risk into targeted apprenticeship practice and capability verification."
      />

      {!selectedOccupation ? (
        <EmptyState text="Select an occupation to open the capability lab." />
      ) : (
        <div className="lattice-grid">
          <div className="lab-card">
            <div className="lab-card-header">
              <div className="lab-icon">
                <Sparkles size={18} />
              </div>
              <div>
                <strong>Capability Lab</strong>
                <small>{selectedOccupation}</small>
              </div>
              <span>
                {loading ? "GENERATING" : task ? "READY TO PRACTICE" : "READY"}
              </span>
            </div>

            <div className="generated-task">
              <small>GROQ-GENERATED APPRENTICESHIP</small>
              <h3>
                {loading
                  ? "Generating a new capability practice..."
                  : practiceSet.title || "No generated practice available yet."}
              </h3>

              {!loading && selectedCapability && (
                <p
                  style={{
                    marginBottom: "10px",
                    fontSize: "11px",
                    color: "#3565d4",
                    fontWeight: 700,
                    letterSpacing: "0.05em",
                  }}
                >
                  TARGET CAPABILITY · {selectedCapability}
                </p>
              )}

              {!loading && practiceSet.scenario && <p>{practiceSet.scenario}</p>}
            </div>

            {sourceTask && (
              <div
                className="generated-task"
                style={{ marginTop: "12px", background: "#f8f8f5" }}
              >
                <small>REAL SOURCE WORK</small>
                <p
                  style={{
                    margin: 0,
                    fontSize: "12px",
                    lineHeight: "1.7",
                    color: "#555b57",
                  }}
                >
                  {sourceTask}
                </p>
                <p
                  style={{
                    margin: "10px 0 0",
                    fontSize: "10px",
                    color: "#777b77",
                  }}
                >
                  Grounding context from the FORGE work graph. This is not itself
                  learner evidence.
                </p>
              </div>
            )}

            <div className="lab-buttons">
              <button
                type="button"
                className="black-button"
                disabled={loading}
                onClick={handleStartPractice}
              >
                {practiceOpen ? "Close Practice" : "Start Practice"}
                <ArrowRight size={14} />
              </button>

              <button
                type="button"
                className="light-button"
                disabled={loading}
                onClick={handleViewRubric}
              >
                {rubricOpen ? "Close Rubric" : "View Rubric"}
              </button>

              <button
                type="button"
                className="light-button"
                disabled={loading}
                onClick={() => loadLab()}
              >
                {loading ? "Generating..." : "Regenerate"}
              </button>
            </div>

            {practiceOpen && (
              <div className="generated-task" style={{ marginTop: "18px" }}>
                <small>PRACTICE SET</small>
                <h3>{practiceSet.title || "Capability practice"}</h3>

                <div
                  style={{
                    display: "grid",
                    gap: "16px",
                    marginTop: "16px",
                  }}
                >
                  <LatticePracticeSection label="SITUATION" value={practiceSet.scenario} />
                  <LatticePracticeSection label="TASK TO PERFORM" value={practiceSet.taskInstruction} />
                  <LatticePracticeList label="PROVIDED INFORMATION" items={practiceSet.providedInformation} />
                  <LatticePracticeList label="CONSTRAINTS" items={practiceSet.constraints} />
                  <LatticePracticeSection label="EXPECTED OUTPUT" value={practiceSet.expectedOutput} />
                  <LatticePracticeList label="REASONING FOCUS" items={practiceSet.reasoningFocus} />
                  <LatticePracticeList label="OBSERVABLE EVIDENCE" items={practiceSet.observableEvidence} />
                </div>

                <p
                  style={{
                    marginTop: "18px",
                    paddingTop: "14px",
                    borderTop: "1px solid #d6d8d3",
                    fontSize: "11px",
                  }}
                >
                  Generated practice is only the work prompt. Your capability is
                  evaluated only after you submit observable work.
                </p>
              </div>
            )}

            {rubricOpen && (
              <div className="generated-task" style={{ marginTop: "18px" }}>
                <small>CAPABILITY VERIFICATION RUBRIC</small>
                <h3>{practiceSet.title || "LATTICE rubric"}</h3>

                {rubric.length ? (
                  <div style={{ display: "grid", gap: "10px", marginTop: "16px" }}>
                    {rubric.map((item, index) => (
                      <div
                        key={item.dimension || index}
                        style={{
                          border: "1px solid #d6d8d3",
                          background: "#ffffff",
                          padding: "14px",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            gap: "12px",
                            alignItems: "center",
                            marginBottom: "8px",
                          }}
                        >
                          <strong
                            style={{
                              fontSize: "12px",
                              textTransform: "uppercase",
                              letterSpacing: "0.06em",
                            }}
                          >
                            {item.dimension || `Dimension ${index + 1}`}
                          </strong>
                          <span
                            style={{
                              fontSize: "10px",
                              color: "#3565d4",
                              fontWeight: 800,
                              letterSpacing: "0.04em",
                              textTransform: "uppercase",
                            }}
                          >
                            Max {item.maxScore ?? 5} points
                          </span>
                        </div>
                        <p style={{ margin: "0 0 7px", fontSize: "12px", lineHeight: "1.6" }}>
                          {item.criterion || "No criterion returned."}
                        </p>
                        <p style={{ margin: 0, color: "#555b57", fontSize: "12px", lineHeight: "1.6" }}>
                          <strong>Good performance:</strong>{" "}
                          {item.goodPerformance || "Not specified."}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No rubric has been generated yet.</p>
                )}

                <p style={{ marginTop: "16px", fontSize: "11px" }}>
                  The rubric defines observable capability evidence. It does not
                  pre-score the learner.
                </p>
              </div>
            )}

            {practiceOpen && (
              <div className="lattice-workspace">
                <div className="lattice-workspace-head">
                  <div>
                    <div className="lattice-workspace-kicker">
                      <ShieldCheck size={13} />
                      Evidence Workspace
                    </div>
                    <h3>Perform the work. Then submit your evidence.</h3>
                  </div>
                  <div className="lattice-evidence-badge">
                    <span
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        background: "#7dd9a5",
                      }}
                    />
                    ATTEMPT {attemptNumber}
                  </div>
                </div>

                <div className="lattice-workspace-body">
                  <div className="lattice-brief">
                    <div className="lattice-panel-label">WORK BRIEF</div>
                    <h4 className="lattice-brief-title">
                      {practiceSet.taskInstruction || "Complete the assigned practice task."}
                    </h4>

                    <div className="lattice-mini-card">
                      <div className="lattice-panel-label">EXPECTED OUTPUT</div>
                      <p>{practiceSet.expectedOutput || "Produce a defensible work outcome."}</p>
                    </div>

                    {Array.isArray(practiceSet.constraints) && practiceSet.constraints.length > 0 && (
                      <div className="lattice-mini-card">
                        <div className="lattice-panel-label">CONSTRAINTS</div>
                        <div className="lattice-chip-row">
                          {practiceSet.constraints.map((item, index) => (
                            <span className="lattice-chip" key={`${item}-${index}`}>
                              {item}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="lattice-trust-note">
                      <ShieldCheck size={14} />
                      Scores are generated by the backend evaluator from submitted
                      evidence — never entered by the learner.
                    </div>
                  </div>

                  <div className="lattice-submit">
                    <div className="lattice-submit-intro">
                      <div className="lattice-submit-icon">
                        <FileText size={18} />
                      </div>
                      <div>
                        <strong>Your work</strong>
                        <span>
                          Show the analysis, decisions, calculations, checks, and
                          conclusion you actually produced.
                        </span>
                      </div>
                    </div>

                    <textarea
                      className="lattice-textarea"
                      value={submission}
                      onChange={(event) => setSubmission(event.target.value)}
                      placeholder="Write or paste your completed work here…\n\nTip: include your reasoning and any checks you performed, not just the final answer."
                      disabled={submitting || Boolean(submissionResult)}
                    />

                    <div className="lattice-submit-meta">
                      <span>{submission.length.toLocaleString()} characters</span>
                      <span>
                        {attemptStartedAt ? (
                          <><Clock3 size={10} style={{ verticalAlign: "-1px" }} /> attempt in progress</>
                        ) : "Ready when you are"}
                      </span>
                    </div>

                    {submissionError && (
                      <div
                        className="api-error"
                        role="alert"
                        style={{ marginTop: "13px" }}
                      >
                        <AlertCircle size={14} style={{ verticalAlign: "-2px", marginRight: "6px" }} />
                        {submissionError}
                      </div>
                    )}

                    <div className="lattice-submit-actions">
                      {!submissionResult ? (
                        <button
                          type="button"
                          className="lattice-submit-button"
                          disabled={submitting || !submission.trim()}
                          onClick={handleSubmitEvidence}
                        >
                          {submitting ? (
                            <><Loader2 size={15} className="lattice-spin" /> Evaluating…</>
                          ) : (
                            <><Send size={15} /> Submit Evidence</>
                          )}
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="lattice-submit-button"
                          onClick={startAnotherAttempt}
                        >
                          <RotateCcw size={15} /> Try Another Attempt
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {submissionResult && (
                  <div
                    className={`lattice-result ${
                      evaluationStatus === "DEMONSTRATED" ? "success" : "warn"
                    }`}
                  >
                    <div className="lattice-result-head">
                      {evaluationStatus === "DEMONSTRATED" ? (
                        <CheckCircle2 size={19} />
                      ) : (
                        <AlertCircle size={19} />
                      )}
                      <strong>
                        {evaluationStatus || "Evidence received"}
                      </strong>
                      {evaluationScore !== null && evaluationScore !== undefined && (
                        <span className="lattice-result-score">
                          {Number(evaluationScore).toFixed(1)} / 5
                        </span>
                      )}
                    </div>
                    {Array.isArray(evaluation?.rubric) && evaluation.rubric.length > 0 && (
                      <div
                        style={{
                          marginTop: "12px",
                          display: "grid",
                          gap: "7px",
                        }}
                      >
                        {evaluation.rubric.map((item, index) => (
                          <div
                            key={item.dimension || index}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              gap: "12px",
                              padding: "8px 10px",
                              borderRadius: "8px",
                              background: "#ffffff",
                              border: "1px solid #e1e5e1",
                              fontSize: "10px",
                            }}
                          >
                            <span>{item.dimension || `Dimension ${index + 1}`}</span>
                            <strong>{item.score ?? "—"} / 5</strong>
                          </div>
                        ))}
                      </div>
                    )}

                    <p>
                      {evaluationStatus === "INSUFFICIENT_EVIDENCE"
                        ? "The attempt was recorded, but the available evidence was not sufficient for a validated capability score. No score was invented."
                        : evaluationStatus === "PARTIAL"
                          ? "The backend found partial evidence of the target capability. Use another practice attempt to strengthen the evidence."
                          : evaluationStatus === "DEMONSTRATED"
                            ? "The backend validated observable evidence for this capability."
                            : "The learner attempt has been received by the evidence pipeline."}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

function LatticePracticeSection({
  label,
  value,
}) {
  if (!value) {
    return null;
  }

  return (
    <div>
      <small
        style={{
          display: "block",
          marginBottom: "6px",
          color: "#3565d4",
          fontSize: "9px",
          fontWeight: 700,
          letterSpacing: "0.12em",
        }}
      >
        {label}
      </small>

      <p
        style={{
          margin: 0,
          color: "#555b57",
          fontSize: "12px",
          lineHeight: "1.7",
        }}
      >
        {value}
      </p>
    </div>
  );
}


function LatticePracticeList({
  label,
  items,
}) {
  const values =
    Array.isArray(items)
      ? items.filter(
          (item) =>
            typeof item === "string" &&
            item.trim()
        )
      : [];

  if (!values.length) {
    return null;
  }

  return (
    <div>
      <small
        style={{
          display: "block",
          marginBottom: "6px",
          color: "#3565d4",
          fontSize: "9px",
          fontWeight: 700,
          letterSpacing: "0.12em",
        }}
      >
        {label}
      </small>

      <ul
        style={{
          margin: 0,
          paddingLeft: "18px",
          color: "#555b57",
          fontSize: "12px",
          lineHeight: "1.7",
        }}
      >
        {values.map(
          (item, index) => (
            <li key={index}>
              {item}
            </li>
          )
        )}
      </ul>
    </div>
  );
}


/* =========================================================
   INTELLIGENCE
========================================================= */

/* =========================================================
   COMMON COMPONENTS
========================================================= */

function SectionHeader({
  number,
  eyebrow,
  title,
  description,
}) {
  return (
    <div className="section-heading">

      <div>

        <div className="eyebrow">
          {number &&
            `${number} / `}
          {eyebrow}
        </div>


        <h1>
          {title}
        </h1>

      </div>


      {description && (
        <p>
          {description}
        </p>
      )}

    </div>
  );
}


function StatItem({
  value,
  label,
}) {
  return (
    <div className="stat-item">

      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>

    </div>
  );
}


function ProcessBox({
  title,
  subtitle,
}) {
  return (
    <div className="process-box">

      <strong>
        {title}
      </strong>

      <small>
        {subtitle}
      </small>

    </div>
  );
}


function ProcessArrow() {
  return (
    <div className="process-arrow">
      →
    </div>
  );
}



function TraceRow({
  occupation,
  task,
  capability,
}) {
  return (
    <div className="trace-row">

      <div>

        <small>
          OCCUPATION
        </small>

        <strong>
          {occupation}
        </strong>

      </div>


      <ArrowRight size={17} />


      <div>

        <small>
          TASK
        </small>

        <strong>
          {task || "—"}
        </strong>

      </div>


      <ArrowRight size={17} />


      <div>

        <small>
          CAPABILITY
        </small>

        <strong>
          {capability || "—"}
        </strong>

      </div>

    </div>
  );
}


function DataNumber({
  value,
  label,
}) {
  return (
    <div className="data-number">

      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>

    </div>
  );
}


function RiskRow({
  icon,
  title,
  text,
  value,
}) {
  return (
    <div className="risk-row">

      <div className="risk-icon">
        {icon}
      </div>


      <div>

        <strong>
          {title}
        </strong>

        <p>
          {text}
        </p>

      </div>


      <span>
        {value}
      </span>

    </div>
  );
}


function SimulatorMetric({
  label,
  value,
  text,
}) {
  return (
    <div className="simulator-metric">

      <small>
        {label}
      </small>

      <strong>
        {value}
      </strong>

      <span>
        {text}
      </span>

    </div>
  );
}


function EmptyState({
  text,
}) {
  return (
    <div className="empty-state">

      <span className="status-dot-blue" />

      {text}

    </div>
  );
}


/* =========================================================
   INTELLIGENCE COMPONENTS
========================================================= */

function IntelligenceNode({
  icon,
  number,
  title,
  text,
}) {
  return (
    <div className="intelligence-node">

      <div className="intelligence-icon">
        {icon}
      </div>

      <small>
        {number}
      </small>

      <strong>
        {title}
      </strong>

      <p>
        {text}
      </p>

    </div>
  );
}


function FlowConnector() {
  return (
    <div className="flow-connector">
      <ArrowRight size={15} />
    </div>
  );
}


function ComponentRow({
  title,
  status,
}) {
  return (
    <div className="component-row">

      <span>
        {title}
      </span>

      <strong>
        {status}
      </strong>

    </div>
  );
}


/* =========================================================
   FOOTER
========================================================= */

function Footer() {
  return (
    <footer className="footer" id="about">

      <div>

        <strong>
          FORGE
        </strong>

        <span>
          Future-Oriented Workforce
          Reconfiguration & Growth Engine
        </span>

      </div>


      <span>
        WORK · AI · CAPABILITY · FUTURE
      </span>

    </footer>
  );
}


/* =========================================================
   DATA HELPERS
========================================================= */

function findArray(
  object,
  paths
) {
  if (!object) {
    return [];
  }


  for (const path of paths) {

    const value =
      path
        .split(".")
        .reduce(
          (
            current,
            key
          ) =>
            current &&
            current[key] !== undefined
              ? current[key]
              : undefined,
          object
        );


    if (Array.isArray(value)) {
      return value;
    }
  }


  return [];
}


function extractNumber(
  object,
  paths
) {
  if (!object) {
    return null;
  }


  for (const path of paths) {

    const value =
      path
        .split(".")
        .reduce(
          (
            current,
            key
          ) =>
            current &&
            current[key] !== undefined
              ? current[key]
              : undefined,
          object
        );


    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return value;
    }
  }


  return null;
}


function extractLabel(
  item
) {
  if (
    typeof item === "string"
  ) {
    return item;
  }


  if (
    !item ||
    typeof item !== "object"
  ) {
    return "";
  }


  return (
    item.name ||
    item.title ||
    item.label ||
    item.task ||
    item.skill ||
    item.capability ||
    item["Task"] ||
    item["Capability Name"] ||
    item["DWA Element Name"] ||
    item.description ||
    ""
  );
}


/* =========================================================
   WORKTRACE COUNTS
========================================================= */

function getTaskCount(
  data,
  tasks
) {
  const value =
    extractNumber(
      data,
      [
        "modules.worktrace.task_count",
        "worktrace.task_count",
        "task_count",
      ]
    );


  if (value !== null) {
    return value;
  }


  return tasks.length || "—";
}


function getCapabilityCount(
  data,
  capabilities
) {
  const value =
    extractNumber(
      data,
      [
        "modules.worktrace.capability_count",
        "worktrace.capability_count",
        "capability_count",
      ]
    );


  if (value !== null) {
    return value;
  }


  return capabilities.length || "—";
}


/* =========================================================
   SKILL SHADOW CAPABILITIES
========================================================= */

function extractRiskCapabilities(
  data
) {
  const array =
    findArray(
      data,
      [
        "modules.skill_shadow.future.top_risk_capabilities",
        "skill_shadow.future.top_risk_capabilities",
        "future.top_risk_capabilities",
      ]
    );


  return array
    .map(
      (item) => {

        if (
          !item ||
          typeof item !== "object"
        ) {
          return null;
        }


        const name =
          item.capability ||
          item["Capability Name"] ||
          item.name ||
          "";


        const exposureLost =
          typeof item.exposure_lost ===
          "number"
            ? item.exposure_lost
            : null;


        const postExposure =
          typeof item.post_ai_exposure ===
          "number"
            ? item.post_ai_exposure
            : null;


        const preExposure =
          typeof item.pre_ai_exposure ===
          "number"
            ? item.pre_ai_exposure
            : null;


        if (!name) {
          return null;
        }


        return {
          key:
            item.capability_key ||
            item.capability_id ||
            name,

          name,

          exposureLost,

          postExposure,

          preExposure,

          taskCount:
            item.task_count,

          marketJobCount:
            item.market_job_count,

          futureDemandSignal:
            item.future_demand_signal,
        };
      }
    )
    .filter(Boolean);
}



function extractRiskCapabilitiesDeeply(data) {
  const results = [];
  const seen = new Set();

  function walk(value, depth = 0) {
    if (!value || depth > 8) return;

    if (Array.isArray(value)) {
      for (const item of value) {
        walk(item, depth + 1);
      }
      return;
    }

    if (typeof value !== "object") return;

    const name =
      value.capability ||
      value["Capability Name"] ||
      value.capability_name ||
      "";

    if (
      typeof name === "string" &&
      name.trim() &&
      !seen.has(name.trim())
    ) {
      seen.add(name.trim());

      results.push({
        key:
          value.capability_key ||
          value.capability_id ||
          name.trim(),
        name: name.trim(),
        exposureLost:
          typeof value.exposure_lost === "number"
            ? value.exposure_lost
            : null,
        postExposure:
          typeof value.post_ai_exposure === "number"
            ? value.post_ai_exposure
            : null,
        preExposure:
          typeof value.pre_ai_exposure === "number"
            ? value.pre_ai_exposure
            : null,
        taskCount: value.task_count,
        marketJobCount: value.market_job_count,
        futureDemandSignal:
          value.future_demand_signal,
      });
    }

    for (const [key, child] of Object.entries(value)) {
      if (
        key === "practice_set" ||
        key === "rubric"
      ) {
        continue;
      }

      walk(child, depth + 1);
    }
  }

  walk(data);

  return results;
}


function extractFirstRealCapabilityName(data) {
  const candidates =
    extractRiskCapabilitiesDeeply(data);

  return candidates.length
    ? candidates[0].name
    : "";
}


/* =========================================================
   LATTICE TASK
========================================================= */

function extractFirstTask(
  data
) {
  if (
    !data ||
    typeof data !== "object"
  ) {
    return "";
  }

  /*
   * First check the known LATTICE locations.
   * This keeps the normal backend path explicit.
   */
  const directCandidates = [
    data?.modules?.lattice?.tasks,
    data?.modules?.lattice?.cases,
    data?.modules?.lattice?.generated_tasks,
    data?.modules?.lattice?.practice_tasks,
    data?.modules?.lattice?.generated_task,
    data?.modules?.lattice?.practice_task,

    data?.lattice?.tasks,
    data?.lattice?.cases,
    data?.lattice?.generated_tasks,
    data?.lattice?.practice_tasks,
    data?.lattice?.generated_task,
    data?.lattice?.practice_task,

    data?.cases,
    data?.preservation?.tasks,
    data?.preservation?.cases,
  ];

  for (
    const candidate of directCandidates
  ) {
    const label =
      extractTaskLabelSafely(
        candidate
      );

    if (label) {
      return label;
    }
  }

  /*
   * If the backend nests the generated exercise
   * differently, walk the response without throwing.
   */
  return findTaskLabelDeeply(
    data
  );
}


function extractTaskLabelSafely(
  value
) {
  if (
    typeof value === "string"
  ) {
    return value.trim();
  }

  if (
    Array.isArray(value)
  ) {
    for (
      const item of value
    ) {
      const label =
        extractTaskLabelSafely(
          item
        );

      if (label) {
        return label;
      }
    }

    return "";
  }

  if (
    !value ||
    typeof value !== "object"
  ) {
    return "";
  }

  const fields = [
    "title",
    "task",
    "task_title",
    "task_instruction",
    "instruction",
    "scenario",
    "description",
    "name",
    "label",
  ];

  for (
    const field of fields
  ) {
    const candidate =
      value[field];

    if (
      typeof candidate === "string" &&
      candidate.trim()
    ) {
      return candidate.trim();
    }
  }

  return "";
}


function findTaskLabelDeeply(
  value,
  depth = 0
) {
  /*
   * Limit recursion so an unexpected/cyclic backend
   * object cannot lock up rendering.
   */
  if (
    depth > 6 ||
    !value ||
    typeof value !== "object"
  ) {
    return "";
  }

  if (
    Array.isArray(value)
  ) {
    for (
      const item of value
    ) {
      const label =
        findTaskLabelDeeply(
          item,
          depth + 1
        );

      if (label) {
        return label;
      }
    }

    return "";
  }

  const preferredKeys = [
    "generated_task",
    "practice_task",
    "task",
    "task_details",
    "exercise",
    "case",
  ];

  for (
    const key of preferredKeys
  ) {
    if (
      Object.prototype.hasOwnProperty.call(
        value,
        key
      )
    ) {
      const label =
        extractTaskLabelSafely(
          value[key]
        ) ||
        findTaskLabelDeeply(
          value[key],
          depth + 1
        );

      if (label) {
        return label;
      }
    }
  }

  for (
    const [key, child] of Object.entries(
      value
    )
  ) {
    if (
      [
        "rubric",
        "metadata",
        "worktrace",
        "skill_shadow",
        "workfold",
        "scenario",
      ].includes(key)
    ) {
      continue;
    }

    if (
      child &&
      typeof child === "object"
    ) {
      const label =
        findTaskLabelDeeply(
          child,
          depth + 1
        );

      if (label) {
        return label;
      }
    }
  }

  return "";
}


/* =========================================================
   LATTICE PRACTICE SET + RUBRIC
========================================================= */

function extractLatticePracticeSet(data) {
  const empty = {
    title: "",
    scenario: "",
    taskInstruction: "",
    providedInformation: [],
    constraints: [],
    expectedOutput: "",
    reasoningFocus: [],
    observableEvidence: [],
    rubric: [],
  };

  if (!data || typeof data !== "object") {
    return empty;
  }

  /*
   * Primary endpoint:
   * /api/lattice/generate
   *
   * {
   *   status: "success",
   *   generation: {
   *     status: "generated",
   *     practice_set: {...}
   *   }
   * }
   */
  const primary = parsePracticeCandidate(
    data?.generation?.practice_set
  );

  if (hasLatticePracticeContent(primary)) {
    return primary;
  }

  /*
   * Some clients/backends may return the generated
   * object one level deeper or as a JSON string.
   */
  const secondaryCandidates = [
    data?.generation,
    data?.generation?.practice,
    data?.practice_set,
    data?.practiceSet,
    data?.generated_practice,
    data?.generatedPractice,
    data?.lattice?.practice_set,
    data?.modules?.lattice?.practice_set,
  ];

  for (const candidate of secondaryCandidates) {
    const normalized =
      parsePracticeCandidate(candidate);

    if (hasLatticePracticeContent(normalized)) {
      return normalized;
    }
  }

  return empty;
}


function parsePracticeCandidate(value) {
  if (!value) {
    return null;
  }

  /*
   * If the backend/client returns JSON as a string,
   * parse it safely.
   */
  if (typeof value === "string") {
    const trimmed = value.trim();

    if (!trimmed) {
      return null;
    }

    try {
      return parsePracticeCandidate(
        JSON.parse(trimmed)
      );
    } catch {
      return {
        title: "",
        scenario: "",
        taskInstruction: trimmed,
        providedInformation: [],
        constraints: [],
        expectedOutput: "",
        reasoningFocus: [],
        observableEvidence: [],
        rubric: [],
      };
    }
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const normalized =
        parsePracticeCandidate(item);

      if (hasLatticePracticeContent(normalized)) {
        return normalized;
      }
    }

    return null;
  }

  if (typeof value !== "object") {
    return null;
  }

  /*
   * If this is the generation wrapper, descend into
   * practice_set / practiceSet before normalizing.
   */
  if (value.practice_set) {
    const nested =
      parsePracticeCandidate(
        value.practice_set
      );

    if (hasLatticePracticeContent(nested)) {
      return nested;
    }
  }

  if (value.practiceSet) {
    const nested =
      parsePracticeCandidate(
        value.practiceSet
      );

    if (hasLatticePracticeContent(nested)) {
      return nested;
    }
  }

  return {
    title: firstLatticeText([
      value.title,
      value.task_title,
      value.taskTitle,
      value.name,
    ]),

    scenario: firstLatticeText([
      value.scenario,
      value.situation,
    ]),

    taskInstruction: firstLatticeText([
      value.task_instruction,
      value.taskInstruction,
      value.task_to_perform,
      value.taskToPerform,
      value.instruction,
      value.task,
    ]),

    providedInformation:
      normalizeLatticeStringArray(
        value.provided_information ||
          value.providedInformation
      ),

    constraints:
      normalizeLatticeStringArray(
        value.constraints
      ),

    expectedOutput: firstLatticeText([
      value.expected_output,
      value.expectedOutput,
      value.observable_output,
      value.observableOutput,
    ]),

    reasoningFocus:
      normalizeLatticeStringArray(
        value.reasoning_focus ||
          value.reasoningFocus
      ),

    observableEvidence:
      normalizeLatticeStringArray(
        value.observable_evidence ||
          value.observableEvidence ||
          value.evidence
      ),

    rubric: normalizeLatticeRubric(
      value.rubric ||
        value.Rubric ||
        value.assessment_rubric ||
        value.assessmentRubric
    ),
  };
}


function hasLatticePracticeContent(value) {
  if (!value) {
    return false;
  }

  return Boolean(
    value.title ||
      value.scenario ||
      value.taskInstruction ||
      value.expectedOutput ||
      value.rubric?.length
  );
}


function normalizeLatticeRubric(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter(
      (item) =>
        item &&
        typeof item === "object"
    )
    .map((item, index) => ({
      dimension:
        firstLatticeText([
          item.dimension,
          item.name,
          item.title,
        ]) ||
        `Dimension ${index + 1}`,

      criterion:
        firstLatticeText([
          item.criterion,
          item.description,
        ]),

      goodPerformance:
        firstLatticeText([
          item.good_performance,
          item.goodPerformance,
          item.expected_performance,
        ]),

      maxScore:
        Number.isFinite(
          Number(item.max_score)
        )
          ? Number(item.max_score)
          : Number.isFinite(
              Number(item.maxScore)
            )
            ? Number(item.maxScore)
            : 5,
    }));
}


function normalizeLatticeStringArray(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => {
      if (typeof item === "string") {
        return item.trim();
      }

      if (
        item &&
        typeof item === "object"
      ) {
        return firstLatticeText([
          item.text,
          item.description,
          item.value,
          item.name,
          item.label,
        ]);
      }

      return "";
    })
    .filter(Boolean);
}


function firstLatticeText(values) {
  for (const value of values) {
    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value.trim();
    }
  }

  return "";
}


/* =========================================================
   WORKFOLD ALLOCATION
========================================================= */

function extractAllocation(
  data
) {

  /*
   * WORKFOLD uses the dedicated redesign
   * endpoint.
   *
   * Actual response:
   *
   * workfold
   *   ├── workforce_summary
   *   │     ├── mean_human_share_percent
   *   │     ├── mean_ai_share_percent
   *   │     ├── task_count
   *   │     └── work_model_counts
   *   │           ├── Human-led
   *   │           ├── Hybrid
   *   │           └── AI-led
   *   │
   *   └── scenario
   *         └── requested_ai_adoption_percent
   *
   * The actual Human and AI shares are taken
   * directly from the backend summary.
   *
   * Hybrid is the remaining share:
   *
   * 100 - Human share - AI share
   *
   * This avoids treating the categorical
   * work_model_counts as the percentage split.
   */

  const empty = {
    human: null,
    hybrid: null,
    ai: null,
    adoption: null,
  };


  if (
    !data ||
    typeof data !== "object"
  ) {
    return empty;
  }


  /*
   * Dedicated /redesign response.
   */

  const workfold =
    data?.workfold ||
    data?.modules?.workfold ||
    null;


  if (!workfold) {
    return empty;
  }


  const summary =
    workfold?.workforce_summary ||
    null;


  const scenario =
    workfold?.scenario ||
    null;


  if (!summary) {
    return {
      ...empty,

      adoption:
        readPercentValue(
          scenario?.requested_ai_adoption_percent
        ),
    };
  }


  /*
   * REAL WORKFOLD METRICS
   *
   * These are backend-computed mean task
   * shares, not frontend-generated values.
   */

  const humanRaw =
    toFiniteNumber(
      summary?.mean_human_share_percent
    );


  const aiRaw =
    toFiniteNumber(
      summary?.mean_ai_share_percent
    );


  const human =
    humanRaw !== null
      ? clampPercent(humanRaw)
      : null;


  const ai =
    aiRaw !== null
      ? clampPercent(aiRaw)
      : null;


  /*
   * Hybrid is the remaining work share.
   *
   * If backend provides an explicit hybrid
   * share, use it; otherwise calculate the
   * remainder from the real human + AI shares.
   */

  const explicitHybrid =
    firstFiniteNumber([
      summary?.mean_hybrid_share_percent,
      summary?.hybrid_work_percent,
      summary?.hybrid_percent,
    ]);


  const rawHybrid =
    explicitHybrid !== null
      ? explicitHybrid
      : (
          human !== null &&
          ai !== null
            ? 100 - human - ai
            : null
        );

  /*
   * Floating-point arithmetic can produce values such as
   * 0.010000000000001563 when the real remainder is zero.
   * Treat tiny residuals as zero and round to two decimals.
   */
  const hybrid =
    rawHybrid === null
      ? null
      : normalizeAllocationPercent(rawHybrid);


  /*
   * REAL SCENARIO VALUE
   */

  const adoption =
    readPercentValue(
      scenario?.requested_ai_adoption_percent
    );


  return {
    human:
      human === null
        ? null
        : normalizeAllocationPercent(human),

    hybrid,

    ai:
      ai === null
        ? null
        : normalizeAllocationPercent(ai),

    adoption:
      adoption === null
        ? null
        : normalizeAllocationPercent(adoption),
  };
}


function normalizeAllocationPercent(
  value
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return null;
  }

  const rounded =
    Math.round(value * 100) / 100;

  if (
    Math.abs(rounded) < 0.005
  ) {
    return 0;
  }

  return Math.max(
    0,
    Math.min(
      100,
      rounded
    )
  );
}


function clampPercent(
  value
) {

  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return null;
  }


  return Math.max(
    0,
    Math.min(
      100,
      value
    )
  );
}


function readPercentValue(
  value
) {

  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return null;
  }


  if (
    value >= 0 &&
    value <= 1
  ) {
    return value * 100;
  }


  return value;
}


function findObjectByKey(
  object,
  targetKey
) {
  if (
    !object ||
    typeof object !== "object"
  ) {
    return null;
  }

  if (
    Object.prototype.hasOwnProperty.call(
      object,
      targetKey
    ) &&
    object[targetKey] &&
    typeof object[targetKey] === "object"
  ) {
    return object[targetKey];
  }

  for (const value of Object.values(object)) {
    if (
      value &&
      typeof value === "object"
    ) {
      const found =
        findObjectByKey(
          value,
          targetKey
        );

      if (found) {
        return found;
      }
    }
  }

  return null;
}


function readModelCount(
  object,
  possibleKeys
) {
  if (
    !object ||
    typeof object !== "object"
  ) {
    return 0;
  }

  const entries =
    Object.entries(object).map(
      ([key, value]) => [
        key
          .toLowerCase()
          .replace(/[_-]+/g, " ")
          .replace(/\s+/g, " ")
          .trim(),
        value,
      ]
    );

  for (
    const possibleKey of possibleKeys
  ) {
    const normalizedKey =
      possibleKey
        .toLowerCase()
        .replace(/[_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();

    const match =
      entries.find(
        ([key]) =>
          key === normalizedKey
      );

    if (match) {
      const number =
        toFiniteNumber(
          match[1]
        );

      if (number !== null) {
        return number;
      }
    }
  }

  return 0;
}


function toFiniteNumber(
  value
) {
  const number =
    Number(value);

  return Number.isFinite(number)
    ? number
    : null;
}


function firstFiniteNumber(
  values
) {
  for (const value of values) {
    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return value;
    }
  }

  return null;
}


function percentage(
  numerator,
  denominator
) {
  if (
    typeof numerator !== "number" ||
    typeof denominator !== "number" ||
    !Number.isFinite(numerator) ||
    !Number.isFinite(denominator) ||
    denominator <= 0
  ) {
    return null;
  }

  return (
    numerator /
    denominator
  ) * 100;
}

function readAllocationValue(
  object,
  keys
) {
  for (
    const key of keys
  ) {

    const value =
      object?.[key];


    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {

      if (
        key ===
          "ai_adoption" &&
        value <= 1
      ) {
        return value * 100;
      }


      if (
        value <= 1
      ) {
        return value * 100;
      }


      return value;
    }
  }


  return null;
}


/* =========================================================
   DISPLAY HELPERS
========================================================= */

function formatBackendPercent(
  value
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  const rounded =
    Math.round(value * 100) / 100;

  if (
    Math.abs(rounded) < 0.005
  ) {
    return "0%";
  }

  return `${rounded}%`;
}


function formatRawNumber(
  value
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "—";
  }


  return value.toFixed(
    4
  );
}


function safeVisualPercent(
  value
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return 0;
  }


  return Math.max(
    0,
    Math.min(
      100,
      value
    )
  );
}


function getInitials(
  text
) {
  if (!text) {
    return "—";
  }


  return text
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(
      (word) =>
        word[0]
    )
    .join("")
    .toUpperCase();
}