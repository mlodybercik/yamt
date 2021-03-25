const table = document.getElementById("table")

let entries = []

function update_text(id, checked, succesful=true) {
    tag = document.getElementById(id)
    const input = tag.getElementsByTagName("input")[0]
    const span = tag.getElementsByTagName("span")[0]
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

async function remove(id) {
    fetch("/delete_watcher", 
        {method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"}, 
        body: "id="+id}).then(response => {
            if(response.ok) {
                document.getElementById(id).remove()
                if(table.getElementsByTagName("tr").length == 1) {
                    table.remove()
                }
                }}
            ).catch((error) => {
                console.log(error)
            }
        )
}


window.onload = function () {
    entries = [...document.getElementsByClassName("running")]
    entries.forEach(running => {
        running.onchange = function () {
            const id = running.parentElement.parentElement.id
            update(id, this.checked)
        }
    });
    entries = [...document.getElementsByClassName("delete")]
    entries.forEach(delete_ => {
        delete_.onclick = function () {
            const id = delete_.parentElement.parentElement.id
            remove(id)
        }
    })
}