const SVG_NS = "http://www.w3.org/2000/svg";

function svgNode(name, attributes = {}, text = null) {
  const node = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  if (text !== null) node.textContent = text;
  return node;
}

function formatNumber(value, digits = 1) {
  return Number(value).toFixed(digits);
}

function drawAxes(svg, width, height, margin, xTicks, yTicks, xScale, yScale) {
  yTicks.forEach((value) => {
    const y = yScale(value);
    svg.appendChild(svgNode("line", { x1: margin.left, y1: y, x2: width - margin.right, y2: y, class: "grid-line" }));
    svg.appendChild(svgNode("text", { x: margin.left - 9, y: y + 4, "text-anchor": "end", class: "axis-label" }, value));
  });
  xTicks.forEach(({ value, label }) => {
    const x = xScale(value);
    svg.appendChild(svgNode("line", { x1: x, y1: height - margin.bottom, x2: x, y2: height - margin.bottom + 5, class: "axis-line" }));
    svg.appendChild(svgNode("text", { x, y: height - margin.bottom + 19, "text-anchor": "middle", class: "axis-label" }, label));
  });
  svg.appendChild(svgNode("line", { x1: margin.left, y1: height - margin.bottom, x2: width - margin.right, y2: height - margin.bottom, class: "axis-line" }));
  svg.appendChild(svgNode("line", { x1: margin.left, y1: margin.top, x2: margin.left, y2: height - margin.bottom, class: "axis-line" }));
}

function drawMcChart(items) {
  const svg = document.getElementById("mc-chart");
  const width = 1000;
  const height = 340;
  const margin = { top: 24, right: 28, bottom: 48, left: 48 };
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = "";
  if (!items.length) return;

  const values = items.map((item) => Number(item.mc));
  const minY = Math.floor((Math.min(...values) - 0.2) * 10) / 10;
  const maxY = Math.ceil((Math.max(...values) + 0.2) * 10) / 10;
  const xScale = (index) => margin.left + index * (width - margin.left - margin.right) / Math.max(1, items.length - 1);
  const yScale = (value) => height - margin.bottom - (value - minY) * (height - margin.top - margin.bottom) / Math.max(0.1, maxY - minY);
  const tickStep = Math.max(1, Math.floor(items.length / 6));
  const xTicks = items.map((item, index) => ({ value: index, label: item.window_end.slice(0, 7) })).filter((_, index) => index % tickStep === 0 || index === items.length - 1);
  const yTicks = Array.from({ length: 5 }, (_, index) => formatNumber(minY + index * (maxY - minY) / 4, 1));

  drawAxes(svg, width, height, margin, xTicks, yTicks, xScale, (value) => yScale(Number(value)));
  const path = items.map((item, index) => `${index === 0 ? "M" : "L"}${xScale(index)},${yScale(item.mc)}`).join(" ");
  svg.appendChild(svgNode("path", { d: path, class: "mc-line" }));

  items.forEach((item, index) => {
    const point = svgNode("circle", { cx: xScale(index), cy: yScale(item.mc), r: 5, class: "mc-point" });
    point.appendChild(svgNode("title", {}, `${item.window_start} 至 ${item.window_end}\nMc ${item.mc.toFixed(1)}；n=${item.sample_count}`));
    svg.appendChild(point);
  });
}

function drawFrequencyChart(items) {
  const svg = document.getElementById("frequency-chart");
  const width = 640;
  const height = 340;
  const margin = { top: 24, right: 24, bottom: 48, left: 48 };
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = "";
  if (!items.length) return;

  const maxMagnitude = Math.max(...items.map((item) => item.magnitude));
  const minMagnitude = Math.min(...items.map((item) => item.magnitude));
  const maxValue = Math.max(...items.map((item) => Math.max(item.count, item.cumulative)));
  const xScale = (value) => margin.left + (value - minMagnitude) * (width - margin.left - margin.right) / Math.max(0.1, maxMagnitude - minMagnitude);
  const yScale = (value) => height - margin.bottom - value * (height - margin.top - margin.bottom) / maxValue;
  const barWidth = Math.max(2, (width - margin.left - margin.right) / items.length * 0.72);
  const tickItems = items.filter((_, index) => index % Math.max(1, Math.floor(items.length / 6)) === 0);
  const xTicks = tickItems.map((item) => ({ value: item.magnitude, label: item.magnitude.toFixed(1) }));
  const yTicks = Array.from({ length: 5 }, (_, index) => Math.round(index * maxValue / 4));

  drawAxes(svg, width, height, margin, xTicks, yTicks, xScale, yScale);
  items.forEach((item) => {
    const x = xScale(item.magnitude) - barWidth / 2;
    const y = yScale(item.count);
    const bar = svgNode("rect", { x, y, width: barWidth, height: height - margin.bottom - y, class: "bar" });
    bar.appendChild(svgNode("title", {}, `M ${item.magnitude.toFixed(1)}：${item.count} 個事件`));
    svg.appendChild(bar);
  });
  const path = items.map((item, index) => `${index === 0 ? "M" : "L"}${xScale(item.magnitude)},${yScale(item.cumulative)}`).join(" ");
  svg.appendChild(svgNode("path", { d: path, class: "cumulative-line" }));
}

