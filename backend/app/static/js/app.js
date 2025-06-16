document.addEventListener('DOMContentLoaded', async () => {
    let token = localStorage.getItem('token') || null; // Ładuj token z localStorage
    let soapChart = null;

    // Helper: fetch z JWT
    async function fetchWithToken(url, opts = {}) {
        if (!token) {
            alert('Proszę się zalogować!');
            return null;
        }
        opts.headers = {
            ...opts.headers,
            'Authorization': `Bearer ${token}`
        };
        return fetch(url, opts);
    }

    // Sprawdź stan zalogowania przy starcie
    if (token) {
        try {
            const resp = await fetchWithToken('/api/v1/unemployment/monthly-avg');
            if (resp && resp.ok) {
                // Użytkownik zalogowany
                document.getElementById('mainNav').classList.remove('hidden');
                document.getElementById('authSection').classList.add('hidden');
                document.getElementById('homeSection').classList.remove('hidden');
                await renderHomeCharts();
                await renderBarChart();
            } else {
                // Token nieważny
                token = null;
                localStorage.removeItem('token');
                document.getElementById('authSection').classList.remove('hidden');
            }
        } catch {
            // Błąd serwera
            token = null;
            localStorage.removeItem('token');
            document.getElementById('authSection').classList.remove('hidden');
        }
    }

    // REJESTRACJA
    document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("regUsername").value;
        const password = document.getElementById("regPassword").value;
        const result = document.getElementById("registerResult");
        result.textContent = "";

        try {
            const res = await fetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (res.ok) {
                result.textContent = data.msg;
                result.className = "text-green-600 mt-2";
            } else {
                result.textContent = data.msg || "Błąd rejestracji";
                result.className = "text-red-600 mt-2";
            }
        } catch {
            result.textContent = "Błąd połączenia z serwerem";
            result.className = "text-red-600 mt-2";
        }
    });

    // LOGOWANIE
    document.getElementById('loginForm').addEventListener('submit', async e => {
        e.preventDefault();
        const user = document.getElementById('username').value;
        const pass = document.getElementById('password').value;
        const out = document.getElementById('loginResult');
        try {
            const resp = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, password: pass})
            });
            const data = await resp.json();
            if (resp.ok) {
                token = data.access_token;
                localStorage.setItem('token', token);
                document.getElementById('mainNav').classList.remove('hidden');
                document.getElementById('authSection').classList.add('hidden');
                document.getElementById('homeSection').classList.remove('hidden');

                await renderHomeCharts();
                await renderBarChart();

                out.textContent = 'Zalogowano pomyślnie!';
                out.className = 'text-green-600 mt-2';
            } else {
                out.textContent = data.msg || 'Błąd logowania';
                out.className = 'error';
            }
        } catch {
            out.textContent = 'Błąd serwera';
            out.className = 'error';
        }
    });

    // EKSPORT DANYCH
    document.getElementById('exportForm').addEventListener('submit', async e => {
        e.preventDefault();
        const t = document.getElementById('type').value;
        const f = document.getElementById('from').value;
        const to = document.getElementById('to').value;
        const fmt = document.getElementById('format').value;
        const out = document.getElementById('exportResult');

        try {
            const resp = await fetchWithToken(
                `/api/v1/export?type=${t}&from=${f}&to=${to}`,
                {headers: {'Accept': fmt}}
            );
            if (!resp) return;
            if (resp.ok) {
                const ct = resp.headers.get('Content-Type');
                if (ct.includes('application/json')) {
                    const blob = await resp.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `data.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                    out.textContent = 'Pobrano plik JSON.';
                    out.className = 'success';
                } else {
                    const text = await resp.text();
                    const blob = new Blob([text], {type: ct});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `data.${fmt.split('/')[1]}`;
                    a.click();
                    URL.revokeObjectURL(url);
                    out.textContent = 'Pobieranie rozpoczęte!';
                    out.className = 'success';
                }
            } else {
                const err = await resp.json();
                out.textContent = err.error || 'Błąd eksportu';
                out.className = 'error';
            }
        } catch {
            out.textContent = 'Błąd serwera';
            out.className = 'error';
        }
    });

    // IMPORT ZGONÓW
    document.getElementById('importDeathsBtn').addEventListener('click', async () => {
        const out = document.getElementById('importDeathsResult');
        try {
            const resp = await fetchWithToken('/api/v1/deaths/import', {method: 'POST'});
            const data = await resp.json();
            out.textContent = resp.ok ? data.msg : data.error;
            out.className = resp.ok ? 'success' : 'error';
        } catch {
            out.textContent = 'Błąd serwera';
            out.className = 'error';
        }
    });

    // SOAP helper
    async function soapRequest(year, month) {
        const body = `<?xml version="1.0"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://example.com/unemployment"><soapenv:Body><ns:get_unemployment_rate><year>${year}</year><month>${month}</month></ns:get_unemployment_rate></soapenv:Body></soapenv:Envelope>`;
        const resp = await fetch('http://localhost:8002/ws/unemployment', {
            method: 'POST',
            headers: {'Content-Type': 'text/xml'},
            body
        });
        const text = await resp.text();
        const m = text.match(/<ns:rate>(.*?)<\/ns:rate>/);
        return m ? parseFloat(m[1]) : null;
    }

    // SOAP: pojedyncza wartość
    document.getElementById('soapFetchBtn').addEventListener('click', async () => {
        const y = document.getElementById('soapYear').value;
        const m = document.getElementById('soapMonth').value;
        const out = document.getElementById('soapResultSingle');
        out.textContent = 'Ładowanie…';
        try {
            const rate = await soapRequest(y, m);
            out.innerHTML = rate != null ? `Stopa w ${m.padStart(2, '0')}.${y}: <b>${rate}%</b>` : '<span class="error">Brak danych</span>';
        } catch {
            out.innerHTML = '<span class="error">Błąd SOAP</span>';
        }
    });

    // SOAP: cała seria + wykres
    document.getElementById('soapFetchAllBtn').addEventListener('click', async () => {
        const out = document.getElementById('soapResultAll');
        out.textContent = 'Ładowanie serii…';
        const calls = [];
        for (let y = 2018; y <= 2022; y++) for (let m = 1; m <= 12; m++) calls.push(soapRequest(y, m).then(rate => ({
            year: y,
            month: m,
            rate
        })));
        const results = await Promise.all(calls);
        const data = results.filter(r => r.rate != null);

        // wykres
        const labels = data.map(r => `${r.year}-${String(r.month).padStart(2, '0')}`);
        const values = data.map(r => r.rate);
        const ctx = document.getElementById('soapChart').getContext('2d');
        if (soapChart) {
            soapChart.config.data.labels = labels;
            soapChart.config.data.datasets[0].data = values;
            soapChart.update();
        } else {
            soapChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{label: 'Stopa bezrobocia[%]', data: values, fill: false, tension: 0.1, borderWidth: 2}]
                },
                options: {
                    responsive: true,
                    scales: {x: {title: {display: true, text: 'Data'}}, y: {title: {display: true, text: 'Stopa[%]'}}}
                }
            });
        }
      out.textContent = 'Ukończono ładowanie wykresu';
    });

    document.getElementById('importFileForm').addEventListener('submit', async e => {
        e.preventDefault();
        const out = document.getElementById('importFileResult');
        const fmt = document.getElementById('importFormat').value;
        const file = document.getElementById('importFile').files[0];

        // walidacja
        if (!fmt || !file) {
            out.innerHTML = '<span class="error">Wybierz format i plik.</span>';
            return;
        }

        const fd = new FormData();
        fd.append('format', fmt);
        fd.append('file', file);

        const resp = await fetchWithToken('/api/v1/unemployment/import/file', {
            method: 'POST',
            body: fd
        });
        if (!resp) return;

        // próbujemy wyciągnąć JSON, ale w razie gdyby serwer zwrócił HTML/text
        let js;
        try {
            js = await resp.json();
        } catch (err) {
            const txt = await resp.text();
            out.innerHTML = `<span class="error">Nieoczekiwana odpowiedź serwera: ${txt}</span>`;
            return;
        }

        if (resp.ok) {
            out.innerHTML = `<span class="success">${js.msg}</span>`;
        } else {
            out.innerHTML = `<span class="error">${js.error || js.msg}</span>`;
        }
    });

    const dateSlider = document.getElementById('dateSlider');
    if (dateSlider) {
        const fromInput = document.getElementById('from');
        const toInput = document.getElementById('to');
        const rangeFromEl = document.getElementById('rangeFrom');
        const rangeToEl = document.getElementById('rangeTo');

        const months = [];
        for (let y = 2018; y <= 2022; y++) {
            for (let m = 0; m < 12; m++) {
                const date = new Date(y, m, 1);
                months.push(date);
            }
        }

        const timestamps = months.map(d => d.getTime());

        noUiSlider.create(dateSlider, {
            start: [timestamps[0], timestamps[timestamps.length - 1]],
            range: {
                min: timestamps[0],
                max: timestamps[timestamps.length - 1]
            },
            step: 30 * 24 * 60 * 60 * 1000, // ~1 miesiąc
            connect: true,
            tooltips: [
                {
                    to: ts => {
                        const d = new Date(parseInt(ts));
                        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                    },
                    from: () => null
                },
                {
                    to: ts => {
                        const d = new Date(parseInt(ts));
                        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                    },
                    from: () => null
                }
            ],
            format: {
                to: v => parseInt(v),
                from: v => parseInt(v)
            }
        });

        dateSlider.noUiSlider.on('update', (values) => {
            const format = ts => {
                const d = new Date(parseInt(ts));
                return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            };
            const fromDate = format(values[0]);
            const toDate = format(values[1]);

            rangeFromEl.textContent = fromDate;
            rangeToEl.textContent = toDate;
            fromInput.value = fromDate;
            toInput.value = toDate;
        });
    }
});

