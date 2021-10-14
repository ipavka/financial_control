
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
                    // console.log(tds[0])
                    tds[c].onclick = function () { beginEdit(this); };
            }
        }
    }
}
let oldColor, oldText, padTop, padBottom = "";
function beginEdit(td) {
    // console.log(td.id)
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
    // console.log(td.id)
    // let change = input.value;

    // console.log(td.innerHTML)
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
        await response.json();
        td.style.color = "red";
    }


    td.style.paddingTop = padTop;
    td.style.paddingBottom = padBottom;
    td.style.backgroundColor = oldColor;
}
applyEdit("edit-table", [1]);