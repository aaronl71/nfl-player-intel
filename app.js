const player = {
    name: "Tyreek Hill",
    team: "Miami Dolphins",
    position: "WR",
    age: 31,
    years_exp: 9,
    pff_grade: 88.2,
    cap_hit: "$28.0M",
    value_rating: "Undervalued",
    projection: {
        rec_yards: 112,
        rec_tds: 1.2,
        targets: 9.4,
        receptions: 6.8
    },
    valuation: {
        war_score: 3.1,
        positional_percentile: "88th",
        production_score: 84.1,
        value_vs_replacement: "+$11.2M",
        cap_hit_pct: "12.8%"
    }
}

const players = [
    { name: "Tyreek Hill",      team: "Miami Dolphins",       position: "WR" },
    { name: "Patrick Mahomes",  team: "Kansas City Chiefs",   position: "QB" },
    { name: "Justin Jefferson", team: "Minnesota Vikings",    position: "WR" },
    { name: "Travis Kelce",     team: "Kansas City Chiefs",   position: "TE" },
    { name: "Saquon Barkley",   team: "Philadelphia Eagles",  position: "RB" },
    { name: "CeeDee Lamb",      team: "Dallas Cowboys",       position: "WR" },
    { name: "Josh Allen",       team: "Buffalo Bills",        position: "QB" },
    { name: "Amon-Ra St. Brown",team: "Detroit Lions",        position: "WR" },
    { name: "Sam LaPorta",      team: "Detroit Lions",        position: "TE" },
    { name: "Bijan Robinson",   team: "Atlanta Falcons",      position: "RB" }
]

const searchInput = document.querySelector('#player-search');

searchInput.addEventListener('input', function(){
    const query = searchInput.value;

    const results = players.filter(function(player) {
        return player.name.toLowerCase().includes(query.toLowerCase());
    })
    const html = results.map(function(player) {
        return `<li class="recent-player-item">${player.name}</li>`
    }).join('');
    
    document.querySelector('#recent-players').innerHTML = html;

    document.querySelectorAll('#recent-players .recent-player-item').forEach(function(li, index){
        li.addEventListener('click', function(){
            renderPlayer(results[index])
        })
    })
})

const filterBtns = document.querySelectorAll('.filter-btn')

filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
        filterBtns.forEach(function(b) { b.classList.remove('active') })
        btn.classList.add('active')
    })
})

function renderPlayer(player){
    document.querySelector('#player-name').textContent = player.name;
    document.querySelector('#player-meta').textContent = `${player.team} · Age ${player.age} · ${player.years_exp}`;
    document.querySelector('.badge-position').textContent = player.position;
}

