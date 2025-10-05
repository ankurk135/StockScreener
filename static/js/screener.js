let stockData = [];
let dataTable = null;
let activeFilters = {};

function showMessage(text, type = 'success') {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message show ${type}`;
    setTimeout(() => msg.classList.remove('show'), 5000);
}

async function refreshData() {
    const btn = document.getElementById('refreshBtn');
    const loading = document.getElementById('loadingOverlay');
    btn.disabled = true;
    loading.classList.add('show');
    
    try {
        const response = await fetch('/api/refresh', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showMessage(result.message, 'success');
            await loadStocks();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        loading.classList.remove('show');
    }
}

async function loadStocks() {
    try {
        const response = await fetch('/api/stocks');
        const result = await response.json();
        
        if (result.success) {
            stockData = result.data;
            displayStocks(stockData);
            updateStatus(result);
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

function formatNumber(val, dec = 2) {
    if (val == null) return 'N/A';
    if (typeof val === 'string') return val;
    return Number(val).toFixed(dec);
}

function formatPercent(val, dec = 2) {
    if (val == null) return 'N/A';
    const n = Number(val);
    const cls = n >= 0 ? 'positive' : 'negative';
    return `<span class="${cls}">${n.toFixed(dec)}%</span>`;
}

function formatTrendValue(trendVal, priceVal, dec = 2) {
    if (trendVal == null || priceVal == null) return 'N/A';
    if (typeof trendVal === 'string' || typeof priceVal === 'string') return 'N/A';
    
    const trend = Number(trendVal);
    const price = Number(priceVal);
    
    // If trend < price, stock is above indicator (bullish - green)
    // If trend > price, stock is below indicator (bearish - red)
    const cls = trend < price ? 'positive' : 'negative';
    return `<span class="${cls}">${trend.toFixed(dec)}</span>`;
}

function displayStocks(stocks) {
    if (dataTable) {
        dataTable.destroy();
        dataTable = null;
    }
    
    const tbody = $('#stockData');
    if (!stocks || stocks.length === 0) {
        tbody.html('<tr><td colspan="41" style="text-align:center;padding:60px;">No stocks</td></tr>');
        return;
    }
    
    tbody.html(stocks.map(s => `
        <tr>
            <td class="stock-name col-basic">${s.Stock_Name || 'N/A'}</td>
            <td class="col-basic">${s.Sector || 'N/A'}</td>
            <td class="col-basic">${s.Industry || 'N/A'}</td>
            <td class="col-price num">${formatNumber(s.Price)}</td>
            <td class="col-price num">${formatPercent(s.Price_1D_Change_Pct)}</td>
            <td class="col-price num">${formatPercent(s.Price_5D_Change_Pct)}</td>
            <td class="col-price num">${formatPercent(s.Price_11D_Change_Pct)}</td>
            <td class="col-price num">${formatNumber(s.TrailingPE)}</td>
            <td class="col-trend num">${formatTrendValue(s.SuperTrend_1D, s.Price)}</td>
            <td class="col-trend num">${formatTrendValue(s.SuperTrend_1W, s.Price)}</td>
            <td class="col-trend num">${formatTrendValue(s.SMA50_1D, s.Price)}</td>
            <td class="col-trend num">${formatPercent(s.SMA50_1D_AwayFromPrice_Pct)}</td>
            <td class="col-trend num">${formatTrendValue(s.SMA200_1D, s.Price)}</td>
            <td class="col-trend num">${formatPercent(s.SMA200_1D_AwayFromPrice_Pct)}</td>
            <td class="col-trend num">${formatTrendValue(s.SMA200_1W, s.Price)}</td>
            <td class="col-trend">${s.GoldenCross_DeathCross || 'N/A'}</td>
            <td class="col-momentum num">${formatNumber(s.RSI_1D)}</td>
            <td class="col-momentum num">${formatNumber(s.RSI_1W)}</td>
            <td class="col-momentum num">${formatNumber(s.MACD_1D)}</td>
            <td class="col-momentum num">${formatNumber(s.MACD_Signal_1D)}</td>
            <td class="col-momentum">${s.MACD_Crossover_Signal_1D || 'N/A'}</td>
            <td class="col-momentum num">${formatNumber(s.MACD_1W)}</td>
            <td class="col-momentum num">${formatNumber(s.MACD_Signal_1W)}</td>
            <td class="col-momentum">${s.MACD_Crossover_Signal_1W || 'N/A'}</td>
            <td class="col-volume num">${formatPercent(s.VolumeChangePct)}</td>
            <td class="col-volume num">${formatNumber(s.RelVol_1D_over_10D)}</td>
            <td class="col-volume num">${formatNumber(s.RelVol_1D_over_30D)}</td>
            <td class="col-volume num">${formatNumber(s.RelVol_10D_over_30D)}</td>
            <td class="col-volume num">${formatNumber(s.RelVol_10D_over_60D)}</td>
            <td class="col-volume num">${formatNumber(s.RelVol_10D_over_90D)}</td>
            <td class="col-money-flow num">${formatNumber(s.MFI)}</td>
            <td class="col-money-flow num">${formatNumber(s.CMF, 3)}</td>
            <td class="col-money-flow num">${formatNumber(s.BuySellPressureRatio)}</td>
            <td class="col-money-flow num">${formatPercent(s.VPT_11D_Change)}</td>
            <td class="col-strength num">${formatNumber(s.RelStrength_18d)}</td>
            <td class="col-strength num">${formatNumber(s.RelStrength_55D)}</td>
            <td class="col-strength num">${formatNumber(s.RelStrength_81d)}</td>
            <td class="col-price num">${formatNumber(s['52WeekHigh'])}</td>
            <td class="col-price num">${formatNumber(s['52WeekLow'])}</td>
            <td class="col-price num">${formatNumber(s['5YearHigh'])}</td>
            <td class="col-price num">${formatNumber(s['5YearLow'])}</td>
        </tr>
    `).join(''));
    
    setTimeout(() => {
        dataTable = $('#stockTable').DataTable({
            dom: '<"#ignored">rt<"#ignored">',
            paging: true,
            pageLength: 50,
            lengthMenu: [[25, 50, 100, -1], [25, 50, 100, "All"]],
            searching: true,
            ordering: false,
            info: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search stocks...",
                lengthMenu: "Show _MENU_ stocks per page",
                info: "Showing _START_ to _END_ of _TOTAL_ stocks",
                infoFiltered: "(filtered from _MAX_ total)"
            },
            initComplete: function() {
                $('#stockTable_length').appendTo('#tableLength');
                $('#stockTable_filter').appendTo('#tableFilter');
                $('#stockTable_info').appendTo('#tableInfo');
                $('#stockTable_paginate').appendTo('#tablePaginate');
                
                // Attach click handlers to filter icons AFTER table is initialized
                attachFilterIconHandlers();
            }
        });
    }, 100);
}

function showFilter(event, columnIndex) {
    event.stopPropagation();
    
    // Close any open filters
    $('.filter-dropdown').remove();
    
    if (!dataTable) {
        console.error('DataTable not initialized');
        alert('Please wait for data to load');
        return;
    }
    
    const th = $(event.target).closest('th');
    const columnName = th.find('.th-line1').text().trim();
    
    console.log('Opening filter for column:', columnIndex, columnName);
    
    // Get column data
    const columnData = getColumnData(columnIndex);
    
    console.log('Column data:', columnData.length, 'items', columnData.slice(0, 5));
    
    if (columnData.length === 0) {
        console.error('No data for column', columnIndex);
        alert('No data available for this column');
        return;
    }
    
    const uniqueValues = [...new Set(columnData)].sort();
    
    console.log('Unique values:', uniqueValues.length);
    
    // Determine if numeric
    const numericCount = columnData.filter(v => {
        const numVal = parseFloat(v);
        return !isNaN(numVal) && v !== '';
    }).length;
    const isNumeric = numericCount >= columnData.length * 0.5;
    
    console.log('Is numeric:', isNumeric, 'Numeric count:', numericCount, '/', columnData.length);
    
    // Build and show filter
    const dropdown = buildExcelFilter(columnIndex, columnName, uniqueValues, isNumeric);
    th.css('position', 'relative').append(dropdown);
    
    // Setup event listeners
    setTimeout(() => {
        setupFilterEventListeners(columnIndex);
        
        // Close on outside click
        $(document).on('click.filterDropdown', function(e) {
            if (!$(e.target).closest('.filter-dropdown').length && 
                !$(e.target).hasClass('filter-icon')) {
                closeAllFilters();
            }
        });
    }, 50);
}

function buildExcelFilter(columnIndex, columnName, uniqueValues, isNumeric) {
    const currentFilter = activeFilters[columnIndex];
    const selectedValues = currentFilter?.type === 'values' ? currentFilter.values : uniqueValues;
    
    let html = '<div class="filter-dropdown show">';
    
    // Section 1: Sort
    html += '<div class="filter-sort-section">';
    html += `<div class="filter-sort-option sort-asc" data-col="${columnIndex}" data-dir="asc">`;
    html += isNumeric ? 'Sort Smallest to Largest' : 'Sort A to Z';
    html += '</div>';
    html += `<div class="filter-sort-option sort-desc" data-col="${columnIndex}" data-dir="desc">`;
    html += isNumeric ? 'Sort Largest to Smallest' : 'Sort Z to A';
    html += '</div>';
    html += '</div>';
    
    // Section 2: Number Filters (if numeric)
    if (isNumeric) {
        html += '<div class="filter-options-section">';
        html += `<select class="filter-number-type" id="filterType_${columnIndex}">`;
        html += '<option value="">Number Filters</option>';
        html += '<option value="greaterThan">Greater Than</option>';
        html += '<option value="lessThan">Less Than</option>';
        html += '<option value="between">Between</option>';
        html += '<option value="equals">Equals</option>';
        html += '</select>';
        html += `<div class="filter-number-inputs" id="filterInputs_${columnIndex}">`;
        html += `<input type="number" class="filter-number-input" id="filterValue1_${columnIndex}" placeholder="Value (without %)" step="any">`;
        html += `<input type="number" class="filter-number-input" id="filterValue2_${columnIndex}" placeholder="To (without %)" step="any" style="display:none;">`;
        html += '</div>';
        html += '</div>';
        
        // Color Filter Section
        html += '<div class="filter-options-section" style="border-top: 1px solid #d9d9d9;">';
        html += '<div style="padding: 4px 0; font-weight: 600; font-size: 12px; color: #666;">Filter by Color:</div>';
        html += '<div style="display: flex; gap: 8px; padding: 4px 0;">';
        html += `<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; flex: 1;">`;
        html += `<input type="checkbox" id="colorGreen_${columnIndex}" class="filter-value-checkbox" checked>`;
        html += `<span style="color: #28a745; font-weight: 600;">Green (Positive)</span>`;
        html += `</label>`;
        html += `<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; flex: 1;">`;
        html += `<input type="checkbox" id="colorRed_${columnIndex}" class="filter-value-checkbox" checked>`;
        html += `<span style="color: #dc3545; font-weight: 600;">Red (Negative)</span>`;
        html += `</label>`;
        html += '</div>';
        html += '</div>';
    }
    
    // Section 3: Values
    html += '<div class="filter-values-section">';
    html += '<div class="filter-search-box">';
    html += `<input type="text" class="filter-search-input" id="filterSearch_${columnIndex}" placeholder="Search">`;
    html += '</div>';
    
    const allSelected = selectedValues.length === uniqueValues.length;
    html += '<div class="filter-select-all">';
    html += `<input type="checkbox" class="filter-value-checkbox" id="selectAll_${columnIndex}" ${allSelected ? 'checked' : ''}>`;
    html += `<label class="filter-value-label" for="selectAll_${columnIndex}">(Select All)</label>`;
    html += '</div>';
    
    html += `<div class="filter-values-list" id="valuesList_${columnIndex}">`;
    uniqueValues.forEach((value, idx) => {
        const isChecked = selectedValues.includes(value);
        const safeId = `filter_${columnIndex}_${idx}`;
        const safeValue = String(value).replace(/"/g, '&quot;');
        html += `<div class="filter-value-item" data-value="${safeValue}">`;
        html += `<input type="checkbox" class="filter-value-checkbox value-cb" id="${safeId}" value="${safeValue}" ${isChecked ? 'checked' : ''}>`;
        html += `<label class="filter-value-label" for="${safeId}">${value}</label>`;
        html += '</div>';
    });
    html += '</div>';
    html += '</div>';
    
    // Footer
    html += '<div class="filter-footer">';
    html += `<button class="filter-btn" data-action="cancel" data-col="${columnIndex}">Cancel</button>`;
    html += `<button class="filter-btn primary" data-action="apply" data-col="${columnIndex}">OK</button>`;
    html += '</div>';
    
    html += '</div>';
    return html;
}

