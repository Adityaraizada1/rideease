#!/usr/bin/env python3
"""
RideEase Web GUI — Modern Browser Dashboard
Runs on Python's standard library (no pip packages needed).
Synchronized with data/vehicles.txt, data/customers.txt, and data/rentals.txt.
"""

import json
import os
import sys
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

PORT = 8080
DATA_DIR = "data"

# Import models from gui.py
from gui import DataStore, Vehicle, Customer, Rental

store = DataStore(DATA_DIR)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RideEase — Vehicle Rental System</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-card { background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.06); transition: all 0.2s ease; }
    .glass-card:hover { transform: translateY(-2px); border-color: rgba(59, 130, 246, 0.4); }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
  <!-- Nav Bar -->
  <header class="sticky top-0 z-40 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <i class="fa-solid fa-car-side text-lg"></i>
        </div>
        <div>
          <span class="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">RideEase</span>
          <span class="text-xs px-2 py-0.5 ml-2 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Vehicle Rentals</span>
        </div>
      </div>

      <div class="flex items-center gap-3" id="nav-user-area">
        <!-- Rendered by JS -->
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- View Navigation Tabs -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
      <div class="flex items-center bg-slate-900 p-1.5 rounded-xl border border-slate-800" id="main-tabs">
        <button onclick="switchTab('fleet')" id="tab-fleet" class="px-5 py-2 rounded-lg text-sm font-semibold transition bg-blue-600 text-white shadow">
          <i class="fa-solid fa-car mr-2"></i> Browse Fleet
        </button>
        <button onclick="switchTab('myrentals')" id="tab-myrentals" class="hidden px-5 py-2 rounded-lg text-sm font-semibold transition text-slate-400 hover:text-white">
          <i class="fa-solid fa-clock-rotate-left mr-2"></i> My Rentals
        </button>
        <button onclick="switchTab('admin')" id="tab-admin" class="hidden px-5 py-2 rounded-lg text-sm font-semibold transition text-slate-400 hover:text-white">
          <i class="fa-solid fa-shield-halved mr-2"></i> Admin Panel
        </button>
      </div>

      <!-- Quick stats pill -->
      <div class="flex items-center gap-4 text-xs font-medium text-slate-400 bg-slate-900/60 border border-slate-800/80 px-4 py-2 rounded-xl">
        <span><strong class="text-slate-200" id="stat-total-fleet">0</strong> Vehicles</span>
        <span>•</span>
        <span><strong class="text-emerald-400" id="stat-avail-fleet">0</strong> Available</span>
        <span>•</span>
        <span><strong class="text-blue-400" id="stat-rented-fleet">0</strong> Active Rentals</span>
      </div>
    </div>

    <!-- VIEW 1: FLEET BROWSER -->
    <section id="view-fleet" class="space-y-6">
      <!-- Filter Bar -->
      <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80">
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase tracking-wider font-bold text-slate-500 mr-2">Filter By:</span>
          <button onclick="setFilterType('All')" id="filter-all" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-white border border-slate-700">All</button>
          <button onclick="setFilterType('Car')" id="filter-car" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800">Cars</button>
          <button onclick="setFilterType('Bike')" id="filter-bike" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800">Bikes</button>
        </div>
        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 text-xs font-medium cursor-pointer text-slate-400 hover:text-slate-200">
            <input type="checkbox" id="avail-only-toggle" onchange="renderFleet()" class="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0">
            Available only
          </label>
        </div>
      </div>

      <!-- Vehicle Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="vehicles-grid">
        <!-- Rendered by JS -->
      </div>
    </section>

    <!-- VIEW 2: MY RENTALS -->
    <section id="view-myrentals" class="hidden space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-white">My Rental History</h2>
          <p class="text-sm text-slate-400">View active bookings, return rented vehicles, and track past receipts.</p>
        </div>
      </div>
      <div class="space-y-4" id="my-rentals-list">
        <!-- Rendered by JS -->
      </div>
    </section>

    <!-- VIEW 3: ADMIN PANEL -->
    <section id="view-admin" class="hidden space-y-8">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-white">Fleet & Operations Control</h2>
          <p class="text-sm text-slate-400">Add or manage vehicles, inspect system rentals, and view total revenues.</p>
        </div>
        <button onclick="openAddVehicleModal()" class="px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center gap-2">
          <i class="fa-solid fa-plus"></i> Add Vehicle
        </button>
      </div>

      <!-- Admin Vehicle Table -->
      <div class="bg-slate-900/60 rounded-2xl border border-slate-800 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-800 font-bold text-slate-200">System Vehicles</div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs uppercase bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-6 py-3">ID</th>
                <th class="px-6 py-3">Type</th>
                <th class="px-6 py-3">Model</th>
                <th class="px-6 py-3">Daily Rate</th>
                <th class="px-6 py-3">Specifications</th>
                <th class="px-6 py-3">Status</th>
                <th class="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60" id="admin-vehicles-table">
              <!-- Rendered by JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Admin All Rentals -->
      <div class="bg-slate-900/60 rounded-2xl border border-slate-800 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-800 font-bold text-slate-200">All Customer Rentals</div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs uppercase bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-6 py-3">Rental ID</th>
                <th class="px-6 py-3">Customer</th>
                <th class="px-6 py-3">Vehicle</th>
                <th class="px-6 py-3">Days</th>
                <th class="px-6 py-3">Total Paid</th>
                <th class="px-6 py-3">Rent Date</th>
                <th class="px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60" id="admin-rentals-table">
              <!-- Rendered by JS -->
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </main>

  <!-- AUTH MODAL (LOGIN / REGISTER) -->
  <div id="auth-modal" class="fixed inset-0 z-50 hidden flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
      <button onclick="closeAuthModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white">
        <i class="fa-solid fa-xmark text-lg"></i>
      </button>

      <div class="flex items-center gap-2 border-b border-slate-800 pb-4 mb-6">
        <button onclick="switchAuthTab('cust-login')" id="auth-tab-cust-login" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 text-white">Customer Sign In</button>
        <button onclick="switchAuthTab('cust-reg')" id="auth-tab-cust-reg" class="px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Register</button>
        <button onclick="switchAuthTab('admin-login')" id="auth-tab-admin-login" class="px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-400 hover:text-white">Admin</button>
      </div>

      <!-- Customer Login Form -->
      <form id="form-cust-login" onsubmit="handleCustomerLogin(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Username</label>
          <input type="text" id="cust-login-user" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Password</label>
          <input type="password" id="cust-login-pass" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <button type="submit" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition">Sign In</button>
      </form>

      <!-- Customer Register Form -->
      <form id="form-cust-reg" onsubmit="handleCustomerRegister(event)" class="space-y-3 hidden">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Username</label>
          <input type="text" id="reg-user" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Password (min 4 chars)</label>
          <input type="password" id="reg-pass" required minlength="4" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
          <input type="text" id="reg-name" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Phone Number</label>
          <input type="text" id="reg-phone" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Email Address</label>
          <input type="email" id="reg-email" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <button type="submit" class="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition">Create Account</button>
      </form>

      <!-- Admin Login Form -->
      <form id="form-admin-login" onsubmit="handleAdminLogin(event)" class="space-y-4 hidden">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Admin Username</label>
          <input type="text" id="admin-user" value="admin" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Admin Password</label>
          <input type="password" id="admin-pass" value="admin123" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <button type="submit" class="w-full py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm transition">Unlock Admin Portal</button>
      </form>
    </div>
  </div>

  <!-- RENT VEHICLE MODAL -->
  <div id="rent-modal" class="fixed inset-0 z-50 hidden flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
      <button onclick="closeRentModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white">
        <i class="fa-solid fa-xmark text-lg"></i>
      </button>

      <h3 class="text-xl font-bold text-white mb-1" id="rent-vehicle-title">Rent Vehicle</h3>
      <p class="text-xs text-slate-400 mb-6" id="rent-vehicle-subtitle">Vehicle Specs</p>

      <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 mb-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm text-slate-400">Daily Rate:</span>
          <span class="text-base font-bold text-blue-400" id="rent-daily-rate">Rs. 0.00</span>
        </div>
        <div class="space-y-2 mt-4">
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-slate-300">Duration:</span>
            <span class="text-sm font-bold text-white"><span id="rent-days-display">3</span> Days</span>
          </div>
          <input type="range" id="rent-days-slider" min="1" max="30" value="3" oninput="updateRentCalculation()" class="w-full accent-blue-600 cursor-pointer">
        </div>
      </div>

      <div class="flex justify-between items-center bg-blue-950/30 border border-blue-800/40 p-4 rounded-xl mb-6">
        <span class="text-sm font-medium text-slate-300">Total Charge:</span>
        <span class="text-2xl font-bold text-emerald-400" id="rent-total-display">Rs. 0.00</span>
      </div>

      <div class="flex gap-3">
        <button onclick="closeRentModal()" class="w-1/2 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-sm">Cancel</button>
        <button onclick="confirmRental()" class="w-1/2 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm">Confirm Booking</button>
      </div>
    </div>
  </div>

  <!-- ADD VEHICLE MODAL (ADMIN) -->
  <div id="add-vehicle-modal" class="fixed inset-0 z-50 hidden flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
      <button onclick="closeAddVehicleModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white">
        <i class="fa-solid fa-xmark text-lg"></i>
      </button>

      <h3 class="text-xl font-bold text-white mb-4">Add New Fleet Vehicle</h3>

      <form onsubmit="handleAddVehicle(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Vehicle ID</label>
          <input type="text" id="add-id" placeholder="C103 or B103" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Vehicle Type</label>
          <select id="add-type" onchange="toggleAddVehicleSpecs()" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
            <option value="Car">Car</option>
            <option value="Bike">Bike</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Model Name</label>
          <input type="text" id="add-model" placeholder="e.g. Honda City" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1">Daily Rental Price (Rs.)</label>
          <input type="number" id="add-price" step="0.01" min="1" placeholder="2000.00" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div id="add-spec1-container">
          <label class="block text-xs font-medium text-slate-400 mb-1" id="add-spec1-label">Number of Seats (1-12)</label>
          <input type="number" id="add-spec1" min="1" max="3000" value="5" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500">
        </div>
        <div class="flex items-center gap-2 pt-2">
          <input type="checkbox" id="add-spec2" checked class="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0">
          <label class="text-xs text-slate-300" id="add-spec2-label">Automatic Transmission</label>
        </div>
        <button type="submit" class="w-full mt-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition">Save to Fleet</button>
      </form>
    </div>
  </div>

  <script>
    let appState = {
      currentUser: null, // null, customer object, or "ADMIN"
      vehicles: [],
      rentals: [],
      filterType: 'All',
      selectedVehicleForRent: null
    };

    async function loadData() {
      try {
        const res = await fetch('/api/data');
        const data = await res.json();
        appState.vehicles = data.vehicles;
        appState.rentals = data.rentals;
        updateStats();
        renderNav();
        renderFleet();
        if (appState.currentUser === 'ADMIN') renderAdmin();
        if (appState.currentUser && appState.currentUser !== 'ADMIN') renderMyRentals();
      } catch (err) {
        console.error("Failed to load data:", err);
      }
    }

    function updateStats() {
      document.getElementById('stat-total-fleet').innerText = appState.vehicles.length;
      document.getElementById('stat-avail-fleet').innerText = appState.vehicles.filter(v => v.available).length;
      document.getElementById('stat-rented-fleet').innerText = appState.rentals.filter(r => r.status === 'ACTIVE').length;
    }

    function renderNav() {
      const area = document.getElementById('nav-user-area');
      const tabMyRentals = document.getElementById('tab-myrentals');
      const tabAdmin = document.getElementById('tab-admin');

      if (!appState.currentUser) {
        tabMyRentals.classList.add('hidden');
        tabAdmin.classList.add('hidden');
        area.innerHTML = `
          <button onclick="openAuthModal('cust-login')" class="px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow">Sign In / Register</button>
        `;
      } else if (appState.currentUser === 'ADMIN') {
        tabMyRentals.classList.add('hidden');
        tabAdmin.classList.remove('hidden');
        area.innerHTML = `
          <div class="flex items-center gap-3">
            <span class="text-xs px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold"><i class="fa-solid fa-shield-halved mr-1.5"></i> Admin</span>
            <button onclick="handleLogout()" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300">Logout</button>
          </div>
        `;
      } else {
        tabMyRentals.classList.remove('hidden');
        tabAdmin.classList.add('hidden');
        area.innerHTML = `
          <div class="flex items-center gap-3">
            <span class="text-xs font-medium text-slate-300"><i class="fa-solid fa-user-circle mr-1 text-blue-400"></i> ${appState.currentUser.name}</span>
            <button onclick="handleLogout()" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300">Logout</button>
          </div>
        `;
      }
    }

    function switchTab(tab) {
      ['fleet', 'myrentals', 'admin'].forEach(t => {
        const view = document.getElementById('view-' + t);
        const btn = document.getElementById('tab-' + t);
        if (view) view.classList.add('hidden');
        if (btn) {
          btn.classList.remove('bg-blue-600', 'text-white', 'shadow');
          btn.classList.add('text-slate-400');
        }
      });
      document.getElementById('view-' + tab).classList.remove('hidden');
      const activeBtn = document.getElementById('tab-' + tab);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-400');
        activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow');
      }

      if (tab === 'fleet') renderFleet();
      if (tab === 'myrentals') renderMyRentals();
      if (tab === 'admin') renderAdmin();
    }

    function setFilterType(type) {
      appState.filterType = type;
      ['All', 'Car', 'Bike'].forEach(t => {
        const btn = document.getElementById('filter-' + t.toLowerCase());
        if (btn) {
          if (t === type) {
            btn.className = "px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-white border border-slate-700";
          } else {
            btn.className = "px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800";
          }
        }
      });
      renderFleet();
    }

    function renderFleet() {
      const grid = document.getElementById('vehicles-grid');
      grid.innerHTML = '';

      const availOnly = document.getElementById('avail-only-toggle').checked;
      const list = appState.vehicles.filter(v => {
        if (appState.filterType === 'Car' && v.type !== 'Car') return false;
        if (appState.filterType === 'Bike' && v.type !== 'Bike') return false;
        if (availOnly && !v.available) return false;
        return true;
      });

      if (list.length === 0) {
        grid.innerHTML = `<div class="col-span-full py-12 text-center text-slate-500 font-medium">No vehicles found matching filters.</div>`;
        return;
      }

      list.forEach(v => {
        const isCar = v.type === 'Car';
        const icon = isCar ? 'fa-car-side' : 'fa-motorcycle';
        const specText = isCar 
          ? `<span><i class="fa-solid fa-chair mr-1"></i> ${v.spec1} Seats</span> • <span>${v.spec2 ? 'Automatic' : 'Manual'}</span>`
          : `<span><i class="fa-solid fa-gauge mr-1"></i> ${v.spec1} cc</span> • <span>${v.spec2 ? 'Helmet Included' : 'No Helmet'}</span>`;

        const statusBadge = v.available 
          ? `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Available</span>`
          : `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">Rented</span>`;

        let actionBtn = '';
        if (v.available) {
          if (appState.currentUser && appState.currentUser !== 'ADMIN') {
            actionBtn = `<button onclick="openRentModal('${v.id}')" class="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md shadow-emerald-600/20">Rent Vehicle</button>`;
          } else if (appState.currentUser === 'ADMIN') {
            actionBtn = `<div class="text-center text-xs text-slate-500 py-2">Admin View</div>`;
          } else {
            actionBtn = `<button onclick="openAuthModal('cust-login')" class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition">Sign In to Rent</button>`;
          }
        } else {
          actionBtn = `<button disabled class="w-full py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-600 font-semibold text-xs cursor-not-allowed">Currently Rented</button>`;
        }

        grid.innerHTML += `
          <div class="glass-card rounded-2xl p-5 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-blue-400">
                    <i class="fa-solid ${icon}"></i>
                  </div>
                  <div>
                    <h4 class="font-bold text-white text-base leading-tight">${v.model}</h4>
                    <span class="text-xs text-slate-500 font-mono">${v.id}</span>
                  </div>
                </div>
                ${statusBadge}
              </div>
              <div class="text-xs text-slate-400 space-x-2 pb-4 border-b border-slate-800">
                ${specText}
              </div>
            </div>

            <div class="mt-4">
              <div class="flex items-baseline justify-between mb-4">
                <span class="text-xs text-slate-400">Daily Rate:</span>
                <span class="text-lg font-bold text-blue-400">Rs. ${parseFloat(v.price).toFixed(2)}</span>
              </div>
              ${actionBtn}
            </div>
          </div>
        `;
      });
    }

    function renderMyRentals() {
      const container = document.getElementById('my-rentals-list');
      container.innerHTML = '';

      if (!appState.currentUser || appState.currentUser === 'ADMIN') return;

      const my = appState.rentals.filter(r => r.username === appState.currentUser.username);
      if (my.length === 0) {
        container.innerHTML = `<div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-500">You have no rental contracts yet. Browse the fleet and rent a vehicle!</div>`;
        return;
      }

      my.slice().reverse().forEach(r => {
        const isActive = r.status === 'ACTIVE';
        const returnBtn = isActive 
          ? `<button onclick="handleReturn('${r.rental_id}')" class="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600/20 text-rose-400 border border-rose-500/30 hover:bg-rose-600 hover:text-white transition">Return Vehicle</button>`
          : `<span class="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-500">Completed on ${r.return_date}</span>`;

        container.innerHTML += `
          <div class="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-3 mb-1">
                <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">${r.rental_id}</span>
                <h4 class="font-bold text-white text-base">${r.vehicle_model} (${r.vehicle_id})</h4>
              </div>
              <p class="text-xs text-slate-400">Rented on: <strong>${r.rent_date}</strong> • Duration: <strong>${r.days} days</strong> • Daily: Rs. ${parseFloat(r.price_per_day).toFixed(2)}</p>
            </div>
            <div class="flex items-center gap-6">
              <div class="text-right">
                <span class="block text-xs text-slate-500">Total Paid</span>
                <span class="text-lg font-bold text-emerald-400">Rs. ${parseFloat(r.total_charge).toFixed(2)}</span>
              </div>
              ${returnBtn}
            </div>
          </div>
        `;
      });
    }

    function renderAdmin() {
      const vBody = document.getElementById('admin-vehicles-table');
      const rBody = document.getElementById('admin-rentals-table');
      vBody.innerHTML = '';
      rBody.innerHTML = '';

      appState.vehicles.forEach(v => {
        const specStr = v.type === 'Car' 
          ? `${v.spec1} seats, ${v.spec2 ? 'Automatic' : 'Manual'}`
          : `${v.spec1} cc, ${v.spec2 ? 'Helmet' : 'No helmet'}`;

        const delBtn = v.available 
          ? `<button onclick="handleDeleteVehicle('${v.id}')" class="px-2.5 py-1 text-xs rounded-lg bg-rose-600/20 text-rose-400 hover:bg-rose-600 hover:text-white transition">Remove</button>`
          : `<span class="text-xs text-slate-600 cursor-not-allowed">Rented</span>`;

        vBody.innerHTML += `
          <tr class="hover:bg-slate-800/40">
            <td class="px-6 py-4 font-mono font-bold text-blue-400">${v.id}</td>
            <td class="px-6 py-4">${v.type}</td>
            <td class="px-6 py-4 font-medium text-white">${v.model}</td>
            <td class="px-6 py-4">Rs. ${parseFloat(v.price).toFixed(2)}</td>
            <td class="px-6 py-4 text-slate-400">${specStr}</td>
            <td class="px-6 py-4"><span class="px-2 py-0.5 rounded text-xs font-bold ${v.available ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}">${v.available ? 'Available' : 'Rented'}</span></td>
            <td class="px-6 py-4 text-right">${delBtn}</td>
          </tr>
        `;
      });

      appState.rentals.slice().reverse().forEach(r => {
        rBody.innerHTML += `
          <tr class="hover:bg-slate-800/40">
            <td class="px-6 py-4 font-mono text-blue-400">${r.rental_id}</td>
            <td class="px-6 py-4 font-medium text-white">@${r.username}</td>
            <td class="px-6 py-4">${r.vehicle_model} (${r.vehicle_id})</td>
            <td class="px-6 py-4">${r.days}</td>
            <td class="px-6 py-4 font-bold text-emerald-400">Rs. ${parseFloat(r.total_charge).toFixed(2)}</td>
            <td class="px-6 py-4 text-slate-400">${r.rent_date}</td>
            <td class="px-6 py-4"><span class="px-2 py-0.5 rounded text-xs font-bold ${r.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}">${r.status}</span></td>
          </tr>
        `;
      });
    }

    // Modal Handlers
    function openAuthModal(tab) {
      document.getElementById('auth-modal').classList.remove('hidden');
      switchAuthTab(tab);
    }
    function closeAuthModal() {
      document.getElementById('auth-modal').classList.add('hidden');
    }
    function switchAuthTab(tab) {
      ['cust-login', 'cust-reg', 'admin-login'].forEach(t => {
        document.getElementById('form-' + t).classList.add('hidden');
        document.getElementById('auth-tab-' + t).className = "px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-400 hover:text-white";
      });
      document.getElementById('form-' + tab).classList.remove('hidden');
      document.getElementById('auth-tab-' + tab).className = "px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 text-white";
    }

    async function handleCustomerLogin(e) {
      e.preventDefault();
      const u = document.getElementById('cust-login-user').value.trim();
      const p = document.getElementById('cust-login-pass').value.trim();
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
      });
      const data = await res.json();
      if (data.success) {
        appState.currentUser = data.customer;
        closeAuthModal();
        renderNav();
        renderFleet();
        switchTab('fleet');
      } else {
        alert(data.message || 'Login failed.');
      }
    }

    async function handleCustomerRegister(e) {
      e.preventDefault();
      const u = document.getElementById('reg-user').value.trim();
      const p = document.getElementById('reg-pass').value.trim();
      const n = document.getElementById('reg-name').value.trim();
      const ph = document.getElementById('reg-phone').value.trim();
      const em = document.getElementById('reg-email').value.trim();

      const res = await fetch('/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p, name: n, phone: ph, email: em})
      });
      const data = await res.json();
      if (data.success) {
        alert('Account created! Please sign in.');
        switchAuthTab('cust-login');
        document.getElementById('cust-login-user').value = u;
      } else {
        alert(data.message || 'Registration failed.');
      }
    }

    function handleAdminLogin(e) {
      e.preventDefault();
      const u = document.getElementById('admin-user').value.trim();
      const p = document.getElementById('admin-pass').value.trim();
      if (u === 'admin' && p === 'admin123') {
        appState.currentUser = 'ADMIN';
        closeAuthModal();
        renderNav();
        switchTab('admin');
      } else {
        alert('Incorrect admin credentials.');
      }
    }

    function handleLogout() {
      appState.currentUser = null;
      renderNav();
      switchTab('fleet');
    }

    function openRentModal(vid) {
      const v = appState.vehicles.find(item => item.id === vid);
      if (!v) return;
      appState.selectedVehicleForRent = v;
      document.getElementById('rent-vehicle-title').innerText = `Rent ${v.model}`;
      document.getElementById('rent-vehicle-subtitle').innerText = `${v.type} • ID: ${v.id}`;
      document.getElementById('rent-daily-rate').innerText = `Rs. ${parseFloat(v.price).toFixed(2)} / day`;
      document.getElementById('rent-days-slider').value = 3;
      updateRentCalculation();
      document.getElementById('rent-modal').classList.remove('hidden');
    }

    function closeRentModal() {
      document.getElementById('rent-modal').classList.add('hidden');
    }

    function updateRentCalculation() {
      const days = parseInt(document.getElementById('rent-days-slider').value);
      document.getElementById('rent-days-display').innerText = days;
      if (appState.selectedVehicleForRent) {
        const total = days * parseFloat(appState.selectedVehicleForRent.price);
        document.getElementById('rent-total-display').innerText = `Rs. ${total.toFixed(2)}`;
      }
    }

    async function confirmRental() {
      const days = parseInt(document.getElementById('rent-days-slider').value);
      const v = appState.selectedVehicleForRent;
      const res = await fetch('/api/rent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: appState.currentUser.username,
          vehicle_id: v.id,
          days: days
        })
      });
      const data = await res.json();
      if (data.success) {
        closeRentModal();
        alert(`Rental Confirmed! Rental ID: ${data.rental_id}`);
        await loadData();
        switchTab('myrentals');
      } else {
        alert(data.message || 'Rental failed.');
      }
    }

    async function handleReturn(rentalId) {
      if (!confirm('Are you sure you want to return this vehicle?')) return;
      const res = await fetch('/api/return', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rental_id: rentalId})
      });
      const data = await res.json();
      if (data.success) {
        alert('Vehicle returned successfully!');
        await loadData();
        renderMyRentals();
      } else {
        alert(data.message || 'Return failed.');
      }
    }

    function openAddVehicleModal() {
      document.getElementById('add-vehicle-modal').classList.remove('hidden');
      toggleAddVehicleSpecs();
    }
    function closeAddVehicleModal() {
      document.getElementById('add-vehicle-modal').classList.add('hidden');
    }

    function toggleAddVehicleSpecs() {
      const type = document.getElementById('add-type').value;
      if (type === 'Car') {
        document.getElementById('add-spec1-label').innerText = 'Number of Seats (1-12)';
        document.getElementById('add-spec1').value = '5';
        document.getElementById('add-spec2-label').innerText = 'Automatic Transmission';
      } else {
        document.getElementById('add-spec1-label').innerText = 'Engine Capacity (CC, 50-3000)';
        document.getElementById('add-spec1').value = '150';
        document.getElementById('add-spec2-label').innerText = 'Helmet Included';
      }
    }

    async function handleAddVehicle(e) {
      e.preventDefault();
      const id = document.getElementById('add-id').value.trim();
      const type = document.getElementById('add-type').value;
      const model = document.getElementById('add-model').value.trim();
      const price = parseFloat(document.getElementById('add-price').value);
      const spec1 = parseInt(document.getElementById('add-spec1').value);
      const spec2 = document.getElementById('add-spec2').checked;

      const res = await fetch('/api/vehicles/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id, type, model, price, spec1, spec2})
      });
      const data = await res.json();
      if (data.success) {
        closeAddVehicleModal();
        alert('Vehicle added to fleet!');
        await loadData();
        renderAdmin();
      } else {
        alert(data.message || 'Could not add vehicle.');
      }
    }

    async function handleDeleteVehicle(vid) {
      if (!confirm(`Are you sure you want to remove vehicle ${vid}?`)) return;
      const res = await fetch('/api/vehicles/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: vid})
      });
      const data = await res.json();
      if (data.success) {
        alert('Vehicle removed successfully.');
        await loadData();
        renderAdmin();
      } else {
        alert(data.message || 'Could not remove vehicle.');
      }
    }

    // Init
    loadData();
  </script>
