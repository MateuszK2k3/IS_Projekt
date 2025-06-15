document.addEventListener('DOMContentLoaded', () => {
    let token = null;
    let soapChart = null;

// helper: fetch z JWT
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
                out.textContent = 'Zalogowano pomyślnie!';
                out.className = 'success';
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
                    const data = await resp.json();
                    out.innerHTML = `
          <table>
            <tr><th>Data</th><th>Wartość</th></tr>
            ${data.map(r => `<tr><td>${r.date}</td><td>${r.count || r.rate}</td></tr>`).join('')}
          </table>`;
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
        console.log("siema")
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
    });

    document.getElementById('importFileForm').addEventListener('submit', async e => {
        e.preventDefault();
        const out  = document.getElementById('importFileResult');
        const fmt  = document.getElementById('importFormat').value;
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
});