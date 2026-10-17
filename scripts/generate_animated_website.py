# scripts/generate_animated_website.py
import os

content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>findit — Smart Lost & Found Reimagined</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Instrument+Serif:ital@0;1&family=Poppins:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            heading: ['"Instrument Serif"', 'serif'],
            body: ['Barlow', 'sans-serif'],
            display: ['Poppins', 'sans-serif'],
            deva: ['"Noto Sans Devanagari"', 'sans-serif']
          },
          colors: {
            brand: {
              gold: '#f1d5a6',
              amber: '#e4b778',
              bronze: '#c8905d',
            }
          }
        }
      }
    };
  </script>

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <!-- Three.js r169 via importmap for 3D Hero & 3D Key -->
  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"
    }
  }
  </script>

  <style>
    :root {
      --bg: #030407;
      --fg: #ffffff;
      --gold-primary: #e4b778;
      --gold-glow: rgba(228, 183, 120, 0.4);
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      background-color: var(--bg);
      color: var(--fg);
      font-family: 'Barlow', sans-serif;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
    }
    ::-webkit-scrollbar-track {
      background: #030407;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.3);
    }

    /* Liquid Glass Design System */
    .liquid-glass {
      background: rgba(255, 255, 255, 0.02);
      background-blend-mode: luminosity;
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.12);
      position: relative;
    }
    
    .liquid-glass::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      padding: 1.2px;
      background: linear-gradient(180deg,
        rgba(255, 255, 255, 0.35) 0%,
        rgba(255, 255, 255, 0.12) 20%,
        rgba(255, 255, 255, 0) 40%,
        rgba(255, 255, 255, 0) 60%,
        rgba(255, 255, 255, 0.12) 80%,
        rgba(255, 255, 255, 0.35) 100%);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
    }

    .liquid-glass-strong {
      background: rgba(255, 255, 255, 0.04);
      background-blend-mode: luminosity;
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 20px 45px -15px rgba(0,0,0,0.8), inset 0 1px 1.5px rgba(255, 255, 255, 0.25);
      position: relative;
    }

    .liquid-glass-strong::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      padding: 1.5px;
      background: linear-gradient(180deg,
        rgba(255, 255, 255, 0.5) 0%,
        rgba(255, 255, 255, 0.2) 25%,
        rgba(255, 255, 255, 0.04) 50%,
        rgba(255, 255, 255, 0.2) 75%,
        rgba(255, 255, 255, 0.5) 100%);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
    }

    /* Ambient background grid */
    .bg-ambient {
      background: radial-gradient(circle at 50% 12%, rgba(70, 50, 140, 0.22) 0%, transparent 60%),
                  radial-gradient(circle at 85% 45%, rgba(200, 144, 93, 0.12) 0%, transparent 50%),
                  radial-gradient(circle at 15% 75%, rgba(35, 90, 150, 0.12) 0%, transparent 50%),
                  #030407;
    }

    /* Glowing radar pulse */
    @keyframes pulse-ring {
      0% { transform: scale(0.9); opacity: 0.8; }
      50% { transform: scale(1.7); opacity: 0; }
      100% { transform: scale(0.9); opacity: 0; }
    }
    .live-pulse {
      position: relative;
    }
    .live-pulse::after {
      content: '';
      position: absolute;
      inset: -2px;
      border-radius: 9999px;
      background: #22c55e;
      animation: pulse-ring 2.2s infinite ease-out;
      z-index: -1;
    }

    /* 3D Background Canvas styles */
    #hero-canvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: grab;
      touch-action: none;
    }
    #hero-canvas.dragging {
      cursor: grabbing;
    }

    /* Kinetic blur words animation */
    @keyframes blurIn {
      0% { filter: blur(14px); opacity: 0; transform: translateY(20px); }
      100% { filter: blur(0); opacity: 1; transform: translateY(0); }
    }
    .animate-blur-in {
      animation: blurIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* 3D Key Stage */
    .hero-key-stage {
      position: relative;
      z-index: 10;
      min-height: 520px;
      width: 100%;
      display: grid;
      place-items: center;
      perspective: 1100px;
      user-select: none;
    }
    .hero-key-stage::before {
      content: "";
      position: absolute;
      z-index: -2;
      width: min(92%, 480px);
      aspect-ratio: 1;
      border: 1px solid rgba(228, 183, 120, 0.18);
      border-radius: 50%;
      box-shadow: 0 0 0 32px rgba(228, 183, 120, 0.025), 0 0 0 90px rgba(228, 183, 120, 0.012);
    }
    .hero-key-stage::after {
      content: "";
      position: absolute;
      z-index: -1;
      width: 65%;
      height: 65%;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(230, 180, 110, 0.32) 0%, rgba(182, 119, 72, 0.12) 50%, transparent 75%);
      filter: blur(55px);
      transform: translate(10%, 6%);
    }
    .key-stage-word {
      position: absolute;
      z-index: -1;
      top: 50%;
      left: 50%;
      color: rgba(238, 233, 220, 0.045);
      font: 700 clamp(130px, 16vw, 240px)/0.8 'Poppins', sans-serif;
      letter-spacing: -0.1em;
      transform: translate(-50%, -50%) rotate(-90deg);
      writing-mode: vertical-rl;
      user-select: none;
      pointer-events: none;
    }
    .key-stage-index {
      position: absolute;
      top: 6%;
      right: 6%;
      display: grid;
      gap: 4px;
      color: #a4b399;
      font: 600 10px/1 'Barlow', sans-serif;
      letter-spacing: 2px;
    }
    .key-stage-index span:first-child { color: #e4b778; }

    .key-interaction {
      position: relative;
      z-index: 2;
      width: 100%;
      height: 100%;
      min-height: 480px;
      display: grid;
      place-items: center;
      cursor: grab;
      touch-action: none;
      user-select: none;
      perspective: 1000px;
    }
    .key-interaction.cursor-grabbing,
    .key-interaction:active {
      cursor: grabbing;
    }

    .key-float {
      animation: findit-key-float 6s ease-in-out infinite;
      transform-style: preserve-3d;
    }

    .key-3d-wrapper {
      position: relative;
      width: 240px;
      height: 520px;
      transform-style: preserve-3d;
      will-change: transform;
    }

    .key-layer {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      transform-style: preserve-3d;
      pointer-events: none;
    }

    .key-layer-back {
      transform: translateZ(-8px);
      filter: brightness(0.55) contrast(1.2);
      opacity: 0.85;
    }

    .key-layer-mid {
      transform: translateZ(-2px);
      filter: brightness(0.8);
      opacity: 0.95;
    }

    .key-layer-front {
      transform: translateZ(6px);
      filter: drop-shadow(0 25px 35px rgba(0,0,0,0.85)) drop-shadow(0 0 50px rgba(228,183,120,0.45));
    }

    .hero-key-svg {
      width: 100%;
      height: 100%;
      display: block;
      overflow: visible;
    }

    .key-stage-caption {
      position: absolute;
      bottom: 5%;
      left: 4%;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #d1d6c9;
      font-family: 'Instrument Serif', serif;
      font-style: italic;
      font-size: 17px;
      background: rgba(255,255,255,0.04);
      backdrop-filter: blur(10px);
      padding: 6px 16px;
      border-radius: 9999px;
      border: 1px solid rgba(255,255,255,0.12);
      box-shadow: 0 10px 20px -5px rgba(0,0,0,0.5);
      pointer-events: none;
    }
    .key-stage-caption .caption-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #e4b778;
      box-shadow: 0 0 12px rgba(228,183,120,0.9);
      animation: pulse-ring 2s infinite ease-out;
    }
    .key-stage-orbit {
      position: absolute;
      z-index: -1;
      border: 1px solid rgba(228, 183, 120, 0.18);
      border-radius: 50%;
      transform: rotate(-31deg);
      width: 90%;
      height: 34%;
      pointer-events: none;
    }
    .orbit-b {
      width: 70%;
      height: 80%;
      transform: rotate(32deg);
      border-color: rgba(200, 144, 93, 0.16);
      pointer-events: none;
    }

    @keyframes findit-key-float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-12px); }
    }

    /* Radar Sonar Sweep Animation for Heatmap */
    @keyframes radarSweep {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .sonar-beam {
      animation: radarSweep 6s linear infinite;
      transform-origin: 50% 50%;
    }

    /* Laser Scanner for OCR */
    @keyframes laserScan {
      0% { top: 4%; opacity: 0.8; }
      50% { top: 92%; opacity: 1; }
      100% { top: 4%; opacity: 0.8; }
    }
    .laser-line {
      animation: laserScan 3s ease-in-out infinite;
    }

    /* Holographic Card Tilt Effect */
    .holo-card {
      position: relative;
      overflow: hidden;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .holo-card::after {
      content: '';
      position: absolute;
      inset: -100%;
      background: linear-gradient(135deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 70%);
      transform: rotate(35deg) translateY(-100%);
      transition: transform 0.6s ease;
      pointer-events: none;
    }
    .holo-card:hover::after {
      transform: rotate(35deg) translateY(100%);
    }

    /* Toast Notification Animation */
    @keyframes toastSlideUp {
      0% { transform: translateY(30px); opacity: 0; }
      15% { transform: translateY(0); opacity: 1; }
      85% { transform: translateY(0); opacity: 1; }
      100% { transform: translateY(-20px); opacity: 0; }
    }
    .toast-animate {
      animation: toastSlideUp 5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
  </style>
</head>
<body class="bg-[#030407] text-white bg-ambient selection:bg-amber-400/20 selection:text-amber-200">

  <!-- ============================================================== -->
  <!-- 1. FLOATING LIQUID NAVIGATION BAR -->
  <!-- ============================================================== -->
  <header class="fixed top-4 inset-x-0 z-50 px-3 sm:px-6 md:px-10 flex items-center justify-between pointer-events-none">
    <!-- Brand Logo -->
    <a href="#" class="liquid-glass rounded-full px-3.5 py-2 sm:px-4 sm:py-2.5 flex items-center gap-2.5 pointer-events-auto hover:bg-white/5 transition group shadow-lg">
      <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-white/10 flex items-center justify-center text-amber-300 group-hover:rotate-45 transition-transform duration-500">
        <i data-lucide="compass" class="w-4 h-4"></i>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-lg sm:text-xl font-bold tracking-tight text-white font-display">find<span class="font-heading italic font-normal text-amber-300 text-xl sm:text-2xl">it</span></span>
        <span class="text-[8px] sm:text-[9px] uppercase tracking-widest text-neutral-400 font-medium ml-1 hidden sm:inline">LOST & FOUND</span>
      </div>
    </a>

    <!-- Right Controls -->
    <div class="flex items-center gap-2 sm:gap-3 pointer-events-auto">
      <!-- Audio Synth Toggle -->
      <button id="audio-toggle-btn" onclick="toggleAudio()" title="Toggle Web Audio Synthesizer Chimes" class="liquid-glass rounded-full w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center text-neutral-400 hover:text-amber-300 hover:bg-white/10 transition">
        <i data-lucide="volume-2" id="audio-icon" class="w-4 h-4"></i>
      </button>

      <!-- Language Selector -->
      <div class="liquid-glass rounded-full px-2 py-1 flex items-center gap-1 text-[11px] font-semibold text-neutral-300">
        <button onclick="changeLanguage('en')" id="lang-en" class="px-2 py-0.5 rounded-full bg-white/20 text-white transition">EN</button>
        <button onclick="changeLanguage('hi')" id="lang-hi" class="px-2 py-0.5 rounded-full hover:text-white transition">हिंदी</button>
        <button onclick="changeLanguage('mr')" id="lang-mr" class="px-2 py-0.5 rounded-full hover:text-white transition">मराठी</button>
      </div>

      <!-- Auth Buttons & User Profile Dropdown -->
      <div id="nav-auth-logged-out" class="flex items-center gap-2">
        <button onclick="openAuthModal('login')" id="nav-login-btn" class="liquid-glass rounded-full px-3.5 py-2 sm:px-4 sm:py-2 text-xs sm:text-sm font-semibold text-neutral-200 hover:text-white hover:bg-white/10 transition shadow-lg flex items-center gap-1.5">
          <i data-lucide="log-in" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-300"></i>
          <span>Sign In</span>
        </button>
        <button onclick="openAuthModal('signup')" id="nav-signup-btn" class="hidden sm:flex liquid-glass-strong rounded-full px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:bg-white/20 transition shadow-lg items-center gap-1.5 border border-amber-300/30">
          <i data-lucide="user-plus" class="w-3.5 h-3.5 text-amber-300"></i>
          <span>Register</span>
        </button>
      </div>

      <div id="nav-user-profile" class="hidden relative">
        <button onclick="toggleUserDropdown(event)" class="liquid-glass rounded-full px-3 py-1.5 flex items-center gap-2 text-xs sm:text-sm font-semibold text-white hover:bg-white/10 transition shadow-lg border border-amber-300/30">
          <div id="user-avatar-initials" class="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-tr from-amber-400 to-amber-600 text-neutral-950 font-bold text-xs flex items-center justify-center shadow-md">
            U
          </div>
          <span id="user-display-name" class="max-w-[90px] sm:max-w-[120px] truncate">User</span>
          <i data-lucide="chevron-down" class="w-3.5 h-3.5 text-neutral-400"></i>
        </button>
        <!-- Dropdown Menu -->
        <div id="user-dropdown-menu" class="hidden absolute right-0 mt-2 w-56 liquid-glass-strong rounded-2xl p-2 shadow-2xl border border-white/15 text-xs z-50">
          <div class="px-3 py-2 border-b border-white/10 mb-1">
            <p id="user-dropdown-name" class="font-bold text-white text-sm truncate">User Name</p>
            <p id="user-dropdown-email" class="text-neutral-400 truncate text-[11px]">user@example.com</p>
          </div>
          <button onclick="openMyReportsModal()" class="w-full text-left px-3 py-2 rounded-xl hover:bg-white/10 text-neutral-200 hover:text-white transition flex items-center gap-2">
            <i data-lucide="package" class="w-4 h-4 text-amber-300"></i>
            <span>My Reported Items</span>
          </button>
          <button onclick="handleLogout()" class="w-full text-left px-3 py-2 rounded-xl hover:bg-rose-500/20 text-rose-300 transition flex items-center gap-2 mt-1">
            <i data-lucide="log-out" class="w-4 h-4 text-rose-400"></i>
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      <!-- Make a Report CTA -->
      <button onclick="openReportModal('LOST')" class="liquid-glass-strong rounded-full px-3.5 py-2 sm:px-5 sm:py-2.5 text-xs sm:text-sm font-semibold text-white flex items-center gap-1.5 hover:bg-white/15 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-black/40">
        <i data-lucide="plus-circle" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-300"></i>
        <span data-i18n="btn_report">Report Item</span>
      </button>
    </div>
  </header>

  <!-- ============================================================== -->
  <!-- 2. FULLSCREEN HERO SECTION WITH 3D GLASS & 3D GOLDEN KEY -->
  <!-- ============================================================== -->
  <section id="overview" class="relative w-full min-h-screen pt-28 pb-16 flex flex-col justify-between overflow-hidden">
    <!-- Three.js Interactive WebGL Background Canvas (Direct Grab-and-Rotate Enabled) -->
    <div class="absolute inset-0 z-0 opacity-85 pointer-events-auto">
      <canvas id="hero-canvas" aria-label="3D Interactive Chromatic Refractive Glass Background"></canvas>
    </div>



    <!-- Hero Content Overlay (2-Column Layout) -->
    <div class="relative z-10 max-w-7xl mx-auto w-full px-6 md:px-12 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center pointer-events-none">
      <!-- Left Column: Copy & Actions -->
      <div class="lg:col-span-7 flex flex-col justify-center pointer-events-auto">
        <!-- Live Community Badge -->
        <div class="inline-flex items-center gap-3 liquid-glass rounded-full px-4 py-1.5 text-xs md:text-sm text-neutral-200 mb-6 animate-blur-in w-fit">
          <span class="bg-amber-300/20 text-amber-200 border border-amber-300/30 px-2.5 py-0.5 rounded-full text-xs font-semibold flex items-center gap-1">
            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-300"></i>
            Live Community
          </span>
          <span class="font-light" data-i18n="hero_stats_reunited">Over 1,420 misplaced items reunited this month</span>
        </div>

        <!-- Big Cinematic Headline -->
        <h1 class="text-5xl sm:text-7xl lg:text-[5.2rem] font-display font-extrabold text-white leading-[0.95] tracking-tight mb-6">
          <span data-i18n="hero_headline_1">Lost something?</span><br>
          <span class="font-heading italic font-normal text-amber-200/90 text-6xl sm:text-8xl lg:text-[6.4rem]" data-i18n="hero_headline_2">
            Let’s bring it home.
          </span>
        </h1>

        <!-- Subheading -->
        <p class="text-neutral-300 text-base sm:text-xl font-light leading-relaxed max-w-xl mb-8" data-i18n="hero_subheading">
          Small things carry priceless stories. FindIt pairs the people who've misplaced something with the kind people who've found it — backed by smart matching and a real Java Spring Boot backend.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-wrap items-center gap-4 mb-8">
          <button onclick="scrollToReports('LOST')" class="liquid-glass-strong rounded-full px-7 py-3.5 text-sm md:text-base font-semibold text-white flex items-center gap-2.5 hover:bg-white/20 transition-all hover:scale-105 active:scale-95 shadow-xl">
            <span data-i18n="btn_find_item">Find My Item</span>
            <i data-lucide="arrow-down-left" class="w-4 h-4 text-amber-300"></i>
          </button>
          
          <button onclick="openReportModal('FOUND')" class="liquid-glass rounded-full px-7 py-3.5 text-sm md:text-base font-medium text-neutral-200 hover:text-white flex items-center gap-2 hover:bg-white/10 transition-all">
            <i data-lucide="arrow-up-right" class="w-4 h-4 text-emerald-400"></i>
            <span data-i18n="btn_found_item">I Found Something</span>
          </button>

          <a href="#matching-engine" class="liquid-glass rounded-full px-5 py-3.5 text-sm font-medium text-amber-300 hover:bg-amber-400/10 transition-all flex items-center gap-2">
            <i data-lucide="cpu" class="w-4 h-4"></i>
            <span data-i18n="btn_try_ai">Try AI Radar</span>
          </a>
        </div>
      </div>

      <!-- Right Column: REAL 3D GOLDEN SKELETON KEY STAGE -->
      <div class="lg:col-span-5 flex items-center justify-center pointer-events-auto">
        <div class="hero-key-stage" role="img" aria-label="A softly illuminated 3D golden key, a reminder that lost things find their way home.">
          <div class="key-stage-word" aria-hidden="true">HOME</div>
          
          <!-- Interactive 3D Golden Skeleton Key (3D Multi-Layer Extruded Volume) -->
          <div
            id="hero-key-interactive"
            class="key-interaction cursor-grab"
            onpointerdown="startKeySwipe(event)"
            onpointermove="moveKeySwipe(event)"
            onpointerup="endKeySwipe(event)"
            onpointercancel="endKeySwipe(event)"
            onpointerleave="leaveKeySwipe(event)"
          >
            <div class="key-float" aria-hidden="true">
              <div id="key-tilt-container" class="key-3d-wrapper">
                <!-- Layer 1: Deep Metallic Bevel & Shadow (translateZ(-8px)) -->
                <div class="key-layer key-layer-back">
                  <svg class="hero-key-svg" viewBox="0 0 240 520" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="gold-back-metal" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#2a1403" />
                        <stop offset="50%" stop-color="#5a310c" />
                        <stop offset="100%" stop-color="#221002" />
                      </linearGradient>
                    </defs>
                    <g>
                      <!-- Transparent Bow Ring (No black circle - 100% see-through) -->
                      <path d="M 120 30 A 85 85 0 1 0 120 200 A 85 85 0 1 0 120 30 Z M 120 58 A 57 57 0 1 1 120 172 A 57 57 0 1 1 120 58 Z" fill-rule="evenodd" fill="url(#gold-back-metal)" stroke="#221002" stroke-width="3" />
                      <!-- Collar -->
                      <rect x="98" y="198" width="44" height="18" rx="4" fill="url(#gold-back-metal)" />
                      <!-- Shaft -->
                      <rect x="105" y="220" width="30" height="252" rx="4" fill="url(#gold-back-metal)" />
                      <!-- 2-Tooth Skeleton Bit -->
                      <path d="M 132 390 L 184 390 L 184 420 L 150 420 L 150 432 L 180 432 L 180 466 L 132 466 Z" fill="url(#gold-back-metal)" />
                      <!-- Tip -->
                      <path d="M 103 468 C 103 496 137 496 137 468 Z" fill="url(#gold-back-metal)" />
                      <circle cx="120" cy="488" r="8" fill="url(#gold-back-metal)" />
                    </g>
                  </svg>
                </div>

                <!-- Layer 2: Mid Bevel Core (translateZ(-2px)) -->
                <div class="key-layer key-layer-mid">
                  <svg class="hero-key-svg" viewBox="0 0 240 520" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="gold-mid-metal" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#5a310c" />
                        <stop offset="30%" stop-color="#a66e33" />
                        <stop offset="60%" stop-color="#c9914f" />
                        <stop offset="100%" stop-color="#4e2808" />
                      </linearGradient>
                    </defs>
                    <g>
                      <!-- Transparent Bow Ring (No black circle - 100% see-through) -->
                      <path d="M 120 30.5 A 84.5 84.5 0 1 0 120 199.5 A 84.5 84.5 0 1 0 120 30.5 Z M 120 58.5 A 56.5 56.5 0 1 1 120 171.5 A 56.5 56.5 0 1 1 120 58.5 Z" fill-rule="evenodd" fill="url(#gold-mid-metal)" stroke="#5a310c" stroke-width="2" />
                      <!-- Collar -->
                      <rect x="99" y="199" width="42" height="17" rx="4" fill="url(#gold-mid-metal)" />
                      <!-- Shaft -->
                      <rect x="106" y="221" width="28" height="251" rx="4" fill="url(#gold-mid-metal)" />
                      <!-- 2-Tooth Skeleton Bit -->
                      <path d="M 133 391 L 183 391 L 183 419 L 151 419 L 151 433 L 179 433 L 179 465 L 133 465 Z" fill="url(#gold-mid-metal)" />
                      <!-- Tip -->
                      <path d="M 104 469 C 104 495 136 495 136 469 Z" fill="url(#gold-mid-metal)" />
                      <circle cx="120" cy="488" r="7.5" fill="url(#gold-mid-metal)" />
                    </g>
                  </svg>
                </div>

                <!-- Layer 3: Polished Front Face with Specular Highlights (translateZ(6px)) -->
                <div class="key-layer key-layer-front">
                  <svg class="hero-key-svg" viewBox="0 0 240 520" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <!-- 3D Cylindrical Tube Highlight Gradient -->
                      <linearGradient id="gold-cyl" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#693c16" />
                        <stop offset="20%" stop-color="#c89255" />
                        <stop offset="42%" stop-color="#fae2b4" />
                        <stop offset="52%" stop-color="#ffffff" />
                        <stop offset="65%" stop-color="#e4b778" />
                        <stop offset="85%" stop-color="#9a6230" />
                        <stop offset="100%" stop-color="#4e290c" />
                      </linearGradient>

                      <!-- Radial Gradient for Ring Curvature -->
                      <radialGradient id="gold-ring" cx="44%" cy="38%" r="60%">
                        <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
                        <stop offset="28%" stop-color="#fae2b4" />
                        <stop offset="60%" stop-color="#e4b778" />
                        <stop offset="85%" stop-color="#9a6230" />
                        <stop offset="100%" stop-color="#4e290c" />
                      </radialGradient>

                      <!-- Sharp Edge Bevel Specular Gradient -->
                      <linearGradient id="gold-edge" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
                        <stop offset="35%" stop-color="#fae2b4" stop-opacity="0.7" />
                        <stop offset="70%" stop-color="#a66e33" stop-opacity="0.4" />
                        <stop offset="100%" stop-color="#ffffff" stop-opacity="0.85" />
                      </linearGradient>
                    </defs>

                    <g>
                      <!-- 1. Bow (Clean circular torus ring with 100% transparent hole) -->
                      <path d="M 120 31 A 84 84 0 1 0 120 199 A 84 84 0 1 0 120 31 Z M 120 59 A 56 56 0 1 1 120 171 A 56 56 0 1 1 120 59 Z" fill-rule="evenodd" fill="url(#gold-ring)" stroke="url(#gold-edge)" stroke-width="2.5" />

                      <!-- 2. Collar (Clean transition between bow and shaft) -->
                      <rect x="100" y="200" width="40" height="16" rx="4" fill="url(#gold-cyl)" stroke="url(#gold-edge)" stroke-width="1.5" />
                      <ellipse cx="120" cy="216" rx="20" ry="5" fill="url(#gold-cyl)" stroke="url(#gold-edge)" stroke-width="1.2" />

                      <!-- 3. Straight Smooth Cylindrical Shaft -->
                      <rect x="107" y="222" width="26" height="250" rx="4" fill="url(#gold-cyl)" stroke="url(#gold-edge)" stroke-width="1.5" />
                      <!-- Specular Center Highlight Ribbon -->
                      <line x1="119" y1="224" x2="119" y2="470" stroke="#ffffff" stroke-opacity="0.85" stroke-width="2.5" />
                      <line x1="124" y1="224" x2="124" y2="470" stroke="#fae4b5" stroke-opacity="0.45" stroke-width="1.5" />

                      <!-- 4. Clean Classic 2-Tooth Skeleton Bit (Stepped notches) -->
                      <path d="
                        M 133 392
                        L 182 392
                        L 182 418
                        L 152 418
                        L 152 434
                        L 178 434
                        L 178 464
                        L 133 464
                        Z
                      " fill="url(#gold-cyl)" stroke="url(#gold-edge)" stroke-width="2" />
                      <!-- Specular gleams on teeth outer tips -->
                      <line x1="181" y1="392" x2="181" y2="418" stroke="#ffffff" stroke-opacity="0.9" stroke-width="2" />
                      <line x1="177" y1="434" x2="177" y2="464" stroke="#ffffff" stroke-opacity="0.9" stroke-width="2" />

                      <!-- 5. Bottom Tip Finial -->
                      <path d="M 105 470 C 105 494 135 494 135 470 Z" fill="url(#gold-cyl)" stroke="url(#gold-edge)" stroke-width="1.5" />
                      <circle cx="120" cy="488" r="7" fill="url(#gold-ring)" stroke="url(#gold-edge)" stroke-width="1.2" />
                    </g>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <span class="key-stage-orbit" aria-hidden="true"></span>
          <span class="key-stage-orbit orbit-b" aria-hidden="true"></span>
        </div>
      </div>
    </div>

    <!-- Hero Bottom Bar: Interactive Metrics -->
    <div class="relative z-10 max-w-7xl mx-auto w-full px-6 md:px-12 flex flex-col md:flex-row items-center justify-end gap-6 pt-6 border-t border-white/10 pointer-events-auto">
      <div class="flex items-center gap-6 sm:gap-10 text-xs sm:text-sm text-neutral-300">
        <div>
          <span class="font-heading italic text-white text-2xl sm:text-3xl font-semibold mr-1.5">96.4%</span>
          <span class="text-neutral-400 font-light">Match Accuracy</span>
        </div>
        <div class="w-px h-6 bg-white/15"></div>
        <div>
          <span class="font-heading italic text-white text-2xl sm:text-3xl font-semibold mr-1.5">&lt; 24h</span>
          <span class="text-neutral-400 font-light">Avg. Handoff</span>
        </div>
        <div class="w-px h-6 bg-white/15"></div>
        <div>
          <span class="font-heading italic text-white text-2xl sm:text-3xl font-semibold mr-1.5">100%</span>
          <span class="text-neutral-400 font-light">Zero-Knowledge</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- 3. ANIMATED KINDNESS COUNTER STRIP -->
  <!-- ============================================================== -->
  <section id="stats" class="py-16 px-6 md:px-12 border-y border-white/10 bg-black/40 relative">
    <div class="max-w-7xl mx-auto">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-10 gap-6">
        <div>
          <span class="text-xs font-semibold uppercase tracking-widest text-amber-300 block mb-2 font-display">
            // THE KINDNESS COUNTER
          </span>
          <h2 class="text-3xl md:text-5xl font-heading italic text-white leading-tight">
            Every report brings a lost item one step closer.
          </h2>
        </div>
        <p class="text-neutral-400 text-sm max-w-md font-light">
          Real-time statistics across campuses, transport hubs, and community public spaces.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div class="liquid-glass rounded-2xl p-6 flex flex-col justify-between hover:translate-y-[-2px] transition-transform">
          <div class="flex items-center justify-between text-neutral-400 mb-6">
            <span class="text-xs uppercase tracking-wider">Total Reports</span>
            <i data-lucide="files" class="w-5 h-5 text-amber-300"></i>
          </div>
          <div>
            <div class="text-4xl lg:text-5xl font-heading italic text-white font-bold" id="stat-total">2,846</div>
            <div class="text-xs text-neutral-400 font-light mt-1">Logged by community members</div>
          </div>
        </div>

        <div class="liquid-glass rounded-2xl p-6 flex flex-col justify-between hover:translate-y-[-2px] transition-transform">
          <div class="flex items-center justify-between text-neutral-400 mb-6">
            <span class="text-xs uppercase tracking-wider">Active Searches</span>
            <i data-lucide="search" class="w-5 h-5 text-blue-400"></i>
          </div>
          <div>
            <div class="text-4xl lg:text-5xl font-heading italic text-white font-bold" id="stat-open">1,214</div>
            <div class="text-xs text-neutral-400 font-light mt-1">Currently open & awaiting match</div>
          </div>
        </div>

        <div class="liquid-glass rounded-2xl p-6 flex flex-col justify-between hover:translate-y-[-2px] transition-transform">
          <div class="flex items-center justify-between text-neutral-400 mb-6">
            <span class="text-xs uppercase tracking-wider">Smart Connections</span>
            <i data-lucide="sparkles" class="w-5 h-5 text-amber-400"></i>
          </div>
          <div>
            <div class="text-4xl lg:text-5xl font-heading italic text-amber-300 font-bold" id="stat-matches">184</div>
            <div class="text-xs text-neutral-400 font-light mt-1">High-confidence matches found</div>
          </div>
        </div>

        <div class="liquid-glass rounded-2xl p-6 flex flex-col justify-between hover:translate-y-[-2px] transition-transform border border-amber-300/20 bg-amber-500/[0.03]">
          <div class="flex items-center justify-between text-neutral-400 mb-6">
            <span class="text-xs uppercase tracking-wider text-amber-200">Reunited Home</span>
            <i data-lucide="heart-handshake" class="w-5 h-5 text-amber-300"></i>
          </div>
          <div>
            <div class="text-4xl lg:text-5xl font-heading italic text-white font-bold" id="stat-returned">1,448</div>
            <div class="text-xs text-amber-200/80 font-light mt-1">Back in their owner’s hands</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- 4. INTERACTIVE AI NEURAL MATCHING ENGINE SIMULATOR -->
  <!-- ============================================================== -->
  <section id="matching-engine" class="py-24 px-6 md:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-12 gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/30 mb-3">
            <i data-lucide="cpu" class="w-3.5 h-3.5"></i>
            <span>Interactive Neural Simulator</span>
          </div>
          <h2 class="text-4xl md:text-5xl font-heading italic text-white leading-tight">
            How FindIt’s Matching Engine Works
          </h2>
          <p class="text-neutral-400 text-base font-light mt-2 max-w-2xl">
            Dual-encoder CLIP vision embeddings, Sentence-Transformers semantic text matching, and Geo-Temporal decay scoring combine into a single verifiable similarity score.
          </p>
        </div>

        <!-- Formula Callout -->
        <div class="liquid-glass rounded-2xl p-4 border border-white/10 text-xs font-mono text-neutral-300 max-w-md">
          <div class="text-amber-300 font-semibold mb-1">Composite Scoring Equation:</div>
          <div class="text-neutral-400">Score = 0.45(Image) + 0.25(Text) + 0.20(Geo) + 0.10(Time)</div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Left: Interactive Sliders & Controls -->
        <div class="lg:col-span-7 liquid-glass-strong rounded-3xl p-6 md:p-8 border border-white/15">
          <!-- Preset Case Selector -->
          <div class="mb-6">
            <label class="block text-xs uppercase tracking-wider text-neutral-400 font-semibold mb-2">Select Live Match Pair Scenario:</label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2" id="sim-presets">
              <button onclick="loadSimPreset(0)" class="sim-preset-btn active p-3 rounded-xl liquid-glass text-left border border-amber-300/40 text-white transition">
                <div class="text-xs font-bold flex items-center justify-between">
                  <span>AirPods Pro vs Case</span>
                  <span class="text-emerald-400">93% Expected</span>
                </div>
                <div class="text-[11px] text-neutral-400 mt-1">Platform 3 • High image & loc overlap</div>
              </button>
              <button onclick="loadSimPreset(1)" class="sim-preset-btn p-3 rounded-xl liquid-glass text-left border border-white/10 text-neutral-300 hover:text-white transition">
                <div class="text-xs font-bold flex items-center justify-between">
                  <span>Black Leather Wallet</span>
                  <span class="text-emerald-400">96% Expected</span>
                </div>
                <div class="text-[11px] text-neutral-400 mt-1">Library Desks • Text & distance match</div>
              </button>
              <button onclick="loadSimPreset(2)" class="sim-preset-btn p-3 rounded-xl liquid-glass text-left border border-white/10 text-neutral-300 hover:text-white transition">
                <div class="text-xs font-bold flex items-center justify-between">
                  <span>Bellroy Navy Backpack</span>
                  <span class="text-amber-300">74% Expected</span>
                </div>
                <div class="text-[11px] text-neutral-400 mt-1">Campus Cafe • Moderate distance gap</div>
              </button>
              <button onclick="loadSimPreset(3)" class="sim-preset-btn p-3 rounded-xl liquid-glass text-left border border-white/10 text-neutral-300 hover:text-white transition">
                <div class="text-xs font-bold flex items-center justify-between">
                  <span>Brass Keys vs Lone Key</span>
                  <span class="text-rose-400">48% Expected</span>
                </div>
                <div class="text-[11px] text-neutral-400 mt-1">Riverside Park • Low feature match</div>
              </button>
            </div>
          </div>

          <!-- The 4 Weight Sliders -->
          <div class="space-y-5">
            <!-- 1. Image Similarity -->
            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-neutral-200 font-medium flex items-center gap-1.5">
                  <i data-lucide="image" class="w-3.5 h-3.5 text-amber-300"></i>
                  <span>CLIP Image Embedding Similarity (45% weight)</span>
                </span>
                <span class="font-mono text-amber-300 font-semibold" id="val-sim-img">95%</span>
              </div>
              <input type="range" id="slider-img" min="0" max="100" value="95" oninput="updateSimScore()" class="w-full accent-amber-400 bg-white/10 rounded-lg cursor-pointer h-2">
              <div class="flex justify-between text-[10px] text-neutral-500 mt-0.5">
                <span>Different visual features</span>
                <span>Identical photo embedding vector</span>
              </div>
            </div>

            <!-- 2. Text Similarity -->
            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-neutral-200 font-medium flex items-center gap-1.5">
                  <i data-lucide="file-text" class="w-3.5 h-3.5 text-blue-400"></i>
                  <span>Sentence-Transformers Semantic Match (25% weight)</span>
                </span>
                <span class="font-mono text-blue-300 font-semibold" id="val-sim-txt">92%</span>
              </div>
              <input type="range" id="slider-txt" min="0" max="100" value="92" oninput="updateSimScore()" class="w-full accent-blue-400 bg-white/10 rounded-lg cursor-pointer h-2">
              <div class="flex justify-between text-[10px] text-neutral-500 mt-0.5">
                <span>Unrelated keywords</span>
                <span>Semantic synonym match ("wallet" ≈ "purse")</span>
              </div>
            </div>

            <!-- 3. Geo Closeness -->
            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-neutral-200 font-medium flex items-center gap-1.5">
                  <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>Geodesic Distance Proximity (20% weight)</span>
                </span>
                <span class="font-mono text-emerald-300 font-semibold" id="val-sim-geo">90% (0.15 km)</span>
              </div>
              <input type="range" id="slider-geo" min="0" max="100" value="90" oninput="updateSimScore()" class="w-full accent-emerald-400 bg-white/10 rounded-lg cursor-pointer h-2">
              <div class="flex justify-between text-[10px] text-neutral-500 mt-0.5">
                <span>Far apart (> 10 km)</span>
                <span>Same building or room (< 50 meters)</span>
              </div>
            </div>

            <!-- 4. Temporal Decay -->
            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-neutral-200 font-medium flex items-center gap-1.5">
                  <i data-lucide="clock" class="w-3.5 h-3.5 text-purple-400"></i>
                  <span>Time-Delta Decay Match (10% weight)</span>
                </span>
                <span class="font-mono text-purple-300 font-semibold" id="val-sim-time">94% (< 2 hrs)</span>
              </div>
              <input type="range" id="slider-time" min="0" max="100" value="94" oninput="updateSimScore()" class="w-full accent-purple-400 bg-white/10 rounded-lg cursor-pointer h-2">
              <div class="flex justify-between text-[10px] text-neutral-500 mt-0.5">
                <span>Weeks apart</span>
                <span>Found minutes after lost report</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Animated Gauge & Decision Output -->
        <div class="lg:col-span-5 liquid-glass-strong rounded-3xl p-6 md:p-8 border border-white/15 flex flex-col justify-between min-h-[460px]">
          <div>
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs uppercase tracking-wider text-neutral-400 font-semibold">Engine Assessment</span>
              <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-white/10 text-neutral-300" id="sim-threshold-badge">
                Threshold: 70.0%
              </span>
            </div>

            <!-- Circular Gauge Visualization -->
            <div class="flex flex-col items-center justify-center my-6 relative">
              <svg class="w-48 h-48 transform -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" stroke="rgba(255,255,255,0.08)" stroke-width="10" fill="transparent" />
                <circle id="sim-gauge-circle" cx="60" cy="60" r="50" stroke="#e4b778" stroke-width="10" stroke-linecap="round" fill="transparent" stroke-dasharray="314.15" stroke-dashoffset="22" class="transition-all duration-500" />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span class="text-4xl font-heading italic font-bold text-white" id="sim-final-score">93.2%</span>
                <span class="text-[11px] text-neutral-400 tracking-wider uppercase mt-1">Confidence Score</span>
              </div>
            </div>

            <!-- Status Banner -->
            <div id="sim-status-banner" class="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-400/30 text-xs transition-all">
              <div class="flex items-center gap-2 text-emerald-300 font-bold text-sm mb-1">
                <i data-lucide="bell-ring" class="w-4 h-4"></i>
                <span id="sim-status-title">High Confidence Match</span>
              </div>
              <p class="text-neutral-300 text-[11px] leading-relaxed" id="sim-status-desc">
                Score crosses the 70% threshold. Automated push notifications dispatched to owner & finder. Private verification challenge unlocked.
              </p>
            </div>
          </div>

          <!-- Dimension Contribution Bars -->
          <div class="pt-6 border-t border-white/10 space-y-2 text-xs">
            <div class="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Image Contribution (0.45×):</span>
              <span class="font-mono text-white" id="contrib-img">42.8%</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Text Contribution (0.25×):</span>
              <span class="font-mono text-white" id="contrib-txt">23.0%</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Geo Contribution (0.20×):</span>
              <span class="font-mono text-white" id="contrib-geo">18.0%</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Time Contribution (0.10×):</span>
              <span class="font-mono text-white" id="contrib-time">9.4%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- 5. INTERACTIVE CAMPUS & CITY TACTICAL HEATMAP -->
  <!-- ============================================================== -->
  <section id="heatmap" class="py-24 px-6 md:px-12 relative bg-black/50 border-t border-white/10">
    <div class="max-w-7xl mx-auto">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-10 gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-3">
            <i data-lucide="radar" class="w-3.5 h-3.5"></i>
            <span>Real-time Spatial Density Radar</span>
          </div>
          <h2 class="text-4xl md:text-5xl font-heading italic text-white leading-tight">
            Campus & Transit Hotspot Radar
          </h2>
          <p class="text-neutral-400 text-base font-light mt-2 max-w-2xl">
            Live geographic clusters identifying where items are most frequently lost or recovered. Click any pulsing cluster to inspect active records.
          </p>
        </div>

        <!-- Controls: Time of day & category filter -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="liquid-glass rounded-full px-4 py-2 flex items-center gap-2 text-xs text-neutral-300">
            <i data-lucide="clock" class="w-3.5 h-3.5 text-amber-300"></i>
            <span id="time-filter-label">2:00 PM (Afternoon Rush)</span>
          </div>
          <button onclick="cycleHeatmapTime()" class="liquid-glass-strong rounded-full px-4 py-2 text-xs font-semibold text-white hover:bg-white/20 transition flex items-center gap-1.5">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Cycle Time Density</span>
          </button>
        </div>
      </div>

      <!-- Tactical SVG Radar Map Board -->
      <div class="liquid-glass-strong rounded-3xl p-6 md:p-8 border border-white/15 relative overflow-hidden">
        <!-- SVG Grid Background & Radar Beam -->
        <div class="relative w-full aspect-[16/9] min-h-[440px] max-h-[580px] bg-neutral-950/80 rounded-2xl border border-white/10 overflow-hidden flex items-center justify-center">
          <!-- Tactical Grid Lines -->
          <svg class="absolute inset-0 w-full h-full opacity-20" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="radar-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="0.8" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#radar-grid)" />
            <circle cx="50%" cy="50%" r="20%" fill="none" stroke="rgba(228,183,120,0.3)" stroke-width="1" />
            <circle cx="50%" cy="50%" r="35%" fill="none" stroke="rgba(228,183,120,0.2)" stroke-width="1" />
            <circle cx="50%" cy="50%" r="48%" fill="none" stroke="rgba(228,183,120,0.15)" stroke-width="1" stroke-dasharray="4 4" />
          </svg>

          <!-- Rotating Radar Sonar Beam -->
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div class="w-full h-full max-w-[650px] max-h-[650px] sonar-beam relative">
              <div class="absolute top-1/2 left-1/2 w-1/2 h-1/2 origin-top-left -translate-x-full -translate-y-full bg-gradient-to-tr from-amber-500/15 via-emerald-500/5 to-transparent rounded-tl-full blur-sm"></div>
            </div>
          </div>

          <!-- Hotspot Nodes on Map -->
          <!-- Node 1: Campus Library -->
          <div onclick="selectHotspot(0)" class="hotspot-node absolute cursor-pointer group" style="top: 30%; left: 35%;">
            <div class="relative flex items-center justify-center">
              <span class="w-12 h-12 rounded-full bg-rose-500/25 animate-ping absolute"></span>
              <span class="w-7 h-7 rounded-full bg-rose-500/40 border-2 border-rose-400 flex items-center justify-center text-[10px] font-bold text-white shadow-lg">42</span>
            </div>
            <div class="absolute top-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[11px] text-white font-medium group-hover:scale-110 transition-transform">
              Central Library
            </div>
          </div>

          <!-- Node 2: Metro Platform 3 -->
          <div onclick="selectHotspot(1)" class="hotspot-node absolute cursor-pointer group" style="top: 58%; left: 68%;">
            <div class="relative flex items-center justify-center">
              <span class="w-10 h-10 rounded-full bg-amber-500/25 animate-ping absolute"></span>
              <span class="w-7 h-7 rounded-full bg-amber-500/40 border-2 border-amber-400 flex items-center justify-center text-[10px] font-bold text-white shadow-lg">28</span>
            </div>
            <div class="absolute top-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[11px] text-white font-medium group-hover:scale-110 transition-transform">
              Metro Platform 3
            </div>
          </div>

          <!-- Node 3: Student Union Café -->
          <div onclick="selectHotspot(2)" class="hotspot-node absolute cursor-pointer group" style="top: 65%; left: 24%;">
            <div class="relative flex items-center justify-center">
              <span class="w-8 h-8 rounded-full bg-blue-500/25 animate-ping absolute"></span>
              <span class="w-6 h-6 rounded-full bg-blue-500/40 border-2 border-blue-400 flex items-center justify-center text-[10px] font-bold text-white shadow-lg">19</span>
            </div>
            <div class="absolute top-7 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[11px] text-white font-medium group-hover:scale-110 transition-transform">
              Student Union
            </div>
          </div>

          <!-- Node 4: Riverside Park Benches -->
          <div onclick="selectHotspot(3)" class="hotspot-node absolute cursor-pointer group" style="top: 22%; left: 75%;">
            <div class="relative flex items-center justify-center">
              <span class="w-8 h-8 rounded-full bg-emerald-500/25 animate-ping absolute"></span>
              <span class="w-6 h-6 rounded-full bg-emerald-500/40 border-2 border-emerald-400 flex items-center justify-center text-[10px] font-bold text-white shadow-lg">15</span>
            </div>
            <div class="absolute top-7 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-[11px] text-white font-medium group-hover:scale-110 transition-transform">
              Riverside Park
            </div>
          </div>

          <!-- Selected Hotspot Flyout Card -->
          <div id="hotspot-card" class="absolute bottom-4 left-4 right-4 sm:right-auto sm:w-80 liquid-glass-strong rounded-2xl p-4 border border-amber-300/30 shadow-2xl transition-all">
            <div class="flex items-center justify-between text-xs mb-2">
              <span class="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold" id="hotspot-badge">High Activity Zone</span>
              <span class="text-neutral-400" id="hotspot-reports-count">42 active reports</span>
            </div>
            <h4 class="text-base font-bold text-white" id="hotspot-title">Campus Central Library</h4>
            <p class="text-xs text-neutral-300 mt-1 mb-3" id="hotspot-desc">
              Frequent items: AirPods cases, phone chargers, notebooks, glasses. Nearest collection point: 2nd floor circulation desk.
            </p>
            <div class="flex items-center gap-2">
              <button onclick="scrollToReports('ALL')" class="flex-1 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition text-center">
                Filter Board
              </button>
              <button onclick="openReportModal('LOST')" class="flex-1 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-300/30 text-xs font-semibold text-amber-200 transition text-center">
                Report Here
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- SAFE HANDOVER HUBS & COLLECTION POINTS DIRECTORY -->
  <!-- ============================================================== -->
  <section id="collection-points" class="py-24 px-6 md:px-12 relative border-t border-white/10">
    <div class="max-w-7xl mx-auto">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-12 gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-3">
            <i data-lucide="building-2" class="w-3.5 h-3.5"></i>
            <span>Neutral Verified Drop-offs</span>
          </div>
          <h2 class="text-4xl md:text-5xl font-heading italic text-white leading-tight">
            Verified Collection Points & Hubs
          </h2>
          <p class="text-neutral-400 text-base font-light mt-2 max-w-2xl">
            Don't want to meet an unfamiliar person? Drop off any found item with official staff at authorized collection desks equipped with secure return lockers and QR handover logging.
          </p>
        </div>

        <button onclick="openQRModal()" class="liquid-glass-strong rounded-full px-6 py-3 text-sm font-semibold text-white bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-300/40 transition flex items-center gap-2 shadow-lg">
          <i data-lucide="qr-code" class="w-4 h-4 text-emerald-300"></i>
          <span>Simulate QR Handover Scanner</span>
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Hub 1 -->
        <div class="liquid-glass rounded-2xl p-6 border border-white/10 hover:border-white/30 transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs mb-3">
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Open 24/7
              </span>
              <span class="text-neutral-400">Campus</span>
            </div>
            <h4 class="font-bold text-base text-white mb-1">Campus Security Main Desk</h4>
            <p class="text-xs text-neutral-400 leading-relaxed mb-4">West Gate Entrance • Building A Lobby. Official custody officers on duty.</p>
          </div>
          <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
            <span>Lockers Available: <strong>14</strong></span>
            <button onclick="openQRModal('Campus Security Main Desk')" class="text-amber-300 font-semibold hover:underline">Hand-in QR</button>
          </div>
        </div>

        <!-- Hub 2 -->
        <div class="liquid-glass rounded-2xl p-6 border border-white/10 hover:border-white/30 transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs mb-3">
              <span class="px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-semibold flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span> 6 AM - 11 PM
              </span>
              <span class="text-neutral-400">Transit</span>
            </div>
            <h4 class="font-bold text-base text-white mb-1">Central Station Lost Property</h4>
            <p class="text-xs text-neutral-400 leading-relaxed mb-4">Mezzanine Level, next to Ticket Office 4. Secure luggage tag registration.</p>
          </div>
          <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
            <span>Lockers Available: <strong>28</strong></span>
            <button onclick="openQRModal('Central Station Lost Property')" class="text-amber-300 font-semibold hover:underline">Hand-in QR</button>
          </div>
        </div>

        <!-- Hub 3 -->
        <div class="liquid-glass rounded-2xl p-6 border border-white/10 hover:border-white/30 transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs mb-3">
              <span class="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-semibold flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-purple-400"></span> 8 AM - 10 PM
              </span>
              <span class="text-neutral-400">Academic</span>
            </div>
            <h4 class="font-bold text-base text-white mb-1">Library Circulation Desk</h4>
            <p class="text-xs text-neutral-400 leading-relaxed mb-4">Ground Floor Atrium. Handles study accessories, tech, and notebooks.</p>
          </div>
          <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
            <span>Lockers Available: <strong>9</strong></span>
            <button onclick="openQRModal('Library Circulation Desk')" class="text-amber-300 font-semibold hover:underline">Hand-in QR</button>
          </div>
        </div>

        <!-- Hub 4 -->
        <div class="liquid-glass rounded-2xl p-6 border border-white/10 hover:border-white/30 transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs mb-3">
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Open 24/7
              </span>
              <span class="text-neutral-400">Civic</span>
            </div>
            <h4 class="font-bold text-base text-white mb-1">City Police Community Desk</h4>
            <p class="text-xs text-neutral-400 leading-relaxed mb-4">High Street Station • Room 101. Official receipt given for high-value items.</p>
          </div>
          <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
            <span>Lockers Available: <strong>20</strong></span>
            <button onclick="openQRModal('City Police Community Desk')" class="text-amber-300 font-semibold hover:underline">Hand-in QR</button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- 9. INTERACTIVE COMMUNITY BOARD (BROWSE & FILTER) -->
  <!-- ============================================================== -->
  <section id="reports" class="py-24 px-6 md:px-12 relative border-t border-white/10">
    <div class="max-w-7xl mx-auto">
      <!-- Section Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
        <div>
          <span class="text-xs font-semibold uppercase tracking-widest text-amber-300 block mb-2 font-display">
            // THE COMMUNITY BOARD
          </span>
          <h2 class="text-4xl md:text-6xl font-heading italic text-white leading-tight">
            Things looking for their way home.
          </h2>
          <p class="text-neutral-400 text-base font-light mt-2 max-w-xl">
            Browse live reports submitted by community members. Use dynamic search, tags, or generate instant social posters.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button onclick="openReportModal('LOST')" class="liquid-glass rounded-full px-5 py-2.5 text-xs md:text-sm text-neutral-200 hover:text-white flex items-center gap-2 hover:bg-white/10 transition">
            <i data-lucide="search" class="w-4 h-4 text-amber-300"></i>
            <span>Report Lost Item</span>
          </button>
          <button onclick="openReportModal('FOUND')" class="liquid-glass-strong rounded-full px-5 py-2.5 text-xs md:text-sm font-semibold text-white flex items-center gap-2 hover:bg-white/20 transition">
            <i data-lucide="plus" class="w-4 h-4 text-emerald-400"></i>
            <span>Report Found Item</span>
          </button>
        </div>
      </div>

      <!-- Live Search & Filtering Controls -->
      <div class="liquid-glass rounded-2xl p-4 md:p-6 mb-10 flex flex-col md:flex-row items-center gap-4 border border-white/10">
        <!-- Search Box -->
        <div class="relative flex-1 w-full">
          <i data-lucide="search" class="w-5 h-5 text-neutral-400 absolute left-4 top-1/2 -translate-y-1/2"></i>
          <input
            id="search-input"
            type="text"
            placeholder="Search item title, place, category, or distinctive detail..."
            class="w-full bg-white/5 border border-white/10 rounded-full pl-12 pr-4 py-3 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-300/50 transition"
            oninput="handleSearch(this.value)"
          >
          <span class="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-neutral-500 hidden sm:inline">⌘K</span>
        </div>

        <!-- Type Filter Chips -->
        <div class="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0" id="type-filters">
          <button onclick="filterType('ALL')" class="type-filter-btn px-4 py-2 rounded-full text-xs font-semibold bg-white text-black transition" data-type="ALL">All Items</button>
          <button onclick="filterType('LOST')" class="type-filter-btn px-4 py-2 rounded-full text-xs font-semibold text-neutral-300 hover:text-white hover:bg-white/10 transition" data-type="LOST">Lost Only</button>
          <button onclick="filterType('FOUND')" class="type-filter-btn px-4 py-2 rounded-full text-xs font-semibold text-neutral-300 hover:text-white hover:bg-white/10 transition" data-type="FOUND">Found Only</button>
        </div>
      </div>

      <!-- Category Filter Pills -->
      <div class="flex items-center gap-2 overflow-x-auto pb-4 mb-8 text-xs scrollbar-none" id="category-filters">
        <button onclick="filterCategory('ALL')" class="cat-pill active px-4 py-1.5 rounded-full liquid-glass-strong text-white border border-amber-300/40">All Categories</button>
        <button onclick="filterCategory('Electronics')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Electronics</button>
        <button onclick="filterCategory('Keys')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Keys & Access</button>
        <button onclick="filterCategory('Bags')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Bags & Backpacks</button>
        <button onclick="filterCategory('Wallets')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Wallets & Cards</button>
        <button onclick="filterCategory('Jewelry')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Jewelry & Watches</button>
        <button onclick="filterCategory('Clothing')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Clothing & Gear</button>
        <button onclick="filterCategory('Pets')" class="cat-pill px-4 py-1.5 rounded-full liquid-glass text-neutral-300 hover:text-white">Pets</button>
      </div>

      <!-- Results Count -->
      <div class="flex items-center justify-between text-xs text-neutral-400 mb-6">
        <span id="results-count">Showing 8 reports</span>
        <span>Sorted by: Most recent first</span>
      </div>

      <!-- Dynamic Grid of Report Cards -->
      <div id="reports-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Rendered dynamically by JavaScript -->
      </div>
    </div>
  </section>

  <!-- ============================================================== -->
  <!-- MODALS -->
  <!-- ============================================================== -->

  <!-- Modal 1: Make a Report (Lost or Found) -->
  <div id="report-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="liquid-glass-strong rounded-3xl max-w-xl w-full p-6 md:p-8 border border-white/20 max-h-[90vh] overflow-y-auto shadow-2xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
          <span class="text-xs uppercase font-semibold tracking-wider text-amber-300 font-display">CREATE NEW REPORT</span>
        </div>
        <button onclick="closeReportModal()" class="w-8 h-8 rounded-full liquid-glass flex items-center justify-center text-neutral-400 hover:text-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <h3 class="text-3xl font-heading italic text-white mb-2" id="modal-heading">
        Let’s get it back where it belongs.
      </h3>
      <p class="text-xs md:text-sm text-neutral-400 font-light mb-6">
        Share the distinctive details. We’ll cross-reference the community database in real-time.
      </p>

      <div class="grid grid-cols-2 gap-2 p-1.5 liquid-glass rounded-full mb-6">
        <button type="button" id="toggle-lost" onclick="setModalType('LOST')" class="py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 bg-white text-black transition">
          <i data-lucide="arrow-down-left" class="w-3.5 h-3.5"></i>
          <span>I lost something</span>
        </button>
        <button type="button" id="toggle-found" onclick="setModalType('FOUND')" class="py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 text-neutral-300 hover:text-white transition">
          <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
          <span>I found something</span>
        </button>
      </div>

      <form id="create-report-form" onsubmit="submitReport(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1">Your Name or Alias</label>
          <input required id="form-reporter" type="text" placeholder="e.g. Alex Morgan" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1">Item Title</label>
          <input required id="form-title" type="text" placeholder="e.g. Blue Bellroy Transit Backpack" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-neutral-300 mb-1">Category</label>
            <select required id="form-category" class="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
              <option value="Electronics">Electronics</option>
              <option value="Keys">Keys & Access</option>
              <option value="Bags">Bags & Backpacks</option>
              <option value="Wallets">Wallets & Cards</option>
              <option value="Jewelry">Jewelry & Watches</option>
              <option value="Clothing">Clothing</option>
              <option value="Pets">Pets</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-neutral-300 mb-1">Date</label>
            <input required id="form-date" type="date" class="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-amber-300">
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1">Location or Landmark</label>
          <input required id="form-location" type="text" placeholder="e.g. Central Library 2nd Floor, near café" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1">Photo URL (Optional)</label>
          <input id="form-photo" type="url" placeholder="https://images.unsplash.com/..." class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1">Description</label>
          <textarea required id="form-desc" rows="3" placeholder="Color, brand, distinctive marks, keychains, scratches..." class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-amber-300"></textarea>
        </div>

        <div id="private-detail-wrap">
          <label class="block text-xs font-medium text-amber-300 mb-1">
            Secret Verification Detail <span class="text-neutral-400 font-normal">(for lost reports — keeps private)</span>
          </label>
          <input id="form-private-detail" type="text" placeholder="e.g. sticker on back, initials inside, USB drive in pocket" class="w-full bg-amber-500/[0.05] border border-amber-400/30 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-300">
          <span class="text-[11px] text-neutral-400 block mt-1">Only you will know this detail — used to confirm you're the real owner.</span>
        </div>

        <div class="pt-4 flex items-center justify-end gap-3 border-t border-white/10">
          <button type="button" onclick="closeReportModal()" class="px-5 py-2.5 rounded-full text-xs font-medium text-neutral-400 hover:text-white transition">Cancel</button>
          <button type="submit" class="liquid-glass-strong rounded-full px-6 py-2.5 text-xs font-semibold text-white bg-amber-500/20 hover:bg-amber-500/30 border border-amber-300/40 transition flex items-center gap-2">
            <span>Publish Report</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal 2: Match Verification & Private Chat Demo -->
  <div id="match-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="liquid-glass-strong rounded-3xl max-w-2xl w-full p-6 md:p-8 border border-white/20 max-h-[90vh] overflow-y-auto shadow-2xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          <span class="text-xs uppercase font-semibold tracking-wider text-amber-300 font-display">VERIFIED MATCH WORKSPACE</span>
        </div>
        <button onclick="closeMatchModal()" class="w-8 h-8 rounded-full liquid-glass flex items-center justify-center text-neutral-400 hover:text-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <h3 class="text-3xl font-heading italic text-white mb-2" id="modal-match-title">
        Match Confidence: 94%
      </h3>
      <p class="text-xs md:text-sm text-neutral-300 font-light mb-6">
        Compare details between the reported Lost item and Found item below, then verify privately.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div class="liquid-glass rounded-2xl p-4 border border-rose-500/20">
          <span class="text-xs font-semibold text-rose-300 block mb-1">LOST REPORT</span>
          <h4 class="font-bold text-white text-sm" id="modal-lost-title">Black Leather Bi-Fold Wallet</h4>
          <p class="text-xs text-neutral-400 mt-1" id="modal-lost-desc">Lost at Campus Library 3rd floor. Has student ID & loyalty cards.</p>
          <div class="text-[11px] text-neutral-500 mt-2">Reported by Alex • Oct 5</div>
        </div>
        <div class="liquid-glass rounded-2xl p-4 border border-emerald-500/20">
          <span class="text-xs font-semibold text-emerald-300 block mb-1">FOUND REPORT</span>
          <h4 class="font-bold text-white text-sm" id="modal-found-title">Dark Leather Wallet</h4>
          <p class="text-xs text-neutral-400 mt-1" id="modal-found-desc">Found near Library Study Desks. Handed in at desk.</p>
          <div class="text-[11px] text-neutral-500 mt-2">Found by Sam • Oct 6</div>
        </div>
      </div>

      <div id="verify-box" class="liquid-glass rounded-2xl p-5 border border-amber-300/30 mb-6 bg-amber-500/[0.04]">
        <div class="flex items-center gap-2 mb-2 text-amber-300 font-semibold text-sm">
          <i data-lucide="key-round" class="w-4 h-4"></i>
          <span>Secret Detail Verification</span>
        </div>
        <p class="text-xs text-neutral-300 mb-3">
          To protect everyone’s belongings, confirm the secret detail recorded by the owner.
          <span class="text-neutral-400 block mt-0.5" id="verify-modal-hint">(Seed Demo: secret detail is <strong>small blue stitch</strong>)</span>
        </p>
        <div class="flex items-center gap-2">
          <input id="verify-input" type="text" placeholder="Enter secret verification detail..." class="flex-1 bg-black/40 border border-white/20 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-amber-300">
          <button onclick="testVerify()" class="liquid-glass-strong rounded-xl px-4 py-2 text-xs font-semibold text-white bg-amber-500/20 hover:bg-amber-500/30 transition">Verify</button>
        </div>
        <div id="verify-feedback" class="text-xs mt-2 hidden"></div>
      </div>

      <div id="chat-section" class="liquid-glass rounded-2xl p-5 border border-white/10 hidden mb-6">
        <div class="flex items-center justify-between text-xs text-neutral-400 mb-4 pb-2 border-b border-white/10">
          <span class="flex items-center gap-1.5 text-emerald-300">
            <i data-lucide="lock" class="w-3.5 h-3.5"></i>
            Encrypted Direct Channel
          </span>
          <span>Arrange Public Hand-off</span>
        </div>
        <div class="space-y-3 mb-4 max-h-48 overflow-y-auto" id="chat-messages">
          <div class="p-3 rounded-xl bg-white/5 text-xs text-neutral-200">
            <span class="text-[10px] text-neutral-400 block font-semibold">Sam (Finder) • 10:42 AM</span>
            Hey! I have your wallet safe. Can meet by the library main lobby around 2 PM.
          </div>
          <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-300/20 text-xs text-amber-100 ml-6">
            <span class="text-[10px] text-amber-300 block font-semibold">You (Owner) • 10:45 AM</span>
            Thank you so much! 2 PM at the main lobby works perfectly. See you there!
          </div>
        </div>
        <div class="flex items-center gap-2">
          <input id="chat-input" type="text" placeholder="Reply to arrange hand-off..." class="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-amber-300">
          <button onclick="sendChatMessage()" class="liquid-glass rounded-xl px-4 py-2 text-xs font-semibold text-white hover:bg-white/10 transition">Send</button>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-white/10">
        <div class="text-xs text-neutral-400">
          Status: <span id="match-status" class="text-amber-300 font-semibold">Awaiting Verification</span>
        </div>
        <button onclick="confirmHandoff()" id="btn-confirm-return" disabled class="liquid-glass rounded-full px-5 py-2 text-xs font-semibold text-neutral-500 cursor-not-allowed transition">
          Confirm Safe Return
        </button>
      </div>
    </div>
  </div>

  <!-- Modal 3: Instant Lost Item Social Notice & Poster Generator -->
  <div id="poster-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="liquid-glass-strong rounded-3xl max-w-2xl w-full p-6 md:p-8 border border-white/20 max-h-[92vh] overflow-y-auto shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase font-semibold tracking-wider text-amber-300 font-display">SOCIAL POSTER GENERATOR</span>
        </div>
        <button onclick="closePosterModal()" class="w-8 h-8 rounded-full liquid-glass flex items-center justify-center text-neutral-400 hover:text-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <p class="text-xs text-neutral-400 mb-6">
        Ready-to-share flyer for WhatsApp groups, Instagram Stories, and print boards with zero-knowledge claim QR code.
      </p>

      <!-- The Live Poster Rendered Preview -->
      <div class="flex justify-center mb-6">
        <div id="poster-canvas-wrap" class="w-full max-w-md bg-white text-black rounded-2xl p-6 shadow-2xl border-4 border-amber-400 relative overflow-hidden font-sans">
          <!-- Poster Emergency Header -->
          <div class="bg-black text-amber-300 text-center py-2.5 px-4 rounded-xl mb-4 font-black tracking-widest text-lg uppercase flex items-center justify-center gap-2">
            <span>🚨 HAVE YOU SEEN THIS? 🚨</span>
          </div>

          <!-- Item Title & Status -->
          <div class="text-center mb-3">
            <h2 class="text-2xl font-black text-black leading-tight uppercase" id="poster-title">APPLE AIRPODS PRO</h2>
            <div class="inline-block bg-rose-100 text-rose-700 px-3 py-0.5 rounded-full text-xs font-bold mt-1" id="poster-type-badge">
              MISSING / LOST ITEM
            </div>
          </div>

          <!-- Poster Image -->
          <div class="w-full h-44 bg-neutral-100 rounded-xl overflow-hidden mb-3 border border-neutral-300">
            <img id="poster-img" src="https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=600&q=80" alt="" class="w-full h-full object-cover">
          </div>

          <!-- Key Details -->
          <div class="bg-neutral-100 rounded-xl p-3 text-xs mb-4 space-y-1 text-neutral-800">
            <div><strong>Last Seen:</strong> <span id="poster-location">Central Station, Platform 3</span></div>
            <div><strong>Date:</strong> <span id="poster-date">October 5, 2026</span></div>
            <div class="text-[11px] text-neutral-600 line-clamp-2 mt-1" id="poster-desc">
              White MagSafe case with small scratch on the hinge. Contains personal initials.
            </div>
          </div>

          <!-- QR Code & Instructions -->
          <div class="flex items-center gap-4 bg-amber-50 rounded-xl p-3 border border-amber-200">
            <!-- Simulated QR Code SVG -->
            <svg class="w-20 h-20 bg-white p-1 rounded-lg border border-neutral-300 shrink-0" viewBox="0 0 100 100" fill="black">
              <!-- Corner Markers -->
              <rect x="5" y="5" width="28" height="28" fill="black"/>
              <rect x="9" y="9" width="20" height="20" fill="white"/>
              <rect x="13" y="13" width="12" height="12" fill="black"/>
              
              <rect x="67" y="5" width="28" height="28" fill="black"/>
              <rect x="71" y="9" width="20" height="20" fill="white"/>
              <rect x="75" y="13" width="12" height="12" fill="black"/>
              
              <rect x="5" y="67" width="28" height="28" fill="black"/>
              <rect x="9" y="71" width="20" height="20" fill="white"/>
              <rect x="13" y="75" width="12" height="12" fill="black"/>
              
              <!-- Data Pixels Mock -->
              <rect x="40" y="10" width="8" height="8"/>
              <rect x="52" y="18" width="8" height="8"/>
              <rect x="40" y="30" width="16" height="8"/>
              <rect x="10" y="40" width="12" height="8"/>
              <rect x="30" y="45" width="8" height="18"/>
              <rect x="50" y="45" width="18" height="8"/>
              <rect x="75" y="40" width="15" height="12"/>
              <rect x="45" y="65" width="10" height="15"/>
              <rect x="65" y="65" width="15" height="8"/>
              <rect x="80" y="80" width="10" height="10"/>
            </svg>
            <div class="text-[11px] text-neutral-800 leading-tight">
              <strong>Scan to Verify & Return</strong><br>
              <span class="text-neutral-600 text-[10px]">Private zero-knowledge channel. Phone numbers are protected. Powered by FindIt.</span>
            </div>
          </div>

          <!-- Tear-off Digital Tabs -->
          <div class="mt-4 pt-3 border-t-2 border-dashed border-neutral-400 flex justify-between text-[8px] font-mono text-neutral-600">
            <span class="border-r border-neutral-300 pr-2">✂ findit.org/claim/842</span>
            <span class="border-r border-neutral-300 px-2">✂ findit.org/claim/842</span>
            <span class="pl-2">✂ findit.org/claim/842</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap items-center justify-end gap-3 pt-3 border-t border-white/10">
        <button onclick="shareWhatsApp()" class="liquid-glass rounded-full px-5 py-2.5 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/20 transition flex items-center gap-1.5">
          <i data-lucide="share-2" class="w-3.5 h-3.5"></i>
          <span>Share to WhatsApp</span>
        </button>
        <button onclick="downloadPoster()" class="liquid-glass-strong rounded-full px-6 py-2.5 text-xs font-semibold text-white bg-amber-500/20 hover:bg-amber-500/30 border border-amber-300/40 transition flex items-center gap-1.5">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>Download Printable Notice</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal 4: Item Details & Verification Claim Modal -->
  <div id="item-detail-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="liquid-glass-strong rounded-3xl max-w-xl w-full p-6 md:p-8 border border-white/20 max-h-[90vh] overflow-y-auto shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <span class="px-3 py-1 rounded-full text-xs font-bold" id="detail-type-pill">LOST</span>
        <button onclick="closeItemDetailModal()" class="w-8 h-8 rounded-full liquid-glass flex items-center justify-center text-neutral-400 hover:text-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="w-full h-56 rounded-2xl overflow-hidden bg-neutral-900 mb-6 border border-white/10">
        <img id="detail-img" src="" alt="" class="w-full h-full object-cover">
      </div>

      <h3 class="text-2xl font-bold text-white mb-2" id="detail-title">Item Title</h3>
      <p class="text-xs text-neutral-300 leading-relaxed mb-6" id="detail-desc">Full item description</p>

      <div class="grid grid-cols-2 gap-3 text-xs mb-6">
        <div class="liquid-glass rounded-xl p-3">
          <span class="text-neutral-400 text-[10px] uppercase block">Location</span>
          <span class="text-white font-semibold flex items-center gap-1 mt-0.5" id="detail-location">Campus</span>
        </div>
        <div class="liquid-glass rounded-xl p-3">
          <span class="text-neutral-400 text-[10px] uppercase block">Date Logged</span>
          <span class="text-white font-semibold mt-0.5 block" id="detail-date">Oct 5, 2026</span>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <button onclick="openPosterModalFromDetail()" class="liquid-glass rounded-full px-4 py-2.5 text-xs font-semibold text-neutral-300 hover:text-white transition flex items-center gap-1.5">
          <i data-lucide="printer" class="w-3.5 h-3.5"></i>
          <span>Create Notice</span>
        </button>
        <button onclick="claimCurrentItem()" class="liquid-glass-strong rounded-full px-5 py-2.5 text-xs font-semibold text-white bg-amber-500/20 hover:bg-amber-500/30 border border-amber-300/40 transition flex items-center gap-1.5">
          <i data-lucide="shield-check" class="w-3.5 h-3.5 text-amber-300"></i>
          <span>I Own This (Verify Claim)</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal 5: QR Handover Scanner Simulation -->
  <div id="qr-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="liquid-glass-strong rounded-3xl max-w-md w-full p-6 md:p-8 border border-white/20 text-center shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <span class="text-xs font-semibold uppercase text-emerald-400 font-display">SAFE CUSTODY CHECK-IN</span>
        <button onclick="closeQRModal()" class="w-8 h-8 rounded-full liquid-glass flex items-center justify-center text-neutral-400 hover:text-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <h3 class="text-xl font-bold text-white mb-1" id="qr-desk-name">Campus Security Main Desk</h3>
      <p class="text-xs text-neutral-400 mb-6">Point camera at the desk’s official QR plaque to transfer custody.</p>

      <!-- Simulated Camera Viewfinder -->
      <div class="w-64 h-64 mx-auto rounded-2xl bg-neutral-900 border-2 border-emerald-400/60 relative overflow-hidden flex items-center justify-center mb-6">
        <div class="absolute inset-4 border border-dashed border-emerald-400/40 rounded-xl"></div>
        <div class="laser-line absolute inset-x-0 h-1 bg-emerald-400 shadow-[0_0_12px_#34d399]"></div>
        <i data-lucide="scan" class="w-16 h-16 text-emerald-400/30"></i>
      </div>

      <button onclick="simulateSuccessfulScan()" class="w-full liquid-glass-strong py-3 rounded-full text-xs font-semibold text-white bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-300/40 transition">
        Simulate Scan & Handover Confirmation
      </button>
    </div>
  </div>

  <!-- Real-time Community Toast Container -->
  <div id="toast-container" class="fixed bottom-6 right-6 z-40 pointer-events-none flex flex-col items-end gap-2"></div>

  <!-- ============================================================== -->
  <!-- 10. FOOTER -->
  <!-- ============================================================== -->
  <footer class="py-14 px-6 md:px-12 border-t border-white/10 bg-black/80 text-xs text-neutral-400 relative">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-3">
        <div class="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-amber-300">
          <i data-lucide="compass" class="w-4 h-4"></i>
        </div>
        <span class="font-display font-bold text-white text-base">findit</span>
        <span class="text-neutral-500">|</span>
        <span>A little kindness goes a long way.</span>
      </div>

      <div class="flex flex-wrap items-center gap-6">
        <span><i data-lucide="cpu" class="w-3.5 h-3.5 inline text-blue-400 mr-1"></i>Smart Matching Engine</span>
        <span><i data-lucide="database" class="w-3.5 h-3.5 inline text-emerald-400 mr-1"></i>Java Spring Boot + PostgreSQL</span>
        <a href="#overview" class="hover:text-white transition">Back to top ↑</a>
      </div>
    </div>
  </footer>

  <!-- ============================================================== -->
  <!-- AUTHENTICATION (LOGIN & SIGNUP) MODAL -->
  <!-- ============================================================== -->
  <div id="auth-modal" class="fixed inset-0 z-50 hidden grid place-items-center bg-black/80 backdrop-blur-xl p-4 overflow-y-auto">
    <div class="liquid-glass-strong rounded-3xl p-6 sm:p-8 max-w-md w-full relative border border-white/15 shadow-2xl animate-blur-in">
      <!-- Close Button -->
      <button onclick="closeAuthModal()" class="absolute top-5 right-5 w-8 h-8 rounded-full bg-white/5 hover:bg-white/15 flex items-center justify-center text-neutral-400 hover:text-white transition">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>

      <!-- Header Badge -->
      <div class="flex items-center gap-2 mb-2">
        <div class="w-8 h-8 rounded-full bg-amber-400/20 text-amber-300 flex items-center justify-center">
          <i data-lucide="shield-check" class="w-4 h-4"></i>
        </div>
        <span class="text-xs font-semibold tracking-wider text-amber-300 uppercase">FindIt Security Portal</span>
      </div>

      <!-- Title & Subtitle -->
      <h3 id="auth-modal-title" class="text-2xl font-bold font-display text-white mb-1">Welcome Back</h3>
      <p id="auth-modal-subtitle" class="text-xs text-neutral-400 mb-6">Access your reports, live matches, and secure community messages.</p>

      <!-- Tab Switcher -->
      <div class="liquid-glass rounded-2xl p-1 flex items-center gap-1 mb-6 text-xs font-semibold">
        <button id="auth-tab-login" onclick="switchAuthTab('login')" class="flex-1 py-2 rounded-xl bg-white/20 text-white font-semibold transition text-center shadow-md">
          Sign In
        </button>
        <button id="auth-tab-signup" onclick="switchAuthTab('signup')" class="flex-1 py-2 rounded-xl text-neutral-400 hover:text-white font-semibold transition text-center">
          Create Account
        </button>
      </div>

      <!-- Error Alert Banner -->
      <div id="auth-error-banner" class="hidden mb-4 p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5">
        <i data-lucide="alert-circle" class="w-4 h-4 text-rose-400 shrink-0 mt-0.5"></i>
        <span id="auth-error-text">Authentication failed. Please check your credentials.</span>
      </div>

      <!-- Success Alert Banner -->
      <div id="auth-success-banner" class="hidden mb-4 p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-start gap-2.5">
        <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 shrink-0 mt-0.5"></i>
        <span id="auth-success-text">Account created successfully! Logging you in...</span>
      </div>

      <!-- Login Form -->
      <form id="login-form" onsubmit="handleLoginSubmit(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Email Address</label>
          <div class="relative">
            <i data-lucide="mail" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="email" id="login-email" required placeholder="alex@example.com" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Password</label>
          <div class="relative">
            <i data-lucide="lock" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="password" id="login-password" required placeholder="••••••••" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-10 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
            <button type="button" onclick="togglePasswordVisibility('login-password', 'login-pwd-eye')" class="absolute right-3.5 top-3 text-neutral-500 hover:text-white transition">
              <i data-lucide="eye" id="login-pwd-eye" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <button type="submit" id="login-submit-btn" class="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-neutral-950 font-bold text-sm shadow-lg shadow-amber-500/20 hover:scale-[1.02] active:scale-[0.98] transition flex items-center justify-center gap-2 mt-6">
          <span>Sign In to FindIt</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </form>

      <!-- Signup Form -->
      <form id="signup-form" onsubmit="handleSignupSubmit(event)" class="hidden space-y-4">
        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Full Name</label>
          <div class="relative">
            <i data-lucide="user" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="text" id="signup-fullname" required maxlength="100" placeholder="Anaya Sharma" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Email Address</label>
          <div class="relative">
            <i data-lucide="mail" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="email" id="signup-email" required maxlength="120" oninput="validateSignupEmail()" placeholder="anaya@example.com" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
          </div>
          <p id="signup-email-feedback" class="text-[11px] text-rose-400 mt-1 hidden"></p>
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Password</label>
          <div class="relative">
            <i data-lucide="lock" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="password" id="signup-password" required maxlength="100" oninput="updatePasswordStrengthMeter()" placeholder="At least 8 chars" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-10 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
            <button type="button" onclick="togglePasswordVisibility('signup-password', 'signup-pwd-eye')" class="absolute right-3.5 top-3 text-neutral-500 hover:text-white transition">
              <i data-lucide="eye" id="signup-pwd-eye" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Password Strength Meter -->
          <div class="mt-2 space-y-1.5">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-neutral-400">Password Strength:</span>
              <span id="pwd-strength-label" class="font-semibold text-neutral-400">None</span>
            </div>
            <div class="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
              <div id="pwd-strength-bar" class="h-full w-0 bg-rose-500 transition-all duration-300"></div>
            </div>

            <!-- Requirements Checklist -->
            <div class="grid grid-cols-2 gap-1 text-[11px] pt-1 text-neutral-400">
              <div id="rule-length" class="flex items-center gap-1.5">
                <i data-lucide="circle" class="w-3 h-3 text-neutral-500"></i>
                <span>8+ characters</span>
              </div>
              <div id="rule-upper" class="flex items-center gap-1.5">
                <i data-lucide="circle" class="w-3 h-3 text-neutral-500"></i>
                <span>1+ Uppercase (A-Z)</span>
              </div>
              <div id="rule-lower" class="flex items-center gap-1.5">
                <i data-lucide="circle" class="w-3 h-3 text-neutral-500"></i>
                <span>1+ Lowercase (a-z)</span>
              </div>
              <div id="rule-symbol" class="flex items-center gap-1.5">
                <i data-lucide="circle" class="w-3 h-3 text-neutral-500"></i>
                <span>Number & Symbol</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-neutral-300 mb-1.5">Confirm Password</label>
          <div class="relative">
            <i data-lucide="lock-check" class="w-4 h-4 absolute left-3.5 top-3 text-neutral-500"></i>
            <input type="password" id="signup-confirm-password" required maxlength="100" oninput="checkPasswordMatch()" placeholder="Re-enter password" class="w-full bg-white/5 border border-white/10 rounded-2xl py-2.5 pl-10 pr-10 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/60 transition">
            <button type="button" onclick="togglePasswordVisibility('signup-confirm-password', 'signup-confirm-pwd-eye')" class="absolute right-3.5 top-3 text-neutral-500 hover:text-white transition">
              <i data-lucide="eye" id="signup-confirm-pwd-eye" class="w-4 h-4"></i>
            </button>
          </div>
          <p id="signup-match-feedback" class="text-[11px] text-rose-400 mt-1 hidden"></p>
        </div>

        <button type="submit" id="signup-submit-btn" class="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-neutral-950 font-bold text-sm shadow-lg shadow-amber-500/20 hover:scale-[1.02] active:scale-[0.98] transition flex items-center justify-center gap-2 mt-6">
          <span>Create Account</span>
          <i data-lucide="user-plus" class="w-4 h-4"></i>
        </button>
      </form>
    </div>
  </div>


  <!-- ============================================================== -->
  <!-- THREE.JS 3D SCENES: CHROMATIC GLASS HERO & REAL 3D GOLDEN KEY -->
  <!-- ============================================================== -->
  <script type="module">
    import * as THREE from 'three';
    import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

    // -------------------------------------------------------------
    // SCENE A: BACKGROUND 3D REFRACTIVE CHROMATIC GLASS
    // -------------------------------------------------------------
    const canvas = document.getElementById('hero-canvas');
    if (canvas) {
      const renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      renderer.setClearColor(0x000000, 0);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.autoClear = false;

      const camera = new THREE.PerspectiveCamera(32, window.innerWidth / window.innerHeight, 0.1, 100);
      camera.position.set(0, 0, 10);
      camera.lookAt(0, 0, 0);

      const quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

      // Offscreen canvas for Headline Refraction
      const textCanvas = document.createElement('canvas');
      const textCtx = textCanvas.getContext('2d');
      const bgTexture = new THREE.CanvasTexture(textCanvas);
      bgTexture.colorSpace = THREE.SRGBColorSpace;
      bgTexture.minFilter = THREE.LinearFilter;
      bgTexture.magFilter = THREE.LinearFilter;
      bgTexture.generateMipmaps = false;

      const bgScene = new THREE.Scene();
      const bgMat = new THREE.ShaderMaterial({
        uniforms: { uTex: { value: bgTexture } },
        vertexShader: `
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = vec4(position.xy, 0.0, 1.0);
          }
        `,
        fragmentShader: `
          uniform sampler2D uTex;
          varying vec2 vUv;
          void main() {
            gl_FragColor = texture2D(uTex, vUv);
            #include <colorspace_fragment>
          }
        `,
        depthTest: false,
        depthWrite: false
      });
      const bgQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), bgMat);
      bgQuad.frustumCulled = false;
      bgScene.add(bgQuad);

      let rtBack = new THREE.WebGLRenderTarget(1, 1, {
        type: THREE.HalfFloatType,
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter
      });
      let rtFront = new THREE.WebGLRenderTarget(1, 1, {
        type: THREE.HalfFloatType,
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter
      });

      // 6-Band Chromatic Dispersion Glass Shader
      const glassVertexShader = `
        varying vec3 vNormal;
        varying vec3 vEye;
        void main() {
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vec4 mvPos = viewMatrix * worldPos;
          gl_Position = projectionMatrix * mvPos;
          vNormal = normalize(normalMatrix * normal);
          vEye = normalize(mvPos.xyz);
        }
      `;

      const glassFragmentShader = `
        uniform sampler2D uTexture;
        uniform vec2 uResolution;
        uniform float uIorR, uIorY, uIorG, uIorC, uIorB, uIorP;
        uniform float uRefractPower, uChromatic, uSaturation, uShininess, uDiffuseness, uFresnelPower;
        uniform vec3 uLight;
        uniform float uBackside;

        varying vec3 vNormal, vEye;

        float specLight(vec3 lightDir, vec3 normal, vec3 eye, float shininess, float diff) {
          vec3 l = normalize(-lightDir);
          vec3 v = -eye;
          vec3 h = normalize(l + v);
          return pow(max(dot(normal, h), 0.0), shininess) + max(0.0, dot(normal, l)) * diff;
        }

        void main() {
          vec2 uv = gl_FragCoord.xy / uResolution;
          vec3 n = normalize(vNormal);
          if (uBackside > 0.5) n = -n;
          vec3 eye = normalize(vEye);

          const int LOOP = 16;
          vec3 colorAcc = vec3(0.0);

          for (int i = 0; i < LOOP; i++) {
            float slide = float(i) / float(LOOP) * 0.045;

            vec3 refrR = refract(eye, n, 1.0 / uIorR);
            vec3 refrY = refract(eye, n, 1.0 / uIorY);
            vec3 refrG = refract(eye, n, 1.0 / uIorG);
            vec3 refrC = refract(eye, n, 1.0 / uIorC);
            vec3 refrB = refract(eye, n, 1.0 / uIorB);
            vec3 refrP = refract(eye, n, 1.0 / uIorP);

            vec4 sR = texture2D(uTexture, uv + refrR.xy * (uRefractPower + slide * 1.0) * uChromatic);
            vec4 sY = texture2D(uTexture, uv + refrY.xy * (uRefractPower + slide * 1.0) * uChromatic);
            vec4 sG = texture2D(uTexture, uv + refrG.xy * (uRefractPower + slide * 2.0) * uChromatic);
            vec4 sC = texture2D(uTexture, uv + refrC.xy * (uRefractPower + slide * 2.5) * uChromatic);
            vec4 sB = texture2D(uTexture, uv + refrB.xy * (uRefractPower + slide * 3.0) * uChromatic);
            vec4 sP = texture2D(uTexture, uv + refrP.xy * (uRefractPower + slide * 1.0) * uChromatic);

            float r = sR.r * 0.5;
            float y = (sY.r * 2.0 + sY.g * 2.0 - sY.b) / 6.0;
            float g = sG.g * 0.5;
            float c = (sC.g * 2.0 + sC.b * 2.0 - sC.r) / 6.0;
            float b = sB.b * 0.5;
            float p = (sP.b * 2.0 + sP.r * 2.0 - sP.g) / 6.0;

            float R = r + (2.0 * p + 2.0 * y - c) / 3.0;
            float G = g + (2.0 * y + 2.0 * c - p) / 3.0;
            float B = b + (2.0 * c + 2.0 * p - y) / 3.0;

            colorAcc += vec3(R, G, B);
          }

          vec3 color = colorAcc / float(LOOP);
          float luma = dot(color, vec3(0.2125, 0.7154, 0.0721));
          color = mix(vec3(luma), color, uSaturation);

          float s1 = specLight(uLight, n, eye, uShininess, uDiffuseness);
          float s2 = specLight(vec3(1.0, 1.0, -1.0), n, eye, uShininess * 0.6, uDiffuseness * 0.5);
          color += (s1 + 0.6 * s2) * (uBackside > 0.5 ? 0.35 : 1.0);

          float f = pow(clamp(1.0 + dot(eye, n), 0.0, 1.0), uFresnelPower);
          color = mix(color, vec3(1.0, 0.95, 0.8), f * (uBackside > 0.5 ? 0.25 : 0.55));

          color += vec3(0.005, 0.006, 0.008);
          gl_FragColor = vec4(color, 1.0);
          #include <colorspace_fragment>
        }
      `;

      function makeGlassMaterial(isBack) {
        return new THREE.ShaderMaterial({
          vertexShader: glassVertexShader,
          fragmentShader: glassFragmentShader,
          uniforms: {
            uTexture: { value: null },
            uResolution: { value: new THREE.Vector2() },
            uIorR: { value: 1.15 },
            uIorY: { value: 1.16 },
            uIorG: { value: 1.18 },
            uIorC: { value: 1.22 },
            uIorB: { value: 1.22 },
            uIorP: { value: 1.22 },
            uRefractPower: { value: isBack ? 0.22 : 0.30 },
            uChromatic: { value: 0.5 },
            uSaturation: { value: 1.12 },
            uShininess: { value: 85.0 },
            uDiffuseness: { value: 0.03 },
            uFresnelPower: { value: 4.8 },
            uLight: { value: new THREE.Vector3(-1.0, 1.0, 1.0).normalize() },
            uBackside: { value: isBack ? 1.0 : 0.0 }
          },
          side: isBack ? THREE.BackSide : THREE.FrontSide,
          depthWrite: !isBack,
          depthTest: true
        });
      }

      const backMat = makeGlassMaterial(true);
      const frontMat = makeGlassMaterial(false);

      const mainScene = new THREE.Scene();
      const pivot = new THREE.Group();
      const spinner = new THREE.Group();
      spinner.rotation.set(-0.35, 0.75, 0.15);
      pivot.add(spinner);
      mainScene.add(pivot);

      let currentMesh = null;
      function setGeometry(geom) {
        geom.computeBoundingBox();
        const bbox = geom.boundingBox;
        const sz = new THREE.Vector3();
        bbox.getSize(sz);
        geom.center();
        const maxD = Math.max(sz.x, sz.y, sz.z);
        geom.scale(1 / maxD, 1 / maxD, 1 / maxD);
        
        if (currentMesh) {
          spinner.remove(currentMesh);
        }
        currentMesh = new THREE.Mesh(geom, frontMat);
        spinner.add(currentMesh);
      }

      // Initial Rounded Cube
      setGeometry(new RoundedBoxGeometry(1.05, 1.05, 1.05, 8, 0.14));

      // Global function to switch shape
      window.switch3DShape = (type) => {
        document.querySelectorAll('#shape-btn-cube, #shape-btn-octa, #shape-btn-torus').forEach(b => {
          b.className = 'px-2.5 py-1 rounded-xl text-neutral-400 hover:text-white text-[11px] font-semibold transition';
        });
        const activeBtn = document.getElementById(`shape-btn-${type}`);
        if (activeBtn) activeBtn.className = 'px-2.5 py-1 rounded-xl bg-white/20 text-white text-[11px] font-semibold transition';

        if (type === 'cube') {
          setGeometry(new RoundedBoxGeometry(1.05, 1.05, 1.05, 8, 0.14));
        } else if (type === 'octa') {
          setGeometry(new THREE.OctahedronGeometry(0.85, 0));
        } else if (type === 'torus') {
          setGeometry(new THREE.TorusGeometry(0.65, 0.28, 24, 48));
        }
        playChime(660);
      };

      // Draw background text for refraction
      function drawText(w, h, dpr) {
        textCanvas.width = Math.floor(w * dpr);
        textCanvas.height = Math.floor(h * dpr);

        textCtx.save();
        textCtx.scale(dpr, dpr);
        textCtx.fillStyle = '#030407';
        textCtx.fillRect(0, 0, w, h);

        const mobile = (w < 768) || (w / h < 1);
        let fs = Math.min(h * 0.18, w * (mobile ? 0.22 : 0.11));
        textCtx.font = `800 ${fs}px Poppins`;

        const lines = ['FINDIT', 'LOST & FOUND', 'RECONNECT'];
        const cx = w * (mobile ? 0.5 : 0.72);
        const cy = h * (mobile ? 0.5 : 0.48);
        const gap = fs * 1.05;

        textCtx.fillStyle = '#222533';
        textCtx.textAlign = 'center';
        textCtx.textBaseline = 'middle';

        for (let i = 0; i < lines.length; i++) {
          textCtx.fillText(lines[i], cx, cy + (i - 1) * gap);
        }
        textCtx.restore();
        bgTexture.needsUpdate = true;
      }

      function layout() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);

        renderer.setPixelRatio(dpr);
        renderer.setSize(w, h, false);

        const bw = Math.floor(w * dpr);
        const bh = Math.floor(h * dpr);
        rtBack.setSize(bw, bh);
        rtFront.setSize(bw, bh);

        backMat.uniforms.uResolution.value.set(bw, bh);
        frontMat.uniforms.uResolution.value.set(bw, bh);

        camera.aspect = w / h;
        camera.updateProjectionMatrix();

        drawText(w, h, dpr);

        const fovRad = (camera.fov * Math.PI) / 180;
        const visH = 2 * Math.tan(fovRad / 2) * 10;
        const visW = visH * camera.aspect;

        const mobile = (w < 768);
        const sx = mobile ? 0.5 : 0.72;
        const sy = mobile ? 0.45 : 0.48;

        pivot.position.set((sx - 0.5) * visW, (0.5 - sy) * visH, 0);
        const px = Math.min(h * 0.42, w * (mobile ? 0.42 : 0.28));
        const s = (px / h) * visH;
        pivot.scale.set(s, s, s);
      }

      window.addEventListener('resize', layout);
      layout();

      // Drag to rotate with inertia & physics
      let isDragging = false;
      let lastX = 0, lastY = 0;
      let velX = 0, velY = 0;
      let targetSpinY = 0;
      let timeSinceDrag = 0;

      const rotX = new THREE.Vector3(1, 0, 0);
      const rotY = new THREE.Vector3(0, 1, 0);
      const q = new THREE.Quaternion();

      function applyRot(dx, dy) {
        q.setFromAxisAngle(rotY, dx);
        spinner.quaternion.premultiply(q);
        q.setFromAxisAngle(rotX, dy);
        spinner.quaternion.premultiply(q);
      }

      canvas.addEventListener('pointerdown', (e) => {
        isDragging = true;
        targetSpinY = 0;
        lastX = e.clientX;
        lastY = e.clientY;
        velX = 0; velY = 0;
        canvas.setPointerCapture(e.pointerId);
        canvas.classList.add('dragging');
        timeSinceDrag = 0;
      });

      canvas.addEventListener('pointermove', (e) => {
        if (!isDragging) return;
        const dx = (e.clientX - lastX) * 0.008;
        const dy = (e.clientY - lastY) * 0.008;
        lastX = e.clientX;
        lastY = e.clientY;
        applyRot(dx, dy);
        velX = dx;
        velY = dy;
        timeSinceDrag = 0;
      });

      const stopDrag = (e) => {
        if (!isDragging) return;
        isDragging = false;
        canvas.classList.remove('dragging');
        try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
      };
      canvas.addEventListener('pointerup', stopDrag);
      canvas.addEventListener('pointercancel', stopDrag);

      let lastTime = performance.now();
      function animate(now) {
        requestAnimationFrame(animate);
        const dt = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        if (!isDragging) {
          timeSinceDrag += dt;
          if (Math.abs(targetSpinY) > 0.0005) {
            const step = targetSpinY * Math.min(1, 0.09 * dt * 60);
            targetSpinY -= step;
            applyRot(step, 0);
          } else {
            targetSpinY = 0;
            if (Math.abs(velX) > 0.00001 || Math.abs(velY) > 0.00001) {
              applyRot(velX, velY);
              const damp = Math.pow(0.94, dt * 60);
              velX *= damp; velY *= damp;
            }
            if (timeSinceDrag > 0.6) {
              const blend = Math.min((timeSinceDrag - 0.6) / 1.0, 1.0);
              applyRot(0.0035 * blend * (dt * 60), 0.0012 * blend * (dt * 60));
            }
          }
        }

        if (!currentMesh) return;

        // Dual Pass Refraction Pipeline
        renderer.setRenderTarget(rtBack);
        renderer.clear();
        renderer.render(bgScene, quadCamera);

        backMat.uniforms.uTexture.value = rtBack.texture;
        currentMesh.material = backMat;

        renderer.setRenderTarget(rtFront);
        renderer.clear();
        renderer.render(bgScene, quadCamera);
        renderer.render(mainScene, camera);

        frontMat.uniforms.uTexture.value = rtFront.texture;
        currentMesh.material = frontMat;

        renderer.setRenderTarget(null);
        renderer.clear();
        renderer.render(bgScene, quadCamera);
        renderer.clearDepth();
        renderer.render(mainScene, camera);
      }

      requestAnimationFrame(animate);
    }

  </script>

  <!-- ============================================================== -->
  <!-- APPLICATION STATE, SIMULATOR, HEATMAP & AUDIO SCRIPTS -->
  <!-- ============================================================== -->
  <script>
    // Web Audio Synthesizer Engine
    let audioContext = null;
    let audioEnabled = true;

    function initAudio() {
      if (!audioContext) {
        try {
          audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (_) {}
      }
    }

    function toggleAudio() {
      audioEnabled = !audioEnabled;
      const btn = document.getElementById('audio-toggle-btn');
      const icon = document.getElementById('audio-icon');
      if (audioEnabled) {
        initAudio();
        icon.setAttribute('data-lucide', 'volume-2');
        btn.classList.add('text-amber-300');
        playChime(600);
      } else {
        icon.setAttribute('data-lucide', 'volume-x');
        btn.classList.remove('text-amber-300');
      }
      lucide.createIcons();
    }

    function playChime(freq = 520, type = 'sine') {
      if (!audioEnabled) return;
      initAudio();
      if (!audioContext) return;
      if (audioContext.state === 'suspended') audioContext.resume();

      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioContext.currentTime);

      gain.gain.setValueAtTime(0.08, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.5);

      osc.connect(gain);
      gain.connect(audioContext.destination);

      osc.start();
      osc.stop(audioContext.currentTime + 0.5);
    }

    function playSuccessChime() {
      playChime(523, 'triangle');
      setTimeout(() => playChime(659, 'triangle'), 100);
      setTimeout(() => playChime(783, 'triangle'), 200);
    }

    // ============================================================
    // API BASE URL & SECURITY UTILITIES
    // ============================================================
    const API_BASE = '/api';

    // HTML Escape to eliminate Stored XSS vulnerabilities
    function escapeHtml(str) {
      if (str == null) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function sanitizeUrl(url) {
      if (!url) return '';
      const trimmed = String(url).trim();
      if (/^https?:\\/\\//i.test(trimmed)) {
        return escapeHtml(trimmed);
      }
      return '';
    }

    // Community Reports & Verified Matches Data
    let reportsData = [];
    let matchesData = [];
    let currentActiveMatchId = 1;
    let currentActiveMatch = null;

    async function loadMatches() {
      try {
        const res = await fetch(`${API_BASE}/matches`);
        if (res.ok) {
          matchesData = await res.json();
          renderReports();
        }
      } catch (err) {
        console.warn('Could not load matches from API:', err);
      }
    }

    async function fetchReports() {
      try {
        const params = new URLSearchParams();
        if (currentTypeFilter !== 'ALL') params.set('type', currentTypeFilter);
        if (currentSearchTerm.trim()) params.set('q', currentSearchTerm.trim());
        const url = `${API_BASE}/items?${params.toString()}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const items = await res.json();
        reportsData = items.map(normalizeItem);
        renderReports();
      } catch (err) {
        console.warn('Could not reach API, showing empty board:', err);
        reportsData = [];
        renderReports();
      }
    }

    function normalizeItem(item) {
      return {
        id: item.id,
        title: item.title,
        type: item.type,       // LOST | FOUND
        category: item.category,
        location: item.location,
        date: item.itemDate ? item.itemDate.slice(0, 10) : '',
        status: item.status,   // OPEN | MATCHED | RETURNED
        description: item.description,
        photoUrl: item.photoUrl || null,
        reporter: item.reporter,
      };
    }

    async function loadDashboard() {
      try {
        const res = await fetch(`${API_BASE}/dashboard`);
        if (!res.ok) return;
        const d = await res.json();
        const el = (id) => document.getElementById(id);
        if (el('stat-total')) el('stat-total').innerText = d.totalReports.toLocaleString();
        if (el('stat-open')) el('stat-open').innerText = d.openReports.toLocaleString();
        if (el('stat-matches')) el('stat-matches').innerText = d.potentialMatches.toLocaleString();
        if (el('stat-returned')) el('stat-returned').innerText = d.returnedItems.toLocaleString();
      } catch (err) {
        console.warn('Dashboard load failed:', err);
      }
    }

    let currentTypeFilter = 'ALL';
    let currentCategoryFilter = 'ALL';
    let currentSearchTerm = '';
    let modalCurrentType = 'LOST';
    let selectedDetailItem = null;

    function renderReports() {
      const grid = document.getElementById('reports-grid');
      if (!grid) return;

      const filtered = reportsData.filter(item => {
        const matchesType = currentTypeFilter === 'ALL' || item.type === currentTypeFilter;
        const matchesCat = currentCategoryFilter === 'ALL' || item.category === currentCategoryFilter;
        const search = currentSearchTerm.toLowerCase();
        const matchesSearch = !search ||
          item.title.toLowerCase().includes(search) ||
          item.location.toLowerCase().includes(search) ||
          item.description.toLowerCase().includes(search) ||
          item.category.toLowerCase().includes(search);

        return matchesType && matchesCat && matchesSearch;
      });

      document.getElementById('results-count').innerText = `Showing ${filtered.length} ${filtered.length === 1 ? 'report' : 'reports'}`;

      if (filtered.length === 0) {
        grid.innerHTML = `
          <div class="col-span-full py-16 text-center liquid-glass rounded-2xl p-8">
            <div class="w-12 h-12 rounded-full liquid-glass mx-auto flex items-center justify-center text-neutral-400 mb-3">
              <i data-lucide="search-x" class="w-6 h-6"></i>
            </div>
            <h4 class="text-xl font-bold text-white mb-1">No matching reports found</h4>
            <p class="text-sm text-neutral-400 mb-4">Try clearing your filters or search keywords, or submit a report to let others help.</p>
            <button onclick="openReportModal('LOST')" class="liquid-glass-strong rounded-full px-5 py-2 text-xs font-semibold text-white">Create a Report</button>
          </div>
        `;
        lucide.createIcons();
        return;
      }

      grid.innerHTML = filtered.map(item => {
        const itemMatch = matchesData.find(m => m.lostItemId === item.id || m.foundItemId === item.id);
        const safePhoto = sanitizeUrl(item.photoUrl);
        const safeTitle = escapeHtml(item.title);
        const safeDesc = escapeHtml(item.description);
        const safeLoc = escapeHtml(item.location);
        const safeCat = escapeHtml(item.category);
        const safeDate = escapeHtml(item.date);

        return `
        <article class="liquid-card liquid-glass rounded-2xl overflow-hidden flex flex-col justify-between group hover:border-white/30 transition-all duration-300 hover:-translate-y-1">
          <!-- Card Image / Header -->
          <div class="relative h-48 w-full bg-neutral-900 overflow-hidden">
            ${safePhoto ? `
              <img src="${safePhoto}" alt="${safeTitle}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-90 group-hover:opacity-100">
            ` : `
              <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-neutral-800 to-neutral-950 text-amber-200/50 font-heading italic text-6xl">
                ${safeTitle.slice(0, 1) || '?'}
              </div>
            `}
            <div class="absolute inset-0 bg-gradient-to-t from-[#030407] via-transparent to-transparent opacity-80"></div>
            
            <!-- Type Pill -->
            <div class="absolute top-3 left-3">
              <span class="px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 backdrop-blur-md ${item.type === 'LOST' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}">
                <i data-lucide="${item.type === 'LOST' ? 'arrow-down-left' : 'arrow-up-right'}" class="w-3.5 h-3.5"></i>
                ${item.type === 'LOST' ? 'LOST' : 'FOUND'}
              </span>
            </div>

            <!-- Status Pill -->
            <div class="absolute top-3 right-3">
              <span class="px-2.5 py-1 rounded-full text-[11px] font-medium backdrop-blur-md ${item.status === 'RETURNED' ? 'bg-amber-400/20 text-amber-300 border border-amber-300/30' : item.status === 'MATCHED' ? 'bg-blue-400/20 text-blue-300 border border-blue-400/30' : 'bg-neutral-800/80 text-neutral-300 border border-white/10'}">
                ${item.status === 'RETURNED' ? 'Reunited Home' : item.status === 'MATCHED' ? 'Possible Match' : 'Still Looking'}
              </span>
            </div>
          </div>

          <!-- Body -->
          <div class="p-5 flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between text-xs text-neutral-400 mb-2">
                <span class="text-amber-300/90 font-medium">${safeCat}</span>
                <span>${safeDate}</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2 group-hover:text-amber-200 transition-colors">${safeTitle}</h3>
              <p class="text-xs text-neutral-300 font-light leading-relaxed line-clamp-2 mb-4">${safeDesc}</p>
            </div>

            <div class="pt-3 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400">
              <div class="flex items-center gap-1.5 truncate max-w-[50%]">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-amber-300 shrink-0"></i>
                <span class="truncate">${safeLoc}</span>
              </div>
              <div class="flex items-center gap-2">
                ${itemMatch ? `
                  <button onclick="openMatchDemoModal(${itemMatch.id})" title="View Match Workspace" class="px-2 py-1 rounded-lg liquid-glass text-amber-300 hover:bg-amber-400/20 transition flex items-center gap-1 text-[11px] font-semibold border border-amber-300/30">
                    <i data-lucide="sparkles" class="w-3 h-3"></i>
                    <span>${itemMatch.scorePercent}%</span>
                  </button>
                ` : ''}
                <button onclick="openPosterModal(${item.id})" title="Create Social Poster" class="p-1.5 rounded-lg liquid-glass hover:text-amber-300 transition">
                  <i data-lucide="printer" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="inspectReport(${item.id})" class="text-xs font-semibold text-white hover:text-amber-300 flex items-center gap-1 transition">
                  <span>Details</span>
                  <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
          </div>
        </article>
      `;
      }).join('');

      lucide.createIcons();
    }

    // Filter Handlers
    function filterType(type) {
      currentTypeFilter = type;
      document.querySelectorAll('.type-filter-btn').forEach(btn => {
        if (btn.dataset.type === type) {
          btn.className = 'type-filter-btn px-4 py-2 rounded-full text-xs font-semibold bg-white text-black transition';
        } else {
          btn.className = 'type-filter-btn px-4 py-2 rounded-full text-xs font-semibold text-neutral-300 hover:text-white hover:bg-white/10 transition';
        }
      });
      fetchReports();
      playChime(500);
    }

    function filterCategory(cat) {
      currentCategoryFilter = cat;
      document.querySelectorAll('.cat-pill').forEach(btn => {
        btn.classList.remove('active', 'liquid-glass-strong', 'border', 'border-amber-300/40', 'text-white');
        btn.classList.add('liquid-glass', 'text-neutral-300');
        if (btn.innerText.includes(cat) || (cat === 'ALL' && btn.innerText.includes('All Categories'))) {
          btn.classList.add('active', 'liquid-glass-strong', 'border', 'border-amber-300/40', 'text-white');
          btn.classList.remove('liquid-glass', 'text-neutral-300');
        }
      });
      renderReports();
      playChime(540);
    }

    function handleSearch(val) {
      currentSearchTerm = val;
      fetchReports();
    }

    function scrollToReports(type) {
      filterType(type);
      document.getElementById('reports')?.scrollIntoView({ behavior: 'smooth' });
    }

    // Report Creation Modal
    function openReportModal(type = 'LOST') {
      setModalType(type);
      if (currentUser) {
        const reporterField = document.getElementById('form-reporter');
        if (reporterField) reporterField.value = currentUser.fullName;
      }
      document.getElementById('report-modal').classList.remove('hidden');
      playChime(620);
    }

    function closeReportModal() {
      document.getElementById('report-modal').classList.add('hidden');
    }

    function setModalType(type) {
      modalCurrentType = type;
      const tLost = document.getElementById('toggle-lost');
      const tFound = document.getElementById('toggle-found');
      const privWrap = document.getElementById('private-detail-wrap');
      const heading = document.getElementById('modal-heading');

      if (type === 'LOST') {
        tLost.className = 'py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 bg-white text-black transition';
        tFound.className = 'py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 text-neutral-300 hover:text-white transition';
        privWrap.classList.remove('hidden');
        heading.innerText = 'Let’s get it back where it belongs.';
      } else {
        tFound.className = 'py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 text-neutral-300 hover:text-white transition';
        tLost.className = 'py-2 rounded-full text-xs font-semibold flex items-center justify-center gap-2 bg-white text-black transition';
        privWrap.classList.add('hidden');
        heading.innerText = 'Thank you for finding someone’s item.';
      }
    }

    async function submitReport(e) {
      e.preventDefault();
      const btn = e.submitter || document.querySelector('#create-report-form [type="submit"]');
      const origHTML = btn ? btn.innerHTML : '';
      if (btn) { btn.disabled = true; btn.innerHTML = '<span>Saving…</span>'; }

      const dateVal = document.getElementById('form-date').value;
      const itemDate = dateVal ? new Date(dateVal).toISOString() : new Date().toISOString();

      const payload = {
        type: modalCurrentType,
        reporter: document.getElementById('form-reporter').value.trim(),
        title: document.getElementById('form-title').value.trim(),
        category: document.getElementById('form-category').value,
        description: document.getElementById('form-desc').value.trim(),
        location: document.getElementById('form-location').value.trim(),
        itemDate,
        photoUrl: document.getElementById('form-photo').value.trim() || null,
        privateDetail: modalCurrentType === 'LOST'
          ? (document.getElementById('form-private-detail').value.trim() || 'unspecified')
          : 'n/a',
      };

      try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

        const res = await fetch(`${API_BASE}/items`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.error || `HTTP ${res.status}`);
        }
        const created = await res.json();
        reportsData.unshift(normalizeItem(created));
        renderReports();
        closeReportModal();
        e.target.reset();
        playSuccessChime();
        showToast(`✨ New report logged: "${created.title}"`);
        document.getElementById('reports')?.scrollIntoView({ behavior: 'smooth' });
        loadDashboard();
        await loadMatches();
      } catch (err) {
        showToast(`⚠️ Could not submit: ${err.message}`);
        console.error('Submit failed:', err);
      } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = origHTML; }
      }
    }

    // Match Workspace Modal — Real Backend Integration
    async function openMatchDemoModal(matchId) {
      if (!matchesData || matchesData.length === 0) {
        await loadMatches();
      }
      currentActiveMatchId = matchId || (matchesData.length > 0 ? matchesData[0].id : 1);

      try {
        const res = await fetch(`${API_BASE}/matches/${currentActiveMatchId}`);
        if (res.ok) {
          currentActiveMatch = await res.json();
        } else if (matchesData.length > 0) {
          currentActiveMatch = matchesData.find(m => m.id === currentActiveMatchId) || matchesData[0];
        }
      } catch (e) {
        currentActiveMatch = matchesData.find(m => m.id === currentActiveMatchId) || null;
      }

      if (currentActiveMatch) {
        const confTitle = document.getElementById('modal-match-title');
        if (confTitle) {
          confTitle.innerText = `Match Confidence: ${currentActiveMatch.scorePercent || Math.round((currentActiveMatch.score || 0.8) * 100)}%`;
        }

        if (currentActiveMatch.lostItem) {
          document.getElementById('modal-lost-title').innerText = currentActiveMatch.lostItem.title;
          document.getElementById('modal-lost-desc').innerText = currentActiveMatch.lostItem.description;
        }
        if (currentActiveMatch.foundItem) {
          document.getElementById('modal-found-title').innerText = currentActiveMatch.foundItem.title;
          document.getElementById('modal-found-desc').innerText = currentActiveMatch.foundItem.description;
        }

        const chat = document.getElementById('chat-section');
        const btn = document.getElementById('btn-confirm-return');
        const status = document.getElementById('match-status');
        const fb = document.getElementById('verify-feedback');
        const vInput = document.getElementById('verify-input');

        fb.classList.add('hidden');
        fb.innerText = '';
        vInput.value = '';

        if (currentActiveMatch.verified) {
          status.className = 'text-emerald-400 font-semibold';
          status.innerText = (currentActiveMatch.lostConfirmed && currentActiveMatch.foundConfirmed) ? '✓ Reunited & Closed' : 'Verified Direct Channel Ready';
          chat.classList.remove('hidden');
          const isClosed = currentActiveMatch.lostConfirmed && currentActiveMatch.foundConfirmed;
          btn.disabled = !!isClosed;
          btn.className = isClosed
            ? 'liquid-glass rounded-full px-5 py-2 text-xs font-semibold text-neutral-500 cursor-not-allowed'
            : 'liquid-glass-strong rounded-full px-5 py-2 text-xs font-semibold text-white bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-300/40 transition';

          await loadChatMessages(currentActiveMatchId);
        } else {
          status.className = 'text-amber-300 font-semibold';
          status.innerText = 'Awaiting Verification Challenge';
          chat.classList.add('hidden');
          btn.disabled = true;
          btn.className = 'liquid-glass rounded-full px-5 py-2 text-xs font-semibold text-neutral-500 cursor-not-allowed transition';
        }
      }

      document.getElementById('match-modal').classList.remove('hidden');
      lucide.createIcons();
      playChime(640);
    }

    function closeMatchModal() {
      document.getElementById('match-modal').classList.add('hidden');
    }

    async function testVerify() {
      const input = document.getElementById('verify-input').value.trim();
      const fb = document.getElementById('verify-feedback');
      const chat = document.getElementById('chat-section');
      const btn = document.getElementById('btn-confirm-return');
      const status = document.getElementById('match-status');

      if (!input) {
        fb.className = 'text-xs mt-2 text-rose-400 font-semibold';
        fb.innerText = 'Please enter the secret verification detail.';
        fb.classList.remove('hidden');
        return;
      }

      fb.className = 'text-xs mt-2 text-amber-300 font-semibold';
      fb.innerText = 'Verifying with secure backend…';
      fb.classList.remove('hidden');

      try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

        const res = await fetch(`${API_BASE}/matches/${currentActiveMatchId}/verify`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ privateDetail: input })
        });
        const data = await res.json();

        if (res.ok && data.verified) {
          fb.className = 'text-xs mt-2 text-emerald-400 font-semibold';
          fb.innerText = data.message || '✓ Verification Successful! Secret detail matches owner report. Direct channel opened.';
          chat.classList.remove('hidden');
          btn.disabled = false;
          btn.className = 'liquid-glass-strong rounded-full px-5 py-2 text-xs font-semibold text-white bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-300/40 transition';
          status.className = 'text-emerald-400 font-semibold';
          status.innerText = 'Verified Connection Ready';
          playSuccessChime();
          loadChatMessages(currentActiveMatchId);
          loadMatches();
        } else {
          fb.className = 'text-xs mt-2 text-rose-400 font-semibold';
          fb.innerText = data.error || '✕ That detail does not match the private record. Please try again.';
          playChime(320, 'sawtooth');
          if (data.locked) {
            document.getElementById('verify-input').disabled = true;
          }
        }
      } catch (err) {
        fb.className = 'text-xs mt-2 text-rose-400 font-semibold';
        fb.innerText = `Network or server error: ${err.message}`;
      }
    }

    async function loadChatMessages(matchId) {
      const msgList = document.getElementById('chat-messages');
      if (!msgList) return;
      try {
        const headers = {};
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
        const res = await fetch(`${API_BASE}/matches/${matchId}/messages`, { headers });
        if (res.ok) {
          const messages = await res.json();
          if (messages.length === 0) {
            msgList.innerHTML = `
              <div class="text-center text-xs text-neutral-400 py-3">
                No messages yet. Agree on a safe, public campus location for return.
              </div>
            `;
          } else {
            msgList.innerHTML = messages.map(m => {
              const isMe = (currentUser && m.senderName === currentUser.fullName) || m.role === 'OWNER';
              return `
                <div class="p-3 rounded-xl ${isMe ? 'bg-amber-500/10 border border-amber-300/20 text-amber-100 ml-6' : 'bg-white/5 border border-white/10 text-neutral-200 mr-6'} text-xs">
                  <span class="text-[10px] ${isMe ? 'text-amber-300' : 'text-neutral-400'} block font-semibold">
                    ${escapeHtml(m.senderName)} (${escapeHtml(m.role)}) • ${escapeHtml((m.sentAt || '').slice(11, 16) || 'Just now')}
                  </span>
                  <p class="mt-0.5 leading-relaxed">${escapeHtml(m.text)}</p>
                </div>
              `;
            }).join('');
            msgList.scrollTop = msgList.scrollHeight;
          }
        }
      } catch (e) {
        console.warn('Could not load chat messages:', e);
      }
    }

    async function sendChatMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;

      const senderName = currentUser ? currentUser.fullName : 'Community Member';
      const role = (currentActiveMatch && currentActiveMatch.lostItem && currentUser && currentActiveMatch.lostItem.reporter === currentUser.fullName) ? 'OWNER' : 'FINDER';

      input.value = '';
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

        const res = await fetch(`${API_BASE}/matches/${currentActiveMatchId}/messages`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            role: role,
            senderName: senderName,
            text: text
          })
        });

        if (res.ok) {
          playChime(700);
          await loadChatMessages(currentActiveMatchId);
        } else {
          const err = await res.json().catch(() => ({}));
          showToast(`⚠️ ${err.error || 'Could not send message'}`);
        }
      } catch (err) {
        showToast(`⚠️ Error sending message: ${err.message}`);
      }
    }

    async function confirmHandoff() {
      const status = document.getElementById('match-status');
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

        const res = await fetch(`${API_BASE}/matches/${currentActiveMatchId}/confirm-return`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ role: 'OWNER' })
        });

        if (res.ok) {
          const d = await res.json();
          status.className = 'text-amber-300 font-bold';
          status.innerText = d.closed ? '✓ Reunited & Closed!' : '✓ Hand-off Confirmed by You';
          playSuccessChime();
          showToast('🎉 Safe hand-off confirmed! 50 Karma points recorded.');
          fetchReports();
          loadDashboard();
          loadMatches();
          setTimeout(() => closeMatchModal(), 1200);
        }
      } catch (err) {
        showToast(`⚠️ Confirmation error: ${err.message}`);
      }
    }

    // Inspect Report Detail
    function inspectReport(id) {
      const item = reportsData.find(r => r.id === id);
      if (!item) return;
      selectedDetailItem = item;

      document.getElementById('detail-title').textContent = item.title;
      document.getElementById('detail-desc').textContent = item.description;
      document.getElementById('detail-location').textContent = item.location;
      document.getElementById('detail-date').textContent = item.date;
      
      const safeImg = sanitizeUrl(item.photoUrl);
      document.getElementById('detail-img').src = safeImg || 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80';
      
      const pill = document.getElementById('detail-type-pill');
      pill.textContent = item.type;
      pill.className = `px-3 py-1 rounded-full text-xs font-bold ${item.type === 'LOST' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}`;

      document.getElementById('item-detail-modal').classList.remove('hidden');
      lucide.createIcons();
      playChime(580);
    }

    function closeItemDetailModal() {
      document.getElementById('item-detail-modal').classList.add('hidden');
    }

    function claimCurrentItem() {
      closeItemDetailModal();
      if (selectedDetailItem) {
        const matched = matchesData.find(m => m.lostItemId === selectedDetailItem.id || m.foundItemId === selectedDetailItem.id);
        if (matched) {
          openMatchDemoModal(matched.id);
          return;
        }
      }
      openMatchDemoModal();
    }

    function openPosterModalFromDetail() {
      if (selectedDetailItem) {
        openPosterModal(selectedDetailItem.id);
      }
      closeItemDetailModal();
    }

    // Poster Modal Handlers
    function openPosterModal(id) {
      const item = (id != null ? reportsData.find(r => r.id === id) : null) || reportsData[0];
      document.getElementById('poster-title').innerText = item.title;
      document.getElementById('poster-location').innerText = item.location;
      document.getElementById('poster-date').innerText = item.date;
      document.getElementById('poster-desc').innerText = item.description;
      if (item.photoUrl) document.getElementById('poster-img').src = item.photoUrl;

      const badge = document.getElementById('poster-type-badge');
      badge.innerText = item.type === 'LOST' ? 'MISSING / LOST ITEM' : 'FOUND ITEM NOTICE';
      badge.className = `inline-block px-3 py-0.5 rounded-full text-xs font-bold mt-1 ${item.type === 'LOST' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`;

      document.getElementById('poster-modal').classList.remove('hidden');
      playChime(600);
    }

    function closePosterModal() {
      document.getElementById('poster-modal').classList.add('hidden');
    }

    function shareWhatsApp() {
      const title = document.getElementById('poster-title').innerText;
      const text = encodeURIComponent(`📢 Lost & Found Alert: ${title}. Verify and arrange safe return at http://localhost:3000/`);
      window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
      playChime(660);
    }

    function downloadPoster() {
      playSuccessChime();
      showToast('📥 Ready to print! A4 Notice template generated.');
      window.print();
    }

    // QR Custody Modal
    function openQRModal(deskName = 'Campus Security Main Desk') {
      document.getElementById('qr-desk-name').innerText = deskName;
      document.getElementById('qr-modal').classList.remove('hidden');
      playChime(640);
    }
    function closeQRModal() {
      document.getElementById('qr-modal').classList.add('hidden');
    }
    function simulateSuccessfulScan() {
      playSuccessChime();
      showToast('✓ Custody Verified! Item registered in Secure Locker #14.');
      closeQRModal();
    }


    // AI Neural Matching Simulator Engine
    const simPresets = [
      { img: 95, txt: 92, geo: 90, time: 94 }, // AirPods vs Case
      { img: 98, txt: 94, geo: 96, time: 92 }, // Black Leather Wallet
      { img: 75, txt: 80, geo: 68, time: 70 }, // Bellroy Navy Backpack
      { img: 40, txt: 50, geo: 60, time: 45 }  // Brass Keys vs Lone Key
    ];

    function loadSimPreset(idx) {
      document.querySelectorAll('.sim-preset-btn').forEach((btn, i) => {
        if (i === idx) {
          btn.className = 'sim-preset-btn active p-3 rounded-xl liquid-glass text-left border border-amber-300/40 text-white transition';
        } else {
          btn.className = 'sim-preset-btn p-3 rounded-xl liquid-glass text-left border border-white/10 text-neutral-300 hover:text-white transition';
        }
      });
      const p = simPresets[idx];
      document.getElementById('slider-img').value = p.img;
      document.getElementById('slider-txt').value = p.txt;
      document.getElementById('slider-geo').value = p.geo;
      document.getElementById('slider-time').value = p.time;
      updateSimScore();
      playChime(560);
    }

    function updateSimScore() {
      const img = parseFloat(document.getElementById('slider-img').value);
      const txt = parseFloat(document.getElementById('slider-txt').value);
      const geo = parseFloat(document.getElementById('slider-geo').value);
      const time = parseFloat(document.getElementById('slider-time').value);

      document.getElementById('val-sim-img').innerText = `${img}%`;
      document.getElementById('val-sim-txt').innerText = `${txt}%`;
      document.getElementById('val-sim-geo').innerText = `${geo}% (${((100 - geo) * 0.05).toFixed(2)} km)`;
      document.getElementById('val-sim-time').innerText = `${time}% (< ${(100 - time) * 0.5} hrs)`;

      const cImg = img * 0.45;
      const cTxt = txt * 0.25;
      const cGeo = geo * 0.20;
      const cTime = time * 0.10;
      const total = cImg + cTxt + cGeo + cTime;

      document.getElementById('contrib-img').innerText = `${cImg.toFixed(1)}%`;
      document.getElementById('contrib-txt').innerText = `${cTxt.toFixed(1)}%`;
      document.getElementById('contrib-geo').innerText = `${cGeo.toFixed(1)}%`;
      document.getElementById('contrib-time').innerText = `${cTime.toFixed(1)}%`;

      document.getElementById('sim-final-score').innerText = `${total.toFixed(1)}%`;

      // Circular gauge offset: circumference is 2 * PI * 50 = 314.15
      const offset = 314.15 * (1 - total / 100);
      const circle = document.getElementById('sim-gauge-circle');
      circle.style.strokeDashoffset = offset;

      const banner = document.getElementById('sim-status-banner');
      const title = document.getElementById('sim-status-title');
      const desc = document.getElementById('sim-status-desc');

      if (total >= 70) {
        circle.setAttribute('stroke', '#22c55e');
        banner.className = 'p-4 rounded-2xl bg-emerald-500/10 border border-emerald-400/30 text-xs transition-all';
        title.className = 'flex items-center gap-2 text-emerald-300 font-bold text-sm mb-1';
        title.innerHTML = '<i data-lucide="bell-ring" class="w-4 h-4"></i> High Confidence Match';
        desc.innerText = `Score (${total.toFixed(1)}%) crosses the 70% threshold. Automated push notifications dispatched to owner & finder. Private verification challenge unlocked.`;
      } else {
        circle.setAttribute('stroke', '#f43f5e');
        banner.className = 'p-4 rounded-2xl bg-rose-500/10 border border-rose-400/30 text-xs transition-all';
        title.className = 'flex items-center gap-2 text-rose-300 font-bold text-sm mb-1';
        title.innerHTML = '<i data-lucide="alert-circle" class="w-4 h-4"></i> Below Notification Threshold';
        desc.innerText = `Score (${total.toFixed(1)}%) is below the 70% threshold. Kept in background queue for secondary corroboration.`;
      }
      lucide.createIcons();
    }

    // Heatmap Hotspot Data & Handlers
    const hotspotsData = [
      {
        title: "Campus Central Library",
        reports: "42 active reports",
        badge: "High Activity Zone",
        desc: "Frequent items: AirPods cases, phone chargers, notebooks, glasses. Nearest collection point: 2nd floor circulation desk."
      },
      {
        title: "Metro Station Platform 3",
        reports: "28 active reports",
        badge: "Commuter Transit Hub",
        desc: "Frequent items: Wallets, transit cards, umbrella, scarves. Nearest collection point: Lost property office beside Ticket 4."
      },
      {
        title: "Student Union Café",
        reports: "19 active reports",
        badge: "Social Common Space",
        desc: "Frequent items: Backpacks, gym water bottles, student IDs. Nearest collection point: Main desk help staff."
      },
      {
        title: "Riverside Park Benches",
        reports: "15 active reports",
        badge: "Recreational Cluster",
        desc: "Frequent items: Keychains, sunglasses, bicycle locks. Nearest collection point: Parks warden kiosk."
      }
    ];

    function selectHotspot(idx) {
      const data = hotspotsData[idx];
      document.getElementById('hotspot-title').innerText = data.title;
      document.getElementById('hotspot-reports-count').innerText = data.reports;
      document.getElementById('hotspot-badge').innerText = data.badge;
      document.getElementById('hotspot-desc').innerText = data.desc;
      playChime(620);
    }

    let heatmapTimeIndex = 0;
    const heatmapTimes = [
      "8:00 AM (Morning Transit)",
      "2:00 PM (Afternoon Rush)",
      "7:00 PM (Evening Commute)",
      "11:00 PM (Night Owl)"
    ];
    function cycleHeatmapTime() {
      heatmapTimeIndex = (heatmapTimeIndex + 1) % heatmapTimes.length;
      document.getElementById('time-filter-label').innerText = heatmapTimes[heatmapTimeIndex];
      playChime(580);
      showToast(`📍 Density recalibrated for: ${heatmapTimes[heatmapTimeIndex]}`);
    }

    function showToast(text) {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const el = document.createElement('div');
      el.className = 'liquid-glass-strong rounded-2xl px-4 py-2.5 text-xs text-white border border-amber-300/30 shadow-2xl flex items-center gap-2 toast-animate pointer-events-auto';
      
      const dot = document.createElement('span');
      dot.className = 'w-2 h-2 rounded-full bg-emerald-400 live-pulse';
      const msg = document.createElement('span');
      msg.textContent = text;
      
      el.appendChild(dot);
      el.appendChild(msg);
      container.appendChild(el);
      setTimeout(() => el.remove(), 5200);
    }

    // Multi-Language Localization Engine (EN / HI / MR)
    const translations = {
      en: {
        nav_overview: "Overview",
        nav_ai_radar: "AI Radar",
        nav_heatmap: "Live Heatmap",
        nav_privacy: "Privacy Shield",
        nav_leaderboard: "Kindness Hall",
        nav_reports: "Browse Reports",
        nav_safe_hubs: "Safe Hubs",
        btn_report: "Report Item",
        hero_stats_reunited: "Over 1,420 misplaced items reunited this month",
        hero_headline_1: "Lost something?",
        hero_headline_2: "Let’s bring it home.",
        hero_subheading: "Small things carry priceless stories. FindIt pairs the people who've misplaced something with the kind people who've found it — protected with zero-knowledge private verification.",
        btn_find_item: "Find My Item",
        btn_found_item: "I Found Something",
        btn_try_ai: "Try AI Radar"
      },
      hi: {
        nav_overview: "सिंहावलोकन",
        nav_ai_radar: "एआई रडार",
        nav_heatmap: "लाइव हीटमैप",
        nav_privacy: "गोपनीयता शील्ड",
        nav_leaderboard: "सम्मान मंच",
        nav_reports: "रिपोर्ट्स देखें",
        nav_safe_hubs: "सुरक्षित केंद्र",
        btn_report: "रिपोर्ट दर्ज करें",
        hero_stats_reunited: "इस महीने 1,420 से अधिक वस्तुएं उनके मालिकों तक पहुंचीं",
        hero_headline_1: "कुछ खो गया?",
        hero_headline_2: "चलिए इसे घर लाते हैं।",
        hero_subheading: "छोटी-छोटी चीज़ों में अनमोल यादें होती हैं। FindIt उन लोगों को जोड़ता है जिनकी कोई चीज़ खो गई है, उन दयालु लोगों से जिन्होंने उसे पाया है।",
        btn_find_item: "मेरी वस्तु खोजें",
        btn_found_item: "मुझे कुछ मिला",
        btn_try_ai: "एआई रडार आज़माएं"
      },
      mr: {
        nav_overview: "आढावा",
        nav_ai_radar: "एआय रडार",
        nav_heatmap: "थेट हीटमॅप",
        nav_privacy: "गोपनीयता सुरक्षा",
        nav_leaderboard: "सद्भावना कक्ष",
        nav_reports: "तक्रारी पहा",
        nav_safe_hubs: "सुरक्षित केंद्रे",
        btn_report: "तक्रार नोंदवा",
        hero_stats_reunited: "या महिन्यात 1,420 हून अधिक वस्तू परत मिळाल्या",
        hero_headline_1: "काही हरवले आहे?",
        hero_headline_2: "चला ते घरी आणूया.",
        hero_subheading: "लहान गोष्टींमध्ये अनमोल आठवणी असतात. FindIt हरवलेल्या वस्तू शोधणाऱ्यांना आणि त्या सापडलेल्या दयाळू लोकांना सुरक्षितपणे एकत्र आणते.",
        btn_find_item: "माझी वस्तू शोधा",
        btn_found_item: "मला काहीतरी सापडले",
        btn_try_ai: "एआय रडार वापरा"
      }
    };

    function changeLanguage(lang) {
      document.querySelectorAll('#lang-en, #lang-hi, #lang-mr').forEach(b => {
        b.className = 'px-2 py-0.5 rounded-full hover:text-white transition';
      });
      const activeBtn = document.getElementById(`lang-${lang}`);
      if (activeBtn) activeBtn.className = 'px-2 py-0.5 rounded-full bg-white/20 text-white transition';

      const dict = translations[lang] || translations.en;
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.innerText = dict[key];
      });

      playChime(640);
    }

    // -------------------------------------------------------------
    // 3D GOLDEN SKELETON KEY: CALM FLOATING LEVITATION & SMOOTH HOVER (NO SPINNING)
    // -------------------------------------------------------------
    let currentHoverY = 0;
    let targetHoverY = 0;
    let currentScale = 1.0;
    let targetScale = 1.0;

    function moveKeySwipe(e) {
      const target = document.getElementById('hero-key-interactive');
      if (!target) return;
      const rect = target.getBoundingClientRect();
      const normX = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 to +0.5
      targetHoverY = normX * 16; // Gentle, subtle ~8 deg perspective tilt on hover
      targetScale = 1.04; // Smooth gentle scale lift
    }

    function leaveKeySwipe(e) {
      targetHoverY = 0; // Smoothly returns to flat 0
      targetScale = 1.0; // Smoothly returns to 1.0
    }

    function endKeySwipe(e) {
      targetHoverY = 0;
      targetScale = 1.0;
    }

    function startKeySwipe(e) {}

    function updateKeyPhysicsLoop() {
      requestAnimationFrame(updateKeyPhysicsLoop);
      const container = document.getElementById('key-tilt-container');
      if (!container) return;

      // Buttery-smooth LERP easing (NO SPINNING, ONLY CALM FLOAT & HOVER)
      currentHoverY += (targetHoverY - currentHoverY) * 0.08;
      currentScale += (targetScale - currentScale) * 0.08;

      container.style.transform = `perspective(1000px) rotateY(${currentHoverY.toFixed(2)}deg) scale(${currentScale.toFixed(3)})`;
    }

    requestAnimationFrame(updateKeyPhysicsLoop);

    // -------------------------------------------------------------
    // USER AUTHENTICATION SYSTEM (LOGIN, SIGNUP, SESSION, SECURITY)
    // -------------------------------------------------------------
    let currentUser = null;
    let authToken = null;

    function openAuthModal(tab = 'login') {
      const modal = document.getElementById('auth-modal');
      if (!modal) return;
      switchAuthTab(tab);
      hideAuthBanners();
      modal.classList.remove('hidden');
      playChime(640);
    }

    function closeAuthModal() {
      const modal = document.getElementById('auth-modal');
      if (modal) modal.classList.add('hidden');
      hideAuthBanners();
    }

    function switchAuthTab(tab) {
      const isLogin = tab === 'login';
      document.getElementById('auth-tab-login').className = isLogin
        ? 'flex-1 py-2 rounded-xl bg-white/20 text-white font-semibold transition text-center shadow-md'
        : 'flex-1 py-2 rounded-xl text-neutral-400 hover:text-white font-semibold transition text-center';
      document.getElementById('auth-tab-signup').className = !isLogin
        ? 'flex-1 py-2 rounded-xl bg-white/20 text-white font-semibold transition text-center shadow-md'
        : 'flex-1 py-2 rounded-xl text-neutral-400 hover:text-white font-semibold transition text-center';

      document.getElementById('auth-modal-title').innerText = isLogin ? 'Welcome Back' : 'Create Account';
      document.getElementById('auth-modal-subtitle').innerText = isLogin
        ? 'Access your reports, live matches, and secure community messages.'
        : 'Join FindIt to report items, receive neural match alerts & protect returns.';

      if (isLogin) {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('signup-form').classList.add('hidden');
      } else {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('signup-form').classList.remove('hidden');
      }
      hideAuthBanners();
      lucide.createIcons();
    }

    function hideAuthBanners() {
      const err = document.getElementById('auth-error-banner');
      const succ = document.getElementById('auth-success-banner');
      if (err) err.classList.add('hidden');
      if (succ) succ.classList.add('hidden');
    }

    function showAuthError(msg) {
      const err = document.getElementById('auth-error-banner');
      const text = document.getElementById('auth-error-text');
      if (err && text) {
        text.innerText = msg || 'An unexpected error occurred.';
        err.classList.remove('hidden');
      }
      playChime(320, 'sawtooth');
    }

    function showAuthSuccess(msg) {
      const succ = document.getElementById('auth-success-banner');
      const text = document.getElementById('auth-success-text');
      if (succ && text) {
        text.innerText = msg;
        succ.classList.remove('hidden');
      }
      playSuccessChime();
    }

    function togglePasswordVisibility(inputId, eyeIconId) {
      const input = document.getElementById(inputId);
      const icon = document.getElementById(eyeIconId);
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        if (icon) icon.setAttribute('data-lucide', 'eye-off');
      } else {
        input.type = 'password';
        if (icon) icon.setAttribute('data-lucide', 'eye');
      }
      lucide.createIcons();
    }

    function validateSignupEmail() {
      const emailInput = document.getElementById('signup-email');
      const fb = document.getElementById('signup-email-feedback');
      if (!emailInput || !fb) return;
      const val = emailInput.value.trim();
      const pattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
      if (val && !pattern.test(val)) {
        fb.innerText = 'Please enter a valid email address.';
        fb.classList.remove('hidden');
      } else {
        fb.classList.add('hidden');
      }
    }

    function updatePasswordStrengthMeter() {
      const pwd = document.getElementById('signup-password').value;
      const bar = document.getElementById('pwd-strength-bar');
      const label = document.getElementById('pwd-strength-label');

      const ruleLen = pwd.length >= 8;
      const ruleUpper = /[A-Z]/.test(pwd);
      const ruleLower = /[a-z]/.test(pwd);
      const ruleSymbol = /[0-9]/.test(pwd) && /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd);

      updateRuleUI('rule-length', ruleLen, '8+ characters');
      updateRuleUI('rule-upper', ruleUpper, '1+ Uppercase (A-Z)');
      updateRuleUI('rule-lower', ruleLower, '1+ Lowercase (a-z)');
      updateRuleUI('rule-symbol', ruleSymbol, 'Number & Symbol');

      let score = 0;
      if (ruleLen) score++;
      if (ruleUpper) score++;
      if (ruleLower) score++;
      if (ruleSymbol) score++;

      if (pwd.length === 0) {
        bar.style.width = '0%';
        bar.className = 'h-full w-0 bg-rose-500 transition-all duration-300';
        label.innerText = 'None';
        label.className = 'font-semibold text-neutral-400';
      } else if (score <= 2) {
        bar.style.width = '33%';
        bar.className = 'h-full w-1/3 bg-rose-500 transition-all duration-300';
        label.innerText = 'Weak';
        label.className = 'font-semibold text-rose-400';
      } else if (score === 3) {
        bar.style.width = '66%';
        bar.className = 'h-full w-2/3 bg-amber-400 transition-all duration-300';
        label.innerText = 'Medium';
        label.className = 'font-semibold text-amber-300';
      } else {
        bar.style.width = '100%';
        bar.className = 'h-full w-full bg-emerald-400 transition-all duration-300';
        label.innerText = 'Strong';
        label.className = 'font-semibold text-emerald-400';
      }

      checkPasswordMatch();
    }

    function updateRuleUI(elId, passed, text) {
      const el = document.getElementById(elId);
      if (!el) return;
      if (passed) {
        el.className = 'flex items-center gap-1.5 text-emerald-400 font-medium';
        el.innerHTML = `<i data-lucide="check-circle-2" class="w-3 h-3 text-emerald-400"></i><span>${text}</span>`;
      } else {
        el.className = 'flex items-center gap-1.5 text-neutral-400';
        el.innerHTML = `<i data-lucide="circle" class="w-3 h-3 text-neutral-500"></i><span>${text}</span>`;
      }
      lucide.createIcons();
    }

    function checkPasswordMatch() {
      const pwd = document.getElementById('signup-password').value;
      const confirm = document.getElementById('signup-confirm-password').value;
      const fb = document.getElementById('signup-match-feedback');
      if (!fb) return;

      if (confirm.length > 0) {
        if (pwd === confirm) {
          fb.innerText = '✓ Passwords match';
          fb.className = 'text-[11px] text-emerald-400 mt-1 font-medium';
          fb.classList.remove('hidden');
        } else {
          fb.innerText = '✕ Passwords do not match';
          fb.className = 'text-[11px] text-rose-400 mt-1 font-medium';
          fb.classList.remove('hidden');
        }
      } else {
        fb.classList.add('hidden');
      }
    }

    async function handleLoginSubmit(e) {
      e.preventDefault();
      hideAuthBanners();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const btn = document.getElementById('login-submit-btn');

      const origText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span>Signing in…</span>';

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Invalid email or password.');
        }

        applyUserSession(data);
        showAuthSuccess(`Welcome back, ${data.fullName}!`);
        setTimeout(() => {
          closeAuthModal();
          showToast(`👋 Signed in as ${data.fullName}`);
        }, 800);
      } catch (err) {
        showAuthError(err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = origText;
        lucide.createIcons();
      }
    }

    async function handleSignupSubmit(e) {
      e.preventDefault();
      hideAuthBanners();

      const fullName = document.getElementById('signup-fullname').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const password = document.getElementById('signup-password').value;
      const confirmPassword = document.getElementById('signup-confirm-password').value;
      const btn = document.getElementById('signup-submit-btn');

      if (password !== confirmPassword) {
        showAuthError('Passwords do not match.');
        return;
      }

      const origText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span>Creating account…</span>';

      try {
        const res = await fetch(`${API_BASE}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fullName, email, password, confirmPassword })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Registration failed.');
        }

        applyUserSession(data);
        showAuthSuccess('Account created! Logging you in...');
        setTimeout(() => {
          closeAuthModal();
          showToast(`🎉 Account created! Welcome to FindIt, ${data.fullName}`);
        }, 900);
      } catch (err) {
        showAuthError(err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = origText;
        lucide.createIcons();
      }
    }

    function applyUserSession(authData) {
      currentUser = {
        id: authData.id,
        fullName: authData.fullName,
        email: authData.email
      };
      authToken = authData.token;

      localStorage.setItem('findit_auth', JSON.stringify({
        token: authToken,
        user: currentUser
      }));

      updateUserUI();
    }

    function updateUserUI() {
      const loggedOutDiv = document.getElementById('nav-auth-logged-out');
      const profileDiv = document.getElementById('nav-user-profile');

      if (currentUser) {
        if (loggedOutDiv) loggedOutDiv.classList.add('hidden');
        if (profileDiv) profileDiv.classList.remove('hidden');

        const initials = currentUser.fullName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2) || 'U';
        document.getElementById('user-avatar-initials').innerText = initials;
        document.getElementById('user-display-name').innerText = currentUser.fullName;
        document.getElementById('user-dropdown-name').innerText = currentUser.fullName;
        document.getElementById('user-dropdown-email').innerText = currentUser.email;

        const reporterField = document.getElementById('form-reporter');
        if (reporterField && !reporterField.value) {
          reporterField.value = currentUser.fullName;
        }
      } else {
        if (loggedOutDiv) loggedOutDiv.classList.remove('hidden');
        if (profileDiv) profileDiv.classList.add('hidden');
      }
      lucide.createIcons();
    }

    function toggleUserDropdown(e) {
      if (e) e.stopPropagation();
      const menu = document.getElementById('user-dropdown-menu');
      if (menu) menu.classList.toggle('hidden');
    }

    document.addEventListener('click', () => {
      const menu = document.getElementById('user-dropdown-menu');
      if (menu && !menu.classList.contains('hidden')) {
        menu.classList.add('hidden');
      }
    });

    async function checkStoredSession() {
      try {
        const stored = localStorage.getItem('findit_auth');
        if (!stored) return;
        const parsed = JSON.parse(stored);
        if (!parsed || !parsed.token) return;

        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { 'Authorization': `Bearer ${parsed.token}` }
        });
        if (res.ok) {
          const profile = await res.json();
          currentUser = profile;
          authToken = parsed.token;
          updateUserUI();
        } else {
          localStorage.removeItem('findit_auth');
        }
      } catch (err) {
        console.warn('Session check failed:', err);
      }
    }

    async function handleLogout() {
      if (authToken) {
        try {
          await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
        } catch (err) {
          console.warn('Logout error:', err);
        }
      }

      currentUser = null;
      authToken = null;
      localStorage.removeItem('findit_auth');
      updateUserUI();
      playChime(400);
      showToast('ℹ️ You have been signed out.');
    }

    function openMyReportsModal() {
      if (!currentUser) return;
      filterType('ALL');
      currentSearchTerm = currentUser.fullName;
      fetchReports();
      document.getElementById('reports')?.scrollIntoView({ behavior: 'smooth' });
      showToast(`📦 Filtered reports filed by ${currentUser.fullName}`);
    }

    // Initialization on DOM Load
    window.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      checkStoredSession();
      fetchReports();
      loadMatches();
      loadDashboard();
      if (typeof updateSimScore === 'function') updateSimScore();
    });
  </script>
</body>
</html>
"""

# Write to S:\IT\Lost and Found\index.html
target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
with open(target_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully generated clean 3D key in {target_path}")
