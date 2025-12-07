// Dashboard JavaScript

// API Base URL
const API_BASE = '/api';

// State
let graphData = null;
let recommendationsData = null;
let sectionsData = null;
let productsData = null;

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    
    // Setup tab switching
    setupTabs();
    
    // Setup layout toggle
    setupLayoutToggle();
    
    // Setup search
    setupSearch();
    
    // Load data
    loadAllData();
});

// Tab Switching
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update panes
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// Layout Toggle
function setupLayoutToggle() {
    const layoutBtns = document.querySelectorAll('.layout-btn');
    
    layoutBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const layout = btn.dataset.layout;
            
            // Update buttons
            layoutBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update plot
            if (sectionsData && productsData && recommendationsData) {
                plotLayoutHeatmap(layout);
            }
        });
    });
}

// Search
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        filterRecommendations(query);
    });
}

// Load All Data
async function loadAllData() {
    try {
        // Load stats
        await loadStats();
        
        // Load graph data
        await loadGraph();
        
        // Load sections
        await loadSections();
        
        // Load products
        await loadProducts();
        
        // Load recommendations
        await loadRecommendations();
        
        console.log('All data loaded successfully');
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Load Stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const result = await response.json();
        
        if (result.success) {
            const stats = result.data;
            document.getElementById('statSections').textContent = stats.sections;
            document.getElementById('statProducts').textContent = stats.products;
            document.getElementById('statCommunities').textContent = stats.communities;
            document.getElementById('statRecommendations').textContent = stats.recommendations;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load Graph
async function loadGraph() {
    try {
        const response = await fetch(`${API_BASE}/graph`);
        const result = await response.json();
        
        if (result.success) {
            graphData = result.data;
            plotGraph();
        }
    } catch (error) {
        console.error('Error loading graph:', error);
    }
}

// Load Sections
async function loadSections() {
    try {
        const response = await fetch(`${API_BASE}/sections`);
        const result = await response.json();
        
        if (result.success) {
            sectionsData = result.data;
        }
    } catch (error) {
        console.error('Error loading sections:', error);
    }
}

// Load Products
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`);
        const result = await response.json();
        
        if (result.success) {
            productsData = result.data;
            plotLayoutHeatmap('current');
        }
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load Recommendations
async function loadRecommendations() {
    try {
        const response = await fetch(`${API_BASE}/recommendations`);
        const result = await response.json();
        
        if (result.success) {
            recommendationsData = result.data;
            displayRecommendations(result.data);
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Plot Graph
function plotGraph() {
    if (!graphData) return;
    
    const nodes = graphData.nodes;
    const edges = graphData.edges;
    
    // Create node positions (use x, y coordinates)
    const nodeX = nodes.map(n => n.x);
    const nodeY = nodes.map(n => n.y);
    const nodeText = nodes.map(n => `${n.section_id}: ${n.name}<br>Community: ${n.community_id || 'N/A'}`);
    const nodeColors = nodes.map(n => n.community_id || 0);
    
    // Create edge traces
    const edgeTraces = [];
    edges.forEach(edge => {
        const srcNode = nodes.find(n => n.section_id === edge.source);
        const dstNode = nodes.find(n => n.section_id === edge.target);
        
        if (srcNode && dstNode) {
            edgeTraces.push({
                x: [srcNode.x, dstNode.x],
                y: [srcNode.y, dstNode.y],
                mode: 'lines',
                line: {
                    width: Math.log(edge.weight + 1) * 0.5,
                    color: 'rgba(150, 150, 150, 0.3)'
                },
                hoverinfo: 'none',
                showlegend: false
            });
        }
    });
    
    // Create node trace
    const nodeTrace = {
        x: nodeX,
        y: nodeY,
        mode: 'markers+text',
        text: nodes.map(n => n.section_id),
        textposition: 'middle center',
        textfont: {
            size: 10,
            color: 'white'
        },
        marker: {
            size: 30,
            color: nodeColors,
            colorscale: 'Viridis',
            line: {
                width: 2,
                color: 'white'
            }
        },
        hovertext: nodeText,
        hoverinfo: 'text',
        showlegend: false
    };
    
    const layout = {
        title: 'Store Section Movement Network',
        showlegend: false,
        hovermode: 'closest',
        xaxis: {
            title: 'X Coordinate',
            showgrid: true,
            zeroline: false
        },
        yaxis: {
            title: 'Y Coordinate',
            showgrid: true,
            zeroline: false
        },
        plot_bgcolor: '#f9fafb',
        paper_bgcolor: 'white'
    };
    
    Plotly.newPlot('graphPlot', [...edgeTraces, nodeTrace], layout, {responsive: true});
}

// Plot Layout Heatmap
function plotLayoutHeatmap(layoutType) {
    if (!sectionsData || !productsData) return;
    
    // Count products per section
    const sectionCounts = {};
    sectionsData.forEach(section => {
        sectionCounts[section.section_id] = 0;
    });
    
    if (layoutType === 'current') {
        // Current layout
        productsData.forEach(product => {
            if (product.current_section_id && product.current_section_id in sectionCounts) {
                sectionCounts[product.current_section_id]++;
            }
        });
    } else {
        // Recommended layout
        if (!recommendationsData) return;
        
        recommendationsData.forEach(rec => {
            if (rec.recommended_section_id && rec.recommended_section_id in sectionCounts) {
                sectionCounts[rec.recommended_section_id]++;
            }
        });
    }
    
    // Create heatmap data
    const z = [];
    const xLabels = [];
    const yLabels = [];
    
    // Get unique x and y coordinates
    const uniqueX = [...new Set(sectionsData.map(s => s.x))].sort((a, b) => a - b);
    const uniqueY = [...new Set(sectionsData.map(s => s.y))].sort((a, b) => a - b);
    
    // Create grid
    uniqueY.forEach(y => {
        const row = [];
        uniqueX.forEach(x => {
            const section = sectionsData.find(s => s.x === x && s.y === y);
            row.push(section ? sectionCounts[section.section_id] : null);
        });
        z.push(row);
    });
    
    const data = [{
        z: z,
        x: uniqueX,
        y: uniqueY,
        type: 'heatmap',
        colorscale: 'Blues',
        hovertemplate: 'X: %{x}<br>Y: %{y}<br>Products: %{z}<extra></extra>'
    }];
    
    const layout = {
        title: `${layoutType === 'current' ? 'Current' : 'Recommended'} Product Density`,
        xaxis: {
            title: 'X Coordinate'
        },
        yaxis: {
            title: 'Y Coordinate'
        },
        plot_bgcolor: '#f9fafb',
        paper_bgcolor: 'white'
    };
    
    Plotly.newPlot('layoutPlot', data, layout, {responsive: true});
}

// Display Recommendations
function displayRecommendations(recommendations) {
    const tbody = document.getElementById('recommendationsBody');
    tbody.innerHTML = '';
    
    if (recommendations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No recommendations found</td></tr>';
        return;
    }
    
    recommendations.forEach(rec => {
        const row = document.createElement('tr');
        
        const scoreClass = rec.score > 0 ? 'score-high' : rec.score > -50 ? 'score-medium' : 'score-low';
        
        row.innerHTML = `
            <td>${rec.product_id}</td>
            <td><strong>${rec.product_name || 'N/A'}</strong></td>
            <td>${rec.section_name || rec.recommended_section_id}</td>
            <td><span class="score-badge ${scoreClass}">${rec.score.toFixed(2)}</span></td>
            <td class="rationale">${rec.rationale}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Filter Recommendations
function filterRecommendations(query) {
    if (!recommendationsData) return;
    
    if (!query) {
        displayRecommendations(recommendationsData);
        return;
    }
    
    const filtered = recommendationsData.filter(rec => 
        (rec.product_name && rec.product_name.toLowerCase().includes(query)) ||
        (rec.section_name && rec.section_name.toLowerCase().includes(query)) ||
        (rec.rationale && rec.rationale.toLowerCase().includes(query))
    );
    
    displayRecommendations(filtered);
}