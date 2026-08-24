# 🌾 Sugar Module & Sugar Desk (Tally Wrapper)

**Sugar Module** is a comprehensive Sugar Trading & Mill ERP extension for Frappe Framework and ERPNext. It includes **Sugar Desk**, a high-speed, keyboard-first Vue.js 3 single-page application modeled after **Tally ERP** ergonomics for rapid voucher entry, live stock tracking, and audit registers.

---

## ✨ Features

- **⚡ Tally-Style Keyboard Ergonomics**:
  - Full keyboard voucher navigation with <kbd>Tab</kbd> / <kbd>Enter</kbd> advance and <kbd>Shift+Tab</kbd> / <kbd>Esc</kbd> retreat.
  - Standard accounting Function Keys (<kbd>F4</kbd> to <kbd>F10</kbd>).
  - <kbd>Alt+G</kbd> "Go To" Command Palette for instant navigation.
  - <kbd>Alt+L</kbd> register list toggle from within any voucher.
- **📄 Core Vouchers**:
  - **Sugar Purchase (<kbd>F9</kbd>)**: Cane supplier & sugar mill procurement with grade, quintals, rates, and automatic value calculation.
  - **Dispatch Entry (<kbd>F8</kbd>)**: Sales dispatches with customer party, broker, vehicle number, quintals, and rate.
  - **Purchase Payment (<kbd>F5</kbd>)**: Supplier payment tracking (RTGS, NEFT, IMPS, Cheque, Cash) with UTR references.
  - **Broker Party Payment (<kbd>F6</kbd>)**: Customer receipts and broker commission settlement.
  - **Contra (<kbd>F4</kbd>)**: Bank-to-bank and cash transfer vouchers.
- **📋 Registers & Audit**:
  - **Sugar Purchase Register (<kbd>L</kbd>)**: Detailed list of all purchases with live available stock quintals and KPI totals.
  - **Dispatch Entry Register (<kbd>K</kbd>)**: List of deliveries with pending balance calculations.
  - **Day Book (<kbd>B</kbd> / <kbd>F10</kbd>)**: Unified multi-voucher chronological transaction stream.
- **🔍 Live Typeahead Search**:
  - Real-time dropdown search across Suppliers, Customers, Brokers, Items, and Bank Accounts.

---

## ⌨️ Keyboard Shortcuts Reference

| Key | Action | Description |
| :--- | :--- | :--- |
| **`F9`** / **`P`** | Sugar Purchase | Open Sugar Purchase voucher entry |
| **`F8`** / **`D`** | Dispatch Entry | Open Dispatch & Delivery voucher entry |
| **`F5`** / **`Y`** | Purchase Payment | Open Supplier Payment voucher entry |
| **`F6`** / **`R`** | Broker Receipt | Open Customer / Broker Receipt voucher entry |
| **`F4`** | Contra Voucher | Open Bank / Cash Transfer entry |
| **`L`** / **`Alt+L`** | Purchase Register | View list of all sugar purchases with stock |
| **`K`** | Dispatch Register | View list of all dispatch entries |
| **`B`** / **`F10`** | Day Book | Open unified Day Book & audit stream |
| **`M`** | Masters Directory | Browse Suppliers, Customers, Brokers, and Items |
| **`Alt+G`** | Go To Palette | Global command search popup |
| **`Esc`** | Back / Gateway | Return to Gateway or dismiss modals |
| **`Enter`** | Accept / Next | Advance field / accept voucher on narration |

---

## 🚀 Installation

### 1. Install App into Bench
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/rohansapkale/Sugar_Module.git --branch sugar-module
bench --site <your-site-name> install-app sugar_module
bench --site <your-site-name> migrate
```

### 2. Build Production Assets
```bash
bench build --app sugar_module
```

### 3. Access Sugar Desk
- **Direct Web URL**: `http://<your-site-name>:8000/sugar-desk`
- **Frappe Desk**: Open App Switcher (top-left 9 dots) and select **Sugar Desk (Tally)**.

---

## 💻 Frontend Development (`apps/sugar_module/frontend`)

The frontend is built with **Vue 3**, **Vite**, and **Vue Router**.

### Directory Structure
```text
apps/sugar_module/frontend/
├── src/
│   ├── components/common/   # Reusable UI (FunctionKeyBar, GoToPalette, LedgerDropdown, etc.)
│   ├── composables/         # useFrappeApi.js, useKeyboardEngine.js
│   ├── router/              # Vue Router configuration
│   ├── views/               # GatewayView, VoucherEntryView, RegisterView, DayBookView, MastersView
│   ├── App.vue
│   ├── main.js
│   └── style.css            # Tally-inspired responsive design system
├── index.html
├── package.json
└── vite.config.js
```

### Running Frontend in Dev Mode (Hot-Reload)
```bash
cd apps/sugar_module/frontend
npm install
npm run dev -- --host
```
The development server runs on `http://localhost:8080` and proxies API requests automatically to your Frappe backend on port `8001` with `X-Frappe-Site-Name`.

### Building Frontend for Production
```bash
cd apps/sugar_module/frontend
npm run build
```
This bundles the application directly into `apps/sugar_module/sugar_module/public/frontend/`, which Frappe serves under `/sugar-desk`.

---

## 🛠️ Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/sugar_module
pre-commit install
```

Tools configured:
- `ruff`
- `eslint`
- `prettier`
- `pyupgrade`

---

## 📄 License

MIT License © Rohan Sapkale
