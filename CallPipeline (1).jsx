import { useEffect, useRef, useState, useCallback } from "react";

/* ─────────────────────────────────────────────
   BRAND TOKENS — Calleem website palette
   (sage page + dark forest card + bright kelly accent)
───────────────────────────────────────────── */
const B = {
  // Page (sage / muted forest)
  page:        "#6f8e72",
  pageDark:    "#5d7d62",
  // Card surfaces (deep forest near-black)
  cardBg:      "#0c2014",
  cardBgMid:   "#10291a",
  nodeBg:      "#13321f",
  nodeBgIdle:  "#0e2517",
  // Accents
  greenDeep:   "#0d3a20",
  green:       "#1c8a4f",   // base brand kelly green
  greenBright: "#23a55a",   // hover / glow
  greenLight:  "#3fc878",   // accent highlights
  greenGlow:   "rgba(35,165,90,0.32)",
  // Inks
  white:       "#ffffff",
  ink:         "#0a1810",
  textW:       "rgba(255,255,255,0.95)",
  textW70:     "rgba(255,255,255,0.6)",
  textW40:     "rgba(255,255,255,0.32)",
  textOnPage:  "#ffffff",
  textOnPageMuted: "rgba(255,255,255,0.7)",
};

/* ─────────────────────────────────────────────
   SOLAR BOLD-STYLE ICONS (inline SVGs)
   Filled, rounded, bold — matches solar-icons aesthetic
───────────────────────────────────────────── */
function Icon({ name, size = 20, color = "currentColor" }) {
  const props = {
    width: size, height: size, viewBox: "0 0 24 24", fill: color,
    xmlns: "http://www.w3.org/2000/svg"
  };
  switch (name) {
    case "phone":
      return (
        <svg {...props}>
          <path fillRule="evenodd" clipRule="evenodd" d="M9.158 4.55a3.42 3.42 0 0 0-2.5-1.05c-.97 0-1.844.418-2.46 1.06l-.32.34c-1.6 1.71-1.7 4.36-.18 6.4 2.18 2.92 4.6 5.34 7.52 7.52 2.04 1.52 4.69 1.42 6.4-.18l.34-.32a3.42 3.42 0 0 0 0-4.96c-.66-.61-1.5-.92-2.34-.92s-1.66.31-2.32.92l-.43.42a.5.5 0 0 1-.62.07 16.6 16.6 0 0 1-3.92-3.92.5.5 0 0 1 .07-.62l.42-.43a3.42 3.42 0 0 0 .34-4.36Z"/>
        </svg>
      );
    case "user":
      return (
        <svg {...props}>
          <path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Z"/>
          <path fillRule="evenodd" clipRule="evenodd" d="M3.75 18.75c0-2.49 4.03-4.5 8.25-4.5s8.25 2.01 8.25 4.5S16.22 21 12 21s-8.25-.76-8.25-2.25Z"/>
        </svg>
      );
    case "calendar-search":
      return (
        <svg {...props}>
          <path d="M7 1.75a.75.75 0 0 1 .75.75v.76c.66-.01 1.38-.01 2.16-.01h4.18c.78 0 1.5 0 2.16.01V2.5a.75.75 0 0 1 1.5 0v.83c.07 0 .13.01.2.02 1.32.18 2.39.55 3.23 1.4.84.83 1.21 1.9 1.39 3.21.17 1.28.17 2.92.17 4.99v.05c0 2.07 0 3.71-.17 4.99-.18 1.31-.55 2.39-1.39 3.22-.84.84-1.91 1.21-3.23 1.39-1.28.17-2.92.17-4.98.17h-2c-2.06 0-3.7 0-4.98-.17-1.32-.18-2.39-.55-3.23-1.4-.84-.83-1.21-1.9-1.39-3.21C1.22 17 1.22 15.36 1.22 13.29v-.05c0-2.07 0-3.71.17-4.99.18-1.31.55-2.39 1.39-3.22.84-.84 1.91-1.21 3.23-1.39.07-.01.13-.02.2-.02V2.5a.75.75 0 0 1 .75-.75ZM12 11.25a3.25 3.25 0 1 0 1.96 5.84l1.22 1.22a.75.75 0 1 0 1.06-1.06l-1.22-1.22A3.25 3.25 0 0 0 12 11.25Zm-1.75 3.25a1.75 1.75 0 1 1 3.5 0 1.75 1.75 0 0 1-3.5 0Z"/>
        </svg>
      );
    case "calendar-check":
      return (
        <svg {...props}>
          <path d="M7 1.75a.75.75 0 0 1 .75.75v.76c.66-.01 1.38-.01 2.16-.01h4.18c.78 0 1.5 0 2.16.01V2.5a.75.75 0 0 1 1.5 0v.83c.07 0 .13.01.2.02 1.32.18 2.39.55 3.23 1.4.84.83 1.21 1.9 1.39 3.21.17 1.28.17 2.92.17 4.99v.05c0 2.07 0 3.71-.17 4.99-.18 1.31-.55 2.39-1.39 3.22-.84.84-1.91 1.21-3.23 1.39-1.28.17-2.92.17-4.98.17h-2c-2.06 0-3.7 0-4.98-.17-1.32-.18-2.39-.55-3.23-1.4-.84-.83-1.21-1.9-1.39-3.21C1.22 17 1.22 15.36 1.22 13.29v-.05c0-2.07 0-3.71.17-4.99.18-1.31.55-2.39 1.39-3.22.84-.84 1.91-1.21 3.23-1.39.07-.01.13-.02.2-.02V2.5a.75.75 0 0 1 .75-.75Zm9.55 11.32a.75.75 0 0 0-1.1-1.02l-3.96 4.27-1.94-2.09a.75.75 0 1 0-1.1 1.02l2.49 2.69c.14.16.34.25.55.25s.41-.09.55-.25l4.51-4.87Z"/>
        </svg>
      );
    case "envelope-check":
      return (
        <svg {...props}>
          <path fillRule="evenodd" clipRule="evenodd" d="M11.95 2c-2.05 0-3.65 0-4.92.16-1.3.16-2.36.5-3.21 1.21-.8.66-1.4 1.5-1.79 2.6C1.65 7 1.5 8.27 1.5 9.92v4.16c0 1.65.15 2.92.53 4 .39 1.1.99 1.94 1.79 2.6.85.71 1.91 1.05 3.21 1.21 1.27.16 2.87.16 4.92.16h.1c2.05 0 3.65 0 4.92-.16 1.3-.16 2.36-.5 3.21-1.21.8-.66 1.4-1.5 1.79-2.6.38-1.08.53-2.35.53-4V9.92c0-1.65-.15-2.92-.53-4-.39-1.1-.99-1.94-1.79-2.6-.85-.71-1.91-1.05-3.21-1.21C15.7 2 14.1 2 12.05 2h-.1ZM5.59 7.65a.75.75 0 0 0-.93 1.18l4.78 3.78a4.13 4.13 0 0 0 5.12 0l4.78-3.78a.75.75 0 0 0-.93-1.18l-4.78 3.78a2.63 2.63 0 0 1-3.26 0L5.59 7.65Z"/>
        </svg>
      );
    case "book":
      return (
        <svg {...props}>
          <path fillRule="evenodd" clipRule="evenodd" d="M2.5 8c0-2.83 0-4.24.88-5.12C4.26 2 5.67 2 8.5 2h2c2.83 0 4.24 0 5.12.88.88.88.88 2.29.88 5.12v8c0 2.83 0 4.24-.88 5.12-.88.88-2.29.88-5.12.88h-2c-2.83 0-4.24 0-5.12-.88C2.5 20.24 2.5 18.83 2.5 16V8Zm15 14h.5c1.4 0 2.1 0 2.66-.27.5-.24.9-.63 1.13-1.13.27-.56.27-1.26.27-2.66V8c0-1.4 0-2.1-.27-2.66a3 3 0 0 0-1.13-1.13C20.1 3.94 19.4 3.94 18 3.94h-.5V22Z"/>
          <path d="M5.5 7.75a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1-.75-.75Zm0 4a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1-.75-.75Zm.75 3.25a.75.75 0 0 0 0 1.5h4a.75.75 0 0 0 0-1.5h-4Z"/>
        </svg>
      );
    case "chat":
      return (
        <svg {...props}>
          <path fillRule="evenodd" clipRule="evenodd" d="M12 2c5.52 0 10 4.03 10 9 0 4.97-4.48 9-10 9-1.05 0-2.07-.15-3.03-.42-.21-.06-.32-.09-.41-.1a1 1 0 0 0-.16 0c-.09.01-.2.05-.43.13l-3.95 1.32a.75.75 0 0 1-.95-.95l1.32-3.95c.07-.22.11-.34.13-.43a1 1 0 0 0 0-.16c-.01-.09-.04-.2-.1-.41A8.83 8.83 0 0 1 2 11c0-4.97 4.48-9 10-9Zm-3.75 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm4.5-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm2.5 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"/>
        </svg>
      );
    case "phone-off":
      return (
        <svg {...props}>
          <path d="m21.78 3.28-2.5 2.5-2.5-2.5a.75.75 0 0 0-1.06 1.06l2.5 2.5-2.5 2.5a.75.75 0 0 0 1.06 1.06l2.5-2.5 2.5 2.5a.75.75 0 0 0 1.06-1.06l-2.5-2.5 2.5-2.5a.75.75 0 0 0-1.06-1.06Z"/>
          <path d="M9.16 4.55a3.42 3.42 0 0 0-2.5-1.05c-.97 0-1.84.42-2.46 1.06l-.32.34c-1.6 1.71-1.7 4.36-.18 6.4 2.18 2.92 4.6 5.34 7.52 7.52 2.04 1.52 4.69 1.42 6.4-.18l.34-.32a3.42 3.42 0 0 0 0-4.96c-.66-.61-1.5-.92-2.34-.92s-1.66.31-2.32.92l-.43.42a.5.5 0 0 1-.62.07 16.6 16.6 0 0 1-3.92-3.92.5.5 0 0 1 .07-.62l.42-.43a3.42 3.42 0 0 0 .34-4.36Z"/>
        </svg>
      );
    case "play":
      return <svg {...props}><path d="M19.4 9.85 8.78 3.78C6.78 2.64 4.5 4.05 4.5 6.36v12.13c0 2.31 2.28 3.72 4.28 2.58l10.62-6.07a3 3 0 0 0 0-5.15Z"/></svg>;
    case "arrow-left":
      return <svg {...props}><path fillRule="evenodd" clipRule="evenodd" d="M15.53 5.47a.75.75 0 0 1 0 1.06L10.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06l-6-6a.75.75 0 0 1 0-1.06l6-6a.75.75 0 0 1 1.06 0Z"/></svg>;
    case "arrow-right":
      return <svg {...props}><path fillRule="evenodd" clipRule="evenodd" d="M8.47 5.47a.75.75 0 0 1 1.06 0l6 6a.75.75 0 0 1 0 1.06l-6 6a.75.75 0 1 1-1.06-1.06L13.94 12 8.47 6.53a.75.75 0 0 1 0-1.06Z"/></svg>;
    default:
      return null;
  }
}

