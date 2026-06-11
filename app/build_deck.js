const pptxgen = require("pptxgenjs");
const path = require("path");

const DOCS = path.join(__dirname, "..", "..", "docs");
const OUT  = path.join(__dirname, "..", "..", "Momentum_ManOxCo_LCS.pptx");

// ── Palette ───────────────────────────────────────────────────────────────────
const C = {
  darkBg:    "0A1628",   // near-black navy
  darkCard:  "132035",   // slightly lighter card on dark
  midBg:     "0D2137",   // mid-dark for accents
  lightBg:   "F7F9FC",   // near-white content slides
  white:     "FFFFFF",
  iceBlue:   "4BBFE8",   // primary accent
  teal:      "0FA3B1",   // secondary accent
  red:       "E84855",   // alert / danger
  orange:    "F4812B",   // warning
  green:     "2EC27E",   // safe / positive
  darkText:  "1A2B3C",   // body on light bg
  mutedText: "64748B",   // secondary on light bg
  lightText: "94A3B8",   // muted on dark bg
};

// ── Helpers ───────────────────────────────────────────────────────────────────
const makeShadow = () => ({
  type: "outer", color: "000000", opacity: 0.18, blur: 8, offset: 3, angle: 135
});

const cardShadow = () => ({
  type: "outer", color: "000000", opacity: 0.1, blur: 6, offset: 2, angle: 135
});

function darkSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: C.darkBg };
  return s;
}

function lightSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };
  return s;
}

// Thin ice-blue rule across the top of light slides
function topRule(s) {
  s.addShape("rect", { x: 0, y: 0, w: 10, h: 0.045, fill: { color: C.iceBlue }, line: { color: C.iceBlue } });
}

// Section label chip
function chip(s, label, x, y) {
  s.addShape("rect", { x, y, w: 1.7, h: 0.26, fill: { color: C.iceBlue }, line: { color: C.iceBlue }, rectRadius: 0 });
  s.addText(label.toUpperCase(), { x, y, w: 1.7, h: 0.26, fontSize: 7.5, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0 });
}

function slideTitle(s, text, y = 0.42) {
  s.addText(text, { x: 0.5, y, w: 9, h: 0.62, fontSize: 28, bold: true, color: C.darkText, fontFace: "Georgia" });
}

