let entries = []

function update_text(id, checked, succesful=true) {
    tag = document.getElementById(id)
    const input = tag.children[0]
    const span = tag.children[1]
    if(succesful) {
        checked ? span.classList["value"] = "text-success" : span.classList["value"] = "text-danger"
        checked ? span.textContent = " Yes!" : span.textContent = " No!"
    } else {
        input.checked = !checked
    }
}

async function update(id, checked) {
    fetch("/update_watcher", 
        {method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"}, 
        body: "id="+id+"&checked="+checked}).then(response => {
            if(response.ok) {
                response.text().then((text) => {
                    update_text(id, checked)
                })
            } else {
                update_text(id, checked, false)
            }
        }).catch((error) => {
            console.log(error)
        })
}


window.onload = function () {
    entries = [...document.getElementsByClassName("running")]
    entries.forEach(running => {
        running.onchange = function () {
            update(this.value, this.checked)
        }
    });
}