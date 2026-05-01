"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";

const B = {
  cardBg: "#648768",
  cardBgMid: "#5b7a62",
  nodeBg: "#3f5c47",
  nodeBgIdle: "#344b3a",
  greenDeep: "#0a4c2f",
  green: "#2C7A44",
  greenBright: "#4ab66f",
  greenLight: "#32704bff",
  greenGlow: "rgba(53, 139, 89, 0.22)",
  white: "#ffffff",
};

const FONT_SANS = "var(--font-manrope), 'Manrope', sans-serif";
const FONT_DISPLAY = "var(--font-host), 'Host Grotesk', sans-serif";

type IconName =
  | "phone"
  | "user"
  | "calendar-search"
  | "calendar-check"
  | "envelope-check"
  | "book"
  | "chat"
  | "phone-off"
  | "play"
  | "arrow-left"
  | "arrow-right";

function Icon({ name, size = 20, color = "currentColor" }: { name: IconName; size?: number; color?: string }) {
  const props = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: color,
    xmlns: "http://www.w3.org/2000/svg",
  };
  switch (name) {
    case "phone":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M9.158 4.55a3.42 3.42 0 0 0-2.5-1.05c-.97 0-1.844.418-2.46 1.06l-.32.34c-1.6 1.71-1.7 4.36-.18 6.4 2.18 2.92 4.6 5.34 7.52 7.52 2.04 1.52 4.69 1.42 6.4-.18l.34-.32a3.42 3.42 0 0 0 0-4.96c-.66-.61-1.5-.92-2.34-.92s-1.66.31-2.32.92l-.43.42a.5.5 0 0 1-.62.07 16.6 16.6 0 0 1-3.92-3.92.5.5 0 0 1 .07-.62l.42-.43a3.42 3.42 0 0 0 .34-4.36Z"
          />
        </svg>
      );
    case "user":
      return (
        <svg {...props}>
          <path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Z" />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M3.75 18.75c0-2.49 4.03-4.5 8.25-4.5s8.25 2.01 8.25 4.5S16.22 21 12 21s-8.25-.76-8.25-2.25Z"
          />
        </svg>
      );
    case "calendar-search":
      return (
        <svg {...props}>
          <path d="M7 1.75a.75.75 0 0 1 .75.75v.76c.66-.01 1.38-.01 2.16-.01h4.18c.78 0 1.5 0 2.16.01V2.5a.75.75 0 0 1 1.5 0v.83c.07 0 .13.01.2.02 1.32.18 2.39.55 3.23 1.4.84.83 1.21 1.9 1.39 3.21.17 1.28.17 2.92.17 4.99v.05c0 2.07 0 3.71-.17 4.99-.18 1.31-.55 2.39-1.39 3.22-.84.84-1.91 1.21-3.23 1.39-1.28.17-2.92.17-4.98.17h-2c-2.06 0-3.7 0-4.98-.17-1.32-.18-2.39-.55-3.23-1.4-.84-.83-1.21-1.9-1.39-3.21C1.22 17 1.22 15.36 1.22 13.29v-.05c0-2.07 0-3.71.17-4.99.18-1.31.55-2.39 1.39-3.22.84-.84 1.91-1.21 3.23-1.39.07-.01.13-.02.2-.02V2.5a.75.75 0 0 1 .75-.75ZM12 11.25a3.25 3.25 0 1 0 1.96 5.84l1.22 1.22a.75.75 0 1 0 1.06-1.06l-1.22-1.22A3.25 3.25 0 0 0 12 11.25Zm-1.75 3.25a1.75 1.75 0 1 1 3.5 0 1.75 1.75 0 0 1-3.5 0Z" />
        </svg>
      );
    case "calendar-check":
      return (
        <svg {...props}>
          <path d="M7 1.75a.75.75 0 0 1 .75.75v.76c.66-.01 1.38-.01 2.16-.01h4.18c.78 0 1.5 0 2.16.01V2.5a.75.75 0 0 1 1.5 0v.83c.07 0 .13.01.2.02 1.32.18 2.39.55 3.23 1.4.84.83 1.21 1.9 1.39 3.21.17 1.28.17 2.92.17 4.99v.05c0 2.07 0 3.71-.17 4.99-.18 1.31-.55 2.39-1.39 3.22-.84.84-1.91 1.21-3.23 1.39-1.28.17-2.92.17-4.98.17h-2c-2.06 0-3.7 0-4.98-.17-1.32-.18-2.39-.55-3.23-1.4-.84-.83-1.21-1.9-1.39-3.21C1.22 17 1.22 15.36 1.22 13.29v-.05c0-2.07 0-3.71.17-4.99.18-1.31.55-2.39 1.39-3.22.84-.84 1.91-1.21 3.23-1.39.07-.01.13-.02.2-.02V2.5a.75.75 0 0 1 .75-.75Zm9.55 11.32a.75.75 0 0 0-1.1-1.02l-3.96 4.27-1.94-2.09a.75.75 0 1 0-1.1 1.02l2.49 2.69c.14.16.34.25.55.25s.41-.09.55-.25l4.51-4.87Z" />
        </svg>
      );
    case "envelope-check":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M11.95 2c-2.05 0-3.65 0-4.92.16-1.3.16-2.36.5-3.21 1.21-.8.66-1.4 1.5-1.79 2.6C1.65 7 1.5 8.27 1.5 9.92v4.16c0 1.65.15 2.92.53 4 .39 1.1.99 1.94 1.79 2.6.85.71 1.91 1.05 3.21 1.21 1.27.16 2.87.16 4.92.16h.1c2.05 0 3.65 0 4.92-.16 1.3-.16 2.36-.5 3.21-1.21.8-.66 1.4-1.5 1.79-2.6.38-1.08.53-2.35.53-4V9.92c0-1.65-.15-2.92-.53-4-.39-1.1-.99-1.94-1.79-2.6-.85-.71-1.91-1.05-3.21-1.21C15.7 2 14.1 2 12.05 2h-.1ZM5.59 7.65a.75.75 0 0 0-.93 1.18l4.78 3.78a4.13 4.13 0 0 0 5.12 0l4.78-3.78a.75.75 0 0 0-.93-1.18l-4.78 3.78a2.63 2.63 0 0 1-3.26 0L5.59 7.65Z"
          />
        </svg>
      );
    case "book":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M2.5 8c0-2.83 0-4.24.88-5.12C4.26 2 5.67 2 8.5 2h2c2.83 0 4.24 0 5.12.88.88.88.88 2.29.88 5.12v8c0 2.83 0 4.24-.88 5.12-.88.88-2.29.88-5.12.88h-2c-2.83 0-4.24 0-5.12-.88C2.5 20.24 2.5 18.83 2.5 16V8Zm15 14h.5c1.4 0 2.1 0 2.66-.27.5-.24.9-.63 1.13-1.13.27-.56.27-1.26.27-2.66V8c0-1.4 0-2.1-.27-2.66a3 3 0 0 0-1.13-1.13C20.1 3.94 19.4 3.94 18 3.94h-.5V22Z"
          />
          <path d="M5.5 7.75a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1-.75-.75Zm0 4a.75.75 0 0 1 .75-.75h6.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1-.75-.75Zm.75 3.25a.75.75 0 0 0 0 1.5h4a.75.75 0 0 0 0-1.5h-4Z" />
        </svg>
      );
    case "chat":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M12 2c5.52 0 10 4.03 10 9 0 4.97-4.48 9-10 9-1.05 0-2.07-.15-3.03-.42-.21-.06-.32-.09-.41-.1a1 1 0 0 0-.16 0c-.09.01-.2.05-.43.13l-3.95 1.32a.75.75 0 0 1-.95-.95l1.32-3.95c.07-.22.11-.34.13-.43a1 1 0 0 0 0-.16c-.01-.09-.04-.2-.1-.41A8.83 8.83 0 0 1 2 11c0-4.97 4.48-9 10-9Zm-3.75 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm4.5-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm2.5 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
          />
        </svg>
      );
    case "phone-off":
      return (
        <svg {...props}>
          <path d="m21.78 3.28-2.5 2.5-2.5-2.5a.75.75 0 0 0-1.06 1.06l2.5 2.5-2.5 2.5a.75.75 0 0 0 1.06 1.06l2.5-2.5 2.5 2.5a.75.75 0 0 0 1.06-1.06l-2.5-2.5 2.5-2.5a.75.75 0 0 0-1.06-1.06Z" />
          <path d="M9.16 4.55a3.42 3.42 0 0 0-2.5-1.05c-.97 0-1.84.42-2.46 1.06l-.32.34c-1.6 1.71-1.7 4.36-.18 6.4 2.18 2.92 4.6 5.34 7.52 7.52 2.04 1.52 4.69 1.42 6.4-.18l.34-.32a3.42 3.42 0 0 0 0-4.96c-.66-.61-1.5-.92-2.34-.92s-1.66.31-2.32.92l-.43.42a.5.5 0 0 1-.62.07 16.6 16.6 0 0 1-3.92-3.92.5.5 0 0 1 .07-.62l.42-.43a3.42 3.42 0 0 0 .34-4.36Z" />
        </svg>
      );
    case "play":
      return (
        <svg {...props}>
          <path d="M19.4 9.85 8.78 3.78C6.78 2.64 4.5 4.05 4.5 6.36v12.13c0 2.31 2.28 3.72 4.28 2.58l10.62-6.07a3 3 0 0 0 0-5.15Z" />
        </svg>
      );
    case "arrow-left":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M15.53 5.47a.75.75 0 0 1 0 1.06L10.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06l-6-6a.75.75 0 0 1 0-1.06l6-6a.75.75 0 0 1 1.06 0Z"
          />
        </svg>
      );
    case "arrow-right":
      return (
        <svg {...props}>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.47 5.47a.75.75 0 0 1 1.06 0l6 6a.75.75 0 0 1 0 1.06l-6 6a.75.75 0 1 1-1.06-1.06L13.94 12 8.47 6.53a.75.75 0 0 1 0-1.06Z"
          />
        </svg>
      );
    default:
      return null;
  }
}