function setupFilterEventListeners(columnIndex) {
    // Number filter type change
    $(`#filterType_${columnIndex}`).on('change', function() {
        const type = $(this).val();
        const inputsDiv = $(`#filterInputs_${columnIndex}`);
        const value2 = $(`#filterValue2_${columnIndex}`);
        
        if (type && type !== '') {
            inputsDiv.addClass('show');
            value2.toggle(type === 'between');
        } else {
            inputsDiv.removeClass('show');
        }
    });
    
    // Search
    $(`#filterSearch_${columnIndex}`).on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $(`#valuesList_${columnIndex} .filter-value-item`).each(function() {
            const value = $(this).data('value').toString().toLowerCase();
            $(this).toggle(value.includes(searchTerm));
        });
        updateSelectAllState(columnIndex);
    });
    
    // Select All
    $(`#selectAll_${columnIndex}`).on('change', function() {
        const isChecked = $(this).is(':checked');
        $(`#valuesList_${columnIndex} .value-cb:visible`).prop('checked', isChecked);
    });
    
    // Individual checkboxes
    $(`#valuesList_${columnIndex} .value-cb`).on('change', function() {
        updateSelectAllState(columnIndex);
    });
    
    // Click on item row
    $(`#valuesList_${columnIndex} .filter-value-item`).on('click', function(e) {
        if (e.target.type !== 'checkbox' && e.target.tagName !== 'LABEL') {
            const cb = $(this).find('.value-cb');
            cb.prop('checked', !cb.is(':checked')).trigger('change');
        }
    });
    
    // Sort buttons
    $('.filter-sort-option').on('click', function() {
        const col = $(this).data('col');
        const dir = $(this).data('dir');
        sortColumn(col, dir);
    });
    
    // Footer buttons
    $('.filter-btn').on('click', function() {
        const action = $(this).data('action');
        const col = $(this).data('col');
        if (action === 'apply') {
            applyFilter(col);
        } else {
            closeAllFilters();
        }
    });
}

