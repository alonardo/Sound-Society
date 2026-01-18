/**
 * Sound & Society - Music Sociology Dashboard
 * Main Application JavaScript
 */

// ============================================
// Global State
// ============================================
let dashboardData = null;
let eventsData = null;
let currentFilters = {
    genre: '',
    decade: '',
    year: ''
};
let selectedEvents = new Set();  // Track selected event indices
let activeCategories = new Set();  // Track active category filters

// Chart instances
let wordFreqChart = null;
let genreSentimentChart = null;
let genreDiversityChart = null;
let trendsChart = null;

// Genre colors
const GENRE_COLORS = {
    rock: '#ef4444',
    pop: '#f97316',
    rnb: '#a855f7',
    hiphop: '#22c55e',
    country: '#eab308',
    dance: '#22d3ee',
    other: '#6b7280'
};

// Chart.js default config
Chart.defaults.color = '#9898a6';
Chart.defaults.borderColor = '#2a2a36';
Chart.defaults.font.family = "'Space Grotesk', sans-serif";

// ============================================
// Data Loading
// ============================================
async function loadData() {
    try {
        const [dataResponse, eventsResponse] = await Promise.all([
            fetch('../data/processed/data.json'),
            fetch('../data/processed/events.json')
        ]);

        if (!dataResponse.ok) throw new Error('Failed to load data.json');

        dashboardData = await dataResponse.json();

        if (eventsResponse.ok) {
            eventsData = await eventsResponse.json();
        }

        initializeDashboard();
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load dashboard data. Please run the pipeline first.');
    }
}

function showError(message) {
    document.querySelector('.main').innerHTML = `
        <div style="text-align: center; padding: 4rem; color: var(--text-muted);">
            <h2 style="color: var(--accent-primary); margin-bottom: 1rem;">Data Not Found</h2>
            <p>${message}</p>
            <p style="margin-top: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.875rem;">
                Run: python run_pipeline.py
            </p>
        </div>
    `;
}

// ============================================
// Dashboard Initialization
// ============================================
function initializeDashboard() {
    updateHomeStats();
    populateFilters();
    initNavigation();
    initExploreSection();
    initTrendsSection();
    initSummarySection();
}

function updateHomeStats() {
    const meta = dashboardData.metadata;
    const songs = dashboardData.songs;

    // Hero song count
    document.getElementById('hero-song-count').textContent = meta.total_songs.toLocaleString();

    // Stats bar
    document.getElementById('stat-songs').textContent = meta.total_songs.toLocaleString();
    document.getElementById('stat-years').textContent =
        `${meta.years_covered[1] - meta.years_covered[0] + 1}`;
    document.getElementById('stat-genres').textContent = meta.genres.length;

    // Calculate total words processed
    const totalWords = songs.reduce((sum, s) => sum + (s.word_count || 0), 0);
    document.getElementById('stat-words').textContent =
        (totalWords / 1000000).toFixed(1) + 'M';
}

function populateFilters() {
    const genres = dashboardData.metadata.genres || [];
    const decades = Object.keys(dashboardData.aggregations.by_decade).sort();
    const years = Object.keys(dashboardData.aggregations.by_year).sort((a, b) => b - a);

    // Explore filters
    const genreFilter = document.getElementById('genre-filter');
    const decadeFilter = document.getElementById('decade-filter');
    const yearFilter = document.getElementById('year-filter');

    genres.forEach(g => {
        const label = dashboardData.aggregations.by_genre[g]?.label || g;
        genreFilter.innerHTML += `<option value="${g}">${label}</option>`;
    });

    decades.forEach(d => {
        decadeFilter.innerHTML += `<option value="${d}">${d}</option>`;
    });

    years.forEach(y => {
        yearFilter.innerHTML += `<option value="${y}">${y}</option>`;
    });
}

