#!/usr/bin/env python3
"""
Generate NER Validation Dashboard from output.json
Usage: python generate_dashboard.py [input_file] [output_file]
"""

import json
import sys
from pathlib import Path

def generate_dashboard(input_file: str = "output.json", output_file: str = "ner_dashboard.html"):
    """Generate an interactive HTML dashboard from NER output data."""

    # Read the JSON lines file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        json_content = f.read().strip()

    # Validate JSON lines format
    lines = json_content.split('\n')
    data = []
    for i, line in enumerate(lines, 1):
        try:
            data.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON on line {i}: {e}")

    print(f"Loaded {len(data)} entity records")

    # Escape backticks and special characters for JavaScript template literal
    escaped_json = json_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NER Validation Dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            display: flex;
            height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            overflow-y: auto;
            flex-shrink: 0;
        }

        .sidebar h1 {
            font-size: 1.25rem;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #334155;
        }

        .test-case-btn {
            display: block;
            width: 100%;
            padding: 12px 15px;
            margin-bottom: 8px;
            background: #334155;
            border: none;
            border-radius: 8px;
            color: #e2e8f0;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
        }

        .test-case-btn:hover {
            background: #475569;
        }

        .test-case-btn.active {
            background: #3b82f6;
            color: white;
        }

        .test-case-btn .count {
            float: right;
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
        }

        /* Main content */
        .main-content {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .header h2 {
            font-size: 1.5rem;
            color: #1e293b;
        }

        /* Summary cards */
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .summary-card .label {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 5px;
        }

        .summary-card .value {
            font-size: 1.75rem;
            font-weight: 600;
            color: #1e293b;
        }

        .summary-card .value.loc { color: #059669; }
        .summary-card .value.org { color: #2563eb; }
        .summary-card .value.per { color: #dc2626; }
        .summary-card .value.misc { color: #7c3aed; }

        /* Phrase cards */
        .phrase-card {
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .phrase-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }

        .phrase-id {
            font-weight: 600;
            color: #1e293b;
        }

        .phrase-metrics {
            display: flex;
            gap: 15px;
            font-size: 0.85rem;
        }

        .phrase-metrics span {
            padding: 4px 10px;
            background: #e2e8f0;
            border-radius: 15px;
        }

        .phrase-text {
            padding: 20px;
            font-size: 1.05rem;
            line-height: 2;
            background: #fefefe;
        }

        /* Entity highlighting */
        .entity {
            padding: 2px 6px;
            border-radius: 4px;
            cursor: help;
            position: relative;
            font-weight: 500;
        }

        .entity-LOC {
            background: #d1fae5;
            border-bottom: 2px solid #059669;
            color: #065f46;
        }

        .entity-ORG {
            background: #dbeafe;
            border-bottom: 2px solid #2563eb;
            color: #1e40af;
        }

        .entity-PER {
            background: #fee2e2;
            border-bottom: 2px solid #dc2626;
            color: #991b1b;
        }

        .entity-MISC {
            background: #ede9fe;
            border-bottom: 2px solid #7c3aed;
            color: #5b21b6;
        }

        .entity-NA {
            background: #f1f5f9;
            border-bottom: 2px solid #94a3b8;
            color: #475569;
        }

        /* Tooltip */
        .tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293b;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s;
            z-index: 100;
            margin-bottom: 5px;
        }

        .entity:hover .tooltip {
            opacity: 1;
            visibility: visible;
        }

        /* Entity list */
        .entity-list {
            padding: 15px 20px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
        }

        .entity-list-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 10px;
        }

        .entity-table {
            width: 100%;
            font-size: 0.85rem;
            border-collapse: collapse;
        }

        .entity-table th {
            text-align: left;
            padding: 8px 10px;
            background: #e2e8f0;
            font-weight: 600;
            color: #475569;
        }

        .entity-table td {
            padding: 8px 10px;
            border-bottom: 1px solid #e2e8f0;
        }

        .entity-table tr:last-child td {
            border-bottom: none;
        }

        .score-bar {
            width: 60px;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }

        .score-fill {
            height: 100%;
            border-radius: 4px;
        }

        .score-high { background: #22c55e; }
        .score-medium { background: #f59e0b; }
        .score-low { background: #ef4444; }

        /* Legend */
        .legend {
            display: flex;
            gap: 20px;
            padding: 15px 20px;
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }

        .legend-color.loc { background: #d1fae5; border: 2px solid #059669; }
        .legend-color.org { background: #dbeafe; border: 2px solid #2563eb; }
        .legend-color.per { background: #fee2e2; border: 2px solid #dc2626; }
        .legend-color.misc { background: #ede9fe; border: 2px solid #7c3aed; }

        /* Filter */
        .filter-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #e2e8f0;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }

        .filter-btn:hover {
            border-color: #3b82f6;
        }

        .filter-btn.active {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }

        /* Confidence indicator */
        .confidence-indicator {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .avg-score {
            font-weight: 600;
        }

        .avg-score.high { color: #22c55e; }
        .avg-score.medium { color: #f59e0b; }
        .avg-score.low { color: #ef4444; }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .empty-state h3 {
            margin-bottom: 10px;
        }

        /* Overall stats panel */
        .overall-stats {
            background: linear-gradient(135deg, #1e293b, #334155);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }

        .overall-stats h3 {
            margin-bottom: 15px;
            font-size: 1rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .stat-item {
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }

        .stat-item .stat-label {
            font-size: 0.75rem;
            opacity: 0.8;
        }

        .stat-item .stat-value {
            font-size: 1.25rem;
            font-weight: 600;
        }

        /* Search */
        .search-box {
            margin-bottom: 20px;
        }

        .search-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
            transition: border-color 0.2s;
        }

        .search-input:focus {
            outline: none;
            border-color: #3b82f6;
        }

        /* Collapsible */
        .phrase-card.collapsed .phrase-text,
        .phrase-card.collapsed .entity-list {
            display: none;
        }

        .toggle-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 5px;
            color: #64748b;
            font-size: 1.2rem;
        }

        .toggle-btn:hover {
            color: #1e293b;
        }

        /* Export button */
        .export-btn {
            background: #059669;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-left: 10px;
        }

        .export-btn:hover {
            background: #047857;
        }
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <h1>NER Validation</h1>
            <div id="test-case-list"></div>
            <div class="overall-stats" id="overall-stats"></div>
        </aside>
        <main class="main-content">
            <div class="header">
                <h2 id="current-test-case">Select a Test Case</h2>
                <button class="export-btn" onclick="exportCSV()">Export CSV</button>
            </div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color loc"></div>
                    <span>LOC (Location)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color org"></div>
                    <span>ORG (Organization)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color per"></div>
                    <span>PER (Person)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color misc"></div>
                    <span>MISC (Miscellaneous)</span>
                </div>
            </div>
            <div class="search-box">
                <input type="text" class="search-input" placeholder="Search phrases or entities..." oninput="handleSearch(this.value)">
            </div>
            <div id="summary-cards" class="summary-cards"></div>
            <div class="filter-bar" id="filter-bar"></div>
            <div id="phrases-container"></div>
        </main>
    </div>

    <script>
        // Embedded NER data
        const jsonData = `''' + escaped_json + '''`;

        let data = [];
        let groupedData = {};
        let currentTestCase = null;
        let currentFilter = 'all';
        let searchQuery = '';

        function init() {
            // Parse JSON lines format
            const lines = jsonData.trim().split('\\n');
            data = lines.map(line => JSON.parse(line));

            // Group by test case
            groupedData = {};
            data.forEach(item => {
                if (!groupedData[item.Test_Case]) {
                    groupedData[item.Test_Case] = {};
                }
                if (!groupedData[item.Test_Case][item.Phrase_ID]) {
                    groupedData[item.Test_Case][item.Phrase_ID] = {
                        phrase: item.Phrase,
                        entities: []
                    };
                }
                groupedData[item.Test_Case][item.Phrase_ID].entities.push(item);
            });

            renderTestCaseList();
            renderOverallStats();

            // Select first test case
            const firstTestCase = Object.keys(groupedData)[0];
            if (firstTestCase) {
                selectTestCase(firstTestCase);
            }
        }

        function renderTestCaseList() {
            const container = document.getElementById('test-case-list');
            container.innerHTML = '';

            Object.keys(groupedData).forEach(testCase => {
                const phraseCount = Object.keys(groupedData[testCase]).length;
                const btn = document.createElement('button');
                btn.className = 'test-case-btn';
                btn.innerHTML = `
                    ${formatTestCaseName(testCase)}
                    <span class="count">${phraseCount}</span>
                `;
                btn.onclick = () => selectTestCase(testCase);
                btn.dataset.testCase = testCase;
                container.appendChild(btn);
            });
        }

        function formatTestCaseName(name) {
            return name.split('_').map(word =>
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }

        function selectTestCase(testCase) {
            currentTestCase = testCase;
            currentFilter = 'all';
            searchQuery = '';
            document.querySelector('.search-input').value = '';

            // Update active state
            document.querySelectorAll('.test-case-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.testCase === testCase);
            });

            document.getElementById('current-test-case').textContent = formatTestCaseName(testCase);

            renderSummaryCards();
            renderFilterBar();
            renderPhrases();
        }

        function renderSummaryCards() {
            const container = document.getElementById('summary-cards');
            const testCaseData = groupedData[currentTestCase];

            // Calculate metrics
            let totalEntities = 0;
            let entityCounts = { LOC: 0, ORG: 0, PER: 0, MISC: 0 };
            let totalScore = 0;
            let scoreCount = 0;
            let lowConfidenceCount = 0;

            Object.values(testCaseData).forEach(phrase => {
                phrase.entities.forEach(entity => {
                    if (entity.Entity_Group !== 'N/A') {
                        totalEntities++;
                        entityCounts[entity.Entity_Group] = (entityCounts[entity.Entity_Group] || 0) + 1;
                        const score = parseFloat(entity.Score);
                        totalScore += score;
                        scoreCount++;
                        if (score < 0.7) lowConfidenceCount++;
                    }
                });
            });

            const avgScore = scoreCount > 0 ? (totalScore / scoreCount).toFixed(4) : 'N/A';
            const phraseCount = Object.keys(testCaseData).length;

            container.innerHTML = `
                <div class="summary-card">
                    <div class="label">Total Phrases</div>
                    <div class="value">${phraseCount}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Total Entities</div>
                    <div class="value">${totalEntities}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Avg Confidence</div>
                    <div class="value ${getScoreClass(avgScore)}">${avgScore}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Low Confidence</div>
                    <div class="value score-low">${lowConfidenceCount}</div>
                </div>
                <div class="summary-card">
                    <div class="label">LOC Entities</div>
                    <div class="value loc">${entityCounts.LOC}</div>
                </div>
                <div class="summary-card">
                    <div class="label">ORG Entities</div>
                    <div class="value org">${entityCounts.ORG}</div>
                </div>
                <div class="summary-card">
                    <div class="label">PER Entities</div>
                    <div class="value per">${entityCounts.PER || 0}</div>
                </div>
                <div class="summary-card">
                    <div class="label">MISC Entities</div>
                    <div class="value misc">${entityCounts.MISC || 0}</div>
                </div>
            `;
        }

        function renderFilterBar() {
            const container = document.getElementById('filter-bar');
            const filters = ['all', 'LOC', 'ORG', 'PER', 'MISC', 'low-confidence'];

            container.innerHTML = filters.map(filter => `
                <button class="filter-btn ${currentFilter === filter ? 'active' : ''}"
                        onclick="setFilter('${filter}')">
                    ${filter === 'all' ? 'All Entities' :
                      filter === 'low-confidence' ? 'Low Confidence (<0.7)' : filter}
                </button>
            `).join('');
        }

        function setFilter(filter) {
            currentFilter = filter;
            renderFilterBar();
            renderPhrases();
        }

        function handleSearch(query) {
            searchQuery = query.toLowerCase();
            renderPhrases();
        }

        function renderPhrases() {
            const container = document.getElementById('phrases-container');
            const testCaseData = groupedData[currentTestCase];

            container.innerHTML = '';

            Object.entries(testCaseData).forEach(([phraseId, phraseData]) => {
                // Search filter
                if (searchQuery) {
                    const phraseMatch = phraseData.phrase.toLowerCase().includes(searchQuery);
                    const entityMatch = phraseData.entities.some(e =>
                        e.Word.toLowerCase().includes(searchQuery) ||
                        e.Entity_Group.toLowerCase().includes(searchQuery)
                    );
                    if (!phraseMatch && !entityMatch) return;
                }

                // Entity type filter
                let filteredEntities = phraseData.entities.filter(e => e.Entity_Group !== 'N/A');

                if (currentFilter !== 'all' && currentFilter !== 'low-confidence') {
                    filteredEntities = filteredEntities.filter(e => e.Entity_Group === currentFilter);
                } else if (currentFilter === 'low-confidence') {
                    filteredEntities = filteredEntities.filter(e => parseFloat(e.Score) < 0.7);
                }

                // Skip if no entities match filter (except for 'all')
                if (currentFilter !== 'all' && filteredEntities.length === 0) {
                    return;
                }

                const card = document.createElement('div');
                card.className = 'phrase-card';

                // Calculate phrase metrics
                const validEntities = phraseData.entities.filter(e => e.Entity_Group !== 'N/A');
                const avgScore = validEntities.length > 0
                    ? (validEntities.reduce((sum, e) => sum + parseFloat(e.Score), 0) / validEntities.length).toFixed(4)
                    : 'N/A';

                const displayEntities = currentFilter === 'all' ? validEntities : filteredEntities;

                card.innerHTML = `
                    <div class="phrase-header">
                        <span class="phrase-id">
                            <button class="toggle-btn" onclick="toggleCard(this)">▼</button>
                            Phrase #${phraseId}
                        </span>
                        <div class="phrase-metrics">
                            <span>${validEntities.length} entities</span>
                            <span class="confidence-indicator">
                                Avg: <span class="avg-score ${getScoreClass(avgScore)}">${avgScore}</span>
                            </span>
                        </div>
                    </div>
                    <div class="phrase-text">
                        ${highlightEntities(phraseData.phrase, displayEntities)}
                    </div>
                    <div class="entity-list">
                        <div class="entity-list-title">Detected Entities</div>
                        ${renderEntityTable(displayEntities)}
                    </div>
                `;

                container.appendChild(card);
            });

            if (container.children.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>No matches found</h3>
                        <p>No phrases match the current filter criteria.</p>
                    </div>
                `;
            }
        }

        function toggleCard(btn) {
            const card = btn.closest('.phrase-card');
            card.classList.toggle('collapsed');
            btn.textContent = card.classList.contains('collapsed') ? '▶' : '▼';
        }

        function highlightEntities(text, entities) {
            if (entities.length === 0) return escapeHtml(text);

            // Sort entities by start position (descending) to avoid position shifting
            const sortedEntities = [...entities].sort((a, b) => b.Start - a.Start);

            let result = text;
            sortedEntities.forEach(entity => {
                const before = result.substring(0, entity.Start);
                const entityText = result.substring(entity.Start, entity.End);
                const after = result.substring(entity.End);

                result = before +
                    `<span class="entity entity-${entity.Entity_Group}">` +
                    escapeHtml(entityText) +
                    `<span class="tooltip">${entity.Entity_Group}: ${entity.Score}</span>` +
                    `</span>` +
                    after;
            });

            // Escape parts that aren't already HTML
            return result;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function renderEntityTable(entities) {
            if (entities.length === 0) {
                return '<p style="color: #94a3b8; font-size: 0.85rem;">No entities detected</p>';
            }

            return `
                <table class="entity-table">
                    <thead>
                        <tr>
                            <th>Entity</th>
                            <th>Type</th>
                            <th>Confidence</th>
                            <th>Position</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${entities.map(e => `
                            <tr>
                                <td><strong>${escapeHtml(e.Word)}</strong></td>
                                <td><span class="entity entity-${e.Entity_Group}" style="padding: 2px 8px;">${e.Entity_Group}</span></td>
                                <td>
                                    <div class="score-bar">
                                        <div class="score-fill ${getScoreClass(e.Score)}"
                                             style="width: ${parseFloat(e.Score) * 100}%"></div>
                                    </div>
                                    ${e.Score}
                                </td>
                                <td>${e.Start}-${e.End}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        function getScoreClass(score) {
            const s = parseFloat(score);
            if (isNaN(s)) return '';
            if (s >= 0.85) return 'score-high';
            if (s >= 0.7) return 'score-medium';
            return 'score-low';
        }

        function renderOverallStats() {
            const container = document.getElementById('overall-stats');

            let totalPhrases = 0;
            let totalEntities = 0;
            let totalScore = 0;
            let scoreCount = 0;

            Object.values(groupedData).forEach(testCase => {
                Object.values(testCase).forEach(phrase => {
                    totalPhrases++;
                    phrase.entities.forEach(entity => {
                        if (entity.Entity_Group !== 'N/A') {
                            totalEntities++;
                            totalScore += parseFloat(entity.Score);
                            scoreCount++;
                        }
                    });
                });
            });

            const avgScore = scoreCount > 0 ? (totalScore / scoreCount).toFixed(4) : 'N/A';

            container.innerHTML = `
                <h3>Overall Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Test Cases</div>
                        <div class="stat-value">${Object.keys(groupedData).length}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Phrases</div>
                        <div class="stat-value">${totalPhrases}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Total Entities</div>
                        <div class="stat-value">${totalEntities}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Avg Confidence</div>
                        <div class="stat-value">${avgScore}</div>
                    </div>
                </div>
            `;
        }

        function exportCSV() {
            const testCaseData = groupedData[currentTestCase];
            let csv = 'Phrase_ID,Phrase,Entity,Type,Score,Start,End\\n';

            Object.entries(testCaseData).forEach(([phraseId, phraseData]) => {
                phraseData.entities.forEach(entity => {
                    csv += `${phraseId},"${phraseData.phrase.replace(/"/g, '""')}","${entity.Word.replace(/"/g, '""')}",${entity.Entity_Group},${entity.Score},${entity.Start},${entity.End}\\n`;
                });
            });

            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentTestCase}_entities.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }

        // Initialize on load
        init();
    </script>
</body>
</html>'''

    # Write the HTML file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Dashboard generated: {output_path.absolute()}")
    print(f"Open in browser: file://{output_path.absolute()}")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "output.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "ner_dashboard.html"
    generate_dashboard(input_file, output_file)