</body>
</html>
"""


class RideEaseWebHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif url.path == "/api/data":
            store.load()
            vehicles = [{
                "id": v.id, "type": v.type, "model": v.model,
                "price": v.price, "spec1": v.spec1, "spec2": v.spec2,
                "available": v.available
            } for v in store.vehicles]
            rentals = [{
                "rental_id": r.rental_id, "username": r.username,
                "vehicle_id": r.vehicle_id, "vehicle_type": r.vehicle_type,
                "vehicle_model": r.vehicle_model, "days": r.days,
                "price_per_day": r.price_per_day, "total_charge": r.total_charge,
                "rent_date": r.rent_date, "return_date": r.return_date,
                "status": r.status
            } for r in store.rentals]
            self._send_json(200, {"vehicles": vehicles, "rentals": rentals})
        else:
            self.send_error(404)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        payload = json.loads(body) if body else {}

        if url.path == "/api/login":
            u = payload.get("username", "")
            p = payload.get("password", "")
            cust = store.find_customer(u)
            if cust and cust.verify_password(p):
                self._send_json(200, {"success": True, "customer": {
                    "username": cust.username, "name": cust.name,
                    "phone": cust.phone, "email": cust.email
                }})
            else:
                self._send_json(401, {"success": False, "message": "Incorrect username or password."})

        elif url.path == "/api/register":
            u = payload.get("username", "").strip()
            p = payload.get("password", "").strip()
            n = payload.get("name", "").strip()
            ph = payload.get("phone", "").strip()
            em = payload.get("email", "").strip()

            if not all([u, p, n, ph, em]):
                self._send_json(400, {"success": False, "message": "All fields required."})
                return
            if len(p) < 4:
                self._send_json(400, {"success": False, "message": "Password must be at least 4 characters."})
                return
            if store.find_customer(u) or u.lower() == "admin":
                self._send_json(400, {"success": False, "message": "Username already taken."})
                return

            cust = Customer(u, p, n, ph, em)
            store.customers.append(cust)
            store.save_all()
            self._send_json(200, {"success": True})

        elif url.path == "/api/rent":
            u = payload.get("username")
            vid = payload.get("vehicle_id")
            days = int(payload.get("days", 1))

            v = store.find_vehicle(vid)
            if not v or not v.available:
                self._send_json(400, {"success": False, "message": "Vehicle not available."})
                return

            total = v.price * days
            rid = store.next_rental_id()
            today = datetime.date.today().isoformat()
            new_r = Rental(rid, u, v.id, v.type, v.model, days, v.price, total, today, "", "ACTIVE")
            store.rentals.append(new_r)
            v.available = False
            store.save_all()
            self._send_json(200, {"success": True, "rental_id": rid})

        elif url.path == "/api/return":
            rid = payload.get("rental_id")
            r = store.find_rental(rid)
            if not r or not r.is_active():
                self._send_json(400, {"success": False, "message": "Active rental not found."})
                return

            today = datetime.date.today().isoformat()
            r.mark_returned(today)
            v = store.find_vehicle(r.vehicle_id)
            if v:
                v.available = True
            store.save_all()
            self._send_json(200, {"success": True})

        elif url.path == "/api/vehicles/add":
            vid = payload.get("id", "").strip()
            vtype = payload.get("type")
            model = payload.get("model", "").strip()
            price = float(payload.get("price", 0))
            s1 = int(payload.get("spec1", 0))
            s2 = bool(payload.get("spec2", False))

            if store.find_vehicle(vid):
                self._send_json(400, {"success": False, "message": "Vehicle ID already exists."})
                return

            v = Vehicle(vtype, vid, model, price, s1, s2, True)
            store.vehicles.append(v)
            store.save_all()
            self._send_json(200, {"success": True})

        elif url.path == "/api/vehicles/delete":
            vid = payload.get("id")
            v = store.find_vehicle(vid)
            if not v:
                self._send_json(404, {"success": False, "message": "Vehicle not found."})
                return
            if not v.available:
                self._send_json(400, {"success": False, "message": "A rented vehicle cannot be removed."})
                return

            store.vehicles = [veh for veh in store.vehicles if veh.id != vid]
            store.save_all()
            self._send_json(200, {"success": True})


def run_server(port=PORT):
    server = HTTPServer(("0.0.0.0", port), RideEaseWebHandler)
    print(f"RideEase Web GUI running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)