// ============================================
// Navigation
// ============================================
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(b => b.classList.remove('active'));

    const activeBtn = document.querySelector(`.nav-btn[data-section="${sectionId}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

// ============================================
// Explore Section
// ============================================
function initExploreSection() {
    // Filter event listeners
    document.getElementById('genre-filter').addEventListener('change', updateExplore);
    document.getElementById('decade-filter').addEventListener('change', updateExplore);
    document.getElementById('year-filter').addEventListener('change', updateExplore);

    // Initial render
    renderGenreStats();
    initWordFreqChart();
    renderTfidfKeywords();
    initGenreComparisonCharts();
    updateExplore();
}

function renderTfidfKeywords() {
    const container = document.getElementById('tfidf-keywords');
    const tfidfData = dashboardData.tfidf?.by_genre;

    if (!tfidfData) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">TF-IDF data not available. Re-run the pipeline.</p>';
        return;
    }

    const byGenre = dashboardData.aggregations.by_genre;

    // Sort genres by song count
    const sortedGenres = Object.entries(tfidfData)
        .sort((a, b) => (byGenre[b[0]]?.count || 0) - (byGenre[a[0]]?.count || 0));

    container.innerHTML = sortedGenres.map(([genre, words]) => {
        const genreLabel = byGenre[genre]?.label || genre;
        const topWords = words.slice(0, 12);

        return `
            <div class="tfidf-genre" data-genre="${genre}">
                <div class="tfidf-genre-header">
                    <span class="tfidf-genre-name">${genreLabel}</span>
                </div>
                <div class="tfidf-words">
                    ${topWords.map(w => `<span class="tfidf-word">${w.word}</span>`).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function renderGenreStats() {
    const byGenre = dashboardData.aggregations.by_genre;
    const container = document.getElementById('genre-stats-row');

    const genreCards = Object.entries(byGenre)
        .sort((a, b) => b[1].count - a[1].count)
        .map(([code, data]) => `
            <div class="genre-stat-card" data-genre="${code}" onclick="filterByGenre('${code}')">
                <div class="genre-name">${data.label}</div>
                <div class="genre-count">${data.count.toLocaleString()}</div>
                <div class="genre-label">songs</div>
            </div>
        `).join('');

    container.innerHTML = genreCards;
}

function filterByGenre(genreCode) {
    document.getElementById('genre-filter').value = genreCode;

    // Update active state on cards
    document.querySelectorAll('.genre-stat-card').forEach(card => {
        card.classList.toggle('active', card.dataset.genre === genreCode);
    });

    updateExplore();
}

function updateExplore() {
    const genre = document.getElementById('genre-filter').value;
    const decade = document.getElementById('decade-filter').value;
    const year = document.getElementById('year-filter').value;

    currentFilters = { genre, decade, year };

    // Update active genre card
    document.querySelectorAll('.genre-stat-card').forEach(card => {
        card.classList.toggle('active', card.dataset.genre === genre);
    });

    updateWordFreqChart();
    updateWordFreqTitle();
    updateTfidfDisplay();
}

function updateTfidfDisplay() {
    const { genre, decade } = currentFilters;
    const container = document.getElementById('tfidf-keywords');
    const titleEl = document.getElementById('tfidf-title');

    // Check if we have decade-specific TF-IDF data
    const tfidfByDecade = dashboardData.tfidf?.by_genre_decade;
    const tfidfByGenre = dashboardData.tfidf?.by_genre;

    if (!tfidfByGenre) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">TF-IDF data not available.</p>';
        return;
    }

    const byGenre = dashboardData.aggregations.by_genre;
    let tfidfData;
    let titleSuffix = '';

    // If decade is selected and we have decade-specific data, use it
    if (decade && tfidfByDecade) {
        // Filter to show only data for the selected decade
        tfidfData = {};
        Object.keys(tfidfByGenre).forEach(g => {
            const key = `${g}_${decade}`;
            if (tfidfByDecade[key]) {
                tfidfData[g] = tfidfByDecade[key];
            }
        });
        titleSuffix = ` (${decade})`;

        // If no decade-specific data, fall back to overall
        if (Object.keys(tfidfData).length === 0) {
            tfidfData = tfidfByGenre;
            titleSuffix = '';
        }
    } else {
        tfidfData = tfidfByGenre;
    }

    // Update title
    titleEl.textContent = `Distinctive Keywords by Genre${titleSuffix}`;

    // Filter by selected genre if one is selected
    let genresToShow = Object.entries(tfidfData);
    if (genre) {
        genresToShow = genresToShow.filter(([g]) => g === genre);
    }

    // Sort by song count
    genresToShow.sort((a, b) => (byGenre[b[0]]?.count || 0) - (byGenre[a[0]]?.count || 0));

    if (genresToShow.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 1rem;">No TF-IDF data for this selection.</p>';
        return;
    }

    container.innerHTML = genresToShow.map(([g, words]) => {
        const genreLabel = byGenre[g]?.label || g;
        const topWords = words.slice(0, 12);

        return `
            <div class="tfidf-genre" data-genre="${g}">
                <div class="tfidf-genre-header">
                    <span class="tfidf-genre-name">${genreLabel}</span>
                </div>
                <div class="tfidf-words">
                    ${topWords.map(w => `<span class="tfidf-word">${w.word}</span>`).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function updateWordFreqTitle() {
    const { genre, decade, year } = currentFilters;
    const titleEl = document.getElementById('word-freq-title');
    const subtitleEl = document.getElementById('word-freq-subtitle');

    let title = 'Top Words in ';
    let parts = [];

    if (genre) {
        const label = dashboardData.aggregations.by_genre[genre]?.label || genre;
        parts.push(label);
    } else {
        parts.push('All');
    }

    if (year) {
        parts.push(year);
    } else if (decade) {
        parts.push(decade);
    }

    title += parts.join(' ') + ' Songs';
    titleEl.textContent = title;
    subtitleEl.textContent = 'Most frequently used words (excluding common stopwords)';
}

function initWordFreqChart() {
    const ctx = document.getElementById('wordFreqChart').getContext('2d');

    wordFreqChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Word Count',
                data: [],
                backgroundColor: '#f97316',
                borderColor: '#f97316',
                borderWidth: 0,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    borderColor: '#2a2a36',
                    borderWidth: 1,
                    callbacks: {
                        label: ctx => `Count: ${ctx.raw.toLocaleString()}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: '#1f1f28' },
                    ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { family: "'Space Grotesk', sans-serif", size: 11 } }
                }
            }
        }
    });

    updateWordFreqChart();
}

