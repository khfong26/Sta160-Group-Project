/* src/website/static/js/main.js
   Chart loaders, filter wiring, and safe updates.
*/

// helper: do a GET and optionally attach query params from an object
async function getData(url, params = null) {
    let full = url;
    if (params && Object.keys(params).length) {
        const qs = new URLSearchParams(params);
        full = `${url}?${qs}`;
    }
    const res = await fetch(full);
    return await res.json();
}

// salary: accept optional filters object { location, job }
async function loadSalaryChart(filters = {}) {
    const data = await getData("/api/salary", filters);

    const trace = {
        x: data.salary || [],
        type: "histogram",
        marker: { color: "#4f46e5" }, // Indigo-600
        hovertemplate: "Salary: $%{x}<br>Count: %{y} jobs<extra></extra>"
    };
    const layout = {
        title: "Salary Distribution",
        xaxis: { title: "Salary (USD)" },
        yaxis: { title: "Count" },
        margin: { t: 40, l: 40, r: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: 'Inter, sans-serif' }
    };

    const el = document.getElementById("chart-salary") || document.getElementById("salary-detail-chart");
    if (!el) return;

    // If chart already exists, use Plotly.react to update; otherwise create it.
    if (el.data && el.data.length) {
        Plotly.react(el, [trace], layout);
    } else {
        Plotly.newPlot(el, [trace], layout, { responsive: true });
    }
}

// skills
async function loadSkillsChart(filters = {}) {
    const data = await getData("/api/skills", filters);

    const el = document.getElementById("chart-skills") || document.getElementById("skills-detail-chart");
    if (!el) return;

    Plotly.newPlot(el, [{
        x: data.skill || [],
        y: data.count || [],
        type: "bar",
        marker: { color: "#10b981" }, // Emerald-500
        hovertemplate: "Skill: %{x}<br>Count: %{y}<extra></extra>"
    }], {
        title: "Top Skills",
        xaxis: { title: "Skill" },
        yaxis: { title: "Count" },
        margin: { t: 40, l: 40, r: 20, b: 120 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: 'Inter, sans-serif' }
    }, { responsive: true });
}

// trends
async function loadTrendsChart(filters = {}) {
    const data = await getData("/api/trends", filters);

    const el = document.getElementById("chart-trends") || document.getElementById("trends-detail-chart");
    if (!el) return;

    Plotly.newPlot(el, [{
        x: data.date || [],
        y: data.postings || [],
        mode: "lines+markers",
        line: { color: "#f97316", width: 3 }, // Orange-500
        marker: { size: 6 },
        hovertemplate: "Date: %{x}<br>Postings: %{y}<extra></extra>"
    }], {
        title: "Job Posting Trends",
        xaxis: { title: "Date" },
        yaxis: { title: "Count" },
        margin: { t: 40, l: 40, r: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: 'Inter, sans-serif' }
    }, { responsive: true });
}

// small debounce helper
const debounce = (fn, wait = 300) => {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn(...args), wait);
    };
};

// single DOMContentLoaded listener  add filter wiring here
document.addEventListener("DOMContentLoaded", () => {
    // initial loads
    if (document.getElementById("chart-salary") || document.getElementById("salary-detail-chart")) loadSalaryChart();
    if (document.getElementById("chart-skills") || document.getElementById("skills-detail-chart")) loadSkillsChart();
    if (document.getElementById("chart-trends") || document.getElementById("trends-detail-chart")) loadTrendsChart();

    // Salary Filters
    const locationFilter = document.getElementById("locationFilter");
    const jobFilter = document.getElementById("jobFilter");

    const updateSalaryWithFilters = debounce(() => {
        const filters = {};
        if (locationFilter && locationFilter.value) filters.location = locationFilter.value;
        if (jobFilter && jobFilter.value) filters.job = jobFilter.value;
        loadSalaryChart(filters);
    }, 300);

    if (locationFilter) {
        locationFilter.addEventListener("change", updateSalaryWithFilters);
    }
    if (jobFilter) {
        jobFilter.addEventListener("change", updateSalaryWithFilters);
    }

    // Trends Filters
    const trendsLocationFilter = document.getElementById("trendsLocationFilter");
    const trendsJobFilter = document.getElementById("trendsJobFilter");

    const updateTrendsWithFilters = debounce(() => {
        const filters = {};
        if (trendsLocationFilter && trendsLocationFilter.value) filters.location = trendsLocationFilter.value;
        if (trendsJobFilter && trendsJobFilter.value) filters.job = trendsJobFilter.value;
        loadTrendsChart(filters);
    }, 300);

    if (trendsLocationFilter) {
        trendsLocationFilter.addEventListener("change", updateTrendsWithFilters);
    }
    if (trendsJobFilter) {
        trendsJobFilter.addEventListener("change", updateTrendsWithFilters);
    }

    // Skills Filters
    const skillsLocationFilter = document.getElementById("skillsLocationFilter");
    const skillsJobFilter = document.getElementById("skillsJobFilter");

    const updateSkillsWithFilters = debounce(() => {
        const filters = {};
        if (skillsLocationFilter && skillsLocationFilter.value) filters.location = skillsLocationFilter.value;
        if (skillsJobFilter && skillsJobFilter.value) filters.job = skillsJobFilter.value;
        loadSkillsChart(filters);
    }, 300);

    if (skillsLocationFilter) {
        skillsLocationFilter.addEventListener("change", updateSkillsWithFilters);
    }
    if (skillsJobFilter) {
        skillsJobFilter.addEventListener("change", updateSkillsWithFilters);
    }

    // Load filters dynamically
    loadFilters();
});

async function loadFilters() {
    const data = await getData("/api/filters");

    const populateSelect = (id, items) => {
        const select = document.getElementById(id);
        if (!select) return;

        // Keep the first option (All ...)
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);

        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            select.appendChild(option);
        });
    };

    const locationSelects = ['locationFilter', 'trendsLocationFilter', 'skillsLocationFilter'];
    const jobSelects = ['jobFilter', 'trendsJobFilter', 'skillsJobFilter'];

    locationSelects.forEach(id => populateSelect(id, data.locations));
    jobSelects.forEach(id => populateSelect(id, data.jobs));
}
