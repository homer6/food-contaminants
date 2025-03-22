// Global variables
let allData = [];
let filteredData = [];

// DOM elements
const contaminantFilter = document.getElementById('contaminant-filter');
const commodityFilter = document.getElementById('commodity-filter');
const levelTypeFilter = document.getElementById('level-type-filter');
const searchInput = document.getElementById('search-input');
const dataTable = document.getElementById('data-tbody');
const chartContainer = document.getElementById('chart-container');

// Load and process data
async function loadData() {
    try {
        const response = await fetch('data/contaminant-levels.csv');
        const csvText = await response.text();
        
        // Parse CSV
        const rows = csvText.split('\n');
        const headers = rows[0].split(',').map(h => h.trim());
        
        allData = rows.slice(1).filter(row => row.trim() !== '').map(row => {
            const values = row.split(',').map(v => v.trim());
            const rowData = {};
            headers.forEach((header, index) => {
                rowData[header] = values[index] || '';
            });
            return rowData;
        });
        
        // Initialize filters and data display
        initializeFilters();
        filteredData = [...allData];
        renderTable();
        renderVisualization();
        
    } catch (error) {
        console.error('Error loading data:', error);
        dataTable.innerHTML = `<tr><td colspan="6">Error loading data. Please try again later.</td></tr>`;
    }
}

// Initialize filter dropdowns
function initializeFilters() {
    const contaminants = new Set();
    const commodities = new Set();
    const levelTypes = new Set();
    
    allData.forEach(item => {
        contaminants.add(item.Contaminant);
        commodities.add(item.Commodity);
        levelTypes.add(item['Contaminant Level Type']);
    });
    
    populateFilter(contaminantFilter, contaminants);
    populateFilter(commodityFilter, commodities);
    populateFilter(levelTypeFilter, levelTypes);
    
    // Add event listeners for filters
    contaminantFilter.addEventListener('change', applyFilters);
    commodityFilter.addEventListener('change', applyFilters);
    levelTypeFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters);
}

// Populate a filter dropdown with options
function populateFilter(selectElement, optionsSet) {
    const options = Array.from(optionsSet).sort();
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}

// Apply all filters and update data display
function applyFilters() {
    const contaminantValue = contaminantFilter.value;
    const commodityValue = commodityFilter.value;
    const levelTypeValue = levelTypeFilter.value;
    const searchValue = searchInput.value.toLowerCase();
    
    filteredData = allData.filter(item => {
        // Apply dropdown filters
        if (contaminantValue && item.Contaminant !== contaminantValue) return false;
        if (commodityValue && item.Commodity !== commodityValue) return false;
        if (levelTypeValue && item['Contaminant Level Type'] !== levelTypeValue) return false;
        
        // Apply search filter
        if (searchValue) {
            const matchesSearch = Object.values(item).some(
                value => value.toLowerCase().includes(searchValue)
            );
            if (!matchesSearch) return false;
        }
        
        return true;
    });
    
    renderTable();
    renderVisualization();
}

// Render data table
function renderTable() {
    if (filteredData.length === 0) {
        dataTable.innerHTML = `<tr><td colspan="6">No data found matching your filters</td></tr>`;
        return;
    }
    
    dataTable.innerHTML = filteredData.map(item => `
        <tr>
            <td>${item.Contaminant}</td>
            <td>${item.Commodity}</td>
            <td>${item['Contaminant Level Type']}</td>
            <td>${item.Level}</td>
            <td>${item.Reference}</td>
            <td><a href="${item['Link to Reference']}" target="_blank">View Source</a></td>
        </tr>
    `).join('');
}

// Render data visualization
function renderVisualization() {
    // Clear previous chart
    chartContainer.innerHTML = '';
    
    if (filteredData.length === 0) {
        chartContainer.innerHTML = '<div class="no-data">No data available for visualization</div>';
        return;
    }
    
    // Group by contaminant (simplified example)
    const contaminantCounts = {};
    filteredData.forEach(item => {
        const contaminant = item.Contaminant;
        contaminantCounts[contaminant] = (contaminantCounts[contaminant] || 0) + 1;
    });
    
    const chartData = Object.entries(contaminantCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value);
    
    // Simple D3 bar chart
    const margin = { top: 20, right: 20, bottom: 100, left: 50 };
    const width = chartContainer.clientWidth - margin.left - margin.right;
    const height = chartContainer.clientHeight - margin.top - margin.bottom;
    
    const svg = d3.select('#chart-container')
        .append('svg')
            .attr('width', chartContainer.clientWidth)
            .attr('height', chartContainer.clientHeight)
        .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // X and Y scales
    const x = d3.scaleBand()
        .domain(chartData.map(d => d.name))
        .range([0, width])
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(chartData, d => d.value)])
        .nice()
        .range([height, 0]);
    
    // X-axis
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end')
            .attr('dx', '-.8em')
            .attr('dy', '.15em');
    
    // Y-axis
    svg.append('g')
        .call(d3.axisLeft(y));
    
    // Bars
    svg.selectAll('rect')
        .data(chartData)
        .enter()
        .append('rect')
            .attr('x', d => x(d.name))
            .attr('y', d => y(d.value))
            .attr('width', x.bandwidth())
            .attr('height', d => height - y(d.value))
            .attr('fill', '#3498db');
}

// Initialize the application
window.addEventListener('load', loadData);