function updateWordFreqChart() {
    const { genre, decade } = currentFilters;

    let wordData = [];

    // Priority: genre+decade combo > genre only > decade only > all
    if (genre && decade) {
        const key = `${genre}_${decade}`;
        wordData = dashboardData.word_frequencies?.by_genre_decade?.[key] || [];
    } else if (genre) {
        wordData = dashboardData.word_frequencies?.by_genre?.[genre] || [];
    } else if (decade) {
        wordData = dashboardData.word_frequencies?.by_decade?.[decade] || [];
    } else {
        // Aggregate all genres
        const allByGenre = dashboardData.word_frequencies?.by_genre || {};
        const wordCounts = {};
        Object.values(allByGenre).forEach(words => {
            words.forEach(w => {
                wordCounts[w.word] = (wordCounts[w.word] || 0) + w.count;
            });
        });
        wordData = Object.entries(wordCounts)
            .map(([word, count]) => ({ word, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 30);
    }

    const labels = wordData.slice(0, 20).map(w => w.word);
    const data = wordData.slice(0, 20).map(w => w.count);

    // Color based on genre
    const color = genre ? (GENRE_COLORS[genre] || '#f97316') : '#f97316';

    wordFreqChart.data.labels = labels;
    wordFreqChart.data.datasets[0].data = data;
    wordFreqChart.data.datasets[0].backgroundColor = color;
    wordFreqChart.data.datasets[0].borderColor = color;
    wordFreqChart.update();
}

function initGenreComparisonCharts() {
    const byGenre = dashboardData.aggregations.by_genre;
    const genres = Object.entries(byGenre).sort((a, b) => b[1].count - a[1].count);

    // Calculate dynamic bounds for sentiment
    const sentimentValues = genres.map(([code, data]) => data.avg_sentiment).filter(v => v != null);
    const sentMin = Math.min(...sentimentValues);
    const sentMax = Math.max(...sentimentValues);
    const sentPadding = (sentMax - sentMin) * 0.2;

    // Sentiment by Genre
    const sentimentCtx = document.getElementById('genreSentimentChart').getContext('2d');
    genreSentimentChart = new Chart(sentimentCtx, {
        type: 'bar',
        data: {
            labels: genres.map(([code, data]) => data.label),
            datasets: [{
                label: 'Avg Sentiment',
                data: genres.map(([code, data]) => data.avg_sentiment),
                backgroundColor: genres.map(([code]) => GENRE_COLORS[code] || '#6b7280'),
                borderWidth: 0,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    borderColor: '#2a2a36',
                    borderWidth: 1,
                    callbacks: {
                        label: ctx => `Sentiment: ${ctx.raw?.toFixed(3) ?? 'N/A'}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 }, maxRotation: 45 }
                },
                y: {
                    min: Math.min(0, sentMin - sentPadding),
                    max: sentMax + sentPadding,
                    grid: { color: '#1f1f28' },
                    ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } }
                }
            }
        }
    });

    // Calculate dynamic bounds for diversity
    const divValues = genres.map(([code, data]) => data.avg_lexical_diversity).filter(v => v != null);
    const divMin = Math.min(...divValues);
    const divMax = Math.max(...divValues);
    const divPadding = (divMax - divMin) * 0.2;

    // Diversity by Genre
    const diversityCtx = document.getElementById('genreDiversityChart').getContext('2d');
    genreDiversityChart = new Chart(diversityCtx, {
        type: 'bar',
        data: {
            labels: genres.map(([code, data]) => data.label),
            datasets: [{
                label: 'Lexical Diversity',
                data: genres.map(([code, data]) => data.avg_lexical_diversity),
                backgroundColor: genres.map(([code]) => GENRE_COLORS[code] || '#6b7280'),
                borderWidth: 0,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    borderColor: '#2a2a36',
                    borderWidth: 1,
                    callbacks: {
                        label: ctx => `TTR: ${ctx.raw?.toFixed(3) ?? 'N/A'}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 }, maxRotation: 45 }
                },
                y: {
                    min: Math.max(0, divMin - divPadding),
                    max: divMax + divPadding,
                    grid: { color: '#1f1f28' },
                    ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } }
                }
            }
        }
    });
}

