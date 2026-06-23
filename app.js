
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
                const url = "http://127.0.0.1:8000/players/" + result[index].player_id + "/full"; 
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

function renderPlayer(player){
    document.querySelector('#player-name').textContent = player.name;
    document.querySelector('#player-meta').textContent = `${player.team} · Age ${Math.round(player.age)} · ${Math.round(player.years_exp)} Years of Experience`;
    document.querySelector('.badge-position').textContent = player.position;
    document.querySelector('#cap-hit-value').textContent = '$' + (player.aav / 1000000).toFixed(1) + 'M';
}