function updateSelectAllState(columnIndex) {
    const total = $(`#valuesList_${columnIndex} .value-cb:visible`).length;
    const checked = $(`#valuesList_${columnIndex} .value-cb:visible:checked`).length;
    $(`#selectAll_${columnIndex}`).prop('checked', total === checked && total > 0);
}

function sortColumn(columnIndex, direction) {
    if (!dataTable) return;
    
    const settings = dataTable.settings()[0];
    settings.aoColumns[columnIndex].bSortable = true;
    settings.oFeatures.bSort = true;
    
    dataTable.order([columnIndex, direction]).draw();
    
    settings.oFeatures.bSort = false;
    settings.aoColumns[columnIndex].bSortable = false;
    
    closeAllFilters();
}

function applyFilter(columnIndex) {
    const filterType = $(`#filterType_${columnIndex}`).val();
    
    // Check color filters for numeric columns
    const greenCheckbox = $(`#colorGreen_${columnIndex}`);
    const redCheckbox = $(`#colorRed_${columnIndex}`);
    const hasColorFilter = greenCheckbox.length > 0;
    const greenChecked = hasColorFilter ? greenCheckbox.is(':checked') : true;
    const redChecked = hasColorFilter ? redCheckbox.is(':checked') : true;
    
    // Determine if any filter is active
    const hasNumericFilter = filterType && filterType !== '';
    const hasColorChange = hasColorFilter && (!greenChecked || !redChecked);
    
    // Value filter checkboxes
    const selectedValues = [];
    $(`#valuesList_${columnIndex} .value-cb:checked`).each(function() {
        selectedValues.push($(this).val());
    });
    
    const allValues = [];
    $(`#valuesList_${columnIndex} .value-cb`).each(function() {
        allValues.push($(this).val());
    });
    
    const hasValueFilter = selectedValues.length < allValues.length && selectedValues.length > 0;
    
    // Priority 1: Numeric filter with optional color
    if (hasNumericFilter) {
        const value1 = parseFloat($(`#filterValue1_${columnIndex}`).val());
        if (isNaN(value1)) {
            alert('Please enter a valid number');
            return;
        }
        
        let value2 = null;
        if (filterType === 'between') {
            value2 = parseFloat($(`#filterValue2_${columnIndex}`).val());
            if (isNaN(value2)) {
                alert('Please enter a valid "To" value');
                return;
            }
        }
        
        activeFilters[columnIndex] = {
            type: 'numeric',
            filterType: filterType,
            value1: value1,
            value2: value2,
            colorGreen: greenChecked,
            colorRed: redChecked,
            columnName: $(`.filter-icon[data-col="${columnIndex}"]`).closest('th').find('.th-line1').text().trim()
        };
    }
    // Priority 2: Color-only filter
    else if (hasColorChange) {
        activeFilters[columnIndex] = {
            type: 'color',
            colorGreen: greenChecked,
            colorRed: redChecked,
            columnName: $(`.filter-icon[data-col="${columnIndex}"]`).closest('th').find('.th-line1').text().trim()
        };
    }
    // Priority 3: Value filter
    else if (hasValueFilter) {
        activeFilters[columnIndex] = {
            type: 'values',
            values: selectedValues,
            columnName: $(`.filter-icon[data-col="${columnIndex}"]`).closest('th').find('.th-line1').text().trim()
        };
    }
    // No filter applied
    else {
        delete activeFilters[columnIndex];
    }
    
    rebuildFilters();
    closeAllFilters();
}