const VB_W = 1180;
const VB_H = 480;
const NW = 210;
const NH = 80;
const HW = 220;
const HH = 110;
const CL = 38;
const CR = VB_W - NW - 38;
const HX = (VB_W - HW) / 2;
const HY = (VB_H - HH) / 2;

const NODE_DEFS = {
  phone: { x: CL, y: 42, w: NW, h: NH },
  calleem: { x: HX, y: HY, w: HW, h: HH },
  cal: { x: CR, y: 42, w: NW, h: NH },
  book: { x: CR, y: 184, w: NW, h: NH },
  confirm: { x: CR, y: 326, w: NW, h: NH },
  kb: { x: CL, y: 184, w: NW, h: NH },
  answer: { x: CR, y: 184, w: NW, h: NH },
  end: { x: CL, y: 326, w: NW, h: NH },
} as const;

type NodeId = keyof typeof NODE_DEFS;

type Bubble = {
  who: "caller" | "calleem";
  text: string;
};

type Step = {
  nodeId: NodeId;
  label: string;
  stepLabel: string;
  bubble: Bubble;
};

type Wire = {
  from: NodeId;
  to: NodeId;
};

type Scenario = {
  label: string;
  iconName: IconName;
  steps: Step[];
  wires: Wire[];
  activeWiresByStep: string[][];
};

