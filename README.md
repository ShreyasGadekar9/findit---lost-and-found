# 🔍 FindIt — Smart Lost & Found Platform

> **Connecting lost items with verified owners through automated matching and private safe channels.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://findit-lost-and-found-avjl.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Three.js](https://img.shields.io/badge/Three.js-r169-black?style=for-the-badge&logo=threedotjs&logoColor=white)](https://threejs.org)
[![Security](https://img.shields.io/badge/Security-OWASP_Hardened-success?style=for-the-badge&logo=shield)](https://owasp.org)

**🔗 Live Website:** [https://findit-lost-and-found-avjl.onrender.com/](https://findit-lost-and-found-avjl.onrender.com/)

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
* **Frontend**: Vanilla JavaScript (ES6+), Three.js (r169), Tailwind CSS, Lucide Icons
* **Security**: OWASP Stored XSS defense, Brute-Force Rate Limiting, HTTP Security Headers (`nosniff`, `SAMEORIGIN`, `Referrer-Policy`), Token-based Auth
* **Deployment**: Hosted on Render with automated HTTPS/SSL encryption

---

## 🚀 Quick Start (Local Run)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShreyasGadekar9/findit---lost-and-found.git
   cd findit---lost-and-found
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
* **Brute-Force Lockout**: 5 failed verification attempts triggers an automatic 24-hour security lockout (`429 Too Many Requests`).
* **Session Lifecycle**: Auth tokens enforce a 7-day TTL with database cleanup; token query parameters in URLs are prohibited to prevent referer leakage.