// ============================================
// Trends Section
// ============================================
function initTrendsSection() {
    populateTrendsYearFilters();
    initTrendsChart();
    initEventSelector();

    // Event listeners
    document.getElementById('trend-metric').addEventListener('change', updateTrendsChart);
    document.getElementById('show-events').addEventListener('change', updateTrendsChart);
    document.getElementById('trend-year-start').addEventListener('change', updateTrendsChart);
    document.getElementById('trend-year-end').addEventListener('change', updateTrendsChart);
}

function populateTrendsYearFilters() {
    const years = Object.keys(dashboardData.aggregations.by_year).sort();
    const startSelect = document.getElementById('trend-year-start');
    const endSelect = document.getElementById('trend-year-end');

    years.forEach(y => {
        startSelect.innerHTML += `<option value="${y}">${y}</option>`;
        endSelect.innerHTML += `<option value="${y}">${y}</option>`;
    });

    // Default: full range
    startSelect.value = years[0];
    endSelect.value = years[years.length - 1];
}

function initEventSelector() {
    if (!eventsData?.events || !eventsData?.categories) return;

    // Initialize all categories as active
    activeCategories = new Set(Object.keys(eventsData.categories));

    // Render categories
    renderEventCategories();

    // Render events
    renderEventItems();

    // Setup search
    document.getElementById('event-search').addEventListener('input', filterEventsBySearch);
}

