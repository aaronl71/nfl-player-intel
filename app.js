
// Search bar input function 
document.getElementById("player-search").addEventListener("input", async function() {
    const query = this.value; 
    const url = "http://127.0.0.1:8000/players?search=" + query; //updates GET request based on search input
    try{
        const response = await fetch(url) //Get request
        if (!response.ok) {
            throw new Error("Response status: ${response.status}")
        }

        const result = await response.json(); // forces JS to await result 

        // rewrites result into HTML form from a list
        const html = result.map(function(player) { 
            return `<li class="recent-player-item">${player.name}</li>`
        }).join('');
        
        // updates the recent players bar to match the search input
        document.querySelector('#recent-players').innerHTML = html;
        
        // user clicks on specific player 
        document.querySelectorAll('#recent-players .recent-player-item').forEach(function(li, index){
            li.addEventListener('click', async function(){
                // updates fetch url based on specific player id from player selected 
                const url = "http://127.0.0.1:8000/players/" + result[index].player_id;
                const proj_url = "http://127.0.0.1:8000/projections/" + result[index].player_id;
                const stats_url = "http://127.0.0.1:8000/players/" + result[index].player_id + "/season_stats";
                try{
                    // JS awaits fetch response 
                    const response = await fetch(url)
                    if (!response.ok) {
                        throw new Error("Response status: ${response.status}")
                    }
                    // JS awaits JSON response
                    const player = await response.json();
                    

                    //calls render player function with selected player object
                    renderPlayer(player);

                    //fetching projection
                    const projResponse = await fetch(proj_url)
                    if (!projResponse.ok) {
                        throw new Error("Response status: ${response.status}")
                    }
                    const projections = await projResponse.json();
                    renderProjection(projections);

                    const statsResponse = await fetch(stats_url);
                    const seasonStats = await statsResponse.json();
                    renderSeasonStats(seasonStats);

                    document.querySelector('.scouting-body').innerHTML =
                        '<p class="scouting-text" style="color: var(--text-3);">Generating report…</p>';
                    const scouting_url = "http://127.0.0.1:8000/scouting/" + result[index].player_id;
                    let fullText = '';
                    const eventSource = new EventSource(scouting_url);
                    eventSource.onmessage = function(event) {
                        if (event.data === '[DONE]') {
                            eventSource.close();
                            renderScoutingReport(fullText);
                            return;
                        }
                        fullText += JSON.parse(event.data);
                        document.querySelector('.scouting-body').innerHTML =
                            '<p class="scouting-text">' + fullText + '</p>';
                    };
                    eventSource.onerror = function() {
                        eventSource.close();
                    };
                }
                
                catch(error){
                console.error(error);
            }
        });
    });
    }   
    catch(error) {
        console.error("Error");
    }
});


const searchInput = document.querySelector('#player-search');


const filterBtns = document.querySelectorAll('.filter-btn')

filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
        filterBtns.forEach(function(b) { b.classList.remove('active') })
        btn.classList.add('active')
    })
})

const ESPN_ABBREV = {
    'LA':  'lar',   // Rams (nflverse uses LA, ESPN uses LAR)
    'JAX': 'jac',   // Jaguars (nflverse uses JAX, ESPN uses JAC)
};

function getTeamLogoUrl(team) {
    const abbrev = ESPN_ABBREV[team] || team.toLowerCase();
    return `https://a.espncdn.com/i/teamlogos/nfl/500/${abbrev}.png`;
}

function renderPlayer(player){
    document.querySelector('#player-name').textContent = player.name;
    const age = player.age != null ? Math.round(player.age) : '—';
    const expYears = player.years_exp != null ? Math.round(player.years_exp) : null;
    const expLabel = expYears === null ? '—' : expYears === 0 ? 'Rookie' : `${expYears} yrs exp`;
    document.querySelector('#player-meta').textContent =
        `${player.team || '—'}  ·  Age ${age}  ·  ${expLabel}`;
    document.querySelector('.badge-position').textContent = player.position || '—';
    const logo = document.querySelector('#team-logo');
    logo.src = getTeamLogoUrl(player.team);
    logo.alt = player.team;
}

function renderProjection(projection){
    document.querySelector('#proj-rec-yards').textContent = projection.projected_rec_yards;
    document.querySelector('#proj-receptions').textContent = projection.projected_receptions;
    document.querySelector('#proj-rec-tds').textContent = projection.projected_rec_tds;
    renderShapBars(projection.top_factors);
}

function renderShapBars(factors) {
    const rows = factors.map(function(f) {
        const barClass = f.direction === 'up' ? 'positive' : 'negative';
        const arrow    = f.direction === 'up' ? '↑' : '↓';
        const dirClass = f.direction === 'up' ? 'pos' : 'neg';
        const sign     = f.value > 0 ? '+' : '';
        return `
            <div class="shap-row">
                <span class="shap-label">${f.label}<span class="shap-feature-val">${f.feature_val}</span></span>
                <div class="shap-bar-track"><div class="shap-bar ${barClass}" style="width: ${f.magnitude}%"></div></div>
                <span class="shap-val ${dirClass}">${sign}${f.value} yds</span>
                <span class="shap-dir ${dirClass}">${arrow}</span>
            </div>`;
    }).join('');
    document.querySelector('.shap-section').innerHTML =
        '<p class="overline">Top Factors</p>' + rows;
}

function renderSeasonStats(stats) {
    const fmt = v => v != null ? v : '—';
    document.querySelector('#season-stats-games').textContent = stats.games + ' games';
    document.querySelector('#stat-targets').textContent    = fmt(stats.targets);
    document.querySelector('#stat-receptions').textContent = fmt(stats.receptions);
    document.querySelector('#stat-rec-yards').textContent  = fmt(stats.rec_yards);
    document.querySelector('#stat-rec-tds').textContent    = fmt(stats.rec_tds);
    document.querySelector('#stat-ypr').textContent        = fmt(stats.yards_per_rec);
    document.querySelector('#stat-catch-rate').textContent = stats.catch_rate != null ? stats.catch_rate + '%' : '—';
}

function renderScoutingReport(data) {
    const body = document.querySelector('.scouting-body');
    const paragraphs = data.scouting_report.split('\n\n').filter(p => p.trim());
    body.innerHTML = paragraphs.map(p => `<p class="scouting-text">${p}</p>`).join('');
}