type ScenarioId = "book" | "info";

const SCENARIOS: Record<ScenarioId, Scenario> = {
  book: {
    label: "Book an Appointment",
    iconName: "calendar-check",
    steps: [
      {
        nodeId: "phone",
        label: "Call comes in",
        stepLabel: "A customer dials your business",
        bubble: { who: "caller", text: "Hi! I'd like to book an appointment for next Tuesday." },
      },
      {
        nodeId: "calleem",
        label: "Calleem answers",
        stepLabel: "Calleem picks up and listens",
        bubble: { who: "calleem", text: "Good morning! Of course — morning or afternoon?" },
      },
      {
        nodeId: "cal",
        label: "Checks calendar",
        stepLabel: "Looking up real-time availability",
        bubble: { who: "calleem", text: "One moment, checking Tuesday for you…" },
      },
      {
        nodeId: "book",
        label: "Books the slot",
        stepLabel: "Appointment confirmed and saved",
        bubble: { who: "calleem", text: "10:30 AM is free. Shall I lock it in?" },
      },
      {
        nodeId: "confirm",
        label: "Sends confirmation",
        stepLabel: "SMS and email confirmation dispatched",
        bubble: { who: "calleem", text: "Done — confirmation sent by SMS and email." },
      },
      {
        nodeId: "end",
        label: "Call ends",
        stepLabel: "Customer happy — appointment booked",
        bubble: { who: "caller", text: "Easy. Thanks so much, see you Tuesday!" },
      },
    ],
    wires: [
      { from: "phone", to: "calleem" },
      { from: "calleem", to: "cal" },
      { from: "calleem", to: "book" },
      { from: "calleem", to: "confirm" },
      { from: "end", to: "calleem" },
    ],
    activeWiresByStep: [[], ["phone->calleem"], ["calleem->cal"], ["calleem->book"], ["calleem->confirm"], ["end->calleem"]],
  },
  info: {
    label: "Answer a Question",
    iconName: "chat",
    steps: [
      {
        nodeId: "phone",
        label: "Call comes in",
        stepLabel: "A customer dials your business",
        bubble: { who: "caller", text: "Hi, what time do you close tonight?" },
      },
      {
        nodeId: "calleem",
        label: "Calleem listens",
        stepLabel: "Identifies it's an info request",
        bubble: { who: "calleem", text: "Good evening! Let me check our hours for you." },
      },
      {
        nodeId: "kb",
        label: "Looks it up",
        stepLabel: "Searches the business knowledge base",
        bubble: { who: "calleem", text: "One second, pulling that up now…" },
      },
      {
        nodeId: "answer",
        label: "Replies instantly",
        stepLabel: "Perfect answer delivered on the spot",
        bubble: { who: "calleem", text: "We close at 8 PM tonight. Anything else I can help with?" },
      },
      {
        nodeId: "end",
        label: "Call ends",
        stepLabel: "Customer happy — question answered",
        bubble: { who: "caller", text: "Perfect, thank you. Goodbye!" },
      },
    ],
    wires: [
      { from: "phone", to: "calleem" },
      { from: "kb", to: "calleem" },
      { from: "calleem", to: "answer" },
      { from: "end", to: "calleem" },
    ],
    activeWiresByStep: [[], ["phone->calleem"], ["kb->calleem"], ["calleem->answer"], ["end->calleem"]],
  },
};