function closeAllFilters() {
    $('.filter-dropdown').remove();
    $(document).off('click.filterDropdown');
}

function attachFilterIconHandlers() {
    $('.filter-icon').off('click').on('click', function(e) {
        e.stopPropagation();
        const colIndex = parseInt($(this).data('col'));
        console.log('Filter clicked for column:', colIndex);
        showFilter(e, colIndex);
    });
}

function getColumnData(columnIndex) {
    const data = [];
    if (!dataTable) {
        console.error('DataTable not initialized in getColumnData');
        return data;
    }
    
    try {
        dataTable.column(columnIndex, { search: 'applied' }).data().each(function(value) {
            // Extract text from HTML or use plain value
            const tempDiv = $('<div>').html(value);
            let cleanValue = tempDiv.text().trim() || String(value).trim();
            
            // Remove % sign for percentage columns
            cleanValue = cleanValue.replace('%', '').trim();
            
            // Include ALL values, even N/A - user can filter them out if needed
            if (cleanValue !== '' && cleanValue !== 'N/A') {
                data.push(cleanValue);
            }
        });
    } catch(e) {
        console.error('Error getting column data:', e);
    }
    
    console.log('Extracted', data.length, 'values from column', columnIndex);
    return data;
}

function rebuildFilters() {
    $.fn.dataTable.ext.search = [];
    
    // Columns with trend-based coloring (compare with price in column 3)
    const trendColumns = [8, 9, 10, 12, 14]; // SuperTrend_1D, SuperTrend_1W, SMA50_1D, SMA200_1D, SMA200_1W
    
    Object.entries(activeFilters).forEach(([colIdx, filter]) => {
        if (filter.type === 'numeric') {
            $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
                const rawValue = data[colIdx];
                const tempDiv = $('<div>').html(rawValue);
                const textValue = tempDiv.text().trim();
                
                // Remove % sign and parse as float
                const cellValue = parseFloat(textValue.replace('%', '').trim());
                
                if (isNaN(cellValue)) return false;
                
                // Check numeric condition
                let numericMatch = true;
                if (filter.filterType) {
                    switch(filter.filterType) {
                        case 'equals': numericMatch = Math.abs(cellValue - filter.value1) < 0.001; break;
                        case 'greaterThan': numericMatch = cellValue > filter.value1; break;
                        case 'lessThan': numericMatch = cellValue < filter.value1; break;
                        case 'between': numericMatch = cellValue >= filter.value1 && cellValue <= filter.value2; break;
                    }
                }
                
                // Check color condition
                let colorMatch = true;
                if (filter.colorGreen !== undefined && filter.colorRed !== undefined) {
                    const isTrendColumn = trendColumns.includes(parseInt(colIdx));
                    
                    if (isTrendColumn) {
                        // For trend columns, determine color by comparing with price
                        const priceValue = parseFloat($(data[3]).text().trim());
                        if (!isNaN(priceValue)) {
                            const isGreen = cellValue < priceValue; // Indicator below price = green
                            if (isGreen && !filter.colorGreen) colorMatch = false;
                            if (!isGreen && !filter.colorRed) colorMatch = false;
                        }
                    } else {
                        // For regular columns, use value sign
                        if (cellValue >= 0 && !filter.colorGreen) colorMatch = false;
                        if (cellValue < 0 && !filter.colorRed) colorMatch = false;
                    }
                }
                
                return numericMatch && colorMatch;
            });
        } else if (filter.type === 'color') {
            $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
                const rawValue = data[colIdx];
                const tempDiv = $('<div>').html(rawValue);
                const textValue = tempDiv.text().trim();
                
                const cellValue = parseFloat(textValue.replace('%', '').trim());
                
                if (isNaN(cellValue)) return false;
                
                const isTrendColumn = trendColumns.includes(parseInt(colIdx));
                
                if (isTrendColumn) {
                    // For trend columns, determine color by comparing with price
                    const priceValue = parseFloat($(data[3]).text().trim());
                    if (!isNaN(priceValue)) {
                        const isGreen = cellValue < priceValue;
                        if (isGreen && !filter.colorGreen) return false;
                        if (!isGreen && !filter.colorRed) return false;
                    }
                } else {
                    // For regular columns, use value sign
                    if (cellValue >= 0 && !filter.colorGreen) return false;
                    if (cellValue < 0 && !filter.colorRed) return false;
                }
                
                return true;
            });
        } else if (filter.type === 'values') {
            $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
                const rawValue = data[colIdx];
                const tempDiv = $('<div>').html(rawValue);
                let cellValue = tempDiv.text().trim();
                
                // Remove % sign for comparison
                cellValue = cellValue.replace('%', '').trim();
                
                return filter.values.includes(cellValue);
            });
        }
    });
    
    if (dataTable) dataTable.draw();
    updateActiveFiltersDisplay();
}

