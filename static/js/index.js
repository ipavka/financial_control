function handle(object) {
    let inp = document.createElement("input");
    inp.type = "text";
    inp.value = object.innerText;
    console.log(inp.value)
    object.innerText = "";
    object.appendChild(inp);

    let _event = object.onclick;
    object.onclick = null;

    inp.onkeydown = async function (e) {
        if(e.keyCode === 13) {
            console.log(inp.value)
            let change = inp.value
            let response = await fetch('/input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: `{"username": "${change}", "password": "${change}"}`
            })
            await response.json();
            object.innerText = inp.value;
            object.onclick = _event;
            object.removeChild(inp)
        }
    }
}