const cy = (node: { y: number; h: number }) => node.y + node.h / 2;
const ra = (node: { x: number; w: number; y: number; h: number }) => ({ x: node.x + node.w, y: cy(node) });
const la = (node: { x: number; y: number; h: number }) => ({ x: node.x, y: cy(node) });
const hLA = () => la(NODE_DEFS.calleem);
const hRA = () => ra(NODE_DEFS.calleem);

const bezPath = (f: { x: number; y: number }, t: { x: number; y: number }) => {
  const dx = t.x - f.x;
  return `M${f.x},${f.y} C${f.x + dx * 0.55},${f.y} ${t.x - dx * 0.55},${t.y} ${t.x},${t.y}`;
};

function resolveWire(wire: Wire) {
  const fromNode = NODE_DEFS[wire.from];
  const toNode = NODE_DEFS[wire.to];
  const from = wire.from === "calleem" ? hRA() : ra(fromNode);
  const to = wire.to === "calleem" ? hLA() : la(toNode);
  return { id: `${wire.from}->${wire.to}`, d: bezPath(from, to), startPt: from, endPt: to };
}

function ActivePulse({ d, active }: { d: string; active: boolean }) {
  if (!active) return null;
  return (
    <g style={{ pointerEvents: "none" }}>
      <circle r="9" fill="url(#pGlow)" opacity="0.6">
        <animateMotion dur="2.2s" repeatCount="indefinite" path={d} keyPoints="0;1" keyTimes="0;1" />
      </circle>
      <circle r="2.8" fill={B.white}>
        <animateMotion dur="2.2s" repeatCount="indefinite" path={d} keyPoints="0;1" keyTimes="0;1" />
      </circle>
    </g>
  );
}

const NODE_META: Record<NodeId, { iconName: IconName; title: string; sub: string; isHub?: boolean }> = {
  phone: { iconName: "phone", title: "Business Phone", sub: "incoming call" },
  calleem: { iconName: "user", title: "Calleem", sub: "AI Receptionist", isHub: true },
  cal: { iconName: "calendar-search", title: "Check Calendar", sub: "availability" },
  book: { iconName: "calendar-check", title: "Book Appointment", sub: "saves the slot" },
  confirm: { iconName: "envelope-check", title: "Send Confirmation", sub: "SMS · email" },
  kb: { iconName: "book", title: "Knowledge Base", sub: "business info" },
  answer: { iconName: "chat", title: "Reply to Caller", sub: "instant answer" },
  end: { iconName: "phone-off", title: "Call Ends", sub: "customer happy" },
};