async function fetchData(url, key) {
    const resp = await fetch(url, {
        headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            Accept: 'application/json'
        }
    });

    if (!resp.ok) {
        throw new Error(`Błąd API: ${resp.status}`);
    }

    const data = await resp.json();
    return data.map(d => ({
        date: d.date,
        value: parseFloat(d[key])
    }));
}

async function renderHomeCharts() {
    let chartInstance;
    try {
        chartInstance = Chart.getChart('combinedChart'); // Pobierz istniejący wykres
        if (chartInstance) {
            chartInstance.destroy(); // Zniszcz istniejący wykres
        }
    } catch (e) {
        console.log('Brak istniejącego wykresu do zniszczenia:', e);
    }

    const [unemployment, deathsRaw] = await Promise.all([
        fetchData('/api/v1/unemployment/monthly-avg', 'rate'),
        fetchData('/api/v1/export?type=deaths&from=2018-01&to=2022-12', 'count'),
    ]);

    const deaths = groupByMonth(deathsRaw);

    const labels = deaths.map(d => d.date); // te same miesiące

    const deathsData = deaths.map(d => d.value);
    const unemploymentMap = new Map(unemployment.map(d => [d.date.slice(0, 7), d.value]));
    const unemploymentData = labels.map(month => unemploymentMap.get(month) || null);

    const ctx = document.getElementById('combinedChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Zgony (miesięcznie)',
                    data: deathsData,
                    backgroundColor: 'rgba(255, 99, 132, 0.3)',
                    yAxisID: 'yDeaths',
                },
                {
                    label: 'Stopa bezrobocia (%)',
                    data: unemploymentData,
                    type: 'line',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: false,
                    yAxisID: 'yUnemployment',
                    tension: 0.3,
                    pointRadius: 2,
                },
            ],
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            stacked: false,
            scales: {
                yDeaths: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Zgony' },
                },
                yUnemployment: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Bezrobocie (%)' },
                    grid: { drawOnChartArea: false },
                    min: 3,
                    max: 8
                },
            },
        },
    });
}

async function renderBarChart() {
    let chartInstance;
    try {
        chartInstance = Chart.getChart('barChart');
        if (chartInstance) {
            chartInstance.destroy();
        }
    } catch (e) {
        console.log('Brak istniejącego wykresu do zniszczenia:', e);
    }

    const resp = await fetch('/api/v1/unemployment/region-latest', {
        headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            Accept: 'application/json'
        },
    });
    const data = await resp.json();
    const ctx = document.getElementById('barChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(r => r.region),
            datasets: [{
                label: 'Stopa bezrobocia (%)',
                data: data.map(r => r.rate),
                backgroundColor: 'rgba(0, 123, 255, 0.6)',
            }],
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    title: { display: true, text: 'Bezrobocie (%)' },
                },
            },
        },
    });
}

function groupByMonth(data) {
    const grouped = {};

    for (const { date, value } of data) {
        const month = date.slice(0, 7); // YYYY-MM
        if (!grouped[month]) grouped[month] = 0;
        grouped[month] += value;
    }

    return Object.entries(grouped).map(([month, total]) => ({
        date: month,
        value: total
    }));
}

window.renderHomeCharts = renderHomeCharts;
window.renderBarChart = renderBarChart;