function updateActiveFiltersDisplay() {
    const filterCount = Object.keys(activeFilters).length;
    $('#filterCount').text(filterCount);
    
    // Update filter icon states
    $('.filter-icon').removeClass('active');
    Object.keys(activeFilters).forEach(colIdx => {
        $(`.filter-icon[data-col="${colIdx}"]`).addClass('active');
    });
    
    if (filterCount > 0) {
        $('#filtersBar').addClass('show');
        const filterChips = $('#filterChips');
        filterChips.empty();
        
        Object.entries(activeFilters).forEach(([colIdx, filter]) => {
            let filterText = '';
            
            if (filter.type === 'numeric') {
                const operators = {
                    equals: '=',
                    greaterThan: '>',
                    lessThan: '<',
                    between: 'between'
                };
                const op = operators[filter.filterType];
                filterText = filter.filterType === 'between' 
                    ? `${filter.value1} - ${filter.value2}`
                    : `${op} ${filter.value1}`;
                
                // Add color info if applicable
                if (filter.colorGreen !== undefined && (!filter.colorGreen || !filter.colorRed)) {
                    const colors = [];
                    if (filter.colorGreen) colors.push('Green');
                    if (filter.colorRed) colors.push('Red');
                    filterText += ` (${colors.join(', ')})`;
                }
            } else if (filter.type === 'color') {
                const colors = [];
                if (filter.colorGreen) colors.push('Green');
                if (filter.colorRed) colors.push('Red');
                filterText = `Color: ${colors.join(', ')}`;
            } else {
                filterText = filter.values.length === 1 
                    ? filter.values[0]
                    : `${filter.values.length} items`;
            }
            
            filterChips.append(`
                <div class="filter-chip">
                    <strong>${filter.columnName}:</strong> ${filterText}
                    <span class="filter-chip-close" onclick="removeFilter(${colIdx})">✕</span>
                </div>
            `);
        });
    } else {
        $('#filtersBar').removeClass('show');
    }
}

