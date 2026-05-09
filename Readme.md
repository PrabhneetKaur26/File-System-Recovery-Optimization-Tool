# File System Recovery & Optimization Tool
Simulated File System with Bitmap Allocation, Inode Table, WAL Journaling, LRU Cache, Defragmentation & Forensic Analysis

## Project Overview

This project implements a **fully simulated file system** , visualized through an interactive **Streamlit dashboard**. It demonstrates core OS concepts including free-space management, inode-based metadata, journaling for crash recovery, caching for read optimization, and disk defragmentation.
The system supports real-time file operations, crash injection, and journal replay.

---

## Features

### Core File System
* Bitmap Allocation Tracks free/used blocks using a bit array; supports First Fit, Best Fit, and Contiguous Extent strategies 
* Inode Table Stores file metadata (name, size, block list, timestamps, permissions) for up to 32 files 
* Directory Tree and File Operations
* WAL Journaling, Write-Ahead Logging records every operation before it commits to disk 
* Crash Simulation, Randomly corrupts 25% of used blocks to simulate power loss or hardware failure 
* Journal Replay: Committed-but-uncheckpointed entries are replayed to restore consistency 
* Recovery Mode UI: Emergency UI with flashing alerts when crash is detected 

### Forensic Analysis
Detects 5 types of integrity issues:
- Corrupted Blocks 
- Orphan Inodes 
- Leaked Blocks
- Bitmap Inconsistency
- Double Allocation

## 🖥 Dashboard Tabs

* File Manager 
* Disk Heatmap 
* Live Terminal 
* Journal & Recovery 
* Performance 
* Forensics 
* Directory Tree 

---

## Installation & Running

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install streamlit plotly pandas
```

### Run the App
```bash
streamlit run app.py
```
---

## How to Test

### Basic Flow
1. **Create files** — Go to File Manager tab, enter name + content, click Create
2. **Read files** — Select a file and click Read to see content + cache behavior
3. **Watch Terminal** — Switch to Live Terminal tab to see real-time block operations

### Crash & Recovery Flow
1. Create 2–3 files
2. Click **CRASH** in the sidebar
3. Observe corrupted blocks (red) in the Disk Heatmap tab
4. Go to Journal & Recovery tab → Emergency Recovery Mode is active
5. Click **Run WAL Recovery** — journal replays committed entries
6. System returns to consistent state

### Optimization Flow
1. Create several files (mix of small and large)
2. Read some files multiple times → watch Cache Hit % rise
3. Delete some files → fragmentation appears in heatmap
4. Click **Defragment Disk** → blocks relocate to be contiguous
5. Run **Benchmark** to compare allocation strategies

### Forensic Scan
1. After a crash (without full recovery), click **Run Forensic Scan**
2. View corrupted blocks, orphan inodes, and any inconsistencies detected

---

## 👨‍💻 Technologies Used

- **Python 3** — Core language
- **Streamlit** — Interactive web dashboard
- **Plotly** — Charts, gauges, heatmap visualizations
- **Pandas** — Data tables and dataframe display

---

## Note

This project was developed with the assistance of AI tools for code generation and debugging.

---

