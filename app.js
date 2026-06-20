

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

