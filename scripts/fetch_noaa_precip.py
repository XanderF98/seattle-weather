<script>
const MONTHS_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
let monthlyData = [];
let annualData = [];

/** 1. SMART DATA PROCESSING (Handles different header names) **/
function getVal(row, keys) {
    const foundKey = Object.keys(row).find(k => keys.includes(k.toUpperCase()));
    return foundKey ? row[foundKey] : null;
}

function processMonthlyRow(row) {
    const dateVal = getVal(row, ['DATE', 'MONTH', 'TIME']);
    const precipVal = getVal(row, ['PRCP', 'PRECIP', 'VALUE', 'PRECIPITATION']);
    
    if (!dateVal) return null;
    
    const dateParts = String(dateVal).split('-');
    const year = parseInt(dateParts[0]);
    const monthIndex = parseInt(dateParts[1]) - 1;
    
    return {
        Year: year,
        Month: MONTHS_ORDER[monthIndex],
        Precip: parseFloat(precipVal) || 0
    };
}

function processAnnualRow(row) {
    const dateVal = getVal(row, ['DATE', 'YEAR', 'TIME']);
    const precipVal = getVal(row, ['PRCP', 'PRECIP', 'VALUE', 'PRECIPITATION']);
    
    if (!dateVal) return null;
    return {
        Year: parseInt(String(dateVal).split('-')[0]),
        Precip: parseFloat(precipVal) || 0
    };
}

function loadCSV(path){
  return new Promise((resolve,reject)=>{
    Papa.parse(path, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: results => {
          if (results.errors.length > 0) reject("Parse Error");
          else resolve(results.data);
      },
      error: err => reject(err)
    });
  });
}

/** 2. UI & CHARTS (Same as before) **/
function initSelectors(){
  const sel = document.getElementById('yearSel');
  const years = Array.from(new Set(monthlyData.map(d=>d.Year))).sort((a,b)=>b-a);
  sel.innerHTML = years.map(y=>`<option value='${y}'>${y}</option>`).join('');
  sel.onchange = renderMonthly;
  if(years.length){ sel.value = years[0]; }
}

function renderMonthly(){
  const year = parseInt(document.getElementById('yearSel').value,10);
  const rows = monthlyData.filter(d=>d.Year===year);
  const monthMap = new Map(rows.map(r=>[r.Month, r.Precip]));
  const x = MONTHS_ORDER;
  const y = x.map(m=> monthMap.has(m) ? monthMap.get(m) : 0);
  const trace = { x, y, type:'bar', marker:{color:'#1B98E0'} };
  Plotly.newPlot('monthlyChart', [trace], { title:`Monthly Rainfall in ${year}`, yaxis:{title:'Inches'} });
}

function renderAnnualTrend() {
    const trace = {
        x: annualData.map(d => d.Year),
        y: annualData.map(d => d.Precip),
        type: 'scatter', mode: 'lines+markers', line: {color: '#123C69'}
    };
    Plotly.newPlot('annualTrend', [trace], { title: 'Total Annual Precipitation', yaxis: {title: 'Inches'} });
}

function renderHeatmap() {
    const years = Array.from(new Set(monthlyData.map(d => d.Year))).sort();
    const zData = years.map(y => {
        const yearRows = monthlyData.filter(d => d.Year === y);
        const monthMap = new Map(yearRows.map(r => [r.Month, r.Precip]));
        return MONTHS_ORDER.map(m => monthMap.get(m) || 0);
    });
    const data = [{ z: zData, x: MONTHS_ORDER, y: years, type: 'heatmap', colorscale: 'Blues' }];
    Plotly.newPlot('monthlyHeat', data, { title: 'Rainfall Intensity (Heatmap)' });
}

/** 3. STARTUP ENGINE **/
window.addEventListener('DOMContentLoaded', () => {
    const errorBox = document.getElementById('error-box');
    
    Promise.all([
        loadCSV('seattle_rain_monthly.csv'),
        loadCSV('seattle_rain_annual.csv')
    ])
    .then(([monthlyRaw, annualRaw]) => {
        monthlyData = monthlyRaw.map(processMonthlyRow).filter(d => d !== null);
        annualData = annualRaw.map(processAnnualRow).filter(d => d !== null);
        
        if(monthlyData.length === 0 || annualData.length === 0) {
            errorBox.innerHTML = "<strong>Error:</strong> Files loaded, but the data format is unexpected. Check your CSV column headers.";
            errorBox.style.display = 'block';
            return;
        }

        initSelectors();
        renderMonthly();
        renderAnnualTrend();
        renderHeatmap();
    })
    .catch(err => {
        console.error(err);
        errorBox.innerHTML = `<strong>Error:</strong> Could not load CSV files. (Details: ${err.statusText || 'File not found or CORS error'})`;
        errorBox.style.display = 'block';
    });
});
</script>
