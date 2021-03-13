const id = document.getElementById("preset_name")
const command = document.getElementById("command")
const input = document.getElementById("input")
const output = document.getElementById("output")

var command_string = ""

function change_text() {
    console.log(1)
    command.value = "HandbrakeCLI -i " + input.value + " -o " + output.value + " " + command_string
}

async function fetch_settings(id, command) {
    let form = new FormData();
    fetch("/render_settings", {method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded"}, body: "id="+id})
    .then((response) => {
    if (response.ok) {
        response.text().then((text) => {
            command_string = text
            change_text()
        })
    }
    }).catch((error) => {
        console.log(error)
    });
}

id.onchange = function() {data = fetch_settings(id.value, command)}
input.onkeyup = function() {change_text()}
output.onkeyup = function() {change_text()}

id.onchange()