/* ─────────────────────────────────────────────
   GEOMETRY
───────────────────────────────────────────── */
const VB_W = 1180;
const VB_H = 480;
const NW   = 210;
const NH   = 80;
const HW   = 220;
const HH   = 110;
const CL   = 38;
const CR   = VB_W - NW - 38;
const HX   = (VB_W - HW) / 2;
const HY   = (VB_H - HH) / 2;

const NODE_DEFS = {
  phone:   { x:CL, y:42,  w:NW, h:NH },
  calleem: { x:HX, y:HY,  w:HW, h:HH },
  cal:     { x:CR, y:42,  w:NW, h:NH },
  book:    { x:CR, y:184, w:NW, h:NH },
  confirm: { x:CR, y:326, w:NW, h:NH },
  kb:      { x:CL, y:184, w:NW, h:NH },
  answer:  { x:CR, y:184, w:NW, h:NH },
  end:     { x:CL, y:326, w:NW, h:NH },
};

/* ─────────────────────────────────────────────
   SCENARIOS
───────────────────────────────────────────── */
const SCENARIOS = {
  book: {
    label: "Book an Appointment",
    iconName: "calendar-check",
    steps: [
      { nodeId:"phone",   label:"Call comes in",      stepLabel:"A customer dials your business",        bubble:{ who:"caller",  text:"Hi! I'd like to book an appointment for next Tuesday." } },
      { nodeId:"calleem", label:"Calleem answers",    stepLabel:"Calleem picks up and listens",          bubble:{ who:"calleem", text:"Good morning! Of course — morning or afternoon?" } },
      { nodeId:"cal",     label:"Checks calendar",    stepLabel:"Looking up real-time availability",     bubble:{ who:"calleem", text:"One moment, checking Tuesday for you…" } },
      { nodeId:"book",    label:"Books the slot",     stepLabel:"Appointment confirmed and saved",       bubble:{ who:"calleem", text:"10:30 AM is free. Shall I lock it in?" } },
      { nodeId:"confirm", label:"Sends confirmation", stepLabel:"SMS and email confirmation dispatched", bubble:{ who:"calleem", text:"Done — confirmation sent by SMS and email." } },
      { nodeId:"end",     label:"Call ends",          stepLabel:"Customer happy — appointment booked",   bubble:{ who:"caller",  text:"Easy. Thanks so much, see you Tuesday!" } },
    ],
    wires: [
      { from:"phone",   to:"calleem" },
      { from:"calleem", to:"cal"     },
      { from:"calleem", to:"book"    },
      { from:"calleem", to:"confirm" },
      { from:"end",     to:"calleem" },
    ],
    activeWiresByStep: [
      [],
      ["phone->calleem"],
      ["calleem->cal"],
      ["calleem->book"],
      ["calleem->confirm"],
      ["end->calleem"],
    ],
  },
  info: {
    label: "Answer a Question",
    iconName: "chat",
    steps: [
      { nodeId:"phone",   label:"Call comes in",     stepLabel:"A customer dials your business",       bubble:{ who:"caller",  text:"Hi, what time do you close tonight?" } },
      { nodeId:"calleem", label:"Calleem listens",   stepLabel:"Identifies it's an info request",      bubble:{ who:"calleem", text:"Good evening! Let me check our hours for you." } },
      { nodeId:"kb",      label:"Looks it up",       stepLabel:"Searches the business knowledge base", bubble:{ who:"calleem", text:"One second, pulling that up now…" } },
      { nodeId:"answer",  label:"Replies instantly", stepLabel:"Perfect answer delivered on the spot", bubble:{ who:"calleem", text:"We close at 8 PM tonight. Anything else I can help with?" } },
      { nodeId:"end",     label:"Call ends",         stepLabel:"Customer happy — question answered",   bubble:{ who:"caller",  text:"Perfect, thank you. Goodbye!" } },
    ],
    wires: [
      { from:"phone",   to:"calleem" },
      { from:"kb",      to:"calleem" },
      { from:"calleem", to:"answer"  },
      { from:"end",     to:"calleem" },
    ],
    activeWiresByStep: [
      [],
      ["phone->calleem"],
      ["kb->calleem"],
      ["calleem->answer"],
      ["end->calleem"],
    ],
  },
};