function renderEventCategories() {
    const container = document.getElementById('events-categories');
    const categories = eventsData.categories;

    container.innerHTML = Object.entries(categories).map(([key, cat]) => `
        <button class="category-btn active" data-category="${key}"
                style="--category-color: ${cat.color}"
                onclick="toggleCategory('${key}')">
            <span class="category-dot" style="background: ${cat.color}"></span>
            ${cat.label}
        </button>
    `).join('');
}

function renderEventItems() {
    const container = document.getElementById('events-list');
    const categories = eventsData.categories;

    container.innerHTML = eventsData.events.map((event, idx) => {
        const cat = categories[event.category];
        const color = cat?.color || '#6b7280';

        return `
            <div class="event-item" data-index="${idx}" data-category="${event.category}"
                 style="--event-color: ${color}"
                 onclick="toggleEvent(${idx})">
                <span class="event-dot"></span>
                <span class="event-year">${event.year}</span>
                <span class="event-label">${event.label}</span>
            </div>
        `;
    }).join('');
}

function toggleCategory(category) {
    const btn = document.querySelector(`.category-btn[data-category="${category}"]`);

    if (activeCategories.has(category)) {
        activeCategories.delete(category);
        btn.classList.remove('active');
    } else {
        activeCategories.add(category);
        btn.classList.add('active');
    }

    // Show/hide events based on category
    document.querySelectorAll('.event-item').forEach(item => {
        const cat = item.dataset.category;
        if (activeCategories.has(cat)) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
            // Also deselect hidden events
            const idx = parseInt(item.dataset.index);
            if (selectedEvents.has(idx)) {
                selectedEvents.delete(idx);
                item.classList.remove('selected');
            }
        }
    });

    updateTrendsChart();
}

function toggleEvent(index) {
    const item = document.querySelector(`.event-item[data-index="${index}"]`);

    if (selectedEvents.has(index)) {
        selectedEvents.delete(index);
        item.classList.remove('selected');
    } else {
        selectedEvents.add(index);
        item.classList.add('selected');
    }

    updateTrendsChart();
}

function filterEventsBySearch() {
    const query = document.getElementById('event-search').value.toLowerCase();

    document.querySelectorAll('.event-item').forEach(item => {
        const label = item.querySelector('.event-label').textContent.toLowerCase();
        const year = item.querySelector('.event-year').textContent;
        const category = item.dataset.category;

        const matchesSearch = !query || label.includes(query) || year.includes(query);
        const matchesCategory = activeCategories.has(category);

        if (matchesSearch && matchesCategory) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

function clearAllEvents() {
    selectedEvents.clear();
    document.querySelectorAll('.event-item').forEach(item => {
        item.classList.remove('selected');
    });
    updateTrendsChart();
}

function selectAllVisibleEvents() {
    document.querySelectorAll('.event-item:not(.hidden)').forEach(item => {
        const idx = parseInt(item.dataset.index);
        selectedEvents.add(idx);
        item.classList.add('selected');
    });
    updateTrendsChart();
}

function initTrendsChart() {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    const byYear = dashboardData.aggregations.by_year;

    const years = Object.keys(byYear).sort();
    const sentiments = years.map(y => byYear[y].avg_sentiment);

    // Calculate initial y-axis bounds for sentiment
    const validSentiments = sentiments.filter(v => v !== null && v !== undefined);
    const sentimentMin = Math.min(...validSentiments);
    const sentimentMax = Math.max(...validSentiments);
    const padding = (sentimentMax - sentimentMin) * 0.15;

    // Build event points dataset
    const eventPoints = buildEventPointsDataset(years, byYear, 'sentiment');

    const datasets = [{
        label: 'Sentiment',
        data: sentiments,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        pointRadius: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#f97316',
        order: 1
    }];

    if (eventPoints) {
        datasets.push(eventPoints);
    }

    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'nearest'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    borderColor: '#2a2a36',
                    borderWidth: 1,
                    titleFont: { weight: '600' },
                    padding: 12,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            if (context.dataset.label === 'Events') {
                                return context.dataset.eventLabels[context.dataIndex];
                            }
                            return `${context.dataset.label}: ${context.raw?.toFixed(3) ?? 'N/A'}`;
                        }
                    },
                    filter: function(tooltipItem) {
                        // Show tooltip for events or if hovering main line
                        return tooltipItem.raw !== null;
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        maxTicksLimit: 12,
                        font: { family: "'JetBrains Mono', monospace", size: 10 }
                    }
                },
                y: {
                    min: sentimentMin - padding,
                    max: sentimentMax + padding,
                    grid: { color: '#1f1f28' },
                    ticks: { font: { family: "'JetBrains Mono', monospace", size: 10 } }
                }
            }
        }
    });
}

