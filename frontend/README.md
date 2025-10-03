# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# 🚀 Task Manager App with Gamified Badges  

## 📖 Why I Started  
As part of my **AI + Full-Stack learning challenge**, I wanted to build a real-world project that goes beyond just CRUD operations. Traditional productivity apps often feel dry — you add tasks, tick them off, and that’s it. I wanted something **fun, rewarding, and motivating**, while also learning how to connect a backend and frontend.  

## 🎯 The Goal  
- To build a **full-stack Task Manager app** (Flask + React).  
- Integrate **gamification mechanics** (badges + confetti) that make everyday task management exciting.  
- Create a project that can serve as both:  
  1. A **portfolio piece** showcasing my ability to build modern web apps.  
  2. A **real tool** that can motivate people to stick with their habits and goals.  

## 🌍 Real-World Problem It Solves  
Most people struggle to stay consistent with habits, tasks, or budgeting. A plain to-do app often doesn’t keep users engaged. This app makes progress **celebratory**:  
- 🎉 Completing tasks gives you **badges** (first task, first habit, first expense, streaks, etc.).  
- 🎊 Confetti and popups make small wins exciting.  
- 📈 Tracks tasks, habits, and expenses in one simple place.  

The app addresses **user motivation and engagement** — a common challenge in productivity tools.  

---

## 🛠️ What I Built So Far (Day 1–4)  
### 🔹 Backend (Flask + SQLite)  
- Built a REST API with Flask and SQLAlchemy.  
- Models: `Task`, `Habit`, `Expense`, and `Badge`.  
- Badge-awarding logic for first-time actions and streaks.  
- Configured CORS so the React frontend can connect smoothly.  

### 🔹 Frontend (React + Vite)  
- Built a frontend with React (Vite setup).  
- Connected frontend to Flask backend with fetch API.  
- Created **BadgePopup component** with `canvas-confetti` for animated celebration.  
- Tested badge triggers (`Task Initiate`, `Getting Started`).  

### 🔹 Gamification Logic  
- First task → 📝 Task Initiate badge.  
- First habit → 🌱 Habit Seed badge.  
- First expense → 💸 Saver Starter badge.  
- First activity → 🚀 Getting Started badge.  
- Future streak logic for 7-day habit tracking.  

### 🔹 3rd Oct 2025  Progress  
- Fully wired **backend ↔ frontend** connection.  
- Successfully created and displayed **real badge popup with confetti**.  
- Reset and tested database badge logic.  
- Added licensing + prepared README for GitHub.  

---

## 📂 Project Structure  
