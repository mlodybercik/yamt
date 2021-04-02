const cpu_avg = document.getElementById("cpu_avg")
const cpu_bars = [...document.getElementById("cpu_card").getElementsByClassName("progress-bar")]
const main_bar = document.getElementById("main-progress").getElementsByClassName("progress-bar")[0]
const worker = document.getElementById("worker")
const watcher = document.getElementById("watcher")
const time_remaining = document.getElementById("time-remaining")    


let last_seen_task = null

function update_bar(bar, percent) {
    const str = percent + "%"
    bar.innerText = str
    bar.style["width"] = str
}

function update_avg(state) {
    cpu_avg.innerText = state
}

function update_time(request) {
    if("curr_task" in request) {
        if(request["curr_task"]) {
            time_remaining.innerText = request["curr_task"]["estimated"]
        } else {
            try {
                time_remaining.innerText = "Waiting for ffmpeg..."   
            } catch (error) {}
        }
    }
}

function reload(request) {
    if("curr_task" in request) {
        if(request["curr_task"]) {
            if(last_seen_task === null) {
                last_seen_task = request["curr_task"]["current_task"]
            } else if(last_seen_task != request["curr_task"]["current_task"]) {
                location.reload()
                return true
            }
        } else if(typeof last_seen_task == "number") {
            location.reload()
            return true
        } else {
            last_seen_task = undefined
        }
    }
}

function update_state(worandwat) {
    worker.innerText = worandwat[0]
    watcher.innerText = worandwat[1]
}

function update_site_state(request) {
    if(reload(request))
        return
    update_avg(request["cpu"]["cpu_avg"])
    for(let i = 0; i<cpu_bars.length; i++) {
        update_bar(cpu_bars[i], request["cpu"]["cpu_usage"][i])
    }
    if("curr_task" in request)
        if(request["curr_task"]) {
            update_bar(main_bar, request["curr_task"]["percent"])
        }
    update_state(request["states"])
    update_time(request)
}

async function get_state() {
    fetch("/get_update", {method: "GET"}).then(response => {
        if(response.ok) {
            response.json().then(json_data => {
                update_site_state(json_data)
                setTimeout(get_state, 3000)
            })
        }
    }).catch(error => {
        console.log(error)
    })
}

window.onload = function () {
    get_state()
    console.log("Started fetching data every 3s")
}