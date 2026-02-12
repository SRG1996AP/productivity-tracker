function addRow() {
    const table = document.getElementById('prodTable').getElementsByTagName('tbody')[0];
    const rowCount = table.rows.length + 1;
    const row = table.insertRow();
    row.innerHTML = `
        <td>${rowCount}</td>
        <td contenteditable="true"></td>
        <td contenteditable="true"></td>
        <td contenteditable="true"></td>
        <td contenteditable="true"></td>
        <td contenteditable="true"></td>
        <td><button onclick="removeRow(this)">Remove</button></td>
    `;
}

function removeRow(btn) {
    const row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function saveData() {
    const table = document.getElementById('prodTable').getElementsByTagName('tbody')[0];
    const entries = [];
    for (let i = 0; i < table.rows.length; i++) {
        const cells = table.rows[i].cells;
        entries.push({
            'No': cells[0].innerText,
            'Activity': cells[1].innerText,
            'Duration': cells[2].innerText,
            'Frequency': cells[3].innerText,
            'Output': cells[4].innerText,
            'Remarks': cells[5].innerText
        });
    }

    fetch('/save_productivity', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({department: department, entries: entries})
    })
    .then(res => res.json())
    .then(data => alert(data.message))
    .catch(err => console.error(err));
}
