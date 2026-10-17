# 🔍 FindIt — Smart Lost & Found Platform

> **Connecting lost items with verified owners through automated matching and private safe channels.**

FindIt is an intelligent Lost & Found platform designed to eliminate public phone number sharing and prevent fraudulent claims. Built with an automated NLP-based similarity matcher and zero-knowledge ownership verification, it ensures that belongings are safely reunited with their rightful owners.

---

## 🌟 Key Features

* **⚡ Automated Similarity Engine**: Real-time matching algorithm calculating text similarity (Jaccard NLP), category matching, geospatial proximity, and date delta to pair Lost and Found reports.
* **🔐 Zero-Knowledge Ownership Verification**: Owners prove ownership by verifying a private detail (e.g., hidden sticker, unique mark, card contents) using constant-time cryptographic checks.
* **🛡️ Brute-Force Rate Limiting**: Mitigates automated guessing with a 5-attempt limit and an automatic 24-hour security lockout.
* **💬 Encrypted Direct Channel**: In-app private chat unlocks strictly after ownership is verified, enabling finder and owner to coordinate safe public handoffs without exposing phone numbers.
* **✨ 3D Hero & Fluid Liquid-Glass UI**: Modern, responsive interface built with Three.js (r169), Barlow typography, micro-interactions, and multi-language support (English, Hindi, Marathi).
* **📄 Social Notice & Print Poster Generator**: Instantly generates print-ready flyers and WhatsApp/social sharing notices with claim instructions.

---

## 🛠️ Tech Stack

* **Backend**: Python 3, `ThreadingHTTPServer`, SQLite with WAL mode, PBKDF2 Password Hashing, REST API
* **Frontend**: Vanilla JavaScript (ES6+), Three.js, Tailwind CSS, Lucide Icons
* **Security**: OWASP Stored XSS defense, Brute-Force Rate Limiting, HTTP Security Headers (`nosniff`, `SAMEORIGIN`, `Referrer-Policy`), Token-based Auth

---

## 🚀 Quick Start (Local Run)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Start the server:**
   ```bash
   python serve.py
   ```
   *Or double-click `start.bat` on Windows.*

3. **Open in browser:**
   ```text
   http://localhost:3000/index.html
   ```

---

## 🔒 Security Hardening Overview

* **XSS Defense**: Strict input sanitization via HTML entity escaping on all user-submitted fields before DOM injection.
* **Endpoint Protection**: `GET /api/matches/{id}/messages` and chat posting return `403 Forbidden` if ownership is not verified.
* **Session Lifecycle**: Auth tokens enforce a 7-day TTL with database cleanup; token query parameters in URLs are prohibited to prevent referer leakage.