function slideTitleLight(s, text, y = 0.42) {
  s.addText(text, { x: 0.5, y, w: 9, h: 0.62, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia" });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Cover
// ════════════════════════════════════════════════════════════════════════════
function slide01_cover(pres) {
  const s = darkSlide(pres);

  // Background circles (atmosphere)
  s.addShape("ellipse", { x: 6.5, y: -1.2, w: 5, h: 5, fill: { color: C.iceBlue, transparency: 88 }, line: { color: C.iceBlue, transparency: 88 } });
  s.addShape("ellipse", { x: -1.5, y: 2.8, w: 4, h: 4, fill: { color: C.teal, transparency: 90 }, line: { color: C.teal, transparency: 90 } });

  // Firm name
  s.addText("LUMINAE INTELLIGENCE", {
    x: 0.7, y: 1.4, w: 8.6, h: 0.75,
    fontSize: 38, bold: true, color: C.iceBlue, fontFace: "Georgia",
    charSpacing: 3,
  });

  // Thin separator line
  s.addShape("rect", { x: 0.7, y: 2.22, w: 5.5, h: 0.028, fill: { color: C.iceBlue, transparency: 40 }, line: { color: C.iceBlue, transparency: 40 } });

  // Product name
  s.addText("Liquid Control System", {
    x: 0.7, y: 2.35, w: 8.6, h: 0.58,
    fontSize: 26, bold: false, color: C.white, fontFace: "Georgia", italic: true,
  });

  // Programme
  s.addText("ManOxCo Oxygen Reliability Transformation · PI-1", {
    x: 0.7, y: 2.98, w: 8.6, h: 0.38,
    fontSize: 13, color: C.lightText, fontFace: "Calibri",
  });

  // Tagline
  s.addText("From Signal to Safety.", {
    x: 0.7, y: 4.05, w: 8.6, h: 0.5,
    fontSize: 16, italic: true, color: C.iceBlue, fontFace: "Georgia",
  });

  // Date / confidential
  s.addText("May 2026  ·  Confidential", {
    x: 0.7, y: 5.1, w: 8.6, h: 0.3,
    fontSize: 9.5, color: C.lightText, fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — The Incident
// ════════════════════════════════════════════════════════════════════════════
function slide02_incident(pres) {
  const s = darkSlide(pres);

  // Background atmosphere
  s.addShape("ellipse", { x: 5.5, y: 1.5, w: 6, h: 6, fill: { color: C.red, transparency: 92 }, line: { color: C.red, transparency: 92 } });

  // Date pill
  s.addShape("rect", { x: 0.65, y: 0.55, w: 2.2, h: 0.44, fill: { color: C.red }, line: { color: C.red } });
  s.addText("01 JANUARY 2025", { x: 0.65, y: 0.55, w: 2.2, h: 0.44, fontSize: 9, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

  // Main quote
  s.addText([
    { text: '"A patient died\n', options: { breakLine: true } },
    { text: "because no system existed\n", options: { breakLine: true } },
    { text: 'to see it coming."', options: {} },
  ], {
    x: 0.65, y: 1.1, w: 8.7, h: 2.5,
    fontSize: 33, color: C.white, fontFace: "Georgia", italic: true, valign: "top",
  });

  // Timeline line
  s.addShape("rect", { x: 0.65, y: 3.88, w: 8.7, h: 0.025, fill: { color: C.lightText, transparency: 60 }, line: { color: C.lightText, transparency: 60 } });
  // Red dot
  s.addShape("ellipse", { x: 4.7, y: 3.73, w: 0.3, h: 0.3, fill: { color: C.red }, line: { color: C.red } });

  // Three cause pills below timeline
  const causes = ["Unauthorised maintenance shutdown", "Distribution interrupted → Madrid", "Tanks depleted · No warning issued"];
  causes.forEach((c, i) => {
    const x = 0.55 + i * 3.18;
    s.addShape("rect", { x, y: 4.12, w: 2.9, h: 0.72, fill: { color: C.darkCard }, line: { color: C.iceBlue, transparency: 60, width: 0.5 } });
    s.addText(c, { x, y: 4.12, w: 2.9, h: 0.72, fontSize: 9.5, color: C.lightText, align: "center", valign: "middle", fontFace: "Calibri", margin: 4 });
  });

  // Bottom label
  s.addText("The incident was not a black swan. It was a predictable failure with no system to catch it.", {
    x: 0.65, y: 5.1, w: 8.7, h: 0.35,
    fontSize: 9.5, color: C.lightText, italic: true, fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — What We Found
// ════════════════════════════════════════════════════════════════════════════
function slide03_findings(pres) {
  const s = darkSlide(pres);

  s.addShape("ellipse", { x: 2, y: -0.5, w: 8, h: 8, fill: { color: C.iceBlue, transparency: 92 }, line: { color: C.iceBlue, transparency: 92 } });

  // Label
  chip(s, "2024 Diagnostic", 0.55, 0.45);

  // Big number
  s.addText("1,781", {
    x: 0.5, y: 0.95, w: 9, h: 2.4,
    fontSize: 110, bold: true, color: C.iceBlue, fontFace: "Georgia", align: "center",
  });
  s.addText("CRITICAL RISK EVENTS DETECTED IN 2024", {
    x: 0.5, y: 3.3, w: 9, h: 0.5,
    fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", align: "center", charSpacing: 2,
  });

  // Three stat cards
  const stats = [
    { num: "8",  label: "hospitals with ≥1\ncritical day" },
    { num: "2",  label: "plants with overdue\nmaintenance" },
    { num: "0",  label: "integrated systems\nmonitoring this" },
  ];
  stats.forEach((st, i) => {
    const x = 1.15 + i * 2.8;
    s.addShape("rect", { x, y: 4.15, w: 2.4, h: 1.1, fill: { color: C.darkCard }, line: { color: C.iceBlue, transparency: 55, width: 0.5 }, shadow: cardShadow() });
    s.addText(st.num, { x, y: 4.18, w: 2.4, h: 0.55, fontSize: 32, bold: true, color: C.iceBlue, align: "center", fontFace: "Georgia" });
    s.addText(st.label, { x, y: 4.72, w: 2.4, h: 0.48, fontSize: 9, color: C.lightText, align: "center", fontFace: "Calibri", margin: 2 });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — Who Is Momentum
// ════════════════════════════════════════════════════════════════════════════
function slide04_luminae(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "About Us", 0.5, 0.13);
  slideTitle(s, "Who Is Momentum");

  // Left column - description
  s.addText("AI-native European consultancy.\nWe don't recommend AI — we ship it.", {
    x: 0.5, y: 1.2, w: 4.3, h: 0.85,
    fontSize: 14, color: C.darkText, fontFace: "Georgia", italic: true, valign: "top",
  });
  s.addText("Founded 2019 by former CERN physicists, DeepMind engineers, and industrial operations directors. 340 consultants across 8 European offices.", {
    x: 0.5, y: 2.15, w: 4.3, h: 0.85,
    fontSize: 11, color: C.mutedText, fontFace: "Calibri",
  });

  // Divider
  s.addShape("rect", { x: 0.5, y: 3.0, w: 4.3, h: 0.025, fill: { color: C.iceBlue, transparency: 40 }, line: { color: C.iceBlue, transparency: 40 } });

  // Differentiator rows
  const diffs = [
    ["Traditional consulting", "Momentum"],
    ["Strategy → handoff", "Strategy + build + operate"],
    ["Monthly reports", "Real-time intelligence"],
    ["Recommends AI", "Ships AI"],
  ];
  s.addText("Traditional", { x: 0.55, y: 3.1, w: 2.0, h: 0.28, fontSize: 9.5, bold: true, color: C.mutedText, fontFace: "Calibri" });
  s.addText("Momentum", { x: 2.75, y: 3.1, w: 2.0, h: 0.28, fontSize: 9.5, bold: true, color: C.teal, fontFace: "Calibri" });
  diffs.slice(1).forEach((row, i) => {
    const y = 3.42 + i * 0.38;
    s.addShape("rect", { x: 0.5, y: y - 0.04, w: 4.3, h: 0.35, fill: { color: i % 2 === 0 ? "EFF6FF" : C.lightBg }, line: { color: C.lightBg } });
    s.addText(row[0], { x: 0.6, y, w: 2.0, h: 0.28, fontSize: 10, color: C.mutedText, fontFace: "Calibri" });
    s.addText(row[1], { x: 2.7, y, w: 2.1, h: 0.28, fontSize: 10, bold: true, color: C.darkText, fontFace: "Calibri" });
  });

  // Right column - 3 pillars
  const pillars = [
    { color: C.iceBlue, title: "AI-Native", body: "Intelligence is the foundation, not a feature added on top" },
    { color: C.teal,    title: "SIGNAL Methodology", body: "From raw sensor to operational decision in under 6 minutes" },
    { color: C.green,   title: "Proven at Scale", body: "Pharma cold chains · National energy grids · Hospital ICU networks" },
  ];
  pillars.forEach((p, i) => {
    const y = 1.15 + i * 1.42;
    s.addShape("rect", { x: 5.3, y, w: 4.1, h: 1.2, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 }, shadow: cardShadow() });
    s.addShape("rect", { x: 5.3, y, w: 0.07, h: 1.2, fill: { color: p.color }, line: { color: p.color } });
    s.addText(p.title, { x: 5.5, y: y + 0.18, w: 3.8, h: 0.32, fontSize: 13, bold: true, color: C.darkText, fontFace: "Georgia" });
    s.addText(p.body, { x: 5.5, y: y + 0.5, w: 3.8, h: 0.55, fontSize: 10.5, color: C.mutedText, fontFace: "Calibri" });
  });

  // Tagline
  s.addText('"We don\'t predict the future. We prevent the worst of it."', {
    x: 0.5, y: 5.1, w: 9, h: 0.32,
    fontSize: 10.5, italic: true, color: C.teal, fontFace: "Georgia",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — SIGNAL Framework
// ════════════════════════════════════════════════════════════════════════════
function slide05_signal(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Methodology", 0.5, 0.13);
  slideTitle(s, "The SIGNAL Framework");

  const steps = [
    { letter: "S", name: "SENSE",     desc: "Connect all data sources — IoT PLCs, ERP exports, hospital systems",    color: "1D4ED8" },
    { letter: "I", name: "INTEGRATE", desc: "Cleanse, unify, and model — Bronze → Silver → Gold medallion layers",   color: C.teal },
    { letter: "G", name: "GENERATE",  desc: "Build dry-out risk models, financial marts, and demand forecasts",       color: C.green },
    { letter: "N", name: "NAVIGATE",  desc: "Deploy the LCS AI Copilot for real-time decision intelligence",          color: "7C3AED" },
    { letter: "A", name: "ALERT",     desc: "Real-time critical threshold notifications — mean time to alert < 6 min", color: C.orange },
    { letter: "L", name: "LEARN",     desc: "Continuous model improvement on live production data",                   color: C.iceBlue },
  ];

  steps.forEach((st, i) => {
    const col = i < 3 ? 0 : 1;
    const row = i % 3;
    const x = 0.45 + col * 4.85;
    const y = 1.22 + row * 1.35;

    s.addShape("rect", { x, y, w: 4.45, h: 1.18, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 }, shadow: cardShadow() });
    // Letter circle
    s.addShape("ellipse", { x: x + 0.15, y: y + 0.22, w: 0.72, h: 0.72, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.letter, { x: x + 0.15, y: y + 0.22, w: 0.72, h: 0.72, fontSize: 22, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Georgia", margin: 0 });
    // Name + desc
    s.addText(st.name, { x: x + 1.02, y: y + 0.13, w: 3.3, h: 0.33, fontSize: 12, bold: true, color: C.darkText, fontFace: "Calibri" });
    s.addText(st.desc, { x: x + 1.02, y: y + 0.48, w: 3.3, h: 0.58, fontSize: 9.5, color: C.mutedText, fontFace: "Calibri" });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — Dry-out Risk
// ════════════════════════════════════════════════════════════════════════════
function slide06_risk(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Risk Model", 0.5, 0.13);
  slideTitle(s, "What 2024 Looked Like");

  // Left: explanation + tiers
  s.addText("The fill-level model estimates real storage per hospital every day — refills minus consumption, cumulatively.", {
    x: 0.5, y: 1.22, w: 4.1, h: 0.75,
    fontSize: 11, color: C.mutedText, fontFace: "Calibri",
  });

  const tiers = [
    { level: "CRITICAL", cond: "< 12%  fill", action: "Dispatch truck now",         color: C.red },
    { level: "HIGH",     cond: "< 24%  fill", action: "Urgent refill within 24h",   color: C.orange },
    { level: "MEDIUM",   cond: "< 50%  fill", action: "Planned refill within 72h",  color: "EAB308" },
    { level: "LOW",      cond: "≥ 50%  fill", action: "Normal schedule",            color: C.green },
  ];
  tiers.forEach((t, i) => {
    const y = 2.08 + i * 0.74;
    s.addShape("rect", { x: 0.5, y, w: 4.1, h: 0.62, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 } });
    s.addShape("rect", { x: 0.5, y, w: 0.06, h: 0.62, fill: { color: t.color }, line: { color: t.color } });
    s.addText(t.level, { x: 0.7, y: y + 0.05, w: 1.1, h: 0.24, fontSize: 9.5, bold: true, color: t.color, fontFace: "Calibri" });
    s.addText(t.cond,  { x: 0.7, y: y + 0.3, w: 1.1, h: 0.24, fontSize: 9, color: C.mutedText, fontFace: "Calibri" });
    s.addText(t.action,{ x: 1.9, y: y + 0.16, w: 2.6, h: 0.3, fontSize: 10, color: C.darkText, fontFace: "Calibri", valign: "middle" });
  });

  // Key callout
  s.addShape("rect", { x: 0.5, y: 5.1, w: 4.1, h: 0.35, fill: { color: "FFF1F2" }, line: { color: C.red, transparency: 50, width: 0.5 } });
  s.addText("LCS would have issued a Madrid alert 72h before the January incident.", {
    x: 0.6, y: 5.1, w: 4.0, h: 0.35, fontSize: 9, color: C.red, fontFace: "Calibri", valign: "middle",
  });

  // Right: chart image
  s.addImage({ path: `${DOCS}/fig_dryout_risk.png`, x: 4.8, y: 1.0, w: 4.9, h: 4.4, sizing: { type: "contain", w: 4.9, h: 4.4 } });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Demo Transition
// ════════════════════════════════════════════════════════════════════════════
function slide07_demo(pres) {
  const s = darkSlide(pres);

  s.addShape("ellipse", { x: 3.5, y: 0.5, w: 7, h: 7, fill: { color: C.teal, transparency: 90 }, line: { color: C.teal, transparency: 90 } });

  s.addText("LIVE DEMO", {
    x: 0.5, y: 0.8, w: 9, h: 0.52,
    fontSize: 13, bold: true, color: C.iceBlue, fontFace: "Calibri", align: "center", charSpacing: 5,
  });
  s.addText("The LCS Copilot", {
    x: 0.5, y: 1.45, w: 9, h: 1.0,
    fontSize: 52, bold: true, color: C.white, fontFace: "Georgia", align: "center",
  });
  s.addText('"Let me show you what your operations director sees every morning."', {
    x: 1.0, y: 2.65, w: 8, h: 0.6,
    fontSize: 16, italic: true, color: C.lightText, fontFace: "Georgia", align: "center",
  });

  // Three demo question cards
  const qs = [
    "Give me the\nmorning briefing.",
    "Which hospitals need\na truck today?",
    "What happens to margins if\nBarcelona shuts down?",
  ];
  qs.forEach((q, i) => {
    const x = 0.5 + i * 3.17;
    s.addShape("rect", { x, y: 3.6, w: 2.95, h: 1.5, fill: { color: C.darkCard }, line: { color: C.iceBlue, transparency: 50, width: 0.5 }, shadow: cardShadow() });
    s.addText(`${i + 1}`, { x, y: 3.65, w: 2.95, h: 0.42, fontSize: 20, bold: true, color: C.iceBlue, align: "center", fontFace: "Georgia" });
    s.addText(q, { x, y: 4.1, w: 2.95, h: 0.9, fontSize: 10.5, color: C.lightText, align: "center", fontFace: "Calibri", margin: 6 });
  });

  s.addText("The Copilot reasons across domains — it doesn't just retrieve data.", {
    x: 0.5, y: 5.22, w: 9, h: 0.3,
    fontSize: 9.5, color: C.lightText, italic: true, fontFace: "Calibri", align: "center",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Risk Evolution
// ════════════════════════════════════════════════════════════════════════════
function slide08_evolution(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Risk Analysis", 0.5, 0.13);
  slideTitle(s, "A Pattern, Not a Single Event");

  s.addText("The top 5 highest-risk hospitals crossed the CRITICAL threshold repeatedly throughout 2024 — long before the January 2025 incident.", {
    x: 0.5, y: 1.12, w: 9, h: 0.55,
    fontSize: 11, color: C.mutedText, fontFace: "Calibri",
  });

  s.addImage({ path: `${DOCS}/fig_risk_evolution.png`, x: 0.4, y: 1.75, w: 9.2, h: 3.6, sizing: { type: "contain", w: 9.2, h: 3.6 } });

  s.addShape("rect", { x: 0.5, y: 5.16, w: 9, h: 0.32, fill: { color: "FFF1F2" }, line: { color: C.red, transparency: 55, width: 0.5 } });
  s.addText("The current delivery schedule does not respond to consumption variability. LCS changes that.", {
    x: 0.6, y: 5.16, w: 8.8, h: 0.32, fontSize: 9.5, color: C.red, fontFace: "Calibri", valign: "middle",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — 18-Month Forecast
// ════════════════════════════════════════════════════════════════════════════
function slide09_forecast(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Demand Forecast", 0.5, 0.13);
  slideTitle(s, "18-Month Operational Forecast");

  // Three stat boxes
  const stats = [
    { val: "+4.2%",  label: "demand growth\nover 18 months",   color: C.iceBlue },
    { val: "8%",     label: "supply headroom\nduring maintenance", color: C.orange },
    { val: "−3%",    label: "headroom if two plants\nshut down simultaneously", color: C.red },
  ];
  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.1;
    s.addShape("rect", { x, y: 1.1, w: 2.8, h: 1.1, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 }, shadow: cardShadow() });
    s.addShape("rect", { x, y: 1.1, w: 2.8, h: 0.055, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.val, { x, y: 1.22, w: 2.8, h: 0.5, fontSize: 28, bold: true, color: st.color, align: "center", fontFace: "Georgia" });
    s.addText(st.label, { x, y: 1.74, w: 2.8, h: 0.42, fontSize: 9.5, color: C.mutedText, align: "center", fontFace: "Calibri", margin: 2 });
  });

  s.addImage({ path: `${DOCS}/fig_demand_forecast.png`, x: 0.4, y: 2.32, w: 9.2, h: 2.95, sizing: { type: "contain", w: 9.2, h: 2.95 } });

  s.addText("Maintenance sequencing is not optional — it is a safety constraint.", {
    x: 0.5, y: 5.27, w: 9, h: 0.27,
    fontSize: 10, bold: true, italic: true, color: C.teal, fontFace: "Georgia",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 10 — Maintenance Schedule
// ════════════════════════════════════════════════════════════════════════════
function slide10_maintenance(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Maintenance Planning", 0.5, 0.13);
  slideTitle(s, "Plant Maintenance — Sequenced for Safety");

  // Table
  const rows = [
    [{ text: "Plant",       options: { bold: true, fill: { color: C.darkBg }, color: C.white } },
     { text: "Last Shutdown",options: { bold: true, fill: { color: C.darkBg }, color: C.white } },
     { text: "Status",      options: { bold: true, fill: { color: C.darkBg }, color: C.white } },
     { text: "Recommended Window", options: { bold: true, fill: { color: C.darkBg }, color: C.white } }],
    ["Barcelona", "Aug 2023",
     { text: "OVERDUE", options: { bold: true, color: C.red } },
     "Jul 2026 → reroute to Madrid + Zaragoza"],
    ["Zaragoza",  "Jun 2023",
     { text: "DUE SOON", options: { bold: true, color: C.orange } },
     "Sep 2026 → reroute to Barcelona + Alicante"],
    ["Alicante",  "Dec 2023",
     { text: "OK",       options: { color: C.green } },
     "Dec 2026"],
    ["Gijon",     "Oct 2023",
     { text: "OK",       options: { color: C.green } },
     "Oct 2026"],
    ["Madrid",    "Jan 2025",
     { text: "OK",       options: { color: C.green } },
     "Jan 2027 (as planned)"],
  ];

  s.addTable(rows, {
    x: 0.5, y: 1.15, w: 9.0, colW: [1.6, 1.6, 1.4, 4.4],
    border: { pt: 0.5, color: "E2E8F0" },
    fill: { color: C.white },
    fontFace: "Calibri", fontSize: 10.5,
    align: "left", valign: "middle",
    rowH: 0.42,
  });

  s.addImage({ path: `${DOCS}/fig_maintenance_schedule.png`, x: 0.4, y: 3.78, w: 9.2, h: 1.65, sizing: { type: "contain", w: 9.2, h: 1.65 } });

  s.addShape("rect", { x: 0.5, y: 5.44, w: 9, h: 0.14, fill: { color: "EFF6FF" }, line: { color: C.iceBlue, transparency: 55, width: 0.5 } });
  s.addText("LCS enforces the no-overlap safety rule automatically when scheduling maintenance windows.", {
    x: 0.6, y: 5.44, w: 8.8, h: 0.14, fontSize: 8.5, color: C.teal, fontFace: "Calibri", valign: "middle",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 11 — Financial Intelligence
// ════════════════════════════════════════════════════════════════════════════
function slide11_finance(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Financial Intelligence", 0.5, 0.13);
  slideTitle(s, "Financial Margin Analysis");

  s.addImage({ path: `${DOCS}/fig_financial_margin.png`, x: 0.4, y: 1.1, w: 6.2, h: 3.3, sizing: { type: "contain", w: 6.2, h: 3.3 } });

  // Insight cards (right column)
  const insights = [
    { color: C.green,  title: "Zaragoza",     body: "Highest margin % — currently underutilised. Best efficiency: €105/ton energy cost." },
    { color: C.red,    title: "Madrid risk",   body: "Highest revenue concentration. Single-point-of-failure — the January incident proved this." },
    { color: C.iceBlue,title: "Recommendation",body: "Rebalance 15% of Madrid routes to Zaragoza + Gijon. Improves resilience and margin." },
  ];
  insights.forEach((ins, i) => {
    const y = 1.12 + i * 1.18;
    s.addShape("rect", { x: 6.8, y, w: 2.8, h: 1.06, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 }, shadow: cardShadow() });
    s.addShape("rect", { x: 6.8, y, w: 0.07, h: 1.06, fill: { color: ins.color }, line: { color: ins.color } });
    s.addText(ins.title, { x: 7.0, y: y + 0.1, w: 2.5, h: 0.28, fontSize: 11, bold: true, color: C.darkText, fontFace: "Calibri" });
    s.addText(ins.body,  { x: 7.0, y: y + 0.4, w: 2.5, h: 0.55, fontSize: 9.5, color: C.mutedText, fontFace: "Calibri" });
  });

  s.addShape("rect", { x: 0.5, y: 4.58, w: 9, h: 0.78, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 } });
  s.addText("Financial exposure from the January 2025 incident:", {
    x: 0.65, y: 4.63, w: 4.0, h: 0.28, fontSize: 10, color: C.mutedText, fontFace: "Calibri",
  });
  s.addText("€2,100,000+", {
    x: 4.8, y: 4.58, w: 2.3, h: 0.78, fontSize: 30, bold: true, color: C.red, fontFace: "Georgia", align: "center", valign: "middle",
  });
  s.addText("legal exposure · reputational damage · emergency logistics", {
    x: 0.65, y: 4.95, w: 4.0, h: 0.28, fontSize: 9.5, color: C.mutedText, fontFace: "Calibri", italic: true,
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 12 — Investment & ROI
// ════════════════════════════════════════════════════════════════════════════
function slide12_investment(pres) {
  const s = darkSlide(pres);

  s.addShape("ellipse", { x: -1, y: 2.5, w: 5, h: 5, fill: { color: C.iceBlue, transparency: 90 }, line: { color: C.iceBlue, transparency: 90 } });

  chip(s, "Investment", 0.55, 0.35);
  slideTitleLight(s, "The Business Case");

  // Four big number cards
  const cards = [
    { val: "€152K",  label: "implementation\n(one-time)",         color: C.iceBlue },
    { val: "€39K",   label: "annual operating\ncost",             color: C.teal },
    { val: "€2.1M+", label: "cost of\none incident",             color: C.red },
    { val: "13×",    label: "ROI on first\nprevented incident",   color: C.green },
  ];
  cards.forEach((c, i) => {
    const x = 0.5 + i * 2.35;
    s.addShape("rect", { x, y: 1.3, w: 2.1, h: 2.1, fill: { color: C.darkCard }, line: { color: i === 3 ? C.green : "1E3A5F", width: 0.5 }, shadow: cardShadow() });
    if (i === 3) {
      s.addShape("rect", { x, y: 1.3, w: 2.1, h: 0.06, fill: { color: C.green }, line: { color: C.green } });
    }
    s.addText(c.val, { x, y: 1.45, w: 2.1, h: 0.88, fontSize: 34, bold: true, color: c.color, align: "center", fontFace: "Georgia" });
    s.addText(c.label, { x, y: 2.38, w: 2.1, h: 0.68, fontSize: 10, color: C.lightText, align: "center", fontFace: "Calibri", margin: 4 });
  });

  // Statement
  s.addShape("rect", { x: 0.5, y: 3.62, w: 9.0, h: 0.78, fill: { color: C.darkCard }, line: { color: C.green, transparency: 55, width: 0.5 } });
  s.addText("LCS pays for itself the first time it stops a truck from being too late.", {
    x: 0.7, y: 3.62, w: 8.6, h: 0.78,
    fontSize: 16, italic: true, color: C.white, fontFace: "Georgia", valign: "middle",
  });

  // Cost breakdown mini
  const items = [
    ["Data pipelines (Bronze → Gold)", "€60,000"],
    ["AI Copilot (Claude-powered)",    "€24,000"],
    ["IoT PLC integration (5 plants)", "€28,000"],
    ["Streaming (Kafka + Spark)",       "€22,000"],
    ["Testing · Training · Go-live",    "€18,000"],
  ];
  s.addText("Implementation breakdown", { x: 0.55, y: 4.58, w: 4.5, h: 0.28, fontSize: 10, bold: true, color: C.lightText, fontFace: "Calibri" });
  items.forEach((row, i) => {
    s.addText(row[0], { x: 0.55, y: 4.9 + i * 0.13, w: 3.6, h: 0.14, fontSize: 8.5, color: C.lightText, fontFace: "Calibri" });
    s.addText(row[1], { x: 4.3, y: 4.9 + i * 0.13, w: 0.9, h: 0.14, fontSize: 8.5, bold: true, color: C.iceBlue, fontFace: "Calibri", align: "right" });
  });

  s.addText("Annual breakdown", { x: 5.5, y: 4.58, w: 4.0, h: 0.28, fontSize: 10, bold: true, color: C.lightText, fontFace: "Calibri" });
  const annual = [
    ["Cloud compute (Spark + Kafka)", "€21,600"],
    ["Object storage (MinIO/S3)",     "€2,400"],
    ["AI API (50K queries/month)",     "€3,600"],
    ["Platform support (8h/month)",   "€9,600"],
    ["Monitoring + alerting",         "€1,800"],
  ];
  annual.forEach((row, i) => {
    s.addText(row[0], { x: 5.5, y: 4.9 + i * 0.13, w: 3.2, h: 0.14, fontSize: 8.5, color: C.lightText, fontFace: "Calibri" });
    s.addText(row[1], { x: 8.8, y: 4.9 + i * 0.13, w: 0.85, h: 0.14, fontSize: 8.5, bold: true, color: C.teal, fontFace: "Calibri", align: "right" });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 13 — Roadmap
// ════════════════════════════════════════════════════════════════════════════
function slide13_roadmap(pres) {
  const s = lightSlide(pres);
  topRule(s);
  chip(s, "Implementation Roadmap", 0.5, 0.13);
  slideTitle(s, "18-Month Delivery Plan");

  const phases = [
    { months: "M1–2",   title: "Foundation",        body: "Bronze → Gold pipeline live\nDry-out risk model running on historical data",   color: "1D4ED8" },
    { months: "M3",     title: "Intelligence",       body: "LCS AI Copilot deployed\nHistorical briefing + model validation",              color: C.teal },
    { months: "M4",     title: "Streaming",          body: "Kafka + Spark Structured Streaming\nAlert pipeline → ops team Slack",          color: C.green },
    { months: "M5–6",   title: "Live OT Data",       body: "PLC integration: all 5 plants\nFull rollout to 25 hospitals",                  color: "7C3AED" },
    { months: "M7–12",  title: "ML Forecasting",     body: "LSTM demand forecasting model\nMaintenance automation in Copilot",             color: C.orange },
    { months: "M13–18", title: "Autonomous Ops",     body: "Copilot proposes schedules\nOperations team approves — not decides",          color: C.iceBlue },
  ];

  // Timeline bar
  s.addShape("rect", { x: 0.5, y: 2.25, w: 9.0, h: 0.045, fill: { color: "CBD5E1" }, line: { color: "CBD5E1" } });

  phases.forEach((ph, i) => {
    const x = 0.5 + i * 1.52;
    const y_card = 2.6;

    // dot on timeline
    s.addShape("ellipse", { x: x + 0.55, y: 2.1, w: 0.28, h: 0.28, fill: { color: ph.color }, line: { color: ph.color } });

    // card
    s.addShape("rect", { x, y: y_card, w: 1.4, h: 2.65, fill: { color: C.white }, line: { color: "E2E8F0", width: 0.5 }, shadow: cardShadow() });
    s.addShape("rect", { x, y: y_card, w: 1.4, h: 0.055, fill: { color: ph.color }, line: { color: ph.color } });

    s.addText(ph.months, { x, y: y_card + 0.1, w: 1.4, h: 0.28, fontSize: 9.5, bold: true, color: ph.color, align: "center", fontFace: "Calibri" });
    s.addText(ph.title,  { x, y: y_card + 0.42, w: 1.4, h: 0.42, fontSize: 11, bold: true, color: C.darkText, align: "center", fontFace: "Calibri", margin: 2 });
    s.addText(ph.body,   { x, y: y_card + 0.9, w: 1.4, h: 1.6, fontSize: 9, color: C.mutedText, align: "center", fontFace: "Calibri", margin: 4 });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 14 — Why Momentum
// ════════════════════════════════════════════════════════════════════════════
function slide14_why(pres) {
  const s = darkSlide(pres);
  s.addShape("ellipse", { x: 5.5, y: -0.5, w: 7, h: 7, fill: { color: C.iceBlue, transparency: 93 }, line: { color: C.iceBlue, transparency: 93 } });

  chip(s, "Why Momentum", 0.55, 0.35);

  s.addText("Every firm in this room can build a dashboard.", {
    x: 0.65, y: 0.85, w: 8.7, h: 0.58,
    fontSize: 24, color: C.lightText, fontFace: "Georgia", italic: true,
  });
  s.addText("Momentum builds the intelligence layer that tells your operations director — before their morning coffee — which hospital needs a truck, which plant is one shutdown away from a crisis, and exactly what it will cost if the wrong decision is made.", {
    x: 0.65, y: 1.62, w: 8.7, h: 1.28,
    fontSize: 16, color: C.white, fontFace: "Georgia",
  });

  s.addShape("rect", { x: 0.65, y: 3.05, w: 8.7, h: 0.025, fill: { color: C.iceBlue, transparency: 50 }, line: { color: C.iceBlue, transparency: 50 } });

  s.addText("The January 2025 incident was preventable. Every incident after today is also preventable — with the right data, the right models, and the right intelligence layer.", {
    x: 0.65, y: 3.2, w: 8.7, h: 1.0,
    fontSize: 16, color: C.white, fontFace: "Georgia",
  });

  s.addText("That is what Momentum delivers.", {
    x: 0.65, y: 4.32, w: 8.7, h: 0.65,
    fontSize: 24, bold: true, color: C.iceBlue, fontFace: "Georgia",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 15 — Close
// ════════════════════════════════════════════════════════════════════════════
function slide15_close(pres) {
  const s = darkSlide(pres);

  s.addShape("ellipse", { x: 3.0, y: 0.5, w: 8, h: 8, fill: { color: C.teal, transparency: 91 }, line: { color: C.teal, transparency: 91 } });
  s.addShape("ellipse", { x: -1.5, y: 2.0, w: 4, h: 4, fill: { color: C.iceBlue, transparency: 90 }, line: { color: C.iceBlue, transparency: 90 } });

  s.addText("LUMINAE INTELLIGENCE", {
    x: 0.5, y: 1.5, w: 9, h: 0.8,
    fontSize: 42, bold: true, color: C.iceBlue, fontFace: "Georgia", align: "center", charSpacing: 3,
  });
  s.addText("From Signal to Safety.", {
    x: 0.5, y: 2.45, w: 9, h: 0.55,
    fontSize: 22, italic: true, color: C.white, fontFace: "Georgia", align: "center",
  });

  s.addShape("rect", { x: 3.5, y: 3.2, w: 3.0, h: 0.025, fill: { color: C.iceBlue, transparency: 40 }, line: { color: C.iceBlue, transparency: 40 } });

  s.addText("Amsterdam · Barcelona · Berlin · Paris · Vienna", {
    x: 0.5, y: 3.38, w: 9, h: 0.38,
    fontSize: 11.5, color: C.lightText, fontFace: "Calibri", align: "center",
  });

  s.addText('"We don\'t predict the future. We prevent the worst of it."', {
    x: 0.5, y: 4.2, w: 9, h: 0.45,
    fontSize: 13, italic: true, color: C.lightText, fontFace: "Georgia", align: "center",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// MAIN
// ════════════════════════════════════════════════════════════════════════════
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title  = "Momentum — ManOxCo LCS";
  pres.author = "Momentum";

  slide01_cover(pres);
  slide02_incident(pres);
  slide03_findings(pres);
  slide04_luminae(pres);
  slide05_signal(pres);
  slide06_risk(pres);
  slide07_demo(pres);
  slide08_evolution(pres);
  slide09_forecast(pres);
  slide10_maintenance(pres);
  slide11_finance(pres);
  slide12_investment(pres);
  slide13_roadmap(pres);
  slide14_why(pres);
  slide15_close(pres);

  await pres.writeFile({ fileName: OUT });
  console.log(`✓ Saved: ${OUT}`);
}

main().catch(console.error);