function buildEventPointsDataset(years, byYear, metric) {
    if (!eventsData?.events || !eventsData?.categories) return null;

    const showEvents = document.getElementById('show-events').checked;
    if (!showEvents || selectedEvents.size === 0) return null;

    const categories = eventsData.categories;

    // Create data array - only for selected events
    const data = [];
    const pointColors = [];
    const pointRadii = [];
    const eventLabels = [];

    years.forEach(year => {
        // Find selected events for this year
        const yearEvents = eventsData.events
            .map((e, idx) => ({ ...e, idx }))
            .filter(e => String(e.year) === year && selectedEvents.has(e.idx));

        if (yearEvents.length > 0) {
            // Use first selected event for this year
            const event = yearEvents[0];
            const yearData = byYear[year];

            let value;
            if (metric === 'diversity') value = yearData?.avg_lexical_diversity;
            else if (metric === 'wordcount') value = yearData?.avg_word_count;
            else value = yearData?.avg_sentiment;

            data.push(value);

            const cat = categories[event.category];
            pointColors.push(cat?.color || '#6b7280');
            pointRadii.push(8);

            // Combine labels if multiple events same year
            const labels = yearEvents.map(e => e.label).join(' | ');
            eventLabels.push(labels);
        } else {
            data.push(null);
            pointColors.push('transparent');
            pointRadii.push(0);
            eventLabels.push('');
        }
    });

    return {
        label: 'Events',
        data: data,
        borderColor: 'transparent',
        backgroundColor: pointColors,
        pointRadius: pointRadii,
        pointHoverRadius: pointRadii.map(r => r > 0 ? 10 : 0),
        pointStyle: 'circle',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        showLine: false,
        order: 0,
        eventLabels: eventLabels
    };
}