function CalleemLogo({ color }: { color: string }) {
  return (
    <svg
      aria-hidden
      focusable="false"
      style={{ width: 26, height: 18, color }}
      viewBox="0 0 41 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g transform="translate(0 0.5)">
        <path d="M 21.821 0.929 C 22.354 0.38 23.092 0.068 23.865 0.065 L 33.762 0.065 C 40.198 0.065 43.42 8.011 38.869 12.659 L 28.958 22.783 C 28.503 23.247 27.725 22.918 27.725 22.26 L 27.725 13.345 L 28.87 12.174 C 29.78 11.245 29.136 9.656 27.848 9.656 L 13.276 9.656 L 21.821 0.929 Z" fill="currentColor" />
        <path d="M 19.179 22.071 C 18.646 22.62 17.908 22.932 17.135 22.935 L 7.238 22.935 C 0.802 22.935 -2.42 14.988 2.131 10.341 L 12.042 0.217 C 12.497 -0.247 13.276 0.082 13.276 0.739 L 13.276 9.655 L 12.13 10.825 C 11.22 11.755 11.864 13.344 13.152 13.344 L 27.724 13.344 L 19.178 22.071 Z" fill="currentColor" />
      </g>
    </svg>
  );
}

function NodeCard({ nodeId, present, isCurrent }: { nodeId: NodeId; present: boolean; isCurrent: boolean }) {
  const meta = NODE_META[nodeId];
  const def = NODE_DEFS[nodeId];
  if (!meta || !def) return null;
  const { iconName, title, sub, isHub } = meta;

  let bg: string;
  let border: string;
  let iconBg: string;
  let iconBorder: string;
  let iconColor: string;
  let opacity: number;
  let shadow: string;

  if (!present) {
    bg = B.nodeBgIdle;
    border = "rgba(255,255,255,0.04)";
    iconBg = "rgba(255,255,255,0.03)";
    iconBorder = "rgba(255,255,255,0.05)";
    iconColor = "rgba(255,255,255,0.28)";
    opacity = 0.32;
    shadow = "0 4px 12px -8px rgba(0,0,0,0.4)";
  } else if (isCurrent) {
    bg = `linear-gradient(180deg, rgba(6,78,59,0.98) 0%, rgba(5,40,23,0.98) 100%)`;
    border = "rgba(27,133,80,0.95)";
    iconBg = `linear-gradient(180deg, rgba(44,122,68,0.96), rgba(8,46,36,0.98))`;
    iconBorder = "rgba(27,133,80,0.95)";
    iconColor = B.white;
    opacity = 1;
    shadow = "0 0 0 1px rgba(27,133,80,0.16), 0 0 0 6px rgba(27,133,80,0.08), 0 0 34px rgba(6,78,59,0.42), 0 18px 30px -12px rgba(0,0,0,0.48)";
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
    <foreignObject x={def.x} y={def.y} width={def.w} height={def.h} style={{ overflow: "visible" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: isHub ? 18 : 14,
          background: bg,
          border: `1px solid ${border}`,
          boxShadow: shadow,
          padding: isHub ? "14px 16px" : "12px 14px",
          display: "flex",
          flexDirection: isHub ? "column" : "row",
          alignItems: "center",
          justifyContent: isHub ? "center" : "flex-start",
          gap: isHub ? 8 : 12,
          textAlign: isHub ? "center" : "left",
          opacity,
          transition: "background 0.5s, border 0.5s, box-shadow 0.5s, opacity 0.5s",
          fontFamily: FONT_SANS,
          position: "relative",
          overflow: "visible",
        }}
      >
        {isCurrent && (
          <div
            aria-hidden
            style={{
              position: "absolute",
              top: -40,
              right: -42,
              width: 150,
              height: 150,
              borderRadius: "9999px",
              background: "rgba(108,141,112,0.24)",
              filter: "blur(44px)",
              pointerEvents: "none",
              zIndex: 0,
            }}
          />
        )}
        {nodeId === "calleem" ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, position: "relative", zIndex: 1 }}>
            <div
              style={{
                width: 54,
                height: 38,
                borderRadius: 12,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: iconBg,
                border: `1px solid ${iconBorder}`,
                color: iconColor,
                transition: "background 0.5s, border 0.5s, color 0.5s",
                boxShadow: isCurrent ? "0 0 0 1px rgba(255,255,255,0.04) inset" : "none",
              }}
            >
              <CalleemLogo color={iconColor} />
            </div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 800,
                color: B.white,
                letterSpacing: "-0.04em",
                transform: "skewX(-8deg)",
                fontStyle: "italic",
                fontFamily: FONT_DISPLAY,
                lineHeight: 1,
              }}
            >
              CALLEEM
            </div>
          </div>
        ) : (
          <>
            <div
              style={{
                width: isHub ? 44 : 36,
                height: isHub ? 44 : 36,
                borderRadius: isHub ? 11 : 9,
                flexShrink: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: iconBg,
                border: `1px solid ${iconBorder}`,
                color: iconColor,
                transition: "background 0.5s, border 0.5s, color 0.5s",
                position: "relative",
                zIndex: 1,
              }}
            >
              <Icon name={iconName} size={isHub ? 22 : 17} />
            </div>
            <div style={{ minWidth: 0, display: "flex", flexDirection: "column", gap: 3, position: "relative", zIndex: 1 }}>
              <div
                style={{
                  fontSize: isHub ? 15 : 13.5,
                  fontWeight: 600,
                  color: B.white,
                  letterSpacing: "0.005em",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  fontFamily: FONT_DISPLAY,
                }}
              >
                {title}
              </div>
              <div
                style={{
                  fontSize: 10.5,
                  color: "rgba(255,255,255,0.55)",
                  textTransform: "uppercase",
                  letterSpacing: "0.10em",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  fontWeight: 500,
                  fontFamily: FONT_SANS,
                }}
              >
                {sub}
              </div>
            </div>
          </>
        )}
      </div>
    </foreignObject>
  );
}