function drawMap(events, threshold) {
  const svg = document.getElementById("event-map");
  const width = 640;
  const height = 390;
  const margin = { top: 18, right: 20, bottom: 30, left: 42 };
  const bounds = { minLon: 119.5, maxLon: 122.6, minLat: 21.4, maxLat: 25.6 };
  const xScale = (lon) => margin.left + (lon - bounds.minLon) * (width - margin.left - margin.right) / (bounds.maxLon - bounds.minLon);
  const yScale = (lat) => height - margin.bottom - (lat - bounds.minLat) * (height - margin.top - margin.bottom) / (bounds.maxLat - bounds.minLat);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = "";
  svg.appendChild(svgNode("rect", { x: margin.left, y: margin.top, width: width - margin.left - margin.right, height: height - margin.top - margin.bottom, rx: 10, class: "map-frame" }));

  const taiwan = [[121.0,25.3],[121.35,24.8],[121.55,24.1],[121.45,23.4],[121.05,22.5],[120.75,21.9],[120.45,22.4],[120.25,23.2],[120.45,24.1],[120.7,24.8]];
  const polygon = taiwan.map(([lon, lat]) => `${xScale(lon)},${yScale(lat)}`).join(" ");
  svg.appendChild(svgNode("polygon", { points: polygon, class: "taiwan-shape" }));

  const filtered = events.filter((event) => event.magnitude >= threshold);
  filtered.forEach((event) => {
    const radius = Math.max(2.2, 1.25 + event.magnitude * 0.8);
    const point = svgNode("circle", { cx: xScale(event.longitude), cy: yScale(event.latitude), r: radius, class: "event-point" });
    point.appendChild(svgNode("title", {}, `${event.event_id}\n${event.time}\nM ${event.magnitude.toFixed(1)} · 深度 ${event.depth_km.toFixed(1)} km`));
    svg.appendChild(point);
  });

  document.getElementById("filter-summary").textContent = `顯示 ${filtered.length} / ${events.length} 個事件`;
}

async function loadDashboard() {
  const status = document.getElementById("load-status");
  try {
    const response = await fetch("data/summary.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const summary = data.summary;

    document.getElementById("data-notice").textContent = data.metadata.data_notice;
    document.getElementById("event-count").textContent = summary.event_count.toLocaleString("zh-Hant");
    document.getElementById("date-range").textContent = `${summary.date_start} — ${summary.date_end}`;
    document.getElementById("overall-mc").textContent = summary.overall_mc.toFixed(1);
    document.getElementById("latest-mc").textContent = summary.latest_mc.toFixed(1);
    document.getElementById("latest-samples").textContent = `3 個月視窗 n = ${summary.latest_mc_samples}`;
    document.getElementById("magnitude-range").textContent = `${summary.magnitude_min.toFixed(1)}–${summary.magnitude_max.toFixed(1)}`;

    drawMcChart(data.moving_mc);
    drawFrequencyChart(data.magnitude_frequency);

    const slider = document.getElementById("magnitude-filter");
    slider.max = Math.ceil(summary.magnitude_max * 10) / 10;
    const updateMap = () => {
      const threshold = Number(slider.value);
      document.getElementById("filter-value").textContent = threshold.toFixed(1);
      drawMap(data.events, threshold);
    };
    slider.addEventListener("input", updateMap);
    updateMap();

    status.textContent = "資料已載入";
    status.className = "status ready";
  } catch (error) {
    console.error(error);
    status.textContent = "資料載入失敗";
    status.className = "status error";
    document.getElementById("data-notice").textContent = "無法讀取分析資料；請檢查 GitHub Actions 是否成功產生 site/data/summary.json。";
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);