/* ─────────────────────────────────────────────
   GEOMETRY HELPERS
───────────────────────────────────────────── */
const cy   = n => n.y + n.h / 2;
const ra   = n => ({ x: n.x + n.w, y: cy(n) });
const la   = n => ({ x: n.x,       y: cy(n) });
const hLA  = () => la(NODE_DEFS.calleem);
const hRA  = () => ra(NODE_DEFS.calleem);

const bezPath = (f, t) => {
  const dx = t.x - f.x;
  return `M${f.x},${f.y} C${f.x+dx*0.55},${f.y} ${t.x-dx*0.55},${t.y} ${t.x},${t.y}`;
};

function resolveWire(w) {
  const fn = NODE_DEFS[w.from], tn = NODE_DEFS[w.to];
  const from = w.from==="calleem" ? hRA() : ra(fn);
  const to   = w.to  ==="calleem" ? hLA() : la(tn);
  return { id:`${w.from}->${w.to}`, d:bezPath(from,to), startPt:from, endPt:to };
}

/* ─────────────────────────────────────────────
   ACTIVE PULSE — single dot, only on active wire
───────────────────────────────────────────── */
function ActivePulse({ d, active }) {
  if (!active) return null;
  return (
    <g style={{ pointerEvents: "none" }}>
      <circle r="9" fill="url(#pGlow)" opacity="0.6">
        <animateMotion dur="2.2s" repeatCount="indefinite" path={d} keyPoints="0;1" keyTimes="0;1"/>
      </circle>
      <circle r="2.8" fill={B.white}>
        <animateMotion dur="2.2s" repeatCount="indefinite" path={d} keyPoints="0;1" keyTimes="0;1"/>
      </circle>
    </g>
  );
}

