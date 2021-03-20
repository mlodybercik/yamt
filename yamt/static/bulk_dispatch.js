function get_and_reset(name) {
    _ = document.getElementById(name)
    _.removeAttribute("id")
    return _
}

const f_input = get_and_reset("input")
const f_output = get_and_reset("output")
const f_preset = get_and_reset("preset_name")

const b_add = document.getElementById("add")
const b_remove = document.getElementById("remove")
const b_run = document.getElementById("run")

const table = document.getElementById("table")

function spawn_form() {
    tr = document.createElement("tr")
    tr.setAttribute("class", "job")

    input = document.createElement("td")
    input_child = f_input.cloneNode(true)
    input_child.value = f_input.value
    input_child.setAttribute("input", "")
    input.appendChild(input_child)

    output = document.createElement("td")
    output_child = f_output.cloneNode(true)
    output_child.value = f_output.value
    output_child.setAttribute("output", "")
    output.appendChild(output_child)

    preset = document.createElement("td")
    preset_child = f_preset.cloneNode(true)
    preset_child.value = f_preset.value
    preset_child.setAttribute("preset", "")
    preset.appendChild(preset_child)

    tr.appendChild(input)
    tr.appendChild(output)
    tr.appendChild(preset)
    return tr
}

const entries = []

b_add.onclick = function () {
    new_row = spawn_form()
    entries.push(new_row)
    table.appendChild(new_row)
}

b_remove.onclick = function () {
    if(entries.length)
        entries.pop().remove()
}

b_run.onclick = function () {
    if(entries.length) {
        let objs = []
        entries.forEach(job => {
            let x = {
                "input": job.querySelector("input[input]").value,
                "output": job.querySelector("input[output]").value,
                "preset": job.querySelector("select[preset]").value,
            }
            objs.push(x)
        });
        fetch("/bulk_dispatch", 
        {method: "POST",
         headers: {"Content-Type": "application/json"}, 
         body: JSON.stringify(objs)})
        .then(response => {
            if(response.ok) {
                console.log("ok")
            }
        })
        .catch(error => {
            console.log(error)
        })
    }
}