function updateTrendsChart() {
    const metric = document.getElementById('trend-metric').value;
    const showEvents = document.getElementById('show-events').checked;
    const yearStart = parseInt(document.getElementById('trend-year-start').value);
    const yearEnd = parseInt(document.getElementById('trend-year-end').value);

    const byYear = dashboardData.aggregations.by_year;
    const allYears = Object.keys(byYear).sort();

    // Filter years by selected range
    const years = allYears.filter(y => {
        const year = parseInt(y);
        return year >= yearStart && year <= yearEnd;
    });

    let values, label, color;

    switch (metric) {
        case 'diversity':
            values = years.map(y => byYear[y].avg_lexical_diversity);
            label = 'Lexical Diversity (TTR)';
            color = '#22d3ee';
            break;
        case 'wordcount':
            values = years.map(y => byYear[y].avg_word_count);
            label = 'Average Word Count';
            color = '#a855f7';
            break;
        default:
            values = years.map(y => byYear[y].avg_sentiment);
            label = 'Sentiment Score';
            color = '#f97316';
    }

    // Calculate dynamic y-axis bounds based on data
    const validValues = values.filter(v => v !== null && v !== undefined);
    const dataMin = Math.min(...validValues);
    const dataMax = Math.max(...validValues);
    const range = dataMax - dataMin;
    const padding = range * 0.15;

    const yMin = dataMin - padding;
    const yMax = dataMax + padding;

    // Update title with year range if not full range
    const fullRange = yearStart === parseInt(allYears[0]) && yearEnd === parseInt(allYears[allYears.length - 1]);
    const yearSuffix = fullRange ? '' : ` (${yearStart}-${yearEnd})`;

    document.getElementById('trends-chart-title').textContent =
        `${metric === 'sentiment' ? 'Sentiment' : metric === 'diversity' ? 'Lexical Diversity' : 'Word Count'} Over Time${yearSuffix}`;
    document.getElementById('trends-chart-subtitle').textContent =
        `How ${metric === 'sentiment' ? 'the emotional tone' : metric === 'diversity' ? 'vocabulary richness' : 'song length'} of hit songs has changed`;

    // Convert hex to rgba for background
    const hexToRgba = (hex, alpha) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    // Update chart labels (years) and data
    trendsChart.data.labels = years;
    trendsChart.data.datasets[0].data = values;
    trendsChart.data.datasets[0].label = label;
    trendsChart.data.datasets[0].borderColor = color;
    trendsChart.data.datasets[0].backgroundColor = hexToRgba(color, 0.1);
    trendsChart.data.datasets[0].pointHoverBackgroundColor = color;

    trendsChart.options.scales.y.min = yMin;
    trendsChart.options.scales.y.max = yMax;

    // Update or remove event points dataset
    const eventDataset = buildEventPointsDataset(years, byYear, metric);

    // Remove existing events dataset if present
    if (trendsChart.data.datasets.length > 1) {
        trendsChart.data.datasets.pop();
    }

    // Add events dataset if enabled
    if (showEvents && eventDataset) {
        trendsChart.data.datasets.push(eventDataset);
    }

    trendsChart.update();

    // Toggle events selector visibility
    document.getElementById('events-selector').style.display = showEvents ? 'block' : 'none';
}


// ============================================
// Summary Section
// ============================================
function initSummarySection() {
    renderSummaryPage();
}