/* ─────────────────────────────────────────────
   NODE META
───────────────────────────────────────────── */
const NODE_META = {
  phone:   { iconName:"phone",          title:"Business Phone",    sub:"incoming call" },
  calleem: { iconName:"user",           title:"Calleem",           sub:"AI Receptionist", isHub:true },
  cal:     { iconName:"calendar-search",title:"Check Calendar",    sub:"availability" },
  book:    { iconName:"calendar-check", title:"Book Appointment",  sub:"saves the slot" },
  confirm: { iconName:"envelope-check", title:"Send Confirmation", sub:"SMS · email" },
  kb:      { iconName:"book",           title:"Knowledge Base",    sub:"business info" },
  answer:  { iconName:"chat",           title:"Reply to Caller",   sub:"instant answer" },
  end:     { iconName:"phone-off",      title:"Call Ends",         sub:"customer happy" },
};

/* ─────────────────────────────────────────────
   NODE CARD — three states
───────────────────────────────────────────── */
function NodeCard({ nodeId, present, isCurrent }) {
  const meta = NODE_META[nodeId];
  const def  = NODE_DEFS[nodeId];
  if (!meta || !def) return null;
  const { iconName, title, sub, isHub } = meta;

  let bg, border, iconBg, iconBorder, iconColor, opacity, shadow;
  if (!present) {
    bg = B.nodeBgIdle;
    border = "rgba(255,255,255,0.04)";
    iconBg = "rgba(255,255,255,0.03)";
    iconBorder = "rgba(255,255,255,0.05)";
    iconColor = "rgba(255,255,255,0.28)";
    opacity = 0.32;
    shadow = "0 4px 12px -8px rgba(0,0,0,0.4)";
  } else if (isCurrent) {
    bg = `linear-gradient(160deg, ${B.nodeBg} 0%, ${B.cardBg} 100%)`;
    border = B.greenBright;
    iconBg = `linear-gradient(180deg, ${B.greenBright}, ${B.green})`;
    iconBorder = B.greenLight;
    iconColor = B.white;
    opacity = 1;
    shadow = `0 0 0 1px rgba(35,165,90,0.20), 0 0 32px rgba(35,165,90,0.32), 0 12px 24px -10px rgba(0,0,0,0.5)`;
  } else {
    bg = B.nodeBg;
    border = "rgba(255,255,255,0.07)";
    iconBg = "rgba(255,255,255,0.05)";
    iconBorder = "rgba(255,255,255,0.08)";
    iconColor = "rgba(255,255,255,0.78)";
    opacity = 1;
    shadow = "0 8px 18px -10px rgba(0,0,0,0.45)";
  }

  return (
    <foreignObject x={def.x} y={def.y} width={def.w} height={def.h} style={{overflow:"visible"}}>
      <div style={{
        width:"100%", height:"100%",
        borderRadius: isHub ? 18 : 14,
        background: bg,
        border: `1px solid ${border}`,
        boxShadow: shadow,
        padding: isHub ? "14px 16px" : "12px 14px",
        display:"flex",
        flexDirection: isHub ? "column" : "row",
        alignItems:"center",
        justifyContent: isHub ? "center" : "flex-start",
        gap: isHub ? 8 : 12,
        textAlign: isHub ? "center" : "left",
        opacity,
        transition: "background 0.5s, border 0.5s, box-shadow 0.5s, opacity 0.5s",
        fontFamily:"'Inter','Helvetica Neue',sans-serif",
      }}>
        <div style={{
          width:isHub?44:36, height:isHub?44:36,
          borderRadius: isHub ? 11 : 9, flexShrink:0,
          display:"flex", alignItems:"center", justifyContent:"center",
          background: iconBg,
          border: `1px solid ${iconBorder}`,
          color: iconColor,
          transition: "background 0.5s, border 0.5s, color 0.5s",
        }}>
          <Icon name={iconName} size={isHub ? 22 : 17}/>
        </div>
        <div style={{minWidth:0, display:"flex", flexDirection:"column", gap:3}}>
          <div style={{fontSize:isHub?15:13.5, fontWeight:600, color:B.white, letterSpacing:"0.005em", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis"}}>
            {title}
          </div>
          <div style={{fontSize:10.5, color:"rgba(255,255,255,0.55)", textTransform:"uppercase", letterSpacing:"0.10em", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis", fontWeight:500}}>
            {sub}
          </div>
        </div>
      </div>
    </foreignObject>
  );
}

/* ─────────────────────────────────────────────
   CHAT BUBBLE
───────────────────────────────────────────── */
function ChatBubble({ bubble, visible }) {
  if (!bubble) return null;
  const isCaller = bubble.who === "caller";
  return (
    <div style={{
      position:"absolute", bottom:30,
      left:  isCaller ? 26 : "auto",
      right: isCaller ? "auto" : 26,
      maxWidth:300,
      opacity: visible ? 1 : 0,
      transform: visible ? "translateY(0)" : "translateY(6px)",
      transition:"opacity 0.4s, transform 0.4s",
      pointerEvents:"none", zIndex:10,
    }}>
      <div style={{
        borderRadius: 14,
        borderBottomLeftRadius:  isCaller ? 4 : 14,
        borderBottomRightRadius: isCaller ? 14 : 4,
        background: isCaller
          ? "rgba(255,255,255,0.07)"
          : "rgba(28,138,79,0.32)",
        border:`1px solid ${isCaller ? "rgba(255,255,255,0.12)" : "rgba(35,165,90,0.4)"}`,
        padding:"10px 14px",
        backdropFilter:"blur(8px)",
      }}>
        <div style={{fontSize:9.5, letterSpacing:"0.14em", textTransform:"uppercase", fontWeight:600,
          color: isCaller ? "rgba(255,255,255,0.42)" : B.greenLight,
          marginBottom:5,
          fontFamily:"'Inter',sans-serif",
        }}>
          {isCaller ? "Caller" : "Calleem"}
        </div>
        <div style={{fontSize:13, lineHeight:1.55,
          color: isCaller ? "rgba(255,255,255,0.88)" : "#c8f0d8",
          fontFamily:"Georgia, 'Times New Roman', serif",
          fontStyle:"italic",
        }}>
          “{bubble.text}”
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   STEP STRIP
───────────────────────────────────────────── */
function StepStrip({ steps, currentStep, onStep }) {
  return (
    <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap:0, marginBottom:22}}>
      {steps.map((s,i) => {
        const done=i<currentStep, cur=i===currentStep;
        return (
          <div key={i} style={{display:"flex", alignItems:"center"}}>
            <button onClick={()=>onStep(i)} title={s.stepLabel} style={{
              display:"flex", flexDirection:"column", alignItems:"center", gap:7,
              background:"none", border:"none", cursor:"pointer", padding:"3px 4px",
            }}>
              <div style={{
                width: cur ? 12 : 8, height: cur ? 12 : 8, borderRadius:"50%",
                background: cur ? B.greenLight : done ? B.greenBright : "rgba(255,255,255,0.28)",
                boxShadow: cur ? `0 0 0 5px rgba(63,200,120,0.22)` : "none",
                transition:"all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
              }}/>
              <div style={{fontSize:9.5, letterSpacing:"0.06em", textTransform:"uppercase",
                color: cur ? B.white : done ? "rgba(255,255,255,0.78)" : "rgba(255,255,255,0.45)",
                fontFamily:"'Inter',sans-serif", fontWeight: cur ? 600 : 500,
                maxWidth:88, textAlign:"center", lineHeight:1.35, whiteSpace:"normal",
                transition:"color 0.4s",
              }}>
                {s.label}
              </div>
            </button>
            {i < steps.length-1 && (
              <div style={{width:34, height:1.5,
                background: done ? B.greenBright : "rgba(255,255,255,0.16)",
                marginBottom:24, marginLeft:4, marginRight:4, flexShrink:0,
                transition:"background 0.4s"}} />
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ─────────────────────────────────────────────
   MAIN
───────────────────────────────────────────── */
export default function CallPipeline() {
  const [scenarioId, setScenarioId] = useState("book");
  const [stepIdx,    setStepIdx]    = useState(0);
  const [bubbleVis,  setBubbleVis]  = useState(true);
  const timerRef = useRef(null);

  const scenario    = SCENARIOS[scenarioId];
  const steps       = scenario.steps;
  const total       = steps.length;
  const currentStep = steps[stepIdx];
  const activeWires = scenario.activeWiresByStep[stepIdx] || [];
  const wires       = scenario.wires.map(resolveWire);

  const advance = useCallback(() => {
    setBubbleVis(false);
    setTimeout(() => { setStepIdx(i => (i+1) % steps.length); setBubbleVis(true); }, 380);
  }, [steps.length]);

  useEffect(() => {
    timerRef.current = setInterval(advance, 3600);
    return () => clearInterval(timerRef.current);
  }, [advance]);

  function switchScenario(id) {
    clearInterval(timerRef.current);
    setScenarioId(id); setStepIdx(0); setBubbleVis(true);
  }
  function goToStep(i) {
    setBubbleVis(false);
    setTimeout(() => { setStepIdx(i); setBubbleVis(true); }, 200);
    clearInterval(timerRef.current);
    timerRef.current = setInterval(advance, 3600);
  }

  const scenarioNodes = new Set(scenario.steps.map(s=>s.nodeId));
  scenarioNodes.add("calleem");
  const currentNodeId = currentStep.nodeId;

  return (
    <>
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"/>
      <div style={{
        minHeight:"100vh", width:"100%",
        background: `linear-gradient(180deg, ${B.page} 0%, ${B.pageDark} 100%)`,
        padding:"44px 20px",
        display:"flex", alignItems:"center", justifyContent:"center",
        fontFamily:"'Inter','Helvetica Neue',sans-serif",
      }}>

        <div style={{width:"100%", maxWidth:1200, position:"relative"}}>

          {/* ── HEADER ── */}
          <div style={{display:"flex", alignItems:"center", justifyContent:"center", marginBottom:14, padding:"0 4px"}}>
            <div style={{display:"flex", flexDirection:"column", alignItems:"center", gap:10}}>
              <div style={{display:"flex", alignItems:"center", gap:8}}>
                {/* logo mark */}
                <svg width="26" height="26" viewBox="0 0 28 28" fill="none">
                  <path d="M5 9 L13 14 L5 19"   stroke={B.greenDeep}   strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  <path d="M11 9 L19 14 L11 19" stroke={B.greenBright} strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                </svg>
                <span style={{fontFamily:"'Inter',sans-serif", fontWeight:700, fontSize:20, letterSpacing:"0.04em", color:B.white}}>Calleem</span>
              </div>
            </div>
          </div>

          {/* ── TITLE ── */}
          <div style={{textAlign:"center", marginBottom:20}}>
            <div style={{display:"inline-flex", alignItems:"center", gap:7, fontSize:11, letterSpacing:"0.18em", textTransform:"uppercase", color:B.greenLight, fontWeight:600, marginBottom:14}}>
              <span style={{width:6, height:6, borderRadius:"50%", background:B.greenLight, display:"block"}}/>
              How it works
            </div>
            <h1 style={{
              fontFamily:"'Inter',sans-serif", fontSize:38, lineHeight:1.1, letterSpacing:"-0.02em",
              color:B.white, margin:0, fontWeight:700,
            }}>
              See how Calleem<br/>handles every call
            </h1>
          </div>

          {/* ── SCENARIO BUTTONS ── */}
          <div style={{display:"flex", justifyContent:"center", gap:10, marginBottom:24}}>
            {Object.entries(SCENARIOS).map(([id, sc]) => {
              const sel = id===scenarioId;
              return (
                <button key={id} onClick={()=>switchScenario(id)} style={{
                  display:"inline-flex", alignItems:"center", gap:8,
                  fontFamily:"'Inter',sans-serif", fontSize:13, fontWeight:600, letterSpacing:"0.005em",
                  padding:"10px 22px", borderRadius:999,
                  border: sel ? `1.5px solid ${B.greenBright}` : "1.5px solid rgba(255,255,255,0.22)",
                  background: sel ? B.green : "rgba(255,255,255,0.06)",
                  color: B.white,
                  cursor:"pointer",
                  boxShadow: sel ? "0 6px 20px -6px rgba(35,165,90,0.55)" : "none",
                  transition:"all 0.25s",
                }}>
                  <Icon name={sc.iconName} size={15}/>
                  {sc.label}
                </button>
              );
            })}
          </div>

          {/* ── STEP STRIP ── */}
          <StepStrip steps={steps} currentStep={stepIdx} onStep={goToStep}/>

          {/* ── THE CARD ── */}
          <div style={{
            position:"relative", borderRadius:24, overflow:"hidden",
            background:`linear-gradient(165deg, ${B.cardBgMid} 0%, ${B.cardBg} 60%, #081a10 100%)`,
            border:`1px solid rgba(255,255,255,0.08)`,
            boxShadow:`0 1px 0 rgba(255,255,255,0.06) inset, 0 30px 60px -32px rgba(8,26,16,0.6)`,
          }}>
            {/* very faint center glow */}
            <div aria-hidden style={{position:"absolute",inset:0,pointerEvents:"none",
              backgroundImage:`radial-gradient(ellipse at 50% 50%, ${B.greenGlow} 0%, transparent 55%)`}}/>

            {/* current step caption */}
            <div style={{
              position:"absolute", top:18, left:"50%", transform:"translateX(-50%)",
              fontSize:10.5, letterSpacing:"0.18em", textTransform:"uppercase",
              color:"rgba(255,255,255,0.62)", fontWeight:600, whiteSpace:"nowrap",
              opacity: bubbleVis ? 1 : 0.4, transition:"opacity 0.4s",
              display:"flex", alignItems:"center", gap:8,
            }}>
              <span style={{color:B.greenLight}}>
                <Icon name="play" size={9}/>
              </span>
              {currentStep.stepLabel}
            </div>

            {/* ── SVG ── */}
            <svg viewBox={`0 0 ${VB_W} ${VB_H}`} style={{width:"100%",height:"auto",display:"block",position:"relative"}} xmlns="http://www.w3.org/2000/svg">
              <defs>
                <radialGradient id="pGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%"   stopColor={B.white}       stopOpacity="1"/>
                  <stop offset="40%"  stopColor={B.greenLight}  stopOpacity="0.75"/>
                  <stop offset="100%" stopColor={B.green}       stopOpacity="0"/>
                </radialGradient>
              </defs>

              {/* base wires */}
              {wires.map(w=>(
                <path key={w.id+"-b"} d={w.d} fill="none"
                  stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>
              ))}

              {/* active wire */}
              {wires.map(w=>{
                const on = activeWires.includes(w.id);
                return <path key={w.id+"-a"} d={w.d} fill="none"
                  stroke={on ? B.greenLight : "transparent"}
                  strokeWidth={on ? 1.8 : 0}
                  opacity={on ? 0.75 : 0}
                  style={{transition:"opacity 0.5s, stroke-width 0.5s"}}/>;
              })}

              {/* anchor dots */}
              {wires.map(w=>(
                <g key={"anc-"+w.id}>
                  <circle cx={w.startPt.x} cy={w.startPt.y} r={2.5} fill={B.white} opacity={0.32}/>
                  <circle cx={w.endPt.x}   cy={w.endPt.y}   r={2.5} fill={B.white} opacity={0.32}/>
                </g>
              ))}

              {/* the one traveling pulse */}
              {wires.map(w=>(
                <ActivePulse key={w.id+"-pulse"} d={w.d}
                  active={activeWires.includes(w.id)}/>
              ))}

              {/* NODES */}
              <NodeCard nodeId="calleem" present={true} isCurrent={currentNodeId === "calleem"}/>
              {[...scenarioNodes].filter(id=>id!=="calleem").map(id=>(
                <NodeCard key={id} nodeId={id}
                  present={true}
                  isCurrent={currentNodeId === id}/>
              ))}
            </svg>

            {/* CONVERSATION BUBBLE */}
            <ChatBubble bubble={currentStep.bubble} visible={bubbleVis}/>
          </div>

          {/* ── CONTROLS ── */}
          <div style={{display:"flex",justifyContent:"center",alignItems:"center",gap:18,marginTop:24}}>
            <button onClick={()=>goToStep((stepIdx-1+total)%total)} style={{
              display:"inline-flex", alignItems:"center", gap:6,
              fontFamily:"'Inter',sans-serif",fontSize:12,fontWeight:600,letterSpacing:"0.02em",
              padding:"9px 20px",borderRadius:999,
              border:"1.5px solid rgba(255,255,255,0.22)",background:"rgba(255,255,255,0.06)",
              color:B.white,cursor:"pointer",transition:"all 0.2s",
            }}><Icon name="arrow-left" size={13}/> Back</button>
            <span style={{fontSize:11,letterSpacing:"0.16em",textTransform:"uppercase",color:"rgba(255,255,255,0.7)",fontWeight:600}}>
              {stepIdx+1} / {total}
            </span>
            <button onClick={()=>goToStep((stepIdx+1)%total)} style={{
              display:"inline-flex", alignItems:"center", gap:6,
              fontFamily:"'Inter',sans-serif",fontSize:12,fontWeight:600,letterSpacing:"0.02em",
              padding:"9px 22px",borderRadius:999,
              border:`1.5px solid ${B.greenBright}`,background:B.green,
              color:B.white,cursor:"pointer",transition:"all 0.2s",
              boxShadow:"0 6px 20px -6px rgba(35,165,90,0.55)",
            }}>Next <Icon name="arrow-right" size={13}/></button>
          </div>

        </div>
      </div>
    </>
  );
}