function removeFilter(columnIndex) {
    delete activeFilters[columnIndex];
    rebuildFilters();
}

function clearAllFilters() {
    activeFilters = {};
    rebuildFilters();
}

function updateStatus(result) {
    const timestamp = result.timestamp || new Date().toLocaleString('en-IN', {
        dateStyle: 'short',
        timeStyle: 'short'
    });
    document.getElementById('statusText').textContent = `${result.data.length} stocks | Last updated: ${timestamp}`;
}

function toggleColumnGroup(group) {
    const checkbox = document.getElementById(`toggle-${group}`);
    const cols = [];
    document.querySelectorAll('th').forEach((th, i) => {
        if (th.classList.contains(`col-${group}`)) cols.push(i);
    });
    if (dataTable) {
        cols.forEach(i => dataTable.column(i).visible(checkbox.checked));
    }
}

function toggleColumnsMenu() {
    const menu = document.getElementById('columnsMenu');
    menu.classList.toggle('show');
    
    setTimeout(() => {
        $(document).on('click.colmenu', (e) => {
            if (!$(e.target).closest('.columns-dropdown').length) {
                menu.classList.remove('show');
                $(document).off('click.colmenu');
            }
        });
    }, 100);
}

window.addEventListener('DOMContentLoaded', loadStocks);