function renderSummaryPage() {
    const container = document.getElementById('summary-grid');
    const byGenre = dashboardData.aggregations.by_genre;
    const tfidfByGenre = dashboardData.tfidf?.by_genre || {};
    const wordFreqByGenre = dashboardData.word_frequencies?.by_genre || {};

    // Genre icons
    const genreIcons = {
        rock: '🎸',
        pop: '🎤',
        rnb: '🎷',
        hiphop: '🎧',
        country: '🤠',
        dance: '🪩',
        other: '🎵'
    };

    // Genre descriptions based on data analysis
    const genreDescriptions = {
        rock: {
            summary: "Rock music emerged from the rebellion of the 1950s and dominated the charts through the 1980s. Known for its emotional intensity and poetic lyrics.",
            characteristics: [
                "Higher lexical diversity than most genres",
                "Often features themes of love, freedom, and rebellion",
                "Vocabulary influenced by blues and folk traditions"
            ]
        },
        pop: {
            summary: "Pop music represents the mainstream of American music, constantly evolving to reflect current trends and tastes.",
            characteristics: [
                "Most commercially successful genre",
                "Emphasis on catchy hooks and repetition",
                "Lyrics focus on universal themes of love and relationships"
            ]
        },
        rnb: {
            summary: "R&B combines soul, funk, and contemporary urban sounds. The genre has continuously evolved while maintaining its emotional core.",
            characteristics: [
                "Rich emotional vocabulary",
                "Strong influence from gospel and soul traditions",
                "Often features themes of love, heartbreak, and sensuality"
            ]
        },
        hiphop: {
            summary: "Hip-Hop emerged from the Bronx in the late 1970s and revolutionized music with its emphasis on lyrical complexity and social commentary.",
            characteristics: [
                "Highest word count per song",
                "Most distinctive vocabulary of any genre",
                "Strong focus on storytelling and wordplay"
            ]
        },
        country: {
            summary: "Country music tells stories of American life, from rural traditions to modern experiences, with distinctive regional vocabulary.",
            characteristics: [
                "Strong narrative tradition",
                "Themes of home, family, and heartache",
                "Regional vocabulary and expressions"
            ]
        },
        dance: {
            summary: "Electronic and dance music prioritizes rhythm and energy over lyrical complexity, designed to move bodies on the dancefloor.",
            characteristics: [
                "Lower word count and lexical diversity",
                "Repetitive hooks for danceability",
                "Focus on mood and energy over storytelling"
            ]
        },
        other: {
            summary: "This category includes songs that cross genre boundaries or don't fit neatly into other categories.",
            characteristics: [
                "Diverse range of styles and influences",
                "Often experimental or genre-blending",
                "Varied lyrical approaches"
            ]
        }
    };

    // Sort genres by song count
    const sortedGenres = Object.entries(byGenre)
        .sort((a, b) => b[1].count - a[1].count);

    container.innerHTML = sortedGenres.map(([code, data]) => {
        const desc = genreDescriptions[code] || genreDescriptions.other;
        const tfidfWords = tfidfByGenre[code]?.slice(0, 8) || [];
        const topWords = wordFreqByGenre[code]?.slice(0, 6) || [];

        // Determine sentiment label
        let sentimentLabel = 'Neutral';
        if (data.avg_sentiment > 0.1) sentimentLabel = 'Positive';
        else if (data.avg_sentiment < -0.05) sentimentLabel = 'Negative';

        return `
            <div class="summary-card" data-genre="${code}">
                <div class="summary-card-header">
                    <div class="summary-genre-icon">${genreIcons[code] || '🎵'}</div>
                    <div class="summary-genre-info">
                        <h3>${data.label}</h3>
                        <span class="song-count">${data.count.toLocaleString()} songs analyzed</span>
                    </div>
                </div>

                <div class="summary-stats">
                    <div class="summary-stat">
                        <span class="summary-stat-value">${data.avg_sentiment?.toFixed(3) ?? 'N/A'}</span>
                        <span class="summary-stat-label">Sentiment</span>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-stat-value">${data.avg_lexical_diversity?.toFixed(3) ?? 'N/A'}</span>
                        <span class="summary-stat-label">Diversity</span>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-stat-value">${Math.round(data.avg_word_count || 0)}</span>
                        <span class="summary-stat-label">Avg Words</span>
                    </div>
                </div>

                <div class="summary-section">
                    <div class="summary-section-title">Distinctive Words (TF-IDF)</div>
                    <div class="summary-keywords">
                        ${tfidfWords.map((w, i) => `<span class="summary-keyword ${i < 3 ? 'highlight' : ''}">${w.word}</span>`).join('')}
                    </div>
                </div>

                <div class="summary-section">
                    <div class="summary-section-title">Most Common Words</div>
                    <div class="summary-keywords">
                        ${topWords.map(w => `<span class="summary-keyword">${w.word}</span>`).join('')}
                    </div>
                </div>

                <div class="summary-section">
                    <div class="summary-section-title">About This Genre</div>
                    <p class="summary-description">${desc.summary}</p>
                    <ul class="summary-description" style="margin-top: 0.5rem; padding-left: 1.2rem;">
                        ${desc.characteristics.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }).join('');
}

// ============================================
// Utilities
// ============================================
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', loadData);