function ChatBubble({ bubble, visible }: { bubble: Bubble; visible: boolean }) {
  if (!bubble) return null;
  const isCaller = bubble.who === "caller";
  return (
    <div
      style={{
        position: "absolute",
        bottom: 30,
        left: isCaller ? 26 : "auto",
        right: isCaller ? "auto" : 26,
        maxWidth: 300,
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(6px)",
        transition: "opacity 0.4s, transform 0.4s",
        pointerEvents: "none",
        zIndex: 10,
        fontFamily: FONT_SANS,
      }}
    >
      <div
        style={{
          borderRadius: 14,
          borderBottomLeftRadius: isCaller ? 4 : 14,
          borderBottomRightRadius: isCaller ? 14 : 4,
          background: isCaller ? "rgba(255,255,255,0.07)" : "rgba(28,138,79,0.32)",
          border: `1px solid ${isCaller ? "rgba(255,255,255,0.12)" : "rgba(35,165,90,0.4)"}`,
          padding: "10px 14px",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          style={{
            fontSize: 9.5,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            fontWeight: 600,
            color: isCaller ? "rgba(255,255,255,0.42)" : B.greenLight,
            marginBottom: 5,
            fontFamily: FONT_SANS,
          }}
        >
          {isCaller ? "Caller" : "Calleem"}
        </div>
        <div
          style={{
            fontSize: 13,
            lineHeight: 1.55,
            color: isCaller ? "rgba(255,255,255,0.88)" : "#c8f0d8",
            fontFamily: FONT_SANS,
            fontStyle: "italic",
          }}
        >
          “{bubble.text}”
        </div>
      </div>
    </div>
  );
}

function StepStrip({ steps, currentStep, onStep }: { steps: Step[]; currentStep: number; onStep: (i: number) => void }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, marginBottom: 22 }}>
      {steps.map((step, index) => {
        const done = index < currentStep;
        const cur = index === currentStep;
        return (
          <div key={step.label} style={{ display: "flex", alignItems: "center" }}>
            <button
              onClick={() => onStep(index)}
              title={step.stepLabel}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 7,
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "3px 4px",
              }}
            >
              <div
                style={{
                  width: cur ? 12 : 8,
                  height: cur ? 12 : 8,
                  borderRadius: "50%",
                  background: cur ? B.greenLight : done ? B.greenBright : "rgba(255,255,255,0.28)",
                  boxShadow: cur ? "0 0 0 5px rgba(63,200,120,0.22)" : "none",
                  transition: "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
              />
              <div
                style={{
                  fontSize: 9.5,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  color: cur ? B.white : done ? "rgba(255,255,255,0.78)" : "rgba(255,255,255,0.45)",
                  fontFamily: FONT_SANS,
                  fontWeight: cur ? 600 : 500,
                  maxWidth: 88,
                  textAlign: "center",
                  lineHeight: 1.35,
                  whiteSpace: "normal",
                  transition: "color 0.4s",
                }}
              >
                {step.label}
              </div>
            </button>
            {index < steps.length - 1 && (
              <div
                style={{
                  width: 34,
                  height: 1.5,
                  background: done ? B.greenBright : "rgba(255,255,255,0.16)",
                  marginBottom: 24,
                  marginLeft: 4,
                  marginRight: 4,
                  flexShrink: 0,
                  transition: "background 0.4s",
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function CallPipelineBox() {
  const [scenarioId, setScenarioId] = useState<ScenarioId>("book");
  const [stepIdx, setStepIdx] = useState(0);
  const [bubbleVis, setBubbleVis] = useState(true);
  const timerRef = useRef<number | null>(null);

  const scenario = SCENARIOS[scenarioId];
  const steps = scenario.steps;
  const total = steps.length;
  const currentStep = steps[stepIdx];
  const activeWires = scenario.activeWiresByStep[stepIdx] || [];
  const wires = scenario.wires.map(resolveWire);

  const advance = useCallback(() => {
    setBubbleVis(false);
    window.setTimeout(() => {
      setStepIdx((current) => (current + 1) % steps.length);
      setBubbleVis(true);
    }, 380);
  }, [steps.length]);

  useEffect(() => {
    timerRef.current = window.setInterval(advance, 3600);
    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [advance]);

  function switchScenario(id: ScenarioId) {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
    }
    setScenarioId(id);
    setStepIdx(0);
    setBubbleVis(true);
  }

  function goToStep(i: number) {
    setBubbleVis(false);
    window.setTimeout(() => {
      setStepIdx(i);
      setBubbleVis(true);
    }, 200);
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
    }
    timerRef.current = window.setInterval(advance, 3600);
  }

  const scenarioNodes = new Set<NodeId>(scenario.steps.map((step) => step.nodeId));
  scenarioNodes.add("calleem");
  const currentNodeId = currentStep.nodeId;

  return (
    <div style={{ width: "100%", fontFamily: FONT_SANS }}>
      <div style={{ display: "flex", justifyContent: "center", gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
        {Object.entries(SCENARIOS).map(([id, sc]) => {
          const selected = id === scenarioId;
          return (
            <button
              key={id}
              onClick={() => switchScenario(id as ScenarioId)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                fontFamily: FONT_SANS,
                fontSize: 13,
                fontWeight: 600,
                letterSpacing: "0.005em",
                padding: "10px 22px",
                borderRadius: 999,
                border: selected ? `1.5px solid ${B.greenBright}` : "1.5px solid rgba(255,255,255,0.22)",
                background: selected ? B.green : "rgba(255,255,255,0.06)",
                color: B.white,
                cursor: "pointer",
                boxShadow: selected ? "0 6px 20px -6px rgba(35,165,90,0.55)" : "none",
                transition: "all 0.25s",
              }}
            >
              <Icon name={sc.iconName} size={15} />
              {sc.label}
            </button>
          );
        })}
      </div>

      <StepStrip steps={steps} currentStep={stepIdx} onStep={goToStep} />

      <div
        style={{
          position: "relative",
          borderRadius: 28,
          overflow: "hidden",
          background: `linear-gradient(165deg, ${B.cardBgMid} 0%, ${B.cardBg} 60%, #4f6f57 100%)`,
          border: "1px solid rgba(255,255,255,0.18)",
          boxShadow: "0 1px 0 rgba(255,255,255,0.08) inset, 0 28px 56px -34px rgba(40,60,46,0.55)",
          minHeight: 420,
        }}
      >
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            opacity: 0.28,
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px)",
            backgroundSize: "48px 48px",
            transform: "perspective(900px) rotateX(60deg)",
            transformOrigin: "top",
          }}
        />
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            background: "radial-gradient(ellipse at 50% 0%, rgba(63,200,120,0.22) 0%, transparent 65%)",
          }}
        />
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            backgroundImage: `radial-gradient(ellipse at 50% 45%, ${B.greenGlow} 0%, transparent 60%)`,
          }}
        />

        <div
          style={{
            position: "absolute",
            top: 18,
            left: "50%",
            transform: "translateX(-50%)",
            fontSize: 10.5,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "rgba(255,255,255,0.62)",
            fontWeight: 600,
            whiteSpace: "nowrap",
            opacity: bubbleVis ? 1 : 0.4,
            transition: "opacity 0.4s",
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontFamily: FONT_SANS,
          }}
        >
          <span style={{ color: B.greenLight }}>
            <Icon name="play" size={9} />
          </span>
          {currentStep.stepLabel}
        </div>

        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          style={{ width: "100%", height: "auto", display: "block", position: "relative" }}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <radialGradient id="pGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={B.white} stopOpacity="1" />
              <stop offset="40%" stopColor={B.greenLight} stopOpacity="0.75" />
              <stop offset="100%" stopColor={B.green} stopOpacity="0" />
            </radialGradient>
          </defs>

          {wires.map((wire) => (
            <path key={`${wire.id}-b`} d={wire.d} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={1} />
          ))}

          {wires.map((wire) => {
            const isOn = activeWires.includes(wire.id);
            return (
              <path
                key={`${wire.id}-a`}
                d={wire.d}
                fill="none"
                stroke={isOn ? B.greenLight : "transparent"}
                strokeWidth={isOn ? 1.8 : 0}
                opacity={isOn ? 0.75 : 0}
                style={{ transition: "opacity 0.5s, stroke-width 0.5s" }}
              />
            );
          })}

          {wires.map((wire) => (
            <g key={`anc-${wire.id}`}>
              <circle cx={wire.startPt.x} cy={wire.startPt.y} r={2.5} fill={B.white} opacity={0.32} />
              <circle cx={wire.endPt.x} cy={wire.endPt.y} r={2.5} fill={B.white} opacity={0.32} />
            </g>
          ))}

          {wires.map((wire) => (
            <ActivePulse key={`${wire.id}-pulse`} d={wire.d} active={activeWires.includes(wire.id)} />
          ))}

          <NodeCard nodeId="calleem" present isCurrent={currentNodeId === "calleem"} />
          {[...scenarioNodes]
            .filter((id) => id !== "calleem")
            .map((id) => (
              <NodeCard key={id} nodeId={id} present isCurrent={currentNodeId === id} />
            ))}
        </svg>

        <ChatBubble bubble={currentStep.bubble} visible={bubbleVis} />
      </div>

      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 18, marginTop: 24 }}>
        <button
          onClick={() => goToStep((stepIdx - 1 + total) % total)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            fontFamily: FONT_SANS,
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: "0.02em",
            padding: "9px 20px",
            borderRadius: 999,
            border: "1.5px solid rgba(255,255,255,0.22)",
            background: "rgba(255,255,255,0.06)",
            color: B.white,
            cursor: "pointer",
            transition: "all 0.2s",
          }}
        >
          <Icon name="arrow-left" size={13} /> Back
        </button>
        <span
          style={{
            fontSize: 11,
            letterSpacing: "0.16em",
            textTransform: "uppercase",
            color: "rgba(255,255,255,0.7)",
            fontWeight: 600,
            fontFamily: FONT_SANS,
          }}
        >
          {stepIdx + 1} / {total}
        </span>
        <button
          onClick={() => goToStep((stepIdx + 1) % total)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            fontFamily: FONT_SANS,
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: "0.02em",
            padding: "9px 22px",
            borderRadius: 999,
            border: `1.5px solid ${B.greenBright}`,
            background: B.green,
            color: B.white,
            cursor: "pointer",
            transition: "all 0.2s",
            boxShadow: "0 6px 20px -6px rgba(35,165,90,0.55)",
          }}
        >
          Next <Icon name="arrow-right" size={13} />
        </button>
      </div>
    </div>
  );
}
