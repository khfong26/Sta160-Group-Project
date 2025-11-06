document.addEventListener("DOMContentLoaded", () => {

  fetch("/api/cpi_data")
    .then(response => response.json())
    .then(data => {
      const trace = {
        x: data.dates,
        y: data.values,
        mode: "lines+markers",
        type: "scatter",
        marker: { color: "#007bff" }
      };
      const layout = {
        title: "FAOSTAT — Food CPI (2015 = 100)",
        xaxis: { title: "Date" },
        yaxis: { title: "Index (2015 = 100)" },
        margin: { t: 50, r: 30, b: 50, l: 60 }
      };
      Plotly.newPlot("faostat-chart", [trace], layout, { responsive: true });
    })
    .catch(err => console.warn("FAOSTAT data load failed:", err));


  // --- Placeholder: World Bank ---
  const wbTrace = {
    x: ["2018", "2019", "2020", "2021", "2022"],
    y: [2.3, 2.1, 3.0, 4.2, 5.6],
    type: "bar",
    marker: { color: "#28a745" }
  };
  Plotly.newPlot("worldbank-chart", [wbTrace], {
    title: "World Bank Inflation (Sample Data)",
    xaxis: { title: "Year" },
    yaxis: { title: "%" },
    margin: { t: 50, r: 30, b: 50, l: 60 }
  }, { responsive: true });


  // --- Placeholder: IMF ---
  const imfTrace = {
    x: ["GDP", "Inflation", "Unemployment"],
    y: [3.5, 6.2, 4.1],
    type: "bar",
    marker: { color: "#ffc107" }
  };
  Plotly.newPlot("imf-chart", [imfTrace], {
    title: "IMF Economic Indicators (Sample Data)",
    margin: { t: 50, r: 30, b: 50, l: 60 }
  }, { responsive: true });


  // --- Placeholder: Our World in Data ---
  const owidTrace = {
    x: ["US", "UK", "Germany", "Japan", "India"],
    y: [250, 230, 210, 200, 180],
    type: "scatter",
    mode: "lines+markers",
    marker: { color: "#dc3545" }
  };
  Plotly.newPlot("owid-chart", [owidTrace], {
    title: "CPI Comparison (Sample Data)",
    margin: { t: 50, r: 30, b: 50, l: 60 }
  }, { responsive: true });

});
