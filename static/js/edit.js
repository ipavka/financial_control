
function getStyle(el, cssprop) {
    if (el.currentStyle)
        return el.currentStyle[cssprop];	 // IE
    else if (document.defaultView && document.defaultView.getComputedStyle)
        return document.defaultView.getComputedStyle(el, "")[cssprop];	// Firefox
    else
        return el.style[cssprop]; //try and get inline style
}

function applyEdit(tabID, editables) {
    let tab = document.getElementById(tabID);
    if (tab) {
        let rows = tab.getElementsByTagName("tr");
        for(let r = 0; r < rows.length; r++) {
            let tds = rows[r].getElementsByTagName("td");
            for (let c = 0; c < tds.length; c++) {
                if (editables.indexOf(c) > -1)
                    tds[c].onclick = function () { beginEdit(this); };
            }
        }
    }
}
let oldColor, oldText, padTop, padBottom = "";
function beginEdit(td) {
    if (td.firstChild && td.firstChild.tagName === "INPUT")
        return;

    oldText = td.innerHTML.trim();
    oldColor = getStyle(td, "backgroundColor");
    padTop = getStyle(td, "paddingTop");
    padBottom = getStyle(td, "paddingBottom");

    let input = document.createElement("input");
    input.value = oldText;

    //// ------- input style -------
    let left = getStyle(td, "paddingLeft").replace("px", "");
    let right = getStyle(td, "paddingRight").replace("px", "");
    input.style.width = td.offsetWidth - left - right - (td.clientLeft * 2) - 2 + "px";
    input.style.height = td.offsetHeight - (td.clientTop * 2) - 2 + "px";
    input.style.border = "0px";
    input.style.fontFamily = "inherit";
    input.style.fontSize = "inherit";
    input.style.textAlign = "inherit";
    input.style.backgroundColor = "LightGoldenRodYellow";

    input.onblur = function () { endEdit(this); };

    td.innerHTML = "";
    td.style.paddingTop = "0px";
    td.style.paddingBottom = "0px";
    td.style.backgroundColor = "LightGoldenRodYellow";
    td.insertBefore(input, td.firstChild);
    input.select();
}
async function endEdit(input) {
    let td = input.parentNode;
    td.removeChild(td.firstChild);	//remove input
    td.innerHTML = input.value;

    if (oldText !== input.value.trim() ) {
        let change = {
            in: input.value,
            id: td.id
        }
        let response = await fetch('/input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: `{"cost": "${change.in}", "cost_id": "${change.id}" }`
        })
        let response_json = await response.json();
        if (response_json.success) {
            alert(response_json.message)
            td.style.color = "red";
        } else {
            alert(response_json.message)
            td.innerHTML = oldText
        }

    }


    td.style.paddingTop = padTop;
    td.style.paddingBottom = padBottom;
    td.style.backgroundColor = oldColor;
}
applyEdit("edit-table", [1]);

// change date display on a more compact
const options = {
    day: 'numeric',
    month: 'numeric',
    year: '2-digit',
    hour: 'numeric',
    minute: 'numeric',
}

function getDate(str) {
    let date = new Date(str);
    let myDate = date.toLocaleString('ru', options).split(', ')
    let time = myDate[1]
    let shortDate = myDate[0].replaceAll('.', '/')
    return [time, shortDate]
}

const elementsList = document.querySelectorAll("#ch-date");
const elementsArray = [...elementsList];

elementsArray.forEach(element => {
    element.innerHTML = getDate(element.innerHTML).join(' ');
});

